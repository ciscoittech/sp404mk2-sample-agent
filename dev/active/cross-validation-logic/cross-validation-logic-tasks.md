# Cross-Validation Logic - Task Checklist

**Phase:** 3 of 5
**Total Hours:** 6 hours
**Timeline:** 1 week
**Dependencies:** Phase 2 (Essentia Integration) complete

---

## Task 3.1: Implement Consensus Algorithm (2 hours)

**Goal:** Create consensus engine to combine multiple BPM estimates

- [ ] **Create Models**
  - [ ] Create `backend/app/services/consensus_engine.py`
  - [ ] Create `BPMEstimate` Pydantic model
    - Fields: bpm, confidence, analyzer, method
  - [ ] Create `ConsensusResult` Pydantic model
    - Fields: bpm, confidence, num_algorithms, agreement_level, all_estimates, outliers_removed

- [ ] **Implement ConsensusEngine Class**
  - [ ] Create `ConsensusEngine` class
  - [ ] Add `__init__()` with configurable weights
  - [ ] Set outlier_threshold = 10.0 BPM
  - [ ] Set weights: essentia=0.5, librosa=0.3, madmom=0.2

- [ ] **Implement calculate_consensus() Method**
  - [ ] Filter out None values
  - [ ] Handle empty estimates list
  - [ ] Handle single estimate (no consensus possible)
  - [ ] Calculate median BPM for outlier detection
  - [ ] Detect outliers (>10 BPM from median)
  - [ ] Remove outliers, log them
  - [ ] Handle case where all are outliers (use median)

- [ ] **Implement Weighted Average**
  - [ ] Calculate weight = analyzer_weight * confidence
  - [ ] Calculate weighted_sum = Σ(bpm * weight)
  - [ ] Calculate consensus_bpm = weighted_sum / total_weight
  - [ ] Round to 1 decimal place

- [ ] **Determine Agreement Level**
  - [ ] Calculate variance between estimates
  - [ ] High agreement: variance ≤4 (±2 BPM)
  - [ ] Medium agreement: variance ≤25 (±5 BPM)
  - [ ] Low agreement: variance >25
  - [ ] Single estimate: 'single'

- [ ] **Add Logging**
  - [ ] Log each estimate received
  - [ ] Log outliers detected
  - [ ] Log final consensus BPM and confidence
  - [ ] Log agreement level

- [ ] **Create Unit Tests**
  - [ ] Create `backend/tests/services/test_consensus_engine.py`
  - [ ] Test with high agreement (±1 BPM)
  - [ ] Test with medium agreement (±5 BPM)
  - [ ] Test with outlier detection
  - [ ] Test with single estimate
  - [ ] Test with all outliers
  - [ ] Test with empty estimates

**Deliverables:**
- ConsensusEngine class implemented
- Weighted average working
- Outlier detection functional
- Unit tests passing

---

## Task 3.2: Create Unified Confidence Scoring (2 hours)

**Goal:** Convert analyzer-specific confidence to 0-100 scale

- [ ] **Implement _calculate_unified_confidence() Method**
  - [ ] Add method to ConsensusEngine class
  - [ ] Accept: estimates, consensus_bpm, outliers_removed
  - [ ] Return: int (0-100)

- [ ] **Base Score Calculation (0-60 points)**
  - [ ] Calculate average internal confidence
  - [ ] Scale to 0-60: avg_confidence * 60
  - [ ] Log base score

- [ ] **Agreement Bonus (0-20 points)**
  - [ ] Calculate variance between estimates
  - [ ] Variance ≤4: +20 points
  - [ ] Variance ≤16: +10 points
  - [ ] Variance >16: 0 points
  - [ ] Log agreement bonus

- [ ] **Variance Penalty (-20 to 0 points)**
  - [ ] Variance >100 (>±10 BPM): -20 points
  - [ ] Variance >25 (>±5 BPM): -10 points
  - [ ] Variance ≤25: 0 penalty
  - [ ] Log variance penalty

- [ ] **Outlier Penalty (-5 per outlier)**
  - [ ] Calculate: -5 * outliers_removed
  - [ ] Log outlier penalty

- [ ] **Count Bonus (0-10 points)**
  - [ ] Calculate: min(10, (num_estimates - 1) * 5)
  - [ ] 2 algorithms: +5
  - [ ] 3 algorithms: +10
  - [ ] Log count bonus

- [ ] **Final Calculation**
  - [ ] Sum all factors
  - [ ] Clamp to 0-100: max(0, min(100, total))
  - [ ] Log final confidence with breakdown

- [ ] **Integrate with calculate_consensus()**
  - [ ] Call _calculate_unified_confidence() in calculate_consensus()
  - [ ] Pass estimates, consensus_bpm, outliers_removed
  - [ ] Store result in ConsensusResult.confidence

- [ ] **Test Confidence Scoring**
  - [ ] Test high agreement scenario (expect 85-95)
  - [ ] Test medium agreement scenario (expect 60-75)
  - [ ] Test low agreement scenario (expect 30-50)
  - [ ] Test single estimate (expect 50-70)
  - [ ] Test with outliers (expect penalty)
  - [ ] Verify all scores are 0-100

- [ ] **Calibration Testing**
  - [ ] Run on 10 test samples with known BPM
  - [ ] Calculate actual accuracy at each confidence level
  - [ ] Adjust weights if needed
  - [ ] Document calibration results

**Deliverables:**
- Unified confidence scoring implemented
- All scoring factors working
- Tests validating score ranges
- Initial calibration complete

---

## Task 3.3: Refactor AudioFeaturesService (2 hours)

**Goal:** Orchestrate multiple analyzers with consensus engine

- [ ] **Update AudioFeaturesService.__init__()**
  - [ ] Import ConsensusEngine, BPMEstimate
  - [ ] Create self.consensus = ConsensusEngine()
  - [ ] Verify Essentia and Librosa analyzers initialized

- [ ] **Create _analyze_with_essentia() Wrapper**
  - [ ] Add method to AudioFeaturesService
  - [ ] Check if self.essentia exists
  - [ ] Call self.essentia.analyze_bpm(audio_path)
  - [ ] Convert result to BPMEstimate
  - [ ] Set analyzer='essentia', method='rhythm_extractor_2013'
  - [ ] Handle exceptions, return None on failure

- [ ] **Update _analyze_with_librosa() Wrapper**
  - [ ] Refactor existing librosa BPM code
  - [ ] Return BPMEstimate instead of float
  - [ ] Set analyzer='librosa', method='beat_track'
  - [ ] Estimate confidence (default 0.65)
  - [ ] Handle exceptions, return None on failure

- [ ] **Implement analyze_bpm_consensus() Method**
  - [ ] Create new async method
  - [ ] Use asyncio.gather() for parallel execution:
    ```python
    results = await asyncio.gather(
        self._analyze_with_essentia(audio_path),
        self._analyze_with_librosa(audio_path),
        return_exceptions=True
    )
    ```
  - [ ] Filter out exceptions
  - [ ] Filter to only BPMEstimate objects
  - [ ] Call self.consensus.calculate_consensus(estimates)
  - [ ] Return ConsensusResult
  - [ ] Log consensus result

- [ ] **Update analyze_file() Method**
  - [ ] Replace direct BPM extraction with analyze_bpm_consensus()
  - [ ] Store consensus.bpm in AudioFeatures.bpm
  - [ ] Store consensus.confidence in AudioFeatures.bpm_confidence (Phase 5 field)
  - [ ] Store consensus metadata in AudioFeatures.analysis_metadata
  - [ ] Keep genre, key, other features unchanged

- [ ] **Add Metadata Storage**
  - [ ] Create analysis_metadata dict:
    ```python
    metadata = {
        'bpm_estimates': [e.dict() for e in consensus.all_estimates],
        'bpm_outliers': [e.dict() for e in consensus.outliers_removed],
        'agreement_level': consensus.agreement_level,
        'num_algorithms': consensus.num_algorithms
    }
    ```
  - [ ] Store in AudioFeatures.analysis_metadata (requires Phase 5 model changes)

- [ ] **Test Parallel Execution**
  - [ ] Verify asyncio.gather() works correctly
  - [ ] Test that both analyzers run in parallel
  - [ ] Measure execution time (should be ~5-7s, not 10s+)
  - [ ] Test that exceptions don't crash the process

- [ ] **Create Integration Tests**
  - [ ] Create `backend/tests/integration/test_consensus_workflow.py`
  - [ ] Test analyze_bpm_consensus() with real audio file
  - [ ] Verify consensus result structure
  - [ ] Verify both analyzers ran
  - [ ] Verify metadata stored
  - [ ] Test with Essentia unavailable (librosa-only)

- [ ] **Test Full Workflow**
  - [ ] Test analyze_file() returns AudioFeatures
  - [ ] Verify BPM from consensus
  - [ ] Verify confidence score present
  - [ ] Verify metadata contains all estimates
  - [ ] Test with various sample types

**Deliverables:**
- AudioFeaturesService refactored
- Parallel execution working
- Consensus integrated
- Metadata stored
- Integration tests passing

---

## Validation Checklist

After completing all tasks:

- [ ] ConsensusEngine class works independently
- [ ] Weighted average produces reasonable BPM
- [ ] Outlier detection catches octave errors
- [ ] Unified confidence scale (0-100) implemented
- [ ] High agreement increases confidence by 20+ points
- [ ] Parallel execution works (asyncio.gather)
- [ ] AudioFeaturesService uses consensus
- [ ] Metadata stores all estimates for debugging
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Processing time <10 seconds per sample
- [ ] Ready for Phase 5 (database changes)

---

## Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| 3.1: Consensus Algorithm | 2h | | |
| 3.2: Confidence Scoring | 2h | | |
| 3.3: Service Integration | 2h | | |
| **Total** | **6h** | | |

---

## Test Scenarios to Validate

### Scenario 1: High Agreement
```python
# Input
estimates = [
    BPMEstimate(bpm=90.5, confidence=0.92, analyzer='essentia'),
    BPMEstimate(bpm=90.0, confidence=0.65, analyzer='librosa')
]

# Expected Output
consensus_bpm: ~90.3
confidence: 85-95
agreement_level: 'high'
```

### Scenario 2: Octave Error Detection
```python
# Input
estimates = [
    BPMEstimate(bpm=104.0, confidence=0.90, analyzer='essentia'),
    BPMEstimate(bpm=26.0, confidence=0.65, analyzer='librosa')
]

# Expected Output
consensus_bpm: 104.0 (26.0 removed as outlier)
confidence: 50-65 (penalty for outlier)
outliers_removed: [26.0 estimate]
```

### Scenario 3: Medium Agreement
```python
# Input
estimates = [
    BPMEstimate(bpm=120.0, confidence=0.88, analyzer='essentia'),
    BPMEstimate(bpm=124.0, confidence=0.60, analyzer='librosa')
]

# Expected Output
consensus_bpm: ~121.5
confidence: 65-75
agreement_level: 'medium'
```

### Scenario 4: Single Estimate
```python
# Input
estimates = [
    BPMEstimate(bpm=110.0, confidence=0.85, analyzer='essentia')
]

# Expected Output
consensus_bpm: 110.0
confidence: 50-60 (penalty for single source)
agreement_level: 'single'
```

---

## Notes

- Consensus engine can be developed and tested independently
- Use mock BPMEstimate objects for unit tests
- Integration tests require real audio files (tests/fixtures/)
- Confidence calibration may need adjustment after testing
- Parallel execution is critical for performance
- Metadata storage enables debugging and transparency
