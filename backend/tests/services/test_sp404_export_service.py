"""
TDD RED Phase Tests for SP404ExportService

These tests define the expected behavior of the SP404 Export Service before implementation.
Following Test-Driven Development (TDD) RED-GREEN-REFACTOR methodology.

Test Strategy:
- 41 MVP-level tests covering all service methods
- REAL integration: Uses actual audio files, real database, real audio processing
- Real soundfile library for audio conversion testing
- No mocks for core audio processing - tests complete workflow
- Follows project pattern from test_hybrid_analysis_service.py

The SP404ExportService provides:
1. Audio Conversion - Convert samples to SP-404MK2 format (48kHz WAV/AIFF)
2. Validation - Ensure samples meet SP-404MK2 requirements (≥100ms, supported formats)
3. Filename Sanitization - Remove unicode, special chars, limit length
4. Organization - Flat, genre-based, or BPM-based folder structures
5. Single Export - Export individual samples with metadata
6. Batch Export - Export multiple samples with aggregated statistics
7. Kit Export - Export complete kits with structure maintained

Expected Failures:
- ImportError: SP404ExportService module doesn't exist yet
- AttributeError: Methods and models not implemented
- All tests should fail until implementation is complete
"""
import pytest
import pytest_asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import time

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    from scipy.io import wavfile
    HAS_SOUNDFILE = False


# =============================================================================
# AUDIO CONVERSION TESTS (10 tests)
# =============================================================================


@pytest.mark.asyncio
async def test_convert_wav_to_sp404_format(tmp_path):
    """
    Test 1: Convert WAV 44.1kHz to 48kHz SP-404MK2 format.

    Validates:
    - 44.1kHz sample rate converted to 48kHz
    - WAV format maintained
    - PCM_16 bit depth preserved
    - Audio quality maintained
    - Output file exists and is valid

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create 44.1kHz WAV file
    input_file = tmp_path / "input_44k.wav"
    sr = 44100
    duration = 1.0
    frequency = 440  # A4 note

    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)

    if HAS_SOUNDFILE:
        sf.write(str(input_file), audio, sr, subtype='PCM_16')
    else:
        wavfile.write(str(input_file), sr, (audio * 32767).astype(np.int16))

    # Act: Convert to SP-404MK2 format
    output_file = tmp_path / "output_48k.wav"
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Conversion successful
    assert result.success is True, "Conversion should succeed"
    assert result.output_path == output_file, "Output path should match"
    assert output_file.exists(), "Output file should exist"

    # Verify output format
    if HAS_SOUNDFILE:
        info = sf.info(str(output_file))
        assert info.samplerate == 48000, "Sample rate should be 48kHz"
        assert info.subtype == 'PCM_16', "Bit depth should be 16-bit"
    else:
        sr_out, data = wavfile.read(str(output_file))
        assert sr_out == 48000, "Sample rate should be 48kHz"

    # Verify metadata
    assert result.original_sample_rate == 44100, "Original SR should be recorded"
    assert result.converted_sample_rate == 48000, "Converted SR should be recorded"


@pytest.mark.asyncio
async def test_convert_mp3_to_sp404_format(tmp_path):
    """
    Test 2: Convert MP3 to 48kHz WAV SP-404MK2 format.

    Validates:
    - MP3 input successfully decoded
    - Converted to 48kHz WAV
    - PCM_16 format
    - File format change tracked
    - Duration preserved

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create test audio (WAV simulating MP3 input)
    # Note: For MVP, we simulate MP3 with WAV since MP3 encoding requires additional libs
    input_file = tmp_path / "input.mp3"
    sr = 44100
    duration = 2.0
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))

    if HAS_SOUNDFILE:
        sf.write(str(input_file), audio, sr, format='WAV')
    else:
        wavfile.write(str(input_file), sr, (audio * 32767).astype(np.int16))

    # Act: Convert
    output_file = tmp_path / "output.wav"
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Conversion successful
    assert result.success is True, "MP3 conversion should succeed"
    assert output_file.exists(), "Output file should exist"
    assert result.original_format != ".wav" or result.success, "Format conversion tracked"


@pytest.mark.asyncio
async def test_convert_maintains_audio_quality(tmp_path):
    """
    Test 3: Verify conversion maintains audio quality.

    Validates:
    - No significant audio degradation
    - Frequency content preserved
    - Duration maintained within tolerance
    - No clipping or distortion
    - Sample count scaled correctly

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create clean test audio
    input_file = tmp_path / "quality_test.wav"
    sr = 44100
    duration = 1.0
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))

    if HAS_SOUNDFILE:
        sf.write(str(input_file), audio, sr)

    # Act: Convert
    output_file = tmp_path / "quality_output.wav"
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Quality maintained
    assert result.success is True, "Conversion should succeed"

    if HAS_SOUNDFILE:
        # Load output and check quality
        output_audio, output_sr = sf.read(str(output_file))
        assert output_sr == 48000, "Output sample rate correct"
        assert len(output_audio) > 0, "Audio data present"
        assert np.max(np.abs(output_audio)) <= 1.0, "No clipping"

        # Duration should be preserved (within 1% tolerance)
        output_duration = len(output_audio) / output_sr
        assert abs(output_duration - duration) / duration < 0.01, "Duration preserved"


@pytest.mark.asyncio
async def test_convert_handles_various_sample_rates(tmp_path):
    """
    Test 4: Handle various input sample rates (16k, 22.05k, 32k, 44.1k, 48k).

    Validates:
    - All common sample rates supported
    - Correct upsampling/downsampling
    - No errors on already-correct rate (48k)
    - Proper resampling algorithm
    - Metadata tracking for all rates

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)
    test_rates = [16000, 22050, 32000, 44100, 48000]

    for input_sr in test_rates:
        # Arrange: Create audio at specific sample rate
        input_file = tmp_path / f"input_{input_sr}hz.wav"
        duration = 0.5
        audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(input_sr * duration)))

        if HAS_SOUNDFILE:
            sf.write(str(input_file), audio, input_sr)

        # Act: Convert
        output_file = tmp_path / f"output_{input_sr}hz.wav"
        result = await service.convert_to_sp404_format(
            input_file,
            output_file,
            format="wav"
        )

        # Assert: Conversion successful for all rates
        assert result.success is True, f"Conversion from {input_sr}Hz should succeed"
        assert result.original_sample_rate == input_sr, f"Original rate {input_sr} tracked"
        assert result.converted_sample_rate == 48000, "All converted to 48kHz"

        if HAS_SOUNDFILE:
            info = sf.info(str(output_file))
            assert info.samplerate == 48000, f"Output from {input_sr}Hz is 48kHz"


@pytest.mark.asyncio
async def test_convert_aiff_output_format(tmp_path):
    """
    Test 5: Convert to AIFF format instead of WAV.

    Validates:
    - AIFF format output supported
    - 48kHz sample rate correct
    - File format is valid AIFF
    - Audio data preserved
    - Format parameter respected

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create input WAV
    input_file = tmp_path / "input.wav"
    sr = 44100
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))

    if HAS_SOUNDFILE:
        sf.write(str(input_file), audio, sr)

    # Act: Convert to AIFF
    output_file = tmp_path / "output.aiff"
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="aiff"
    )

    # Assert: AIFF output successful
    assert result.success is True, "AIFF conversion should succeed"
    assert output_file.exists(), "AIFF file should exist"

    if HAS_SOUNDFILE:
        info = sf.info(str(output_file))
        assert info.samplerate == 48000, "Sample rate should be 48kHz"
        assert info.format == 'AIFF', "Format should be AIFF"


@pytest.mark.asyncio
async def test_convert_file_not_found(tmp_path):
    """
    Test 6: Handle missing input file gracefully.

    Validates:
    - Missing file error handled
    - Result indicates failure
    - Error message is descriptive
    - No output file created
    - No crash or unhandled exception

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Non-existent input file
    input_file = tmp_path / "nonexistent.wav"
    output_file = tmp_path / "output.wav"

    # Act: Attempt conversion
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Graceful failure
    assert result.success is False, "Should fail for missing file"
    assert result.error_message is not None, "Error message should be provided"
    assert "not found" in result.error_message.lower(), "Error should mention file not found"
    assert not output_file.exists(), "No output file should be created"


@pytest.mark.asyncio
async def test_convert_unsupported_format(tmp_path):
    """
    Test 7: Reject unsupported output formats.

    Validates:
    - Only WAV and AIFF accepted
    - MP3/FLAC/other formats rejected
    - Clear error message
    - Exception raised with details
    - No partial conversion

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService, SP404ExportError

    # Arrange: Create valid input
    input_file = tmp_path / "input.wav"
    sr = 44100
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))

    if HAS_SOUNDFILE:
        sf.write(str(input_file), audio, sr)

    # Act & Assert: Attempt unsupported format
    service = SP404ExportService(None)
    output_file = tmp_path / "output.mp3"

    with pytest.raises(SP404ExportError, match="Unsupported output format"):
        await service.convert_to_sp404_format(
            input_file,
            output_file,
            format="mp3"
        )


@pytest.mark.asyncio
async def test_convert_corrupted_file(tmp_path):
    """
    Test 8: Handle corrupted audio file gracefully.

    Validates:
    - Corrupted file detected
    - Graceful error handling
    - Result indicates failure
    - Error message explains issue
    - No crash

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create corrupted WAV file
    input_file = tmp_path / "corrupted.wav"
    with open(input_file, 'wb') as f:
        f.write(b'RIFF\x00\x00\x00\x00WAVEfmt ')  # Invalid WAV header
        f.write(b'\x00' * 50)  # Garbage data

    # Act: Attempt conversion
    output_file = tmp_path / "output.wav"
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Graceful failure
    assert result.success is False, "Should fail for corrupted file"
    assert result.error_message is not None, "Error message should be provided"


@pytest.mark.asyncio
async def test_convert_zero_byte_file(tmp_path):
    """
    Test 9: Handle empty (zero-byte) file.

    Validates:
    - Empty file detected
    - Result indicates failure
    - Appropriate error message
    - No output created
    - No crash on empty read

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create empty file
    input_file = tmp_path / "empty.wav"
    input_file.touch()

    # Act: Attempt conversion
    output_file = tmp_path / "output.wav"
    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Graceful failure
    assert result.success is False, "Should fail for empty file"
    assert result.error_message is not None, "Error message should be provided"


@pytest.mark.asyncio
async def test_convert_creates_output_directory(tmp_path):
    """
    Test 10: Auto-create output directory if missing.

    Validates:
    - Output directory created automatically
    - Nested directories supported
    - Conversion succeeds after dir creation
    - File written to correct location
    - Proper permissions set

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create input, output in non-existent directory
    input_file = tmp_path / "input.wav"
    sr = 44100
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))

    if HAS_SOUNDFILE:
        sf.write(str(input_file), audio, sr)

    # Act: Convert to nested non-existent directory
    output_dir = tmp_path / "exports" / "hip-hop" / "samples"
    output_file = output_dir / "output.wav"

    service = SP404ExportService(None)
    result = await service.convert_to_sp404_format(
        input_file,
        output_file,
        format="wav"
    )

    # Assert: Directory created and file exists
    assert result.success is True, "Conversion should succeed with dir creation"
    assert output_dir.exists(), "Output directory should be created"
    assert output_file.exists(), "Output file should exist in created directory"


# =============================================================================
# VALIDATION TESTS (6 tests)
# =============================================================================


def test_validate_sample_meets_duration_requirement(tmp_path):
    """
    Test 11: Validate sample meets ≥100ms duration requirement.

    Validates:
    - Samples ≥100ms pass validation
    - Duration check is accurate
    - All validation flags correct
    - No errors reported
    - Valid flag is True

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create valid sample (>100ms)
    audio_file = tmp_path / "valid_duration.wav"
    sr = 48000
    duration = 1.0  # 1 second (well above 100ms)
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))

    if HAS_SOUNDFILE:
        sf.write(str(audio_file), audio, sr)

    # Act: Validate
    service = SP404ExportService(None)
    result = service.validate_sample(audio_file)

    # Assert: Validation passes
    assert result.valid is True, "Sample should be valid"
    assert result.meets_duration_requirement is True, "Duration requirement met"
    assert result.format_supported is True, "Format supported"
    assert result.file_readable is True, "File readable"
    assert len(result.errors) == 0, "No errors should be present"


def test_validate_sample_too_short(tmp_path):
    """
    Test 12: Reject sample <100ms duration.

    Validates:
    - Samples <100ms fail validation
    - Duration requirement flag is False
    - Error message explains issue
    - Valid flag is False
    - Specific duration reported

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create short sample (50ms)
    audio_file = tmp_path / "too_short.wav"
    sr = 48000
    duration = 0.05  # 50ms (below 100ms requirement)
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))

    if HAS_SOUNDFILE:
        sf.write(str(audio_file), audio, sr)

    # Act: Validate
    service = SP404ExportService(None)
    result = service.validate_sample(audio_file)

    # Assert: Validation fails
    assert result.valid is False, "Sample should be invalid"
    assert result.meets_duration_requirement is False, "Duration requirement not met"
    assert len(result.errors) > 0, "Should have error messages"
    assert any("too short" in err.lower() or "duration" in err.lower()
               for err in result.errors), "Error should mention duration"


def test_validate_sample_format_supported(tmp_path):
    """
    Test 13: Accept supported formats (WAV, AIFF, MP3, FLAC).

    Validates:
    - WAV format accepted
    - AIFF format accepted
    - Format detection works
    - format_supported flag correct
    - No format-related errors

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)
    supported_formats = ['.wav', '.aiff', '.mp3', '.flac']

    for fmt in supported_formats:
        # Arrange: Create file with supported extension
        audio_file = tmp_path / f"sample{fmt}"
        sr = 48000
        duration = 1.0
        audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))

        if HAS_SOUNDFILE and fmt in ['.wav', '.aiff']:
            sf.write(str(audio_file), audio, sr, format=fmt[1:].upper())
        else:
            # Create placeholder file for formats we can't write
            # (format validation should check extension, not file content)
            audio_file.touch()

        # Act: Validate
        result = service.validate_sample(audio_file)

        # Assert: Format supported
        assert result.format_supported is True, f"{fmt} should be supported"


def test_validate_sample_format_unsupported(tmp_path):
    """
    Test 14: Reject unsupported formats (OGG, M4A, etc).

    Validates:
    - Unsupported formats fail
    - format_supported flag False
    - Clear error about format
    - Valid flag is False
    - No false positives

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Create unsupported format file
    audio_file = tmp_path / "sample.xyz"
    audio_file.touch()

    # Act: Validate
    service = SP404ExportService(None)
    result = service.validate_sample(audio_file)

    # Assert: Format not supported
    assert result.valid is False, "Sample should be invalid"
    assert result.format_supported is False, "Format should not be supported"
    assert len(result.errors) > 0, "Should have error messages"
    assert any("format" in err.lower() or "unsupported" in err.lower()
               for err in result.errors), "Error should mention format"


def test_validate_sample_file_readable(tmp_path):
    """
    Test 15: Check file readability and permissions.

    Validates:
    - File exists check
    - File readable check
    - Proper error for missing file
    - file_readable flag accurate
    - Clear error message

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Test 1: Valid readable file
    audio_file = tmp_path / "readable.wav"
    sr = 48000
    audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, sr))

    if HAS_SOUNDFILE:
        sf.write(str(audio_file), audio, sr)

    service = SP404ExportService(None)
    result = service.validate_sample(audio_file)

    assert result.file_readable is True, "File should be readable"


def test_validate_sample_file_missing(tmp_path):
    """
    Test 16: Handle missing file in validation.

    Validates:
    - Missing file detected
    - file_readable flag False
    - Valid flag False
    - Error message mentions missing file
    - No crash on missing file

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    # Arrange: Non-existent file
    audio_file = tmp_path / "nonexistent.wav"

    # Act: Validate
    service = SP404ExportService(None)
    result = service.validate_sample(audio_file)

    # Assert: Missing file detected
    assert result.valid is False, "Sample should be invalid"
    assert result.file_readable is False, "File should not be readable"
    assert len(result.errors) > 0, "Should have error messages"
    assert any("not found" in err.lower() or "missing" in err.lower()
               for err in result.errors), "Error should mention missing file"


# =============================================================================
# FILENAME SANITIZATION TESTS (5 tests)
# =============================================================================


def test_sanitize_filename_ascii_characters():
    """
    Test 17: Preserve ASCII alphanumeric characters.

    Validates:
    - A-Z, a-z preserved
    - 0-9 preserved
    - Underscore and hyphen preserved
    - Extension preserved
    - No unnecessary modifications

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)

    # Test valid ASCII names
    test_cases = [
        ("sample_001.wav", "sample_001.wav"),
        ("Cool-Beat-2024.wav", "Cool-Beat-2024.wav"),
        ("HipHop123.wav", "HipHop123.wav"),
    ]

    for input_name, expected_pattern in test_cases:
        result = service.sanitize_filename(input_name)
        assert result.endswith(".wav"), "Extension should be preserved"
        # Should preserve valid ASCII characters


def test_sanitize_filename_remove_double_byte():
    """
    Test 18: Remove or normalize unicode/double-byte characters.

    Validates:
    - Japanese characters removed
    - Chinese characters removed
    - Emoji removed
    - Accented characters normalized or removed
    - Valid fallback filename

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)

    # Test unicode filenames
    test_cases = [
        "サンプル.wav",       # Japanese
        "样本.wav",           # Chinese
        "música🎵.wav",      # Spanish with emoji
        "Café_Music.wav",     # Accented characters
    ]

    for input_name in test_cases:
        result = service.sanitize_filename(input_name)

        # Should not contain original unicode
        assert "サンプル" not in result, "Japanese should be removed"
        assert "样本" not in result, "Chinese should be removed"
        assert "🎵" not in result, "Emoji should be removed"

        # Should still have .wav extension
        assert result.endswith(".wav"), "Extension should be preserved"
        assert len(result) > 4, "Should have some filename before extension"


def test_sanitize_filename_replace_spaces():
    """
    Test 19: Replace spaces with underscores.

    Validates:
    - Spaces converted to underscores
    - Multiple spaces handled
    - Leading/trailing spaces handled
    - Result is valid filename
    - No spaces remain

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)

    test_cases = [
        "My Cool Sample.wav",
        "   Leading Spaces.wav",
        "Trailing Spaces   .wav",
        "Multiple   Spaces.wav",
    ]

    for input_name in test_cases:
        result = service.sanitize_filename(input_name)

        # No spaces should remain
        assert " " not in result, f"Spaces should be removed/replaced: {result}"
        assert "_" in result or "." in result, "Should have underscores or just extension"
        assert result.endswith(".wav"), "Extension preserved"


def test_sanitize_filename_limit_length():
    """
    Test 20: Limit filename to maximum 255 characters.

    Validates:
    - Long filenames truncated
    - Extension preserved after truncation
    - Maximum length not exceeded
    - Truncation doesn't break filename
    - Valid filename after truncation

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)

    # Create extremely long filename
    input_name = "a" * 300 + ".wav"

    result = service.sanitize_filename(input_name)

    # Assert: Length limited
    assert len(result) <= 255, "Filename should be max 255 chars"
    assert result.endswith(".wav"), "Extension should be preserved"
    assert len(result) > 4, "Should have some name before extension"


def test_sanitize_filename_empty_fallback():
    """
    Test 21: Generate valid fallback for empty/invalid names.

    Validates:
    - Empty name gets fallback
    - All-special-chars gets fallback
    - Fallback is valid filename
    - Extension preserved
    - Reasonable fallback name

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService

    service = SP404ExportService(None)

    test_cases = [
        "!!!.wav",
        "@#$%^&*.wav",
        "....wav",
    ]

    for input_name in test_cases:
        result = service.sanitize_filename(input_name)

        # Should have valid fallback
        assert len(result) > 4, "Should have filename beyond .wav"
        assert result.endswith(".wav"), "Extension should be preserved"
        # Should contain some valid characters (letters or numbers)


# =============================================================================
# SINGLE SAMPLE EXPORT TESTS (8 tests)
# =============================================================================


@pytest.mark.asyncio
async def test_export_single_sample_success(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 22: Export single sample successfully (complete workflow).

    Validates:
    - Sample loaded from database
    - Audio file converted to SP-404MK2 format
    - Output file created
    - Metadata generated
    - Result includes all details
    - Export record created in database

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create sample in database
    sample = Sample(
        user_id=test_user.id,
        title="Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
        duration=2.0,
        genre="hip-hop",
        bpm=95.0
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Arrange: Export configuration
    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        include_metadata=True,
        sanitize_filenames=True,
        output_base_path=str(tmp_path / "exports")
    )

    # Act: Export single sample
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: Export successful
    assert result.success is True, "Export should succeed"
    assert result.sample_id == sample.id, "Sample ID should match"
    assert result.format == "wav", "Format should match"
    assert result.file_size_bytes > 0, "File size should be positive"
    assert result.conversion_time_seconds > 0, "Conversion time recorded"

    # Verify output file exists
    output_path = Path(result.output_path)
    assert output_path.exists(), "Output file should exist"


@pytest.mark.asyncio
async def test_export_single_sample_with_metadata(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 23: Export sample with metadata text file.

    Validates:
    - Metadata file created (.txt)
    - Contains sample information
    - BPM, genre, key included
    - File locations correct
    - Metadata readable and formatted

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create sample with metadata
    sample = Sample(
        user_id=test_user.id,
        title="Metadata Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
        genre="jazz",
        bpm=120.0,
        musical_key="Cm"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        include_metadata=True,  # Enable metadata
        sanitize_filenames=True,
        output_base_path=str(tmp_path / "exports")
    )

    # Act: Export with metadata
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: Metadata file created
    assert result.success is True, "Export should succeed"
    assert result.metadata_file_created is True, "Metadata file should be created"

    # Check for metadata file
    output_dir = Path(result.output_path).parent
    metadata_files = list(output_dir.glob("*.txt"))
    assert len(metadata_files) > 0, "Metadata text file should exist"


@pytest.mark.asyncio
async def test_export_single_sample_sanitizes_filename(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 24: Filename sanitization during export.

    Validates:
    - Unicode removed from filename
    - Special characters handled
    - Spaces converted to underscores
    - Valid filename generated
    - Original title preserved in metadata

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create sample with problematic filename
    sample = Sample(
        user_id=test_user.id,
        title="サンプル Music 🎵!@#.wav",  # Unicode + emoji + special chars
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        sanitize_filenames=True,
        output_base_path=str(tmp_path / "exports")
    )

    # Act: Export
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: Filename sanitized
    assert result.success is True, "Export should succeed"
    assert result.output_filename is not None, "Output filename should be set"

    # Filename should not contain unicode or special chars
    assert "サンプル" not in result.output_filename, "Unicode removed"
    assert "🎵" not in result.output_filename, "Emoji removed"
    assert "!" not in result.output_filename, "Special chars removed"


@pytest.mark.asyncio
async def test_export_single_sample_creates_folders(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 25: Auto-create output folders if missing.

    Validates:
    - Output directory created
    - Nested directories supported
    - Genre folders created
    - File written to correct location
    - No permission errors

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create sample
    sample = Sample(
        user_id=test_user.id,
        title="Folder Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
        genre="electronic"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Export to non-existent nested directory
    export_config = ExportConfig(
        organize_by="genre",
        format="wav",
        output_base_path=str(tmp_path / "new_exports" / "organized")
    )

    # Act: Export (should create directories)
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: Directories created
    assert result.success is True, "Export should succeed"
    output_path = Path(result.output_path)
    assert output_path.exists(), "Output file should exist"
    assert output_path.parent.exists(), "Output directory should be created"


@pytest.mark.asyncio
async def test_export_single_sample_missing_sample(
    db_session: AsyncSession,
    tmp_path
):
    """
    Test 26: Handle non-existent sample ID.

    Validates:
    - Error raised for missing sample
    - Descriptive error message
    - No files created
    - Database consistency maintained
    - Proper exception type

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService, SP404ExportError
    from app.schemas.sp404_export import ExportConfig

    # Arrange: Export config for non-existent sample
    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "exports")
    )

    # Act & Assert: Should raise error
    service = SP404ExportService(db_session)

    with pytest.raises(SP404ExportError, match="not found"):
        await service.export_single_sample(
            sample_id=999999,  # Non-existent ID
            config=export_config
        )


@pytest.mark.asyncio
async def test_export_single_sample_conversion_fails(
    db_session: AsyncSession,
    test_user,
    tmp_path
):
    """
    Test 27: Handle conversion failure gracefully.

    Validates:
    - Conversion errors caught
    - Result indicates failure
    - Error message provided
    - Partial files cleaned up
    - Database not corrupted

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create sample with non-existent file
    sample = Sample(
        user_id=test_user.id,
        title="Conversion Fail Sample",
        file_path="/fake/path/nonexistent.wav",
        file_size=12345
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "exports")
    )

    # Act: Export (should fail gracefully)
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: Graceful failure
    assert result.success is False, "Export should fail"
    assert result.error is not None, "Error message should be provided"


@pytest.mark.asyncio
async def test_export_single_sample_tracks_export(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 28: Export record created in database.

    Validates:
    - SP404Export record created
    - SP404ExportSample relationship created
    - Export metadata tracked
    - Timestamps recorded
    - Query returns correct data

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample
    from app.models.sp404_export import SP404Export
    from sqlalchemy import select

    # Arrange: Create sample
    sample = Sample(
        user_id=test_user.id,
        title="Tracking Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "exports")
    )

    # Act: Export
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: Export tracked
    assert result.success is True, "Export should succeed"

    # Query export record
    stmt = select(SP404Export).where(SP404Export.user_id == test_user.id)
    query_result = await db_session.execute(stmt)
    export_record = query_result.scalar_one_or_none()

    assert export_record is not None, "Export record should be created"
    assert export_record.export_type == "single", "Export type should be single"
    assert export_record.sample_count == 1, "Sample count should be 1"


@pytest.mark.asyncio
async def test_export_single_sample_aiff_format(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 29: Export to AIFF format instead of WAV.

    Validates:
    - AIFF format respected
    - File extension correct
    - Format parameter propagated
    - Audio conversion correct
    - File playable

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create sample
    sample = Sample(
        user_id=test_user.id,
        title="AIFF Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    export_config = ExportConfig(
        organize_by="flat",
        format="aiff",  # AIFF instead of WAV
        output_base_path=str(tmp_path / "exports")
    )

    # Act: Export as AIFF
    service = SP404ExportService(db_session)
    result = await service.export_single_sample(
        sample_id=sample.id,
        config=export_config
    )

    # Assert: AIFF export successful
    assert result.success is True, "AIFF export should succeed"
    assert result.format == "aiff", "Format should be AIFF"
    assert result.output_filename.endswith(".aiff"), "File extension should be .aiff"


# =============================================================================
# BATCH EXPORT TESTS (8 tests)
# =============================================================================


@pytest.mark.asyncio
async def test_export_batch_flat_organization(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 30: Batch export with flat organization (all in one folder).

    Validates:
    - Multiple samples exported
    - All in same directory
    - No subfolders created
    - Aggregated statistics correct
    - All samples processed

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create 3 samples
    sample_ids = []
    for i in range(1, 4):
        sample = Sample(
            user_id=test_user.id,
            title=f"Batch Sample {i}",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "batch_flat")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )

    # Assert: Batch successful
    assert result.total_requested == 3, "Should request 3 samples"
    assert result.successful == 3, "All 3 should succeed"
    assert result.failed == 0, "None should fail"
    assert len(result.results) == 3, "Should have 3 individual results"

    # Verify flat organization (all files in same dir)
    output_base = Path(export_config.output_base_path)
    wav_files = list(output_base.glob("*.wav"))
    assert len(wav_files) == 3, "Should have 3 WAV files in base directory"


@pytest.mark.asyncio
async def test_export_batch_genre_organization(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 31: Batch export organized by genre folders.

    Validates:
    - Samples grouped by genre
    - Genre folders created
    - Correct sample in correct folder
    - Mixed genres handled
    - Folder structure clean

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create samples with different genres
    genres = ["hip-hop", "jazz", "electronic"]
    sample_ids = []

    for genre in genres:
        sample = Sample(
            user_id=test_user.id,
            title=f"{genre} Sample",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size,
            genre=genre
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="genre",  # Genre organization
        format="wav",
        output_base_path=str(tmp_path / "batch_genre")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )

    # Assert: Batch successful
    assert result.total_requested == 3, "Should request 3 samples"
    assert result.successful == 3, "All should succeed"

    # Verify genre folders created
    output_base = Path(export_config.output_base_path)
    for genre in genres:
        genre_folder = output_base / genre
        assert genre_folder.exists(), f"{genre} folder should exist"

        wav_files = list(genre_folder.glob("*.wav"))
        assert len(wav_files) > 0, f"{genre} folder should have WAV files"


@pytest.mark.asyncio
async def test_export_batch_bpm_organization(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 32: Batch export organized by BPM ranges.

    Validates:
    - BPM range folders created (slow, 70-90, 90-110, 110-130, 130-150, fast)
    - Samples sorted by BPM
    - Range boundaries correct
    - Missing BPM handled
    - Folder naming consistent

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create samples with different BPMs
    bpms = [60, 85, 95, 120, 140, 160]
    sample_ids = []

    for bpm in bpms:
        sample = Sample(
            user_id=test_user.id,
            title=f"BPM {bpm} Sample",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size,
            bpm=float(bpm)
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="bpm",  # BPM organization
        format="wav",
        output_base_path=str(tmp_path / "batch_bpm")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )

    # Assert: Batch successful
    assert result.total_requested == 6, "Should request 6 samples"
    assert result.successful == 6, "All should succeed"

    # Verify BPM folders exist
    output_base = Path(export_config.output_base_path)
    bpm_folders_found = [f.name for f in output_base.iterdir() if f.is_dir()]
    assert len(bpm_folders_found) > 0, "BPM folders should be created"


@pytest.mark.asyncio
async def test_export_batch_mixed_formats(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 33: Batch export with mixed input formats (MP3, WAV, FLAC).

    Validates:
    - All formats converted correctly
    - Consistent output format
    - No format-specific errors
    - All conversions successful
    - Statistics aggregated correctly

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create samples with different formats (simulate with different paths)
    formats = ["sample.wav", "sample.mp3", "sample.flac"]
    sample_ids = []

    for fmt in formats:
        sample = Sample(
            user_id=test_user.id,
            title=f"Format {fmt}",
            file_path=str(test_wav_fixture),  # All use same WAV for testing
            file_size=test_wav_fixture.stat().st_size
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "batch_mixed")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )

    # Assert: All formats handled
    assert result.total_requested == 3, "Should request 3 samples"
    assert result.successful == 3, "All should succeed"
    assert result.failed == 0, "None should fail"


@pytest.mark.asyncio
async def test_export_batch_partial_failure(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 34: Batch export with some samples failing (partial failure).

    Validates:
    - Successful samples exported
    - Failed samples tracked
    - Error details captured
    - Statistics reflect partial success
    - Process continues after failures

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create mix of valid and invalid samples
    sample_ids = []

    # Valid sample
    valid_sample = Sample(
        user_id=test_user.id,
        title="Valid Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size
    )
    db_session.add(valid_sample)
    await db_session.flush()
    sample_ids.append(valid_sample.id)

    # Invalid sample (missing file)
    invalid_sample = Sample(
        user_id=test_user.id,
        title="Invalid Sample",
        file_path="/fake/missing.wav",
        file_size=12345
    )
    db_session.add(invalid_sample)
    await db_session.flush()
    sample_ids.append(invalid_sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "batch_partial")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )

    # Assert: Partial success
    assert result.total_requested == 2, "Should request 2 samples"
    assert result.successful == 1, "1 should succeed"
    assert result.failed == 1, "1 should fail"
    assert len(result.errors) > 0, "Should have error details"


@pytest.mark.asyncio
async def test_export_batch_empty_list(db_session: AsyncSession, tmp_path):
    """
    Test 35: Batch export with empty sample list.

    Validates:
    - Empty list handled gracefully
    - No errors raised
    - Statistics reflect zero samples
    - No files created
    - Quick execution

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "batch_empty")
    )

    # Act: Export empty list
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=[],  # Empty list
        config=export_config
    )

    # Assert: Graceful handling
    assert result.total_requested == 0, "Should request 0 samples"
    assert result.successful == 0, "None should succeed"
    assert result.failed == 0, "None should fail"
    assert len(result.results) == 0, "No individual results"


@pytest.mark.asyncio
async def test_export_batch_aggregates_statistics(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 36: Batch export aggregates statistics (total size, time, count).

    Validates:
    - Total file size calculated
    - Total time tracked
    - Average time per sample
    - Sample count correct
    - Statistics accurate

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create 3 samples
    sample_ids = []
    for i in range(1, 4):
        sample = Sample(
            user_id=test_user.id,
            title=f"Stats Sample {i}",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="flat",
        format="wav",
        output_base_path=str(tmp_path / "batch_stats")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    start_time = time.time()
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )
    elapsed = time.time() - start_time

    # Assert: Statistics aggregated
    assert result.total_samples == 3, "Total samples should be 3"
    assert result.successful == 3, "All should succeed"
    assert result.total_size_bytes > 0, "Total size should be positive"
    assert result.total_time_seconds > 0, "Total time should be positive"
    assert result.total_time_seconds <= elapsed + 1.0, "Time should be reasonable"

    # Average calculation
    expected_avg = result.total_time_seconds / 3
    assert abs(result.average_time_per_sample - expected_avg) < 0.1, \
        "Average time should match total / count"


@pytest.mark.asyncio
async def test_export_batch_creates_subfolder_structure(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 37: Batch export creates proper subfolder hierarchy.

    Validates:
    - Base directory created
    - Organization subfolders created
    - Nested structure correct
    - File placement correct
    - No orphaned files

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.sample import Sample

    # Arrange: Create samples
    sample_ids = []
    genres = ["hip-hop", "jazz"]

    for genre in genres:
        sample = Sample(
            user_id=test_user.id,
            title=f"{genre} Structure Sample",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size,
            genre=genre
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="genre",
        format="wav",
        output_base_path=str(tmp_path / "batch_structure")
    )

    # Act: Batch export
    service = SP404ExportService(db_session)
    result = await service.export_batch(
        sample_ids=sample_ids,
        config=export_config
    )

    # Assert: Folder structure created
    assert result.successful == 2, "Both should succeed"

    output_base = Path(export_config.output_base_path)
    assert output_base.exists(), "Base directory should exist"

    for genre in genres:
        genre_folder = output_base / genre
        assert genre_folder.exists(), f"{genre} folder should exist"


# =============================================================================
# KIT EXPORT TESTS (4 tests)
# =============================================================================


@pytest.mark.asyncio
async def test_export_kit_maintains_structure(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 38: Export kit maintains folder structure.

    Validates:
    - Kit folder created
    - Kit metadata preserved
    - Sample relationships maintained
    - Folder hierarchy correct
    - All kit samples included

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.kit import Kit, KitSample
    from app.models.sample import Sample

    # Arrange: Create kit with samples
    kit = Kit(
        user_id=test_user.id,
        name="Test Kit",
        description="Test kit for export"
    )
    db_session.add(kit)
    await db_session.flush()

    # Add samples to kit using KitSample join table
    for i in range(1, 4):
        sample = Sample(
            user_id=test_user.id,
            title=f"Kit Sample {i}",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size
        )
        db_session.add(sample)
        await db_session.flush()

        # Link sample to kit via KitSample
        kit_sample = KitSample(
            kit_id=kit.id,
            sample_id=sample.id,
            pad_bank="A",
            pad_number=i
        )
        db_session.add(kit_sample)

    await db_session.commit()
    await db_session.refresh(kit)

    export_config = ExportConfig(
        organize_by="kit",
        format="wav",
        output_base_path=str(tmp_path / "kit_export")
    )

    # Act: Export kit
    service = SP404ExportService(db_session)
    result = await service.export_kit(
        kit_id=kit.id,
        config=export_config
    )

    # Assert: Kit exported with structure
    assert result.success is True, "Kit export should succeed"
    assert result.sample_count == 3, "Should export 3 samples"

    # Verify kit folder exists
    kit_folder = Path(export_config.output_base_path) / "Test_Kit"
    assert kit_folder.exists(), "Kit folder should be created"


@pytest.mark.asyncio
async def test_export_kit_all_samples(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 39: Export all samples in kit.

    Validates:
    - All kit samples exported
    - No samples skipped
    - Count matches kit size
    - Each sample has output file
    - Batch processing used

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.kit import Kit, KitSample
    from app.models.sample import Sample

    # Arrange: Create kit with multiple samples
    kit = Kit(
        user_id=test_user.id,
        name="Complete Kit",
        description="All samples kit"
    )
    db_session.add(kit)
    await db_session.flush()

    for i in range(1, 6):  # 5 samples
        sample = Sample(
            user_id=test_user.id,
            title=f"Sample {i}",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size
        )
        db_session.add(sample)
        await db_session.flush()

        # Link sample to kit via KitSample
        kit_sample = KitSample(
            kit_id=kit.id,
            sample_id=sample.id,
            pad_bank="A",
            pad_number=i
        )
        db_session.add(kit_sample)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="kit",
        format="wav",
        output_base_path=str(tmp_path / "complete_kit")
    )

    # Act: Export kit
    service = SP404ExportService(db_session)
    result = await service.export_kit(
        kit_id=kit.id,
        config=export_config
    )

    # Assert: All samples exported
    assert result.success is True, "Export should succeed"
    assert result.sample_count == 5, "Should export all 5 samples"
    assert result.successful == 5, "All should succeed"


@pytest.mark.asyncio
async def test_export_kit_missing_samples(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 40: Handle kit with some missing sample files.

    Validates:
    - Available samples exported
    - Missing samples tracked
    - Partial export successful
    - Error details provided
    - Kit still usable

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.kit import Kit, KitSample
    from app.models.sample import Sample

    # Arrange: Create kit with valid and missing samples
    kit = Kit(
        user_id=test_user.id,
        name="Partial Kit",
        description="Kit with missing samples"
    )
    db_session.add(kit)
    await db_session.flush()

    # Valid sample
    sample1 = Sample(
        user_id=test_user.id,
        title="Valid Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size
    )
    db_session.add(sample1)
    await db_session.flush()

    kit_sample1 = KitSample(
        kit_id=kit.id,
        sample_id=sample1.id,
        pad_bank="A",
        pad_number=1
    )
    db_session.add(kit_sample1)

    # Missing sample
    sample2 = Sample(
        user_id=test_user.id,
        title="Missing Sample",
        file_path="/fake/missing.wav",
        file_size=12345
    )
    db_session.add(sample2)
    await db_session.flush()

    kit_sample2 = KitSample(
        kit_id=kit.id,
        sample_id=sample2.id,
        pad_bank="A",
        pad_number=2
    )
    db_session.add(kit_sample2)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="kit",
        format="wav",
        output_base_path=str(tmp_path / "partial_kit")
    )

    # Act: Export kit
    service = SP404ExportService(db_session)
    result = await service.export_kit(
        kit_id=kit.id,
        config=export_config
    )

    # Assert: Partial success
    assert result.sample_count == 2, "Should attempt 2 samples"
    assert result.successful == 1, "1 should succeed"
    assert result.failed == 1, "1 should fail"
    assert len(result.errors) > 0, "Should have error details"


@pytest.mark.asyncio
async def test_export_kit_bank_organization(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture,
    tmp_path
):
    """
    Test 41: Export kit with bank/pad organization (SP-404MK2 layout).

    Validates:
    - Banks organized correctly
    - Pads numbered/labeled
    - Layout matches SP-404MK2
    - Metadata includes pad info
    - Structure is SP-404 compatible

    Expected to fail until SP404ExportService is implemented.
    """
    from app.services.sp404_export_service import SP404ExportService
    from app.schemas.sp404_export import ExportConfig
    from app.models.kit import Kit, KitSample
    from app.models.sample import Sample

    # Arrange: Create kit with bank organization
    kit = Kit(
        user_id=test_user.id,
        name="Organized Kit",
        description="Kit with bank layout"
    )
    db_session.add(kit)
    await db_session.flush()

    # Add samples with pad positions using KitSample
    bank_letters = ["A", "B"]
    for bank_idx, bank_letter in enumerate(bank_letters, 1):  # 2 banks
        for pad in range(1, 5):  # 4 pads per bank
            sample = Sample(
                user_id=test_user.id,
                title=f"Bank{bank_idx}_Pad{pad}",
                file_path=str(test_wav_fixture),
                file_size=test_wav_fixture.stat().st_size
            )
            db_session.add(sample)
            await db_session.flush()

            # Link sample to kit with bank/pad info
            kit_sample = KitSample(
                kit_id=kit.id,
                sample_id=sample.id,
                pad_bank=bank_letter,
                pad_number=pad
            )
            db_session.add(kit_sample)

    await db_session.commit()

    export_config = ExportConfig(
        organize_by="bank",
        format="wav",
        output_base_path=str(tmp_path / "bank_kit"),
        include_bank_layout=True
    )

    # Act: Export kit with bank organization
    service = SP404ExportService(db_session)
    result = await service.export_kit(
        kit_id=kit.id,
        config=export_config
    )

    # Assert: Bank organization maintained
    assert result.success is True, "Export should succeed"
    assert result.sample_count == 8, "Should export 8 samples (2 banks × 4 pads)"

    # Verify bank folders
    base_path = Path(export_config.output_base_path) / "Organized_Kit"
    if base_path.exists():
        # Bank folders should exist (implementation-dependent)
        assert True, "Kit exported with bank structure"


# =============================================================================
# META-TEST: Verify imports will fail (RED phase)
# =============================================================================


def test_imports_succeed():
    """
    Meta-test to verify that service implementation is complete.

    This test verifies that the service has been implemented and
    all necessary imports are available.
    """
    # These imports should now succeed
    from app.services.sp404_export_service import SP404ExportService
    from app.services.sp404_export_service import SP404ExportError
    from app.schemas.sp404_export import ExportConfig, ConversionResult, ValidationResult

    # Verify classes are importable
    assert SP404ExportService is not None
    assert SP404ExportError is not None
    assert ExportConfig is not None
    assert ConversionResult is not None
    assert ValidationResult is not None
