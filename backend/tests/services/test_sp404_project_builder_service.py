"""
Unit tests for SP-404MK2 Project Builder Service.

Tests validate:
- Project generation from kit with PADCONF.BIN creation
- ZIP file structure (samples/ + PADCONF.BIN + PROJECT_INFO.txt)
- BPM auto-detection (median or fallback to 120)
- Audio format conversion (48kHz/16-bit WAV/AIFF)
- Error handling for missing kits, no samples, conversion failures
- Database export tracking
"""

import pytest
import pytest_asyncio
from pathlib import Path
import zipfile
import tempfile
import shutil
from typing import List

from app.schemas.sp404_project import ProjectBuildRequest, ProjectBuildResult
from app.services.sp404_project_builder_service import SP404ProjectBuilderService
from app.models.kit import Kit, KitSample
from app.models.sample import Sample
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class TestSP404ProjectBuilderService:
    """Tests for SP-404MK2 project building from kits"""

    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create service instance"""
        return SP404ProjectBuilderService(db_session)

    @pytest_asyncio.fixture
    async def temp_export_dir(self):
        """Create temporary export directory"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    @pytest_asyncio.fixture
    async def test_kit_with_samples(self, db_session, tmp_path):
        """Create test kit with 3 samples at different BPMs"""
        import numpy as np
        import soundfile as sf

        # Create kit
        kit = Kit(
            user_id=1,
            name="Test Hip-Hop Kit",
            description="Test kit for project builder"
        )
        db_session.add(kit)
        await db_session.flush()

        # Create 3 real audio samples with different BPMs
        samples = []
        bpms = [85.0, 90.0, 95.0]

        for i, bpm in enumerate(bpms):
            # Generate real WAV file
            sample_rate = 44100
            duration = 2.0
            frequency = 440 + (i * 50)
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = 0.5 * np.sin(2 * np.pi * frequency * t)

            wav_path = tmp_path / f"sample_{i}.wav"
            sf.write(wav_path, audio, sample_rate)

            # Create sample record
            sample = Sample(
                user_id=1,
                title=f"Sample {i+1}",
                file_path=str(wav_path),
                duration=duration,
                bpm=bpm,
                genre="hip-hop",
                tags=["test"]
            )
            db_session.add(sample)
            await db_session.flush()
            samples.append(sample)

            # Add to kit on pad 1-3 of bank A
            kit_sample = KitSample(
                kit_id=kit.id,
                sample_id=sample.id,
                pad_bank="A",
                pad_number=i + 1
            )
            db_session.add(kit_sample)

        await db_session.commit()
        await db_session.refresh(kit)

        return kit, samples

    @pytest_asyncio.fixture
    async def test_kit_empty(self, db_session):
        """Create empty kit with no samples"""
        kit = Kit(
            user_id=1,
            name="Empty Kit",
            description="Kit with no samples"
        )
        db_session.add(kit)
        await db_session.commit()
        await db_session.refresh(kit)
        return kit

    # ==================
    # SUCCESS PATH TESTS
    # ==================

    @pytest.mark.asyncio
    async def test_build_project_success(self, service, test_kit_with_samples, temp_export_dir):
        """Test successful project build with all components"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="MyProject",
            project_bpm=None,  # Auto-detect
            audio_format="wav",
            include_bank_layout=False
        )

        result = await service.build_project(
            kit_id=kit.id,
            request=request,
            output_base_path=temp_export_dir
        )

        # Verify success
        assert result.success is True
        assert result.export_id is not None
        assert result.project_name == "MyProject"
        assert result.sample_count == 3
        assert result.file_size_bytes > 0
        assert result.download_url is not None
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_build_project_creates_padconf(self, service, test_kit_with_samples, temp_export_dir):
        """Test that PADCONF.BIN is created with correct size"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="TestKit",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        # Extract and verify PADCONF.BIN
        assert result.success is True

        # Find the ZIP file
        zip_files = list(temp_export_dir.glob("*.zip"))
        assert len(zip_files) == 1

        # Extract and check PADCONF.BIN
        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            assert "PADCONF.BIN" in zf.namelist()

            # Extract PADCONF.BIN and verify size
            padconf_data = zf.read("PADCONF.BIN")
            assert len(padconf_data) == 52000, "PADCONF.BIN must be exactly 52,000 bytes"

    @pytest.mark.asyncio
    async def test_build_project_creates_zip(self, service, test_kit_with_samples, temp_export_dir):
        """Test that ZIP file is created with correct structure"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="StructureTest",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True

        # Find ZIP file
        zip_files = list(temp_export_dir.glob("*.zip"))
        assert len(zip_files) == 1

        # Verify ZIP structure
        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            files = zf.namelist()

            # Must contain PADCONF.BIN
            assert "PADCONF.BIN" in files

            # Must contain PROJECT_INFO.txt
            assert "PROJECT_INFO.txt" in files

            # Must contain samples/ directory
            sample_files = [f for f in files if f.startswith("samples/")]
            assert len(sample_files) == 3, "Should have 3 sample files"

            # Verify all samples are WAV format
            for sample_file in sample_files:
                assert sample_file.endswith(".wav")

    @pytest.mark.asyncio
    async def test_detect_project_bpm_median(self, service, test_kit_with_samples):
        """Test BPM auto-detection uses median of sample BPMs"""
        kit, samples = test_kit_with_samples
        # Samples have BPMs: 85, 90, 95
        # Median should be 90.0

        detected_bpm = service._detect_project_bpm(samples)

        assert detected_bpm == 90.0, "Should return median BPM of 90.0"

    @pytest.mark.asyncio
    async def test_detect_project_bpm_fallback(self, service, db_session):
        """Test BPM auto-detection fallback to 120 when no BPMs available"""
        # Create samples without BPM
        samples = [
            Sample(user_id=1, title="No BPM 1", file_path="/test/1.wav", bpm=None),
            Sample(user_id=1, title="No BPM 2", file_path="/test/2.wav", bpm=None)
        ]

        detected_bpm = service._detect_project_bpm(samples)

        assert detected_bpm == 120.0, "Should fallback to 120.0 BPM"

    @pytest.mark.asyncio
    async def test_build_project_with_custom_bpm(self, service, test_kit_with_samples, temp_export_dir):
        """Test project build with user-specified BPM"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="CustomBPM",
            project_bpm=140.0,  # User-specified
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True

        # Verify PADCONF.BIN uses custom BPM
        zip_files = list(temp_export_dir.glob("*.zip"))
        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            padconf_data = zf.read("PADCONF.BIN")

            # Project BPM is at offset 0x13-0x14 (big-endian)
            # 140.0 BPM → 14000
            bpm_bytes = padconf_data[0x13:0x15]
            bpm_int = int.from_bytes(bpm_bytes, 'big')
            assert bpm_int == 14000, "PADCONF should use custom BPM of 140.0"

    @pytest.mark.asyncio
    async def test_audio_export_with_format_conversion(self, service, test_kit_with_samples, temp_export_dir):
        """Test audio samples are converted to 48kHz/16-bit"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="ConversionTest",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True

        # Extract and verify sample properties
        zip_files = list(temp_export_dir.glob("*.zip"))

        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            sample_files = [f for f in zf.namelist() if f.startswith("samples/")]

            # Extract first sample and verify format
            import soundfile as sf
            import io

            sample_data = zf.read(sample_files[0])
            audio_buffer = io.BytesIO(sample_data)

            # Read audio properties
            info = sf.info(audio_buffer)

            assert info.samplerate == 48000, "Sample rate should be 48kHz"
            assert info.subtype == "PCM_16", "Bit depth should be 16-bit"

    @pytest.mark.asyncio
    async def test_audio_export_creates_correct_directory(self, service, test_kit_with_samples, temp_export_dir):
        """Test that samples are organized in samples/ directory"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="DirTest",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        zip_files = list(temp_export_dir.glob("*.zip"))

        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            files = zf.namelist()

            # All audio files should be in samples/
            audio_files = [f for f in files if f.endswith(".wav")]
            for audio_file in audio_files:
                assert audio_file.startswith("samples/"), f"Audio file {audio_file} should be in samples/ directory"

    @pytest.mark.asyncio
    async def test_build_project_aiff_format(self, service, test_kit_with_samples, temp_export_dir):
        """Test project build with AIFF output format"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="AIFFTest",
            audio_format="aiff"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True

        # Verify AIFF files in ZIP
        zip_files = list(temp_export_dir.glob("*.zip"))
        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            sample_files = [f for f in zf.namelist() if f.startswith("samples/")]

            # All samples should be AIFF
            for sample_file in sample_files:
                assert sample_file.endswith(".aiff") or sample_file.endswith(".aif")

    # ================
    # ERROR PATH TESTS
    # ================

    @pytest.mark.asyncio
    async def test_build_project_kit_not_found(self, service, temp_export_dir):
        """Test error handling for non-existent kit"""
        request = ProjectBuildRequest(
            project_name="NoKit",
            audio_format="wav"
        )

        result = await service.build_project(
            kit_id=99999,  # Non-existent
            request=request,
            output_base_path=temp_export_dir
        )

        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
        assert result.export_id is None

    @pytest.mark.asyncio
    async def test_build_project_no_samples(self, service, test_kit_empty, temp_export_dir):
        """Test error handling for kit with no samples"""
        request = ProjectBuildRequest(
            project_name="EmptyKit",
            audio_format="wav"
        )

        result = await service.build_project(
            kit_id=test_kit_empty.id,
            request=request,
            output_base_path=temp_export_dir
        )

        assert result.success is False
        assert result.error_message is not None
        assert "no samples" in result.error_message.lower()
        assert result.sample_count == 0

    @pytest.mark.asyncio
    async def test_build_project_creates_export_record(self, service, test_kit_with_samples, temp_export_dir, db_session):
        """Test that export record is created in database"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="DBTest",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True
        assert result.export_id is not None

        # Verify export record exists
        from app.models.sp404_export import SP404Export
        stmt = select(SP404Export).where(SP404Export.id == int(result.export_id))
        db_result = await db_session.execute(stmt)
        export_record = db_result.scalar_one_or_none()

        assert export_record is not None
        assert export_record.export_type == "project"
        assert export_record.sample_count == 3
        assert export_record.format == "wav"

    @pytest.mark.asyncio
    async def test_build_project_project_info_content(self, service, test_kit_with_samples, temp_export_dir):
        """Test that PROJECT_INFO.txt contains correct metadata"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="InfoTest",
            project_bpm=110.0,
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        zip_files = list(temp_export_dir.glob("*.zip"))
        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            info_content = zf.read("PROJECT_INFO.txt").decode('utf-8')

            # Verify key information is present
            assert "InfoTest" in info_content  # Project name
            assert "110.0" in info_content or "110" in info_content  # BPM
            assert "3" in info_content  # Sample count
            assert "Test Hip-Hop Kit" in info_content  # Kit name

    @pytest.mark.asyncio
    async def test_build_project_sanitizes_filenames(self, service, db_session, tmp_path, temp_export_dir):
        """Test that non-ASCII filenames are sanitized"""
        import numpy as np
        import soundfile as sf

        # Create kit
        kit = Kit(user_id=1, name="Unicode Kit")
        db_session.add(kit)
        await db_session.flush()

        # Create sample with non-ASCII filename
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        wav_path = tmp_path / "測試sample.wav"  # Chinese characters
        sf.write(wav_path, audio, sample_rate)

        sample = Sample(
            user_id=1,
            title="測試 Sample",  # Non-ASCII title
            file_path=str(wav_path),
            duration=1.0,
            bpm=90.0
        )
        db_session.add(sample)
        await db_session.flush()

        kit_sample = KitSample(
            kit_id=kit.id,
            sample_id=sample.id,
            pad_bank="A",
            pad_number=1
        )
        db_session.add(kit_sample)
        await db_session.commit()

        # Build project
        request = ProjectBuildRequest(
            project_name="UnicodeTest",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True

        # Verify filenames are ASCII-safe
        zip_files = list(temp_export_dir.glob("*.zip"))
        with zipfile.ZipFile(zip_files[0], 'r') as zf:
            sample_files = [f for f in zf.namelist() if f.startswith("samples/")]

            for sample_file in sample_files:
                # Should only contain ASCII characters
                assert sample_file.isascii(), f"Filename {sample_file} should be ASCII-safe"

    @pytest.mark.asyncio
    async def test_build_project_download_url_format(self, service, test_kit_with_samples, temp_export_dir):
        """Test that download_url is properly formatted"""
        kit, samples = test_kit_with_samples

        request = ProjectBuildRequest(
            project_name="URLTest",
            audio_format="wav"
        )

        result = await service.build_project(kit.id, request, temp_export_dir)

        assert result.success is True
        assert result.download_url is not None
        assert result.download_url.startswith("/api/v1/")
        assert "download" in result.download_url.lower()
        assert str(result.export_id) in result.download_url
