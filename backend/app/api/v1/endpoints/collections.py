"""
Collection management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.collection import CollectionSample
from app.models.user import User
from app.schemas.collection_schemas import (
    AddSamplesRequest,
    CollectionCreate,
    CollectionDetailResponse,
    CollectionListResponse,
    CollectionResponse,
    CollectionUpdate,
    SampleInCollectionResponse,
)
from app.services.collection_service import CollectionService

router = APIRouter()


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_in: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new collection."""
    service = CollectionService(db)

    try:
        collection = await service.create_collection(
            user_id=current_user.id,
            name=collection_in.name,
            description=collection_in.description,
            parent_collection_id=collection_in.parent_collection_id,
            is_smart=collection_in.is_smart,
            smart_rules=collection_in.smart_rules.model_dump() if collection_in.smart_rules else None
        )
        return collection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=CollectionListResponse)
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_smart: bool = Query(True)
):
    """List collections with pagination."""
    service = CollectionService(db)

    collections, total = await service.list_collections(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_smart=include_smart
    )

    return {
        "items": collections,
        "total": total
    }


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
async def get_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get collection with samples and sub-collections."""
    service = CollectionService(db)

    collection = await service.get_collection(
        collection_id=collection_id,
        user_id=current_user.id,
        include_samples=True,
        include_sub_collections=True
    )

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    # Build response with samples and sub-collections
    response = CollectionDetailResponse.model_validate(collection)

    # Get samples with added_at timestamp from association table
    if collection.samples:
        from sqlalchemy import select


        # Get association data for added_at timestamps
        assoc_query = select(CollectionSample).where(
            CollectionSample.collection_id == collection_id
        )
        assoc_result = await db.execute(assoc_query)
        associations = {assoc.sample_id: assoc.added_at for assoc in assoc_result.scalars().all()}

        # Build sample responses
        sample_responses = []
        for sample in collection.samples:
            sample_responses.append(
                SampleInCollectionResponse(
                    id=sample.id,
                    title=sample.title,
                    genre=sample.genre,
                    bpm=sample.bpm,
                    duration=sample.duration,
                    added_at=associations.get(sample.id)
                )
            )
        response.samples = sample_responses

    return response


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    collection_in: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update collection."""
    service = CollectionService(db)

    # Build update kwargs from non-None fields
    update_data = collection_in.model_dump(exclude_unset=True)
    if "smart_rules" in update_data and update_data["smart_rules"]:
        update_data["smart_rules"] = update_data["smart_rules"]

    try:
        collection = await service.update_collection(
            collection_id=collection_id,
            user_id=current_user.id,
            **update_data
        )

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )

        return collection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete collection."""
    service = CollectionService(db)

    deleted = await service.delete_collection(
        collection_id=collection_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    return {"success": True}


@router.post("/{collection_id}/samples")
async def add_samples_to_collection(
    collection_id: int,
    samples_in: AddSamplesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add samples to collection."""
    service = CollectionService(db)

    try:
        count = await service.add_samples_to_collection(
            collection_id=collection_id,
            user_id=current_user.id,
            sample_ids=samples_in.sample_ids
        )

        return {"count": count}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{collection_id}/samples/{sample_id}")
async def remove_sample_from_collection(
    collection_id: int,
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove sample from collection."""
    service = CollectionService(db)

    try:
        removed = await service.remove_sample_from_collection(
            collection_id=collection_id,
            user_id=current_user.id,
            sample_id=sample_id
        )

        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sample not found in collection"
            )

        return {"success": True}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{collection_id}/samples")
async def get_collection_samples(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get paginated samples in collection."""
    service = CollectionService(db)

    try:
        samples, total = await service.get_collection_samples(
            collection_id=collection_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )

        # Add file URLs
        for sample in samples:
            sample.file_url = f"/api/v1/samples/{sample.id}/download"

        return {
            "items": samples,
            "total": total
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{collection_id}/evaluate")
async def evaluate_smart_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluate smart collection rules and update samples."""
    service = CollectionService(db)

    try:
        count = await service.evaluate_smart_collection(
            collection_id=collection_id,
            user_id=current_user.id
        )

        # Get updated collection
        collection = await service.get_collection(collection_id, current_user.id)

        return {
            "count": count,
            "updated_at": collection.updated_at if collection else None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
