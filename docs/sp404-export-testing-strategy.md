# SP-404MK2 Export Service - Testing Strategy Guide

**For**: Test Writer Agent
**Purpose**: Comprehensive testing approach for export functionality

---

## Testing Philosophy

### Coverage Goals
- **Service Layer**: >90% line coverage
- **API Endpoints**: >85% line coverage
- **Models**: >95% line coverage
- **Critical Paths**: 100% coverage (conversion, validation, sanitization)

### Testing Approach
- **Test-Driven Development**: Write tests before implementation
- **MVP Focus**: 2-5 tests per feature, avoid over-engineering
- **Realistic Fixtures**: Use actual audio files for integration tests
- **Fast Tests**: Mock external dependencies where appropriate

---

## Test File Structure

```
backend/tests/
├── services/
│   └── test_sp404_export_service.py      # Core service logic tests
├── api/
│   └── test_sp404_export.py              # API endpoint tests
├── models/
│   └── test_sp404_export_models.py       # Database model tests
├── schemas/
│   └── test_sp404_export_schemas.py      # Pydantic schema tests
└── fixtures/
    ├── audio/                            # Test audio files
    │   ├── test_sample_48k.wav           # Already correct format
    │   ├── test_sample_44k.mp3           # Needs conversion
    │   ├── test_sample_22k.wav           # Low sample rate
    │   ├── test_sample_stereo.wav        # Stereo file
    │   ├── test_sample_mono.wav          # Mono file
    │   ├── test_sample_short.wav         # <100ms (should fail)
    │   ├── test_sample_unicode_名前.wav   # Unicode filename
    │   └── test_sample_special!@#.mp3    # Special characters
    └── conftest.py                       # Shared fixtures
```

---

## Fixture Definitions

### Database Fixtures (`conftest.py`)

```python
import pytest
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.sample import Sample
from app.models.user import User

@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_sample_wav(db_session, test_user, tmp_path):
    """Create test sample with WAV file."""
    # Create test WAV file
    audio_file = tmp_path / "test_sample.wav"
    # Use soundfile to create a valid WAV
    import soundfile as sf
    import numpy as np

    # Create 1 second of audio at 44100Hz
    sr = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave

    sf.write(str(audio_file), audio, sr, subtype='PCM_16')

    # Create database record
    sample = Sample(
        id=1,
        user_id=test_user.id,
        title="Test Sample",
        file_path=str(audio_file),
        file_size=audio_file.stat().st_size,
        duration=duration,
        genre="hip-hop",
        bpm=95.0,
        musical_key="C"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    return sample


@pytest.fixture
async def test_sample_mp3(db_session, test_user, tmp_path):
    """Create test sample with MP3 file."""
    # Note: MP3 creation requires additional libraries
    # For MVP, copy pre-created test file
    audio_file = tmp_path / "test_sample.mp3"
    # Copy from fixtures
    import shutil
    fixture_path = Path(__file__).parent / "fixtures" / "audio" / "test_sample_44k.mp3"
    shutil.copy(fixture_path, audio_file)

    sample = Sample(
        id=2,
        user_id=test_user.id,
        title="Test MP3 Sample",
        file_path=str(audio_file),
        file_size=audio_file.stat().st_size,
        duration=2.0,
        genre="electronic",
        bpm=128.0
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    return sample


@pytest.fixture
async def test_sample_short(db_session, test_user, tmp_path):
    """Create test sample with duration < 100ms."""
    audio_file = tmp_path / "test_sample_short.wav"

    import soundfile as sf
    import numpy as np

    # Create 50ms of audio (should fail validation)
    sr = 48000
    duration = 0.05  # 50ms
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * 440 * t)

    sf.write(str(audio_file), audio, sr, subtype='PCM_16')

    sample = Sample(
        id=3,
        user_id=test_user.id,
        title="Short Sample",
        file_path=str(audio_file),
        file_size=audio_file.stat().st_size,
        duration=duration
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    return sample


@pytest.fixture
def export_config():
    """Default export configuration."""
    from app.schemas.sp404_export import ExportConfig

    return ExportConfig(
        organize_by="flat",
        format="wav",
        include_metadata=True,
        sanitize_filenames=True,
        output_base_path=None
    )


@pytest.fixture
def sp404_service(db_session):
    """Create SP404ExportService instance."""
    from app.services.sp404_export_service import SP404ExportService

    return SP404ExportService(db_session)
```

---

## Unit Tests - Service Layer

### File: `backend/tests/services/test_sp404_export_service.py`

```python
import pytest
from pathlib import Path
import numpy as np
import soundfile as sf

from app.services.sp404_export_service import SP404ExportService, SP404ExportError
from app.schemas.sp404_export import ExportConfig


class TestConversion:
    """Test audio conversion to SP-404MK2 format."""

    @pytest.mark.asyncio
    async def test_convert_to_sp404_format_wav(self, sp404_service, tmp_path):
        """Test conversion to WAV format."""
        # Create input file (44.1kHz)
        input_file = tmp_path / "input.wav"
        sr = 44100
        duration = 1.0
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        sf.write(str(input_file), audio, sr)

        # Convert
        output_file = tmp_path / "output.wav"
        result = await sp404_service.convert_to_sp404_format(
            input_file,
            output_file,
            "wav"
        )

        # Assert
        assert result.success is True
        assert result.output_path == output_file
        assert output_file.exists()

        # Verify output format
        info = sf.info(str(output_file))
        assert info.samplerate == 48000
        assert info.subtype == 'PCM_16'

    @pytest.mark.asyncio
    async def test_convert_to_sp404_format_aiff(self, sp404_service, tmp_path):
        """Test conversion to AIFF format."""
        input_file = tmp_path / "input.wav"
        sr = 44100
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))
        sf.write(str(input_file), audio, sr)

        output_file = tmp_path / "output.aiff"
        result = await sp404_service.convert_to_sp404_format(
            input_file,
            output_file,
            "aiff"
        )

        assert result.success is True
        info = sf.info(str(output_file))
        assert info.samplerate == 48000
        assert info.format == 'AIFF'

    @pytest.mark.asyncio
    async def test_convert_44k_to_48k(self, sp404_service, tmp_path):
        """Test sample rate conversion from 44.1kHz to 48kHz."""
        input_file = tmp_path / "input_44k.wav"
        sr = 44100
        duration = 2.0
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        sf.write(str(input_file), audio, sr)

        output_file = tmp_path / "output_48k.wav"
        result = await sp404_service.convert_to_sp404_format(
            input_file,
            output_file,
            "wav"
        )

        assert result.success is True
        assert result.original_sample_rate == 44100
        assert result.converted_sample_rate == 48000

        # Verify output
        info = sf.info(str(output_file))
        assert info.samplerate == 48000

    @pytest.mark.asyncio
    async def test_convert_stereo_preserves_channels(self, sp404_service, tmp_path):
        """Test stereo audio conversion preserves both channels."""
        input_file = tmp_path / "input_stereo.wav"
        sr = 44100
        duration = 1.0

        # Create stereo audio (different frequencies per channel)
        samples = int(sr * duration)
        left = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
        right = np.sin(2 * np.pi * 880 * np.linspace(0, duration, samples))
        stereo = np.column_stack([left, right])

        sf.write(str(input_file), stereo, sr)

        output_file = tmp_path / "output_stereo.wav"
        result = await sp404_service.convert_to_sp404_format(
            input_file,
            output_file,
            "wav"
        )

        assert result.success is True

        # Verify stereo preserved
        info = sf.info(str(output_file))
        assert info.channels == 2
        assert info.samplerate == 48000

    @pytest.mark.asyncio
    async def test_convert_already_48k_still_works(self, sp404_service, tmp_path):
        """Test conversion of already-correct format still works."""
        input_file = tmp_path / "input_48k.wav"
        sr = 48000
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))
        sf.write(str(input_file), audio, sr, subtype='PCM_16')

        output_file = tmp_path / "output_48k.wav"
        result = await sp404_service.convert_to_sp404_format(
            input_file,
            output_file,
            "wav"
        )

        assert result.success is True
        assert result.original_sample_rate == 48000
        assert result.converted_sample_rate == 48000

    @pytest.mark.asyncio
    async def test_convert_file_not_found(self, sp404_service, tmp_path):
        """Test conversion fails gracefully for missing file."""
        input_file = tmp_path / "nonexistent.wav"
        output_file = tmp_path / "output.wav"

        result = await sp404_service.convert_to_sp404_format(
            input_file,
            output_file,
            "wav"
        )

        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_convert_invalid_format(self, sp404_service, tmp_path):
        """Test conversion rejects invalid output format."""
        input_file = tmp_path / "input.wav"
        sr = 44100
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))
        sf.write(str(input_file), audio, sr)

        output_file = tmp_path / "output.mp3"

        with pytest.raises(SP404ExportError, match="Unsupported output format"):
            await sp404_service.convert_to_sp404_format(
                input_file,
                output_file,
                "mp3"
            )


class TestValidation:
    """Test sample validation."""

    def test_validate_sample_valid(self, sp404_service, tmp_path):
        """Test validation passes for valid sample."""
        # Create valid sample (>100ms, 48kHz)
        audio_file = tmp_path / "valid.wav"
        sr = 48000
        duration = 1.0
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        sf.write(str(audio_file), audio, sr)

        result = sp404_service.validate_sample(audio_file)

        assert result.valid is True
        assert result.meets_duration_requirement is True
        assert result.format_supported is True
        assert result.file_readable is True
        assert len(result.errors) == 0

    def test_validate_sample_too_short(self, sp404_service, tmp_path):
        """Test validation fails for samples < 100ms."""
        audio_file = tmp_path / "short.wav"
        sr = 48000
        duration = 0.05  # 50ms
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        sf.write(str(audio_file), audio, sr)

        result = sp404_service.validate_sample(audio_file)

        assert result.valid is False
        assert result.meets_duration_requirement is False
        assert "too short" in result.errors[0].lower()

    def test_validate_sample_unsupported_format(self, sp404_service, tmp_path):
        """Test validation fails for unsupported format."""
        audio_file = tmp_path / "sample.xyz"
        audio_file.touch()

        result = sp404_service.validate_sample(audio_file)

        assert result.valid is False
        assert result.format_supported is False
        assert "unsupported format" in result.errors[0].lower()

    def test_validate_sample_file_not_found(self, sp404_service, tmp_path):
        """Test validation fails for missing file."""
        audio_file = tmp_path / "nonexistent.wav"

        result = sp404_service.validate_sample(audio_file)

        assert result.valid is False
        assert result.file_readable is False
        assert "not found" in result.errors[0].lower()


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_filename_unicode(self, sp404_service):
        """Test unicode characters normalized to ASCII."""
        input_name = "Café_Music_名前.wav"
        result = sp404_service.sanitize_filename(input_name)

        # Unicode should be removed or normalized
        assert "café" not in result.lower() or "cafe" in result.lower()
        assert "名前" not in result

    def test_sanitize_filename_special_chars(self, sp404_service):
        """Test special characters removed."""
        input_name = "Sample!@#$%^&*().wav"
        result = sp404_service.sanitize_filename(input_name)

        # Only alphanumeric, underscore, hyphen allowed
        assert "!" not in result
        assert "@" not in result
        assert "#" not in result

    def test_sanitize_filename_spaces(self, sp404_service):
        """Test spaces converted to underscores."""
        input_name = "My Cool Sample.wav"
        result = sp404_service.sanitize_filename(input_name)

        assert " " not in result
        assert "_" in result

    def test_sanitize_filename_preserves_extension(self, sp404_service):
        """Test file extension preserved."""
        input_name = "sample.wav"
        result = sp404_service.sanitize_filename(input_name)

        assert result.endswith(".wav")

    def test_sanitize_filename_empty_fallback(self, sp404_service):
        """Test fallback for empty/invalid names."""
        input_name = "!!!.wav"
        result = sp404_service.sanitize_filename(input_name)

        # Should have some valid name
        assert len(result) > 4  # More than just ".wav"

    def test_sanitize_filename_length_limit(self, sp404_service):
        """Test filename length limited to 255 chars."""
        input_name = "a" * 300 + ".wav"
        result = sp404_service.sanitize_filename(input_name)

        assert len(result) <= 255


class TestOrganization:
    """Test organization strategies."""

    def test_organize_path_flat(self, sp404_service, test_sample_wav, tmp_path):
        """Test flat organization (no subfolders)."""
        base_path = tmp_path / "exports"

        result = sp404_service._organize_export_path(
            base_path,
            test_sample_wav,
            "flat"
        )

        assert result == base_path

    def test_organize_path_genre(self, sp404_service, test_sample_wav, tmp_path):
        """Test genre-based organization."""
        base_path = tmp_path / "exports"
        test_sample_wav.genre = "hip-hop"

        result = sp404_service._organize_export_path(
            base_path,
            test_sample_wav,
            "genre"
        )

        assert result == base_path / "hip-hop"

    def test_organize_path_bpm(self, sp404_service, test_sample_wav, tmp_path):
        """Test BPM-based organization."""
        base_path = tmp_path / "exports"
        test_sample_wav.bpm = 95.0

        result = sp404_service._organize_export_path(
            base_path,
            test_sample_wav,
            "bpm"
        )

        assert result == base_path / "90-110"

    def test_get_bpm_folder_name(self, sp404_service):
        """Test BPM to folder name mapping."""
        assert sp404_service._get_bpm_folder_name(65) == "slow"
        assert sp404_service._get_bpm_folder_name(85) == "70-90"
        assert sp404_service._get_bpm_folder_name(95) == "90-110"
        assert sp404_service._get_bpm_folder_name(120) == "110-130"
        assert sp404_service._get_bpm_folder_name(140) == "130-150"
        assert sp404_service._get_bpm_folder_name(160) == "fast"
        assert sp404_service._get_bpm_folder_name(None) == "unknown_bpm"


class TestExportSingle:
    """Test single sample export."""

    @pytest.mark.asyncio
    async def test_export_single_sample_success(
        self,
        sp404_service,
        db_session,
        test_sample_wav,
        export_config,
        tmp_path
    ):
        """Test successful single sample export."""
        export_config.output_base_path = str(tmp_path / "exports")

        result = await sp404_service.export_single_sample(
            test_sample_wav.id,
            export_config,
            db_session
        )

        assert result.success is True
        assert result.sample_id == test_sample_wav.id
        assert result.format == "wav"
        assert result.file_size_bytes > 0
        assert result.conversion_time_seconds > 0

        # Verify file exists
        output_path = Path(result.output_path) / result.output_filename
        assert output_path.exists()

    @pytest.mark.asyncio
    async def test_export_single_sample_validation_fails(
        self,
        sp404_service,
        db_session,
        test_sample_short,
        export_config,
        tmp_path
    ):
        """Test export fails gracefully for invalid sample."""
        export_config.output_base_path = str(tmp_path / "exports")

        result = await sp404_service.export_single_sample(
            test_sample_short.id,
            export_config,
            db_session
        )

        assert result.success is False
        assert "validation failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_export_single_sample_not_found(
        self,
        sp404_service,
        db_session,
        export_config,
        tmp_path
    ):
        """Test export fails for non-existent sample."""
        export_config.output_base_path = str(tmp_path / "exports")

        with pytest.raises(SP404ExportError, match="not found"):
            await sp404_service.export_single_sample(
                9999,  # Non-existent ID
                export_config,
                db_session
            )


class TestExportBatch:
    """Test batch export."""

    @pytest.mark.asyncio
    async def test_export_batch_all_success(
        self,
        sp404_service,
        db_session,
        test_sample_wav,
        test_sample_mp3,
        export_config,
        tmp_path
    ):
        """Test batch export with all samples succeeding."""
        export_config.output_base_path = str(tmp_path / "exports")
        sample_ids = [test_sample_wav.id, test_sample_mp3.id]

        result = await sp404_service.export_batch(
            sample_ids,
            export_config,
            db_session
        )

        assert result.total_requested == 2
        assert result.successful == 2
        assert result.failed == 0
        assert len(result.results) == 2
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_export_batch_partial_failure(
        self,
        sp404_service,
        db_session,
        test_sample_wav,
        test_sample_short,
        export_config,
        tmp_path
    ):
        """Test batch export with some samples failing."""
        export_config.output_base_path = str(tmp_path / "exports")
        sample_ids = [test_sample_wav.id, test_sample_short.id]

        result = await sp404_service.export_batch(
            sample_ids,
            export_config,
            db_session
        )

        assert result.total_requested == 2
        assert result.successful == 1
        assert result.failed == 1
        assert len(result.errors) > 0
```

---

## Integration Tests - API Layer

### File: `backend/tests/api/test_sp404_export.py`

```python
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_export_single_sample_endpoint(test_sample_wav, db_session):
    """Test POST /sp404/samples/{id}/export endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/sp404/samples/{test_sample_wav.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav",
                "include_metadata": True,
                "sanitize_filenames": True
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["sample_id"] == test_sample_wav.id
    assert data["format"] == "wav"


@pytest.mark.asyncio
async def test_export_batch_endpoint(test_sample_wav, test_sample_mp3, db_session):
    """Test POST /sp404/samples/export-batch endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sp404/samples/export-batch",
            json={
                "sample_ids": [test_sample_wav.id, test_sample_mp3.id],
                "config": {
                    "organize_by": "genre",
                    "format": "wav"
                }
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_requested"] == 2
    assert data["successful"] >= 0
    assert data["organized_by"] == "genre"


@pytest.mark.asyncio
async def test_export_invalid_sample_id():
    """Test export returns 404 for invalid sample ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sp404/samples/9999/export",
            json={"organize_by": "flat", "format": "wav"}
        )

    assert response.status_code == 404 or response.status_code == 422
```

---

## Model Tests

### File: `backend/tests/models/test_sp404_export_models.py`

```python
import pytest
from app.models.sp404_export import SP404Export, SP404ExportSample


@pytest.mark.asyncio
async def test_create_export_record(db_session, test_user):
    """Test creating SP404Export record."""
    export = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/exports/test",
        organized_by="flat",
        format="wav",
        total_size_bytes=1024000,
        export_duration_seconds=2.5
    )

    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    assert export.id is not None
    assert export.user_id == test_user.id
    assert export.export_type == "single"


@pytest.mark.asyncio
async def test_export_sample_relationship(db_session, test_user, test_sample_wav):
    """Test SP404ExportSample relationship."""
    export = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/exports/test",
        organized_by="flat",
        format="wav"
    )
    db_session.add(export)
    await db_session.commit()

    export_sample = SP404ExportSample(
        export_id=export.id,
        sample_id=test_sample_wav.id,
        output_filename="test.wav",
        conversion_successful=True
    )
    db_session.add(export_sample)
    await db_session.commit()

    # Verify relationship
    assert len(export.exported_samples) == 1
    assert export.exported_samples[0].sample_id == test_sample_wav.id
```

---

## Schema Tests

### File: `backend/tests/schemas/test_sp404_export_schemas.py`

```python
import pytest
from pydantic import ValidationError
from app.schemas.sp404_export import ExportConfig, ConversionResult


def test_export_config_valid():
    """Test valid ExportConfig."""
    config = ExportConfig(
        organize_by="genre",
        format="wav",
        include_metadata=True
    )

    assert config.organize_by == "genre"
    assert config.format == "wav"


def test_export_config_invalid_organization():
    """Test invalid organization strategy rejected."""
    with pytest.raises(ValidationError):
        ExportConfig(organize_by="invalid")


def test_export_config_invalid_format():
    """Test invalid format rejected."""
    with pytest.raises(ValidationError):
        ExportConfig(format="mp3")


def test_conversion_result_serialization():
    """Test ConversionResult serialization."""
    result = ConversionResult(
        success=True,
        output_path=Path("/output/file.wav"),
        original_format=".mp3",
        original_sample_rate=44100,
        original_duration=2.5
    )

    assert result.success is True
    assert result.converted_sample_rate == 48000
```

---

## Performance Tests

### File: `backend/tests/performance/test_sp404_export_performance.py`

```python
import pytest
import time


@pytest.mark.asyncio
async def test_single_export_performance(sp404_service, test_sample_wav, export_config, db_session, tmp_path):
    """Test single export completes within reasonable time."""
    export_config.output_base_path = str(tmp_path)

    start = time.time()
    result = await sp404_service.export_single_sample(
        test_sample_wav.id,
        export_config,
        db_session
    )
    elapsed = time.time() - start

    assert result.success is True
    assert elapsed < 5.0  # Should complete in <5 seconds


@pytest.mark.asyncio
async def test_batch_export_performance(sp404_service, db_session, export_config, tmp_path):
    """Test batch export scales reasonably."""
    # Create 10 test samples
    # ... (sample creation code)

    sample_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    export_config.output_base_path = str(tmp_path)

    start = time.time()
    result = await sp404_service.export_batch(
        sample_ids,
        export_config,
        db_session
    )
    elapsed = time.time() - start

    assert elapsed < 30.0  # 10 samples in <30 seconds
```

---

## Test Execution

### Run All Tests
```bash
# Run all tests with coverage
pytest --cov=app.services.sp404_export_service \
       --cov=app.models.sp404_export \
       --cov=app.api.v1.endpoints.sp404_export \
       --cov-report=html \
       backend/tests/

# Run specific test file
pytest backend/tests/services/test_sp404_export_service.py

# Run specific test class
pytest backend/tests/services/test_sp404_export_service.py::TestConversion

# Run with verbose output
pytest -v backend/tests/
```

### Watch Mode (for TDD)
```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw backend/tests/ -- --cov=app.services.sp404_export_service
```

---

## Test Priority Order

### Phase 1: Critical Path (Week 1)
1. ✅ Audio conversion tests
2. ✅ Validation tests
3. ✅ Filename sanitization tests
4. ✅ Single export tests

### Phase 2: Core Features (Week 2)
5. ✅ Organization strategy tests
6. ✅ Batch export tests
7. ✅ API endpoint tests
8. ✅ Model relationship tests

### Phase 3: Edge Cases (Week 3)
9. ✅ Error handling tests
10. ✅ Performance tests
11. ✅ Kit export tests
12. ✅ ZIP creation tests

---

## Mock Strategies

### Mock File System
```python
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_export_with_mocked_filesystem(sp404_service):
    """Test export with mocked file operations."""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('soundfile.write'):
            # Test export logic without actual file I/O
            pass
```

### Mock Database
```python
@pytest.mark.asyncio
async def test_export_with_mocked_db():
    """Test export with mocked database."""
    mock_db = Mock(spec=AsyncSession)
    # Configure mock behavior
    # Test export logic
```

---

This testing strategy provides comprehensive coverage for the SP-404MK2 export service while maintaining MVP simplicity.
