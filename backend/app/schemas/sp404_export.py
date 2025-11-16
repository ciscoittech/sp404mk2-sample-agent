"""
SP-404MK2 Export schemas
"""
from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class ExportConfig(BaseModel):
    """Configuration for SP-404 export"""
    organize_by: str = Field(default="flat", description="Organization strategy")
    format: str = Field(default="wav", description="Output format")
    include_metadata: bool = Field(default=True, description="Include metadata files")
    sanitize_filenames: bool = Field(default=True, description="Sanitize filenames")
    output_base_path: Optional[str] = Field(default=None, description="Output directory")
    include_bank_layout: bool = Field(default=False, description="Include bank layout for kits")

    @field_validator("organize_by")
    @classmethod
    def validate_organize_by(cls, v: str) -> str:
        """Validate organization strategy"""
        allowed = ["flat", "genre", "bpm", "key", "kit", "bank"]
        if v not in allowed:
            raise ValueError(f"organize_by must be one of {allowed}")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate output format"""
        allowed = ["wav", "aiff"]
        if v not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v


class ConversionResult(BaseModel):
    """Result of audio conversion"""
    success: bool
    output_path: Optional[Path] = None
    original_format: Optional[str] = None
    original_sample_rate: Optional[int] = None
    converted_sample_rate: int = 48000
    converted_bit_depth: int = 16
    original_duration: Optional[float] = None
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class ValidationResult(BaseModel):
    """Result of sample validation"""
    valid: bool
    duration_ms: float = 0.0
    meets_duration_requirement: bool = False
    format_supported: bool = False
    file_readable: bool = False
    errors: List[str] = Field(default_factory=list)


class ExportResult(BaseModel):
    """Result of single sample export"""
    success: bool
    sample_id: int
    format: str
    output_path: Optional[str] = None
    output_filename: Optional[str] = None
    file_size_bytes: int = 0
    conversion_time_seconds: float = 0.0
    error: Optional[str] = None
    metadata_file_created: bool = False
    download_url: Optional[str] = Field(None, description="URL to download exported file")
    export_id: Optional[int] = Field(None, description="Export record ID for tracking")


class BatchExportRequest(BaseModel):
    """Request for batch export"""
    sample_ids: List[int] = Field(..., description="List of sample IDs to export")
    config: ExportConfig = Field(..., description="Export configuration")


class BatchExportResult(BaseModel):
    """Result of batch export"""
    total_requested: int
    successful: int
    failed: int
    results: List[ExportResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    organized_by: str = "flat"
    total_size_bytes: int = 0
    total_time_seconds: float = 0.0
    average_time_per_sample: float = 0.0
    total_samples: int = 0
    output_base_path: str = ""
    job_id: Optional[int] = Field(None, description="Export job ID for tracking")
    export_id: Optional[int] = Field(None, description="Export record ID")

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requested == 0:
            return 0.0
        return (self.successful / self.total_requested) * 100


class KitExportResult(BaseModel):
    """Result of kit export"""
    success: bool
    kit_id: int
    kit_name: str
    sample_count: int
    successful: int
    failed: int
    output_path: str
    format: str
    total_size_bytes: int = 0
    export_time_seconds: float = 0.0
    errors: List[str] = Field(default_factory=list)
