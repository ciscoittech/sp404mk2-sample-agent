# Confidence Scoring & Metadata - Task Checklist

**Phase:** 5 of 5 (Final Phase)
**Total Hours:** 2 hours
**Timeline:** 2-3 days
**Dependencies:** Phase 3 (Cross-Validation Logic) complete

---

## Task 5.1: Update AudioFeatures Model (1 hour)

**Goal:** Add confidence and metadata fields to database schema

- [ ] **Update AudioFeatures Model**
  - [ ] Open `backend/app/models/audio_features.py`
  - [ ] Add `bpm_confidence = Column(Integer, nullable=True)`
  - [ ] Add `genre_confidence = Column(Integer, nullable=True)`
  - [ ] Add `key_confidence = Column(Integer, nullable=True)`
  - [ ] Add `analysis_metadata = Column(JSON, nullable=True)`
  - [ ] Add docstrings explaining field purposes

- [ ] **Create Alembic Migration**
  - [ ] Run: `alembic revision -m "add_confidence_fields"`
  - [ ] Edit migration file
  - [ ] Add upgrade() with 4 add_column operations
  - [ ] Add downgrade() with 4 drop_column operations
  - [ ] Test migration: `alembic upgrade head`
  - [ ] Test rollback: `alembic downgrade -1`
  - [ ] Verify database schema updated

- [ ] **Update Pydantic Schemas**
  - [ ] Open `backend/app/schemas/audio_features.py`
  - [ ] Add fields to `AudioFeaturesBase`:
    - `bpm_confidence: Optional[int]`
    - `genre_confidence: Optional[int]`
    - `key_confidence: Optional[int]`
  - [ ] Create `AudioFeaturesResponse` schema
  - [ ] Add `analysis_metadata: Optional[dict]` (excluded from base)
  - [ ] Add field validators (0-100 range for confidence)

- [ ] **Update AudioFeaturesService**
  - [ ] Open `backend/app/services/audio_features_service.py`
  - [ ] Update `analyze_file()` to set confidence fields
  - [ ] Store `consensus.confidence` in `bpm_confidence`
  - [ ] Store `genre_result.confidence * 100` in `genre_confidence`
  - [ ] Create metadata dict:
    ```python
    metadata = {
        'bpm_estimates': [e.dict() for e in consensus.all_estimates],
        'bpm_outliers': [e.dict() for e in consensus.outliers_removed],
        'agreement_level': consensus.agreement_level,
        'num_algorithms': consensus.num_algorithms,
        'genre_predictions': [...]  # if genre available
    }
    ```
  - [ ] Store in `analysis_metadata` field

- [ ] **Test Database Operations**
  - [ ] Create test sample with confidence scores
  - [ ] Save to database
  - [ ] Query back and verify fields
  - [ ] Test with null confidence (backward compatibility)
  - [ ] Test JSON serialization of metadata

**Deliverables:**
- AudioFeatures model with 4 new fields
- Migration script created and tested
- Schemas updated and validated
- Service populates fields correctly
- Database tests passing

---

## Task 5.2: Update API Responses (1 hour)

**Goal:** Return confidence scores in API and create debug endpoint

- [ ] **Update Sample API Endpoint**
  - [ ] Open `backend/app/api/v1/endpoints/samples.py`
  - [ ] Verify GET `/samples/{id}` returns confidence fields
  - [ ] Update response_model to include confidence
  - [ ] Test API response includes:
    - `bpm_confidence`
    - `genre_confidence`
    - `key_confidence` (if set)

- [ ] **Create Debug Endpoint**
  - [ ] Create `BPMDebugInfo` Pydantic model
    - Fields: value, confidence, estimates, outliers, agreement_level
  - [ ] Create `GenreDebugInfo` Pydantic model
    - Fields: value, confidence, predictions
  - [ ] Create `AnalysisDebugResponse` model
    - Fields: sample_id, bpm (BPMDebugInfo), genre (GenreDebugInfo), metadata
  - [ ] Add GET `/samples/{id}/analysis-debug` endpoint
  - [ ] Extract metadata from `analysis_metadata` JSON field
  - [ ] Return structured debug information
  - [ ] Handle missing metadata gracefully (404 or empty)

- [ ] **Update Frontend Templates**
  - [ ] Open `frontend/templates/partials/sample-card.html`
  - [ ] Add confidence badge for BPM:
    ```html
    {% if sample.bpm_confidence %}
      {% if sample.bpm_confidence >= 80 %}
        <span class="badge badge-success">✓ High Confidence</span>
      {% elif sample.bpm_confidence >= 50 %}
        <span class="badge badge-warning">⚠ Medium Confidence</span>
      {% else %}
        <span class="badge badge-error">⚠ Low Confidence - Review</span>
      {% endif %}
    {% endif %}
    ```
  - [ ] Add confidence indicator for genre
  - [ ] Add optional debug link: `/samples/{{ sample.id }}/debug`

- [ ] **Create Confidence Indicator Helpers**
  - [ ] Create `frontend/static/js/confidence-indicator.js`
  - [ ] Add `confidenceColor(confidence)` function
  - [ ] Add `confidenceIcon(confidence)` function
  - [ ] Add `confidenceText(confidence)` function
  - [ ] Make available globally or as Alpine.js component

- [ ] **Add CSS Styling**
  - [ ] Open `frontend/static/css/main.css`
  - [ ] Add styles for confidence badges:
    ```css
    .confidence-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }
    ```
  - [ ] Ensure DaisyUI badge colors work correctly
  - [ ] Add hover effects for debug link

- [ ] **Create Debug Page (Optional)**
  - [ ] Create `frontend/pages/sample-debug.html`
  - [ ] Display sample info (filename, duration, etc.)
  - [ ] Show BPM analysis section:
    - Final BPM and confidence
    - All estimates from analyzers
    - Outliers removed
    - Agreement level
  - [ ] Show Genre analysis section:
    - Final genre and confidence
    - Top 3 predictions
  - [ ] Show raw metadata JSON (collapsible)

- [ ] **Test API Responses**
  - [ ] Test GET `/samples/1` returns confidence fields
  - [ ] Test GET `/samples/1/analysis-debug` returns full metadata
  - [ ] Test with sample that has no confidence (null)
  - [ ] Test with invalid sample_id (404)
  - [ ] Verify JSON structure matches schemas

- [ ] **Test Frontend**
  - [ ] Navigate to samples page
  - [ ] Verify confidence badges appear
  - [ ] Verify color coding correct (green/yellow/red)
  - [ ] Test samples with null confidence (badge hidden)
  - [ ] Click debug link, verify debug page loads
  - [ ] Verify debug page shows all analysis details

- [ ] **Write API Tests**
  - [ ] Create `backend/tests/api/test_confidence_api.py`
  - [ ] Test sample endpoint includes confidence
  - [ ] Test debug endpoint returns metadata
  - [ ] Test backward compatibility (null confidence)
  - [ ] Test 404 for missing sample

- [ ] **Write Frontend E2E Tests**
  - [ ] Create `frontend/tests/e2e/test-confidence-indicators.spec.js`
  - [ ] Test confidence badges display
  - [ ] Test color coding
  - [ ] Test debug link navigation
  - [ ] Test with null confidence

**Deliverables:**
- API returns confidence in all responses
- Debug endpoint created and tested
- Frontend shows confidence indicators
- Visual warnings for low confidence
- All tests passing
- Documentation updated

---

## Validation Checklist

After completing all tasks:

- [ ] Database migration runs successfully
- [ ] All new samples have confidence scores
- [ ] Existing samples have null confidence (backward compatible)
- [ ] API includes confidence in responses
- [ ] Debug endpoint returns full metadata
- [ ] UI shows confidence badges
- [ ] Color coding correct (green/yellow/red)
- [ ] Low confidence warnings visible
- [ ] Debug view accessible
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] Documentation updated

---

## Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| 5.1: Model Updates | 1h | | |
| 5.2: API & UI Updates | 1h | | |
| **Total** | **2h** | | |

---

## Test Scenarios

### Scenario 1: High Confidence Sample
```
Input: Sample with Essentia (90.5, 0.92) and Librosa (90.0, 0.65)
Expected Database:
  - bpm: 90.3
  - bpm_confidence: 87
  - analysis_metadata: {...}

Expected UI:
  - "90.3 BPM [✓ High Confidence]" (green badge)
```

### Scenario 2: Low Confidence Sample
```
Input: Sample with only Librosa (125.0, 0.35) due to Essentia failure
Expected Database:
  - bpm: 125.0
  - bpm_confidence: 35
  - analysis_metadata: {...}

Expected UI:
  - "125.0 BPM [⚠ Low Confidence - Review]" (red badge)
  - Warning message visible
```

### Scenario 3: Legacy Sample (No Confidence)
```
Input: Existing sample analyzed before Phase 5
Expected Database:
  - bpm: 90.0
  - bpm_confidence: null
  - analysis_metadata: null

Expected UI:
  - "90.0 BPM" (no badge shown)
  - No warnings or errors
```

### Scenario 4: Debug Endpoint
```
Request: GET /api/v1/samples/1/analysis-debug
Expected Response:
{
  "sample_id": 1,
  "bpm": {
    "value": 90.5,
    "confidence": 87,
    "estimates": [
      {"bpm": 90.5, "confidence": 0.92, "analyzer": "essentia"},
      {"bpm": 90.0, "confidence": 0.65, "analyzer": "librosa"}
    ],
    "outliers": [],
    "agreement_level": "high"
  },
  "genre": {...},
  "metadata": {...}
}
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Run all tests locally
- [ ] Test migration on development database
- [ ] Backup production database
- [ ] Review migration script
- [ ] Test API endpoints locally
- [ ] Test UI locally

### Deployment Steps
1. [ ] Stop production server
2. [ ] Backup database
3. [ ] Run migration: `alembic upgrade head`
4. [ ] Verify migration: check database schema
5. [ ] Deploy new code
6. [ ] Start production server
7. [ ] Test API endpoints in production
8. [ ] Test UI in production
9. [ ] Monitor logs for errors

### Post-Deployment
- [ ] Verify confidence scores appear for new samples
- [ ] Verify existing samples still work (null confidence)
- [ ] Check debug endpoint works
- [ ] Monitor performance metrics
- [ ] Collect user feedback

---

## Rollback Plan

If issues occur:
1. [ ] Stop production server
2. [ ] Run migration rollback: `alembic downgrade -1`
3. [ ] Deploy previous code version
4. [ ] Restart production server
5. [ ] Verify system working
6. [ ] Investigate issue
7. [ ] Fix and redeploy

---

## Notes

- Migration is backward-compatible (nullable fields)
- Existing samples continue to work without confidence
- Can backfill confidence later with re-analysis script
- Debug endpoint is optional (power users only)
- UI indicators should be subtle, not alarming
- Confidence formula can be tuned after testing
