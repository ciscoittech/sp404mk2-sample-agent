"""Tests for audio utility functions."""

import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.utils.audio_utils import detect_sample_type


def create_test_audio(duration: float, output_path: Path) -> None:
    """Create a test audio file with specified duration.

    Args:
        duration: Duration in seconds
        output_path: Path to save audio file
    """
    sr = 44100
    samples = int(duration * sr)
    # Generate simple sine wave
    t = np.linspace(0, duration, samples)
    audio = np.sin(2 * np.pi * 440 * t) * 0.5  # 440 Hz sine wave
    sf.write(str(output_path), audio, sr)


class TestDetectSampleType:
    """Test sample type detection function."""

    def test_short_sample_is_one_shot(self, tmp_path):
        """Test that short samples (< 1s) are detected as one-shots."""
        audio_file = tmp_path / "kick.wav"
        create_test_audio(0.5, audio_file)

        result = detect_sample_type(audio_file)
        assert result == "one-shot"

    def test_long_sample_is_loop(self, tmp_path):
        """Test that long samples (>= 1s) are detected as loops."""
        audio_file = tmp_path / "beat_loop.wav"
        create_test_audio(4.0, audio_file)

        result = detect_sample_type(audio_file)
        assert result == "loop"

    def test_boundary_case_is_loop(self, tmp_path):
        """Test that exactly 1.0s is detected as loop."""
        audio_file = tmp_path / "boundary.wav"
        create_test_audio(1.0, audio_file)

        result = detect_sample_type(audio_file)
        assert result == "loop"

    def test_very_short_sample_is_one_shot(self, tmp_path):
        """Test that very short samples (< 0.1s) are detected as one-shots."""
        audio_file = tmp_path / "click.wav"
        create_test_audio(0.05, audio_file)

        result = detect_sample_type(audio_file)
        assert result == "one-shot"

    def test_custom_threshold(self, tmp_path):
        """Test custom duration threshold."""
        audio_file = tmp_path / "snare.wav"
        create_test_audio(0.75, audio_file)

        # With default threshold (1.0s), should be one-shot
        result = detect_sample_type(audio_file, duration_threshold=1.0)
        assert result == "one-shot"

        # With lower threshold (0.5s), should be loop
        result = detect_sample_type(audio_file, duration_threshold=0.5)
        assert result == "loop"

    def test_invalid_file_returns_loop(self, tmp_path):
        """Test that invalid files default to 'loop' (safe default)."""
        invalid_file = tmp_path / "nonexistent.wav"

        result = detect_sample_type(invalid_file)
        assert result == "loop"

    def test_corrupted_file_returns_loop(self, tmp_path):
        """Test that corrupted files default to 'loop'."""
        corrupted_file = tmp_path / "corrupted.wav"
        # Create an invalid audio file (just text)
        corrupted_file.write_text("not an audio file")

        result = detect_sample_type(corrupted_file)
        assert result == "loop"

    def test_empty_file_returns_loop(self, tmp_path):
        """Test that empty files default to 'loop'."""
        empty_file = tmp_path / "empty.wav"
        empty_file.touch()

        result = detect_sample_type(empty_file)
        assert result == "loop"


class TestRealWorldScenarios:
    """Test realistic audio sample scenarios."""

    def test_kick_drum_sample(self, tmp_path):
        """Test typical kick drum duration."""
        kick = tmp_path / "kick.wav"
        create_test_audio(0.3, kick)  # 300ms kick

        assert detect_sample_type(kick) == "one-shot"

    def test_snare_drum_sample(self, tmp_path):
        """Test typical snare drum duration."""
        snare = tmp_path / "snare.wav"
        create_test_audio(0.2, snare)  # 200ms snare

        assert detect_sample_type(snare) == "one-shot"

    def test_hihat_sample(self, tmp_path):
        """Test typical hi-hat duration."""
        hihat = tmp_path / "hihat.wav"
        create_test_audio(0.15, hihat)  # 150ms hi-hat

        assert detect_sample_type(hihat) == "one-shot"

    def test_drum_loop_sample(self, tmp_path):
        """Test typical drum loop duration."""
        loop = tmp_path / "drum_loop.wav"
        create_test_audio(2.0, loop)  # 2 second loop

        assert detect_sample_type(loop) == "loop"

    def test_vocal_phrase_sample(self, tmp_path):
        """Test typical vocal phrase duration."""
        vocal = tmp_path / "vocal_phrase.wav"
        create_test_audio(3.5, vocal)  # 3.5 second phrase

        assert detect_sample_type(vocal) == "loop"

    def test_bass_line_loop(self, tmp_path):
        """Test typical bass line loop duration."""
        bass = tmp_path / "bass_loop.wav"
        create_test_audio(4.0, bass)  # 4 bar loop at 120 BPM

        assert detect_sample_type(bass) == "loop"
