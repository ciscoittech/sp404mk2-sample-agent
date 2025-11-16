"""BPM validation and octave error correction utilities.

This module provides functions to detect and correct common octave errors
in BPM detection algorithms (particularly librosa's beat_track). Librosa
often detects BPM at half or double the actual tempo, requiring correction.
"""

from typing import Tuple


def correct_octave_errors(
    bpm: float,
    expected_range: Tuple[float, float] = (60, 180),
    max_iterations: int = 3
) -> float:
    """Correct common octave errors in BPM detection.

    Librosa often detects BPM at half or double the actual tempo.
    This function tries multiplying by 2, 4, 8 or dividing by 2, 4, 8
    to bring BPM into the expected range.

    Args:
        bpm: Raw BPM from detection algorithm
        expected_range: (min, max) acceptable BPM range
        max_iterations: Maximum multiplier/divisor attempts (2^1, 2^2, 2^3)

    Returns:
        Corrected BPM within expected range

    Examples:
        >>> correct_octave_errors(26.0, (60, 180))
        104.0  # 26 * 4 = 104

        >>> correct_octave_errors(225.0, (60, 180))
        112.5  # 225 / 2 = 112.5

        >>> correct_octave_errors(90.0, (60, 180))
        90.0  # Already in range
    """
    min_bpm, max_bpm = expected_range
    corrected = bpm

    # If already in range, return as-is
    if min_bpm <= corrected <= max_bpm:
        return corrected

    # If too low, try doubling up to max_iterations times
    if corrected < min_bpm:
        for i in range(1, max_iterations + 1):
            multiplier = 2 ** i  # 2, 4, 8
            candidate = bpm * multiplier
            if min_bpm <= candidate <= max_bpm:
                return candidate
            elif candidate > max_bpm:
                break  # Stop if we've gone too high

    # If too high, try halving up to max_iterations times
    if corrected > max_bpm:
        for i in range(1, max_iterations + 1):
            divisor = 2 ** i  # 2, 4, 8
            candidate = bpm / divisor
            if min_bpm <= candidate <= max_bpm:
                return candidate
            elif candidate < min_bpm:
                break  # Stop if we've gone too low

    # If still out of range, return closest boundary
    if corrected < min_bpm:
        return bpm * 2  # At least try doubling
    else:
        return bpm / 2  # At least try halving


def validate_bpm(
    bpm: float,
    sample_type: str = "loop",
    apply_correction: bool = True
) -> Tuple[float, bool]:
    """Validate and optionally correct BPM value.

    Args:
        bpm: Detected BPM
        sample_type: "loop", "one-shot", or "general"
        apply_correction: Whether to apply octave correction

    Returns:
        Tuple of (corrected_bpm, was_corrected)

    Examples:
        >>> validate_bpm(26.0, "loop", apply_correction=True)
        (104.0, True)

        >>> validate_bpm(90.0, "loop", apply_correction=True)
        (90.0, False)

        >>> validate_bpm(26.0, "loop", apply_correction=False)
        (26.0, False)
    """
    # Define expected ranges by sample type
    ranges = {
        "loop": (60, 180),     # Typical music loops
        "one-shot": (40, 200), # One-shots can be wider
        "general": (40, 200)   # Fallback
    }

    expected_range = ranges.get(sample_type, ranges["general"])

    if apply_correction:
        corrected = correct_octave_errors(bpm, expected_range)
        was_corrected = abs(corrected - bpm) > 0.1
        return corrected, was_corrected
    else:
        return bpm, False
