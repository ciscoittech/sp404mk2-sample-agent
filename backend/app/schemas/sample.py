"""
Pydantic schemas for samples
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class SampleBase(BaseModel):
    """Base sample schema."""
    title: str = Field(..., min_length=1, max_length=200)
    genre: Optional[str] = None
    bpm: Optional[float] = Field(None, ge=20, le=300)
    musical_key: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class SampleCreate(SampleBase):
    """Schema for creating a sample (form data)."""
    pass


class SampleUpdate(BaseModel):
    """Schema for updating a sample."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    genre: Optional[str] = None
    bpm: Optional[float] = Field(None, ge=20, le=300)
    musical_key: Optional[str] = None
    tags: Optional[List[str]] = None


class SampleInDBBase(SampleBase):
    """Base schema for sample in database."""
    id: int
    user_id: int
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Sample(SampleInDBBase):
    """Schema for sample responses."""
    file_url: Optional[str] = None  # Generated URL for file access
    vibe_analysis: Optional['VibeAnalysisResponse'] = None


class SampleInDB(SampleInDBBase):
    """Schema for sample in database."""
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class SampleListResponse(BaseModel):
    """Response schema for paginated sample list."""
    items: List[Sample]
    total: int
    page: int
    pages: int
    limit: int


class VibeAnalysisResponse(BaseModel):
    """Schema for vibe analysis results."""
    mood_primary: str
    mood_secondary: Optional[str] = None
    energy_level: float = Field(..., ge=0, le=1)
    danceability: Optional[float] = Field(None, ge=0, le=1)
    acousticness: Optional[float] = Field(None, ge=0, le=1)
    instrumentalness: Optional[float] = Field(None, ge=0, le=1)
    texture_tags: List[str] = Field(default_factory=list)
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(..., ge=0, le=1)
    
    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Request to analyze a sample."""
    force_reanalyze: bool = False


class AnalysisResponse(BaseModel):
    """Response when analysis is triggered."""
    status: str
    message: str
    job_id: Optional[str] = None


# Update forward reference
Sample.model_rebuild()