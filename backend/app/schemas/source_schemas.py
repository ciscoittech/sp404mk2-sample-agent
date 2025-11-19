"""
Pydantic schemas for sample sources
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SourceTypeEnum(str, Enum):
    """Source type enumeration for sample origins."""
    YOUTUBE = "youtube"
    UPLOAD = "upload"
    SAMPLE_PACK = "sample_pack"
    BATCH_IMPORT = "batch_import"


class LicenseTypeEnum(str, Enum):
    """License type enumeration for sample usage rights."""
    ROYALTY_FREE = "royalty_free"
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"


class SampleSourceCreate(BaseModel):
    """Schema for creating a sample source."""
    source_type: SourceTypeEnum
    source_url: Optional[str] = Field(None, max_length=2048)
    artist: Optional[str] = Field(None, max_length=255)
    album: Optional[str] = Field(None, max_length=255)
    release_date: Optional[datetime] = None
    license_type: LicenseTypeEnum = LicenseTypeEnum.UNKNOWN
    original_filename: Optional[str] = Field(None, max_length=255)
    import_batch_id: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class SampleSourceUpdate(BaseModel):
    """Schema for updating a sample source."""
    source_url: Optional[str] = Field(None, max_length=2048)
    artist: Optional[str] = Field(None, max_length=255)
    album: Optional[str] = Field(None, max_length=255)
    release_date: Optional[datetime] = None
    license_type: Optional[LicenseTypeEnum] = None
    original_filename: Optional[str] = Field(None, max_length=255)
    metadata_json: Optional[Dict[str, Any]] = None


class SampleSourceResponse(BaseModel):
    """Schema for sample source responses."""
    id: int
    sample_id: int
    source_type: SourceTypeEnum
    source_url: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    release_date: Optional[datetime]
    license_type: LicenseTypeEnum
    original_filename: Optional[str]
    import_batch_id: Optional[str]
    metadata_json: Dict[str, Any]
    attribution_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SampleWithSourceResponse(BaseModel):
    """Extended sample response including source metadata."""
    id: int
    user_id: int
    title: str
    file_path: str
    file_size: Optional[int]
    duration: Optional[float]
    bpm: Optional[float]
    musical_key: Optional[str]
    genre: Optional[str]
    tags: list[str]
    bpm_confidence: Optional[int]
    genre_confidence: Optional[int]
    key_confidence: Optional[int]
    created_at: datetime
    analyzed_at: Optional[datetime]
    last_accessed_at: Optional[datetime]

    # Source metadata
    source: Optional[SampleSourceResponse] = None

    class Config:
        from_attributes = True
