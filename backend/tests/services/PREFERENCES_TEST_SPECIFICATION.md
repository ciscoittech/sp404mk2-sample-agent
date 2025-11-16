# User Preferences Service - Test Specification

**Test Writer Agent Deliverable**
**Date:** 2025-11-14
**Status:** RED Phase (Tests Written, Implementation Pending)

---

## Overview

This document specifies the test suite for the User Preferences System, which allows users to configure:
- AI model selection (vibe analysis and batch processing)
- Auto-analysis behavior (single upload vs. batch)
- Audio feature extraction settings
- Cost limits per API request

### Design Pattern: Single-Row Configuration

The preferences system uses a **single-row design** with `id=1`, following the pattern:
- Only one preferences record exists in the database
- First access creates defaults if none exist
- Updates always modify the same row (id=1)
- No multi-user preferences (MVP scope)

---

## Test Suite Structure

### File: `backend/tests/services/test_preferences_service.py`

**Test Count:** 4 MVP-level tests
**Integration Type:** REAL async database (no mocks)
**Dependencies:** SQLAlchemy async session, Pydantic schemas

---

## Test Details

### Test 1: `test_get_preferences_creates_defaults`

**Purpose:** Validate default preferences creation on first access.

**What It Tests:**
- Service creates default preferences if none exist
- Default values match expected configuration
- Database round-trip works correctly
- Single-row design (id=1) is enforced
- Timestamps are properly set

**Expected Default Values:**
```python
{
    "id": 1,
    "vibe_analysis_model": "qwen/qwen3-7b-it",      # Cheaper model
    "auto_vibe_analysis": True,                      # Analyze on upload
    "auto_audio_features": True,                     # Extract features
    "batch_processing_model": "qwen/qwen3-7b-it",   # Same as vibe
    "batch_auto_analyze": False,                     # No batch auto-analyze
    "max_cost_per_request": None,                    # No cost limit
    "created_at": <datetime>,
    "updated_at": <datetime>
}
```

**Assertions:**
- Response is `UserPreferenceResponse` instance
- All default fields match expected values
- Timestamps exist and are valid
- ID is always 1 (single-row design)

---

### Test 2: `test_update_preferences_partial`

**Purpose:** Validate partial update functionality.

**What It Tests:**
- Partial updates work (only specified fields change)
- Unchanged fields remain the same
- Database persistence across service calls
- `updated_at` timestamp changes on update
- Multiple sequential updates work correctly

**Test Flow:**
1. Get initial default preferences
2. Update only `vibe_analysis_model` to "qwen/qwen3-235b-a22b-2507"
3. Verify only that field changed, others unchanged
4. Verify `updated_at` increased
5. Update different field (`batch_auto_analyze` to True)
6. Verify both updates persisted
7. Verify `updated_at` increased again

**Assertions:**
- Updated field reflects new value
- All other fields remain unchanged
- `updated_at` timestamp increases on each update
- Cumulative updates persist correctly

---

### Test 3: `test_helper_methods`

**Purpose:** Validate convenience helper methods.

**What It Tests:**
- `get_vibe_model()` returns `vibe_analysis_model` value
- `get_batch_model()` returns `batch_processing_model` value
- `should_auto_analyze(is_batch=False)` returns `auto_vibe_analysis`
- `should_auto_analyze(is_batch=True)` returns `batch_auto_analyze`
- `should_extract_features()` returns `auto_audio_features`
- `get_cost_limit()` returns `max_cost_per_request` (can be None)

**Test Setup:**
```python
# Set specific preferences for testing
await service.update_preferences(UserPreferenceUpdate(
    vibe_analysis_model="qwen/qwen3-235b-a22b-2507",
    batch_processing_model="qwen/qwen3-7b-it",
    auto_vibe_analysis=True,
    batch_auto_analyze=False,
    auto_audio_features=True,
    max_cost_per_request=0.05
))
```

**Assertions:**
- Each helper method returns correct value
- Batch vs. single upload logic is correct
- Cost limit handles None correctly

**Rationale:**
Helper methods provide:
- Clearer semantics than direct field access
- Simplified usage in other services
- Encapsulation of preference logic

---

### Test 4: `test_get_available_models`

**Purpose:** Validate static model metadata retrieval.

**What It Tests:**
- Static method works without database connection
- Returns exactly 2 models (7B and 235B)
- Model metadata includes all required fields
- Both expected models are present
- Pricing reflects model complexity (235B > 7B)

**Expected Models:**
```python
[
    {
        "model_id": "qwen/qwen3-7b-it",
        "name": "Qwen3 7B (Fast & Affordable)",
        "input_cost": 0.0000006,   # $0.60 per million tokens
        "output_cost": 0.0000006,
        "description": "7B parameter model. Fast, affordable, good for basic analysis."
    },
    {
        "model_id": "qwen/qwen3-235b-a22b-2507",
        "name": "Qwen3 235B (Powerful & Accurate)",
        "input_cost": 0.000004,    # $4.00 per million tokens
        "output_cost": 0.000004,
        "description": "235B parameter model. Slower, expensive, best accuracy."
    }
]
```

**Assertions:**
- Response is `AvailableModelsResponse` instance
- Exactly 2 models returned
- Both model IDs present
- All metadata fields exist and valid
- 235B costs more than 7B (both input and output)

**Usage:**
This static method provides UI with:
- Available model options for dropdowns
- Pricing information for cost estimation
- Model descriptions for user guidance

---

## Models and Schemas

### Database Model: `backend/app/models/user_preferences.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class UserPreference(Base):
    """
    User preferences for AI model selection and auto-analysis behavior.

    Single-row design: Always use id=1 for the global preferences.
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, default=1)

    # Model Selection
    vibe_analysis_model = Column(
        String,
        nullable=False,
        default="qwen/qwen3-7b-it"
    )
    batch_processing_model = Column(
        String,
        nullable=False,
        default="qwen/qwen3-7b-it"
    )

    # Auto-Analysis Settings
    auto_vibe_analysis = Column(Boolean, nullable=False, default=True)
    batch_auto_analyze = Column(Boolean, nullable=False, default=False)
    auto_audio_features = Column(Boolean, nullable=False, default=True)

    # Cost Controls
    max_cost_per_request = Column(Float, nullable=True, default=None)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
```

### Pydantic Schemas: `backend/app/schemas/preferences.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserPreferenceBase(BaseModel):
    """Base model for user preferences."""
    vibe_analysis_model: str = Field(default="qwen/qwen3-7b-it")
    auto_vibe_analysis: bool = Field(default=True)
    auto_audio_features: bool = Field(default=True)
    batch_processing_model: str = Field(default="qwen/qwen3-7b-it")
    batch_auto_analyze: bool = Field(default=False)
    max_cost_per_request: Optional[float] = Field(default=None, ge=0.0)


class UserPreferenceUpdate(BaseModel):
    """Model for updating preferences. All fields optional for partial updates."""
    vibe_analysis_model: Optional[str] = Field(default=None)
    auto_vibe_analysis: Optional[bool] = Field(default=None)
    auto_audio_features: Optional[bool] = Field(default=None)
    batch_processing_model: Optional[str] = Field(default=None)
    batch_auto_analyze: Optional[bool] = Field(default=None)
    max_cost_per_request: Optional[float] = Field(default=None, ge=0.0)


class UserPreferenceResponse(UserPreferenceBase):
    """Response model with database fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelMetadata(BaseModel):
    """Metadata for a single AI model."""
    model_id: str
    name: str
    input_cost: float  # Cost per token
    output_cost: float  # Cost per token
    description: str


class AvailableModelsResponse(BaseModel):
    """Response with available AI models and their metadata."""
    models: list[ModelMetadata]
```

---

## Service Interface

### File: `backend/app/services/preferences_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.user_preferences import UserPreference
from app.schemas.preferences import (
    UserPreferenceResponse,
    UserPreferenceUpdate,
    AvailableModelsResponse,
    ModelMetadata
)


class PreferencesService:
    """Service for managing user preferences."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_preferences(self) -> UserPreferenceResponse:
        """
        Get user preferences, creating defaults if none exist.

        Returns:
            UserPreferenceResponse with current preferences
        """
        # Implementation needed

    async def update_preferences(
        self,
        update: UserPreferenceUpdate
    ) -> UserPreferenceResponse:
        """
        Update user preferences with partial data.

        Only fields provided in update will be changed.
        Returns updated preferences.

        Args:
            update: UserPreferenceUpdate with fields to change

        Returns:
            UserPreferenceResponse with updated preferences
        """
        # Implementation needed

    async def get_vibe_model(self) -> str:
        """Get the vibe analysis model ID."""
        # Implementation needed

    async def get_batch_model(self) -> str:
        """Get the batch processing model ID."""
        # Implementation needed

    async def should_auto_analyze(self, is_batch: bool = False) -> bool:
        """
        Check if auto-analysis should run for this operation.

        Args:
            is_batch: True if this is a batch operation

        Returns:
            True if auto-analysis should run
        """
        # Implementation needed

    async def should_extract_features(self) -> bool:
        """Check if audio features should be extracted automatically."""
        # Implementation needed

    async def get_cost_limit(self) -> Optional[float]:
        """Get the maximum cost per request, or None if no limit."""
        # Implementation needed

    @staticmethod
    async def get_available_models() -> AvailableModelsResponse:
        """
        Get list of available AI models with metadata.

        Static method - no database required.

        Returns:
            AvailableModelsResponse with model metadata
        """
        # Implementation needed
```

---

## Implementation Guidelines

### 1. Service Implementation Strategy

**get_preferences():**
```python
async def get_preferences(self) -> UserPreferenceResponse:
    # Query for id=1
    result = await self.db.execute(
        select(UserPreference).where(UserPreference.id == 1)
    )
    prefs = result.scalar_one_or_none()

    # Create defaults if none exist
    if prefs is None:
        prefs = UserPreference(id=1)  # Force id=1
        self.db.add(prefs)
        await self.db.commit()
        await self.db.refresh(prefs)

    return UserPreferenceResponse.from_orm(prefs)
```

**update_preferences():**
```python
async def update_preferences(
    self,
    update: UserPreferenceUpdate
) -> UserPreferenceResponse:
    # Get existing preferences
    prefs = await self.get_preferences()

    # Get database object
    result = await self.db.execute(
        select(UserPreference).where(UserPreference.id == 1)
    )
    db_prefs = result.scalar_one()

    # Update only provided fields
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prefs, field, value)

    await self.db.commit()
    await self.db.refresh(db_prefs)

    return UserPreferenceResponse.from_orm(db_prefs)
```

**Helper methods:**
```python
async def get_vibe_model(self) -> str:
    prefs = await self.get_preferences()
    return prefs.vibe_analysis_model

async def should_auto_analyze(self, is_batch: bool = False) -> bool:
    prefs = await self.get_preferences()
    return prefs.batch_auto_analyze if is_batch else prefs.auto_vibe_analysis
```

**Static method:**
```python
@staticmethod
async def get_available_models() -> AvailableModelsResponse:
    models = [
        ModelMetadata(
            model_id="qwen/qwen3-7b-it",
            name="Qwen3 7B (Fast & Affordable)",
            input_cost=0.0000006,
            output_cost=0.0000006,
            description="7B parameter model. Fast, affordable, good for basic analysis."
        ),
        ModelMetadata(
            model_id="qwen/qwen3-235b-a22b-2507",
            name="Qwen3 235B (Powerful & Accurate)",
            input_cost=0.000004,
            output_cost=0.000004,
            description="235B parameter model. Slower, expensive, best accuracy."
        )
    ]
    return AvailableModelsResponse(models=models)
```

### 2. Database Migration

**Alembic Migration:**
```python
def upgrade():
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vibe_analysis_model', sa.String(), nullable=False),
        sa.Column('batch_processing_model', sa.String(), nullable=False),
        sa.Column('auto_vibe_analysis', sa.Boolean(), nullable=False),
        sa.Column('batch_auto_analyze', sa.Boolean(), nullable=False),
        sa.Column('auto_audio_features', sa.Boolean(), nullable=False),
        sa.Column('max_cost_per_request', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
```

### 3. Integration Points

**Where This Service Will Be Used:**

1. **Sample Upload Endpoint** (`/api/v1/samples/upload`)
   - Check `should_auto_analyze(is_batch=False)`
   - Check `should_extract_features()`
   - Get `vibe_model` for analysis

2. **Batch Processing** (`/api/v1/batches/{id}/process`)
   - Check `should_auto_analyze(is_batch=True)`
   - Get `batch_model` for processing

3. **Settings UI** (`/settings`)
   - Display current preferences
   - Update preferences via form
   - Show available models with pricing

4. **Cost Estimation**
   - Use `get_cost_limit()` for warnings
   - Use model metadata for cost calculation

---

## Running Tests

### Current State (RED Phase)

```bash
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py -v

# EXPECTED: All tests fail with ImportError
# ModuleNotFoundError: No module named 'app.services.preferences_service'
# ModuleNotFoundError: No module named 'app.schemas.preferences'
# ModuleNotFoundError: No module named 'app.models.user_preferences'
```

### After Implementation (GREEN Phase)

```bash
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py -v

# EXPECTED: All 4 tests pass
# test_get_preferences_creates_defaults PASSED
# test_update_preferences_partial PASSED
# test_helper_methods PASSED
# test_get_available_models PASSED
```

### With Coverage

```bash
cd backend
../venv/bin/python -m pytest tests/services/test_preferences_service.py \
    --cov=app.services.preferences_service \
    --cov-report=term-missing
```

---

## Success Criteria

### RED Phase (Current) ✅

- ✅ 4 MVP tests written
- ✅ All tests use REAL async database
- ✅ Clear docstrings explain each test
- ✅ Tests fail with ImportError (expected)
- ✅ No mocks used

### GREEN Phase (Next)

- ⏳ Database model created
- ⏳ Pydantic schemas created
- ⏳ Service implemented
- ⏳ All 4 tests pass
- ⏳ Migration created

### Integration Phase (Future)

- ⏳ Settings UI implemented
- ⏳ Sample upload uses preferences
- ⏳ Batch processing uses preferences
- ⏳ Cost limits enforced

---

## Design Rationale

### Why Single-Row Design?

**Pros:**
- Simplifies implementation (no user ID needed)
- Perfect for MVP (single-user system)
- Fast queries (always id=1)
- No cascade deletion concerns

**Future Scaling:**
If multi-user support is needed later:
```sql
ALTER TABLE user_preferences ADD COLUMN user_id INTEGER;
ALTER TABLE user_preferences DROP CONSTRAINT user_preferences_pkey;
ALTER TABLE user_preferences ADD PRIMARY KEY (user_id);
```

### Why Two Model Fields?

Separate `vibe_analysis_model` and `batch_processing_model` because:
- Batch processing may benefit from faster/cheaper model
- Single uploads justify more expensive model for quality
- Gives users flexibility to optimize cost vs. quality

### Why Helper Methods?

Instead of direct field access:
```python
# Bad: Direct access
if prefs.auto_vibe_analysis:
    ...

# Good: Helper method
if await service.should_auto_analyze(is_batch=False):
    ...
```

**Benefits:**
- Clearer intent (`should_auto_analyze` vs. `auto_vibe_analysis`)
- Handles batch logic internally
- Easier to refactor later
- Better for mocking in tests

---

## Next Steps

1. **Coder Agent:** Implement service, models, schemas
2. **Test Agent:** Verify all tests pass
3. **Architect Agent:** Design settings UI
4. **Coder Agent:** Implement settings UI
5. **Integration:** Connect to sample upload and batch processing

---

**Status: Ready for Coder Agent Implementation** 🎉
