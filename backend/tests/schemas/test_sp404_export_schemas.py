"""
Tests for SP-404MK2 Export Pydantic schemas
"""
import pytest
from pathlib import Path
from pydantic import ValidationError

from app.schemas.sp404_export import (
    ExportConfig,
    ConversionResult,
    ValidationResult,
    ExportResult,
    BatchExportResult
)


def test_export_config_defaults():
    """Test default values for ExportConfig."""
    config = ExportConfig()

    assert config.organize_by == "flat"
    assert config.format == "wav"
    assert config.include_metadata is True
    assert config.sanitize_filenames is True
    assert config.output_base_path is None


def test_export_config_validation():
    """Test validation of organize_by field."""
    # Valid values
    valid_configs = [
        ExportConfig(organize_by="flat"),
        ExportConfig(organize_by="genre"),
        ExportConfig(organize_by="bpm"),
        ExportConfig(organize_by="key")
    ]

    for config in valid_configs:
        assert config.organize_by in ["flat", "genre", "bpm", "key"]

    # Invalid value
    with pytest.raises(ValidationError) as exc_info:
        ExportConfig(organize_by="invalid")

    assert "organize_by must be one of" in str(exc_info.value)


def test_export_config_format_validation():
    """Test format validation - only wav/aiff allowed."""
    # Valid formats
    config_wav = ExportConfig(format="wav")
    assert config_wav.format == "wav"

    config_aiff = ExportConfig(format="aiff")
    assert config_aiff.format == "aiff"

    # Invalid format
    with pytest.raises(ValidationError) as exc_info:
        ExportConfig(format="mp3")

    assert "format must be one of" in str(exc_info.value)


def test_conversion_result_success():
    """Test successful conversion result."""
    result = ConversionResult(
        success=True,
        output_path=Path("/output/file.wav"),
        original_format=".mp3",
        original_sample_rate=44100,
        converted_sample_rate=48000,
        original_duration=2.5
    )

    assert result.success is True
    assert result.output_path == Path("/output/file.wav")
    assert result.original_format == ".mp3"
    assert result.original_sample_rate == 44100
    assert result.converted_sample_rate == 48000
    assert result.original_duration == 2.5
    assert result.error_message is None


def test_conversion_result_failure():
    """Test failed conversion with error message."""
    result = ConversionResult(
        success=False,
        error_message="File not found"
    )

    assert result.success is False
    assert result.error_message == "File not found"
    assert result.output_path is None
    assert result.converted_sample_rate == 48000  # Default value


def test_validation_result_valid_sample():
    """Test validation result for valid sample."""
    result = ValidationResult(
        valid=True,
        meets_duration_requirement=True,
        format_supported=True,
        file_readable=True,
        errors=[]
    )

    assert result.valid is True
    assert result.meets_duration_requirement is True
    assert result.format_supported is True
    assert result.file_readable is True
    assert len(result.errors) == 0


def test_validation_result_invalid_duration():
    """Test validation result for sample <100ms (rejected)."""
    result = ValidationResult(
        valid=False,
        meets_duration_requirement=False,
        format_supported=True,
        file_readable=True,
        errors=["Sample duration 50ms is too short (minimum 100ms)"]
    )

    assert result.valid is False
    assert result.meets_duration_requirement is False
    assert len(result.errors) == 1
    assert "too short" in result.errors[0]


def test_export_result_schema():
    """Test single export result schema."""
    result = ExportResult(
        success=True,
        sample_id=123,
        format="wav",
        output_path="/exports/sample.wav",
        output_filename="sample.wav",
        file_size_bytes=1024000,
        conversion_time_seconds=1.5
    )

    assert result.success is True
    assert result.sample_id == 123
    assert result.format == "wav"
    assert result.output_path == "/exports/sample.wav"
    assert result.output_filename == "sample.wav"
    assert result.file_size_bytes == 1024000
    assert result.conversion_time_seconds == 1.5
    assert result.error is None


def test_batch_export_result_schema():
    """Test batch export result aggregation."""
    result1 = ExportResult(
        success=True,
        sample_id=1,
        format="wav",
        output_path="/export/s1.wav",
        output_filename="s1.wav",
        file_size_bytes=1000000,
        conversion_time_seconds=1.0
    )

    result2 = ExportResult(
        success=True,
        sample_id=2,
        format="wav",
        output_path="/export/s2.wav",
        output_filename="s2.wav",
        file_size_bytes=2000000,
        conversion_time_seconds=1.5
    )

    result3 = ExportResult(
        success=False,
        sample_id=3,
        format="wav",
        error="Conversion failed"
    )

    batch_result = BatchExportResult(
        total_requested=3,
        successful=2,
        failed=1,
        results=[result1, result2, result3],
        errors=["Sample 3: Conversion failed"],
        organized_by="genre",
        total_size_bytes=3000000,
        total_duration_seconds=2.5
    )

    assert batch_result.total_requested == 3
    assert batch_result.successful == 2
    assert batch_result.failed == 1
    assert len(batch_result.results) == 3
    assert len(batch_result.errors) == 1
    assert batch_result.organized_by == "genre"
    assert batch_result.total_size_bytes == 3000000
    assert batch_result.total_duration_seconds == 2.5


def test_batch_export_result_statistics():
    """Test batch export success/failure counts and success rate."""
    # All successful
    batch_all_success = BatchExportResult(
        total_requested=5,
        successful=5,
        failed=0,
        results=[],
        errors=[]
    )
    assert batch_all_success.success_rate == 100.0

    # Partial success
    batch_partial = BatchExportResult(
        total_requested=10,
        successful=7,
        failed=3,
        results=[],
        errors=[]
    )
    assert batch_partial.success_rate == 70.0

    # All failed
    batch_all_fail = BatchExportResult(
        total_requested=5,
        successful=0,
        failed=5,
        results=[],
        errors=[]
    )
    assert batch_all_fail.success_rate == 0.0

    # Zero requested (edge case)
    batch_zero = BatchExportResult(
        total_requested=0,
        successful=0,
        failed=0,
        results=[],
        errors=[]
    )
    assert batch_zero.success_rate == 0.0


def test_export_config_custom_values():
    """Test ExportConfig with custom values."""
    config = ExportConfig(
        organize_by="bpm",
        format="aiff",
        include_metadata=False,
        sanitize_filenames=False,
        output_base_path="/custom/export/path"
    )

    assert config.organize_by == "bpm"
    assert config.format == "aiff"
    assert config.include_metadata is False
    assert config.sanitize_filenames is False
    assert config.output_base_path == "/custom/export/path"


def test_conversion_result_partial_data():
    """Test ConversionResult with minimal data."""
    result = ConversionResult(
        success=True,
        output_path=Path("/output.wav")
    )

    assert result.success is True
    assert result.output_path == Path("/output.wav")
    assert result.original_format is None
    assert result.original_sample_rate is None
    assert result.converted_sample_rate == 48000  # Default


def test_validation_result_multiple_errors():
    """Test ValidationResult with multiple validation errors."""
    result = ValidationResult(
        valid=False,
        meets_duration_requirement=False,
        format_supported=False,
        file_readable=False,
        errors=[
            "File not found",
            "Duration too short (50ms < 100ms)",
            "Unsupported format: .xyz"
        ]
    )

    assert result.valid is False
    assert len(result.errors) == 3
    assert "File not found" in result.errors
    assert "Duration too short" in result.errors[1]
    assert "Unsupported format" in result.errors[2]


def test_export_result_failure():
    """Test ExportResult for failed export."""
    result = ExportResult(
        success=False,
        sample_id=999,
        format="wav",
        error="Sample validation failed"
    )

    assert result.success is False
    assert result.sample_id == 999
    assert result.error == "Sample validation failed"
    assert result.output_path is None
    assert result.file_size_bytes == 0
    assert result.conversion_time_seconds == 0.0


def test_batch_export_result_defaults():
    """Test BatchExportResult with default values."""
    result = BatchExportResult(
        total_requested=0,
        successful=0,
        failed=0
    )

    assert result.total_requested == 0
    assert result.successful == 0
    assert result.failed == 0
    assert result.results == []
    assert result.errors == []
    assert result.organized_by == "flat"  # Default
    assert result.total_size_bytes == 0
    assert result.total_duration_seconds == 0.0
