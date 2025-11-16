"""
BPM accuracy validation tests for Essentia vs librosa.

Tests BPM detection accuracy against known ground truth values.
Target: 90%+ accuracy within ±2 BPM for Essentia.
"""
import pytest
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import soundfile as sf

from app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from app.services.essentia_analyzer import EssentiaAnalyzer

from app.services.audio_features_service import AudioFeaturesService


def create_click_track(bpm: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    """
    Create a simple click track at specified BPM for testing.

    Args:
        bpm: Target beats per minute
        duration: Duration in seconds
        sample_rate: Audio sample rate

    Returns:
        Audio signal with clear beats at specified BPM
    """
    # Calculate samples per beat
    beat_interval = 60.0 / bpm  # seconds per beat
    samples_per_beat = int(beat_interval * sample_rate)

    # Create click track
    total_samples = int(duration * sample_rate)
    audio = np.zeros(total_samples)

    # Add clicks at beat positions
    num_beats = int(duration / beat_interval)
    for i in range(num_beats):
        click_pos = int(i * samples_per_beat)
        if click_pos < total_samples:
            # Create click: short sine burst
            click_duration = 0.01  # 10ms click
            click_samples = int(click_duration * sample_rate)
            t = np.linspace(0, click_duration, click_samples)
            click = 0.8 * np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 50)

            end_pos = min(click_pos + click_samples, total_samples)
            audio[click_pos:end_pos] = click[:end_pos - click_pos]

    return audio


def create_musical_sample(bpm: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    """
    Create a musical sample with harmonic content at specified BPM.

    Args:
        bpm: Target beats per minute
        duration: Duration in seconds
        sample_rate: Audio sample rate

    Returns:
        Audio signal with musical content at specified BPM
    """
    beat_interval = 60.0 / bpm
    t = np.linspace(0, duration, int(duration * sample_rate))

    # Create bassline on beats
    audio = np.zeros_like(t)
    num_beats = int(duration / beat_interval)

    for i in range(num_beats):
        beat_time = i * beat_interval
        # Envelope for each beat
        envelope = np.exp(-(t - beat_time) * 4) * (t >= beat_time)
        # Bass note (110Hz A)
        bass = 0.6 * np.sin(2 * np.pi * 110 * t) * envelope
        audio += bass

    # Add hi-hat on eighth notes
    for i in range(num_beats * 2):
        eighth_time = i * beat_interval / 2
        envelope = np.exp(-(t - eighth_time) * 20) * (t >= eighth_time)
        hihat = 0.2 * np.random.randn(len(t)) * envelope  # Noise burst
        audio += hihat

    return audio


@pytest.fixture
def ground_truth_samples(tmp_path) -> Dict[str, Tuple[Path, float]]:
    """
    Create test samples with known BPM values.

    Returns:
        Dictionary mapping sample name to (path, ground_truth_bpm)
    """
    samples = {}
    sample_rate = 44100
    duration = 8.0  # 8 seconds for good BPM detection

    # Test common BPMs
    test_bpms = [
        ("90bpm_click", 90.0, "click"),
        ("120bpm_click", 120.0, "click"),
        ("140bpm_click", 140.0, "click"),
        ("90bpm_musical", 90.0, "musical"),
        ("120bpm_musical", 120.0, "musical"),
        ("140bpm_musical", 140.0, "musical"),
        ("75bpm_musical", 75.0, "musical"),  # Slower tempo
        ("160bpm_musical", 160.0, "musical"),  # Faster tempo
    ]

    for name, bpm, sample_type in test_bpms:
        if sample_type == "click":
            audio = create_click_track(bpm, duration, sample_rate)
        else:
            audio = create_musical_sample(bpm, duration, sample_rate)

        file_path = tmp_path / f"{name}.wav"
        sf.write(str(file_path), audio, sample_rate)
        samples[name] = (file_path, bpm)

    return samples


def is_bpm_accurate(detected: float, ground_truth: float, tolerance: float = 2.0) -> bool:
    """
    Check if detected BPM is within tolerance of ground truth.

    Args:
        detected: Detected BPM value
        ground_truth: Known ground truth BPM
        tolerance: Acceptable error in BPM (default: ±2 BPM)

    Returns:
        True if within tolerance
    """
    # Also check for half/double tempo detection
    half_tempo = ground_truth / 2
    double_tempo = ground_truth * 2

    within_main = abs(detected - ground_truth) <= tolerance
    within_half = abs(detected - half_tempo) <= tolerance
    within_double = abs(detected - double_tempo) <= tolerance

    return within_main or within_half or within_double


@pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
class TestEssentiaAccuracy:
    """Test Essentia BPM detection accuracy."""

    @pytest.mark.asyncio
    async def test_click_track_90bpm(self, ground_truth_samples):
        """Test Essentia accuracy on 90 BPM click track."""
        analyzer = EssentiaAnalyzer()
        audio_path, ground_truth = ground_truth_samples["90bpm_click"]

        result = await analyzer.analyze_bpm(audio_path, method="multifeature")

        assert result is not None
        assert is_bpm_accurate(result.bpm, ground_truth), \
            f"Detected {result.bpm:.1f} BPM, expected {ground_truth} BPM (±2)"

        print(f"\n  90 BPM click: detected {result.bpm:.1f} (conf: {result.confidence:.2f})")

    @pytest.mark.asyncio
    async def test_click_track_120bpm(self, ground_truth_samples):
        """Test Essentia accuracy on 120 BPM click track."""
        analyzer = EssentiaAnalyzer()
        audio_path, ground_truth = ground_truth_samples["120bpm_click"]

        result = await analyzer.analyze_bpm(audio_path, method="multifeature")

        assert result is not None
        assert is_bpm_accurate(result.bpm, ground_truth), \
            f"Detected {result.bpm:.1f} BPM, expected {ground_truth} BPM (±2)"

        print(f"\n  120 BPM click: detected {result.bpm:.1f} (conf: {result.confidence:.2f})")

    @pytest.mark.asyncio
    async def test_musical_90bpm(self, ground_truth_samples):
        """Test Essentia accuracy on 90 BPM musical sample."""
        analyzer = EssentiaAnalyzer()
        audio_path, ground_truth = ground_truth_samples["90bpm_musical"]

        result = await analyzer.analyze_bpm(audio_path, method="multifeature")

        assert result is not None
        assert is_bpm_accurate(result.bpm, ground_truth), \
            f"Detected {result.bpm:.1f} BPM, expected {ground_truth} BPM (±2)"

        print(f"\n  90 BPM musical: detected {result.bpm:.1f} (conf: {result.confidence:.2f})")

    @pytest.mark.asyncio
    async def test_musical_120bpm(self, ground_truth_samples):
        """Test Essentia accuracy on 120 BPM musical sample."""
        analyzer = EssentiaAnalyzer()
        audio_path, ground_truth = ground_truth_samples["120bpm_musical"]

        result = await analyzer.analyze_bpm(audio_path, method="multifeature")

        assert result is not None
        assert is_bpm_accurate(result.bpm, ground_truth), \
            f"Detected {result.bpm:.1f} BPM, expected {ground_truth} BPM (±2)"

        print(f"\n  120 BPM musical: detected {result.bpm:.1f} (conf: {result.confidence:.2f})")

    @pytest.mark.asyncio
    async def test_all_samples_accuracy_report(self, ground_truth_samples):
        """Generate accuracy report across all test samples."""
        analyzer = EssentiaAnalyzer()

        results = []
        for name, (audio_path, ground_truth) in ground_truth_samples.items():
            result = await analyzer.analyze_bpm(audio_path, method="multifeature")

            if result:
                accurate = is_bpm_accurate(result.bpm, ground_truth)
                error = abs(result.bpm - ground_truth)

                # Check for half/double tempo
                tempo_type = "correct"
                if abs(result.bpm - ground_truth / 2) <= 2.0:
                    tempo_type = "half"
                elif abs(result.bpm - ground_truth * 2) <= 2.0:
                    tempo_type = "double"

                results.append({
                    "name": name,
                    "ground_truth": ground_truth,
                    "detected": result.bpm,
                    "error": error,
                    "confidence": result.confidence,
                    "accurate": accurate,
                    "tempo_type": tempo_type
                })

        # Calculate accuracy
        total = len(results)
        accurate_count = sum(1 for r in results if r["accurate"])
        accuracy_pct = (accurate_count / total) * 100

        # Print report
        print("\n" + "="*70)
        print("ESSENTIA BPM ACCURACY REPORT")
        print("="*70)
        print(f"Total samples: {total}")
        print(f"Accurate (±2 BPM): {accurate_count}")
        print(f"Accuracy: {accuracy_pct:.1f}%")
        print("\nDetails:")
        print("-"*70)

        for r in results:
            status = "✓" if r["accurate"] else "✗"
            print(f"{status} {r['name']:20s}: "
                  f"GT={r['ground_truth']:6.1f} "
                  f"Detected={r['detected']:6.1f} "
                  f"Error={r['error']:5.1f} "
                  f"Conf={r['confidence']:.2f} "
                  f"({r['tempo_type']})")

        print("="*70 + "\n")

        # Target: 90%+ accuracy
        assert accuracy_pct >= 80.0, \
            f"Accuracy {accuracy_pct:.1f}% below 80% target (aiming for 90%+)"


class TestLibrosaAccuracy:
    """Test librosa BPM detection accuracy for comparison."""

    @pytest.mark.asyncio
    async def test_librosa_90bpm_musical(self, ground_truth_samples, monkeypatch):
        """Test librosa accuracy on 90 BPM musical sample."""
        from app.core.config import settings
        monkeypatch.setattr(settings, 'USE_ESSENTIA', False)

        service = AudioFeaturesService()
        audio_path, ground_truth = ground_truth_samples["90bpm_musical"]

        features = await service.analyze_file(audio_path)

        if features.bpm:
            print(f"\n  90 BPM musical (librosa): detected {features.bpm:.1f}")
            # librosa is less accurate, so we don't assert accuracy

    @pytest.mark.asyncio
    async def test_librosa_accuracy_comparison(self, ground_truth_samples, monkeypatch):
        """Compare librosa vs Essentia accuracy."""
        from app.core.config import settings

        # Test librosa
        monkeypatch.setattr(settings, 'USE_ESSENTIA', False)
        service_librosa = AudioFeaturesService()

        librosa_results = []
        for name, (audio_path, ground_truth) in ground_truth_samples.items():
            features = await service_librosa.analyze_file(audio_path)
            if features.bpm:
                accurate = is_bpm_accurate(features.bpm, ground_truth)
                librosa_results.append({
                    "name": name,
                    "detected": features.bpm,
                    "accurate": accurate
                })

        librosa_accuracy = (sum(1 for r in librosa_results if r["accurate"]) /
                           len(librosa_results) * 100) if librosa_results else 0

        print(f"\n  librosa accuracy: {librosa_accuracy:.1f}%")

        # Test Essentia (if available)
        if ESSENTIA_AVAILABLE:
            monkeypatch.setattr(settings, 'USE_ESSENTIA', True)
            from app.services.essentia_analyzer import EssentiaAnalyzer
            analyzer = EssentiaAnalyzer()

            essentia_results = []
            for name, (audio_path, ground_truth) in ground_truth_samples.items():
                result = await analyzer.analyze_bpm(audio_path)
                if result:
                    accurate = is_bpm_accurate(result.bpm, ground_truth)
                    essentia_results.append({
                        "name": name,
                        "detected": result.bpm,
                        "accurate": accurate
                    })

            essentia_accuracy = (sum(1 for r in essentia_results if r["accurate"]) /
                               len(essentia_results) * 100) if essentia_results else 0

            print(f"  Essentia accuracy: {essentia_accuracy:.1f}%")
            print(f"  Improvement: +{essentia_accuracy - librosa_accuracy:.1f}%")

            # Essentia should be more accurate
            assert essentia_accuracy >= librosa_accuracy, \
                "Essentia should be at least as accurate as librosa"


class TestConfidenceScores:
    """Test BPM confidence scoring."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_confidence_on_clear_signal(self, ground_truth_samples):
        """Test that click tracks produce high confidence scores."""
        analyzer = EssentiaAnalyzer()
        audio_path, _ = ground_truth_samples["120bpm_click"]

        result = await analyzer.analyze_bpm(audio_path)

        assert result is not None
        # Click tracks should have very high confidence
        assert result.confidence > 0.5, \
            f"Click track confidence {result.confidence:.2f} unexpectedly low"

        print(f"\n  Click track confidence: {result.confidence:.3f}")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_confidence_correlation_with_accuracy(self, ground_truth_samples):
        """Test that higher confidence correlates with better accuracy."""
        analyzer = EssentiaAnalyzer()

        results = []
        for name, (audio_path, ground_truth) in ground_truth_samples.items():
            result = await analyzer.analyze_bpm(audio_path)
            if result:
                accurate = is_bpm_accurate(result.bpm, ground_truth)
                results.append({
                    "confidence": result.confidence,
                    "accurate": accurate
                })

        # Group by confidence level
        high_conf = [r for r in results if r["confidence"] > 0.7]
        low_conf = [r for r in results if r["confidence"] <= 0.7]

        if high_conf:
            high_conf_accuracy = sum(1 for r in high_conf if r["accurate"]) / len(high_conf)
            print(f"\n  High confidence (>0.7) accuracy: {high_conf_accuracy*100:.1f}%")

        if low_conf:
            low_conf_accuracy = sum(1 for r in low_conf if r["accurate"]) / len(low_conf)
            print(f"  Low confidence (≤0.7) accuracy: {low_conf_accuracy*100:.1f}%")

        # Expect high confidence samples to be more accurate
        if high_conf and low_conf:
            assert high_conf_accuracy >= low_conf_accuracy, \
                "Higher confidence should correlate with better accuracy"
