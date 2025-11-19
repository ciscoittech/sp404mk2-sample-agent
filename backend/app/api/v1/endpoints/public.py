"""
Public endpoints (no auth required) - for development/testing
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.sample_service import SampleService
from app.schemas.sample import SampleCreate, SampleListResponse, Sample
import os
import json
from pathlib import Path

router = APIRouter()


@router.get("/samples/", response_model=SampleListResponse)
async def list_public_samples(
    page: int = 1,
    limit: int = 100,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    bpm_min: Optional[float] = None,
    bpm_max: Optional[float] = None,
    instrument_type: Optional[str] = None,
    sample_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all samples without authentication (for development)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 10000:
        limit = 100

    skip = (page - 1) * limit

    sample_service = SampleService(db)

    # Get samples with filters (no user_id filter)
    if search or genre or bpm_min or bpm_max or instrument_type or sample_type:
        samples = await sample_service.search_samples(
            user_id=None,  # Show all samples
            search=search,
            genre=genre,
            bpm_min=bpm_min,
            bpm_max=bpm_max,
            instrument_type=instrument_type,
            sample_type=sample_type,
            skip=skip,
            limit=limit
        )
    else:
        samples = await sample_service.get_samples(
            user_id=None,  # Show all samples
            skip=skip,
            limit=limit
        )

    total = await sample_service.count_user_samples(None)

    # Convert ORM models to dicts to avoid lazy loading issues with Pydantic
    sample_dicts = []
    for sample in samples:
        # Extract vibe analysis from extra_metadata to avoid lazy-load relationships
        vibe_analysis = None
        if sample.extra_metadata and isinstance(sample.extra_metadata, dict):
            vibe_data = sample.extra_metadata.get('vibe_analysis')
            if vibe_data:
                vibe_analysis = vibe_data

        # Convert ORM object to dict, handling NULL values
        sample_dict = {
            "id": sample.id,
            "user_id": sample.user_id,
            "title": sample.title,
            "genre": sample.genre,
            "bpm": sample.bpm,
            "musical_key": sample.musical_key,
            "tags": sample.tags if sample.tags is not None else [],  # Handle NULL tags
            "file_path": sample.file_path,
            "file_size": sample.file_size,
            "duration": sample.duration,
            "created_at": sample.created_at,
            "analyzed_at": sample.analyzed_at,
            "last_accessed_at": sample.last_accessed_at,
            "bpm_confidence": sample.bpm_confidence,
            "genre_confidence": sample.genre_confidence,
            "key_confidence": sample.key_confidence,
            "file_url": f"/api/v1/public/samples/{sample.id}/download",
            "vibe_analysis": vibe_analysis
        }
        sample_dicts.append(sample_dict)

    # Calculate pages
    pages = (total + limit - 1) // limit
    has_more = page < pages

    # Return JSON for API requests - create Sample objects from dicts for Pydantic validation
    sample_objects = [Sample(**d) for d in sample_dicts]
    return SampleListResponse(
        items=sample_objects,
        total=total,
        page=page,
        pages=pages,
        limit=limit
    )


@router.post("/samples/", response_model=Sample, status_code=status.HTTP_201_CREATED)
async def upload_sample_public(
    file: UploadFile = File(...),
    title: str = Form(...),
    genre: Optional[str] = Form(None, alias="upload-genre"),
    bpm: Optional[str] = Form(None),  # Accept as string then convert
    musical_key: Optional[str] = Form(None),
    tags: Optional[str] = Form(""),  # Default to empty string
    db: AsyncSession = Depends(get_db)
):
    """Upload a sample without authentication (for demo purposes)."""
    print(f"Upload attempt: title={title}, file={file.filename}, genre={genre}, bpm={bpm}, tags='{tags}'")
    
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = "." + file.filename.split(".")[-1].lower()
    allowed_extensions = {".wav", ".mp3", ".flac", ".aiff", ".m4a", ".ogg"}
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Convert BPM to float if provided
    bpm_float = None
    if bpm and bpm.strip():
        try:
            bpm_float = float(bpm)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BPM must be a valid number"
            )
    
    # Convert empty genre to None
    if genre and not genre.strip():
        genre = None
    
    # Convert empty musical_key to None  
    if musical_key and not musical_key.strip():
        musical_key = None
    
    # Parse tags from JSON string or comma-separated
    tags_list = []
    if tags and tags.strip():
        try:
            # Try parsing as JSON first
            tags_list = json.loads(tags)
        except json.JSONDecodeError:
            # If not JSON, treat as comma-separated string
            tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Create sample data
    sample_data = SampleCreate(
        title=title,
        genre=genre,
        bpm=bpm_float,
        musical_key=musical_key,
        tags=tags_list
    )
    
    # Create sample with demo user (user_id=1)
    sample_service = SampleService(db)
    sample = await sample_service.create_sample(
        data=sample_data,
        file=file,
        user_id=1  # Demo user
    )
    
    # Add file URL for response
    sample.file_url = f"/api/v1/public/samples/{sample.id}/download"
    
    return sample


@router.post("/samples/{sample_id}/analyze")
async def analyze_sample_public(
    sample_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger AI analysis on a sample without authentication (for demo purposes)."""
    from app.services.sample_service import SampleService
    
    sample_service = SampleService(db)
    
    # Check if sample exists (no user filter for public endpoint)
    sample = await sample_service.get_sample_by_id(
        sample_id=sample_id,
        user_id=None
    )
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    # Queue analysis
    job_id = await sample_service.analyze_sample(sample_id)

    # Return JSON for API requests
    return {
        "status": "processing",
        "message": "Analysis queued",
        "job_id": job_id
    }


@router.get("/debug/env")
async def debug_environment():
    """Debug endpoint to check environment."""
    cwd = os.getcwd()
    
    # Check various paths
    paths_to_check = [
        "test_batch_collection",
        "../test_batch_collection", 
        "/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/test_batch_collection"
    ]
    
    results = {}
    for path in paths_to_check:
        full_path = os.path.abspath(path)
        results[path] = {
            "exists": os.path.exists(path),
            "is_dir": os.path.isdir(path) if os.path.exists(path) else None,
            "absolute": full_path
        }
    
    return {
        "working_directory": cwd,
        "paths": results,
        "directory_contents": os.listdir(".") if os.path.exists(".") else []
    }
