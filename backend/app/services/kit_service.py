"""
KitService for managing SP-404MK2 kit creation and pad assignments.

Provides comprehensive kit management including:
- Kit CRUD operations with user isolation
- Pad assignment and management (16 pads across 4 banks)
- Smart sample recommendations based on pad purpose, BPM, and genre
- Kit export preparation with manifest generation
"""
import logging
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import tempfile
import os

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.kit import Kit, KitSample
from app.models.sample import Sample
from app.schemas.kit import (
    ExportManifest,
    ExportSampleInfo,
    SampleRecommendation,
)

logger = logging.getLogger(__name__)


# ===========================
# Custom Exceptions
# ===========================

class KitNotFoundError(Exception):
    """Raised when a kit is not found or user doesn't have access."""
    pass


class SampleNotFoundError(Exception):
    """Raised when a sample is not found."""
    pass


class InvalidPadNumberError(Exception):
    """Raised when pad number is invalid (must be 1-16)."""
    pass


class InvalidPadBankError(Exception):
    """Raised when pad bank is invalid (must be A, B, C, or D)."""
    pass


class PadAlreadyAssignedError(Exception):
    """Raised when trying to assign to an already-occupied pad."""
    pass


# ===========================
# Pad Purpose Definitions
# ===========================

# Smart recommendation rules based on pad number
PAD_PURPOSES = {
    # Pads 1-4: Loops and melodic samples
    1: {"duration_min": 3.0, "tags": ["loop", "sample", "melody", "melodic"]},
    2: {"duration_min": 3.0, "tags": ["loop", "sample", "melody", "melodic"]},
    3: {"duration_min": 3.0, "tags": ["loop", "sample", "melody", "melodic"]},
    4: {"duration_min": 3.0, "tags": ["loop", "sample", "melody", "melodic"]},

    # Pads 5-8: Textures and cymbals
    5: {"duration_max": 2.0, "tags": ["crash", "cymbal", "tom", "texture"]},
    6: {"duration_max": 2.0, "tags": ["crash", "cymbal", "tom", "texture"]},
    7: {"duration_max": 2.0, "tags": ["crash", "cymbal", "tom", "texture"]},
    8: {"duration_max": 2.0, "tags": ["crash", "cymbal", "tom", "texture"]},

    # Pads 9-12: Accents and percussion
    9: {"duration_max": 1.5, "tags": ["clap", "rim", "shaker", "808", "perc", "percussion"]},
    10: {"duration_max": 1.5, "tags": ["clap", "rim", "shaker", "808", "perc", "percussion"]},
    11: {"duration_max": 1.5, "tags": ["clap", "rim", "shaker", "808", "perc", "percussion"]},
    12: {"duration_max": 1.5, "tags": ["clap", "rim", "shaker", "808", "perc", "percussion"]},

    # Pads 13-16: Core drum sounds ("the heart")
    13: {"duration_max": 1.0, "tags": ["kick", "bass drum", "808"]},  # Main kick
    14: {"duration_max": 1.0, "tags": ["snare", "clap"]},  # Main snare
    15: {"duration_max": 1.0, "tags": ["hat", "hihat", "closed", "chh"]},  # Closed hat
    16: {"duration_max": 1.0, "tags": ["hat", "hihat", "open", "ohh"]},  # Open hat
}


class KitService:
    """
    Service for managing SP-404MK2 kits and pad assignments.

    Handles:
    - Kit creation, retrieval, update, and deletion
    - Pad assignment management with validation
    - Smart sample recommendations based on pad purpose
    - Export manifest generation
    """

    def __init__(self):
        """Initialize KitService."""
        pass

    # ===========================
    # Kit CRUD Operations
    # ===========================

    async def create_kit(
        self,
        db: AsyncSession,
        user_id: int,
        name: str,
        description: Optional[str] = None,
    ) -> Kit:
        """
        Create a new kit.

        Args:
            db: Database session
            user_id: User ID who owns the kit
            name: Kit name (1-255 characters)
            description: Optional kit description

        Returns:
            Kit: Created kit instance

        Raises:
            ValueError: If name is empty or exceeds 255 characters
        """
        logger.info(f"Creating kit '{name}' for user {user_id}")

        # Validate name
        if not name or not name.strip():
            raise ValueError("Kit name cannot be empty")
        if len(name) > 255:
            raise ValueError("Kit name cannot exceed 255 characters")

        # Create kit
        kit = Kit(
            user_id=user_id,
            name=name,
            description=description,
            pad_layout={},
            bank_config={},
        )

        db.add(kit)
        await db.commit()

        # Re-fetch with relationships loaded to avoid greenlet errors
        result = await db.execute(
            select(Kit)
            .options(selectinload(Kit.samples).selectinload(KitSample.sample))
            .where(Kit.id == kit.id)
        )
        kit = result.scalar_one()

        logger.info(f"Kit created successfully: ID={kit.id}, name='{kit.name}'")
        return kit

    async def get_kit_by_id(
        self,
        db: AsyncSession,
        kit_id: int,
        user_id: int,
    ) -> Optional[Kit]:
        """
        Get a kit by ID with user access check.

        Args:
            db: Database session
            kit_id: Kit ID
            user_id: User ID (for access control)

        Returns:
            Optional[Kit]: Kit if found and user has access, None otherwise
        """
        logger.debug(f"Fetching kit {kit_id} for user {user_id}")

        result = await db.execute(
            select(Kit)
            .options(selectinload(Kit.samples).selectinload(KitSample.sample))
            .where(
                and_(
                    Kit.id == kit_id,
                    Kit.user_id == user_id,
                )
            )
        )
        kit = result.scalar_one_or_none()

        if kit:
            logger.debug(f"Kit {kit_id} found with {len(kit.samples)} samples")
        else:
            logger.debug(f"Kit {kit_id} not found for user {user_id}")

        return kit

    async def get_user_kits(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Kit]:
        """
        Get all kits for a user with pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of kits to skip
            limit: Maximum number of kits to return

        Returns:
            List[Kit]: List of kits ordered by creation date (newest first)
        """
        logger.debug(f"Fetching kits for user {user_id} (skip={skip}, limit={limit})")

        result = await db.execute(
            select(Kit)
            .options(selectinload(Kit.samples).selectinload(KitSample.sample))
            .where(Kit.user_id == user_id)
            .order_by(Kit.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        kits = list(result.scalars().all())

        logger.info(f"Retrieved {len(kits)} kits for user {user_id}")
        return kits

    async def update_kit(
        self,
        db: AsyncSession,
        kit_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Kit:
        """
        Update kit metadata (partial update).

        Args:
            db: Database session
            kit_id: Kit ID to update
            user_id: User ID (for access control)
            name: New name (optional)
            description: New description (optional)
            is_public: New public status (optional)

        Returns:
            Kit: Updated kit instance

        Raises:
            KitNotFoundError: If kit not found or user doesn't have access
            ValueError: If name validation fails
        """
        logger.info(f"Updating kit {kit_id} for user {user_id}")

        # Fetch kit with access check
        kit = await self.get_kit_by_id(db, kit_id, user_id)
        if not kit:
            raise KitNotFoundError(f"Kit {kit_id} not found or access denied")

        # Validate name if provided
        if name is not None:
            if not name.strip():
                raise ValueError("Kit name cannot be empty")
            if len(name) > 255:
                raise ValueError("Kit name cannot exceed 255 characters")
            kit.name = name

        # Update other fields if provided
        if description is not None:
            kit.description = description
        if is_public is not None:
            kit.is_public = is_public

        await db.commit()

        # Re-fetch with relationships loaded to avoid greenlet errors
        result = await db.execute(
            select(Kit)
            .options(selectinload(Kit.samples).selectinload(KitSample.sample))
            .where(Kit.id == kit_id)
        )
        kit = result.scalar_one()

        logger.info(f"Kit {kit_id} updated successfully")
        return kit

    async def delete_kit(
        self,
        db: AsyncSession,
        kit_id: int,
        user_id: int,
    ) -> bool:
        """
        Delete a kit and all its pad assignments.

        Args:
            db: Database session
            kit_id: Kit ID to delete
            user_id: User ID (for access control)

        Returns:
            bool: True if deleted, False if not found

        Note:
            Cascade delete will remove all KitSample assignments
        """
        logger.info(f"Deleting kit {kit_id} for user {user_id}")

        # Fetch kit with access check
        kit = await self.get_kit_by_id(db, kit_id, user_id)
        if not kit:
            logger.warning(f"Kit {kit_id} not found for user {user_id}")
            return False

        # Delete all pad assignments first (required for async sessions)
        delete_assignments = await db.execute(
            select(KitSample).where(KitSample.kit_id == kit_id)
        )
        for assignment in delete_assignments.scalars().all():
            await db.delete(assignment)

        # Then delete the kit
        await db.delete(kit)
        await db.commit()

        logger.info(f"Kit {kit_id} deleted successfully")
        return True

    # ===========================
    # Pad Assignment Operations
    # ===========================

    async def assign_sample_to_pad(
        self,
        db: AsyncSession,
        kit_id: int,
        sample_id: int,
        pad_bank: str,
        pad_number: int,
        user_id: int,
        volume: float = 1.0,
        pitch_shift: int = 0,
    ) -> KitSample:
        """
        Assign a sample to a specific pad in a kit.

        Args:
            db: Database session
            kit_id: Kit ID
            sample_id: Sample ID to assign
            pad_bank: Pad bank (A, B, C, or D)
            pad_number: Pad number (1-16)
            user_id: User ID (for access control)
            volume: Playback volume (0.0-1.0), default 1.0
            pitch_shift: Pitch shift in semitones, default 0

        Returns:
            KitSample: Created pad assignment

        Raises:
            KitNotFoundError: If kit not found or user doesn't have access
            SampleNotFoundError: If sample not found
            InvalidPadBankError: If pad bank is invalid
            InvalidPadNumberError: If pad number is invalid
            PadAlreadyAssignedError: If pad already has a sample
        """
        logger.info(
            f"Assigning sample {sample_id} to kit {kit_id} "
            f"pad {pad_bank}{pad_number} (vol={volume}, pitch={pitch_shift})"
        )

        # Validate pad bank
        if pad_bank not in ['A', 'B', 'C', 'D']:
            raise InvalidPadBankError(f"Invalid pad bank '{pad_bank}'. Must be A, B, C, or D")

        # Validate pad number
        if pad_number < 1 or pad_number > 16:
            raise InvalidPadNumberError(f"Invalid pad number {pad_number}. Must be 1-16")

        # Verify kit exists and user has access
        kit = await self.get_kit_by_id(db, kit_id, user_id)
        if not kit:
            raise KitNotFoundError(f"Kit {kit_id} not found or access denied")

        # Check if pad already has a sample (do this BEFORE checking sample exists)
        existing_result = await db.execute(
            select(KitSample).where(
                and_(
                    KitSample.kit_id == kit_id,
                    KitSample.pad_bank == pad_bank,
                    KitSample.pad_number == pad_number,
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise PadAlreadyAssignedError(
                f"Pad {pad_bank}{pad_number} already assigned to sample {existing.sample_id}"
            )

        # Verify sample exists
        sample_result = await db.execute(
            select(Sample).where(Sample.id == sample_id)
        )
        sample = sample_result.scalar_one_or_none()
        if not sample:
            raise SampleNotFoundError(f"Sample {sample_id} not found")

        # Create assignment
        assignment = KitSample(
            kit_id=kit_id,
            sample_id=sample_id,
            pad_bank=pad_bank,
            pad_number=pad_number,
            volume=volume,
            pitch_shift=pitch_shift,
        )

        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        # Load sample relationship
        await db.refresh(assignment, ['sample'])

        logger.info(f"Sample {sample_id} assigned to pad {pad_bank}{pad_number}")
        return assignment

    async def remove_sample_from_pad(
        self,
        db: AsyncSession,
        kit_id: int,
        pad_bank: str,
        pad_number: int,
        user_id: int,
    ) -> bool:
        """
        Remove a sample assignment from a pad.

        Args:
            db: Database session
            kit_id: Kit ID
            pad_bank: Pad bank (A, B, C, or D)
            pad_number: Pad number (1-16)
            user_id: User ID (for access control)

        Returns:
            bool: True if removed, False if pad was empty

        Raises:
            KitNotFoundError: If kit not found or user doesn't have access
        """
        logger.info(f"Removing sample from kit {kit_id} pad {pad_bank}{pad_number}")

        # Verify kit exists and user has access
        kit = await self.get_kit_by_id(db, kit_id, user_id)
        if not kit:
            raise KitNotFoundError(f"Kit {kit_id} not found or access denied")

        # Find assignment
        result = await db.execute(
            select(KitSample).where(
                and_(
                    KitSample.kit_id == kit_id,
                    KitSample.pad_bank == pad_bank,
                    KitSample.pad_number == pad_number,
                )
            )
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            logger.debug(f"No assignment found for pad {pad_bank}{pad_number}")
            return False

        await db.delete(assignment)
        await db.commit()

        logger.info(f"Sample removed from pad {pad_bank}{pad_number}")
        return True

    async def get_pad_assignment(
        self,
        db: AsyncSession,
        kit_id: int,
        pad_bank: str,
        pad_number: int,
    ) -> Optional[KitSample]:
        """
        Get the sample assignment for a specific pad.

        Args:
            db: Database session
            kit_id: Kit ID
            pad_bank: Pad bank (A, B, C, or D)
            pad_number: Pad number (1-16)

        Returns:
            Optional[KitSample]: Assignment if exists, None otherwise
        """
        result = await db.execute(
            select(KitSample)
            .options(selectinload(KitSample.sample))
            .where(
                and_(
                    KitSample.kit_id == kit_id,
                    KitSample.pad_bank == pad_bank,
                    KitSample.pad_number == pad_number,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_pad_assignments(
        self,
        db: AsyncSession,
        kit_id: int,
    ) -> List[KitSample]:
        """
        Get all pad assignments for a kit.

        Args:
            db: Database session
            kit_id: Kit ID

        Returns:
            List[KitSample]: List of all pad assignments
        """
        result = await db.execute(
            select(KitSample)
            .options(selectinload(KitSample.sample))
            .where(KitSample.kit_id == kit_id)
            .order_by(KitSample.pad_bank, KitSample.pad_number)
        )
        return list(result.scalars().all())

    # ===========================
    # Smart Recommendations
    # ===========================

    async def get_recommended_samples(
        self,
        db: AsyncSession,
        kit_id: int,
        pad_number: int,
        user_id: int,
        limit: int = 10,
    ) -> List[Sample]:
        """
        Get smart sample recommendations for a specific pad.

        Recommendations are based on:
        1. Pad purpose (duration and tag filtering)
        2. BPM matching (±10 BPM of existing kit samples)
        3. Genre matching (same genre as existing kit samples)

        Args:
            db: Database session
            kit_id: Kit ID
            pad_number: Pad number (1-16)
            user_id: User ID (for access control)
            limit: Maximum number of recommendations

        Returns:
            List[Sample]: Recommended samples ordered by relevance

        Raises:
            InvalidPadNumberError: If pad number is invalid
            KitNotFoundError: If kit not found
        """
        logger.info(f"Getting recommendations for kit {kit_id} pad {pad_number}")

        # Validate pad number
        if pad_number < 1 or pad_number > 16:
            raise InvalidPadNumberError(f"Invalid pad number {pad_number}. Must be 1-16")

        # Verify kit exists
        kit = await self.get_kit_by_id(db, kit_id, user_id)
        if not kit:
            raise KitNotFoundError(f"Kit {kit_id} not found or access denied")

        # Get pad purpose rules
        purpose = PAD_PURPOSES.get(pad_number, {})
        duration_min = purpose.get("duration_min")
        duration_max = purpose.get("duration_max")
        relevant_tags = purpose.get("tags", [])

        # Build base query
        query = select(Sample).where(Sample.user_id == user_id)

        # Apply duration filters ONLY if duration is not NULL
        # This makes duration filtering optional rather than exclusionary
        if duration_min is not None:
            query = query.where(
                or_(
                    Sample.duration.is_(None),  # Include samples without duration
                    Sample.duration >= duration_min
                )
            )
        if duration_max is not None:
            query = query.where(
                or_(
                    Sample.duration.is_(None),  # Include samples without duration
                    Sample.duration <= duration_max
                )
            )

        # Get existing kit samples for BPM/genre matching
        existing_assignments = await self.get_all_pad_assignments(db, kit_id)

        # Apply BPM matching if kit has samples with BPM
        avg_bpm = None
        if existing_assignments:
            existing_bpms = [
                a.sample.bpm for a in existing_assignments
                if a.sample.bpm is not None
            ]
            if existing_bpms:
                avg_bpm = sum(existing_bpms) / len(existing_bpms)
                bpm_min = avg_bpm - 10
                bpm_max = avg_bpm + 10
                query = query.where(
                    or_(
                        Sample.bpm.is_(None),  # Include samples without BPM
                        and_(
                            Sample.bpm >= bpm_min,
                            Sample.bpm <= bpm_max,
                        )
                    )
                )
                logger.debug(f"BPM matching: {bpm_min:.1f} - {bpm_max:.1f}")

        # Apply genre matching if kit has samples with genre
        most_common_genre = None
        if existing_assignments:
            existing_genres = [
                a.sample.genre for a in existing_assignments
                if a.sample.genre is not None
            ]
            if existing_genres:
                # Get most common genre
                genre_counts = {}
                for genre in existing_genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
                most_common_genre = max(genre_counts, key=genre_counts.get)
                logger.debug(f"Genre matching: preferring '{most_common_genre}'")

        # Build comprehensive ordering (cumulative, not overriding)
        # Priority: 1) Tag match, 2) Genre match, 3) Newest first
        order_criteria = []

        # 1. Tag matching (highest priority)
        if relevant_tags:
            tag_conditions = []
            for tag in relevant_tags:
                # JSON array contains check (SQLite compatible)
                tag_conditions.append(
                    func.json_extract(Sample.tags, '$').like(f'%"{tag}"%')
                )
            if tag_conditions:
                order_criteria.append(or_(*tag_conditions).desc())

        # 2. Genre matching (second priority)
        if most_common_genre:
            order_criteria.append((Sample.genre == most_common_genre).desc())

        # 3. Newest samples first (fallback for consistent ordering)
        order_criteria.append(Sample.created_at.desc())

        # Apply all ordering criteria
        query = query.order_by(*order_criteria)

        # Limit results
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        samples = list(result.scalars().all())

        logger.info(
            f"Found {len(samples)} recommendations for pad {pad_number} "
            f"(purpose: {purpose})"
        )
        return samples

    # ===========================
    # Export Operations
    # ===========================

    async def prepare_kit_export(
        self,
        db: AsyncSession,
        kit_id: int,
        user_id: int,
        output_format: str = "wav",
    ) -> ExportManifest:
        """
        Prepare export manifest for a kit.

        Args:
            db: Database session
            kit_id: Kit ID to export
            user_id: User ID (for access control)
            output_format: Output audio format (wav or aiff)

        Returns:
            ExportManifest: Export manifest with kit details and sample list

        Raises:
            KitNotFoundError: If kit not found or user doesn't have access
            ValueError: If kit has no samples
        """
        logger.info(f"Preparing export manifest for kit {kit_id}")

        # Verify kit exists and user has access
        kit = await self.get_kit_by_id(db, kit_id, user_id)
        if not kit:
            raise KitNotFoundError(f"Kit {kit_id} not found or access denied")

        # Get all pad assignments
        assignments = await self.get_all_pad_assignments(db, kit_id)
        if not assignments:
            raise ValueError("Kit has no samples to export")

        # Build sample info list
        sample_infos = []
        for assignment in assignments:
            sample = assignment.sample
            original_filename = Path(sample.file_path).name

            # Sanitize filename for export
            export_filename = self._sanitize_filename(
                original_filename,
                output_format,
            )

            sample_info = ExportSampleInfo(
                sample_id=sample.id,
                original_filename=original_filename,
                export_filename=export_filename,
                pad_bank=assignment.pad_bank,
                pad_number=assignment.pad_number,
                volume=assignment.volume,
                pitch_shift=assignment.pitch_shift,
                file_path=sample.file_path,
            )
            sample_infos.append(sample_info)

        # Create manifest
        manifest = ExportManifest(
            kit_id=kit.id,
            kit_name=kit.name,
            output_format=output_format,
            samples=sample_infos,
            total_samples=len(sample_infos),
        )

        logger.info(f"Export manifest prepared with {len(sample_infos)} samples")
        return manifest

    def _sanitize_filename(
        self,
        filename: str,
        output_format: str,
    ) -> str:
        """
        Sanitize filename for SP-404MK2 compatibility.

        Args:
            filename: Original filename
            output_format: Output format (wav or aiff)

        Returns:
            str: Sanitized filename
        """
        # Remove extension
        name = Path(filename).stem

        # Replace spaces with underscores
        name = name.replace(" ", "_")

        # Remove non-ASCII characters
        name = "".join(c for c in name if ord(c) < 128)

        # Limit length
        if len(name) > 200:
            name = name[:200]

        # Add extension
        ext = "aif" if output_format == "aiff" else "wav"
        return f"{name}.{ext}"
