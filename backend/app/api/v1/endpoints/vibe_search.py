"""
Vibe Search API endpoints for semantic sample discovery.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db
from app.services.embedding_service import EmbeddingService, EmbeddingError
from app.services.vibe_search_service import VibeSearchService
from app.services.usage_tracking_service import UsageTrackingService

router = APIRouter()


class VibeSearchResult(BaseModel):
    """Single search result with sample metadata and similarity score."""
    id: int = Field(..., description="Sample ID")
    title: str = Field(..., description="Sample title")
    bpm: Optional[float] = Field(None, description="Beats per minute")
    musical_key: Optional[str] = Field(None, description="Musical key")
    genre: Optional[str] = Field(None, description="Genre classification")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    similarity: float = Field(..., description="Similarity score (0-1)", ge=0, le=1)

    # Vibe analysis fields
    mood: Optional[str] = Field(None, description="Primary mood")
    mood_secondary: Optional[str] = Field(None, description="Secondary mood")
    energy_level: Optional[float] = Field(None, description="Energy level (0-1)")
    danceability: Optional[float] = Field(None, description="Danceability score (0-1)")
    vibe_tags: List[str] = Field(default_factory=list, description="Texture/vibe tags")
    acousticness: Optional[float] = Field(None, description="Acousticness score (0-1)")
    instrumentalness: Optional[float] = Field(None, description="Instrumentalness score (0-1)")

    # URLs
    preview_url: str = Field(..., description="Preview/streaming URL")
    full_url: str = Field(..., description="Full download URL")


class VibeSearchResponse(BaseModel):
    """Response model for vibe search endpoint."""
    query: str = Field(..., description="Original search query")
    results: List[VibeSearchResult] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results returned")
    execution_time_ms: int = Field(..., description="Query execution time in milliseconds")


class SimilarSamplesResponse(BaseModel):
    """Response model for similar samples endpoint."""
    reference_sample_id: int = Field(..., description="ID of reference sample")
    results: List[VibeSearchResult] = Field(..., description="Similar samples")
    count: int = Field(..., description="Number of results returned")


def get_embedding_service(db: AsyncSession = Depends(get_db)) -> EmbeddingService:
    """Dependency for embedding service."""
    usage_service = UsageTrackingService(db)
    return EmbeddingService(usage_service)


def get_vibe_search_service(
    db: AsyncSession = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> VibeSearchService:
    """Dependency for vibe search service."""
    return VibeSearchService(embedding_service, db)


@router.get("/vibe", response_model=VibeSearchResponse)
async def search_samples_by_vibe(
    query: str = Query(..., description="Natural language search query", min_length=1),
    limit: int = Query(20, description="Maximum results to return", ge=1, le=100),
    bpm_min: Optional[float] = Query(None, description="Minimum BPM", ge=0),
    bpm_max: Optional[float] = Query(None, description="Maximum BPM", ge=0),
    genre: Optional[str] = Query(None, description="Genre filter (exact match)"),
    energy_min: Optional[float] = Query(None, description="Minimum energy level", ge=0, le=1),
    energy_max: Optional[float] = Query(None, description="Maximum energy level", ge=0, le=1),
    danceability_min: Optional[float] = Query(None, description="Minimum danceability", ge=0, le=1),
    danceability_max: Optional[float] = Query(None, description="Maximum danceability", ge=0, le=1),
    vibe_search_service: VibeSearchService = Depends(get_vibe_search_service)
):
    """
    Search for samples using natural language queries and semantic similarity.

    Performs vector search on sample embeddings to find samples that match the
    vibe/mood described in the query. Supports filtering by BPM, genre, energy, etc.

    Example queries:
    - "dark moody loop"
    - "energetic trap drums"
    - "chill jazz piano"
    - "aggressive 808 bass"
    """
    try:
        results = await vibe_search_service.search_by_vibe(
            query=query,
            limit=limit,
            filters={
                "bpm_min": bpm_min,
                "bpm_max": bpm_max,
                "genre": genre,
                "energy_min": energy_min,
                "energy_max": energy_max,
                "danceability_min": danceability_min,
                "danceability_max": danceability_max
            }
        )

        # Format results - remove fields not in response model, add placeholder URLs
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result.get("id"),
                "title": result.get("title"),
                "bpm": result.get("bpm"),
                "musical_key": result.get("musical_key"),
                "genre": result.get("genre"),
                "duration": result.get("duration"),
                "similarity": result.get("similarity"),
                "mood": result.get("mood_primary"),
                "mood_secondary": result.get("mood_secondary"),
                "energy_level": result.get("energy_level"),
                "danceability": result.get("danceability"),
                "vibe_tags": result.get("vibe_tags", []),
                "acousticness": result.get("acousticness"),
                "instrumentalness": result.get("instrumentalness"),
                "preview_url": f"/api/v1/samples/{result.get('id')}/preview",
                "full_url": f"/api/v1/samples/{result.get('id')}/download"
            }
            formatted_results.append(formatted_result)

        return VibeSearchResponse(
            query=query,
            results=formatted_results,
            count=len(formatted_results),
            execution_time_ms=0
        )

    except EmbeddingError as e:
        raise HTTPException(status_code=400, detail=f"Embedding error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/similar/{sample_id}", response_model=SimilarSamplesResponse)
async def get_similar_samples(
    sample_id: int,
    limit: int = Query(10, description="Maximum results to return", ge=1, le=50),
    vibe_search_service: VibeSearchService = Depends(get_vibe_search_service)
):
    """
    Find samples similar to a given sample based on vibe/characteristics.

    Uses the sample's embedding to find other samples with similar sonic and
    musical characteristics.
    """
    try:
        results = await vibe_search_service.find_similar(
            sample_id=sample_id,
            limit=limit
        )

        # Format results - remove fields not in response model, add placeholder URLs
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result.get("id"),
                "title": result.get("title"),
                "bpm": result.get("bpm"),
                "musical_key": result.get("musical_key"),
                "genre": result.get("genre"),
                "duration": result.get("duration"),
                "similarity": result.get("similarity"),
                "mood": result.get("mood_primary"),
                "mood_secondary": result.get("mood_secondary"),
                "energy_level": result.get("energy_level"),
                "danceability": result.get("danceability"),
                "vibe_tags": result.get("vibe_tags", []),
                "acousticness": result.get("acousticness"),
                "instrumentalness": result.get("instrumentalness"),
                "preview_url": f"/api/v1/samples/{result.get('id')}/preview",
                "full_url": f"/api/v1/samples/{result.get('id')}/download"
            }
            formatted_results.append(formatted_result)

        return SimilarSamplesResponse(
            reference_sample_id=sample_id,
            results=formatted_results,
            count=len(formatted_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar samples search failed: {str(e)}")
