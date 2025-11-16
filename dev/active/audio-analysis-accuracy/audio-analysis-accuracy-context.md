# Audio Analysis Accuracy - Context

**Feature:** Improve BPM detection and genre classification accuracy
**Status:** Planning Complete
**Created:** 2025-11-15
**Last Updated:** 2025-11-15

---

## Problem Statement

The current audio analysis system is producing inaccurate results:
- BPM detection ranges from 26 BPM to 225 BPM for loops (should typically be 60-180 BPM)
- Genre classification is not implemented
- Octave errors are common (26 BPM should be 104 BPM, 225 BPM should be 112.5 BPM)

---

## Key Decisions

### 1. Multi-Library Approach
**Decision:** Use Essentia (primary) + Librosa (fallback) + Madmom (optional)
**Rationale:**
- Essentia provides 90-95% BPM accuracy and built-in genre classification
- Librosa remains for feature extraction and fallback
- Cross-validation increases confidence
- Madmom optional for future enhancement

### 2. Octave Correction as Quick Win
**Decision:** Implement Phase 1 (octave correction) first
**Rationale:**
- Immediate improvement with minimal changes
- Can validate with existing samples
- Doesn't require new dependencies
- 8 hours estimated effort

### 3. Essentia Integration
**Decision:** Integrate Essentia in Phase 2
**Rationale:**
- Commercial-grade accuracy (90-95% BPM, 80-85% genre)
- Pre-trained genre models (87 classes, 519 styles)
- Confidence scores included
- Active development and community

### 4. Genre Mapping
**Decision:** Map Essentia's 87 classes to 10 SP-404MK2 production categories
**Rationale:**
- Too many genres confuse users
- SP-404MK2 workflow focuses on production genres
- Allows multi-label tagging for edge cases

---

## Architecture Notes

### Current Implementation
- **File:** `backend/app/services/audio_features_service.py`
- **BPM Method:** `librosa.beat.beat_track()` with default prior
- **Validation:** 20-300 BPM range (too wide)
- **Genre:** Not implemented

### Proposed Architecture
```
Audio File → Preprocessing → Multi-Library Analysis → Consensus → Validation
                                     ↓
                          [Essentia, Librosa, Madmom]
                                     ↓
                          Weighted Average + Confidence
                                     ↓
                          Octave Correction + Range Check
```

### Key Components
1. **Preprocessor:** Normalize, mono conversion, resample
2. **EssentiaAnalyzer:** RhythmExtractor2013 + genre models
3. **LibrosaAnalyzer:** Enhanced with custom prior and octave correction
4. **MadmomAnalyzer:** Optional TempoEstimationProcessor
5. **ConsensusEngine:** Weighted average, outlier detection, confidence scoring
6. **Validator:** Octave correction, range checking, sanity tests

---

## Key Files

### Existing Files to Modify
- `backend/app/services/audio_features_service.py` - Add orchestration logic
- `backend/app/models/audio_features.py` - Add confidence and metadata fields
- `backend/requirements.txt` - Add essentia, madmom dependencies

### New Files to Create
- `backend/app/services/essentia_analyzer.py` - Essentia integration
- `backend/app/services/madmom_analyzer.py` - Madmom integration (optional)
- `backend/app/services/consensus_engine.py` - Multi-algorithm consensus
- `backend/app/utils/bpm_validation.py` - Octave correction and validation
- `backend/tests/fixtures/test_dataset.json` - Ground truth BPM/genre data
- `backend/tests/integration/test_audio_analysis_accuracy.py` - Accuracy tests
- `backend/config/genre_mapping.json` - Essentia → SP-404 genre mapping

---

## Dependencies

### Python Libraries
- **essentia** (optional): Audio analysis with ML models
- **madmom** (optional): RNN-based beat tracking
- **scikit-learn** (optional): Random Forest fallback classifier
- **scipy**: Custom prior distribution for librosa

### Models/Data
- **Discogs-MAEST models** (~100-200MB): Genre classification
- **Test dataset** (100-200 samples): Ground truth for validation

---

## Testing Strategy

### Test Dataset
- 100 samples with verified BPM (10 per range: 60-80, 80-100, etc.)
- 200 samples with verified genre (20 per category)
- Document ground truth in JSON

### Accuracy Benchmarks
- **BPM:** 95%+ within ±2 BPM
- **Genre:** 80%+ correct primary genre
- **Performance:** <8 seconds per sample

### Integration Tests
- `test_bpm_accuracy()` - Validate BPM predictions
- `test_genre_accuracy()` - Validate genre predictions
- `test_performance()` - Ensure <8s processing time
- `test_confidence_calibration()` - Confidence correlates with accuracy

---

## Success Metrics

### BPM Accuracy
- Target: 95%+ within ±2 BPM
- Current: ~60-70% (estimated)
- Improvement: +25-35 percentage points

### Genre Classification
- Target: 80%+ correct
- Current: N/A (not implemented)
- New feature

### Performance
- Target: <8 seconds per sample
- Current: 3-5 seconds
- Acceptable: 8-12 seconds (due to multi-library)

### Confidence Scoring
- Target: Correlation >0.8 with actual accuracy
- High confidence (>80) → 95%+ accurate
- Low confidence (<50) → Flag for manual review

---

## Risks & Mitigations

### Risk 1: Essentia Installation Complexity
- **Mitigation:** Docker images, fallback to librosa-only mode

### Risk 2: TensorFlow Model Size
- **Mitigation:** Lazy loading, optional download, lite mode

### Risk 3: Performance Degradation
- **Mitigation:** Parallel execution, fast/accurate mode toggle

### Risk 4: Algorithm Disagreement
- **Mitigation:** Store all estimates, allow manual override

### Risk 5: Training Data for Fallback
- **Mitigation:** Use existing samples, AI vibe analysis for labels

---

## Next Steps

1. **Phase 1 (Week 1):** Implement octave correction for quick wins
2. **Phase 2 (Week 2-3):** Integrate Essentia for major accuracy boost
3. **Phase 3 (Week 3):** Add cross-validation and consensus logic
4. **Phase 4 (Week 4):** Enhance genre classification
5. **Phase 5 (Week 4):** Add confidence scoring and polish

---

## Notes

- Start with Phase 1 for immediate improvement
- Essentia may require pre-built Docker images for easy installation
- Consider user preference for fast mode (librosa-only) vs accurate mode (multi-library)
- Manual override and learning from corrections can improve over time
- Conservative confidence scoring preferred (unknown > wrong)

---

## Research Links

- **Essentia:** https://essentia.upf.edu/
- **Madmom:** https://github.com/CPJKU/madmom
- **Discogs-MAEST Models:** https://essentia.upf.edu/models.html
- **BPM Detection Research:** MIR (Music Information Retrieval) papers on octave errors
