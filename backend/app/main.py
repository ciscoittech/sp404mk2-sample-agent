"""
FastAPI application entry point
"""
from fastapi import FastAPI, WebSocket
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

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Template setup
templates = Jinja2Templates(directory="/app/backend/templates")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


# Mount static files from frontend (after specific routes)
frontend_dir = "/app/frontend"
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")
    # Serve frontend pages
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