# Essentia Integration - Context

**Feature:** Integrate Essentia library for high-accuracy audio analysis
**Phase:** 2 of 5
**Status:** Ready to Implement
**Created:** 2025-11-15
**Last Updated:** 2025-11-15

---

## Why Essentia?

### Current Problem
- Librosa BPM detection: ~60-70% accuracy
- Octave errors common (26 BPM, 225 BPM)
- No built-in genre classification
- Simple onset detection algorithm

### Essentia Benefits
- **90-95% BPM accuracy** (commercial-grade)
- **Built-in confidence scores** for beat detection
- **Pre-trained genre models** (87 classes, 519 Discogs styles)
- **Active development** by Music Technology Group (UPF)
- **Production-ready** (used by Spotify, SoundCloud)

---

## Key Decisions

### 1. Essentia as Primary, Librosa as Fallback
**Decision:** Use Essentia for analysis, fall back to librosa if unavailable
**Rationale:**
- Best accuracy from Essentia
- Librosa already working (no regression risk)
- Graceful degradation if installation fails

### 2. RhythmExtractor2013 Algorithm
**Decision:** Use `RhythmExtractor2013` with multifeature method
**Rationale:**
- State-of-the-art accuracy (as of 2013, still excellent in 2025)
- Provides confidence scores
- Two methods available:
  - `multifeature`: More accurate, slower (for <30s samples)
  - `degara`: Faster, slightly less accurate (for >30s samples)

### 3. Genre Models via TensorFlow
**Decision:** Use Discogs-MAEST pre-trained models
**Rationale:**
- 519 style labels from Discogs dataset
- 80-85% accuracy on genre classification
- Pre-trained (no need to train our own)
- Lazy loading (only load when needed)

### 4. Feature Flag System
**Decision:** `USE_ESSENTIA` config variable with auto-fallback
**Rationale:**
- Easy to disable if issues arise
- CI/CD can run without Essentia
- Users can choose librosa-only mode for speed

---

## Architecture Notes

### Installation Strategy

**macOS:**
```bash
pip install essentia
```

**Docker (Ubuntu):**
```dockerfile
RUN apt-get install -y \
    build-essential \
    libyaml-dev \
    libfftw3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libsamplerate0-dev \
    libtag1-dev
RUN pip install essentia
```

### Service Architecture

```
AudioFeaturesService (orchestrator)
    ↓
    ├─ If USE_ESSENTIA=true and available
    │   └─ EssentiaAnalyzer
    │       ├─ analyze_bpm() → RhythmExtractor2013
    │       ├─ analyze_genre() → TensorFlow models
    │       └─ analyze_full() → Combined
    │
    └─ If USE_ESSENTIA=false or unavailable
        └─ LibrosaAnalyzer (existing)
```

### Genre Model Pipeline

```
Audio File (16kHz) → TensorflowPredictMAEST → Embeddings
                                                    ↓
                                          TensorflowPredict → Genre Predictions
                                                    ↓
                                          Map to SP-404 Categories
```

---

## Key Files

### Files to Create
- `backend/app/services/essentia_analyzer.py` - Main Essentia service
- `backend/scripts/download_essentia_models.py` - Model downloader
- `backend/config/genre_mapping.json` - Essentia → SP-404 mapping
- `backend/tests/services/test_essentia_analyzer.py` - Tests
- `docs/ESSENTIA_INSTALL.md` - Installation guide

### Files to Modify
- `backend/requirements.txt` - Add essentia dependency
- `backend/app/core/config.py` - Add USE_ESSENTIA flag
- `backend/app/services/audio_features_service.py` - Integrate Essentia
- `docker-compose.yml` - Add build dependencies
- `Dockerfile` - Add Essentia installation

### Models Directory
```
backend/models/essentia/
├── discogs-maest-30s-pw-519l-2.pb          (~100MB)
└── genre_discogs519-discogs-maest-30s-pw-519l-1.pb  (~50MB)
```

---

## Dependencies

### Python Packages
- **essentia** - Audio analysis library
- **tensorflow** - Required for genre models (already in requirements)
- **numpy** - Already installed

### System Libraries (Linux/Docker)
- build-essential
- libyaml-dev
- libfftw3-dev
- libavcodec-dev (FFmpeg)
- libavformat-dev
- libavutil-dev
- libsamplerate0-dev
- libtag1-dev

### Models
- Discogs-MAEST embedding model
- Genre classification model (519 labels)
- Source: https://essentia.upf.edu/models.html

---

## Testing Strategy

### Test Fixtures Needed
Create `tests/fixtures/` with:
- `sample_90bpm.wav` - Known 90 BPM hip-hop loop
- `sample_120bpm.wav` - Known 120 BPM house loop
- `sample_kick.wav` - One-shot kick drum
- `test_dataset.json` - Ground truth labels

### Test Cases
1. **BPM Detection:**
   - Test with known BPM samples
   - Validate confidence scores (0.0-1.0)
   - Check beat positions

2. **Genre Classification:**
   - Test with labeled samples
   - Validate top-3 predictions
   - Check SP-404 category mapping

3. **Fallback Behavior:**
   - Mock Essentia as unavailable
   - Verify librosa fallback works
   - Check logging messages

4. **Feature Flag:**
   - Test USE_ESSENTIA=true
   - Test USE_ESSENTIA=false
   - Verify correct analyzer selected

---

## Implementation Order

### Task Sequence
1. **Task 2.1** - Install Essentia (1h)
   - Get it working on local machine
   - Document any issues

2. **Task 2.2** - Implement EssentiaAnalyzer (4h)
   - Start with BPM only
   - Add tests incrementally

3. **Task 2.3** - Download Models (2h)
   - Get models working locally
   - Add to Docker

4. **Task 2.4** - Genre Classification (3h)
   - Implement with TensorFlow
   - Map to SP-404 categories

5. **Task 2.5** - Feature Flag (1h)
   - Add config
   - Integrate with AudioFeaturesService

6. **Task 2.6** - Tests (1h)
   - Write comprehensive tests
   - Set up CI/CD mocking

---

## Configuration

### Environment Variables
```bash
# .env

# Essentia settings
USE_ESSENTIA=true
ESSENTIA_BPM_METHOD=multifeature  # or 'degara'
AUDIO_ANALYSIS_TIMEOUT=30

# Model paths
ESSENTIA_MODELS_DIR=backend/models/essentia
```

### Genre Mapping Preview
```json
{
  "sp404_categories": {
    "Hip-Hop/Trap": ["hip-hop", "trap", "boom bap", "lo-fi"],
    "Electronic": ["house", "techno", "drum and bass", "dubstep"],
    "Jazz/Soul": ["jazz", "soul", "funk", "r&b"],
    ...
  },
  "confidence_threshold": 0.15
}
```

---

## Risks & Mitigations

### Risk 1: Essentia Installation Complexity
**Impact:** High (blocks entire phase)
**Mitigation:**
- Start with local installation first
- Document all errors encountered
- Prepare Docker image with Essentia pre-installed
- Have librosa fallback ready

### Risk 2: Model Download Issues
**Impact:** Medium (blocks genre classification)
**Mitigation:**
- Manual download as backup
- Host models on project storage
- Make genre classification optional

### Risk 3: TensorFlow Version Conflicts
**Impact:** Medium (genre models won't load)
**Mitigation:**
- Pin TensorFlow version
- Test on multiple Python versions
- Provide alternative genre classification (Phase 4)

---

## Success Metrics

### BPM Accuracy
- **Target:** 90%+ within ±2 BPM
- **Test Dataset:** 10 samples with verified BPM
- **Current Baseline:** 60-70% (librosa)

### Genre Accuracy
- **Target:** 80%+ correct primary genre
- **Test Dataset:** 20 samples with manual labels
- **Current Baseline:** N/A (not implemented)

### Performance
- **Target:** <8 seconds per sample
- **Current:** 3-5 seconds (librosa)
- **Acceptable:** 8-10 seconds (Essentia is slower)

### Reliability
- **Target:** Fallback to librosa works 100% of the time
- **Test:** Mock Essentia failures
- **Logging:** Clear indication of which analyzer used

---

## Next Steps After Completion

1. **Validate Accuracy:**
   - Test on 100+ samples
   - Compare Essentia vs Librosa results
   - Document accuracy improvements

2. **Move to Phase 3:**
   - Implement cross-validation (Essentia + Librosa consensus)
   - Add weighted averaging
   - Unified confidence scoring (0-100)

3. **Move to Phase 5:**
   - Add confidence fields to database
   - Update API responses
   - Add UI indicators

---

## Notes

- Essentia sample rate for genre models is **16kHz** (different from BPM at 44.1kHz)
- Genre models expect 30-second audio clips (will truncate or pad)
- RhythmExtractor2013 returns multiple outputs: (bpm, beats, confidence, estimates, intervals)
- Lazy loading of genre models saves memory if only BPM needed
- Feature flag allows A/B testing Essentia vs Librosa

---

## Resources

- **Essentia Docs:** https://essentia.upf.edu/
- **Model Downloads:** https://essentia.upf.edu/models.html
- **RhythmExtractor2013:** https://essentia.upf.edu/reference/std_RhythmExtractor2013.html
- **TensorFlow Models:** https://essentia.upf.edu/machine_learning.html
