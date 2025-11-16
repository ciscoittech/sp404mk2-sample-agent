# Confidence Scoring & Metadata - Context

**Feature:** Add confidence scores and analysis metadata to database and UI
**Phase:** 5 of 5 (Final Phase)
**Status:** Ready to Implement
**Created:** 2025-11-15
**Dependencies:** Phase 3 (Cross-Validation Logic) must be complete

---

## Why Confidence Scoring Matters

### The Problem
Without confidence scores, users can't distinguish between:
- **High-confidence predictions:** 90 BPM detected by 2 algorithms agreeing within ±1 BPM
- **Low-confidence predictions:** 90 BPM detected by 1 algorithm with low internal confidence

This leads to:
- Users trusting wrong predictions
- Manual review of all samples (inefficient)
- No way to prioritize which samples need attention

### The Solution
Explicit confidence scores (0-100) that tell users:
- **90+ confidence:** Trust this prediction
- **50-80 confidence:** Probably correct, verify if critical
- **<50 confidence:** Likely wrong, needs manual review

---

## Key Decisions

### 1. Integer Confidence Scale (0-100)
**Decision:** Use 0-100 integer scale, not 0.0-1.0 float
**Rationale:**
- More intuitive for users (like a percentage)
- No floating-point display issues
- Easier to show in UI badges/colors
- Standard across BPM, genre, key predictions

### 2. JSON Metadata Field
**Decision:** Store all analysis details in single JSON column
**Rationale:**
- Flexibility to store any metadata structure
- No schema changes for new analyzer features
- Easy to query and display in debug view
- PostgreSQL/SQLite both support JSON columns

### 3. Non-Nullable Confidence Fields
**Decision:** Allow null confidence (backward compatibility)
**Rationale:**
- Existing samples don't have confidence scores
- Null = "not analyzed with new system"
- Can backfill later with re-analysis
- Graceful migration path

### 4. Separate Debug Endpoint
**Decision:** Create `/analysis-debug` instead of adding to main response
**Rationale:**
- Main API stays lightweight
- Debug info is verbose (all estimates, outliers, etc.)
- Most users don't need full metadata
- Developers/power users can access when needed

---

## Architecture Notes

### Database Schema

**New Fields:**
- `bpm_confidence: Integer (0-100)` - Unified confidence for BPM prediction
- `genre_confidence: Integer (0-100)` - Unified confidence for genre classification
- `key_confidence: Integer (0-100)` - Future use for key detection
- `analysis_metadata: JSON` - Full analysis details

**Metadata Structure:**
```json
{
  "bpm_estimates": [
    {
      "bpm": 90.5,
      "confidence": 0.92,
      "analyzer": "essentia",
      "method": "rhythm_extractor_2013"
    },
    {
      "bpm": 90.0,
      "confidence": 0.65,
      "analyzer": "librosa",
      "method": "beat_track"
    }
  ],
  "bpm_outliers": [],
  "agreement_level": "high",
  "num_algorithms": 2,
  "genre_predictions": [
    {"genre": "Hip-Hop", "confidence": 0.72},
    {"genre": "Boom Bap", "confidence": 0.18},
    {"genre": "Lo-Fi", "confidence": 0.06}
  ],
  "analyzer_versions": {
    "essentia": "2.1-beta6",
    "librosa": "0.10.1"
  }
}
```

### API Response Format

**Standard Response (Lightweight):**
```json
{
  "id": 123,
  "filename": "kick_808.wav",
  "bpm": 90.5,
  "bpm_confidence": 87,
  "genre": "Hip-Hop",
  "genre_confidence": 72,
  "key": "C minor"
}
```

**Debug Response (Detailed):**
```json
{
  "sample_id": 123,
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
  "genre": {
    "value": "Hip-Hop",
    "confidence": 72,
    "predictions": [
      {"genre": "Hip-Hop", "confidence": 0.72},
      {"genre": "Boom Bap", "confidence": 0.18}
    ]
  },
  "metadata": { ... }
}
```

---

## UI Design Principles

### Confidence Indicators

**Color Coding:**
- **Green (✓):** High confidence (80-100) - Trust this
- **Yellow (⚠):** Medium confidence (50-79) - Verify if important
- **Red (⚠):** Low confidence (0-49) - Manual review needed

**Visual Treatment:**
```
BPM: 90.5 [✓ High Confidence]        ← Green badge
BPM: 125.0 [⚠ Medium Confidence]     ← Yellow badge
BPM: 60.0 [⚠ Low Confidence - Review] ← Red badge
```

### Progressive Disclosure
- **Default view:** Show confidence badge only
- **Hover/click:** Show confidence percentage
- **Debug link:** Full analysis details

---

## Key Files

### Files to Modify
- `backend/app/models/audio_features.py` - Add fields
- `backend/app/schemas/audio_features.py` - Update schemas
- `backend/app/api/v1/endpoints/samples.py` - Add confidence to responses
- `backend/app/services/audio_features_service.py` - Store confidence in database
- `frontend/templates/partials/sample-card.html` - Add UI indicators

### Files to Create
- `backend/alembic/versions/XXX_add_confidence_fields.py` - Migration
- `frontend/static/js/confidence-indicator.js` - UI helper functions
- `frontend/pages/sample-debug.html` - Debug view (optional)

---

## Migration Strategy

### Backward Compatibility
- Existing samples: `bpm_confidence = NULL`
- New samples: `bpm_confidence = 0-100`
- API handles both: Show confidence if available, hide if null

### Backfill Strategy (Optional)
```python
# backend/scripts/backfill_confidence.py

async def backfill_confidence_scores():
    """Re-analyze all samples to add confidence scores."""
    samples = await db.query(Sample).filter(Sample.bpm_confidence == None).all()

    for sample in samples:
        # Re-analyze with new system
        consensus = await audio_service.analyze_bpm_consensus(sample.file_path)

        # Update confidence
        sample.bpm_confidence = consensus.confidence
        sample.analysis_metadata = {...}

    await db.commit()
```

**Decision:** Backfill not required initially, do on-demand or gradually

---

## UI Implementation

### DaisyUI Badge Components

```html
<!-- High Confidence (green) -->
<span class="badge badge-success gap-2">
  <svg>...</svg> High Confidence
</span>

<!-- Medium Confidence (yellow) -->
<span class="badge badge-warning gap-2">
  <svg>...</svg> Medium Confidence
</span>

<!-- Low Confidence (red) -->
<span class="badge badge-error gap-2">
  <svg>...</svg> Low Confidence - Review
</span>
```

### Alpine.js Reactive Indicators

```html
<div x-data="{ confidence: {{ sample.bpm_confidence }} }">
  <span :class="{
    'badge-success': confidence >= 80,
    'badge-warning': confidence >= 50 && confidence < 80,
    'badge-error': confidence < 50
  }" class="badge">
    <span x-text="confidence >= 80 ? '✓ High' : (confidence >= 50 ? '⚠ Medium' : '⚠ Low')"></span>
  </span>
</div>
```

---

## Performance Considerations

### Database Indexing
```sql
-- Not needed: confidence is not frequently queried for filtering
-- JSON metadata is for display only, not filtering
```

### API Response Size
- Standard response: +20 bytes per sample (2 int fields)
- Debug response: +500-1000 bytes (full metadata)
- Impact: Negligible for <1000 samples per page

### Frontend Rendering
- Badges render fast (DaisyUI is optimized)
- Alpine.js reactive updates are efficient
- No performance impact expected

---

## Testing Strategy

### Database Migration Testing
1. Test migration on empty database
2. Test migration on database with existing samples
3. Verify null constraints work
4. Test rollback

### API Testing
1. Test sample response includes confidence
2. Test debug endpoint returns metadata
3. Test with null confidence (backward compatibility)
4. Test with invalid sample_id (404)

### UI Testing
1. Test confidence badges render correctly
2. Test color coding (green/yellow/red)
3. Test with null confidence (badge hidden)
4. Test debug link navigation

---

## Success Metrics

### Database
- All new samples have confidence scores
- Migration runs without errors
- Existing samples have null confidence (backward compatible)

### API
- Every sample response includes confidence (if available)
- Debug endpoint returns full metadata
- Response time <100ms (no degradation)

### UI
- Confidence indicators visible on all sample cards
- Color coding matches confidence level
- Low-confidence warnings prominent
- Debug view accessible

---

## Risks & Mitigations

### Risk: Migration Fails on Production
**Mitigation:**
- Test thoroughly on development database
- Backup production database before migration
- Have rollback script ready
- Run migration during low-traffic period

### Risk: UI Overwhelms Users with Warnings
**Mitigation:**
- Use subtle badges (not big warnings)
- Make warnings actionable ("Review needed")
- Progressive disclosure (debug view optional)

### Risk: Confidence Scores Inaccurate
**Mitigation:**
- Calibrate on test dataset first
- Monitor accuracy in production
- Adjust formula if needed
- Allow manual override

---

## Future Enhancements

### Manual Override Workflow
1. User clicks "Override BPM"
2. Enters correct BPM
3. System stores override
4. Learns from correction (future ML)

### Confidence Trend Analysis
- Track confidence distribution over time
- Identify systematic errors
- Fine-tune scoring formula

### Batch Review Interface
- Filter by low confidence (<50)
- Bulk review and correction
- Export corrections for retraining

---

## Next Steps After Completion

Phase 5 is the final phase! After completion:
1. System has Essentia integration (Phase 2)
2. Multi-library consensus (Phase 3)
3. Confidence scoring (Phase 5)

**System is production-ready for:**
- High-accuracy BPM detection (90-95%)
- Genre classification (80-85%)
- Confidence-aware predictions
- Transparent analysis metadata

**Recommended Post-Launch:**
1. Monitor accuracy metrics
2. Collect user feedback on confidence indicators
3. Fine-tune confidence formula if needed
4. Consider Phase 1 (octave correction) if still seeing errors
5. Consider Phase 4 (genre taxonomy) for better mapping

---

## Notes

- Confidence scores are for user information, not filtering criteria
- Metadata is stored for transparency and debugging
- UI should be subtle (badges, not alerts)
- Migration is backward-compatible (nullable fields)
- Debug endpoint is opt-in (power users only)
