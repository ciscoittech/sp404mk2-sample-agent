"""
Pydantic schemas for user preferences API.

Defines request/response models for the user preferences system.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserPreferenceBase(BaseModel):
    """Base schema for user preferences with validation."""

    vibe_analysis_model: str = Field(
        default="qwen/qwen3-7b-it",
        description="Model to use for vibe analysis (e.g., 'qwen/qwen3-7b-it')"
    )
    auto_vibe_analysis: bool = Field(
        default=True,
        description="Whether to automatically analyze vibes on sample upload"
    )
    auto_audio_features: bool = Field(
        default=True,
        description="Whether to automatically extract audio features on upload"
    )
    batch_processing_model: str = Field(
        default="qwen/qwen3-7b-it",
        description="Model to use for batch processing analysis"
    )
    batch_auto_analyze: bool = Field(
        default=False,
        description="Whether to automatically analyze batches after processing"
    )
    max_cost_per_request: Optional[float] = Field(
        default=None,
        description="Maximum cost per API request in USD (None for no limit)"
    )
    default_export_format: str = Field(
        default="wav",
        description="Default export format for SP-404 exports (wav or aiff)"
    )
    default_export_organization: str = Field(
        default="flat",
        description="Default organization method for SP-404 exports (flat, genre, bpm, key)"
    )
    auto_sanitize_filenames: bool = Field(
        default=True,
        description="Whether to automatically sanitize filenames during SP-404 export"
    )

    @field_validator("vibe_analysis_model", "batch_processing_model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate that model name is in expected format."""
        if not v or "/" not in v:
            raise ValueError("Model name must be in format 'provider/model-name'")
        return v

    @field_validator("max_cost_per_request")
    @classmethod
    def validate_cost_limit(cls, v: Optional[float]) -> Optional[float]:
        """Validate cost limit is positive if set."""
        if v is not None and v <= 0:
            raise ValueError("Cost limit must be positive")
        return v

    @field_validator("default_export_format")
    @classmethod
    def validate_export_format(cls, v: str) -> str:
        """Validate export format is wav or aiff."""
        if v not in ("wav", "aiff"):
            raise ValueError("Export format must be 'wav' or 'aiff'")
        return v

    @field_validator("default_export_organization")
    @classmethod
    def validate_export_organization(cls, v: str) -> str:
        """Validate export organization method."""
        if v not in ("flat", "genre", "bpm", "key"):
            raise ValueError("Export organization must be 'flat', 'genre', 'bpm', or 'key'")
        return v


class UserPreferenceUpdate(BaseModel):
    """Schema for partial preference updates (all fields optional)."""

    vibe_analysis_model: Optional[str] = Field(
        default=None,
        description="Model to use for vibe analysis"
    )
    auto_vibe_analysis: Optional[bool] = Field(
        default=None,
        description="Whether to automatically analyze vibes on upload"
    )
    auto_audio_features: Optional[bool] = Field(
        default=None,
        description="Whether to automatically extract audio features"
    )
    batch_processing_model: Optional[str] = Field(
        default=None,
        description="Model to use for batch processing"
    )
    batch_auto_analyze: Optional[bool] = Field(
        default=None,
        description="Whether to automatically analyze batches"
    )
    max_cost_per_request: Optional[float] = Field(
        default=None,
        description="Maximum cost per request in USD (None for no limit)"
    )
    default_export_format: Optional[str] = Field(
        default=None,
        description="Default export format for SP-404 exports (wav or aiff)"
    )
    default_export_organization: Optional[str] = Field(
        default=None,
        description="Default organization method for SP-404 exports (flat, genre, bpm, key)"
    )
    auto_sanitize_filenames: Optional[bool] = Field(
        default=None,
        description="Whether to automatically sanitize filenames during SP-404 export"
    )

    @field_validator("vibe_analysis_model", "batch_processing_model")
    @classmethod
    def validate_model_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate model name format if provided."""
        if v is not None and (not v or "/" not in v):
            raise ValueError("Model name must be in format 'provider/model-name'")
        return v

    @field_validator("max_cost_per_request")
    @classmethod
    def validate_cost_limit(cls, v: Optional[float]) -> Optional[float]:
        """Validate cost limit is positive if set."""
        if v is not None and v <= 0:
            raise ValueError("Cost limit must be positive")
        return v

    @field_validator("default_export_format")
    @classmethod
    def validate_export_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate export format if provided."""
        if v is not None and v not in ("wav", "aiff"):
            raise ValueError("Export format must be 'wav' or 'aiff'")
        return v

    @field_validator("default_export_organization")
    @classmethod
    def validate_export_organization(cls, v: Optional[str]) -> Optional[str]:
        """Validate export organization method if provided."""
        if v is not None and v not in ("flat", "genre", "bpm", "key"):
            raise ValueError("Export organization must be 'flat', 'genre', 'bpm', or 'key'")
        return v


class UserPreferenceResponse(BaseModel):
    """Schema for preference responses with timestamps."""

    id: int = Field(..., description="Preference record ID (always 1 for single-row design)")
    vibe_analysis_model: str = Field(..., description="Model used for vibe analysis")
    auto_vibe_analysis: bool = Field(..., description="Auto-analyze vibes on upload")
    auto_audio_features: bool = Field(..., description="Auto-extract audio features")
    batch_processing_model: str = Field(..., description="Model used for batch processing")
    batch_auto_analyze: bool = Field(..., description="Auto-analyze batches")
    max_cost_per_request: Optional[float] = Field(..., description="Maximum cost per request in USD")
    default_export_format: str = Field(..., description="Default export format for SP-404 exports")
    default_export_organization: str = Field(..., description="Default organization method for SP-404 exports")
    auto_sanitize_filenames: bool = Field(..., description="Auto-sanitize filenames during SP-404 export")
    created_at: datetime = Field(..., description="When preferences were created")
    updated_at: datetime = Field(..., description="When preferences were last updated")

    class Config:
        from_attributes = True


class ModelMetadata(BaseModel):
    """Metadata for a single available model."""

    model_id: str = Field(..., description="Model identifier (e.g., 'qwen/qwen3-7b-it')")
    name: str = Field(..., description="Human-readable model name")
    input_cost: float = Field(..., description="Cost per input token in USD")
    output_cost: float = Field(..., description="Cost per output token in USD")
    description: str = Field(..., description="Model description and capabilities")


class AvailableModelsResponse(BaseModel):
    """Response containing all available models and their metadata."""

    models: List[ModelMetadata] = Field(..., description="List of available models with pricing")
