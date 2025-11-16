# Octave Correction - Task Checklist

**Phase:** 1 of 5
**Total Hours:** 8 hours
**Timeline:** 1 week

---

## Task 1.1: Implement Octave Correction Function (2 hours)

- [ ] **Create bpm_validation.py module**
  - [ ] Create `backend/app/utils/bpm_validation.py`
  - [ ] Add module docstring

- [ ] **Implement correct_octave_errors() function**
  - [ ] Define function signature with type hints
  - [ ] Implement doubling logic (if too low)
  - [ ] Implement halving logic (if too high)
  - [ ] Add boundary checking
  - [ ] Add comprehensive docstring with examples

- [ ] **Implement validate_bpm() function**
  - [ ] Define ranges for loop/one-shot/general
  - [ ] Call correct_octave_errors() if apply_correction=True
  - [ ] Return (corrected_bpm, was_corrected) tuple
  - [ ] Add docstring

- [ ] **Create unit tests**
  - [ ] Create `backend/tests/utils/__init__.py`
  - [ ] Create `backend/tests/utils/test_bpm_validation.py`
  - [ ] Test too low (26 → 104)
  - [ ] Test too high (225 → 112.5)
  - [ ] Test already in range (90 → 90)
  - [ ] Test edge cases (30, 300)
  - [ ] Test different sample types

---

## Task 1.2: Add Sample Type Detection (1.5 hours)

- [ ] **Create audio_utils.py module**
  - [ ] Create `backend/app/utils/audio_utils.py`
  - [ ] Add module docstring

- [ ] **Implement detect_sample_type() function**
  - [ ] Use soundfile.info() to get duration
  - [ ] Apply threshold (default 1.0 second)
  - [ ] Return "one-shot" or "loop"
  - [ ] Handle errors (return "loop" as default)
  - [ ] Add docstring

- [ ] **Update AudioFeatures model**
  - [ ] Add `sample_type` field to model
  - [ ] Create Alembic migration
  - [ ] Run migration

- [ ] **Integrate with AudioFeaturesService**
  - [ ] Call detect_sample_type() in analyze_file()
  - [ ] Pass sample_type to _extract_bpm()
  - [ ] Store sample_type in database

- [ ] **Create tests**
  - [ ] Test short audio (<1s) → "one-shot"
  - [ ] Test long audio (≥1s) → "loop"
  - [ ] Test error handling

---

## Task 1.3: Improve Librosa Prior Distribution (1.5 hours)

- [ ] **Implement _get_tempo_prior() method**
  - [ ] Create multi-modal Gaussian distribution
  - [ ] Add peaks at common tempos: 90, 105, 115, 140, 170 BPM
  - [ ] Use scipy.stats.norm for Gaussians
  - [ ] Normalize distribution
  - [ ] Add docstring

- [ ] **Update _extract_bpm() method**
  - [ ] Accept sample_type parameter
  - [ ] Call _get_tempo_prior(sample_type)
  - [ ] Pass prior to librosa.beat.beat_track()
  - [ ] Import validate_bpm from utils
  - [ ] Call validate_bpm(raw_bpm, sample_type)
  - [ ] Log corrections

- [ ] **Test prior distribution**
  - [ ] Generate visualization (optional)
  - [ ] Test with known-BPM samples
  - [ ] Compare with/without prior

---

## Task 1.4: Create Test Dataset with Known BPMs (2 hours)

- [ ] **Create sample generator script**
  - [ ] Create `backend/tests/fixtures/generate_test_samples.py`
  - [ ] Implement generate_click_track() function
  - [ ] Add sine wave click generation
  - [ ] Save as WAV files

- [ ] **Generate test samples**
  - [ ] 90 BPM click track (4 seconds)
  - [ ] 105 BPM click track (4 seconds)
  - [ ] 140 BPM click track (2 seconds)
  - [ ] 170 BPM click track (2 seconds)
  - [ ] 75 BPM click track (4 seconds)
  - [ ] Create samples directory: `tests/fixtures/samples/`

- [ ] **Create test dataset JSON**
  - [ ] Create `backend/tests/fixtures/test_dataset.json`
  - [ ] Document ground truth BPM for each sample
  - [ ] Include metadata (genre, sample_type, duration, source)

- [ ] **Verify test samples**
  - [ ] Listen to each click track
  - [ ] Verify BPM with online tool
  - [ ] Test with librosa.beat.beat_track()

- [ ] **Create README**
  - [ ] Document test dataset structure
  - [ ] Explain how to regenerate samples
  - [ ] List expected BPMs

---

## Task 1.5: Add Logging for Debugging (1 hour)

- [ ] **Add logging to _extract_bpm()**
  - [ ] Log input parameters (sample_type, duration)
  - [ ] Log raw BPM detected (DEBUG level)
  - [ ] Log corrections (INFO level)
  - [ ] Log validation result (DEBUG level)

- [ ] **Track correction statistics**
  - [ ] Add self._bpm_stats dict
  - [ ] Track total analyzed
  - [ ] Track corrections applied
  - [ ] Calculate correction rate

- [ ] **Implement get_bpm_correction_stats() method**
  - [ ] Return statistics dict
  - [ ] Include total_analyzed
  - [ ] Include corrections_applied
  - [ ] Include correction_rate

- [ ] **Add exception logging**
  - [ ] Log errors with exc_info=True
  - [ ] Include context (file path, parameters)

- [ ] **Test logging**
  - [ ] Verify DEBUG logs appear
  - [ ] Verify INFO logs for corrections
  - [ ] Check statistics calculation

---

## Validation Checklist

After completing all tasks:

- [ ] Octave correction function works correctly
- [ ] Sample type detection accurate
- [ ] Custom prior improves accuracy
- [ ] Test dataset created and validated
- [ ] Logging comprehensive
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Accuracy improvement measured (target: 75-80%)
- [ ] No regression in existing functionality
- [ ] Ready for Phase 3 (Cross-Validation)

---

## Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| 1.1: Correction Function | 2h | | |
| 1.2: Sample Type Detection | 1.5h | | |
| 1.3: Prior Distribution | 1.5h | | |
| 1.4: Test Dataset | 2h | | |
| 1.5: Logging | 1h | | |
| **Total** | **8h** | | |

---

## Success Criteria

- BPM accuracy improves from 60-70% to 75-80%
- Octave errors reduced from 20-30% to 5-10%
- Works independently of Essentia
- Provides better fallback when Essentia unavailable
- Foundation for cross-validation (Phase 3)
