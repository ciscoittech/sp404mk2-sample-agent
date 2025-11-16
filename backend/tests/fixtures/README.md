# Test Fixtures - BPM Accuracy Validation

This directory contains test samples with known BPMs for validating BPM detection accuracy.

## Contents

- **`samples/`** - Generated test audio files (WAV format)
- **`test_dataset.json`** - Ground truth BPM values and metadata
- **`generate_test_samples.py`** - Script to regenerate test samples
- **`test_sample.wav`** - Legacy test sample (retained for compatibility)

## Test Dataset Structure

The `test_dataset.json` file contains ground truth data for all test samples:

```json
{
  "version": "1.0",
  "created": "2025-11-16T...",
  "description": "Ground truth BPMs for accuracy validation",
  "samples": [
    {
      "file": "fixtures/samples/click_90bpm.wav",
      "ground_truth_bpm": 90.0,
      "genre": "hip-hop",
      "sample_type": "loop",
      "duration": 4.0,
      "source": "Generated click track",
      "notes": "Boom bap tempo"
    }
  ]
}
```

## Sample Types

### Click Tracks (9 samples)

Simple click tracks with clear, audible beats at precise positions. Each click is a 10ms sine burst at 1000Hz.

**BPMs Covered:**
- 60 BPM - Lower boundary edge case
- 75 BPM - Slow tempo edge case
- 90 BPM - Boom bap tempo
- 105 BPM - Classic hip-hop tempo
- 115 BPM - Mid-tempo
- 120 BPM - Common house tempo
- 140 BPM - Trap tempo
- 170 BPM - Double-time
- 180 BPM - Upper boundary edge case

### Musical Samples (3 samples)

Realistic musical content with bass notes and hi-hats to test BPM detection on musical material (not just clicks).

**BPMs Covered:**
- 90 BPM - Musical content at boom bap tempo
- 105 BPM - Musical content at classic tempo
- 140 BPM - Musical content at trap tempo

## Regenerating Test Samples

If you need to regenerate the test samples (e.g., to add new BPMs or modify generation parameters):

```bash
cd backend/tests/fixtures
python generate_test_samples.py
```

This will:
1. Create/update all WAV files in `samples/`
2. Regenerate `test_dataset.json` with current metadata
3. Print summary of generated samples

## Validation Criteria

BPM detection is considered **accurate** if the detected value is within **±2 BPM** of the ground truth.

### Accuracy Targets

- **Librosa (baseline):** 75%+ accuracy
- **Essentia:** 90%+ accuracy
- **With octave correction:** Should catch and fix 2x/1/2x errors

### Error Types

- **correct** - Within ±2 BPM of ground truth
- **half** - Detected at half tempo (e.g., 45 BPM instead of 90 BPM)
- **double** - Detected at double tempo (e.g., 180 BPM instead of 90 BPM)
- **triple** - Detected at 3x tempo
- **third** - Detected at 1/3 tempo
- **other** - Error doesn't match common octave patterns

## Verifying Ground Truth

To verify the ground truth BPMs are correct, you can:

### Option 1: Online BPM Detector
Upload samples to an online BPM detector:
- https://www.onlinesequencer.net/import
- https://tunebat.com/Analyzer

### Option 2: DAW (Digital Audio Workstation)
Import samples into Ableton, Logic, FL Studio, etc. and check detected BPM.

### Option 3: Manual Verification
For click tracks:
```python
import soundfile as sf
import numpy as np

# Load audio
audio, sr = sf.read("samples/click_90bpm.wav")

# Find clicks (peaks)
threshold = 0.1
clicks = np.where(audio > threshold)[0]
click_positions = clicks[np.diff(np.concatenate([[0], clicks])) > 100]

# Calculate intervals
intervals = np.diff(click_positions) / sr  # seconds
avg_interval = np.mean(intervals)
measured_bpm = 60.0 / avg_interval

print(f"Measured BPM: {measured_bpm:.2f}")
```

## Running Accuracy Tests

Run all accuracy validation tests:

```bash
# Run all accuracy tests
pytest backend/tests/accuracy/test_bpm_accuracy_validation.py -v

# Run specific test
pytest backend/tests/accuracy/test_bpm_accuracy_validation.py::test_bpm_accuracy_on_known_dataset -v

# Generate comprehensive report
pytest backend/tests/accuracy/test_bpm_accuracy_validation.py::test_generate_comprehensive_report -v -s
```

## Troubleshooting

### Sample Generation Fails

**Error:** `ModuleNotFoundError: No module named 'soundfile'`
```bash
pip install soundfile numpy
```

**Error:** `libsndfile not found`
```bash
# macOS
brew install libsndfile

# Ubuntu/Debian
sudo apt-get install libsndfile1

# Windows
# Install via conda: conda install -c conda-forge libsndfile
```

### Test Failures

**Low accuracy (<75%)**
1. Check if octave correction is enabled (Tasks 1.1-1.3 complete)
2. Verify custom prior distribution is being used
3. Check logs for BPM correction messages
4. Run individual sample tests to identify problematic BPMs

**Octave errors not corrected**
1. Verify `app/utils/bpm_validation.py` is working
2. Check BPM validation range (60-180 for loops)
3. Review logs for correction attempts
4. Test with different `max_iterations` in correction function

### Samples Sound Wrong

**Click tracks have no clicks**
- Verify WAV file size is >0 bytes
- Check sample rate is 44100 Hz
- Listen with audio player (VLC, QuickTime, etc.)
- Regenerate with `generate_test_samples.py`

**Musical samples sound odd**
- This is expected - they're synthesized, not real recordings
- They should still have clear beats for BPM detection
- If completely silent, regenerate samples

## Integration with CI/CD

These tests can be run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run BPM Accuracy Tests
  run: |
    pytest backend/tests/accuracy/test_bpm_accuracy_validation.py \
      --junit-xml=reports/accuracy-tests.xml
```

## Contributing

When adding new test samples:

1. Add sample configuration to `generate_test_samples.py`
2. Run script to generate samples
3. Verify ground truth BPM manually
4. Update this README with new BPM coverage
5. Run accuracy tests to ensure they pass

## References

- **Octave Correction Plan:** `dev/active/octave-correction/octave-correction-plan.md`
- **Audio Features Service:** `backend/app/services/audio_features_service.py`
- **BPM Validation:** `backend/app/utils/bpm_validation.py`
- **Essentia Analyzer:** `backend/app/services/essentia_analyzer.py` (if available)
