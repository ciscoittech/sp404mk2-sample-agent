"""Audio utility functions for sample analysis.

Provides helper functions for audio file processing including sample type
detection (one-shot vs loop) based on duration analysis.
"""

from pathlib import Path
import soundfile as sf


def detect_sample_type(audio_path: Path, duration_threshold: float = 1.0) -> str:
    """
    Detect if audio sample is a one-shot or loop.

    Uses duration as primary indicator:
    - < duration_threshold seconds: likely one-shot (kicks, snares, hits)
    - >= duration_threshold seconds: likely loop (beats, phrases)

    Args:
        audio_path: Path to audio file
        duration_threshold: Duration threshold in seconds (default: 1.0)

    Returns:
        "one-shot" if duration < threshold, else "loop"

    Examples:
        >>> detect_sample_type(Path("kick.wav"))  # 0.5s duration
        "one-shot"

        >>> detect_sample_type(Path("beat_loop.wav"))  # 4.0s duration
        "loop"

        >>> detect_sample_type(Path("snare.wav"), duration_threshold=0.5)
        "one-shot"
    """
    try:
        info = sf.info(str(audio_path))
        duration = info.duration

        if duration < duration_threshold:
            return "one-shot"
        else:
            return "loop"

    except Exception:
        # Safe default: assume loop (more conservative validation)
        # Loops have tighter BPM range (60-180) vs one-shots (40-200)
        return "loop"
