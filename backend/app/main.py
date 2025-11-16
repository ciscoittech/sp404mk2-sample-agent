"""
FastAPI application entry point
"""
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.websocket import websocket_endpoint
from app.db import init_models  # Import all models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    print("Starting up SP404MK2 Sample Agent API...")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler to convert Pydantic ValidationError to 400 instead of 422
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert 422 validation errors to 400 bad request."""
    # Extract first error message
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        msg = first_error.get('msg', 'Validation error')
        field = first_error.get('loc', [])[-1] if first_error.get('loc') else 'field'
        detail = f"{field}: {msg}"
    else:
        detail = "Validation error"

    return JSONResponse(
        status_code=400,
        content={"detail": detail}
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Import templates and paths from shared config to avoid circular imports
from app.templates_config import templates, frontend_dir


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


# Template routes for pages that use Jinja2
@app.get("/pages/usage.html")
async def usage_page(request: Request):
    """Render usage page with Jinja2 template."""
    return templates.TemplateResponse("pages/usage.html", {"request": request})


@app.get("/pages/settings.html")
async def settings_page(request: Request):
    """Render settings page with Jinja2 template."""
    return templates.TemplateResponse("pages/settings.html", {"request": request})


# Mount static files from frontend (after specific routes)
# Try local path first, then Docker path
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")
    # Serve other frontend pages as static files
    app.mount("/pages", StaticFiles(directory=os.path.join(frontend_dir, "pages"), html=True), name="pages")
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="root")


# WebSocket endpoint
@app.websocket("/ws/vibe/{sample_id}")
async def websocket_vibe_analysis(websocket: WebSocket, sample_id: int):
    """WebSocket endpoint for real-time vibe analysis."""
    from app.db.session import get_db
    async for db in get_db():
        await websocket_endpoint(websocket, sample_id, db)
        break