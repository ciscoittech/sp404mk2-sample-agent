# Cross-Validation Logic - Implementation Plan

**Phase:** 3 of 5
**Estimated Hours:** 6 hours
**Timeline:** 1 week
**Dependencies:** Phase 2 (Essentia Integration) must be complete

---

## EXECUTIVE SUMMARY

Implement multi-library cross-validation to combine BPM estimates from Essentia and Librosa. Use weighted consensus algorithm to produce a single high-confidence BPM estimate with unified confidence scoring (0-100 scale).

**Goals:**
- Run both Essentia and Librosa analyzers in parallel
- Implement consensus algorithm for BPM
- Create unified confidence scoring (0-100)
- Detect and handle outliers
- Store all estimates in metadata for debugging

**Success Metrics:**
- Agreement within ±2 BPM increases confidence by 20+ points
- High-confidence predictions (>80) are 95%+ accurate
- Processing time <10 seconds per sample (parallel execution)
- All algorithm estimates stored in debug metadata

---

## ARCHITECTURE OVERVIEW

### Current State (After Phase 2)
```
Audio File → EssentiaAnalyzer → BPM + Confidence
           OR
Audio File → LibrosaAnalyzer → BPM + Confidence
```

### Target State
```
Audio File → Preprocessing
                ↓
        ┌───────┴───────┐
        ▼               ▼
  EssentiaAnalyzer  LibrosaAnalyzer
        │               │
        └───────┬───────┘
                ↓
        ConsensusEngine
                ↓
     Weighted Average + Outlier Detection
                ↓
     Unified Confidence Scoring (0-100)
                ↓
     Final BPM + Confidence + Metadata
```

### Consensus Algorithm Logic

```python
def consensus_bpm(estimates: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate consensus BPM from multiple analyzers.

    estimates: [(bpm, confidence), ...]
    returns: (consensus_bpm, consensus_confidence)
    """
    # Step 1: Filter out None values
    valid = [e for e in estimates if e[0] is not None]

    # Step 2: Detect outliers (>10 BPM from median)
    median_bpm = np.median([bpm for bpm, _ in valid])
    filtered = [e for e in valid if abs(e[0] - median_bpm) <= 10]

    # Step 3: Weighted average
    total_weight = sum(conf for _, conf in filtered)
    weighted_bpm = sum(bpm * conf for bpm, conf in filtered) / total_weight

    # Step 4: Calculate unified confidence (0-100)
    confidence = calculate_unified_confidence(filtered, weighted_bpm)

    return weighted_bpm, confidence
```

---

## DETAILED IMPLEMENTATION PLAN

### Task 3.1: Implement Consensus Algorithm (2 hours)

**Objective:** Create consensus engine to combine multiple BPM estimates

**Implementation:**

```python
# backend/app/services/consensus_engine.py

from typing import List, Tuple, Optional
import numpy as np
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class BPMEstimate(BaseModel):
    """Single BPM estimate from an analyzer."""
    bpm: float
    confidence: float  # 0.0 to 1.0 (internal)
    analyzer: str  # 'essentia', 'librosa', 'madmom'
    method: Optional[str] = None  # e.g., 'multifeature', 'beat_track'


class ConsensusResult(BaseModel):
    """Consensus BPM result."""
    bpm: float
    confidence: int  # 0-100 unified scale
    num_algorithms: int
    agreement_level: str  # 'high', 'medium', 'low'
    all_estimates: List[BPMEstimate]
    outliers_removed: List[BPMEstimate]


class ConsensusEngine:
    """Combine multiple BPM estimates into consensus result."""

    def __init__(self):
        self.outlier_threshold = 10.0  # BPM
        self.weights = {
            'essentia': 0.5,
            'librosa': 0.3,
            'madmom': 0.2
        }

    def calculate_consensus(
        self,
        estimates: List[BPMEstimate]
    ) -> ConsensusResult:
        """
        Calculate consensus BPM from multiple estimates.

        Args:
            estimates: List of BPM estimates from different analyzers

        Returns:
            ConsensusResult with weighted BPM and unified confidence
        """
        # Filter out None values
        valid = [e for e in estimates if e.bpm is not None]

        if len(valid) == 0:
            logger.warning("No valid BPM estimates")
            return ConsensusResult(
                bpm=0.0,
                confidence=0,
                num_algorithms=0,
                agreement_level='none',
                all_estimates=[],
                outliers_removed=[]
            )

        # Single estimate (no consensus possible)
        if len(valid) == 1:
            estimate = valid[0]
            # Convert internal confidence (0-1) to unified (0-100)
            unified_conf = int(estimate.confidence * 70)  # Max 70 for single
            return ConsensusResult(
                bpm=estimate.bpm,
                confidence=unified_conf,
                num_algorithms=1,
                agreement_level='single',
                all_estimates=valid,
                outliers_removed=[]
            )

        # Detect outliers
        bpms = [e.bpm for e in valid]
        median_bpm = np.median(bpms)

        outliers = []
        filtered = []
        for estimate in valid:
            if abs(estimate.bpm - median_bpm) > self.outlier_threshold:
                outliers.append(estimate)
                logger.warning(
                    f"Outlier detected: {estimate.analyzer} "
                    f"BPM {estimate.bpm:.1f} (median: {median_bpm:.1f})"
                )
            else:
                filtered.append(estimate)

        # Fallback if all outliers
        if len(filtered) == 0:
            logger.warning("All estimates are outliers, using median")
            filtered = valid
            outliers = []

        # Weighted average
        total_weight = 0.0
        weighted_sum = 0.0

        for estimate in filtered:
            weight = self.weights.get(estimate.analyzer, 0.3) * estimate.confidence
            weighted_sum += estimate.bpm * weight
            total_weight += weight

        consensus_bpm = weighted_sum / total_weight

        # Calculate unified confidence
        unified_confidence = self._calculate_unified_confidence(
            filtered,
            consensus_bpm,
            outliers_removed=len(outliers)
        )

        # Determine agreement level
        if len(filtered) >= 2:
            variance = np.var([e.bpm for e in filtered])
            if variance <= 4:  # Within ±2 BPM
                agreement = 'high'
            elif variance <= 25:  # Within ±5 BPM
                agreement = 'medium'
            else:
                agreement = 'low'
        else:
            agreement = 'single'

        logger.info(
            f"Consensus BPM: {consensus_bpm:.1f} "
            f"(confidence: {unified_confidence}, agreement: {agreement})"
        )

        return ConsensusResult(
            bpm=round(consensus_bpm, 1),
            confidence=unified_confidence,
            num_algorithms=len(filtered),
            agreement_level=agreement,
            all_estimates=valid,
            outliers_removed=outliers
        )

    def _calculate_unified_confidence(
        self,
        estimates: List[BPMEstimate],
        consensus_bpm: float,
        outliers_removed: int
    ) -> int:
        """
        Calculate unified confidence score (0-100).

        Factors:
        - Number of algorithms agreeing
        - Variance between estimates
        - Individual confidence scores
        - Outliers removed
        """
        # Placeholder - implemented in Task 3.2
        return 50
```

**Steps:**
1. Create `backend/app/services/consensus_engine.py`
2. Implement `BPMEstimate` model
3. Implement `ConsensusResult` model
4. Implement `ConsensusEngine` class
5. Implement `calculate_consensus()` method
6. Add outlier detection logic
7. Add weighted average calculation
8. Write unit tests

**Deliverables:**
- [ ] ConsensusEngine class implemented
- [ ] Weighted average working
- [ ] Outlier detection working
- [ ] Unit tests passing

**Files Created:**
- `backend/app/services/consensus_engine.py`
- `backend/tests/services/test_consensus_engine.py`

---

### Task 3.2: Create Unified Confidence Scoring (2 hours)

**Objective:** Convert analyzer-specific confidence to 0-100 scale

**Confidence Scoring Formula:**

```python
def _calculate_unified_confidence(
    self,
    estimates: List[BPMEstimate],
    consensus_bpm: float,
    outliers_removed: int
) -> int:
    """
    Calculate 0-100 confidence score.

    Scoring factors:
    1. Base confidence: Average of individual confidences (0-60 points)
    2. Agreement bonus: Multiple algorithms within ±2 BPM (+20 points)
    3. Variance penalty: High variance between estimates (-10 to -20 points)
    4. Outlier penalty: Removed outliers (-5 points each)
    5. Count bonus: 3+ algorithms (+10 points)
    """
    num_estimates = len(estimates)

    # Factor 1: Base confidence (0-60)
    avg_internal_conf = np.mean([e.confidence for e in estimates])
    base_score = avg_internal_conf * 60

    # Factor 2: Agreement bonus (0-20)
    variance = np.var([e.bpm for e in estimates])
    if variance <= 4:  # Within ±2 BPM
        agreement_bonus = 20
    elif variance <= 16:  # Within ±4 BPM
        agreement_bonus = 10
    else:
        agreement_bonus = 0

    # Factor 3: Variance penalty (0 to -20)
    if variance > 100:  # >±10 BPM
        variance_penalty = -20
    elif variance > 25:  # >±5 BPM
        variance_penalty = -10
    else:
        variance_penalty = 0

    # Factor 4: Outlier penalty (-5 per outlier)
    outlier_penalty = -5 * outliers_removed

    # Factor 5: Count bonus (0-10)
    count_bonus = min(10, (num_estimates - 1) * 5)  # +5 per extra algorithm

    # Calculate total
    total = base_score + agreement_bonus + variance_penalty + outlier_penalty + count_bonus

    # Clamp to 0-100
    final_confidence = max(0, min(100, int(total)))

    logger.debug(
        f"Confidence calculation: base={base_score:.1f}, "
        f"agreement={agreement_bonus}, variance={variance_penalty}, "
        f"outlier={outlier_penalty}, count={count_bonus}, "
        f"final={final_confidence}"
    )

    return final_confidence
```

**Confidence Scale Meaning:**
- **90-100:** Multiple algorithms agree within ±2 BPM, high internal confidence
- **70-89:** 2+ algorithms agree within ±5 BPM, good confidence
- **50-69:** Single algorithm with high confidence, or some disagreement
- **30-49:** Low internal confidence or high variance
- **0-29:** Very low confidence, likely unreliable

**Steps:**
1. Implement `_calculate_unified_confidence()` method
2. Add base confidence calculation (0-60)
3. Add agreement bonus (0-20)
4. Add variance penalty (-20 to 0)
5. Add outlier penalty (-5 each)
6. Add count bonus (0-10)
7. Test with various scenarios
8. Calibrate against test dataset

**Deliverables:**
- [ ] Unified confidence scoring implemented
- [ ] Calibrated against test samples
- [ ] Tests validating score ranges
- [ ] Documentation of scoring factors

---

### Task 3.3: Refactor AudioFeaturesService (2 hours)

**Objective:** Orchestrate multiple analyzers and consensus engine

**Implementation:**

```python
# backend/app/services/audio_features_service.py

from app.services.essentia_analyzer import EssentiaAnalyzer, ESSENTIA_AVAILABLE
from app.services.consensus_engine import ConsensusEngine, BPMEstimate
import asyncio


class AudioFeaturesService:
    def __init__(self):
        # Initialize analyzers
        self.essentia = None
        self.consensus = ConsensusEngine()

        if ESSENTIA_AVAILABLE:
            try:
                self.essentia = EssentiaAnalyzer()
                logger.info("Essentia analyzer initialized")
            except Exception as e:
                logger.warning(f"Essentia init failed: {e}")

    async def _analyze_with_essentia(
        self,
        audio_path: Path
    ) -> Optional[BPMEstimate]:
        """Analyze with Essentia."""
        if not self.essentia:
            return None

        try:
            result = await self.essentia.analyze_bpm(audio_path)
            if result:
                return BPMEstimate(
                    bpm=result.bpm,
                    confidence=result.confidence,
                    analyzer='essentia',
                    method='rhythm_extractor_2013'
                )
        except Exception as e:
            logger.error(f"Essentia analysis failed: {e}")
        return None

    async def _analyze_with_librosa(
        self,
        audio_path: Path
    ) -> Optional[BPMEstimate]:
        """Analyze with Librosa."""
        try:
            # Existing librosa code
            bpm = self._extract_bpm(y, sr)
            if bpm:
                # Estimate confidence (librosa doesn't provide it)
                confidence = 0.65  # Default moderate confidence
                return BPMEstimate(
                    bpm=bpm,
                    confidence=confidence,
                    analyzer='librosa',
                    method='beat_track'
                )
        except Exception as e:
            logger.error(f"Librosa analysis failed: {e}")
        return None

    async def analyze_bpm_consensus(
        self,
        audio_path: Path
    ) -> ConsensusResult:
        """
        Analyze BPM using multiple algorithms and consensus.

        Returns:
            ConsensusResult with BPM, confidence, and metadata
        """
        # Run analyzers in parallel
        results = await asyncio.gather(
            self._analyze_with_essentia(audio_path),
            self._analyze_with_librosa(audio_path),
            return_exceptions=True
        )

        # Filter out exceptions
        estimates = [r for r in results if isinstance(r, BPMEstimate)]

        # Calculate consensus
        consensus = self.consensus.calculate_consensus(estimates)

        logger.info(
            f"BPM consensus: {consensus.bpm} "
            f"(confidence: {consensus.confidence}, "
            f"algorithms: {consensus.num_algorithms})"
        )

        return consensus

    async def analyze_file(self, file_path: Path) -> AudioFeatures:
        """
        Complete audio analysis with consensus BPM.
        """
        # BPM consensus
        consensus = await self.analyze_bpm_consensus(file_path)

        # Genre (Essentia only for now)
        genre_result = None
        if self.essentia:
            genre_result = await self.essentia.analyze_genre(file_path)

        # Other features (librosa)
        key = self._extract_key(y, sr)
        # ... other features ...

        return AudioFeatures(
            bpm=consensus.bpm,
            bpm_confidence=consensus.confidence,
            genre=genre_result.primary_genre if genre_result else None,
            genre_confidence=int(genre_result.confidence * 100) if genre_result else None,
            key=key,
            # ... other fields ...
            analysis_metadata={
                'bpm_estimates': [e.dict() for e in consensus.all_estimates],
                'bpm_outliers': [e.dict() for e in consensus.outliers_removed],
                'agreement_level': consensus.agreement_level,
                'num_algorithms': consensus.num_algorithms
            }
        )
```

**Steps:**
1. Update `AudioFeaturesService.__init__()` to create ConsensusEngine
2. Implement `_analyze_with_essentia()` wrapper
3. Update `_analyze_with_librosa()` to return BPMEstimate
4. Implement `analyze_bpm_consensus()` with parallel execution
5. Update `analyze_file()` to use consensus
6. Store all estimates in `analysis_metadata`
7. Add integration tests

**Deliverables:**
- [ ] AudioFeaturesService refactored
- [ ] Parallel execution working
- [ ] Consensus integrated
- [ ] Metadata stored
- [ ] Tests passing

**Files Modified:**
- `backend/app/services/audio_features_service.py`

**Files Created:**
- `backend/tests/integration/test_consensus_workflow.py`

---

## TESTING STRATEGY

### Test Scenarios

**1. High Agreement (±1 BPM):**
```python
estimates = [
    BPMEstimate(bpm=90.5, confidence=0.92, analyzer='essentia'),
    BPMEstimate(bpm=90.0, confidence=0.65, analyzer='librosa')
]
# Expected: consensus ~90.3, confidence 85+
```

**2. Medium Agreement (±5 BPM):**
```python
estimates = [
    BPMEstimate(bpm=120.0, confidence=0.88, analyzer='essentia'),
    BPMEstimate(bpm=124.0, confidence=0.60, analyzer='librosa')
]
# Expected: consensus ~121, confidence 60-75
```

**3. Outlier Detection:**
```python
estimates = [
    BPMEstimate(bpm=104.0, confidence=0.90, analyzer='essentia'),
    BPMEstimate(bpm=26.0, confidence=0.65, analyzer='librosa')  # Octave error
]
# Expected: Remove 26.0 outlier, use 104.0
```

**4. Single Estimate:**
```python
estimates = [
    BPMEstimate(bpm=110.0, confidence=0.85, analyzer='essentia')
]
# Expected: BPM 110.0, confidence ~60 (single source penalty)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_consensus_workflow():
    """Test full consensus workflow."""
    service = AudioFeaturesService()
    consensus = await service.analyze_bpm_consensus(Path("tests/fixtures/sample_90bpm.wav"))

    assert consensus.bpm is not None
    assert 0 <= consensus.confidence <= 100
    assert consensus.num_algorithms >= 1
    assert len(consensus.all_estimates) >= 1
```

---

## SUCCESS CRITERIA

- [x] Consensus algorithm combines multiple estimates
- [x] Outlier detection removes octave errors
- [x] Unified confidence scale (0-100) implemented
- [x] High agreement increases confidence
- [x] Parallel execution working (asyncio.gather)
- [x] Metadata stores all estimates for debugging
- [x] Tests pass with various scenarios
- [x] Processing time <10 seconds

---

## NEXT STEPS

After Phase 3, move to **Phase 5: Confidence Scoring & Metadata** to:
1. Add confidence fields to database
2. Update API responses
3. Add UI confidence indicators
