"""
Batch processing endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.batch import (
    BatchCreate, BatchStatus, BatchResponse, 
    BatchProgress, BatchListResponse
)
from app.services.batch_service import BatchService

router = APIRouter()


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


@router.ws("/{batch_id}/progress")
async def batch_progress_websocket(
    websocket: WebSocket,
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time batch progress updates."""
    await websocket.accept()
    
    batch_service = BatchService(db)
    
    try:
        # Verify batch ownership
        batch = await batch_service.get_batch(batch_id, current_user.id)
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