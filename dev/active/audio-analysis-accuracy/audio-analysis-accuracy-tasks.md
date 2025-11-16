# Audio Analysis Accuracy - Task Checklist

**Total Estimated Hours:** 32 hours
**Timeline:** 4-5 weeks at 8 hours/week

---

## Phase 1: BPM Validation & Octave Correction (8 hours)

**Goal:** Fix immediate octave error issues with current librosa implementation

- [ ] **[Task 1.1]** Implement `correct_octave_errors()` function (2 hours)
  - [ ] Create `backend/app/utils/bpm_validation.py`
  - [ ] Implement octave correction logic (2x, 3x, 1/2, 1/3 multipliers)
  - [ ] Make expected range configurable
  - [ ] Integrate with `AudioFeaturesService._extract_bpm()`
  - [ ] Add unit tests for octave correction

- [ ] **[Task 1.2]** Add sample type detection (1.5 hours)
  - [ ] Implement duration-based heuristic (< 1s = one-shot, > 1s = loop)
  - [ ] Add different validation ranges per type
  - [ ] Update `AudioFeatures` model with `sample_type` field
  - [ ] Create database migration
  - [ ] Add tests for sample type detection

- [ ] **[Task 1.3]** Improve librosa prior distribution (1.5 hours)
  - [ ] Research custom scipy.stats prior for 80-140 BPM range
  - [ ] Weight toward common hip-hop tempos (85, 90, 95, 105, 110, 115, 140, 170)
  - [ ] Integrate custom prior with `librosa.beat.beat_track()`
  - [ ] Test on existing samples
  - [ ] Document prior selection rationale

- [ ] **[Task 1.4]** Create test dataset with known BPMs (2 hours)
  - [ ] Collect 10 samples per BPM range (60-80, 80-100, 100-120, 120-140, 140-160, 160-180, 40-60, one-shots)
  - [ ] Verify BPM using online tools (Tunebat, DAW detection, manual tap)
  - [ ] Document ground truth in `tests/fixtures/test_dataset.json`
  - [ ] Write pytest tests for BPM accuracy
  - [ ] Set up continuous accuracy monitoring

- [ ] **[Task 1.5]** Add logging for debugging (1 hour)
  - [ ] Log raw BPM from librosa
  - [ ] Log corrected BPM after octave correction
  - [ ] Log confidence scores
  - [ ] Track correction frequency statistics
  - [ ] Add debug endpoint for analysis metadata

---

## Phase 2: Essentia Integration (12 hours)

**Goal:** Integrate Essentia for primary BPM and genre detection

- [ ] **[Task 2.1]** Add Essentia to requirements (1 hour)
  - [ ] Add essentia to `backend/requirements.txt`
  - [ ] Test installation on macOS
  - [ ] Test installation on Linux (Ubuntu/Debian)
  - [ ] Test installation in Docker
  - [ ] Document installation issues and workarounds
  - [ ] Add optional dependency flag for graceful degradation

- [ ] **[Task 2.2]** Implement `EssentiaAnalyzer` class (4 hours)
  - [ ] Create `backend/app/services/essentia_analyzer.py`
  - [ ] Implement BPM extraction using `RhythmExtractor2013`
  - [ ] Add multi-feature vs degara algorithm selection
  - [ ] Extract confidence scores from beat analysis
  - [ ] Extract beat positions and intervals
  - [ ] Add error handling and logging
  - [ ] Write unit tests for EssentiaAnalyzer

- [ ] **[Task 2.3]** Download and integrate genre models (2 hours)
  - [ ] Download Discogs-MAEST embedding model
  - [ ] Download genre classification model (519 labels)
  - [ ] Test TensorFlow compatibility (version check)
  - [ ] Create genre mapping to SP-404 categories
  - [ ] Add models to Docker image (or lazy download)
  - [ ] Document model sources and licenses

- [ ] **[Task 2.4]** Implement genre classification (3 hours)
  - [ ] Implement embedding extraction with TensorflowPredictMAEST
  - [ ] Implement genre prediction with TensorflowPredict
  - [ ] Extract top-3 genre predictions with probabilities
  - [ ] Map Essentia genres to SP-404 categories
  - [ ] Calculate genre confidence scores
  - [ ] Add genre to AudioFeatures model
  - [ ] Write tests for genre classification

- [ ] **[Task 2.5]** Add feature flag system (1 hour)
  - [ ] Add `USE_ESSENTIA` config variable to `backend/app/core/config.py`
  - [ ] Implement graceful degradation if Essentia unavailable
  - [ ] Log which analyzer is active (Essentia vs Librosa)
  - [ ] Add runtime check for Essentia availability
  - [ ] Document feature flag usage

- [ ] **[Task 2.6]** Update tests (1 hour)
  - [ ] Test Essentia analyzer separately
  - [ ] Mock Essentia for CI/CD if installation fails
  - [ ] Add integration tests for Essentia workflow
  - [ ] Update existing tests to handle both analyzers
  - [ ] Document testing strategy

---

## Phase 3: Cross-Validation Logic (6 hours)

**Goal:** Combine multiple libraries for consensus-based BPM detection

- [ ] **[Task 3.1]** Implement consensus algorithm (2 hours)
  - [ ] Create `backend/app/services/consensus_engine.py`
  - [ ] Implement weighted average based on confidence
  - [ ] Add outlier detection (remove estimates >10 BPM from median)
  - [ ] Implement fallback to highest-confidence single estimate
  - [ ] Handle cases with only one valid estimate
  - [ ] Write unit tests for consensus logic

- [ ] **[Task 3.2]** Create unified confidence scoring (2 hours)
  - [ ] Map Essentia confidence (0.0-1.0) to 0-100 scale
  - [ ] Map Librosa confidence (derived) to 0-100 scale
  - [ ] Map Madmom confidence (optional) to 0-100 scale
  - [ ] Implement agreement bonus (multiple algorithms within ±2 BPM → +10-20 points)
  - [ ] Implement variance penalty (high disagreement → lower confidence)
  - [ ] Calibrate confidence scoring with test dataset
  - [ ] Write tests for confidence scoring

- [ ] **[Task 3.3]** Refactor `AudioFeaturesService` (2 hours)
  - [ ] Orchestrate multiple analyzers (Essentia, Librosa, Madmom)
  - [ ] Implement parallel execution with `asyncio.gather()`
  - [ ] Store all estimates in `analysis_metadata` JSON field
  - [ ] Update API to return confidence scores
  - [ ] Add debug endpoint for multi-algorithm results
  - [ ] Write integration tests for orchestration

---

## Phase 4: Genre Classification Enhancement (4 hours)

**Goal:** Improve genre classification with fallback strategies

- [ ] **[Task 4.1]** Implement fallback classifier (2 hours)
  - [ ] Create `backend/app/services/genre_classifier.py`
  - [ ] Train Random Forest on MFCC + chroma + spectral features
  - [ ] Use manually labeled samples from existing database
  - [ ] Support 5-10 primary genres for SP-404MK2
  - [ ] Save/load trained model
  - [ ] Write tests for fallback classifier

- [ ] **[Task 4.2]** Create genre taxonomy (1 hour)
  - [ ] Create `backend/config/genre_mapping.json`
  - [ ] Map 87 Essentia classes → 10 SP-404 categories
  - [ ] Define confidence thresholds for multi-label (e.g., >0.15 → add as tag)
  - [ ] Document genre mapping rationale
  - [ ] Add tests for genre mapping

- [ ] **[Task 4.3]** Add genre to database schema (1 hour)
  - [ ] Update `Sample` model with `primary_genre` field
  - [ ] Add `genre_tags` array field for multi-label
  - [ ] Add `genre_confidence` field
  - [ ] Create migration script for existing samples
  - [ ] Add API endpoints for genre filtering
  - [ ] Update frontend to display genre tags

---

## Phase 5: Confidence Scoring & Metadata (2 hours)

**Goal:** Add comprehensive confidence tracking and metadata

- [ ] **[Task 5.1]** Update AudioFeatures model (1 hour)
  - [ ] Add `bpm_confidence` field (0-100)
  - [ ] Add `genre_confidence` field (0-100)
  - [ ] Add `analysis_metadata` JSON field
  - [ ] Store all algorithm estimates in metadata
  - [ ] Create database migration
  - [ ] Update serializers/schemas

- [ ] **[Task 5.2]** Update API responses (1 hour)
  - [ ] Include confidence scores in JSON responses
  - [ ] Add `/samples/{id}/analysis-debug` endpoint for full metadata
  - [ ] Update frontend to show confidence indicators
  - [ ] Add visual warning for low-confidence predictions (<50)
  - [ ] Add manual override UI for corrections
  - [ ] Document API changes

---

## Testing & Validation

- [ ] Run full pytest suite after each phase
- [ ] Benchmark BPM accuracy on test dataset
- [ ] Validate performance hasn't degraded >20%
- [ ] Test with 100+ samples for regression
- [ ] Update documentation with results

---

## Documentation

- [ ] Update CHANGELOG.md with feature details
- [ ] Document Essentia installation process
- [ ] Add accuracy benchmarks to README
- [ ] Create user guide for confidence scores
- [ ] Document manual override workflow

---

## Completion Checklist

- [ ] All 20 tasks completed
- [ ] BPM accuracy ≥95% on test dataset
- [ ] Genre accuracy ≥80% on test dataset
- [ ] Performance <8 seconds per sample
- [ ] Confidence scoring calibrated
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Feature deployed to production
