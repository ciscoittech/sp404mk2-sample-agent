"""
Tests for SP-404MK2 Project Builder Pydantic schemas.

Tests validate:
- ProjectBuildRequest validation (project_name, BPM, format, bank_layout)
- ProjectBuildResult serialization (success, export_id, metadata)
- Request/response round-trip JSON serialization
- ASCII-only validation for project names
- BPM range validation (20-300)
- Format enum validation (wav/aiff only)
"""

import pytest
from pydantic import ValidationError
import json

from app.schemas.sp404_project import ProjectBuildRequest, ProjectBuildResult


class TestProjectBuildRequest:
    """Tests for ProjectBuildRequest validation"""

    def test_valid_request_minimal(self):
        """Test valid request with minimal required fields"""
        request = ProjectBuildRequest(
            project_name="My Kit"
        )
        assert request.project_name == "My Kit"
        assert request.project_bpm is None  # Optional - auto-detect
        assert request.audio_format == "wav"  # Default
        assert request.include_bank_layout is False  # Default

    def test_valid_request_full(self):
        """Test valid request with all fields"""
        request = ProjectBuildRequest(
            project_name="Drum Kit Pro",
            project_bpm=120.5,
            audio_format="aiff",
            include_bank_layout=True
        )
        assert request.project_name == "Drum Kit Pro"
        assert request.project_bpm == 120.5
        assert request.audio_format == "aiff"
        assert request.include_bank_layout is True

    def test_project_name_empty_fails(self):
        """Test that empty project name raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name="")

        assert "project_name" in str(exc_info.value)

    def test_project_name_max_length_31(self):
        """Test project name max length is 31 characters"""
        # Valid: 31 characters
        valid_name = "A" * 31
        request = ProjectBuildRequest(project_name=valid_name)
        assert request.project_name == valid_name

        # Invalid: 32 characters
        invalid_name = "A" * 32
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name=invalid_name)

        assert "project_name" in str(exc_info.value)

    def test_project_name_ascii_only(self):
        """Test that non-ASCII characters in project name fail"""
        # Valid: ASCII only
        valid_name = "Dusty_Drums"
        request = ProjectBuildRequest(project_name=valid_name)
        assert request.project_name == valid_name

        # Invalid: Non-ASCII character
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name="Café Drums")

        assert "project_name" in str(exc_info.value) or "ASCII" in str(exc_info.value)

    def test_bpm_range_minimum(self):
        """Test BPM minimum value is 20.0"""
        # Valid: 20.0
        request = ProjectBuildRequest(project_name="Test", project_bpm=20.0)
        assert request.project_bpm == 20.0

        # Invalid: 19.9
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name="Test", project_bpm=19.9)

        assert "project_bpm" in str(exc_info.value)

    def test_bpm_range_maximum(self):
        """Test BPM maximum value is 300.0"""
        # Valid: 300.0
        request = ProjectBuildRequest(project_name="Test", project_bpm=300.0)
        assert request.project_bpm == 300.0

        # Invalid: 300.1
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name="Test", project_bpm=300.1)

        assert "project_bpm" in str(exc_info.value)

    def test_bpm_typical_values(self):
        """Test typical BPM values work correctly"""
        typical_bpms = [60.0, 90.0, 100.0, 120.0, 140.0, 150.0, 200.0]
        for bpm in typical_bpms:
            request = ProjectBuildRequest(project_name="Test", project_bpm=bpm)
            assert request.project_bpm == bpm

    def test_bpm_optional_none(self):
        """Test BPM is optional and defaults to None"""
        request = ProjectBuildRequest(project_name="Test")
        assert request.project_bpm is None

    def test_audio_format_wav_valid(self):
        """Test WAV format is accepted"""
        request = ProjectBuildRequest(
            project_name="Test",
            audio_format="wav"
        )
        assert request.audio_format == "wav"

    def test_audio_format_aiff_valid(self):
        """Test AIFF format is accepted"""
        request = ProjectBuildRequest(
            project_name="Test",
            audio_format="aiff"
        )
        assert request.audio_format == "aiff"

    def test_audio_format_invalid_mp3(self):
        """Test invalid format MP3 is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name="Test", audio_format="mp3")

        assert "audio_format" in str(exc_info.value)

    def test_audio_format_case_sensitive(self):
        """Test format is case-sensitive (lowercase only)"""
        # Uppercase should fail
        with pytest.raises(ValidationError) as exc_info:
            ProjectBuildRequest(project_name="Test", audio_format="WAV")

        assert "audio_format" in str(exc_info.value)

    def test_include_bank_layout_default(self):
        """Test include_bank_layout defaults to False"""
        request = ProjectBuildRequest(project_name="Test")
        assert request.include_bank_layout is False

    def test_include_bank_layout_true(self):
        """Test include_bank_layout can be set to True"""
        request = ProjectBuildRequest(
            project_name="Test",
            include_bank_layout=True
        )
        assert request.include_bank_layout is True


class TestProjectBuildResult:
    """Tests for ProjectBuildResult serialization"""

    def test_result_success_minimal(self):
        """Test successful result with minimal fields"""
        result = ProjectBuildResult(
            success=True,
            export_id="export_123",
            project_name="My Kit"
        )
        assert result.success is True
        assert result.export_id == "export_123"
        assert result.project_name == "My Kit"

    def test_result_success_full(self):
        """Test successful result with all metadata"""
        result = ProjectBuildResult(
            success=True,
            export_id="export_456",
            project_name="Dusty Drums",
            sample_count=12,
            file_size_bytes=50000000,
            download_url="/api/v1/exports/download/export_456"
        )
        assert result.success is True
        assert result.export_id == "export_456"
        assert result.project_name == "Dusty Drums"
        assert result.sample_count == 12
        assert result.file_size_bytes == 50000000
        assert result.download_url == "/api/v1/exports/download/export_456"

    def test_result_failure(self):
        """Test failed result with error message"""
        result = ProjectBuildResult(
            success=False,
            error_message="Kit contains no samples"
        )
        assert result.success is False
        assert result.error_message == "Kit contains no samples"
        assert result.export_id is None

    def test_result_json_serialization(self):
        """Test result can be serialized to JSON"""
        result = ProjectBuildResult(
            success=True,
            export_id="export_789",
            project_name="Test Kit",
            sample_count=5,
            file_size_bytes=10000000
        )

        # Serialize to JSON
        json_str = result.model_dump_json()
        assert isinstance(json_str, str)

        # Parse back
        parsed = json.loads(json_str)
        assert parsed["success"] is True
        assert parsed["export_id"] == "export_789"
        assert parsed["project_name"] == "Test Kit"
        assert parsed["sample_count"] == 5
        assert parsed["file_size_bytes"] == 10000000

    def test_result_json_deserialization(self):
        """Test result can be deserialized from JSON"""
        json_data = {
            "success": True,
            "export_id": "export_999",
            "project_name": "Loaded Kit",
            "sample_count": 8,
            "file_size_bytes": 25000000,
            "download_url": "/api/v1/exports/download/export_999"
        }

        result = ProjectBuildResult(**json_data)
        assert result.success is True
        assert result.export_id == "export_999"
        assert result.project_name == "Loaded Kit"
        assert result.sample_count == 8

    def test_result_defaults(self):
        """Test default values for result fields"""
        result = ProjectBuildResult(
            success=True,
            export_id="export_default"
        )
        assert result.success is True
        assert result.export_id == "export_default"
        assert result.project_name is None
        assert result.sample_count == 0
        assert result.file_size_bytes == 0
        assert result.download_url is None
        assert result.error_message is None


class TestProjectBuildRequestRoundTrip:
    """Tests for request/response round-trip JSON serialization"""

    def test_request_json_roundtrip(self):
        """Test request can round-trip through JSON"""
        original = ProjectBuildRequest(
            project_name="Round Trip Test",
            project_bpm=125.5,
            audio_format="aiff",
            include_bank_layout=True
        )

        # Serialize to JSON
        json_str = original.model_dump_json()

        # Deserialize back
        reconstructed = ProjectBuildRequest(**json.loads(json_str))

        assert reconstructed.project_name == original.project_name
        assert reconstructed.project_bpm == original.project_bpm
        assert reconstructed.audio_format == original.audio_format
        assert reconstructed.include_bank_layout == original.include_bank_layout

    def test_request_model_dump(self):
        """Test model_dump() produces correct dictionary"""
        request = ProjectBuildRequest(
            project_name="Dump Test",
            project_bpm=100.0,
            audio_format="wav"
        )

        dumped = request.model_dump()

        assert dumped["project_name"] == "Dump Test"
        assert dumped["project_bpm"] == 100.0
        assert dumped["audio_format"] == "wav"
        assert dumped["include_bank_layout"] is False

    def test_result_model_dump(self):
        """Test result model_dump() produces correct dictionary"""
        result = ProjectBuildResult(
            success=True,
            export_id="dump_test",
            project_name="Test Result",
            sample_count=10,
            file_size_bytes=5000000
        )

        dumped = result.model_dump()

        assert dumped["success"] is True
        assert dumped["export_id"] == "dump_test"
        assert dumped["project_name"] == "Test Result"
        assert dumped["sample_count"] == 10
        assert dumped["file_size_bytes"] == 5000000


class TestProjectBuildRequestEdgeCases:
    """Edge case tests for ProjectBuildRequest"""

    def test_project_name_single_character(self):
        """Test single character project name is valid"""
        request = ProjectBuildRequest(project_name="A")
        assert request.project_name == "A"

    def test_project_name_with_spaces(self):
        """Test project name can contain spaces"""
        request = ProjectBuildRequest(project_name="My Drum Kit")
        assert request.project_name == "My Drum Kit"

    def test_project_name_with_numbers(self):
        """Test project name can contain numbers"""
        request = ProjectBuildRequest(project_name="Kit123")
        assert request.project_name == "Kit123"

    def test_project_name_with_special_chars(self):
        """Test project name can contain ASCII special characters"""
        request = ProjectBuildRequest(project_name="Kit-2024_Final")
        assert request.project_name == "Kit-2024_Final"

    def test_bpm_decimal_precision(self):
        """Test BPM accepts decimal values"""
        request = ProjectBuildRequest(project_name="Test", project_bpm=120.555)
        assert request.project_bpm == 120.555

    def test_result_zero_samples(self):
        """Test result with zero samples"""
        result = ProjectBuildResult(
            success=True,
            export_id="empty_kit",
            sample_count=0
        )
        assert result.sample_count == 0

    def test_result_large_file_size(self):
        """Test result with large file size"""
        large_size = 1_000_000_000  # 1 GB
        result = ProjectBuildResult(
            success=True,
            export_id="large_kit",
            file_size_bytes=large_size
        )
        assert result.file_size_bytes == large_size
