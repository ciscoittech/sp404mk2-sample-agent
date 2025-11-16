# Essentia Integration - Task Checklist

**Phase:** 2 of 5
**Total Hours:** 12 hours
**Timeline:** 1-2 weeks

---

## Task 2.1: Add Essentia to Requirements (1 hour)

**Goal:** Install Essentia and validate on all platforms

- [ ] **Add to requirements.txt**
  - [ ] Add `essentia` to `backend/requirements.txt`
  - [ ] Research version compatibility (Python 3.10, 3.11, 3.13)
  - [ ] Pin version if needed

- [ ] **Test macOS Installation**
  - [ ] Run `pip install essentia` on macOS
  - [ ] Verify with `python -c "import essentia; print(essentia.__version__)"`
  - [ ] Document any errors encountered
  - [ ] Test sample code (MonoLoader, RhythmExtractor2013)

- [ ] **Test Linux/Docker Installation**
  - [ ] Update Dockerfile with system dependencies
  - [ ] Add build-essential, libyaml-dev, libfftw3-dev
  - [ ] Add FFmpeg libraries (libavcodec-dev, libavformat-dev, libavutil-dev)
  - [ ] Add libsamplerate0-dev, libtag1-dev
  - [ ] Build Docker image and test installation
  - [ ] Verify Essentia imports correctly

- [ ] **Create Installation Documentation**
  - [ ] Create `docs/ESSENTIA_INSTALL.md`
  - [ ] Document macOS installation steps
  - [ ] Document Linux/Docker installation steps
  - [ ] List common errors and solutions
  - [ ] Add troubleshooting section

- [ ] **Add Optional Dependency Handling**
  - [ ] Create `ESSENTIA_AVAILABLE` flag
  - [ ] Add try/except for import
  - [ ] Test behavior when not installed

**Deliverables:**
- Essentia in requirements.txt
- Working installation on macOS and Docker
- ESSENTIA_INSTALL.md documentation
- Optional import handling

---

## Task 2.2: Implement EssentiaAnalyzer Class (4 hours)

**Goal:** Create service class for Essentia-based BPM analysis

- [ ] **Create Base Structure**
  - [ ] Create `backend/app/services/essentia_analyzer.py`
  - [ ] Add imports (essentia.standard)
  - [ ] Create `BPMResult` Pydantic model
  - [ ] Create `EssentiaAnalyzer` class skeleton
  - [ ] Add `__init__()` with availability check

- [ ] **Implement Audio Loading**
  - [ ] Implement `_load_audio()` method
  - [ ] Use MonoLoader with 44.1kHz sample rate
  - [ ] Add resampleQuality=4 for best quality
  - [ ] Add error handling for file loading
  - [ ] Test with various audio formats (WAV, MP3, FLAC)

- [ ] **Implement BPM Extraction**
  - [ ] Implement `analyze_bpm()` method
  - [ ] Initialize RhythmExtractor2013
  - [ ] Extract: (bpm, beats, confidence, estimates, intervals)
  - [ ] Calculate mean confidence from beat_confidence array
  - [ ] Return BPMResult with all data
  - [ ] Add comprehensive logging

- [ ] **Add Method Selection Logic**
  - [ ] Implement `get_recommended_method()`
  - [ ] Use 'multifeature' for samples <30s
  - [ ] Use 'degara' for samples >30s
  - [ ] Allow manual override via parameter
  - [ ] Document method differences

- [ ] **Error Handling & Logging**
  - [ ] Add try/except around audio loading
  - [ ] Add try/except around BPM extraction
  - [ ] Log BPM, confidence, method used
  - [ ] Return None on failure (graceful degradation)
  - [ ] Add debug-level logging for beat positions

- [ ] **Create Unit Tests**
  - [ ] Create `backend/tests/services/test_essentia_analyzer.py`
  - [ ] Test `_load_audio()` with fixtures
  - [ ] Test `analyze_bpm()` with known BPM sample
  - [ ] Test method selection logic
  - [ ] Test error handling (invalid file)
  - [ ] Add @pytest.mark.skipif for when Essentia unavailable

**Deliverables:**
- EssentiaAnalyzer class with BPM extraction
- BPMResult model
- Error handling and logging
- Unit tests passing

---

## Task 2.3: Download and Integrate Genre Models (2 hours)

**Goal:** Set up pre-trained genre classification models

- [ ] **Create Models Directory**
  - [ ] Create `backend/models/essentia/` directory
  - [ ] Add `.gitignore` for large model files
  - [ ] Add README with model info

- [ ] **Create Download Script**
  - [ ] Create `backend/scripts/download_essentia_models.py`
  - [ ] Add URLs for embedding model (discogs-maest-30s-pw-519l-2.pb)
  - [ ] Add URL for genre model (genre_discogs519-discogs-maest-30s-pw-519l-1.pb)
  - [ ] Implement download with progress bar
  - [ ] Add checksum verification (optional)
  - [ ] Skip download if files exist

- [ ] **Download Models Locally**
  - [ ] Run download script
  - [ ] Verify models downloaded (~150MB total)
  - [ ] Test loading models with TensorflowPredictMAEST
  - [ ] Verify TensorFlow compatibility

- [ ] **Create Genre Mapping Config**
  - [ ] Create `backend/config/genre_mapping.json`
  - [ ] Map Essentia genres to 10 SP-404 categories
  - [ ] Add confidence_threshold (0.15)
  - [ ] Add multi-label support rules
  - [ ] Document mapping rationale

- [ ] **Docker Integration**
  - [ ] Option 1: Copy models into Docker image
  - [ ] Option 2: Download at container startup
  - [ ] Update Dockerfile with model handling
  - [ ] Test Docker build with models
  - [ ] Document model size impact

- [ ] **Implement Lazy Loading**
  - [ ] Add `_genre_models` property to EssentiaAnalyzer
  - [ ] Implement `_load_genre_models()` method
  - [ ] Load only when `analyze_genre()` called
  - [ ] Cache loaded models
  - [ ] Add clear error if models missing

**Deliverables:**
- Models downloaded to backend/models/essentia/
- Download script working
- Genre mapping config created
- Docker integration complete
- Lazy loading implemented

---

## Task 2.4: Implement Genre Classification (3 hours)

**Goal:** Add genre classification with TensorFlow models

- [ ] **Create GenreResult Model**
  - [ ] Create `GenreResult` Pydantic model
  - [ ] Add fields: primary_genre, confidence, top_3_genres
  - [ ] Add sp404_category field
  - [ ] Add all_predictions dict (optional)

- [ ] **Implement Genre Analysis**
  - [ ] Add `analyze_genre()` method to EssentiaAnalyzer
  - [ ] Load audio at 16kHz (required by models)
  - [ ] Extract embeddings with TensorflowPredictMAEST
  - [ ] Predict genre with TensorflowPredict
  - [ ] Get top 3 predictions with probabilities

- [ ] **Add Genre Label Mapping**
  - [ ] Download genre labels metadata
  - [ ] Implement `_get_genre_label(index)` method
  - [ ] Map index → genre name
  - [ ] Test all 519 labels load correctly

- [ ] **Implement SP-404 Category Mapping**
  - [ ] Implement `_load_genre_mapping()` method
  - [ ] Implement `_map_to_sp404_category()` method
  - [ ] Match genre against category keywords
  - [ ] Return "Experimental" as default
  - [ ] Test mapping with various genres

- [ ] **Implement Full Analysis**
  - [ ] Implement `analyze_full()` method
  - [ ] Combine BPM + genre analysis
  - [ ] Return unified result dict
  - [ ] Add 'analyzer': 'essentia' metadata
  - [ ] Handle partial failures gracefully

- [ ] **Add Genre Tests**
  - [ ] Create genre test fixtures (hip-hop, house, jazz samples)
  - [ ] Test genre classification accuracy
  - [ ] Test SP-404 category mapping
  - [ ] Test top-3 predictions
  - [ ] Test full analysis workflow

**Deliverables:**
- Genre classification implemented
- GenreResult model
- SP-404 category mapping working
- Full analysis method
- Tests passing

---

## Task 2.5: Add Feature Flag System (1 hour)

**Goal:** Enable/disable Essentia with graceful fallback

- [ ] **Update Config Settings**
  - [ ] Add `USE_ESSENTIA: bool` to `backend/app/core/config.py`
  - [ ] Add `ESSENTIA_BPM_METHOD: str` (default: "multifeature")
  - [ ] Add `AUDIO_ANALYSIS_TIMEOUT: int` (default: 30)
  - [ ] Document new settings

- [ ] **Update .env.example**
  - [ ] Add `USE_ESSENTIA=true`
  - [ ] Add `ESSENTIA_BPM_METHOD=multifeature`
  - [ ] Add `AUDIO_ANALYSIS_TIMEOUT=30`
  - [ ] Add comments explaining options

- [ ] **Integrate with AudioFeaturesService**
  - [ ] Import EssentiaAnalyzer and ESSENTIA_AVAILABLE
  - [ ] Add analyzer selection in `__init__()`
  - [ ] Check `USE_ESSENTIA` and `ESSENTIA_AVAILABLE`
  - [ ] Initialize EssentiaAnalyzer if available
  - [ ] Set `self.analyzer_type` ("essentia" or "librosa")
  - [ ] Log which analyzer is active

- [ ] **Add Fallback Logic**
  - [ ] Update `analyze_file()` to try Essentia first
  - [ ] Catch exceptions and fall back to librosa
  - [ ] Log fallback events
  - [ ] Ensure no regression to existing librosa code

- [ ] **Add Runtime Availability Check**
  - [ ] Create `_check_essentia_available()` helper
  - [ ] Check if import succeeded
  - [ ] Check if models are downloaded
  - [ ] Return boolean availability status

**Deliverables:**
- Feature flag in config
- Environment variables updated
- AudioFeaturesService integration
- Fallback logic working
- Logging for analyzer selection

---

## Task 2.6: Update Tests (1 hour)

**Goal:** Comprehensive testing with CI/CD compatibility

- [ ] **Create Essentia Test Suite**
  - [ ] Update `test_essentia_analyzer.py`
  - [ ] Add `@pytest.mark.skipif(not ESSENTIA_AVAILABLE)`
  - [ ] Test BPM extraction
  - [ ] Test genre classification
  - [ ] Test full analysis
  - [ ] Test method selection logic

- [ ] **Create Test Fixtures**
  - [ ] Create `tests/fixtures/sample_90bpm.wav`
  - [ ] Create `tests/fixtures/sample_120bpm.wav`
  - [ ] Create `tests/fixtures/sample_kick.wav`
  - [ ] Create `tests/fixtures/test_dataset.json` with ground truth
  - [ ] Verify BPM with online tools

- [ ] **Add Integration Tests**
  - [ ] Test AudioFeaturesService with Essentia
  - [ ] Test fallback behavior
  - [ ] Test feature flag toggling
  - [ ] Test with/without models available

- [ ] **Add CI/CD Mocking**
  - [ ] Mock Essentia import for CI/CD
  - [ ] Test that librosa fallback works in CI
  - [ ] Ensure tests pass with and without Essentia
  - [ ] Document CI/CD strategy

- [ ] **Update Test Documentation**
  - [ ] Document test fixture requirements
  - [ ] Document how to run tests locally
  - [ ] Document CI/CD mocking approach
  - [ ] Add troubleshooting section

**Deliverables:**
- Comprehensive test suite
- Test fixtures created
- CI/CD compatibility
- Documentation updated
- All tests passing

---

## Validation Checklist

After completing all tasks:

- [ ] Essentia installs on macOS
- [ ] Essentia installs in Docker
- [ ] BPM detection works with test samples
- [ ] Genre classification works
- [ ] Confidence scores look reasonable
- [ ] Feature flag toggles correctly
- [ ] Fallback to librosa works
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for Phase 3

---

## Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| 2.1: Requirements | 1h | | |
| 2.2: EssentiaAnalyzer | 4h | | |
| 2.3: Genre Models | 2h | | |
| 2.4: Genre Classification | 3h | | |
| 2.5: Feature Flag | 1h | | |
| 2.6: Tests | 1h | | |
| **Total** | **12h** | | |

---

## Notes

- Start with Task 2.1 to verify installation works
- Task 2.2 can proceed with just BPM (no genre yet)
- Tasks 2.3 and 2.4 can be done together (genre)
- Task 2.5 is integration work (do last)
- Task 2.6 should be done incrementally with each task
