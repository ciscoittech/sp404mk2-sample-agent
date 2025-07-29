"""
API v1 router aggregation
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, samples, public, batch

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(samples.router, prefix="/samples", tags=["samples"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(public.router, prefix="/public", tags=["public"])