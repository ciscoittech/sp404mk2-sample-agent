"""
Test suite for Audio Features Service (TDD RED phase).

These tests are designed to FAIL initially as the service doesn't exist yet.
Following TDD methodology: Write failing tests first, then implement code to make them pass.

Test Strategy:
- REAL_INTEGRATION_TEST: No mocked audio analysis, uses real librosa
- Real database integration with SQLAlchemy async
- Real WAV file fixtures (programmatically generated)
"""
import pytest
import pytest_asyncio
from pathlib import Path
from sqlalchemy import select

from app.services.audio_features_service import AudioFeaturesService
from app.models.audio_features import AudioFeatures, AudioError
from app.models.sample import Sample


@pytest.mark.asyncio
async def test_analyze_real_wav_file(audio_service, test_wav_fixture):
    """
    REAL_INTEGRATION_TEST

    Test real audio analysis with librosa on a generated WAV file.

    This test validates:
    - Service can load and analyze real audio files
    - Librosa integration works correctly
    - Returns AudioFeatures with reasonable values
    - At least 50% of features are successfully extracted (not None)

    Expected behavior:
    - BPM should be between 40-200 or None (if detection fails)
    - Key should be valid note (C, C#, D, etc.) or None
    - Spectral features should be > 0 or None
    - Duration should match fixture (approx 2 seconds)

    This test WILL FAIL until AudioFeaturesService is implemented.
    """
    # Arrange: Real WAV file exists at test_wav_fixture path
    assert test_wav_fixture.exists(), "Test WAV fixture must exist"
    assert test_wav_fixture.suffix == ".wav", "Fixture must be WAV file"

    # Act: Analyze the real audio file
    features = await audio_service.analyze_file(test_wav_fixture)

    # Assert: Returns AudioFeatures with reasonable values
    assert isinstance(features, AudioFeatures), "Should return AudioFeatures instance"
    assert features.file_path == test_wav_fixture, "File path should match input"

    # Duration validation
    assert features.duration_seconds is not None, "Duration must be extracted"
    assert 1.5 <= features.duration_seconds <= 2.5, "Duration should be ~2 seconds"

    # BPM validation (if detected)
    if features.bpm is not None:
        assert 40 <= features.bpm <= 200, f"BPM {features.bpm} outside reasonable range"

    # Key validation (if detected)
    valid_keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if features.key is not None:
        assert features.key in valid_keys, f"Key {features.key} not a valid note"

    # Spectral features validation (if detected)
    if features.spectral_centroid is not None:
        assert features.spectral_centroid > 0, "Spectral centroid must be positive"

    if features.spectral_rolloff is not None:
        assert features.spectral_rolloff > 0, "Spectral rolloff must be positive"

    if features.zero_crossing_rate is not None:
        assert features.zero_crossing_rate >= 0, "Zero crossing rate must be non-negative"

    # Feature completeness: At least 50% of features should be non-None
    all_features = [
        features.bpm,
        features.key,
        features.spectral_centroid,
        features.spectral_rolloff,
        features.zero_crossing_rate,
        features.duration_seconds
    ]
    non_none_count = sum(1 for f in all_features if f is not None)
    completeness_ratio = non_none_count / len(all_features)

    assert completeness_ratio >= 0.5, (
        f"At least 50% of features should be extracted, got {completeness_ratio:.1%}"
    )


@pytest.mark.asyncio
async def test_invalid_file_raises_audio_error(audio_service, tmp_path):
    """
    Test that invalid files raise AudioError with proper attributes.

    This test validates:
    - Non-existent files raise AudioError
    - Corrupted files raise AudioError
    - AudioError includes message, file_path, and original_error
    - Error messages are descriptive

    No mocking - uses real Path objects and file operations.
    """
    # Test 1: Non-existent file
    non_existent = tmp_path / "does_not_exist.wav"

    with pytest.raises(AudioError) as exc_info:
        await audio_service.analyze_file(non_existent)

    error = exc_info.value
    assert error.file_path == non_existent, "Error should include file path"
    assert error.message, "Error should have descriptive message"
    assert "not found" in error.message.lower() or "does not exist" in error.message.lower(), \
        "Error message should indicate file not found"

    # Test 2: Corrupted file (invalid WAV data)
    corrupted_file = tmp_path / "corrupted.wav"
    corrupted_file.write_bytes(b"Not a valid WAV file, just random bytes")

    with pytest.raises(AudioError) as exc_info:
        await audio_service.analyze_file(corrupted_file)

    error = exc_info.value
    assert error.file_path == corrupted_file, "Error should include file path"
    assert error.message, "Error should have descriptive message"
    assert error.original_error is not None, "Error should wrap original exception"

    # Test 3: Empty file
    empty_file = tmp_path / "empty.wav"
    empty_file.write_bytes(b"")

    with pytest.raises(AudioError) as exc_info:
        await audio_service.analyze_file(empty_file)

    error = exc_info.value
    assert error.file_path == empty_file, "Error should include file path"
    assert error.message, "Error should have descriptive message"


@pytest.mark.asyncio
async def test_save_features_to_database(audio_service, db_session, test_wav_fixture, test_user):
    """
    REAL_INTEGRATION_TEST

    Test audio features round-trip through database with real SQLAlchemy.

    This test validates:
    - Features can be serialized to JSON for database storage
    - Sample.extra_metadata JSONB field stores features correctly
    - Features can be deserialized after database retrieval
    - All feature values are preserved through serialization

    Uses real async SQLAlchemy session (not mocked) and real Sample model.
    """
    # Arrange: Analyze real WAV file
    features = await audio_service.analyze_file(test_wav_fixture)
    assert isinstance(features, AudioFeatures), "Analysis should succeed"

    # Create a Sample record with features in extra_metadata
    sample = Sample(
        user_id=test_user.id,
        title="Test Audio Features Sample",
        file_path=str(test_wav_fixture),
        extra_metadata={
            "audio_features": features.to_dict()  # Serialize to dict for JSON
        }
    )

    # Act: Save to database and commit
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    sample_id = sample.id

    # Clear session to ensure fresh query
    await db_session.close()

    # Query back from database
    result = await db_session.execute(
        select(Sample).where(Sample.id == sample_id)
    )
    retrieved_sample = result.scalar_one()

    # Assert: Retrieved features match original
    assert retrieved_sample is not None, "Sample should be retrieved from database"
    assert "audio_features" in retrieved_sample.extra_metadata, \
        "extra_metadata should contain audio_features"

    # Deserialize features from database
    features_dict = retrieved_sample.extra_metadata["audio_features"]
    retrieved_features = AudioFeatures.from_dict(features_dict)

    # Verify all feature values preserved
    assert retrieved_features.file_path == features.file_path, "File path should match"
    assert retrieved_features.duration_seconds == features.duration_seconds, \
        "Duration should match"
    assert retrieved_features.bpm == features.bpm, "BPM should match"
    assert retrieved_features.key == features.key, "Key should match"
    assert retrieved_features.spectral_centroid == features.spectral_centroid, \
        "Spectral centroid should match"
    assert retrieved_features.spectral_rolloff == features.spectral_rolloff, \
        "Spectral rolloff should match"
    assert retrieved_features.zero_crossing_rate == features.zero_crossing_rate, \
        "Zero crossing rate should match"

    # Verify JSONB serialization worked correctly
    assert isinstance(retrieved_sample.extra_metadata, dict), \
        "extra_metadata should be deserialized as dict"
    assert isinstance(features_dict, dict), "Features should serialize to dict"
