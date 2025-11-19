"""
FastAPI application entry point
"""
from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


# Serve React app from react-app/dist (Vite build output)
import os
react_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "react-app", "dist")
if os.path.exists(react_dist):
    # Mount static assets
    assets_path = os.path.join(react_dist, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    # Serve index.html for all other routes (React Router will handle routing)
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        """Serve React app for all routes (SPA)."""
        index_path = os.path.join(react_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="React app not found")


# WebSocket endpoint
@app.websocket("/ws/vibe/{sample_id}")
async def websocket_vibe_analysis(websocket: WebSocket, sample_id: int):
    """WebSocket endpoint for real-time vibe analysis."""
    from app.db.session import get_db
    async for db in get_db():
        await websocket_endpoint(websocket, sample_id, db)
        break