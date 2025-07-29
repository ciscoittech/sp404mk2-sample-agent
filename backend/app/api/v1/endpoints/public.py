"""
Public endpoints (no auth required) - for development/testing
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.sample_service import SampleService

router = APIRouter()


@router.get("/samples/")
async def list_public_samples(
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
    """List all samples without authentication (for development)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    
    skip = (page - 1) * limit
    
    sample_service = SampleService(db)
    
    # Get samples with filters (no user_id filter)
    if search or genre or bpm_min or bpm_max:
        samples = await sample_service.search_samples(
            user_id=None,  # Show all samples
            search=search,
            genre=genre,
            bpm_min=bpm_min,
            bpm_max=bpm_max,
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
    
    # Add file URLs
    for sample in samples:
        sample.file_url = f"/api/v1/samples/{sample.id}/download"
    
    # Calculate pages
    pages = (total + limit - 1) // limit
    has_more = page < pages
    
    # Return HTML for HTMX requests
    if hx_request:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="/app/backend/templates")
        
        # Convert SQLAlchemy models to simple dicts to avoid lazy loading issues
        sample_dicts = []
        for s in samples:
            sample_dict = {
                "id": s.id,
                "title": s.title,
                "genre": s.genre,
                "bpm": s.bpm,
                "musical_key": s.musical_key,
                "tags": s.tags,
                "file_url": s.file_url,
                "created_at": s.created_at,
                "vibe_analysis": None  # Skip for now to avoid async issues
            }
            sample_dicts.append(sample_dict)
        
        return templates.TemplateResponse("partials/sample-grid.html", {
            "request": request,
            "samples": sample_dicts,
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