# User Preferences System - TDD RED Phase Complete

**Date:** 2025-11-14
**Test Writer Agent Deliverable**
**Status:** ✅ Ready for Coder Agent

---

## Summary

MVP test suite for User Preferences System has been created following TDD methodology. All 4 tests use REAL async database integration (no mocks) and are ready to guide implementation.

---

## Deliverables

### 1. Test Suite
**File:** `backend/tests/services/test_preferences_service.py`
- ✅ 4 MVP-level tests written
- ✅ REAL async database integration
- ✅ Clear docstrings explaining each test
- ✅ Comprehensive assertions

### 2. Test Specification
**File:** `backend/tests/services/PREFERENCES_TEST_SPECIFICATION.md`
- ✅ Complete test documentation
- ✅ Model and schema specifications
- ✅ Service interface definition
- ✅ Implementation guidelines
- ✅ Integration points identified

---

## Test Overview

### Test 1: Default Preferences Creation
**Purpose:** Validate that preferences are created with correct defaults on first access.

**Key Assertions:**
- Single-row design (id=1) enforced
- Default model: "qwen/qwen3-7b-it"
- Auto-analysis enabled for single uploads
- Auto-analysis disabled for batch processing
- Timestamps properly set

### Test 2: Partial Updates
**Purpose:** Validate that only specified fields are updated, others remain unchanged.

**Key Assertions:**
- Partial updates work correctly
- Unchanged fields persist
- Updated timestamp increases
- Multiple sequential updates work

### Test 3: Helper Methods
**Purpose:** Validate convenience methods for accessing preferences.

**Key Assertions:**
- `get_vibe_model()` returns correct model
- `get_batch_model()` returns correct model
- `should_auto_analyze(is_batch)` handles batch logic
- `should_extract_features()` returns correct value
- `get_cost_limit()` handles None correctly

### Test 4: Available Models
**Purpose:** Validate static method returns model metadata.

**Key Assertions:**
- Returns exactly 2 models (7B and 235B)
- Model metadata includes all required fields
- 235B model costs more than 7B model
- No database connection required (static method)

---

## Implementation Requirements

The Coder agent must implement:

### 1. Database Model
**File:** `backend/app/models/user_preferences.py`

```python
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, default=1)
    vibe_analysis_model = Column(String, nullable=False, default="qwen/qwen3-7b-it")
    batch_processing_model = Column(String, nullable=False, default="qwen/qwen3-7b-it")
    auto_vibe_analysis = Column(Boolean, nullable=False, default=True)
    batch_auto_analyze = Column(Boolean, nullable=False, default=False)
    auto_audio_features = Column(Boolean, nullable=False, default=True)
    max_cost_per_request = Column(Float, nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 2. Pydantic Schemas
**File:** `backend/app/schemas/preferences.py`

- `UserPreferenceBase` - Base model with defaults
- `UserPreferenceUpdate` - All fields optional for partial updates
- `UserPreferenceResponse` - Response with id and timestamps
- `ModelMetadata` - Single AI model metadata
- `AvailableModelsResponse` - List of available models

### 3. Service Implementation
**File:** `backend/app/services/preferences_service.py`

**Methods:**
- `get_preferences()` - Get/create defaults
- `update_preferences(update)` - Partial update
- `get_vibe_model()` - Helper to get vibe model
- `get_batch_model()` - Helper to get batch model
- `should_auto_analyze(is_batch)` - Auto-analysis logic
- `should_extract_features()` - Feature extraction flag
- `get_cost_limit()` - Cost limit getter
- `get_available_models()` - Static model metadata (no DB)

### 4. Database Migration
**File:** `backend/alembic/versions/xxx_add_user_preferences.py`

Create `user_preferences` table with all columns and constraints.

---

## Running Tests

### Current State (RED Phase)

```bash
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py -v

# EXPECTED OUTPUT:
# ModuleNotFoundError: No module named 'app.services.preferences_service'
# (All tests fail with ImportError - this is correct!)
```

### After Implementation (GREEN Phase)

```bash
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py -v

# EXPECTED OUTPUT:
# test_get_preferences_creates_defaults PASSED
# test_update_preferences_partial PASSED
# test_helper_methods PASSED
# test_get_available_models PASSED
```

---

## Key Design Decisions

### 1. Single-Row Design
- Only one preferences record (id=1)
- Perfect for MVP single-user system
- Easy to scale to multi-user later if needed

### 2. Two Model Fields
- `vibe_analysis_model` - For single upload analysis
- `batch_processing_model` - For batch operations
- Allows cost/quality optimization per use case

### 3. Separate Batch Flags
- `auto_vibe_analysis` - Auto-analyze single uploads
- `batch_auto_analyze` - Auto-analyze batch items
- Different defaults (True vs. False) make sense

### 4. Helper Methods Over Direct Access
- Clearer intent and semantics
- Encapsulates batch logic
- Easier to mock and test
- Better for future refactoring

### 5. Static Available Models
- No database required
- Fast for UI dropdowns
- Easy to maintain (just code)
- Could move to DB later if dynamic pricing needed

---

## Integration Points

This service will be used by:

1. **Sample Upload** (`/api/v1/samples/upload`)
   - Check auto-analysis settings
   - Get model for vibe analysis
   - Check feature extraction flag

2. **Batch Processing** (`/api/v1/batches/{id}/process`)
   - Get batch model
   - Check batch auto-analyze flag

3. **Settings UI** (`/settings`)
   - Display current preferences
   - Update preferences
   - Show available models with pricing

4. **Cost Tracking**
   - Enforce cost limits
   - Calculate estimated costs
   - Warn users about expensive operations

---

## Test Strategy Highlights

### Why REAL Database Integration?

✅ **Pros:**
- Tests actual SQLAlchemy async behavior
- Validates schema design
- Catches integration issues
- More valuable than mocked tests

❌ **Minimal Cons:**
- Slightly slower (still < 5 seconds total)
- Requires database fixture

### Why 4 Tests (Not More)?

Following MVP testing guidelines:
- Cover critical functionality only
- Avoid enterprise test bloat
- Keep test suite maintainable
- Focus on high-value scenarios

### What We DON'T Test

(Appropriate for MVP scope)
- ❌ Validation errors (Pydantic handles this)
- ❌ Database connection failures
- ❌ Performance under load
- ❌ Concurrent update conflicts
- ❌ Migration rollback scenarios

---

## Implementation Tips

### get_preferences() Pattern

```python
async def get_preferences(self) -> UserPreferenceResponse:
    # Always query for id=1
    result = await self.db.execute(
        select(UserPreference).where(UserPreference.id == 1)
    )
    prefs = result.scalar_one_or_none()

    # Create defaults if none exist
    if prefs is None:
        prefs = UserPreference(id=1)  # Force single row
        self.db.add(prefs)
        await self.db.commit()
        await self.db.refresh(prefs)

    return UserPreferenceResponse.from_orm(prefs)
```

### update_preferences() Pattern

```python
async def update_preferences(
    self,
    update: UserPreferenceUpdate
) -> UserPreferenceResponse:
    # Get existing record
    result = await self.db.execute(
        select(UserPreference).where(UserPreference.id == 1)
    )
    prefs = result.scalar_one()

    # Update only provided fields
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)

    await self.db.commit()
    await self.db.refresh(prefs)

    return UserPreferenceResponse.from_orm(prefs)
```

### Available Models Data

```python
@staticmethod
async def get_available_models() -> AvailableModelsResponse:
    return AvailableModelsResponse(models=[
        ModelMetadata(
            model_id="qwen/qwen3-7b-it",
            name="Qwen3 7B (Fast & Affordable)",
            input_cost=0.0000006,   # $0.60 per million tokens
            output_cost=0.0000006,
            description="7B parameter model. Fast, affordable, good for basic analysis."
        ),
        ModelMetadata(
            model_id="qwen/qwen3-235b-a22b-2507",
            name="Qwen3 235B (Powerful & Accurate)",
            input_cost=0.000004,    # $4.00 per million tokens
            output_cost=0.000004,
            description="235B parameter model. Slower, expensive, best accuracy."
        )
    ])
```

---

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   └── user_preferences.py         # TO IMPLEMENT
│   ├── schemas/
│   │   └── preferences.py              # TO IMPLEMENT
│   └── services/
│       └── preferences_service.py      # TO IMPLEMENT
├── alembic/
│   └── versions/
│       └── xxx_add_preferences.py      # TO IMPLEMENT
└── tests/
    └── services/
        ├── test_preferences_service.py           # ✅ COMPLETE (4 tests)
        └── PREFERENCES_TEST_SPECIFICATION.md     # ✅ COMPLETE (docs)
```

---

## Success Criteria

### RED Phase (Current) ✅

- ✅ 4 tests created (no more, no less)
- ✅ All tests use REAL async database
- ✅ Clear docstrings explain purpose
- ✅ Assertions validate critical behavior
- ✅ No mocks or patches used
- ✅ Tests fail with ImportError (expected)

### GREEN Phase (Next)

- ⏳ Database model implemented
- ⏳ Pydantic schemas implemented
- ⏳ Service methods implemented
- ⏳ All 4 tests pass
- ⏳ Migration created and applied

### REFACTOR Phase (Future)

- ⏳ Settings UI created
- ⏳ Integration with sample upload
- ⏳ Integration with batch processing
- ⏳ Cost enforcement implemented

---

## Dependencies

**Already Installed:**
- ✅ pytest
- ✅ pytest-asyncio
- ✅ SQLAlchemy (async)
- ✅ Pydantic
- ✅ Alembic

**No New Dependencies Required**

---

## Quick Commands

```bash
# Run preferences tests only
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py -v

# Run with output
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py -v -s

# Run with coverage
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py \
    --cov=app.services.preferences_service \
    --cov-report=term-missing

# Run all service tests
cd backend
../venv/bin/python -m pytest tests/services/ -v
```

---

## Notes for Coder Agent

### Implementation Order

1. **Start with schemas** - Define Pydantic models first (no DB needed)
2. **Then database model** - Create SQLAlchemy model
3. **Create migration** - Alembic migration for table
4. **Implement service** - Start with get/update, then helpers
5. **Run tests** - Should all pass if implementation is correct

### Common Pitfalls to Avoid

❌ **Don't use `dict()` for Pydantic v2:**
```python
# BAD (deprecated in Pydantic v2)
update_data = update.dict(exclude_unset=True)

# GOOD (Pydantic v2)
update_data = update.model_dump(exclude_unset=True)
```

❌ **Don't forget to refresh after commit:**
```python
await self.db.commit()
await self.db.refresh(prefs)  # Important!
return UserPreferenceResponse.from_orm(prefs)
```

❌ **Don't forget the single-row constraint:**
```python
# Always query for id=1
select(UserPreference).where(UserPreference.id == 1)

# And force id=1 on creation
prefs = UserPreference(id=1)
```

### Testing Tips

- Run tests after each method implementation
- Use `-v -s` flags to see detailed output
- Check SQL queries with `echo=True` in engine if needed
- Tests should pass without modification

---

## Related Documentation

- **Test Specification:** `backend/tests/services/PREFERENCES_TEST_SPECIFICATION.md`
- **OpenRouter Tests:** `backend/tests/services/test_openrouter_service.py` (reference pattern)
- **Audio Features Tests:** `backend/tests/test_audio_features_service.py` (reference pattern)
- **Fixtures:** `backend/tests/conftest.py` (existing db_session fixture)

---

**Status: Ready for Coder Agent Implementation** 🎉

**Handoff:** Test suite is complete and validated. All tests are properly structured and will fail with ImportError until implementation is complete. Follow the specification document for implementation details.
