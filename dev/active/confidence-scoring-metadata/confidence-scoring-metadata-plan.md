# Confidence Scoring & Metadata - Implementation Plan

**Phase:** 5 of 5
**Estimated Hours:** 2 hours
**Timeline:** 2-3 days
**Dependencies:** Phase 3 (Cross-Validation Logic) must be complete

---

## EXECUTIVE SUMMARY

Add database fields for confidence scores and analysis metadata. Update API responses to include confidence information. Create UI indicators to show users when predictions are low-confidence and may need review.

**Goals:**
- Add `bpm_confidence` and `genre_confidence` fields to database
- Add `analysis_metadata` JSON field for debugging
- Update API to return confidence scores
- Create `/samples/{id}/analysis-debug` endpoint
- Add UI confidence indicators

**Success Metrics:**
- Confidence scores stored for all samples
- API returns confidence with every prediction
- UI shows visual warnings for low-confidence (<50)
- Debug endpoint provides full analysis metadata

---

## ARCHITECTURE OVERVIEW

### Current State (After Phase 3)
```
AudioFeaturesService → ConsensusResult → AudioFeatures
                                              ↓
                                         Sample (database)
                                              ↓
                                         API Response (no confidence)
```

### Target State
```
AudioFeaturesService → ConsensusResult → AudioFeatures
                                              ↓
                                    ┌─────────┴─────────┐
                                    ▼                   ▼
                           bpm_confidence      analysis_metadata
                           genre_confidence           (JSON)
                                    ├───────────────────┤
                                    ▼
                              Sample (database)
                                    ↓
                              API Response
                      {
                        "bpm": 90.5,
                        "bpm_confidence": 87,
                        "genre": "Hip-Hop",
                        "genre_confidence": 72,
                        "metadata": {...}
                      }
                                    ↓
                              UI Indicator
                        ✅ High confidence (>80)
                        ⚠️  Medium confidence (50-80)
                        ❌ Low confidence (<50)
```

---

## DETAILED IMPLEMENTATION PLAN

### Task 5.1: Update AudioFeatures Model (1 hour)

**Objective:** Add confidence and metadata fields to database schema

**Database Changes:**

```python
# backend/app/models/audio_features.py

from sqlalchemy import Column, Integer, JSON

class AudioFeatures(Base):
    __tablename__ = "audio_features"

    # ... existing fields ...
    bpm = Column(Float, nullable=True)
    key = Column(String(10), nullable=True)
    genre = Column(String(50), nullable=True)

    # NEW: Confidence scores (0-100)
    bpm_confidence = Column(Integer, nullable=True)
    genre_confidence = Column(Integer, nullable=True)
    key_confidence = Column(Integer, nullable=True)  # Future

    # NEW: Analysis metadata (JSON)
    analysis_metadata = Column(JSON, nullable=True)
    # Structure:
    # {
    #   "bpm_estimates": [
    #     {"bpm": 90.5, "confidence": 0.92, "analyzer": "essentia"},
    #     {"bpm": 90.0, "confidence": 0.65, "analyzer": "librosa"}
    #   ],
    #   "bpm_outliers": [],
    #   "agreement_level": "high",
    #   "num_algorithms": 2,
    #   "genre_predictions": [
    #     {"genre": "Hip-Hop", "confidence": 0.72},
    #     {"genre": "Boom Bap", "confidence": 0.18}
    #   ]
    # }
```

**Migration Script:**

```python
# backend/alembic/versions/add_confidence_fields.py

def upgrade():
    op.add_column('audio_features', sa.Column('bpm_confidence', sa.Integer(), nullable=True))
    op.add_column('audio_features', sa.Column('genre_confidence', sa.Integer(), nullable=True))
    op.add_column('audio_features', sa.Column('key_confidence', sa.Integer(), nullable=True))
    op.add_column('audio_features', sa.Column('analysis_metadata', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('audio_features', 'analysis_metadata')
    op.drop_column('audio_features', 'key_confidence')
    op.drop_column('audio_features', 'genre_confidence')
    op.drop_column('audio_features', 'bpm_confidence')
```

**Schema Updates:**

```python
# backend/app/schemas/audio_features.py

class AudioFeaturesBase(BaseModel):
    bpm: Optional[float] = None
    bpm_confidence: Optional[int] = None
    genre: Optional[str] = None
    genre_confidence: Optional[int] = None
    key: Optional[str] = None
    key_confidence: Optional[int] = None
    # ... other fields ...

class AudioFeaturesResponse(AudioFeaturesBase):
    """API response with confidence scores."""
    id: int
    sample_id: int
    analysis_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
```

**Steps:**
1. Update AudioFeatures model with new fields
2. Create Alembic migration
3. Run migration on database
4. Update Pydantic schemas
5. Test database operations

**Deliverables:**
- [ ] AudioFeatures model updated
- [ ] Migration script created and tested
- [ ] Schemas updated
- [ ] Database migrated

**Files Modified:**
- `backend/app/models/audio_features.py`
- `backend/app/schemas/audio_features.py`

**Files Created:**
- `backend/alembic/versions/XXX_add_confidence_fields.py`

---

### Task 5.2: Update API Responses (1 hour)

**Objective:** Return confidence scores in API responses and create debug endpoint

**API Updates:**

```python
# backend/app/api/v1/endpoints/samples.py

from app.schemas.audio_features import AudioFeaturesResponse

@router.get("/{sample_id}", response_model=SampleResponse)
async def get_sample(sample_id: int, db: AsyncSession = Depends(get_db)):
    """Get sample with confidence scores."""
    sample = await db.get(Sample, sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    # Response now includes confidence scores
    return sample


@router.get("/{sample_id}/analysis-debug", response_model=AnalysisDebugResponse)
async def get_analysis_debug(sample_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get detailed analysis metadata for debugging.

    Returns:
    - All BPM estimates from different analyzers
    - Outliers removed
    - Agreement level
    - Genre predictions (top 3)
    - Full analysis metadata
    """
    sample = await db.get(Sample, sample_id)
    if not sample or not sample.audio_features:
        raise HTTPException(status_code=404, detail="Analysis not found")

    features = sample.audio_features

    return {
        "sample_id": sample_id,
        "bpm": {
            "value": features.bpm,
            "confidence": features.bpm_confidence,
            "estimates": features.analysis_metadata.get("bpm_estimates", []),
            "outliers": features.analysis_metadata.get("bpm_outliers", []),
            "agreement_level": features.analysis_metadata.get("agreement_level")
        },
        "genre": {
            "value": features.genre,
            "confidence": features.genre_confidence,
            "predictions": features.analysis_metadata.get("genre_predictions", [])
        },
        "metadata": features.analysis_metadata
    }
```

**Debug Response Schema:**

```python
# backend/app/schemas/audio_features.py

class BPMDebugInfo(BaseModel):
    """Detailed BPM analysis info."""
    value: Optional[float]
    confidence: Optional[int]
    estimates: List[dict]
    outliers: List[dict]
    agreement_level: Optional[str]


class GenreDebugInfo(BaseModel):
    """Detailed genre analysis info."""
    value: Optional[str]
    confidence: Optional[int]
    predictions: List[dict]


class AnalysisDebugResponse(BaseModel):
    """Full analysis debug information."""
    sample_id: int
    bpm: BPMDebugInfo
    genre: GenreDebugInfo
    metadata: dict
```

**Frontend Updates:**

```html
<!-- frontend/templates/partials/sample-card.html -->

<div class="sample-card">
  <h3>{{ sample.filename }}</h3>

  <!-- BPM with confidence indicator -->
  <div class="bpm-info">
    <span class="bpm-value">{{ sample.bpm }} BPM</span>
    {% if sample.bpm_confidence %}
      {% if sample.bpm_confidence >= 80 %}
        <span class="badge badge-success">✓ High Confidence</span>
      {% elif sample.bpm_confidence >= 50 %}
        <span class="badge badge-warning">⚠ Medium Confidence</span>
      {% else %}
        <span class="badge badge-error">⚠ Low Confidence - Review</span>
      {% endif %}
    {% endif %}
  </div>

  <!-- Genre with confidence -->
  <div class="genre-info">
    <span class="genre-value">{{ sample.genre }}</span>
    {% if sample.genre_confidence %}
      <span class="confidence-score">{{ sample.genre_confidence }}%</span>
    {% endif %}
  </div>

  <!-- Debug link (optional) -->
  <a href="/samples/{{ sample.id }}/debug" class="text-sm">View Analysis Details</a>
</div>
```

**Alpine.js Confidence Indicator:**

```javascript
// frontend/static/js/confidence-indicator.js

function confidenceColor(confidence) {
  if (confidence >= 80) return 'success';
  if (confidence >= 50) return 'warning';
  return 'error';
}

function confidenceIcon(confidence) {
  if (confidence >= 80) return '✓';
  if (confidence >= 50) return '⚠';
  return '⚠';
}

function confidenceText(confidence) {
  if (confidence >= 80) return 'High Confidence';
  if (confidence >= 50) return 'Medium Confidence';
  return 'Low Confidence - Review Needed';
}
```

**Steps:**
1. Update sample API endpoint to include confidence
2. Create `/analysis-debug` endpoint
3. Create debug response schemas
4. Update frontend templates with confidence indicators
5. Add CSS for confidence badges
6. Test API responses

**Deliverables:**
- [ ] API returns confidence scores
- [ ] Debug endpoint created
- [ ] Frontend shows confidence indicators
- [ ] Visual warnings for low confidence
- [ ] Documentation updated

**Files Modified:**
- `backend/app/api/v1/endpoints/samples.py`
- `backend/app/schemas/audio_features.py`
- `frontend/templates/partials/sample-card.html`

**Files Created:**
- `frontend/static/js/confidence-indicator.js`
- `frontend/pages/sample-debug.html` (optional)

---

## UI MOCKUPS

### Sample Card with Confidence Indicators

```
┌─────────────────────────────────────────┐
│ 🎵 kick_808_hard.wav                    │
├─────────────────────────────────────────┤
│ BPM: 90.5 [✓ High Confidence]           │
│ Genre: Hip-Hop [72% confidence]         │
│ Key: C minor                            │
│                                         │
│ [View Details] [Download] [Add to Kit] │
└─────────────────────────────────────────┘
```

### Low Confidence Warning

```
┌─────────────────────────────────────────┐
│ 🎵 weird_loop.wav                       │
├─────────────────────────────────────────┤
│ BPM: 125.0 [⚠ Low Confidence]           │
│ ⚠️ Analysis uncertain - manual review   │
│    recommended                          │
│                                         │
│ [View Analysis Details] [Override BPM] │
└─────────────────────────────────────────┘
```

### Debug View

```
Analysis Debug Information
━━━━━━━━━━━━━━━━━━━━━━━━━━

BPM Analysis
  Final: 90.5 BPM (confidence: 87)
  Agreement: High

  Estimates:
  ✓ Essentia: 90.5 BPM (confidence: 0.92)
  ✓ Librosa: 90.0 BPM (confidence: 0.65)

  Outliers Removed: None

Genre Analysis
  Final: Hip-Hop (confidence: 72)

  Top 3 Predictions:
  1. Hip-Hop: 72%
  2. Boom Bap: 18%
  3. Lo-Fi: 6%

Full Metadata: [JSON view]
```

---

## TESTING STRATEGY

### Database Tests

```python
# backend/tests/models/test_audio_features.py

def test_audio_features_with_confidence():
    """Test AudioFeatures model with confidence fields."""
    features = AudioFeatures(
        bpm=90.5,
        bpm_confidence=87,
        genre="Hip-Hop",
        genre_confidence=72,
        analysis_metadata={
            "bpm_estimates": [
                {"bpm": 90.5, "confidence": 0.92, "analyzer": "essentia"}
            ],
            "agreement_level": "high"
        }
    )
    assert features.bpm_confidence == 87
    assert features.analysis_metadata["agreement_level"] == "high"
```

### API Tests

```python
# backend/tests/api/test_samples.py

@pytest.mark.asyncio
async def test_get_sample_with_confidence(client):
    """Test sample API returns confidence scores."""
    response = await client.get("/api/v1/samples/1")
    assert response.status_code == 200
    data = response.json()
    assert "bpm_confidence" in data
    assert 0 <= data["bpm_confidence"] <= 100

@pytest.mark.asyncio
async def test_analysis_debug_endpoint(client):
    """Test debug endpoint returns full metadata."""
    response = await client.get("/api/v1/samples/1/analysis-debug")
    assert response.status_code == 200
    data = response.json()
    assert "bpm" in data
    assert "estimates" in data["bpm"]
    assert "agreement_level" in data["bpm"]
```

### Frontend Tests

```javascript
// frontend/tests/e2e/test-confidence-indicators.spec.js

test('confidence indicators display correctly', async ({ page }) => {
  await page.goto('/samples');

  // High confidence should show green badge
  const highConfidenceBadge = page.locator('.badge-success').first();
  await expect(highConfidenceBadge).toBeVisible();
  await expect(highConfidenceBadge).toContainText('High Confidence');

  // Low confidence should show warning
  const lowConfidenceWarning = page.locator('.badge-error').first();
  await expect(lowConfidenceWarning).toBeVisible();
  await expect(lowConfidenceWarning).toContainText('Low Confidence');
});
```

---

## SUCCESS CRITERIA

- [x] `bpm_confidence` and `genre_confidence` fields in database
- [x] `analysis_metadata` JSON field stores all estimates
- [x] Migration runs successfully on existing database
- [x] API returns confidence scores with every response
- [x] `/analysis-debug` endpoint provides full metadata
- [x] UI shows confidence indicators
- [x] Visual warnings for low confidence (<50)
- [x] All tests passing
- [x] Documentation updated

---

## ROLLOUT PLAN

### Step 1: Database Migration
1. Create migration script
2. Test on development database
3. Backup production database
4. Run migration on production
5. Verify all tables updated

### Step 2: API Updates
1. Update models and schemas
2. Test API endpoints locally
3. Deploy API changes
4. Verify responses include confidence

### Step 3: Frontend Updates
1. Update templates with confidence indicators
2. Test UI locally
3. Deploy frontend changes
4. Verify indicators display correctly

### Step 4: Backfill Existing Data (Optional)
1. Re-analyze existing samples to add confidence scores
2. Run batch update script
3. Verify metadata populated

---

## NEXT STEPS AFTER COMPLETION

All phases complete! System now has:
1. ✅ Essentia integration (Phase 2)
2. ✅ Multi-library consensus (Phase 3)
3. ✅ Confidence scoring and metadata (Phase 5)

**Recommended Next Steps:**
1. Collect accuracy metrics from production
2. Fine-tune confidence scoring formula
3. Add manual override workflow
4. Implement learning from corrections
5. Consider Phase 1 (octave correction) as optimization
6. Consider Phase 4 (genre taxonomy) for better genre mapping
