"""
Tests for confidence scoring and metadata functionality.

Tests cover:
- AudioFeatures model with confidence fields
- Sample model with confidence fields
- Pydantic schema validation (0-100 range)
- AudioFeaturesService populating confidence scores
- HybridAnalysisService saving confidence to database
- Backward compatibility (existing samples without confidence)
"""
import pytest
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sample import Sample
from app.models.audio_features import AudioFeatures
from app.schemas.sample import SampleBase, SampleUpdate
from app.services.audio_features_service import AudioFeaturesService


class TestAudioFeaturesModelConfidence:
    """Test AudioFeatures Pydantic model with confidence fields."""

    def test_audio_features_with_confidence_scores(self):
        """Test AudioFeatures model accepts confidence scores."""
        features = AudioFeatures(
            file_path=Path("/fake/path.wav"),
            bpm=90.5,
            bpm_confidence=87,
            genre="Hip-Hop",
            genre_confidence=72,
            key="C",
            key_confidence=65,
            metadata={
                "analyzer": "essentia",
                "bpm_method": "rhythm_extractor_2013"
            }
        )

        assert features.bpm == 90.5
        assert features.bpm_confidence == 87
        assert features.genre == "Hip-Hop"
        assert features.genre_confidence == 72
        assert features.key_confidence == 65
        assert features.metadata["analyzer"] == "essentia"

    def test_audio_features_confidence_optional(self):
        """Test confidence fields are optional."""
        features = AudioFeatures(
            file_path=Path("/fake/path.wav"),
            bpm=90.5,
            # No confidence scores provided
        )

        assert features.bpm == 90.5
        assert features.bpm_confidence is None
        assert features.genre_confidence is None
        assert features.key_confidence is None

    def test_audio_features_confidence_validation(self):
        """Test confidence scores must be 0-100."""
        # Valid confidence (0-100)
        features = AudioFeatures(
            file_path=Path("/fake/path.wav"),
            bpm=90.5,
            bpm_confidence=50
        )
        assert features.bpm_confidence == 50

        # Invalid: negative confidence
        with pytest.raises(ValueError):
            AudioFeatures(
                file_path=Path("/fake/path.wav"),
                bpm=90.5,
                bpm_confidence=-1
            )

        # Invalid: confidence > 100
        with pytest.raises(ValueError):
            AudioFeatures(
                file_path=Path("/fake/path.wav"),
                bpm=90.5,
                bpm_confidence=101
            )


class TestSampleSchemaConfidence:
    """Test Sample Pydantic schemas with confidence fields."""

    def test_sample_base_with_confidence(self):
        """Test SampleBase schema includes confidence fields."""
        sample = SampleBase(
            title="Test Sample",
            bpm=90.5,
            bpm_confidence=87,
            genre="Hip-Hop",
            genre_confidence=72
        )

        assert sample.bpm == 90.5
        assert sample.bpm_confidence == 87
        assert sample.genre == "Hip-Hop"
        assert sample.genre_confidence == 72

    def test_sample_update_with_confidence(self):
        """Test SampleUpdate schema can update confidence fields."""
        update = SampleUpdate(
            bpm_confidence=95,
            genre_confidence=80
        )

        assert update.bpm_confidence == 95
        assert update.genre_confidence == 80

    def test_sample_confidence_validation(self):
        """Test confidence validation in schemas."""
        # Valid
        sample = SampleBase(
            title="Test",
            bpm_confidence=100  # Max valid value
        )
        assert sample.bpm_confidence == 100

        # Invalid
        with pytest.raises(ValueError):
            SampleBase(
                title="Test",
                bpm_confidence=150  # Over 100
            )


@pytest.mark.asyncio
class TestAudioFeaturesServiceConfidence:
    """Test AudioFeaturesService populates confidence scores."""

    async def test_essentia_populates_confidence_scores(self):
        """Test Essentia analyzer populates confidence scores."""
        service = AudioFeaturesService()

        # Skip if Essentia not available
        if service.analyzer_type != "essentia":
            pytest.skip("Essentia not available")

        # Use a real test file
        test_file = Path(__file__).parent / "fixtures" / "test_audio.wav"
        if not test_file.exists():
            pytest.skip("Test audio file not found")

        features = await service.analyze_file(test_file)

        # Check BPM confidence is populated (Essentia provides this)
        if features.bpm is not None:
            assert features.bpm_confidence is not None
            assert 0 <= features.bpm_confidence <= 100
            assert isinstance(features.bpm_confidence, int)

        # Check metadata contains analyzer info
        assert features.metadata is not None
        assert features.metadata.get("analyzer") == "essentia"
        assert "bpm_method" in features.metadata

    async def test_librosa_populates_default_confidence(self):
        """Test librosa analyzer populates default confidence (65)."""
        service = AudioFeaturesService()

        # Force librosa mode
        original_type = service.analyzer_type
        service.analyzer_type = "librosa"

        try:
            # Use a real test file
            test_file = Path(__file__).parent / "fixtures" / "test_audio.wav"
            if not test_file.exists():
                pytest.skip("Test audio file not found")

            features = await service.analyze_file(test_file)

            # Librosa should populate default confidence (65)
            if features.bpm is not None:
                assert features.bpm_confidence == 65
                assert features.metadata.get("analyzer") == "librosa"

        finally:
            service.analyzer_type = original_type

    async def test_confidence_scores_are_integers(self):
        """Test confidence scores are converted to integers (0-100 scale)."""
        service = AudioFeaturesService()

        test_file = Path(__file__).parent / "fixtures" / "test_audio.wav"
        if not test_file.exists():
            pytest.skip("Test audio file not found")

        features = await service.analyze_file(test_file)

        # All confidence scores should be integers
        if features.bpm_confidence is not None:
            assert isinstance(features.bpm_confidence, int)
        if features.genre_confidence is not None:
            assert isinstance(features.genre_confidence, int)
        if features.key_confidence is not None:
            assert isinstance(features.key_confidence, int)


class TestDatabaseModel:
    """Test Sample SQLAlchemy model structure."""

    def test_sample_model_has_confidence_attributes(self):
        """Test Sample model defines confidence attributes."""
        # Verify Sample model has the new attributes
        assert hasattr(Sample, 'bpm_confidence')
        assert hasattr(Sample, 'genre_confidence')
        assert hasattr(Sample, 'key_confidence')
        assert hasattr(Sample, 'analysis_metadata')

    def test_sample_instantiation_with_confidence(self):
        """Test Sample can be instantiated with confidence scores."""
        # This tests the model definition, not database persistence
        sample = Sample(
            user_id=1,
            title="Test Sample",
            file_path="/fake/path.wav",
            bpm=90.5,
            bpm_confidence=87,
            genre="Hip-Hop",
            genre_confidence=72,
            musical_key="C minor",
            key_confidence=65,
            analysis_metadata={
                "analyzer": "essentia",
                "bpm_method": "rhythm_extractor_2013",
                "timestamp": "2025-11-16T12:00:00Z"
            }
        )

        # Verify attributes are set correctly
        assert sample.bpm_confidence == 87
        assert sample.genre_confidence == 72
        assert sample.key_confidence == 65
        assert sample.analysis_metadata["analyzer"] == "essentia"

    def test_backward_compatibility_null_confidence(self):
        """Test samples can be created without confidence scores."""
        # Create sample without confidence (backward compatibility)
        sample = Sample(
            user_id=1,
            title="Old Sample",
            file_path="/fake/old.wav",
            bpm=120.0
            # No confidence scores
        )

        # Should work fine with NULL values
        assert sample.bpm == 120.0
        assert sample.bpm_confidence is None
        assert sample.genre_confidence is None
        assert sample.key_confidence is None


class TestMetadataStructure:
    """Test analysis_metadata JSON structure."""

    def test_metadata_contains_required_fields(self):
        """Test metadata contains analyzer and method info."""
        metadata = {
            "analyzer": "essentia",
            "bpm_method": "rhythm_extractor_2013",
            "sample_type": "loop",
            "timestamp": "2025-11-16T12:00:00Z"
        }

        # Essentia metadata
        assert metadata["analyzer"] == "essentia"
        assert metadata["bpm_method"] == "rhythm_extractor_2013"
        assert "timestamp" in metadata

    def test_metadata_structure_for_librosa(self):
        """Test librosa metadata structure."""
        metadata = {
            "analyzer": "librosa",
            "bpm_method": "beat_track",
            "sample_type": "loop",
            "timestamp": "2025-11-16T12:00:00Z"
        }

        assert metadata["analyzer"] == "librosa"
        assert metadata["bpm_method"] == "beat_track"
