# API Patterns - SP404MK2 Sample Agent

## FastAPI Endpoint Structure

### Basic Endpoint Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.sample import SampleCreate, SampleResponse
from app.services.sample_service import SampleService

router = APIRouter(prefix="/api/v1/samples", tags=["samples"])

@router.post("/", response_model=SampleResponse, status_code=201)
async def create_sample(
    request: Request,
    data: SampleCreate,
    db: AsyncSession = Depends(get_db)
) -> SampleResponse:
    """
    Create a new sample.

    - **name**: Sample name (required)
    - **file_path**: Path to audio file (required)
    - **genre**: Music genre (optional)
    - **bpm**: Beats per minute (optional)

    Returns the created sample with generated ID.
    """
    try:
        service = SampleService(db)
        sample = await service.create_sample(data)
        return SampleResponse.model_validate(sample)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create sample: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Dual Response Pattern (JSON + HTMX)

### Endpoint with Dual Response
```python
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="backend/templates")

@router.post("/", response_model=SampleResponse)
async def create_sample(
    request: Request,
    data: SampleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create sample - supports both JSON and HTMX responses."""
    # Business logic
    service = SampleService(db)
    sample = await service.create_sample(data)

    # HTMX request - return HTML template
    if "hx-request" in request.headers:
        return templates.TemplateResponse(
            "samples/sample-card.html",
            {
                "request": request,
                "sample": sample
            }
        )

    # Regular API request - return JSON
    return SampleResponse.model_validate(sample)
```

### HTMX Template (sample-card.html)
```html
<div class="card bg-base-100 shadow-xl" id="sample-{{ sample.id }}">
    <div class="card-body">
        <h2 class="card-title">{{ sample.name }}</h2>
        <p>{{ sample.description }}</p>

        <div class="flex gap-2">
            <div class="badge badge-primary">{{ sample.genre }}</div>
            <div class="badge badge-secondary">{{ sample.bpm }} BPM</div>
        </div>

        <div class="card-actions justify-end">
            <button hx-post="/api/v1/samples/{{ sample.id }}/analyze"
                    hx-target="#analysis-{{ sample.id }}"
                    class="btn btn-primary btn-sm">
                Analyze
            </button>
        </div>
    </div>
</div>
```

## File Upload Pattern

### Multipart Form Data Upload
```python
from fastapi import File, UploadFile, Form
from pathlib import Path

@router.post("/upload")
async def upload_sample(
    audio_file: UploadFile = File(...),
    name: str = Form(...),
    genre: str = Form(None, alias="upload-genre"),  # Alias for form conflicts
    description: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle multipart file upload with metadata."""

    # Validate file type
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(400, "Invalid audio file type")

    # Validate file size
    content = await audio_file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(400, f"File too large (max {MAX_UPLOAD_SIZE} bytes)")

    # Save file
    upload_dir = Path(UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / audio_file.filename
    with file_path.open("wb") as f:
        f.write(content)

    # Create database record
    service = SampleService(db)
    sample = await service.create_sample(
        SampleCreate(
            name=name,
            genre=genre,
            description=description,
            file_path=str(file_path)
        )
    )

    return SampleResponse.model_validate(sample)
```

## Pagination Pattern

### List with Pagination and Filters
```python
from typing import List, Optional

@router.get("/", response_model=List[SampleResponse])
async def list_samples(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    min_bpm: Optional[float] = Query(None),
    max_bpm: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> List[SampleResponse]:
    """
    List samples with pagination and filtering.

    - **page**: Page number (starts at 1)
    - **page_size**: Items per page (max 100)
    - **search**: Search in name/description
    - **genre**: Filter by genre
    - **min_bpm/max_bpm**: BPM range filter
    """
    offset = (page - 1) * page_size

    # Build query
    query = select(Sample)

    # Apply filters
    if search:
        query = query.where(
            or_(
                Sample.name.ilike(f"%{search}%"),
                Sample.description.ilike(f"%{search}%")
            )
        )

    if genre:
        query = query.where(Sample.genre == genre)

    if min_bpm is not None:
        query = query.where(Sample.bpm >= min_bpm)

    if max_bpm is not None:
        query = query.where(Sample.bpm <= max_bpm)

    # Apply pagination
    query = query.offset(offset).limit(page_size).order_by(Sample.created_at.desc())

    # Execute
    result = await db.execute(query)
    samples = result.scalars().all()

    return [SampleResponse.model_validate(s) for s in samples]
```

## Background Tasks Pattern

### Long-Running Operations
```python
from fastapi import BackgroundTasks
import asyncio

@router.post("/batches/{batch_id}/analyze")
async def analyze_batch(
    batch_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start batch analysis in background."""

    # Validate batch exists
    batch = await db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(404, "Batch not found")

    # Queue background task
    background_tasks.add_task(analyze_batch_task, batch_id)

    return {
        "status": "processing",
        "batch_id": batch_id,
        "message": "Analysis started in background"
    }

async def analyze_batch_task(batch_id: int):
    """Background task for batch analysis."""
    async with AsyncSessionLocal() as db:
        try:
            service = BatchService(db)
            await service.analyze_batch(batch_id)
            logger.info(f"Batch {batch_id} analysis complete")
        except Exception as e:
            logger.error(f"Batch {batch_id} analysis failed: {e}")
```

## WebSocket Pattern

### Real-Time Updates
```python
from fastapi import WebSocket, WebSocketDisconnect

@router.websocket("/ws/vibe-analysis/{sample_id}")
async def vibe_analysis_websocket(
    websocket: WebSocket,
    sample_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Real-time vibe analysis updates via WebSocket."""
    await websocket.accept()

    try:
        # Get sample
        sample = await db.get(Sample, sample_id)
        if not sample:
            await websocket.send_json({"status": "error", "message": "Sample not found"})
            return

        # Phase 1: Audio feature extraction
        await websocket.send_json({"status": "extracting_features", "progress": 30})
        audio_service = AudioFeaturesService()
        features = await audio_service.extract_features(sample.file_path)

        # Phase 2: AI vibe analysis
        await websocket.send_json({"status": "analyzing_vibe", "progress": 70})
        openrouter_service = OpenRouterService(OPENROUTER_API_KEY, db)
        vibe = await openrouter_service.analyze_vibe(features)

        # Complete
        await websocket.send_json({
            "status": "complete",
            "progress": 100,
            "result": vibe
        })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for sample {sample_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        await websocket.close()
```

## Error Handling Pattern

### Consistent Error Responses
```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    details: Optional[dict] = None

@router.post("/samples")
async def create_sample(data: SampleCreate, db: AsyncSession = Depends(get_db)):
    """Create sample with comprehensive error handling."""
    try:
        service = SampleService(db)
        sample = await service.create_sample(data)
        return SampleResponse.model_validate(sample)

    except ValueError as e:
        # Validation error
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="ValidationError",
                message=str(e)
            ).model_dump()
        )

    except FileNotFoundError as e:
        # File not found
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="FileNotFoundError",
                message="Audio file not found",
                details={"file_path": str(e)}
            ).model_dump()
        )

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error creating sample: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred"
            ).model_dump()
        )
```

## Dependency Injection Patterns

### Database Session
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Service Dependencies
```python
def get_sample_service(db: AsyncSession = Depends(get_db)) -> SampleService:
    """Dependency for sample service."""
    return SampleService(db)

@router.get("/samples/{id}")
async def get_sample(
    id: int,
    service: SampleService = Depends(get_sample_service)
):
    """Get sample using injected service."""
    sample = await service.get_sample(id)
    if not sample:
        raise HTTPException(404, "Sample not found")
    return SampleResponse.model_validate(sample)
```

## Router Registration

### Main API Router (backend/app/api/v1/api.py)
```python
from fastapi import APIRouter
from app.api.v1.endpoints import public, batch, usage, preferences, sp404_export

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(public.router, tags=["samples"])
api_router.include_router(batch.router, prefix="/batches", tags=["batches"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(sp404_export.router, prefix="/sp404", tags=["sp404-export"])
```

### Main Application (backend/app/main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="SP404MK2 Sample Agent API",
    version="1.0.0",
    description="AI-powered sample collection for Roland SP-404MK2"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(api_router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## HTTP Status Codes

### Standard Usage
- **200**: Success (GET, PATCH, DELETE)
- **201**: Created (POST)
- **204**: No Content (DELETE without body)
- **400**: Bad Request (validation error)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (resource doesn't exist)
- **409**: Conflict (duplicate resource)
- **422**: Unprocessable Entity (Pydantic validation)
- **500**: Internal Server Error (unexpected error)
