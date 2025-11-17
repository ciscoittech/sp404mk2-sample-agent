"""
SP-404MK2 Project Builder schemas

Defines request/response contracts for project generation:
- ProjectBuildRequest: User input for creating a project
- ProjectBuildResult: Server response with generated project metadata
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ProjectBuildRequest(BaseModel):
    """Request to build an SP-404MK2 project from a kit"""

    project_name: str = Field(
        ...,
        min_length=1,
        max_length=31,
        description="Project name (1-31 ASCII characters)"
    )
    project_bpm: Optional[float] = Field(
        None,
        ge=20.0,
        le=300.0,
        description="Project BPM (20-300, optional for auto-detect)"
    )
    audio_format: str = Field(
        "wav",
        pattern="^(wav|aiff)$",
        description="Audio format for samples (wav or aiff)"
    )
    include_bank_layout: bool = Field(
        False,
        description="Include bank layout configuration in export"
    )

    @field_validator("project_name")
    @classmethod
    def validate_ascii_only(cls, v: str) -> str:
        """Ensure project name contains only ASCII characters"""
        if not v.isascii():
            raise ValueError("project_name must contain only ASCII characters")
        return v


class ProjectBuildResult(BaseModel):
    """Response from building an SP-404MK2 project"""

    success: bool = Field(
        ...,
        description="Whether project generation succeeded"
    )
    export_id: Optional[str] = Field(
        None,
        description="Unique export ID for tracking and download"
    )
    project_name: Optional[str] = Field(
        None,
        description="Project name used in generation"
    )
    sample_count: int = Field(
        0,
        ge=0,
        description="Number of samples included in project"
    )
    file_size_bytes: int = Field(
        0,
        ge=0,
        description="Total size of generated project ZIP in bytes"
    )
    download_url: Optional[str] = Field(
        None,
        description="URL to download the generated project ZIP"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )
