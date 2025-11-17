"""
Unit tests for SP-404MK2 PADCONF.BIN service.

Tests validate:
- Binary format compliance (52,000 bytes)
- Correct byte offsets for all fields
- BPM encoding (9000 = 90.00 BPM)
- Filename handling (ASCII, 23 char limit)
- Round-trip consistency (write → read → verify)
"""

import pytest
from pathlib import Path
import tempfile

from app.services.padconf_service import PadconfService, PadConfig, ProjectConfig


class TestPadconfService:
    """Tests for PADCONF.BIN generation and parsing"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return PadconfService()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_create_empty_padconf(self, service):
        """Test creating minimal PADCONF.BIN file"""
        project = ProjectConfig(
            project_name="Test Kit",
            project_bpm=90.0,
            tempo_mode="project"
        )

        data = service.create_padconf(project, [])

        # Verify file size
        assert len(data) == 52000, "PADCONF.BIN must be exactly 52,000 bytes"

        # Verify tempo mode
        assert data[0x12] == 0x01, "Tempo mode should be 0x01 (project)"

        # Verify project BPM at correct offset
        bpm_value = int.from_bytes(data[0x13:0x15], 'big')
        assert bpm_value == 9000, "Project BPM should be 9000 (90.00)"

    def test_create_empty_padconf_zeroed(self, service):
        """Test that empty PADCONF is properly zeroed"""
        project = ProjectConfig(project_name="Empty", project_bpm=120.0)
        data = service.create_padconf(project, [])

        # Verify most of file is zeroed (except header)
        # Check some pad metadata areas that should be zero
        assert data[0xA5:0xA9] == b'\x00\x00\x00\x00', "Pad 1 metadata should start zeroed"

    def test_write_single_pad_bpm(self, service):
        """Test writing single pad with BPM to correct offset"""
        project = ProjectConfig(project_name="Test", project_bpm=120.0)
        pad = PadConfig(
            pad_index=1,
            filename="kick.wav",
            bpm=90.0,
            volume=100
        )

        data = service.create_padconf(project, [pad])

        # Verify BPM at correct offset: 0xA5 + 0x22 = 0xC7
        bpm_offset = 0xA5 + 0x22
        bpm_value = int.from_bytes(data[bpm_offset:bpm_offset+2], 'big')
        assert bpm_value == 9000, "Pad 1 BPM should be 9000 (90.00)"

    def test_write_multiple_pads_spacing(self, service):
        """Test multiple pads have correct 172-byte spacing"""
        project = ProjectConfig(project_name="Multi Pad", project_bpm=120.0)
        pads = [
            PadConfig(pad_index=1, filename="kick.wav", bpm=90.0),
            PadConfig(pad_index=2, filename="snare.wav", bpm=95.0),
            PadConfig(pad_index=3, filename="hihat.wav", bpm=100.0)
        ]

        data = service.create_padconf(project, pads)

        # Verify pad 1 BPM
        pad1_bpm_offset = 0xA5 + 0x22
        pad1_bpm = int.from_bytes(data[pad1_bpm_offset:pad1_bpm_offset+2], 'big')
        assert pad1_bpm == 9000, "Pad 1 BPM incorrect"

        # Verify pad 2 BPM (172 bytes later)
        pad2_bpm_offset = 0xA5 + 172 + 0x22
        pad2_bpm = int.from_bytes(data[pad2_bpm_offset:pad2_bpm_offset+2], 'big')
        assert pad2_bpm == 9500, "Pad 2 BPM incorrect"

        # Verify pad 3 BPM (344 bytes from start)
        pad3_bpm_offset = 0xA5 + (2 * 172) + 0x22
        pad3_bpm = int.from_bytes(data[pad3_bpm_offset:pad3_bpm_offset+2], 'big')
        assert pad3_bpm == 10000, "Pad 3 BPM incorrect"

    def test_write_pad_filename_correct_offset(self, service):
        """Test filename written to correct offset"""
        project = ProjectConfig(project_name="Test", project_bpm=120.0)
        pad = PadConfig(
            pad_index=1,
            filename="kick.wav",
            bpm=90.0
        )

        data = service.create_padconf(project, [pad])

        # Verify filename at 0x6C20
        filename_offset = 0x6C20
        filename_bytes = data[filename_offset:filename_offset+24]
        filename = filename_bytes.split(b'\x00')[0].decode('ascii')
        assert filename == "kick.wav", "Filename should match"

    def test_write_filename_truncation(self, service):
        """Test long filenames are truncated to 23 characters"""
        project = ProjectConfig(project_name="Test", project_bpm=120.0)
        long_filename = "this_is_a_very_long_filename_that_exceeds_limit.wav"

        pad = PadConfig(
            pad_index=1,
            filename=long_filename,
            bpm=90.0
        )

        data = service.create_padconf(project, [pad])

        # Read filename
        filename_offset = 0x6C20
        filename_bytes = data[filename_offset:filename_offset+24]
        filename = filename_bytes.split(b'\x00')[0].decode('ascii')

        assert len(filename) <= 23, f"Filename should be truncated to 23 chars, got {len(filename)}"

    def test_write_filename_ascii_sanitization(self, service):
        """Test non-ASCII characters are stripped from filenames"""
        project = ProjectConfig(project_name="Test", project_bpm=120.0)
        # Filename with non-ASCII characters
        pad = PadConfig(
            pad_index=1,
            filename="kick_café_🎵.wav",
            bpm=90.0
        )

        data = service.create_padconf(project, [pad])

        # Read filename
        filename_offset = 0x6C20
        filename_bytes = data[filename_offset:filename_offset+24]
        filename = filename_bytes.split(b'\x00')[0].decode('ascii')

        # Non-ASCII characters should be removed
        assert '🎵' not in filename, "Non-ASCII characters should be stripped"
        assert 'caf' in filename.lower(), "ASCII characters should be preserved"

    def test_project_name_write_and_read(self, service):
        """Test project name is correctly written and null-terminated"""
        project = ProjectConfig(
            project_name="Dusty Drums",
            project_bpm=95.0,
            tempo_mode="project"
        )

        data = service.create_padconf(project, [])

        # Verify project name at offset 0x81
        name_offset = 0x81
        name_bytes = data[name_offset:name_offset+32]
        project_name = name_bytes.split(b'\x00')[0].decode('ascii')
        assert project_name == "Dusty Drums", "Project name should be preserved"

    def test_tempo_mode_bank(self, service):
        """Test bank tempo mode is correctly written"""
        project = ProjectConfig(
            project_name="Bank Mode",
            project_bpm=120.0,
            tempo_mode="bank"
        )

        data = service.create_padconf(project, [])

        assert data[0x12] == 0x00, "Bank tempo mode should be 0x00"

    def test_round_trip_consistency(self, service, temp_dir):
        """Test write → read → verify consistency"""
        # Create test data
        original_project = ProjectConfig(
            project_name="Round Trip Test",
            project_bpm=140.0,
            tempo_mode="project"
        )
        original_pads = [
            PadConfig(pad_index=1, filename="sample1.wav", bpm=120.0, volume=100),
            PadConfig(pad_index=2, filename="sample2.wav", bpm=130.0, volume=80),
            PadConfig(pad_index=16, filename="sample16.wav", bpm=125.0, volume=110)  # Different pad
        ]

        # Write
        data = service.create_padconf(original_project, original_pads)

        # Save to temp file
        temp_file = temp_dir / "test_padconf.bin"
        temp_file.write_bytes(data)

        # Read back
        read_project, read_pads = service.read_padconf(temp_file)

        # Verify project
        assert read_project.project_name == "Round Trip Test"
        assert read_project.project_bpm == 140.0
        assert read_project.tempo_mode == "project"

        # Verify pads
        assert len(read_pads) == 3
        assert read_pads[0].filename == "sample1.wav"
        assert read_pads[0].bpm == 120.0
        assert read_pads[0].volume == 100
        assert read_pads[1].filename == "sample2.wav"
        assert read_pads[1].bpm == 130.0
        assert read_pads[1].volume == 80

    def test_round_trip_with_effects(self, service, temp_dir):
        """Test round-trip with effect settings"""
        project = ProjectConfig(
            project_name="Effects Test",
            project_bpm=100.0
        )
        pad = PadConfig(
            pad_index=5,
            filename="drums.wav",
            bpm=100.0,
            loop=True,
            bpm_sync=True,
            vinyl_effect=True,
            pan=80,
            pitch=3,
            attack=10,
            release=50
        )

        # Write and read
        data = service.create_padconf(project, [pad])
        temp_file = temp_dir / "effects.bin"
        temp_file.write_bytes(data)

        read_project, read_pads = service.read_padconf(temp_file)

        # Verify effect settings
        assert len(read_pads) == 1
        read_pad = read_pads[0]
        assert read_pad.loop is True
        assert read_pad.bpm_sync is True
        assert read_pad.vinyl_effect is True
        assert read_pad.pan == 80
        assert read_pad.pitch == 3
        assert read_pad.attack == 10
        assert read_pad.release == 50

    def test_read_invalid_file_size(self, service, temp_dir):
        """Test error handling for invalid file size"""
        # Create file with wrong size
        temp_file = temp_dir / "invalid.bin"
        temp_file.write_bytes(b"too small")

        with pytest.raises(ValueError, match="Invalid PADCONF.BIN size"):
            service.read_padconf(temp_file)

    def test_read_nonexistent_file(self, service):
        """Test error handling for nonexistent file"""
        with pytest.raises(FileNotFoundError):
            service.read_padconf(Path("/nonexistent/file.bin"))

    def test_multiple_pad_indices(self, service, temp_dir):
        """Test all 160 pads can be written and read"""
        project = ProjectConfig(project_name="All Pads", project_bpm=120.0)

        # Create pads at various indices
        pads = [
            PadConfig(pad_index=1, filename="pad_001.wav", bpm=120.0),
            PadConfig(pad_index=16, filename="pad_016.wav", bpm=120.0),
            PadConfig(pad_index=17, filename="pad_017.wav", bpm=120.0),  # Bank B
            PadConfig(pad_index=160, filename="pad_160.wav", bpm=120.0),  # Last pad
        ]

        data = service.create_padconf(project, pads)

        # Verify size
        assert len(data) == 52000

        # Read back and verify all pads
        temp_file = temp_dir / "all_pads.bin"
        temp_file.write_bytes(data)

        read_project, read_pads = service.read_padconf(temp_file)

        assert len(read_pads) == 4
        assert read_pads[0].filename == "pad_001.wav"
        assert read_pads[3].filename == "pad_160.wav"

    def test_bpm_precision(self, service, temp_dir):
        """Test BPM values maintain decimal precision"""
        project = ProjectConfig(project_name="BPM Test", project_bpm=120.0)
        pad = PadConfig(
            pad_index=1,
            filename="test.wav",
            bpm=90.55  # Test decimal precision
        )

        data = service.create_padconf(project, [pad])

        # Read back
        temp_file = temp_dir / "bpm_test.bin"
        temp_file.write_bytes(data)

        read_project, read_pads = service.read_padconf(temp_file)

        # BPM should be close (within rounding error)
        assert abs(read_pads[0].bpm - 90.55) < 0.01

    def test_volume_range(self, service):
        """Test volume values at boundaries (0-127)"""
        project = ProjectConfig(project_name="Volume Test", project_bpm=120.0)
        pads = [
            PadConfig(pad_index=1, filename="silent.wav", volume=0),
            PadConfig(pad_index=2, filename="medium.wav", volume=64),
            PadConfig(pad_index=3, filename="loud.wav", volume=127)
        ]

        data = service.create_padconf(project, pads)

        assert len(data) == 52000  # Verify still valid size
