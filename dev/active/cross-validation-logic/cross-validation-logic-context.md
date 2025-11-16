# Cross-Validation Logic - Context

**Feature:** Multi-library BPM consensus with unified confidence scoring
**Phase:** 3 of 5
**Status:** Ready to Implement
**Created:** 2025-11-15
**Dependencies:** Phase 2 (Essentia Integration) must be complete

---

## Why Cross-Validation?

### The Problem
Single-library analysis is prone to errors:
- **Librosa:** Octave errors (26 BPM instead of 104 BPM)
- **Essentia:** Occasionally gives unexpected results
- **No confidence in results:** Is 90 BPM reliable or a guess?

### The Solution
Run multiple analyzers and combine results:
- **Confidence boost:** Multiple algorithms agreeing = high confidence
- **Error detection:** Outliers caught and removed
- **Transparency:** Store all estimates for debugging
- **Reliability:** Weighted average reduces single-algorithm bias

---

## Key Decisions

### 1. Parallel Execution
**Decision:** Run Essentia and Librosa in parallel with `asyncio.gather()`
**Rationale:**
- Don't slow down analysis (10s max vs 6-8s sequential)
- Both analyzers are I/O and CPU independent
- Graceful failure handling (one can fail, other continues)

### 2. Weighted Consensus
**Decision:** Weight Essentia (0.5), Librosa (0.3), Madmom (0.2)
**Rationale:**
- Essentia is most accurate (90-95%)
- Librosa is baseline (60-70%)
- Madmom future enhancement
- Weights can be tuned based on accuracy testing

### 3. Outlier Detection
**Decision:** Remove estimates >10 BPM from median
**Rationale:**
- Catches octave errors (26 BPM vs 104 BPM = 78 BPM difference)
- Allows ±5 BPM variance for legitimate disagreement
- Uses median (not mean) to avoid outlier skew

### 4. Unified Confidence Scale (0-100)
**Decision:** Convert all confidence to 0-100 integer scale
**Rationale:**
- User-friendly (percentage-like)
- Combines multiple confidence factors
- Easier to display in UI
- Standard across all predictions (BPM, genre, key)

---

## Architecture Notes

### Consensus Algorithm Flow

```
1. Collect Estimates
   ├─ Essentia: (bpm, confidence)
   ├─ Librosa: (bpm, confidence)
   └─ Madmom: (bpm, confidence) [optional]

2. Filter Valid Estimates
   └─ Remove None values

3. Detect Outliers
   ├─ Calculate median BPM
   ├─ Remove estimates >10 BPM from median
   └─ Log outliers for debugging

4. Weighted Average
   ├─ weight = analyzer_weight * confidence
   ├─ weighted_sum = Σ(bpm * weight)
   └─ consensus_bpm = weighted_sum / total_weight

5. Calculate Unified Confidence
   ├─ Base score (0-60): Average internal confidence
   ├─ Agreement bonus (0-20): Variance between estimates
   ├─ Variance penalty (-20-0): High disagreement
   ├─ Outlier penalty (-5 each): Removed outliers
   └─ Count bonus (0-10): Number of algorithms

6. Return Result
   ├─ Consensus BPM
   ├─ Unified confidence (0-100)
   ├─ Agreement level (high/medium/low)
   └─ All estimates + outliers (metadata)
```

### Confidence Scoring Formula

```python
confidence = (
    base_score          # 0-60: Average of internal confidences
    + agreement_bonus   # 0-20: Multiple algorithms within ±2 BPM
    + variance_penalty  # -20-0: Penalty for high variance
    + outlier_penalty   # -5 each: Removed outliers
    + count_bonus       # 0-10: Number of algorithms
)
# Clamp to 0-100
```

**Example Calculations:**

**High Confidence (92):**
- Essentia: 90.5 BPM, 0.92 confidence
- Librosa: 90.0 BPM, 0.65 confidence
- Base: (0.92 + 0.65)/2 * 60 = 47.1
- Agreement: +20 (within ±2 BPM)
- Variance: 0 (low variance)
- Outliers: 0
- Count: +5 (2 algorithms)
- **Total: 72**

**Low Confidence (35):**
- Essentia: 120.0 BPM, 0.50 confidence
- Librosa: 60.0 BPM, 0.40 confidence (octave error)
- Base: (0.50 + 0.40)/2 * 60 = 27
- Agreement: 0 (high variance)
- Variance: -20 (60 BPM difference)
- Outliers: -5 (librosa removed)
- Count: +5 (started with 2)
- **Total: 7** (after removing outlier, recalculate with only Essentia → ~35)

---

## Key Files

### Files to Create
- `backend/app/services/consensus_engine.py` - Consensus logic
- `backend/tests/services/test_consensus_engine.py` - Unit tests
- `backend/tests/integration/test_consensus_workflow.py` - Integration tests

### Files to Modify
- `backend/app/services/audio_features_service.py` - Integrate consensus
- `backend/app/models/audio_features.py` - Add metadata field (later in Phase 5)

---

## Implementation Strategy

### Task Order
1. **Task 3.1:** Build consensus engine independently (can test with mock data)
2. **Task 3.2:** Add confidence scoring to consensus engine
3. **Task 3.3:** Integrate into AudioFeaturesService

### Testing Approach
1. **Unit tests:** Test consensus algorithm with known inputs
2. **Integration tests:** Test with real audio files
3. **Calibration:** Validate confidence scores match actual accuracy

---

## Confidence Score Calibration

### Target Accuracy by Confidence Level
- **90-100:** 95%+ accurate (within ±2 BPM)
- **70-89:** 85%+ accurate (within ±3 BPM)
- **50-69:** 70%+ accurate (within ±5 BPM)
- **30-49:** 50%+ accurate (unreliable, flag for review)
- **0-29:** Likely wrong, don't trust

### Calibration Process
1. Run consensus on 100 test samples
2. Calculate actual accuracy at each confidence level
3. Adjust scoring formula if needed
4. Validate calibration holds on new samples

---

## Edge Cases

### 1. Single Estimate Only
- Essentia fails, only Librosa available
- **Handling:** Return BPM with confidence penalty (max 70)

### 2. All Estimates are Outliers
- Essentia: 120 BPM, Librosa: 60 BPM, Madmom: 180 BPM
- **Handling:** Use median, mark as low confidence

### 3. High Variance, High Confidence
- Essentia: 100 BPM (0.95), Librosa: 110 BPM (0.90)
- **Handling:** Variance penalty reduces final confidence

### 4. Low Internal Confidence, High Agreement
- Essentia: 90 BPM (0.40), Librosa: 90 BPM (0.45)
- **Handling:** Agreement bonus, but base score is low

---

## Performance Considerations

### Parallel Execution
```python
# Run analyzers in parallel (not sequential)
results = await asyncio.gather(
    self._analyze_with_essentia(audio_path),
    self._analyze_with_librosa(audio_path),
    return_exceptions=True  # Don't fail if one analyzer crashes
)
```

**Performance:**
- **Sequential:** 3-5s (Essentia) + 2-3s (Librosa) = 5-8s
- **Parallel:** max(3-5s, 2-3s) = 3-5s
- **Target:** <10s total analysis time

### Metadata Storage
Store all estimates in `analysis_metadata` JSON field:
```json
{
  "bpm_estimates": [
    {"bpm": 90.5, "confidence": 0.92, "analyzer": "essentia"},
    {"bpm": 90.0, "confidence": 0.65, "analyzer": "librosa"}
  ],
  "bpm_outliers": [],
  "agreement_level": "high",
  "num_algorithms": 2,
  "consensus_bpm": 90.3,
  "consensus_confidence": 87
}
```

---

## Success Metrics

### Agreement Detection
- **High agreement:** Variance ≤4 (±2 BPM) → +20 confidence
- **Medium agreement:** Variance ≤25 (±5 BPM) → +10 confidence
- **Low agreement:** Variance >25 → 0 bonus

### Outlier Detection
- **Test case:** Librosa returns 26 BPM, Essentia returns 104 BPM
- **Expected:** Remove 26 BPM as outlier, use 104 BPM

### Confidence Calibration
- **High confidence (>80):** 95%+ accuracy on test dataset
- **Medium confidence (50-80):** 75%+ accuracy
- **Low confidence (<50):** Flag for manual review

---

## Risks & Mitigations

### Risk: Analyzer Disagreement Too High
**Problem:** Essentia and Librosa consistently disagree by 10+ BPM
**Mitigation:**
- Outlier detection removes one
- Low confidence score warns user
- Manual override available

### Risk: Confidence Score Not Calibrated
**Problem:** Confidence doesn't match actual accuracy
**Mitigation:**
- Test on 100+ samples with ground truth
- Adjust scoring formula weights
- Iterative calibration

### Risk: Performance Degradation
**Problem:** Parallel execution doesn't work as expected
**Mitigation:**
- Use asyncio.gather() correctly
- Monitor execution times
- Fallback to sequential if needed

---

## Next Steps After Phase 3

Move to **Phase 5: Confidence Scoring & Metadata:**
1. Add `bpm_confidence` field to AudioFeatures model
2. Add `analysis_metadata` JSON field
3. Update API to return confidence scores
4. Add UI indicators for low confidence
5. Create `/samples/{id}/analysis-debug` endpoint

---

## Notes

- Consensus engine is testable independently (no database needed)
- Can mock BPMEstimate objects for unit tests
- Integration tests require real audio files
- Confidence formula can be tuned after testing
- Parallel execution requires proper async handling
- Metadata is critical for debugging and transparency
