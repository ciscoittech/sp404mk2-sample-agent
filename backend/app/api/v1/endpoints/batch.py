"""
Batch processing endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.batch import (
    BatchCreate, BatchStatus, BatchResponse,
    BatchListResponse
)
from app.services.batch_service import BatchService

router = APIRouter()
public_router = APIRouter()


@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_data: BatchCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new batch processing job."""
    batch_service = BatchService(db)
    
    # Create batch record
    batch = await batch_service.create_batch(
        user_id=current_user.id,
        collection_path=batch_data.collection_path,
        options=batch_data.options
    )
    
    # Start processing in background
    background_tasks.add_task(
        batch_service.process_batch,
        batch_id=batch.id
    )
    
    return batch


@router.get("/", response_model=BatchListResponse)
async def list_batches(
    page: int = 1,
    limit: int = 20,
    status: Optional[BatchStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's batch processing jobs."""
    batch_service = BatchService(db)
    
    batches = await batch_service.list_batches(
        user_id=current_user.id,
        page=page,
        limit=limit,
        status=status
    )
    
    return batches


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get batch processing status."""
    batch_service = BatchService(db)
    
    batch = await batch_service.get_batch(
        batch_id=batch_id,
        user_id=current_user.id
    )
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    return batch


@router.post("/{batch_id}/cancel")
async def cancel_batch(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running batch job."""
    batch_service = BatchService(db)
    
    success = await batch_service.cancel_batch(
        batch_id=batch_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel batch"
        )
    
    return {"message": "Batch cancelled successfully"}


@router.websocket("/{batch_id}/progress")
async def batch_progress_websocket(
    websocket: WebSocket,
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time batch progress updates."""
    await websocket.accept()
    
    batch_service = BatchService(db)
    
    try:
        # For now, skip authentication in WebSocket
        # In production, you'd validate a token sent in the connection
        
        # Verify batch exists
        batch = await batch_service.get_batch_by_id(batch_id)
        if not batch:
            await websocket.close(code=4004, reason="Batch not found")
            return
        
        # Send progress updates
        async for progress in batch_service.watch_progress(batch_id):
            await websocket.send_json({
                "type": "progress",
                "data": progress.dict()
            })
            
            if progress.status in ["completed", "failed", "cancelled"]:
                break
                
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))


# Public endpoints for testing (no auth required)
@public_router.post("/")
async def create_batch_public(
    background_tasks: BackgroundTasks,
    collection_path: str = Form(...),
    batch_size: int = Form(5),
    vibe_analysis: bool = Form(False),
    groove_analysis: bool = Form(False),
    era_detection: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    """Create a new batch processing job (PUBLIC - no auth)."""
    try:
        from app.schemas.batch import BatchCreate

        # Create options dict from form data
        options = {
            "vibe_analysis": vibe_analysis,
            "groove_analysis": groove_analysis,
            "era_detection": era_detection
        }

        # Create batch data
        batch_data = BatchCreate(
            collection_path=collection_path,
            batch_size=batch_size,
            options=options
        )

        batch_service = BatchService(db)

        # Use demo user ID 1
        batch = await batch_service.create_batch(
            user_id=1,
            collection_path=batch_data.collection_path,
            options=batch_data.options
        )

        # Start processing in background
        background_tasks.add_task(
            batch_service.process_batch,
            batch_id=batch.id
        )

        return batch
    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@public_router.get("/")
async def list_batches_public(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List batch processing jobs (PUBLIC - no auth)."""
    batch_service = BatchService(db)

    # Convert string status to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = BatchStatus(status)
        except ValueError:
            pass

    batches = await batch_service.list_batches(
        user_id=1,  # Demo user
        page=page,
        limit=limit,
        status=status_enum
    )

    # Return JSON for API requests
    return batches


@public_router.get("/{batch_id}")
async def get_batch_public(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get batch processing status (PUBLIC - no auth)."""
    batch_service = BatchService(db)

    batch = await batch_service.get_batch(
        batch_id=batch_id,
        user_id=1  # Demo user
    )

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    return batch


@public_router.post("/{batch_id}/import")
async def import_batch_results(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Import batch results into samples table."""
    try:
        batch_service = BatchService(db)

        # Get batch
        batch = await batch_service.get_batch(
            batch_id=batch_id,
            user_id=1  # Demo user
        )

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )

        if batch.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch processing not completed"
            )

        # Import the results
        imported_count = await batch_service.import_results_to_samples(batch_id)

        return {"status": "success", "imported_count": imported_count}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@public_router.post("/{batch_id}/cancel")
async def cancel_batch_public(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running batch job (PUBLIC - no auth)."""
    try:
        batch_service = BatchService(db)

        success = await batch_service.cancel_batch(
            batch_id=batch_id,
            user_id=1  # Demo user
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel batch"
            )

        return {"message": "Batch cancelled successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@public_router.post("/{batch_id}/retry")
async def retry_batch_public(
    batch_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed batch job."""
    try:
        batch_service = BatchService(db)

        # Get the failed batch
        batch = await batch_service.get_batch(
            batch_id=batch_id,
            user_id=1  # Demo user
        )

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )

        # Validate it's in FAILED status
        if batch.status != "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot retry batch with status: {batch.status}"
            )

        # Create new batch with same collection_path and options
        new_batch = await batch_service.create_batch(
            user_id=1,  # Demo user
            collection_path=batch.collection_path,
            options=batch.options
        )

        # Start processing in background
        background_tasks.add_task(
            batch_service.process_batch,
            batch_id=new_batch.id
        )

        return new_batch

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@public_router.get("/{batch_id}/export")
async def export_batch_results(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download batch results as JSON file."""
    try:
        batch_service = BatchService(db)

        # Get batch
        batch = await batch_service.get_batch(
            batch_id=batch_id,
            user_id=1  # Demo user
        )

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )

        # Check if export_path exists
        export_path = Path(batch.export_path) if batch.export_path else None

        if not export_path or not export_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export file not found. Batch may not be completed."
            )

        # Return file with download headers
        return FileResponse(
            path=str(export_path),
            media_type="application/json",
            filename=f"batch_{batch_id}_results.json"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )