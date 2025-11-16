# AUDIO ANALYSIS ACCURACY IMPROVEMENT PLAN

## EXECUTIVE SUMMARY

The current audio analysis system uses librosa's default `beat_track()` method, which is susceptible to octave errors (detecting BPM at half/double the actual tempo) and lacks validation logic. This plan proposes a **multi-library cross-validation approach** combining librosa, madmom, and essentia to achieve 95%+ BPM accuracy and 80%+ genre classification accuracy.

**Timeline Estimate:** 32-40 hours (4-5 weeks at 8 hours/week)
**Success Metrics:**
- BPM accuracy: 95%+ within ±2 BPM on test dataset
- Genre classification: 80%+ correct on known samples
- Performance: <8 seconds per sample (current: 3-5 seconds)
- Confidence scoring: 0-100 scale for all predictions

---

## RESEARCH FINDINGS

### Better Python Libraries

#### **1. Librosa (Current)**
**Pros:**
- Already integrated and well-documented
- Comprehensive feature extraction (spectral, MFCC, chroma)
- Async-friendly (pure Python/NumPy)
- Strong community support

**Cons:**
- BPM detection prone to octave errors (26 BPM → should be 104 BPM)
- Default `beat_track()` uses simple onset detection
- No built-in genre classification models
- Wide BPM validation range (20-300) catches invalid results but doesn't correct them

**Current Accuracy:** ~60-70% BPM accuracy (based on octave error prevalence)

#### **2. Madmom**
**Pros:**
- State-of-the-art beat tracking algorithms (RNN-based)
- Multiple tempo estimation methods (TempoEstimationProcessor)
- Designed specifically for MIR (Music Information Retrieval)
- Actively used in 2025 research

**Cons:**
- Known rounding issues (124 BPM → 125 BPM)
- Slower than librosa (ML-based algorithms)
- Less comprehensive feature extraction
- Primarily focused on rhythm/beat tracking

**Expected Accuracy:** 85-90% BPM accuracy with octave correction

#### **3. Essentia**
**Pros:**
- **Commercial-grade accuracy** (built by UPF/Music Technology Group)
- `RhythmExtractor2013` with confidence scores
- **Pre-trained genre classification models** (87 classes, 519 styles from Discogs)
- Multi-feature and fast (degara) algorithms
- Beat position + confidence + intervals
- Comprehensive extractor (`essentia_streaming_extractor_music`)

**Cons:**
- C++ library with Python bindings (installation complexity)
- Larger dependency footprint
- May require TensorFlow for genre models

**Expected Accuracy:** 90-95% BPM accuracy, 80-85% genre classification

#### **4. Aubio**
**Pros:**
- Lightweight and fast
- Simple Python interface
- Good for real-time applications
- Command-line tools available

**Cons:**
- Known octave preference (prefers ~107 BPM)
- BPM may be half/double of real value
- Limited feature extraction vs librosa
- Less accurate than madmom/essentia

**Expected Accuracy:** 70-75% BPM accuracy

### **Recommendation: Essentia (Primary) + Librosa (Fallback)**

**Rationale:**
1. **Essentia** provides the highest accuracy for both BPM and genre classification
2. **Librosa** remains valuable for:
   - Feature extraction (spectral, MFCC, chroma) - already working well
   - Fallback when Essentia installation fails
   - Cross-validation to increase confidence
3. **Madmom** optional for future enhancement if Essentia underperforms

---

### BPM Detection Improvements

#### **1. Octave Error Detection & Correction**
**Problem:** librosa often returns 26 BPM when actual is 104 BPM, or 225 BPM when actual is 112.5 BPM.

**Solution:** Implement octave correction logic:
```python
def correct_octave_errors(bpm: float, expected_range: tuple = (60, 180)) -> float:
    """Correct common octave errors in BPM detection."""
    min_bpm, max_bpm = expected_range

    # If too low, try doubling up to 3 times
    corrected = bpm
    while corrected < min_bpm and corrected * 2 <= max_bpm:
        corrected *= 2

    # If too high, try halving up to 3 times
    while corrected > max_bpm and corrected / 2 >= min_bpm:
        corrected /= 2

    return corrected
```

#### **2. Multi-Algorithm Consensus**
Use multiple libraries and take weighted average or majority vote:
- Essentia RhythmExtractor2013 (multifeature) - **weight: 0.5**
- Librosa beat_track with custom prior - **weight: 0.3**
- Madmom TempoEstimationProcessor (optional) - **weight: 0.2**

**Consensus Logic:**
```python
def consensus_bpm(estimates: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Calculate consensus BPM from multiple estimates.

    Args:
        estimates: List of (bpm, confidence) tuples

    Returns:
        (consensus_bpm, consensus_confidence)
    """
    # Filter out None values
    valid = [(bpm, conf) for bpm, conf in estimates if bpm is not None]

    if not valid:
        return None, 0.0

    # Weighted average
    total_weight = sum(conf for _, conf in valid)
    weighted_bpm = sum(bpm * conf for bpm, conf in valid) / total_weight

    # Confidence is average of individual confidences
    avg_confidence = total_weight / len(valid)

    return weighted_bpm, avg_confidence
```

#### **3. Confidence Scoring**
Each library provides confidence differently:
- **Essentia:** `beats_confidence` array (0.0-1.0)
- **Librosa:** Derive from beat strength correlation
- **Madmom:** Model-based probability

**Unified Confidence (0-100):**
- **90-100:** Multiple algorithms agree within ±2 BPM
- **70-89:** 2+ algorithms agree within ±5 BPM
- **50-69:** Single algorithm with high internal confidence
- **0-49:** High variance between algorithms or low internal confidence

#### **4. Preprocessing Techniques**
- **Pre-emphasis filtering:** Boost high frequencies for better onset detection
- **Normalization:** Ensure consistent amplitude across samples
- **Sample rate standardization:** Resample to 44.1kHz or 48kHz
- **Mono conversion:** Already implemented correctly

---

### Genre Classification Improvements

#### **Current Approach: None**
The system currently only extracts features (MFCC, chroma, spectral) but doesn't classify genre.

#### **Proposed Approach: Essentia Pre-trained Models**

**1. Essentia TensorFlow Models**
```python
from essentia.standard import (
    MonoLoader,
    TensorflowPredictMAEST,
    TensorflowPredict
)

# Load audio
audio = MonoLoader(filename=file_path, sampleRate=16000, resampleQuality=4)()

# Extract embeddings
embedding_model = TensorflowPredictMAEST(
    graphFilename="discogs-maest-30s-pw-519l-2.pb",
    output="PartitionedCall/Identity_12"
)
embeddings = embedding_model(audio)

# Classify genre
genre_model = TensorflowPredict(
    graphFilename="genre_discogs519-discogs-maest-30s-pw-519l-1.pb",
    inputs=["embeddings"],
    outputs=["PartitionedCall/Identity_1"]
)
predictions = genre_model({"embeddings": embeddings})
```

**2. Genre Mapping for SP-404MK2**
Map 87 Essentia classes to SP-404MK2 production genres:
- **Hip-Hop/Trap** ← hip-hop, trap, boom bap, lo-fi
- **Electronic** ← house, techno, drum and bass, dubstep
- **Jazz/Soul** ← jazz, soul, funk, r&b
- **Vintage/Retro** ← disco, 70s, 80s, oldies
- **Breaks/Drums** ← breakbeat, drum breaks

**3. Feature Engineering (Fallback)**
If Essentia models unavailable, use supervised learning on extracted features:
```python
from sklearn.ensemble import RandomForestClassifier

# Features: MFCC (13) + Chroma (12) + Spectral (4) + Temporal (3)
features = np.concatenate([
    mfcc_mean,
    chroma_mean,
    [spectral_centroid, spectral_rolloff, spectral_bandwidth, spectral_flatness],
    [zero_crossing_rate, rms_energy, harmonic_ratio]
])

# Train on GTZAN dataset or manually labeled samples
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
```

**Expected Accuracy:**
- **Essentia models:** 80-85%
- **Random Forest on features:** 65-70%

---

## CURRENT IMPLEMENTATION ANALYSIS

### File: `backend/app/services/audio_features_service.py`

#### **BPM Detection (Lines 174-191)**
```python
def _extract_bpm(self, y: np.ndarray, sr: int) -> Optional[float]:
    try:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        # ... handle array vs scalar

        # Validate BPM range
        if tempo and 20 <= tempo <= 300:
            return tempo
        return None
```

**Identified Weaknesses:**
1. **No octave correction:** Accepts 26 BPM without trying 52, 104, 208
2. **Default prior:** Uses librosa's default log-normal prior centered at ~120 BPM
3. **No confidence scoring:** Returns BPM or None, no indication of reliability
4. **Wide validation:** 20-300 BPM too permissive (should be 60-180 for most loops)
5. **Single algorithm:** No cross-validation with other libraries

#### **Key Detection (Lines 193-235)**
Uses chroma features with correlation to major/minor profiles. **This approach is acceptable** but could benefit from Essentia's key detection models.

**Weakness:** Simple heuristic vs. ML-based approach

#### **Genre Classification: Missing**
No genre classification implemented. Only feature extraction.

#### **Preprocessing: Adequate**
- Mono conversion: ✅ Correct (line 120)
- Sample rate handling: ✅ Uses native sample rate (sr=None)
- Stereo handling: ✅ Properly converts to mono

**Missing:**
- Pre-emphasis filtering
- Amplitude normalization
- Duration-based algorithm selection (different approaches for one-shots vs loops)

---

## ARCHITECTURE DESIGN

### Multi-Library Cross-Validation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     Audio File Input                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Preprocessing Layer                             │
│  • Normalize amplitude                                       │
│  • Convert to mono (if stereo)                              │
│  • Resample to 44.1kHz (if needed)                          │
│  • Pre-emphasis filter (optional)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┬──────────────┐
        ▼                           ▼              ▼
┌──────────────┐          ┌──────────────┐  ┌──────────────┐
│   Essentia   │          │   Librosa    │  │   Madmom     │
│  (Primary)   │          │  (Fallback)  │  │  (Optional)  │
├──────────────┤          ├──────────────┤  ├──────────────┤
│ BPM: 104.5   │          │ BPM: 26.0 →  │  │ BPM: 105.0   │
│ Conf: 0.92   │          │ Corrected:   │  │ Conf: 0.88   │
│              │          │ 104.0        │  │              │
│              │          │ Conf: 0.65   │  │              │
└──────┬───────┘          └──────┬───────┘  └──────┬───────┘
       │                         │                  │
       └─────────────┬───────────┴──────────────────┘
                     ▼
         ┌───────────────────────┐
         │  Consensus Algorithm  │
         │  • Weighted average   │
         │  • Outlier detection  │
         │  • Confidence score   │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  BPM Validation       │
         │  • Octave correction  │
         │  • Range check        │
         │  • Sanity tests       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  Final BPM: 104.5     │
         │  Confidence: 87/100   │
         └───────────────────────┘
```

### BPM Validation Pipeline

```
Input BPM → Octave Correction → Range Validation → Consensus
                                                         │
    ┌────────────────────────────────────────────────────┘
    ▼
Is confidence > 70?
    │
    ├─ Yes → Return BPM + Confidence
    │
    └─ No → Flag for Manual Review
              (store multiple estimates)
```

### Genre Classification Pipeline

```
Audio Features → Essentia Embeddings → TensorFlow Model → Genre Predictions
                                                                  │
                                                                  ▼
                                                    ┌─────────────────────────┐
                                                    │ Top 3 Genres:           │
                                                    │ 1. Hip-Hop (0.72)       │
                                                    │ 2. Boom Bap (0.18)      │
                                                    │ 3. Lo-Fi (0.06)         │
                                                    └────────┬────────────────┘
                                                             │
                                                             ▼
                                                    Map to SP-404 Categories
                                                             │
                                                             ▼
                                                    Primary: "Hip-Hop/Trap"
                                                    Confidence: 72/100
```

---

## PHASE BREAKDOWN

### Phase 1: BPM Validation & Octave Correction (8 hours)

**Goal:** Fix immediate octave error issues with current librosa implementation

**Deliverables:**
1. Octave error detection and correction function
2. Tighter BPM range validation (60-180 for loops, 40-200 for general)
3. Sample type detection (one-shot vs loop)
4. Unit tests with known BPM samples

**Tasks:**
1. **[Task 1.1]** Implement `correct_octave_errors()` function (2 hours)
   - Handle 2x, 3x, 1/2, 1/3 multipliers
   - Configurable expected range
   - Integration with `_extract_bpm()`

2. **[Task 1.2]** Add sample type detection (1.5 hours)
   - Duration-based heuristic (< 1s = one-shot, > 1s = loop)
   - Different validation ranges per type
   - Update AudioFeatures model with `sample_type` field

3. **[Task 1.3]** Improve librosa prior distribution (1.5 hours)
   - Custom scipy.stats prior for 80-140 BPM range
   - Weighted toward common hip-hop tempos (85, 90, 95, 105, 110, 115, 140, 170)

4. **[Task 1.4]** Create test dataset with known BPMs (2 hours)
   - 10 samples with verified BPM (use online tools)
   - Document ground truth in JSON
   - Write pytest tests for accuracy

5. **[Task 1.5]** Add logging for debugging (1 hour)
   - Log raw BPM, corrected BPM, confidence
   - Track correction frequency

---

### Phase 2: Essentia Integration (12 hours)

**Goal:** Integrate Essentia for primary BPM and genre detection

**Deliverables:**
1. Essentia installation and dependency management
2. `EssentiaAnalyzer` service class
3. BPM extraction with confidence scores
4. Genre classification with pre-trained models
5. Graceful fallback to librosa if unavailable

**Tasks:**
1. **[Task 2.1]** Add Essentia to requirements (1 hour)
   - Test installation on macOS, Linux, Docker
   - Document installation issues
   - Add optional dependency flag

2. **[Task 2.2]** Implement `EssentiaAnalyzer` class (4 hours)
   - BPM extraction using `RhythmExtractor2013`
   - Multi-feature vs degara algorithm selection
   - Confidence score extraction
   - Beat positions and intervals

3. **[Task 2.3]** Download and integrate genre models (2 hours)
   - Download Discogs-MAEST models
   - Test TensorFlow compatibility
   - Create genre mapping to SP-404 categories
   - Add to Docker image

4. **[Task 2.4]** Implement genre classification (3 hours)
   - Embedding extraction
   - Top-3 genre predictions
   - Map to SP-404 categories (Hip-Hop, Electronic, Jazz, etc.)
   - Confidence scores

5. **[Task 2.5]** Add feature flag system (1 hour)
   - `USE_ESSENTIA` config variable
   - Graceful degradation if unavailable
   - Log which analyzer is active

6. **[Task 2.6]** Update tests (1 hour)
   - Test Essentia analyzer separately
   - Mock Essentia for CI/CD if needed

---

### Phase 3: Cross-Validation Logic (6 hours)

**Goal:** Combine multiple libraries for consensus-based BPM detection

**Deliverables:**
1. Multi-algorithm BPM estimation
2. Weighted consensus calculation
3. Outlier detection
4. Unified confidence scoring (0-100)

**Tasks:**
1. **[Task 3.1]** Implement consensus algorithm (2 hours)
   - Weighted average based on confidence
   - Outlier detection (remove estimates >10 BPM from median)
   - Fallback to highest-confidence single estimate

2. **[Task 3.2]** Create unified confidence scoring (2 hours)
   - Map library-specific confidences to 0-100 scale
   - Agreement bonus (multiple algorithms within ±2 BPM)
   - Penalty for high variance

3. **[Task 3.3]** Refactor `AudioFeaturesService` (2 hours)
   - Orchestrate multiple analyzers
   - Parallel execution (asyncio.gather)
   - Store all estimates in metadata for debugging

---

### Phase 4: Genre Classification Enhancement (4 hours)

**Goal:** Improve genre classification with fallback strategies

**Deliverables:**
1. Primary: Essentia TensorFlow models
2. Fallback: Feature-based classification
3. SP-404 genre mapping
4. Multi-label support (tags)

**Tasks:**
1. **[Task 4.1]** Implement fallback classifier (2 hours)
   - Train Random Forest on MFCC + chroma + spectral features
   - Use manually labeled samples from existing database
   - 5-10 primary genres for SP-404MK2

2. **[Task 4.2]** Create genre taxonomy (1 hour)
   - Map 87 Essentia classes → 10 SP-404 categories
   - Define confidence thresholds for multi-label
   - Create JSON mapping file

3. **[Task 4.3]** Add genre to database schema (1 hour)
   - Update Sample model with genre fields
   - Migration script for existing samples
   - API endpoints for genre filtering

---

### Phase 5: Confidence Scoring & Metadata (2 hours)

**Goal:** Add comprehensive confidence tracking and metadata

**Deliverables:**
1. Confidence scores for all predictions
2. Debug metadata (all algorithm estimates)
3. API fields for confidence display
4. UI indicators for low-confidence predictions

**Tasks:**
1. **[Task 5.1]** Update AudioFeatures model (1 hour)
   - Add `bpm_confidence` field
   - Add `genre_confidence` field
   - Add `analysis_metadata` JSON field
   - Store all algorithm estimates

2. **[Task 5.2]** Update API responses (1 hour)
   - Include confidence scores in JSON
   - Add `/samples/{id}/analysis-debug` endpoint
   - Update frontend to show confidence indicators

---

## COMPLETE TASK LIST

### Phase 1: BPM Validation & Octave Correction (8 hours)
- [1.1] Implement octave correction function (2h)
- [1.2] Add sample type detection (1.5h)
- [1.3] Improve librosa prior distribution (1.5h)
- [1.4] Create test dataset with known BPMs (2h)
- [1.5] Add BPM debugging logs (1h)

### Phase 2: Essentia Integration (12 hours)
- [2.1] Add Essentia dependencies (1h)
- [2.2] Implement EssentiaAnalyzer class (4h)
- [2.3] Download and integrate genre models (2h)
- [2.4] Implement genre classification (3h)
- [2.5] Add feature flag system (1h)
- [2.6] Update tests for Essentia (1h)

### Phase 3: Cross-Validation Logic (6 hours)
- [3.1] Implement consensus algorithm (2h)
- [3.2] Create unified confidence scoring (2h)
- [3.3] Refactor AudioFeaturesService orchestration (2h)

### Phase 4: Genre Classification Enhancement (4 hours)
- [4.1] Implement fallback Random Forest classifier (2h)
- [4.2] Create genre taxonomy mapping (1h)
- [4.3] Add genre to database schema (1h)

### Phase 5: Confidence Scoring & Metadata (2 hours)
- [5.1] Update AudioFeatures model with confidence fields (1h)
- [5.2] Update API responses and UI (1h)

---

## RISK ANALYSIS

### Risk 1: Essentia Installation Complexity
**Description:** Essentia is a C++ library with Python bindings, may have platform-specific build issues
**Probability:** Medium (40%)
**Impact:** High (blocks Phase 2-4)
**Mitigation:**
- Test installation early on macOS, Linux, Docker
- Provide pre-built Docker images with Essentia
- Document fallback to librosa-only mode
- Consider using Essentia.js via subprocess if Python bindings fail

### Risk 2: TensorFlow Model Size
**Description:** Genre classification models may be large (100MB+), affecting Docker image size and startup time
**Probability:** High (70%)
**Impact:** Medium (slower builds, larger storage)
**Mitigation:**
- Lazy-load models only when genre classification requested
- Provide "lite" mode without genre models
- Cache models in shared volume for Docker
- Optional download during first run

### Risk 3: Performance Degradation
**Description:** Running 2-3 algorithms may increase analysis time from 3-5s to 10-15s
**Probability:** Medium (50%)
**Impact:** Medium (slower batch processing)
**Mitigation:**
- Parallel execution using asyncio.gather()
- Cache results to avoid re-analysis
- Provide "fast mode" (librosa-only) vs "accurate mode" (multi-library)
- User preference for speed vs accuracy

### Risk 4: Algorithm Disagreement
**Description:** Different libraries may give vastly different BPM estimates, making consensus difficult
**Probability:** Medium (40%)
**Impact:** Medium (low confidence scores, user confusion)
**Mitigation:**
- Store all estimates in metadata for user review
- Flag high-variance results for manual verification
- Allow manual BPM override and learning from corrections
- Conservative confidence scoring (prefer "unknown" over "wrong")

### Risk 5: Training Data for Fallback Classifier
**Description:** Random Forest fallback needs labeled training data, which doesn't exist yet
**Probability:** High (80%)
**Impact:** Low (Essentia models are primary)
**Mitigation:**
- Use existing 2,328 samples with manual genre tags
- Leverage AI vibe analysis for weak labels
- Start with small dataset (100-200 samples)
- Semi-supervised learning: high-confidence Essentia predictions as labels

---

## SUCCESS METRICS

### BPM Accuracy
- **Target:** 95%+ within ±2 BPM of ground truth
- **Measurement:** Test on 100 samples with verified BPM
- **Current Baseline:** ~60-70% (estimated based on octave errors)
- **Minimum Acceptable:** 90% within ±3 BPM

### Genre Classification Accuracy
- **Target:** 80%+ correct primary genre
- **Measurement:** Test on manually labeled samples
- **Current Baseline:** N/A (not implemented)
- **Minimum Acceptable:** 70% for broad categories

### Performance
- **Target:** <8 seconds per sample (average)
- **Current:** 3-5 seconds (librosa only)
- **Maximum Acceptable:** 12 seconds per sample
- **Batch Mode:** Should leverage parallel processing for 100+ samples

### Confidence Scoring
- **Target:** Confidence score correlates >0.8 with actual accuracy
- **Calibration:** High-confidence (>80) predictions should be >95% accurate
- **Low-confidence handling:** <50 confidence should flag for manual review

### User Experience
- **API Response Time:** <10s for single sample analysis
- **Batch Processing:** 1000 samples in <2 hours (7.2s/sample)
- **UI Indicators:** Clear visual feedback for low-confidence predictions
- **Manual Override:** Easy correction workflow for wrong predictions

---

## TESTING STRATEGY

### Test Dataset Creation

**1. Known BPM Samples (100 samples)**
- 10 samples per BPM range:
  - 60-80 BPM (slow hip-hop, trap)
  - 80-100 BPM (boom bap, downtempo)
  - 100-120 BPM (classic hip-hop)
  - 120-140 BPM (house, upbeat)
  - 140-160 BPM (drum & bass, jungle)
  - 160-180 BPM (fast electronic)
  - 40-60 BPM (half-time, experimental)
  - One-shots (no BPM)
- Verify BPM using:
  - Tunebat online analyzer
  - Manual tap tempo
  - DAW BPM detection (Ableton, FL Studio)
- Document in `test_dataset.json`:
  ```json
  {
    "file": "samples/test/boom_bap_90.wav",
    "ground_truth_bpm": 90.0,
    "genre": "hip-hop",
    "sample_type": "loop",
    "duration": 4.0
  }
  ```

**2. Genre Classification Samples (200 samples)**
- 20 samples per category:
  - Hip-Hop/Trap
  - Electronic
  - Jazz/Soul
  - Vintage/Retro
  - Breaks/Drums
  - Ambient
  - Rock
  - Classical
  - World
  - Experimental
- Manually verified genre labels
- Include edge cases (fusion genres)

### Accuracy Benchmarks

**BPM Detection:**
```python
def calculate_bpm_accuracy(predictions, ground_truth):
    """
    Accuracy = % of predictions within ±2 BPM of ground truth
    """
    within_threshold = 0
    for pred, truth in zip(predictions, ground_truth):
        if abs(pred - truth) <= 2.0:
            within_threshold += 1

    return within_threshold / len(predictions) * 100
```

**Genre Classification:**
```python
def calculate_genre_accuracy(predictions, ground_truth):
    """
    Accuracy = % of correct primary genre predictions
    """
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    return correct / len(predictions) * 100
```

### Performance Benchmarks

**Test Scenarios:**
1. **Single Sample Analysis:**
   - Measure time for 10 random samples
   - Average should be <8s

2. **Batch Processing:**
   - Process 100 samples sequentially
   - Measure total time and per-sample average

3. **Parallel Processing:**
   - Process 100 samples with asyncio.gather()
   - Compare to sequential time

4. **Cold Start:**
   - Measure first analysis (includes model loading)
   - Should be <15s

### Integration Tests

```python
# tests/integration/test_audio_analysis_accuracy.py

import pytest
from pathlib import Path
import json

def load_test_dataset():
    """Load ground truth dataset."""
    with open("tests/fixtures/test_dataset.json") as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_bpm_accuracy():
    """Test BPM accuracy on known dataset."""
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    correct = 0
    for sample in dataset:
        if sample["sample_type"] == "one-shot":
            continue  # Skip one-shots

        features = await service.analyze_file(Path(sample["file"]))

        if abs(features.bpm - sample["ground_truth_bpm"]) <= 2.0:
            correct += 1

    accuracy = correct / len([s for s in dataset if s["sample_type"] != "one-shot"])
    assert accuracy >= 0.95, f"BPM accuracy {accuracy:.1%} below target 95%"

@pytest.mark.asyncio
async def test_genre_accuracy():
    """Test genre classification on known dataset."""
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    correct = 0
    for sample in dataset:
        features = await service.analyze_file(Path(sample["file"]))

        if features.genre == sample["genre"]:
            correct += 1

    accuracy = correct / len(dataset)
    assert accuracy >= 0.80, f"Genre accuracy {accuracy:.1%} below target 80%"

@pytest.mark.asyncio
async def test_performance():
    """Test analysis performance."""
    import time
    service = AudioFeaturesService()

    sample_file = Path("tests/fixtures/sample.wav")

    start = time.time()
    await service.analyze_file(sample_file)
    duration = time.time() - start

    assert duration < 8.0, f"Analysis took {duration:.2f}s, exceeds 8s target"
```

### Regression Testing

**After Each Phase:**
1. Run full test suite (pytest)
2. Benchmark BPM accuracy on test dataset
3. Check performance hasn't degraded >20%
4. Validate existing samples still process correctly

**Continuous Monitoring:**
- Track accuracy metrics in production
- Log confidence scores distribution
- Flag samples with low confidence for review
- A/B test new algorithms against production

---

## TOTAL ESTIMATE

**Total Development Hours:** 32 hours

**Phase Breakdown:**
- Phase 1 (BPM Validation): 8 hours
- Phase 2 (Essentia Integration): 12 hours
- Phase 3 (Cross-Validation): 6 hours
- Phase 4 (Genre Classification): 4 hours
- Phase 5 (Confidence Scoring): 2 hours

**Timeline:** 4-5 weeks at 8 hours/week, or 2-3 weeks full-time

**Dependencies:**
- Essentia installation testing (Phase 2 start)
- Test dataset creation (can be parallel to Phase 1)
- TensorFlow model download (Phase 2.3)

**Critical Path:**
Phase 1 → Phase 2 → Phase 3 → Phase 5
(Phase 4 can run parallel to Phase 3)

---

## IMPLEMENTATION PRIORITY

**Immediate (Week 1):**
- Phase 1: Octave correction fixes quick wins

**High Priority (Week 2-3):**
- Phase 2: Essentia integration for major accuracy boost
- Phase 3: Cross-validation for confidence scoring

**Medium Priority (Week 4):**
- Phase 4: Genre classification adds new feature
- Phase 5: Polish and metadata

**Future Enhancements:**
- Madmom integration for additional validation
- Key detection improvement with Essentia
- Real-time analysis optimization
- User feedback loop for continuous learning
