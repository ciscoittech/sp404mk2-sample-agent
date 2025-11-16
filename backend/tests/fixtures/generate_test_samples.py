"""
Generate test samples with known BPMs for validation.

This script creates click tracks at specific BPMs to validate
BPM detection accuracy. All samples have known ground truth BPMs
that can be used to measure detection accuracy.

Usage:
    python backend/tests/fixtures/generate_test_samples.py

Output:
    - WAV files in backend/tests/fixtures/samples/
    - test_dataset.json with ground truth BPMs
"""
import json
import numpy as np
import soundfile as sf
from pathlib import Path
from datetime import datetime


def generate_click_track(bpm: float, duration: float, output_path: Path):
    """
    Generate click track at specific BPM for testing.

    Creates an audio file with clear, audible clicks at precise beat
    positions. Each click is a 10ms sine burst at 1000Hz, making it
    easy for BPM detection algorithms to lock onto the tempo.

    Args:
        bpm: Target beats per minute (e.g., 90.0, 140.0)
        duration: Duration in seconds (e.g., 4.0)
        output_path: Path to save WAV file

    Example:
        >>> output = Path("tests/fixtures/samples/click_90bpm.wav")
        >>> generate_click_track(90.0, 4.0, output)
        Generated: tests/fixtures/samples/click_90bpm.wav (90.0 BPM, 4.0s)
    """
    sr = 44100  # Sample rate (CD quality)
    beat_interval = 60.0 / bpm  # Seconds per beat

    # Generate audio buffer
    samples = int(duration * sr)
    audio = np.zeros(samples)

    # Add clicks at beat positions
    beat_samples = int(beat_interval * sr)
    for i in range(0, samples, beat_samples):
        if i < samples:
            # Create click (short sine burst)
            click_dur = int(0.01 * sr)  # 10ms click
            t = np.linspace(0, 0.01, click_dur)
            click = np.sin(2 * np.pi * 1000 * t) * 0.5  # 1000Hz sine

            # Add click to audio
            end_idx = min(i + click_dur, samples)
            audio[i:end_idx] = click[:end_idx - i]

    # Save WAV file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), audio, sr)
    print(f"Generated: {output_path} ({bpm} BPM, {duration}s)")


def generate_musical_sample(bpm: float, duration: float, output_path: Path):
    """
    Generate musical sample with harmonic content at specific BPM.

    Creates a more realistic musical sample with bass notes and hi-hats
    to test BPM detection on musical content (not just click tracks).

    Args:
        bpm: Target beats per minute
        duration: Duration in seconds
        output_path: Path to save WAV file

    Example:
        >>> output = Path("tests/fixtures/samples/musical_90bpm.wav")
        >>> generate_musical_sample(90.0, 4.0, output)
        Generated: tests/fixtures/samples/musical_90bpm.wav (90.0 BPM, 4.0s)
    """
    sr = 44100
    beat_interval = 60.0 / bpm
    t = np.linspace(0, duration, int(duration * sr))

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
        # Noise burst for hi-hat
        hihat = 0.2 * np.random.randn(len(t)) * envelope
        audio += hihat

    # Normalize to prevent clipping
    audio = audio / np.max(np.abs(audio)) * 0.8

    # Save WAV file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), audio, sr)
    print(f"Generated: {output_path} ({bpm} BPM, {duration}s)")


def create_test_dataset():
    """
    Create comprehensive test dataset with known BPMs.

    Generates:
    - Click tracks at common hip-hop tempos
    - Musical samples for realism testing
    - Edge cases (slow/fast tempos)
    - Test dataset JSON with ground truth

    Returns:
        dict: Test dataset structure with sample metadata
    """
    # Define test samples
    test_samples = [
        # Click tracks - common hip-hop tempos
        {
            "bpm": 90.0,
            "duration": 4.0,
            "filename": "click_90bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Boom bap tempo"
        },
        {
            "bpm": 105.0,
            "duration": 4.0,
            "filename": "click_105bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Classic hip-hop tempo"
        },
        {
            "bpm": 115.0,
            "duration": 4.0,
            "filename": "click_115bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Mid-tempo"
        },
        {
            "bpm": 140.0,
            "duration": 2.0,
            "filename": "click_140bpm.wav",
            "genre": "trap",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Trap tempo"
        },
        {
            "bpm": 170.0,
            "duration": 2.0,
            "filename": "click_170bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Double-time"
        },
        # Edge cases
        {
            "bpm": 75.0,
            "duration": 4.0,
            "filename": "click_75bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Slow tempo edge case"
        },
        {
            "bpm": 120.0,
            "duration": 4.0,
            "filename": "click_120bpm.wav",
            "genre": "house",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Common house tempo"
        },
        {
            "bpm": 60.0,
            "duration": 4.0,
            "filename": "click_60bpm.wav",
            "genre": "downtempo",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Lower boundary edge case"
        },
        {
            "bpm": 180.0,
            "duration": 2.0,
            "filename": "click_180bpm.wav",
            "genre": "dnb",
            "sample_type": "loop",
            "source": "Generated click track",
            "notes": "Upper boundary edge case"
        },
        # Musical samples for realism
        {
            "bpm": 90.0,
            "duration": 4.0,
            "filename": "musical_90bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated musical sample",
            "notes": "Musical content at boom bap tempo"
        },
        {
            "bpm": 140.0,
            "duration": 2.0,
            "filename": "musical_140bpm.wav",
            "genre": "trap",
            "sample_type": "loop",
            "source": "Generated musical sample",
            "notes": "Musical content at trap tempo"
        },
        {
            "bpm": 105.0,
            "duration": 4.0,
            "filename": "musical_105bpm.wav",
            "genre": "hip-hop",
            "sample_type": "loop",
            "source": "Generated musical sample",
            "notes": "Musical content at classic tempo"
        },
    ]

    # Generate samples
    base_dir = Path(__file__).parent / "samples"
    base_dir.mkdir(parents=True, exist_ok=True)

    dataset = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "description": "Ground truth BPMs for accuracy validation",
        "samples": []
    }

    for sample in test_samples:
        output_path = base_dir / sample["filename"]

        # Generate audio
        if "click" in sample["filename"]:
            generate_click_track(sample["bpm"], sample["duration"], output_path)
        else:
            generate_musical_sample(sample["bpm"], sample["duration"], output_path)

        # Add to dataset
        dataset["samples"].append({
            "file": str(output_path.relative_to(Path(__file__).parent.parent)),
            "ground_truth_bpm": sample["bpm"],
            "genre": sample["genre"],
            "sample_type": sample["sample_type"],
            "duration": sample["duration"],
            "source": sample["source"],
            "notes": sample["notes"]
        })

    # Save dataset JSON
    dataset_path = Path(__file__).parent / "test_dataset.json"
    with open(dataset_path, 'w') as f:
        json.dump(dataset, f, indent=2)

    print(f"\nTest dataset saved to: {dataset_path}")
    print(f"Total samples: {len(dataset['samples'])}")

    return dataset


if __name__ == "__main__":
    print("="*70)
    print("Generating Test Dataset for BPM Accuracy Validation")
    print("="*70)
    print()

    dataset = create_test_dataset()

    print()
    print("="*70)
    print("Summary")
    print("="*70)
    print(f"Click tracks: {sum(1 for s in dataset['samples'] if 'click' in s['file'])}")
    print(f"Musical samples: {sum(1 for s in dataset['samples'] if 'musical' in s['file'])}")
    print(f"BPM range: {min(s['ground_truth_bpm'] for s in dataset['samples'])}-{max(s['ground_truth_bpm'] for s in dataset['samples'])} BPM")
    print()
    print("Next steps:")
    print("1. Verify samples with external tool (e.g., Ableton, online BPM detector)")
    print("2. Run accuracy validation tests: pytest backend/tests/accuracy/")
    print("3. Review results and tune octave correction if needed")
    print()
