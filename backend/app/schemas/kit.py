"""
Pydantic schemas for Kit Builder API.

These schemas define the structure for:
- Kit creation and updates
- Pad assignments
- Sample recommendations
- Kit export manifests
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ===========================
# Kit Schemas
# ===========================

class KitCreate(BaseModel):
    """Schema for creating a new kit."""

    name: str = Field(..., description="Name of the kit (1-255 characters)")
    description: Optional[str] = Field(None, description="Optional description of the kit")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate kit name is not empty and within length limits."""
        if not v or not v.strip():
            raise ValueError("Kit name cannot be empty")
        if len(v) > 255:
            raise ValueError("Kit name cannot exceed 255 characters")
        return v


class KitUpdate(BaseModel):
    """Schema for updating an existing kit (partial updates allowed)."""

    name: Optional[str] = Field(None, description="Updated kit name")
    description: Optional[str] = Field(None, description="Updated kit description")
    is_public: Optional[bool] = Field(None, description="Whether the kit is publicly visible")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate kit name if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Kit name cannot be empty")
            if len(v) > 255:
                raise ValueError("Kit name cannot exceed 255 characters")
        return v


class SampleInfo(BaseModel):
    """Nested sample information for responses."""

    id: int = Field(..., description="Sample database ID")
    title: str = Field(..., description="Sample title")
    file_path: str = Field(..., description="Path to audio file")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    bpm: Optional[float] = Field(None, description="Detected BPM")
    genre: Optional[str] = Field(None, description="Musical genre")
    tags: List[str] = Field(default_factory=list, description="Sample tags")

    class Config:
        from_attributes = True


class PadAssignmentInfo(BaseModel):
    """Information about a pad assignment (for kit details)."""

    kit_id: int = Field(..., description="Kit ID")
    sample_id: int = Field(..., description="Sample ID")
    pad_bank: str = Field(..., description="Pad bank (A-J, 10 banks on SP-404MK2)")
    pad_number: int = Field(..., description="Pad number (1-16)")
    volume: float = Field(..., description="Playback volume (0.0-1.0)")
    pitch_shift: int = Field(..., description="Pitch shift in semitones")
    sample: SampleInfo = Field(..., description="Sample details")

    class Config:
        from_attributes = True


class KitResponse(BaseModel):
    """Schema for kit details response."""

    id: int = Field(..., description="Kit database ID")
    user_id: int = Field(..., description="Owner user ID")
    name: str = Field(..., description="Kit name")
    description: Optional[str] = Field(None, description="Kit description")
    is_public: bool = Field(..., description="Whether kit is public")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    samples: List[PadAssignmentInfo] = Field(default_factory=list, description="Pad assignments")

    class Config:
        from_attributes = True


class KitListResponse(BaseModel):
    """Schema for paginated kit list."""

    kits: List[KitResponse] = Field(..., description="List of kits")
    total: int = Field(..., description="Total number of kits")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items returned")


# ===========================
# Pad Assignment Schemas
# ===========================

class PadAssignmentRequest(BaseModel):
    """Schema for assigning a sample to a pad."""

    sample_id: int = Field(..., description="Sample ID to assign")
    pad_bank: str = Field(..., description="Pad bank (A-J, 10 banks on SP-404MK2)")
    pad_number: int = Field(..., description="Pad number (1-16)")
    volume: float = Field(1.0, description="Playback volume (0.0-1.0)", ge=0.0, le=1.0)
    pitch_shift: int = Field(0, description="Pitch shift in semitones", ge=-12, le=12)

    @field_validator('pad_bank')
    @classmethod
    def validate_bank(cls, v: str) -> str:
        """Validate pad bank is A-J (10 banks on SP-404MK2)."""
        if v not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            raise ValueError("Pad bank must be A-J")
        return v

    @field_validator('pad_number')
    @classmethod
    def validate_pad_number(cls, v: int) -> int:
        """Validate pad number is 1-16."""
        if v < 1 or v > 16:
            raise ValueError("Pad number must be between 1 and 16")
        return v


class PadAssignmentResponse(BaseModel):
    """Schema for pad assignment response."""

    kit_id: int = Field(..., description="Kit ID")
    sample_id: int = Field(..., description="Sample ID")
    pad_bank: str = Field(..., description="Pad bank (A-J, 10 banks on SP-404MK2)")
    pad_number: int = Field(..., description="Pad number (1-16)")
    volume: float = Field(..., description="Playback volume (0.0-1.0)")
    pitch_shift: int = Field(..., description="Pitch shift in semitones")
    sample: SampleInfo = Field(..., description="Sample details")

    class Config:
        from_attributes = True


# ===========================
# Recommendation Schemas
# ===========================

class SampleRecommendation(BaseModel):
    """Schema for a recommended sample with reasoning."""

    id: int = Field(..., description="Sample database ID")
    title: str = Field(..., description="Sample title")
    file_path: str = Field(..., description="Path to audio file")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    bpm: Optional[float] = Field(None, description="Detected BPM")
    genre: Optional[str] = Field(None, description="Musical genre")
    tags: List[str] = Field(default_factory=list, description="Sample tags")
    recommendation_reason: str = Field(..., description="Why this sample was recommended")

    class Config:
        from_attributes = True


class RecommendationsResponse(BaseModel):
    """Schema for pad recommendations response."""

    kit_id: int = Field(..., description="Kit ID")
    pad_number: int = Field(..., description="Pad number being filled")
    samples: List[SampleRecommendation] = Field(..., description="Recommended samples")
    total: int = Field(..., description="Total recommendations available")


# ===========================
# Export Schemas
# ===========================

class ExportSampleInfo(BaseModel):
    """Information about a sample in the export manifest."""

    sample_id: int = Field(..., description="Sample database ID")
    original_filename: str = Field(..., description="Original filename")
    export_filename: str = Field(..., description="Sanitized export filename")
    pad_bank: str = Field(..., description="Pad bank (A-J, 10 banks on SP-404MK2)")
    pad_number: int = Field(..., description="Pad number (1-16)")
    volume: float = Field(..., description="Playback volume (0.0-1.0)")
    pitch_shift: int = Field(..., description="Pitch shift in semitones")
    file_path: str = Field(..., description="Original file path")


class ExportManifest(BaseModel):
    """Export manifest with kit details and samples to export."""

    kit_id: int = Field(..., description="Kit database ID")
    kit_name: str = Field(..., description="Kit name")
    output_format: str = Field(..., description="Output audio format (wav or aiff)")
    samples: List[ExportSampleInfo] = Field(..., description="Samples to export")
    total_samples: int = Field(..., description="Total number of samples")
