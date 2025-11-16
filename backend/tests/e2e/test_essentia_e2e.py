"""
End-to-end integration tests for Essentia analysis workflow.

Tests complete workflows: upload → analyze → store → retrieve
Tests with real audio files, concurrent analyses, and error scenarios.
"""
import pytest
import asyncio
from pathlib import Path
from typing import Dict
import numpy as np
import soundfile as sf

from app.utils.essentia_check import ESSENTIA_AVAILABLE
from app.services.audio_features_service import AudioFeaturesService
from app.models.audio_features import AudioFeatures, AudioError


@pytest.fixture
def real_audio_samples(tmp_path) -> Dict[str, Path]:
    """Create realistic audio samples for E2E testing."""
    samples = {}
    sample_rate = 44100

    # 1. Hip-hop beat (90 BPM)
    duration = 4.0
    t = np.linspace(0, duration, int(duration * sample_rate))
    kick = np.zeros_like(t)
    for i in range(4):  # 4 beats
        beat_time = i * (60/90)
        envelope = np.exp(-(t - beat_time) * 15) * (t >= beat_time)
        kick += 0.8 * np.sin(2 * np.pi * 60 * t) * envelope

    snare = np.zeros_like(t)
    for i in [1, 3]:  # Snare on 2 and 4
        beat_time = i * (60/90)
        envelope = np.exp(-(t - beat_time) * 25) * (t >= beat_time)
        snare += 0.6 * np.random.randn(len(t)) * envelope

    hiphop = kick + snare
    hiphop_path = tmp_path / "hiphop_90bpm.wav"
    sf.write(str(hiphop_path), hiphop, sample_rate)
    samples["hiphop"] = hiphop_path

    # 2. House track (125 BPM)
    duration = 8.0
    t = np.linspace(0, duration, int(duration * sample_rate))
    house = np.zeros_like(t)

    # Four-on-floor kick
    for i in range(int(duration * 125/60)):
        beat_time = i * (60/125)
        envelope = np.exp(-(t - beat_time) * 12) * (t >= beat_time)
        house += 0.7 * np.sin(2 * np.pi * 50 * t) * envelope

    # Hi-hats on sixteenths
    for i in range(int(duration * 125/60 * 4)):
        beat_time = i * (60/125/4)
        envelope = np.exp(-(t - beat_time) * 30) * (t >= beat_time)
        house += 0.3 * np.random.randn(len(t)) * envelope

    house_path = tmp_path / "house_125bpm.wav"
    sf.write(str(house_path), house, sample_rate)
    samples["house"] = house_path

    # 3. One-shot kick (for edge case testing)
    duration = 0.5
    t = np.linspace(0, duration, int(duration * sample_rate))
    oneshot = 0.9 * np.sin(2 * np.pi * 60 * t) * np.exp(-t * 10)

    oneshot_path = tmp_path / "oneshot_kick.wav"
    sf.write(str(oneshot_path), oneshot, sample_rate)
    samples["oneshot"] = oneshot_path

    return samples


class TestCompleteWorkflow:
    """Test complete end-to-end analysis workflows."""

    @pytest.mark.asyncio
    async def test_upload_analyze_workflow(self, real_audio_samples):
        """Test: Upload file → Analyze → Get features."""
        service = AudioFeaturesService()
        audio_path = real_audio_samples["hiphop"]

        # Step 1: Verify file exists
        assert audio_path.exists()

        # Step 2: Analyze
        features = await service.analyze_file(audio_path)

        # Step 3: Validate results
        assert isinstance(features, AudioFeatures)
        assert features.file_path == audio_path
        assert features.bpm is not None
        assert features.duration_seconds > 0
        assert features.sample_rate == 44100
        assert features.metadata is not None

        # Step 4: Verify analyzer was used
        analyzer = features.metadata.get("analyzer")
        assert analyzer in ["essentia", "librosa"]

        print(f"\n  Workflow test: {analyzer} analyzer")
        print(f"  BPM: {features.bpm:.1f}")
        print(f"  Duration: {features.duration_seconds:.1f}s")

    @pytest.mark.asyncio
    async def test_multiple_file_analysis_workflow(self, real_audio_samples):
        """Test: Analyze multiple files sequentially."""
        service = AudioFeaturesService()

        results = {}
        for name, audio_path in real_audio_samples.items():
            features = await service.analyze_file(audio_path)
            results[name] = features

        # Validate all analyses succeeded
        assert len(results) == len(real_audio_samples)
        for name, features in results.items():
            assert isinstance(features, AudioFeatures)
            assert features.bpm is not None or name == "oneshot"  # One-shot may not have BPM

        print(f"\n  Analyzed {len(results)} files successfully")

    @pytest.mark.asyncio
    async def test_concurrent_analysis_workflow(self, real_audio_samples):
        """Test: Concurrent analysis of multiple files."""
        service = AudioFeaturesService()

        # Analyze all files concurrently
        tasks = [
            service.analyze_file(audio_path)
            for audio_path in real_audio_samples.values()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Validate all succeeded
        successful = [r for r in results if isinstance(r, AudioFeatures)]
        errors = [r for r in results if isinstance(r, Exception)]

        assert len(successful) == len(real_audio_samples), \
            f"Some analyses failed: {errors}"

        print(f"\n  Concurrent analysis: {len(successful)} files analyzed")


class TestErrorScenarios:
    """Test error handling in complete workflows."""

    @pytest.mark.asyncio
    async def test_file_not_found_error(self):
        """Test: Analyze non-existent file → Error."""
        service = AudioFeaturesService()
        non_existent = Path("/tmp/does_not_exist_12345.wav")

        with pytest.raises(AudioError) as exc_info:
            await service.analyze_file(non_existent)

        assert "not found" in str(exc_info.value).lower()
        print(f"\n  File not found error: {exc_info.value.message}")

    @pytest.mark.asyncio
    async def test_empty_file_error(self, tmp_path):
        """Test: Analyze empty file → Error."""
        service = AudioFeaturesService()

        # Create empty file
        empty_file = tmp_path / "empty.wav"
        empty_file.touch()

        with pytest.raises(AudioError) as exc_info:
            await service.analyze_file(empty_file)

        assert "empty" in str(exc_info.value).lower()
        print(f"\n  Empty file error: {exc_info.value.message}")

    @pytest.mark.asyncio
    async def test_corrupted_file_error(self, tmp_path):
        """Test: Analyze corrupted file → Error."""
        service = AudioFeaturesService()

        # Create corrupted file (random bytes)
        corrupted_file = tmp_path / "corrupted.wav"
        with open(corrupted_file, 'wb') as f:
            f.write(b"This is not a WAV file" * 100)

        with pytest.raises(AudioError) as exc_info:
            await service.analyze_file(corrupted_file)

        print(f"\n  Corrupted file error: {exc_info.value.message}")

    @pytest.mark.asyncio
    async def test_very_short_audio(self, tmp_path):
        """Test: Analyze very short audio (<0.1s)."""
        service = AudioFeaturesService()

        # Create very short sample (0.05s)
        sample_rate = 44100
        duration = 0.05
        audio = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(duration * sample_rate)))

        short_file = tmp_path / "very_short.wav"
        sf.write(str(short_file), audio, sample_rate)

        # Should handle gracefully (may not have BPM)
        features = await service.analyze_file(short_file)

        assert isinstance(features, AudioFeatures)
        assert features.duration_seconds < 0.1
        print(f"\n  Very short audio: {features.duration_seconds:.3f}s analyzed")

    @pytest.mark.asyncio
    async def test_very_long_audio(self, tmp_path):
        """Test: Analyze long audio (>5 minutes)."""
        # Skip by default as this is slow
        pytest.skip("Long audio test - enable manually for stress testing")

        service = AudioFeaturesService()

        # Create 5-minute sample
        sample_rate = 44100
        duration = 300.0  # 5 minutes
        # Use sparse generation to save memory
        audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(duration * sample_rate)))

        long_file = tmp_path / "very_long.wav"
        sf.write(str(long_file), audio, sample_rate)

        features = await service.analyze_file(long_file)

        assert isinstance(features, AudioFeatures)
        assert features.duration_seconds > 290  # ~5 minutes


class TestFallbackBehavior:
    """Test fallback from Essentia to librosa."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_essentia_failure_fallback(self, real_audio_samples, monkeypatch):
        """Test: Essentia fails → Falls back to librosa."""
        service = AudioFeaturesService()
        audio_path = real_audio_samples["hiphop"]

        # Force Essentia to fail
        if service.analyzer_type == "essentia":
            original_method = service._analyze_with_essentia

            async def mock_essentia_fail(*args, **kwargs):
                raise RuntimeError("Simulated Essentia failure")

            service._analyze_with_essentia = mock_essentia_fail

            # Should fallback to librosa
            features = await service.analyze_file(audio_path)

            assert isinstance(features, AudioFeatures)
            assert features.metadata.get("analyzer") == "librosa"

            print(f"\n  Fallback test: Essentia → librosa successful")

            # Restore
            service._analyze_with_essentia = original_method

    @pytest.mark.asyncio
    async def test_librosa_only_workflow(self, real_audio_samples, monkeypatch):
        """Test: Complete workflow with librosa only (no Essentia)."""
        from app.core.config import settings
        monkeypatch.setattr(settings, 'USE_ESSENTIA', False)

        service = AudioFeaturesService()
        audio_path = real_audio_samples["house"]

        features = await service.analyze_file(audio_path)

        assert isinstance(features, AudioFeatures)
        assert features.metadata.get("analyzer") == "librosa"
        assert features.bpm is not None

        print(f"\n  librosa-only workflow: BPM={features.bpm:.1f}")


class TestRealAudioFiles:
    """Test with actual audio files if available."""

    @pytest.mark.asyncio
    async def test_real_fixture_file(self):
        """Test analysis of real test fixture if available."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "test_sample.wav"

        if not fixture_path.exists():
            pytest.skip("Real test fixture not found")

        service = AudioFeaturesService()
        features = await service.analyze_file(fixture_path)

        assert isinstance(features, AudioFeatures)
        assert features.duration_seconds > 0

        print(f"\n  Real fixture analysis:")
        print(f"    Duration: {features.duration_seconds:.2f}s")
        print(f"    BPM: {features.bpm}")
        print(f"    Sample rate: {features.sample_rate}")
        print(f"    Channels: {features.num_channels}")
        print(f"    Analyzer: {features.metadata.get('analyzer')}")


@pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
class TestEssentiaSpecificWorkflow:
    """Test Essentia-specific E2E workflows."""

    @pytest.mark.asyncio
    async def test_essentia_bpm_confidence_workflow(self, real_audio_samples):
        """Test: Analyze → Check confidence → Validate BPM."""
        from app.services.essentia_analyzer import EssentiaAnalyzer

        analyzer = EssentiaAnalyzer()
        audio_path = real_audio_samples["house"]

        result = await analyzer.analyze_bpm(audio_path)

        assert result is not None
        assert result.bpm > 0
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.beats) > 0

        print(f"\n  Essentia workflow:")
        print(f"    BPM: {result.bpm:.1f}")
        print(f"    Confidence: {result.confidence:.3f}")
        print(f"    Beats detected: {len(result.beats)}")

    @pytest.mark.asyncio
    async def test_essentia_full_analysis_workflow(self, real_audio_samples):
        """Test: Full Essentia analysis (BPM + genre if models available)."""
        from app.services.essentia_analyzer import EssentiaAnalyzer

        analyzer = EssentiaAnalyzer()
        audio_path = real_audio_samples["hiphop"]

        result = await analyzer.analyze_full(audio_path)

        assert isinstance(result, dict)
        assert "bpm" in result
        assert "genre" in result
        assert "analyzer" in result
        assert result["analyzer"] == "essentia"
        assert result["success"] is True

        print(f"\n  Full analysis:")
        print(f"    BPM: {result['bpm'].bpm if result['bpm'] else 'N/A'}")
        print(f"    Genre: {result['genre'].primary_genre if result['genre'] else 'N/A'}")


class TestStressScenarios:
    """Test system under stress conditions."""

    @pytest.mark.asyncio
    async def test_rapid_sequential_analyses(self, real_audio_samples):
        """Test: Many sequential analyses in quick succession."""
        service = AudioFeaturesService()
        audio_path = real_audio_samples["hiphop"]

        # Run 20 analyses quickly
        for i in range(20):
            features = await service.analyze_file(audio_path)
            assert isinstance(features, AudioFeatures)

        print(f"\n  20 rapid sequential analyses: PASS")

    @pytest.mark.asyncio
    async def test_concurrent_stress_10_files(self, real_audio_samples):
        """Test: 10 concurrent analyses."""
        service = AudioFeaturesService()
        audio_path = real_audio_samples["house"]

        # Create 10 concurrent tasks
        tasks = [service.analyze_file(audio_path) for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = [r for r in results if isinstance(r, AudioFeatures)]
        assert len(successful) == 10

        print(f"\n  10 concurrent analyses: PASS")


class TestMetadataPreservation:
    """Test that metadata is preserved through workflow."""

    @pytest.mark.asyncio
    async def test_metadata_contains_analyzer_info(self, real_audio_samples):
        """Test: Metadata tracks which analyzer was used."""
        service = AudioFeaturesService()
        audio_path = real_audio_samples["hiphop"]

        features = await service.analyze_file(audio_path)

        assert features.metadata is not None
        assert "analyzer" in features.metadata
        assert features.metadata["analyzer"] in ["essentia", "librosa"]

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_essentia_metadata_complete(self, real_audio_samples, monkeypatch):
        """Test: Essentia analysis includes all expected metadata."""
        from app.core.config import settings
        monkeypatch.setattr(settings, 'USE_ESSENTIA', True)
        monkeypatch.setattr(settings, 'ENABLE_GENRE_CLASSIFICATION', False)

        service = AudioFeaturesService()
        audio_path = real_audio_samples["house"]

        features = await service.analyze_file(audio_path)

        metadata = features.metadata
        assert metadata.get("analyzer") == "essentia"
        assert "bpm_confidence" in metadata
        assert "bpm_method" in metadata

        print(f"\n  Essentia metadata:")
        print(f"    Analyzer: {metadata['analyzer']}")
        print(f"    BPM confidence: {metadata['bpm_confidence']}")
        print(f"    BPM method: {metadata['bpm_method']}")
