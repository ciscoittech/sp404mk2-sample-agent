"""
Sample management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.sample import (
    SampleCreate, Sample, SampleUpdate, 
    SampleListResponse, AnalysisRequest, AnalysisResponse
)
from app.services.sample_service import SampleService

templates = Jinja2Templates(directory="templates")


router = APIRouter()
public_router = APIRouter()

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".aiff", ".m4a", ".ogg"}


def validate_audio_file(file: UploadFile) -> None:
    """Validate that uploaded file is an audio file."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = "." + file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/", response_model=Sample, status_code=status.HTTP_201_CREATED)
async def create_sample(
    file: UploadFile = File(...),
    title: str = Form(...),
    genre: Optional[str] = Form(None),
    bpm: Optional[float] = Form(None),
    musical_key: Optional[str] = Form(None),
    tags: Optional[str] = Form("[]"),  # JSON string
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new sample with file upload."""
    # Validate file
    validate_audio_file(file)
    
    # Parse tags from JSON string
    try:
        tags_list = json.loads(tags) if tags else []
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tags format. Must be JSON array."
        )
    
    # Create sample data
    sample_data = SampleCreate(
        title=title,
        genre=genre,
        bpm=bpm,
        musical_key=musical_key,
        tags=tags_list
    )
    
    # Create sample
    sample_service = SampleService(db)
    sample = await sample_service.create_sample(
        data=sample_data,
        file=file,
        user_id=current_user.id
    )
    
    # Add file URL for response
    sample.file_url = f"/api/v1/samples/{sample.id}/download"
    
    return sample


@router.get("/")
async def list_samples(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    bpm_min: Optional[float] = None,
    bpm_max: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None)
):
    """List user's samples with pagination."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    
    skip = (page - 1) * limit
    
    sample_service = SampleService(db)
    
    user_id = current_user.id
    
    # Get samples with filters
    if search or genre or bpm_min or bpm_max:
        samples = await sample_service.search_samples(
            user_id=user_id,
            search=search,
            genre=genre,
            bpm_min=bpm_min,
            bpm_max=bpm_max,
            skip=skip,
            limit=limit
        )
    else:
        samples = await sample_service.get_samples(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
    
    total = await sample_service.count_user_samples(user_id)
    
    # Add file URLs
    for sample in samples:
        sample.file_url = f"/api/v1/samples/{sample.id}/download"
    
    # Calculate pages
    pages = (total + limit - 1) // limit
    has_more = page < pages
    
    # Return HTML for HTMX requests
    if hx_request:
        return templates.TemplateResponse("partials/sample-grid.html", {
            "request": request,
            "samples": samples,
            "has_more": has_more,
            "next_page": page + 1
        })
    
    # Return JSON for API requests
    return {
        "items": samples,
        "total": total,
        "page": page,
        "pages": pages,
        "limit": limit
    }


@router.get("/search", response_model=List[Sample])
async def search_samples(
    q: Optional[str] = None,
    genre: Optional[str] = None,
    bpm_min: Optional[float] = None,
    bpm_max: Optional[float] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search samples with filters."""
    sample_service = SampleService(db)
    
    samples = await sample_service.search_samples(
        user_id=current_user.id,
        search=q,
        genre=genre,
        bpm_min=bpm_min,
        bpm_max=bpm_max,
        limit=limit
    )
    
    # Add file URLs
    for sample in samples:
        sample.file_url = f"/api/v1/samples/{sample.id}/download"
    
    return samples


@router.get("/{sample_id}", response_model=Sample)
async def get_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific sample by ID."""
    sample_service = SampleService(db)
    
    sample = await sample_service.get_sample_by_id(
        sample_id=sample_id,
        user_id=current_user.id
    )
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    # Add file URL
    sample.file_url = f"/api/v1/samples/{sample.id}/download"
    
    return sample


@router.patch("/{sample_id}", response_model=Sample)
async def update_sample(
    sample_id: int,
    update_data: SampleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update sample metadata."""
    sample_service = SampleService(db)
    
    sample = await sample_service.update_sample(
        sample_id=sample_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    # Add file URL
    sample.file_url = f"/api/v1/samples/{sample.id}/download"
    
    return sample


@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a sample."""
    sample_service = SampleService(db)
    
    deleted = await sample_service.delete_sample(
        sample_id=sample_id,
        user_id=current_user.id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    return None


@router.post("/{sample_id}/analyze", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_sample(
    sample_id: int,
    request: AnalysisRequest = AnalysisRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger AI analysis on a sample."""
    sample_service = SampleService(db)
    
    # Check if sample exists and belongs to user
    sample = await sample_service.get_sample_by_id(
        sample_id=sample_id,
        user_id=current_user.id
    )
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    # Queue analysis
    job_id = await sample_service.analyze_sample(sample_id)
    
    return {
        "status": "processing",
        "message": "Analysis queued",
        "job_id": job_id
    }


@router.get("/{sample_id}/download")
async def download_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download sample file."""
    from fastapi.responses import FileResponse
    import os
    
    sample_service = SampleService(db)
    
    # Get sample
    sample = await sample_service.get_sample_by_id(
        sample_id=sample_id,
        user_id=current_user.id
    )
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    # Check if file exists
    if not os.path.exists(sample.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample file not found"
        )
    
    # Return file
    return FileResponse(
        path=sample.file_path,
        filename=f"{sample.title}{os.path.splitext(sample.file_path)[1]}",
        media_type="audio/*"
    )


# Public endpoints (no authentication required)
@public_router.get("/")
async def list_samples_public(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    bpm_min: Optional[float] = None,
    bpm_max: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None)
):
    """List all samples without authentication (public endpoint)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    
    skip = (page - 1) * limit
    
    sample_service = SampleService(db)
    
    # Get samples with filters (all users)
    if search or genre or bpm_min or bpm_max:
        samples = await sample_service.search_samples(
            user_id=None,  # No user filter for public endpoint
            search=search,
            genre=genre,
            bpm_min=bpm_min,
            bpm_max=bpm_max,
            skip=skip,
            limit=limit
        )
    else:
        samples = await sample_service.get_samples(
            user_id=None,  # No user filter for public endpoint
            skip=skip,
            limit=limit
        )
    
    total = await sample_service.count_all_samples()
    
    # Add file URLs
    for sample in samples:
        sample.file_url = f"/api/v1/public/samples/{sample.id}/download"
    
    # Calculate pages
    pages = (total + limit - 1) // limit
    has_more = page < pages
    
    # Return HTML for HTMX requests
    if hx_request:
        return templates.TemplateResponse("partials/sample-grid.html", {
            "request": request,
            "samples": samples,
            "has_more": has_more,
            "next_page": page + 1
        })
    
    # Return JSON for API requests
    return {
        "items": samples,
        "total": total,
        "page": page,
        "pages": pages,
        "limit": limit
    }


@public_router.get("/{sample_id}/download")
async def download_sample_public(
    sample_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Download sample file without authentication (public endpoint)."""
    from fastapi.responses import FileResponse
    import os
    
    sample_service = SampleService(db)
    
    # Get sample (no user filter)
    sample = await sample_service.get_sample_by_id(
        sample_id=sample_id,
        user_id=None  # No user filter for public endpoint
    )
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    # Check if file exists
    if not os.path.exists(sample.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample file not found"
        )
    
    # Return file
    return FileResponse(
        path=sample.file_path,
        filename=f"{sample.title}{os.path.splitext(sample.file_path)[1]}",
        media_type="audio/*"
    )