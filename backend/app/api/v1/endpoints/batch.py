"""
Batch processing endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, Request, Header, Form
from fastapi.responses import HTMLResponse
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
    request: Request,
    background_tasks: BackgroundTasks,
    collection_path: str = Form(...),
    batch_size: int = Form(5),
    vibe_analysis: bool = Form(False),
    groove_analysis: bool = Form(False),
    era_detection: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None)
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
        
        # Return HTML response for HTMX
        if hx_request:
            return HTMLResponse(content=f"""
            <div class="alert alert-success">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>Batch processing started! Check the Active Processing section for progress.</span>
            </div>
            """)
        
        return batch
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        if hx_request:
            return HTMLResponse(content=f"""
            <div class="alert alert-error">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>Error starting batch: {str(e)}</span>
            </div>
            """)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@public_router.get("/")
async def list_batches_public(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None)
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
    
    # Return HTML for HTMX requests
    if hx_request:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="/app/backend/templates")
        
        # Return different templates based on status filter
        if status == "processing":
            return templates.TemplateResponse("partials/active-batches.html", {
                "request": request,
                "batches": batches.items if batches else []
            })
        else:
            return templates.TemplateResponse("partials/batch-history.html", {
                "request": request,
                "batches": batches.items if batches else []
            })
    
    # Return JSON for API requests
    return batches


@public_router.get("/{batch_id}")
async def get_batch_public(
    batch_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None)
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
    
    # Return HTML for HTMX requests
    if hx_request:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="/app/backend/templates")
        
        return templates.TemplateResponse("partials/batch-details.html", {
            "request": request,
            "batch": batch
        })
    
    return batch


@public_router.post("/{batch_id}/import")
async def import_batch_results(
    batch_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None)
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
        
        # Return HTML for HTMX
        if hx_request:
            return HTMLResponse(content=f"""
            <div class="alert alert-success">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>Successfully imported {imported_count} samples! View them on the <a href="/pages/samples.html" class="link">Samples page</a>.</span>
            </div>
            """)
        
        return {"status": "success", "imported_count": imported_count}
        
    except Exception as e:
        if hx_request:
            return HTMLResponse(content=f"""
            <div class="alert alert-error">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>Error importing results: {str(e)}</span>
            </div>
            """)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )