"""
Pydantic schemas for audio features and analysis debug information
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BPMDebugInfo(BaseModel):
    """Detailed BPM analysis info."""
    value: Optional[float] = None
    confidence: Optional[int] = None
    raw_value: Optional[float] = None
    was_corrected: Optional[bool] = None
    method: Optional[str] = None


class GenreDebugInfo(BaseModel):
    """Detailed genre analysis info."""
    value: Optional[str] = None
    confidence: Optional[int] = None
    sp404_category: Optional[str] = None
    top_3: Optional[List[Dict[str, Any]]] = None


class AnalysisDebugResponse(BaseModel):
    """Full analysis debug information."""
    sample_id: int
    bpm: BPMDebugInfo
    genre: Optional[GenreDebugInfo] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AudioFeaturesBase(BaseModel):
    """Base audio features schema."""
    bpm: Optional[float] = None
    bpm_confidence: Optional[int] = Field(None, ge=0, le=100)
    genre: Optional[str] = None
    genre_confidence: Optional[int] = Field(None, ge=0, le=100)
    key: Optional[str] = None
    key_confidence: Optional[int] = Field(None, ge=0, le=100)


class AudioFeaturesResponse(AudioFeaturesBase):
    """API response with confidence scores."""
    id: int
    sample_id: int
    analysis_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
