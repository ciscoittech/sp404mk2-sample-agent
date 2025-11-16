"""Demonstration of sample type detection and BPM validation.

This script creates test samples and shows how sample type detection
and BPM validation work together.
"""

import asyncio
import numpy as np
import soundfile as sf
from pathlib import Path
from tempfile import TemporaryDirectory

from app.services.audio_features_service import AudioFeaturesService
from app.utils.audio_utils import detect_sample_type


def create_test_sample(filename: str, duration: float, bpm: float = 90) -> Path:
    """Create a test audio sample with beat pattern."""
    sr = 44100
    samples = int(duration * sr)
    audio = np.zeros(samples)

    if bpm > 0:
        # Add beats
        beat_interval = 60.0 / bpm
        beat_samples = int(beat_interval * sr)

        for i in range(0, samples, beat_samples):
            if i < samples:
                click_dur = int(0.01 * sr)
                t = np.linspace(0, 0.01, click_dur)
                click = np.sin(2 * np.pi * 1000 * t) * 0.5
                end_idx = min(i + click_dur, samples)
                audio[i:end_idx] = click[:end_idx - i]
    else:
        # Simple sine wave (no beat pattern)
        t = np.linspace(0, duration, samples)
        audio = np.sin(2 * np.pi * 60 * t) * 0.5

    filepath = Path(filename)
    sf.write(str(filepath), audio, sr)
    return filepath


async def demo():
    """Run sample type detection demonstration."""
    print("=" * 70)
    print("Sample Type Detection & BPM Validation Demonstration")
    print("=" * 70)
    print()

    service = AudioFeaturesService()

    with TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Test samples: (name, duration, bpm)
        test_samples = [
            ("kick.wav", 0.3, 0),           # One-shot, no BPM pattern
            ("snare.wav", 0.4, 0),          # One-shot, no BPM pattern
            ("hihat.wav", 0.2, 0),          # One-shot, very short
            ("loop_90bpm.wav", 4.0, 90),    # Loop at 90 BPM
            ("loop_120bpm.wav", 2.0, 120),  # Loop at 120 BPM
            ("phrase.wav", 3.5, 0),         # Long sample, no clear BPM
        ]

        for name, duration, bpm in test_samples:
            print(f"\nSample: {name}")
            print("-" * 70)

            # Create sample
            filepath = create_test_sample(str(tmppath / name), duration, bpm)

            # Detect sample type
            sample_type = detect_sample_type(filepath)
            print(f"  Duration: {duration:.2f}s")
            print(f"  Sample Type: {sample_type}")

            # Analyze with AudioFeaturesService
            features = await service.analyze_file(filepath)

            print(f"  Detected BPM: {features.bpm if features.bpm else 'None (too short or no pattern)'}")
            print(f"  Stored Sample Type: {features.sample_type}")

            if features.bpm:
                if bpm > 0:
                    error = abs(features.bpm - bpm)
                    print(f"  Expected BPM: {bpm}")
                    print(f"  Error: {error:.1f} BPM")

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("Sample type detection distinguishes:")
    print("  - One-shots: < 1.0s duration (kicks, snares, hi-hats)")
    print("  - Loops: >= 1.0s duration (beats, phrases, melodies)")
    print()
    print("BPM validation applies different ranges:")
    print("  - One-shots: 40-200 BPM (wider range)")
    print("  - Loops: 60-180 BPM (tighter range)")
    print()
    print("Octave correction automatically fixes:")
    print("  - 26 BPM → 104 BPM (4x multiplier)")
    print("  - 225 BPM → 112.5 BPM (2x divisor)")
    print()


if __name__ == "__main__":
    asyncio.run(demo())
