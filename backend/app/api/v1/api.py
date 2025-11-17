"""
API v1 router aggregation
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, samples, public, batch, usage, preferences, sp404_export, kits, vibe_search, projects

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(samples.router, prefix="/samples", tags=["samples"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(batch.public_router, prefix="/public/batch", tags=["public-batch"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(samples.public_router, prefix="/public/samples", tags=["public-samples"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(usage.public_router, prefix="/public/usage", tags=["public-usage"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(sp404_export.router, prefix="/sp404", tags=["sp404-export"])
api_router.include_router(kits.router, prefix="/kits", tags=["kits"])
api_router.include_router(vibe_search.router, prefix="/search", tags=["vibe-search"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])