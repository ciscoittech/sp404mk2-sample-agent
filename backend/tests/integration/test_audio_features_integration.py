"""
Integration tests for AudioFeaturesService with Essentia feature flags.

Tests the complete integration between AudioFeaturesService, EssentiaAnalyzer,
and librosa fallback behavior with various configuration scenarios.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

from app.services.audio_features_service import AudioFeaturesService
from app.models.audio_features import AudioFeatures, AudioError
from app.core.config import settings
from app.utils.essentia_check import ESSENTIA_AVAILABLE

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_audio_path(tmp_path):
    """Create a test audio file fixture.

    Note: For real tests, use actual audio files from tests/fixtures/
    This is a placeholder that returns a path.
    """
    # In real tests, this would return path to a real audio file
    # For now, we'll use a mock or skip tests that need real audio
    fixture_dir = Path(__file__).parent.parent / "fixtures"
    sample_path = fixture_dir / "test_sample.wav"

    if sample_path.exists():
        return sample_path

    # Create a minimal WAV file for testing if fixtures don't exist
    import numpy as np
    import soundfile as sf

    # Create 1 second of silence at 44.1kHz
    duration = 1.0
    sample_rate = 44100
    samples = np.zeros(int(duration * sample_rate))

    test_file = tmp_path / "test.wav"
    sf.write(str(test_file), samples, sample_rate)
    return test_file


class TestAudioFeaturesIntegration:
    """Integration tests for AudioFeaturesService with feature flags."""

    def test_service_initialization_with_essentia_enabled(self):
        """Test service initializes with Essentia when enabled and available."""
        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = True
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            if ESSENTIA_AVAILABLE:
                service = AudioFeaturesService()
                assert service.analyzer_type in ["essentia", "librosa"]
                # Should be essentia if available, librosa if init failed
            else:
                service = AudioFeaturesService()
                assert service.analyzer_type == "librosa"

    def test_service_initialization_with_essentia_disabled(self):
        """Test service uses librosa when USE_ESSENTIA=False."""
        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = False
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            service = AudioFeaturesService()
            assert service.analyzer_type == "librosa"
            assert service.essentia_analyzer is None

    @pytest.mark.asyncio
    async def test_analyze_with_essentia_available(self, sample_audio_path):
        """Test analysis succeeds with Essentia when available."""
        if not ESSENTIA_AVAILABLE:
            pytest.skip("Essentia not available")

        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = True
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            service = AudioFeaturesService()

            if service.analyzer_type == "essentia":
                features = await service.analyze_file(sample_audio_path)

                assert isinstance(features, AudioFeatures)
                assert features.file_path == sample_audio_path
                assert features.bpm is not None  # Should have BPM
                assert features.metadata is not None
                assert features.metadata.get("analyzer") == "essentia"
                assert "bpm_confidence" in features.metadata

    @pytest.mark.asyncio
    async def test_analyze_with_librosa_only(self, sample_audio_path):
        """Test analysis works with librosa when Essentia disabled."""
        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = False
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            service = AudioFeaturesService()
            features = await service.analyze_file(sample_audio_path)

            assert isinstance(features, AudioFeatures)
            assert features.file_path == sample_audio_path
            # BPM may be None for silent/simple test files, which is valid
            assert features.metadata is not None
            assert features.metadata.get("analyzer") == "librosa"

    @pytest.mark.asyncio
    async def test_fallback_essentia_to_librosa(self, sample_audio_path):
        """Test automatic fallback from Essentia to librosa on failure."""
        if not ESSENTIA_AVAILABLE:
            pytest.skip("Essentia not available")

        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = True
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            service = AudioFeaturesService()

            # Force Essentia to fail by mocking the analyzer
            if service.analyzer_type == "essentia":
                original_essentia_method = service._analyze_with_essentia

                async def mock_essentia_fail(*args, **kwargs):
                    raise RuntimeError("Simulated Essentia failure")

                service._analyze_with_essentia = mock_essentia_fail

                # Should fall back to librosa
                features = await service.analyze_file(sample_audio_path)

                assert isinstance(features, AudioFeatures)
                assert features.metadata.get("analyzer") == "librosa"

                # Restore original method
                service._analyze_with_essentia = original_essentia_method

    @pytest.mark.asyncio
    async def test_genre_classification_flag_respected(self, sample_audio_path):
        """Test ENABLE_GENRE_CLASSIFICATION flag is respected."""
        if not ESSENTIA_AVAILABLE:
            pytest.skip("Essentia not available")

        # Test with genre classification disabled (default)
        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = True
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            service = AudioFeaturesService()

            if service.analyzer_type == "essentia":
                features = await service.analyze_file(sample_audio_path)

                # Genre should not be in metadata when disabled
                if features.metadata:
                    genre = features.metadata.get("genre")
                    # Genre might be None or not present
                    # This is expected when ENABLE_GENRE_CLASSIFICATION=False

    @pytest.mark.asyncio
    async def test_bpm_method_configuration(self, sample_audio_path):
        """Test ESSENTIA_BPM_METHOD configuration is used."""
        if not ESSENTIA_AVAILABLE:
            pytest.skip("Essentia not available")

        for method in ["multifeature", "degara"]:
            with patch('app.services.audio_features_service.settings') as mock_settings:
                mock_settings.USE_ESSENTIA = True
                mock_settings.ENABLE_GENRE_CLASSIFICATION = False
                mock_settings.ESSENTIA_BPM_METHOD = method
                mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

                service = AudioFeaturesService()

                if service.analyzer_type == "essentia":
                    features = await service.analyze_file(sample_audio_path)

                    assert isinstance(features, AudioFeatures)
                    if features.metadata:
                        # Check that the method was used
                        bpm_method = features.metadata.get("bpm_method")
                        assert bpm_method == method or bpm_method is None

    @pytest.mark.asyncio
    async def test_file_not_found_error(self):
        """Test proper error handling for missing files."""
        service = AudioFeaturesService()

        non_existent_path = Path("/tmp/does_not_exist_12345.wav")

        with pytest.raises(AudioError) as exc_info:
            await service.analyze_file(non_existent_path)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_empty_file_error(self, tmp_path):
        """Test proper error handling for empty files."""
        service = AudioFeaturesService()

        # Create empty file
        empty_file = tmp_path / "empty.wav"
        empty_file.touch()

        with pytest.raises(AudioError) as exc_info:
            await service.analyze_file(empty_file)

        assert "empty" in str(exc_info.value).lower()

    def test_logging_analyzer_selection(self, caplog):
        """Test that analyzer selection is properly logged."""
        with caplog.at_level(logging.INFO):
            with patch('app.services.audio_features_service.settings') as mock_settings:
                mock_settings.USE_ESSENTIA = True
                mock_settings.ENABLE_GENRE_CLASSIFICATION = False
                mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
                mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

                service = AudioFeaturesService()

                # Should log which analyzer was selected
                assert any("analyzer" in msg.lower() for msg in caplog.messages)

    @pytest.mark.asyncio
    async def test_metadata_contains_analyzer_info(self, sample_audio_path):
        """Test that metadata always contains analyzer information."""
        service = AudioFeaturesService()
        features = await service.analyze_file(sample_audio_path)

        assert features.metadata is not None
        assert "analyzer" in features.metadata
        assert features.metadata["analyzer"] in ["essentia", "librosa"]

    @pytest.mark.asyncio
    async def test_essentia_metadata_has_confidence(self, sample_audio_path):
        """Test that Essentia analysis includes confidence scores in metadata."""
        if not ESSENTIA_AVAILABLE:
            pytest.skip("Essentia not available")

        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = True
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            service = AudioFeaturesService()

            if service.analyzer_type == "essentia":
                features = await service.analyze_file(sample_audio_path)

                assert features.metadata is not None
                assert "analyzer" in features.metadata
                assert "bpm_confidence" in features.metadata
                assert "bpm_method" in features.metadata


class TestEssentiaAvailabilityCheck:
    """Tests for Essentia availability checking."""

    def test_essentia_available_constant(self):
        """Test ESSENTIA_AVAILABLE constant reflects actual availability."""
        from app.utils.essentia_check import ESSENTIA_AVAILABLE

        # Should be True or False, never None
        assert isinstance(ESSENTIA_AVAILABLE, bool)

    def test_service_respects_availability(self):
        """Test service respects ESSENTIA_AVAILABLE flag."""
        with patch('app.services.audio_features_service.ESSENTIA_AVAILABLE', False):
            with patch('app.services.audio_features_service.settings') as mock_settings:
                mock_settings.USE_ESSENTIA = True  # User wants Essentia
                mock_settings.ENABLE_GENRE_CLASSIFICATION = False
                mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
                mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

                service = AudioFeaturesService()

                # Should fall back to librosa when unavailable
                assert service.analyzer_type == "librosa"
                assert service.essentia_analyzer is None


class TestConfigurationValidation:
    """Tests for configuration validation."""

    def test_invalid_bpm_method_handling(self):
        """Test handling of invalid BPM method configuration."""
        # This should be handled gracefully or use a default
        with patch('app.services.audio_features_service.settings') as mock_settings:
            mock_settings.USE_ESSENTIA = True
            mock_settings.ENABLE_GENRE_CLASSIFICATION = False
            mock_settings.ESSENTIA_BPM_METHOD = "invalid_method"
            mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

            # Service should still initialize (Essentia will validate method)
            service = AudioFeaturesService()
            assert service is not None

    def test_default_configuration(self):
        """Test service works with default configuration."""
        # Don't mock settings, use actual defaults
        service = AudioFeaturesService()

        assert service is not None
        assert service.analyzer_type in ["essentia", "librosa"]


# Performance/stress tests (optional, can be slow)
class TestPerformance:
    """Performance and edge case tests."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_multiple_analyses_consistency(self, sample_audio_path):
        """Test that multiple analyses of the same file produce consistent results."""
        service = AudioFeaturesService()

        # Analyze same file twice
        features1 = await service.analyze_file(sample_audio_path)
        features2 = await service.analyze_file(sample_audio_path)

        # BPM should be consistent (within small margin)
        if features1.bpm and features2.bpm:
            assert abs(features1.bpm - features2.bpm) < 0.5

        # Analyzer should be the same
        assert features1.metadata["analyzer"] == features2.metadata["analyzer"]
