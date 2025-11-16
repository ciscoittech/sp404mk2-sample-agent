"""Tests for custom tempo prior distribution in AudioFeaturesService."""

import numpy as np
import pytest

from app.services.audio_features_service import AudioFeaturesService


class TestTempoPrior:
    """Tests for the _get_tempo_prior method."""

    @pytest.fixture
    def service(self):
        """Create AudioFeaturesService instance."""
        return AudioFeaturesService()

    def test_prior_returns_none_for_one_shot(self, service):
        """Test that one-shots get None (use librosa default)."""
        prior = service._get_tempo_prior(sample_type="one-shot")
        assert prior is None

    def test_prior_returns_array_for_loop(self, service):
        """Test that loops get a numpy array prior."""
        prior = service._get_tempo_prior(sample_type="loop")
        assert prior is not None
        assert isinstance(prior, np.ndarray)

    def test_prior_has_correct_shape(self, service):
        """Test prior has correct shape (271 elements for 30-300 BPM)."""
        prior = service._get_tempo_prior(sample_type="loop")
        assert len(prior) == 271  # 30-300 BPM at 1 BPM resolution

    def test_prior_is_normalized(self, service):
        """Test prior sums to 1.0 (normalized probability distribution)."""
        prior = service._get_tempo_prior(sample_type="loop")
        # Use np.isclose to handle floating point precision
        assert np.isclose(prior.sum(), 1.0, atol=1e-6)

    def test_prior_all_positive(self, service):
        """Test all prior values are non-negative."""
        prior = service._get_tempo_prior(sample_type="loop")
        assert np.all(prior >= 0)

    def test_prior_has_peaks_at_target_tempos(self, service):
        """Test prior has peaks near target hip-hop tempos."""
        prior = service._get_tempo_prior(sample_type="loop")
        tempos = np.linspace(30, 300, 271)

        # Expected peaks near these tempos (±5 BPM tolerance)
        target_tempos = [90, 105, 115, 140, 170]

        for target in target_tempos:
            # Find region around target (±5 BPM)
            idx = np.argmin(np.abs(tempos - target))
            region_start = max(0, idx-5)
            region_end = min(len(prior), idx+6)
            local_region = prior[region_start:region_end]

            # There should be a significant peak in this region
            peak_value = np.max(local_region)

            # The peak should be significantly higher than the baseline
            baseline = np.mean(prior)  # Average probability
            assert peak_value > baseline * 2.0, \
                f"Expected significant peak near {target} BPM, peak={peak_value:.6f}, baseline={baseline:.6f} (ratio={peak_value/baseline:.2f}x)"

    def test_prior_peak_at_90_bpm(self, service):
        """Test prior has peak near 90 BPM (boom bap)."""
        prior = service._get_tempo_prior(sample_type="loop")
        tempos = np.linspace(30, 300, 271)

        # Find value at 90 BPM
        idx_90 = np.argmin(np.abs(tempos - 90))
        value_90 = prior[idx_90]

        # Should be higher than far-away tempos
        idx_50 = np.argmin(np.abs(tempos - 50))
        idx_130 = np.argmin(np.abs(tempos - 130))

        assert value_90 > prior[idx_50]
        assert value_90 > prior[idx_130]

    def test_prior_peak_at_140_bpm(self, service):
        """Test prior has peak near 140 BPM (trap)."""
        prior = service._get_tempo_prior(sample_type="loop")
        tempos = np.linspace(30, 300, 271)

        # Find value near 140 BPM (check a ±5 BPM range for the peak)
        idx_140 = np.argmin(np.abs(tempos - 140))
        region_140 = prior[max(0, idx_140-5):min(len(prior), idx_140+6)]
        value_140 = np.max(region_140)  # Take max in region

        # Should be higher than far-away tempos (outside the peak regions)
        # Use 60 BPM and 200 BPM as far-away references
        idx_60 = np.argmin(np.abs(tempos - 60))
        idx_200 = np.argmin(np.abs(tempos - 200))

        assert value_140 > prior[idx_60]
        assert value_140 > prior[idx_200]

    def test_prior_low_at_extremes(self, service):
        """Test prior is low at extreme tempos (30, 300 BPM)."""
        prior = service._get_tempo_prior(sample_type="loop")
        tempos = np.linspace(30, 300, 271)

        # Find peaks
        peak_value = np.max(prior)

        # Values at extremes should be much lower
        assert prior[0] < peak_value * 0.1  # 30 BPM
        assert prior[-1] < peak_value * 0.1  # 300 BPM

    def test_prior_general_sample_type(self, service):
        """Test prior for general sample type (treated as loop)."""
        prior = service._get_tempo_prior(sample_type="general")
        # Should be same as loop (not None)
        assert prior is not None
        assert isinstance(prior, np.ndarray)

    def test_prior_unknown_sample_type(self, service):
        """Test prior for unknown sample type defaults to loop behavior."""
        prior = service._get_tempo_prior(sample_type="unknown")
        # Default behavior is loop (not None)
        assert prior is not None
        assert isinstance(prior, np.ndarray)


class TestTempoPriorIntegration:
    """Integration tests for tempo prior in BPM extraction."""

    @pytest.fixture
    def service(self):
        """Create AudioFeaturesService instance."""
        return AudioFeaturesService()

    def test_prior_used_in_bpm_extraction(self, service, caplog):
        """Test that custom prior is logged when used."""
        # Create a simple audio signal
        import librosa
        sr = 22050
        duration = 2.0
        # Generate a 100 BPM click track
        y = np.zeros(int(sr * duration))
        beat_interval = 60.0 / 100  # seconds per beat
        beat_samples = int(beat_interval * sr)
        for i in range(0, len(y), beat_samples):
            if i < len(y):
                y[i] = 0.5

        # Extract BPM with loop type (should use prior)
        with caplog.at_level("DEBUG"):
            bpm = service._extract_bpm(y, sr, sample_type="loop")

        # Check logging
        assert "Using custom prior for loop" in caplog.text

    def test_prior_not_used_for_one_shot(self, service, caplog):
        """Test that default prior is logged for one-shots."""
        # Create a simple audio signal
        sr = 22050
        duration = 0.5  # Short one-shot
        y = np.random.randn(int(sr * duration)) * 0.1

        # Extract BPM with one-shot type (should not use prior)
        with caplog.at_level("DEBUG"):
            bpm = service._extract_bpm(y, sr, sample_type="one-shot")

        # Check logging
        assert "Using default librosa prior for one-shot" in caplog.text

    def test_prior_performance(self, service):
        """Test that prior generation is fast (<10ms)."""
        import time

        start = time.perf_counter()
        for _ in range(100):
            prior = service._get_tempo_prior(sample_type="loop")
        elapsed = time.perf_counter() - start

        # Should be very fast (100 iterations in <100ms)
        assert elapsed < 0.1, f"Prior generation too slow: {elapsed*10:.2f}ms per call"

    def test_prior_caching_not_required(self, service):
        """Test that prior can be regenerated without performance issues."""
        # Generate prior 10 times
        priors = [service._get_tempo_prior(sample_type="loop") for _ in range(10)]

        # All should be equal
        for p in priors[1:]:
            assert np.array_equal(p, priors[0])


class TestPriorVisualization:
    """Tests and utilities for visualizing the prior distribution."""

    @pytest.fixture
    def service(self):
        """Create AudioFeaturesService instance."""
        return AudioFeaturesService()

    def test_prior_visualization_data(self, service):
        """Test that prior can be visualized (provides correct data)."""
        prior = service._get_tempo_prior(sample_type="loop")
        tempos = np.linspace(30, 300, 271)

        # Should have matching shapes for plotting
        assert len(prior) == len(tempos)

        # Find peaks for visualization markers
        target_tempos = [90, 105, 115, 140, 170]
        peaks = []
        for target in target_tempos:
            idx = np.argmin(np.abs(tempos - target))
            peaks.append((tempos[idx], prior[idx]))

        # All peaks should be in reasonable range
        for tempo, prob in peaks:
            assert 80 <= tempo <= 180
            assert prob > 0
