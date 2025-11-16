# Octave Correction - Context

**Feature:** Fix octave errors in librosa BPM detection
**Phase:** 1 of 5 (Audio Analysis Accuracy)
**Status:** Ready to Implement
**Created:** 2025-11-16
**Dependencies:** None (standalone improvement)

---

## Why Octave Correction?

### The Problem
Librosa's beat_track() frequently detects BPM at octave intervals:
- 26 BPM instead of 104 BPM (off by 4x)
- 52 BPM instead of 104 BPM (off by 2x)
- 225 BPM instead of 112.5 BPM (off by 2x)
- 180 BPM instead of 90 BPM (off by 2x)

This happens because librosa's onset detection can lock onto every 2nd, 3rd, or 4th beat instead of every beat.

### The Solution
Simple validation and correction:
1. If BPM < 60: try doubling (2x, 4x, 8x)
2. If BPM > 180: try halving (÷2, ÷4, ÷8)
3. Bring BPM into expected range

---

## Key Decisions

### 1. Expected BPM Ranges
**Decision:** Use different ranges for loops vs one-shots
**Rationale:**
- Loops: 60-180 BPM (typical music range)
- One-shots: 40-200 BPM (wider tolerance)
- Most hip-hop: 85-170 BPM

### 2. Correction Strategy
**Decision:** Iterative doubling/halving up to 3 times
**Rationale:**
- Catches 2x, 4x, 8x errors
- Most octave errors are 2x or 4x
- Prevents infinite loops

### 3. Sample Type Detection
**Decision:** Use duration threshold (1 second)
**Rationale:**
- Simple and effective
- <1s = one-shot (kick, snare)
- ≥1s = loop (beat, pattern)
- Easy to override if needed

### 4. Custom Prior Distribution
**Decision:** Multi-modal Gaussian peaks at common hip-hop tempos
**Rationale:**
- Biases librosa toward 90, 105, 115, 140, 170 BPM
- Reduces octave errors
- Still allows wide range

---

## Architecture Notes

### Correction Flow

```
Raw BPM from librosa
    ↓
Is it in expected range? (60-180 for loops)
    ↓
NO → Try doubling/halving
    ↓
Found valid BPM? → Return corrected
    ↓
NO → Return closest attempt
```

### Integration Points

```
AudioFeaturesService
    ↓
detect_sample_type() → "loop" or "one-shot"
    ↓
_extract_bpm(sample_type)
    ↓
librosa.beat_track(prior=custom_prior)
    ↓
validate_bpm(raw_bpm, sample_type)
    ↓
correct_octave_errors() if needed
    ↓
Return corrected BPM + metadata
```

---

## Key Files

### Files to Create
- `backend/app/utils/bpm_validation.py` - Correction logic
- `backend/app/utils/audio_utils.py` - Sample type detection
- `backend/tests/utils/test_bpm_validation.py` - Unit tests
- `backend/tests/fixtures/generate_test_samples.py` - Test data generator
- `backend/tests/fixtures/test_dataset.json` - Ground truth BPMs

### Files to Modify
- `backend/app/services/audio_features_service.py` - Integrate correction
- `backend/app/models/audio_features.py` - Add sample_type field

---

## Testing Strategy

### Test Dataset
Generate click tracks at known BPMs:
- 90 BPM (boom bap)
- 105 BPM (classic hip-hop)
- 140 BPM (trap)
- 170 BPM (double-time)
- 75 BPM (slow)
- Plus musical samples if available

### Validation
- Accuracy target: 75-80% within ±2 BPM
- Improvement: +10-15% over current librosa
- Combined with Essentia: 90-95% total

---

## Expected Improvements

### Before (Current Librosa)
- Accuracy: ~60-70%
- Octave errors: Common (20-30% of samples)
- User trust: Low

### After (With Octave Correction)
- Accuracy: ~75-80%
- Octave errors: Rare (5-10% of samples)
- User trust: Medium

### With Essentia (Phase 2 Complete)
- Accuracy: 90-95%
- Octave errors: Very rare (<2%)
- User trust: High

---

## Success Metrics

- 75%+ accuracy on test dataset
- Octave corrections logged and tracked
- No regression in existing functionality
- Works as fallback when Essentia unavailable

---

## Notes

- This is a "quick win" improvement
- Works independently of Essentia
- Low risk (just validation logic)
- Provides better librosa fallback
- Foundation for cross-validation (Phase 3)
