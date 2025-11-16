"""
Utility script to generate real audio fixtures for testing.

This script creates real WAV files that can be used for testing audio analysis.
Run this script to pre-generate fixtures if needed, or use the pytest fixtures
in conftest.py which generate them automatically.

Usage:
    python backend/tests/generate_test_fixtures.py
"""
import numpy as np
from pathlib import Path


def create_test_wav(output_path: Path, duration: float = 2.0, frequency: int = 440, sample_rate: int = 44100):
    """
    Generate a simple sine wave WAV file.

    Args:
        output_path: Where to save the WAV file
        duration: Length in seconds (default 2.0)
        frequency: Frequency in Hz (default 440Hz = A4 note)
        sample_rate: Sample rate in Hz (default 44100)

    The generated file is a pure tone that can be analyzed by librosa
    for BPM, spectral features, etc.
    """
    try:
        import soundfile as sf

        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)

        # Write to file
        sf.write(output_path, audio, sample_rate)
        print(f"✓ Created {output_path} using soundfile")
        print(f"  Duration: {duration}s, Frequency: {frequency}Hz, Sample Rate: {sample_rate}Hz")

    except ImportError:
        # Fallback to scipy if soundfile not available
        from scipy.io import wavfile

        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = (0.5 * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

        # Write to file
        wavfile.write(output_path, sample_rate, audio)
        print(f"✓ Created {output_path} using scipy")
        print(f"  Duration: {duration}s, Frequency: {frequency}Hz, Sample Rate: {sample_rate}Hz")


def create_corrupted_wav(output_path: Path):
    """
    Create an invalid WAV file for error testing.

    This file has a WAV extension but contains invalid data.
    """
    output_path.write_bytes(b"Not a valid WAV file, just random bytes for testing")
    print(f"✓ Created corrupted file {output_path}")


def main():
    """Generate test fixtures in the fixtures directory."""
    # Create fixtures directory
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)

    print("Generating audio test fixtures...\n")

    # Generate test WAV files
    create_test_wav(fixtures_dir / "test_sample.wav", duration=2.0, frequency=440)
    create_test_wav(fixtures_dir / "test_sample_short.wav", duration=0.5, frequency=880)
    create_test_wav(fixtures_dir / "test_sample_bass.wav", duration=3.0, frequency=110)

    # Generate corrupted file
    create_corrupted_wav(fixtures_dir / "corrupted.wav")

    # Create empty file
    empty_path = fixtures_dir / "empty.wav"
    empty_path.write_bytes(b"")
    print(f"✓ Created empty file {empty_path}")

    print(f"\n✓ All fixtures created in {fixtures_dir}")
    print("\nThese fixtures can be used for manual testing or as reference.")
    print("Pytest will auto-generate fixtures in tmp_path during test runs.")


if __name__ == "__main__":
    main()
