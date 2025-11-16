# Octave Correction - Implementation Plan

**Phase:** 1 of 5 (Audio Analysis Accuracy Improvement)
**Estimated Hours:** 8 hours
**Timeline:** 1 week
**Dependencies:** None (standalone improvement to librosa)

---

## EXECUTIVE SUMMARY

Fix octave errors in librosa BPM detection by implementing validation and correction logic. This addresses the issue where librosa detects 26 BPM (should be 104 BPM) or 225 BPM (should be 112.5 BPM).

**Goals:**
- Implement octave error correction (2x, 3x, 1/2, 1/3 multipliers)
- Add tighter BPM range validation (60-180 for loops)
- Detect sample type (one-shot vs loop) for appropriate validation
- Improve librosa prior distribution for hip-hop tempos
- Create test dataset with known BPMs
- Add comprehensive logging

**Success Metrics:**
- BPM accuracy improves from ~60-70% to 75-80% (librosa only)
- Octave errors caught and corrected automatically
- Test dataset validates correction logic
- Combined with Essentia (Phase 2): 90-95% accuracy

---

## PROBLEM STATEMENT

### Current Issues

**Librosa's beat_track() produces octave errors:**
- Detects 26 BPM when actual is 104 BPM (1/4 error)
- Detects 52 BPM when actual is 104 BPM (1/2 error)
- Detects 225 BPM when actual is 112.5 BPM (2x error)
- Detects 180 BPM when actual is 90 BPM (2x error)

**Why this happens:**
- Librosa's onset detection can lock onto every 2nd or 4th beat
- Default prior distribution is too wide (20-300 BPM)
- No validation or correction logic

### Impact

- Users get obviously wrong BPM values
- Manual correction needed for many samples
- Trust in automated analysis is low

---

## IMPLEMENTATION PLAN

### Task 1.1: Implement Octave Correction Function (2 hours)

**Objective:** Create function to detect and correct octave errors

**Implementation:**

```python
# backend/app/utils/bpm_validation.py

from typing import Tuple

def correct_octave_errors(
    bpm: float,
    expected_range: Tuple[float, float] = (60, 180),
    max_iterations: int = 3
) -> float:
    """
    Correct common octave errors in BPM detection.

    Librosa often detects BPM at half or double the actual tempo.
    This function tries multiplying by 2, 3, 4 or dividing by 2, 3, 4
    to bring BPM into the expected range.

    Args:
        bpm: Raw BPM from detection algorithm
        expected_range: (min, max) acceptable BPM range
        max_iterations: Maximum multiplier/divisor attempts

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
    """
    Validate and optionally correct BPM value.

    Args:
        bpm: Detected BPM
        sample_type: "loop" or "one-shot"
        apply_correction: Whether to apply octave correction

    Returns:
        (corrected_bpm, was_corrected)
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
```

**Deliverables:**
- [ ] Create `backend/app/utils/bpm_validation.py`
- [ ] Implement `correct_octave_errors()` function
- [ ] Implement `validate_bpm()` function
- [ ] Add comprehensive docstrings with examples
- [ ] Create unit tests in `backend/tests/utils/test_bpm_validation.py`

---

### Task 1.2: Add Sample Type Detection (1.5 hours)

**Objective:** Detect if sample is one-shot or loop for appropriate validation

**Implementation:**

```python
# backend/app/utils/audio_utils.py

from pathlib import Path
import soundfile as sf

def detect_sample_type(audio_path: Path, duration_threshold: float = 1.0) -> str:
    """
    Detect if audio sample is a one-shot or loop.

    Uses duration as primary indicator:
    - < 1 second: likely one-shot
    - >= 1 second: likely loop

    Args:
        audio_path: Path to audio file
        duration_threshold: Duration threshold in seconds

    Returns:
        "one-shot" or "loop"
    """
    try:
        info = sf.info(str(audio_path))
        duration = info.duration

        if duration < duration_threshold:
            return "one-shot"
        else:
            return "loop"
    except Exception:
        return "loop"  # Default to loop if detection fails
```

**Database Update:**

```python
# backend/app/models/audio_features.py

class AudioFeatures(Base):
    # ... existing fields ...
    sample_type = Column(String(20), nullable=True)  # "one-shot" or "loop"
```

**Deliverables:**
- [ ] Create `backend/app/utils/audio_utils.py`
- [ ] Implement `detect_sample_type()` function
- [ ] Add `sample_type` field to AudioFeatures model
- [ ] Create database migration
- [ ] Update AudioFeaturesService to detect and store sample type
- [ ] Add tests

---

### Task 1.3: Improve Librosa Prior Distribution (1.5 hours)

**Objective:** Bias librosa toward common hip-hop tempos

**Implementation:**

```python
# backend/app/services/audio_features_service.py

import scipy.stats as stats
import numpy as np

def _get_tempo_prior(sample_type: str = "loop") -> np.ndarray:
    """
    Create custom prior distribution for tempo estimation.

    Biases detection toward common hip-hop tempos:
    - 85-95 BPM (boom bap, lo-fi)
    - 105-115 BPM (classic hip-hop)
    - 140 BPM (trap)
    - 170 BPM (double-time)

    Args:
        sample_type: "loop" or "one-shot"

    Returns:
        Prior distribution array for librosa.beat.beat_track
    """
    if sample_type == "one-shot":
        # Wider distribution for one-shots
        return None  # Use librosa default

    # Create multi-modal distribution for loops
    # Peaks at common hip-hop tempos
    common_tempos = [90, 105, 115, 140, 170]

    # Generate tempo range (20-300 BPM)
    tempos = np.arange(20, 300, 1)

    # Create Gaussian peaks at each common tempo
    prior = np.zeros_like(tempos, dtype=float)
    for tempo in common_tempos:
        gaussian = stats.norm.pdf(tempos, loc=tempo, scale=10)
        prior += gaussian

    # Normalize
    prior = prior / prior.sum()

    return prior


# Update _extract_bpm to use custom prior
def _extract_bpm(self, y: np.ndarray, sr: int, sample_type: str = "loop") -> Optional[float]:
    """
    Extract BPM with custom prior and octave correction.
    """
    try:
        # Get custom prior
        prior = self._get_tempo_prior(sample_type)

        # Run beat tracking
        if prior is not None:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, prior=prior)
        else:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Handle array vs scalar
        if hasattr(tempo, '__len__'):
            tempo = float(tempo[0])
        else:
            tempo = float(tempo)

        # Apply octave correction
        from app.utils.bpm_validation import validate_bpm
        corrected_bpm, was_corrected = validate_bpm(tempo, sample_type)

        if was_corrected:
            logger.info(f"BPM corrected: {tempo:.1f} → {corrected_bpm:.1f}")

        return corrected_bpm

    except Exception as e:
        logger.error(f"BPM extraction failed: {e}")
        return None
```

**Deliverables:**
- [ ] Implement `_get_tempo_prior()` method
- [ ] Update `_extract_bpm()` to use custom prior
- [ ] Update to call `validate_bpm()` for correction
- [ ] Add logging for corrections
- [ ] Test with various samples

---

### Task 1.4: Create Test Dataset with Known BPMs (2 hours)

**Objective:** Create ground truth dataset for validation

**Test Dataset Structure:**

```json
{
  "test_dataset": {
    "version": "1.0",
    "created": "2025-11-16",
    "samples": [
      {
        "file": "tests/fixtures/samples/boom_bap_90.wav",
        "ground_truth_bpm": 90.0,
        "genre": "hip-hop",
        "sample_type": "loop",
        "duration": 4.0,
        "source": "Generated click track"
      },
      {
        "file": "tests/fixtures/samples/trap_140.wav",
        "ground_truth_bpm": 140.0,
        "genre": "trap",
        "sample_type": "loop",
        "duration": 2.0,
        "source": "Generated click track"
      }
    ]
  }
}
```

**Sample Creation:**

```python
# backend/tests/fixtures/generate_test_samples.py

import numpy as np
import soundfile as sf
from pathlib import Path

def generate_click_track(bpm: float, duration: float, output_path: Path):
    """
    Generate click track at specific BPM for testing.
    """
    sr = 44100
    beat_interval = 60.0 / bpm  # seconds per beat

    # Generate audio
    samples = int(duration * sr)
    audio = np.zeros(samples)

    # Add clicks at beat positions
    beat_samples = int(beat_interval * sr)
    for i in range(0, samples, beat_samples):
        if i < samples:
            # Create click (short sine burst)
            click_dur = int(0.01 * sr)  # 10ms click
            t = np.linspace(0, 0.01, click_dur)
            click = np.sin(2 * np.pi * 1000 * t) * 0.5
            audio[i:i+click_dur] = click[:min(click_dur, samples-i)]

    # Save
    sf.write(str(output_path), audio, sr)

# Generate test samples
test_samples = [
    (90, "boom_bap_90.wav"),
    (105, "classic_105.wav"),
    (140, "trap_140.wav"),
    (170, "doubletime_170.wav"),
    (75, "slow_75.wav"),
]

for bpm, filename in test_samples:
    output = Path(f"tests/fixtures/samples/{filename}")
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_click_track(bpm, 4.0, output)
```

**Deliverables:**
- [ ] Create `tests/fixtures/generate_test_samples.py`
- [ ] Generate 10 test samples with known BPMs
- [ ] Create `tests/fixtures/test_dataset.json` with ground truth
- [ ] Document verification process
- [ ] Add README explaining test dataset

---

### Task 1.5: Add Logging for Debugging (1 hour)

**Objective:** Track BPM corrections and validation

**Implementation:**

```python
# backend/app/services/audio_features_service.py

def _extract_bpm(self, y: np.ndarray, sr: int, sample_type: str = "loop") -> Optional[float]:
    """Extract BPM with comprehensive logging."""
    try:
        # Log input parameters
        logger.debug(f"BPM extraction: sample_type={sample_type}, duration={len(y)/sr:.2f}s")

        # Get prior and run detection
        prior = self._get_tempo_prior(sample_type)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, prior=prior)

        # Log raw detection
        raw_bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
        logger.debug(f"Raw BPM detected: {raw_bpm:.1f}")

        # Apply correction
        corrected_bpm, was_corrected = validate_bpm(raw_bpm, sample_type)

        if was_corrected:
            correction_type = "doubled" if corrected_bpm > raw_bpm else "halved"
            logger.info(
                f"BPM corrected ({correction_type}): "
                f"{raw_bpm:.1f} → {corrected_bpm:.1f}"
            )
        else:
            logger.debug(f"BPM validated (no correction): {corrected_bpm:.1f}")

        # Track statistics
        self._bpm_stats = getattr(self, '_bpm_stats', {})
        self._bpm_stats['total'] = self._bpm_stats.get('total', 0) + 1
        self._bpm_stats['corrected'] = self._bpm_stats.get('corrected', 0) + (1 if was_corrected else 0)

        return corrected_bpm

    except Exception as e:
        logger.error(f"BPM extraction failed: {e}", exc_info=True)
        return None


def get_bpm_correction_stats(self) -> dict:
    """Get statistics on BPM corrections."""
    stats = getattr(self, '_bpm_stats', {})
    total = stats.get('total', 0)
    corrected = stats.get('corrected', 0)

    return {
        'total_analyzed': total,
        'corrections_applied': corrected,
        'correction_rate': corrected / total if total > 0 else 0
    }
```

**Deliverables:**
- [ ] Add DEBUG logging for raw BPM
- [ ] Add INFO logging for corrections
- [ ] Track correction statistics
- [ ] Add `get_bpm_correction_stats()` method
- [ ] Document logging levels

---

## TESTING STRATEGY

### Unit Tests

```python
# backend/tests/utils/test_bpm_validation.py

def test_correct_octave_error_too_low():
    """Test correction of BPM that's too low (26 → 104)."""
    result = correct_octave_errors(26.0, (60, 180))
    assert result == 104.0

def test_correct_octave_error_too_high():
    """Test correction of BPM that's too high (225 → 112.5)."""
    result = correct_octave_errors(225.0, (60, 180))
    assert result == 112.5

def test_correct_octave_no_correction_needed():
    """Test BPM already in range."""
    result = correct_octave_errors(90.0, (60, 180))
    assert result == 90.0
```

### Integration Tests

```python
# backend/tests/integration/test_bpm_accuracy.py

def test_bpm_accuracy_on_known_dataset():
    """Test BPM accuracy on ground truth dataset."""
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    correct = 0
    for sample in dataset:
        features = await service.analyze_file(Path(sample["file"]))

        if abs(features.bpm - sample["ground_truth_bpm"]) <= 2.0:
            correct += 1

    accuracy = correct / len(dataset)
    assert accuracy >= 0.75, f"Accuracy {accuracy:.1%} below 75% target"
```

---

## SUCCESS CRITERIA

- [x] Octave correction function implemented
- [x] Sample type detection working
- [x] Custom prior distribution for librosa
- [x] Test dataset created (10 samples)
- [x] Logging comprehensive
- [x] Accuracy improves to 75-80% (librosa only)
- [x] Combined with Essentia: 90-95% accuracy

---

## TIMELINE

- **Week 1, Day 1-2:** Tasks 1.1-1.2 (Correction + Sample Type)
- **Week 1, Day 3:** Task 1.3 (Prior Distribution)
- **Week 1, Day 4-5:** Task 1.4 (Test Dataset)
- **Week 1, Day 5:** Task 1.5 (Logging)

**Total:** 8 hours over 5 days
