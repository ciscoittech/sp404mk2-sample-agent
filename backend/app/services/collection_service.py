"""
Collection service implementation
"""
from datetime import datetime
from typing import Any

from app.models.collection import Collection, CollectionSample
from app.models.sample import Sample
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CollectionService:
    """Service for collection operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create_collection(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
        parent_collection_id: int | None = None,
        is_smart: bool = False,
        smart_rules: dict[str, Any] | None = None
    ) -> Collection:
        """Create new collection."""
        # Verify parent collection exists and belongs to user
        if parent_collection_id:
            parent = await self.get_collection(parent_collection_id, user_id)
            if not parent:
                raise ValueError("Parent collection not found or unauthorized")

        collection = Collection(
            user_id=user_id,
            name=name,
            description=description,
            parent_collection_id=parent_collection_id,
            is_smart=is_smart,
            smart_rules=smart_rules or {},
            sample_count=0
        )

        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)

        # If smart collection, evaluate rules immediately
        if is_smart and smart_rules:
            await self.evaluate_smart_collection(int(collection.id), user_id)
            await self.db.refresh(collection)

        return collection

    # READ
    async def get_collection(
        self,
        collection_id: int,
        user_id: int,
        include_samples: bool = False,
        include_sub_collections: bool = False
    ) -> Collection | None:
        """Get collection by ID with authorization check."""
        query = select(Collection).where(
            and_(
                Collection.id == collection_id,
                Collection.user_id == user_id
            )
        )

        if include_samples:
            query = query.options(selectinload(Collection.samples))

        if include_sub_collections:
            query = query.options(selectinload(Collection.sub_collections))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_collections(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        include_smart: bool = True
    ) -> tuple[list[Collection], int]:
        """List collections with pagination."""
        # Build query
        query = select(Collection).where(Collection.user_id == user_id)

        if not include_smart:
            query = query.where(Collection.is_smart == False)

        # Get total count
        count_query = select(func.count(Collection.id)).where(Collection.user_id == user_id)
        if not include_smart:
            count_query = count_query.where(Collection.is_smart == False)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(Collection.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        collections = list(result.scalars().all())

        return collections, total

    # UPDATE
    async def update_collection(
        self,
        collection_id: int,
        user_id: int,
        **kwargs: Any
    ) -> Collection | None:
        """Update collection fields."""
        collection = await self.get_collection(collection_id, user_id)
        if not collection:
            return None

        # Update allowed fields
        allowed_fields = ["name", "description", "parent_collection_id", "is_smart", "smart_rules"]
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(collection, field, value)

        # Use setattr for updated_at
        collection.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(collection)

        # If smart collection was updated, re-evaluate rules
        if collection.is_smart and "smart_rules" in kwargs:
            await self.evaluate_smart_collection(int(collection.id), user_id)
            await self.db.refresh(collection)

        return collection

    # DELETE
    async def delete_collection(
        self,
        collection_id: int,
        user_id: int
    ) -> bool:
        """Delete collection (cascades to sub-collections and samples)."""
        collection = await self.get_collection(collection_id, user_id)
        if not collection:
            return False

        await self.db.delete(collection)
        await self.db.commit()

        return True

    # SAMPLES
    async def add_samples_to_collection(
        self,
        collection_id: int,
        user_id: int,
        sample_ids: list[int]
    ) -> int:
        """Add multiple samples to collection, return count added."""
        collection = await self.get_collection(collection_id, user_id)
        if not collection:
            raise ValueError("Collection not found or unauthorized")

        if collection.is_smart:
            raise ValueError("Cannot manually add samples to smart collection")

        # Verify all samples belong to user
        sample_query = select(Sample).where(
            and_(
                Sample.id.in_(sample_ids),
                Sample.user_id == user_id
            )
        )
        result = await self.db.execute(sample_query)
        valid_samples = list(result.scalars().all())

        if len(valid_samples) != len(sample_ids):
            raise ValueError("Some samples not found or unauthorized")

        # Add samples (skip duplicates)
        count_added = 0
        for sample in valid_samples:
            # Check if already exists
            existing = await self.db.execute(
                select(CollectionSample).where(
                    and_(
                        CollectionSample.collection_id == collection_id,
                        CollectionSample.sample_id == sample.id
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Add new association
            association = CollectionSample(
                collection_id=collection_id,
                sample_id=sample.id
            )
            self.db.add(association)
            count_added += 1

        await self.db.commit()

        # Update sample count
        await self.update_sample_count(collection_id)

        return count_added

    async def remove_sample_from_collection(
        self,
        collection_id: int,
        user_id: int,
        sample_id: int
    ) -> bool:
        """Remove sample from collection."""
        collection = await self.get_collection(collection_id, user_id)
        if not collection:
            return False

        if collection.is_smart:
            raise ValueError("Cannot manually remove samples from smart collection")

        # Delete association
        stmt = delete(CollectionSample).where(
            and_(
                CollectionSample.collection_id == collection_id,
                CollectionSample.sample_id == sample_id
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        if result.rowcount > 0:
            # Update sample count
            await self.update_sample_count(collection_id)
            return True

        return False

    async def get_collection_samples(
        self,
        collection_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[list[Sample], int]:
        """Get paginated samples in collection."""
        collection = await self.get_collection(collection_id, user_id)
        if not collection:
            raise ValueError("Collection not found or unauthorized")

        # Get total count
        count_query = select(func.count(CollectionSample.sample_id)).where(
            CollectionSample.collection_id == collection_id
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get samples with pagination
        query = (
            select(Sample)
            .join(CollectionSample, Sample.id == CollectionSample.sample_id)
            .where(CollectionSample.collection_id == collection_id)
            .order_by(CollectionSample.added_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        samples = list(result.scalars().all())

        return samples, total

    # SMART COLLECTIONS
    async def evaluate_smart_collection(
        self,
        collection_id: int,
        user_id: int
    ) -> int:
        """Evaluate smart rules and update samples, return count."""
        collection = await self.get_collection(collection_id, user_id)
        if not collection:
            raise ValueError("Collection not found or unauthorized")

        if not collection.is_smart:
            raise ValueError("Collection is not a smart collection")

        # Clear existing associations
        await self.db.execute(
            delete(CollectionSample).where(
                CollectionSample.collection_id == collection_id
            )
        )

        # Get matching samples
        rules = collection.smart_rules if isinstance(collection.smart_rules, dict) else {}
        matching_samples = await self.get_smart_collection_candidates(
            user_id,
            rules
        )

        # Add new associations
        for sample in matching_samples:
            association = CollectionSample(
                collection_id=collection_id,
                sample_id=sample.id
            )
            self.db.add(association)

        await self.db.commit()

        # Update sample count
        count = len(matching_samples)
        collection.sample_count = count
        collection.updated_at = datetime.now()
        await self.db.commit()

        return count

    async def get_smart_collection_candidates(
        self,
        user_id: int,
        rules: dict[str, Any]
    ) -> list[Sample]:
        """Query samples matching smart rules."""
        query = select(Sample).where(Sample.user_id == user_id)

        conditions = []

        # Genre filter
        if rules.get("genres"):
            conditions.append(Sample.genre.in_(rules["genres"]))

        # BPM range filter
        if rules.get("bpm_min") is not None:
            conditions.append(Sample.bpm >= rules["bpm_min"])
        if rules.get("bpm_max") is not None:
            conditions.append(Sample.bpm <= rules["bpm_max"])

        # Tags filter (sample must have at least one matching tag)
        if rules.get("tags"):
            tag_conditions = []
            for tag in rules["tags"]:
                # JSON array contains check - PostgreSQL specific
                tag_conditions.append(Sample.tags.contains([tag]))
            if tag_conditions:
                conditions.append(or_(*tag_conditions))

        # Confidence filter (any confidence score meets threshold)
        if rules.get("min_confidence") is not None:
            min_conf = rules["min_confidence"]
            conf_conditions = []
            if Sample.bpm_confidence:
                conf_conditions.append(Sample.bpm_confidence >= min_conf)
            if Sample.genre_confidence:
                conf_conditions.append(Sample.genre_confidence >= min_conf)
            if Sample.key_confidence:
                conf_conditions.append(Sample.key_confidence >= min_conf)
            if conf_conditions:
                conditions.append(or_(*conf_conditions))

        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # UTILITIES
    async def update_sample_count(
        self,
        collection_id: int
    ) -> None:
        """Update denormalized sample_count."""
        count_query = select(func.count(CollectionSample.sample_id)).where(
            CollectionSample.collection_id == collection_id
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0

        # Update collection
        update_query = select(Collection).where(Collection.id == collection_id)
        result = await self.db.execute(update_query)
        collection = result.scalar_one_or_none()

        if collection:
            collection.sample_count = count
            collection.updated_at = datetime.now()
            await self.db.commit()
