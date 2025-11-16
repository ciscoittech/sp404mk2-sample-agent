"""
TDD RED Phase Tests for PreferencesService

These tests define the expected behavior of the User Preferences System before implementation.
Following Test-Driven Development (TDD) RED-GREEN-REFACTOR methodology.

Test Strategy:
- 4 MVP-level tests covering critical functionality
- REAL async database integration (no mocks)
- Tests single-row user preferences (id=1)
- All tests use real database session and PreferencesService

Expected Failures:
- ImportError: PreferencesService module doesn't exist yet
- AttributeError: Methods and models not implemented
- All tests should fail until implementation is complete
"""
import pytest
import pytest_asyncio
from sqlalchemy import select


class TestPreferencesService:
    """MVP test suite for PreferencesService."""

    @pytest.mark.asyncio
    async def test_get_preferences_creates_defaults(self, db_session):
        """
        Test 1: Get preferences creates defaults if none exist.

        Validates:
        - Service creates default preferences on first access
        - Default values match expected configuration
        - Database round-trip works correctly
        - Single-row design (id=1) is enforced

        Expected default values:
        - vibe_analysis_model: "qwen/qwen3-7b-it" (cheaper model)
        - auto_vibe_analysis: True (analyze on upload)
        - auto_audio_features: True (extract features on upload)
        - batch_processing_model: "qwen/qwen3-7b-it" (batch uses same model)
        - batch_auto_analyze: False (no auto-analysis for batch)
        - max_cost_per_request: None (no cost limit by default)
        """
        # Import models (will fail until implemented)
        from app.services.preferences_service import PreferencesService
        from app.schemas.preferences import UserPreferenceResponse

        # Arrange: Create service with clean database
        service = PreferencesService(db_session)

        # Act: Get preferences (should create defaults)
        prefs = await service.get_preferences()

        # Assert: Verify response type
        assert isinstance(prefs, UserPreferenceResponse), \
            "Response must be UserPreferenceResponse instance"

        # Assert: Verify default values
        assert prefs.id == 1, "Must use single-row design with id=1"
        assert prefs.vibe_analysis_model == "qwen/qwen3-7b-it", \
            "Default vibe model should be qwen3-7b-it"
        assert prefs.auto_vibe_analysis is True, \
            "Auto vibe analysis should be enabled by default"
        assert prefs.auto_audio_features is True, \
            "Auto audio features should be enabled by default"
        assert prefs.batch_processing_model == "qwen/qwen3-7b-it", \
            "Default batch model should be qwen3-7b-it"
        assert prefs.batch_auto_analyze is False, \
            "Batch auto-analyze should be disabled by default"
        assert prefs.max_cost_per_request is None, \
            "Cost limit should be None by default"

        # Assert: Verify timestamps exist
        assert prefs.created_at is not None, "Created timestamp must be set"
        assert prefs.updated_at is not None, "Updated timestamp must be set"

    @pytest.mark.asyncio
    async def test_update_preferences_partial(self, db_session):
        """
        Test 2: Update preferences with partial data.

        Validates:
        - Partial updates work (only change specified fields)
        - Unchanged fields remain the same
        - Database persistence across service calls
        - updated_at timestamp changes on update
        - Multiple sequential updates work correctly

        This tests the core update workflow:
        1. Get initial defaults
        2. Update only vibe_analysis_model
        3. Verify only that field changed
        4. Update again with different field
        5. Verify cumulative changes
        """
        # Import models
        from app.services.preferences_service import PreferencesService
        from app.schemas.preferences import UserPreferenceUpdate

        # Arrange: Create service and get initial defaults
        service = PreferencesService(db_session)
        original = await service.get_preferences()

        # Act: Update only vibe_analysis_model
        update_data = UserPreferenceUpdate(
            vibe_analysis_model="qwen/qwen3-235b-a22b-2507"
        )
        updated = await service.update_preferences(update_data)

        # Assert: Verify only specified field changed
        assert updated.vibe_analysis_model == "qwen/qwen3-235b-a22b-2507", \
            "Vibe model should be updated"
        assert updated.auto_vibe_analysis == original.auto_vibe_analysis, \
            "Auto vibe analysis should remain unchanged"
        assert updated.batch_processing_model == original.batch_processing_model, \
            "Batch model should remain unchanged"
        assert updated.batch_auto_analyze == original.batch_auto_analyze, \
            "Batch auto-analyze should remain unchanged"
        assert updated.auto_audio_features == original.auto_audio_features, \
            "Auto audio features should remain unchanged"
        assert updated.max_cost_per_request == original.max_cost_per_request, \
            "Cost limit should remain unchanged"

        # Assert: Verify updated_at changed
        assert updated.updated_at > original.updated_at, \
            "Updated timestamp must increase on update"

        # Act: Update a different field
        update_data2 = UserPreferenceUpdate(
            batch_auto_analyze=True
        )
        updated2 = await service.update_preferences(update_data2)

        # Assert: Verify both updates persisted
        assert updated2.vibe_analysis_model == "qwen/qwen3-235b-a22b-2507", \
            "Previous update should persist"
        assert updated2.batch_auto_analyze is True, \
            "New update should be applied"
        assert updated2.updated_at > updated.updated_at, \
            "Updated timestamp must increase again"

    @pytest.mark.asyncio
    async def test_helper_methods(self, db_session):
        """
        Test 3: Helper methods return correct values.

        Validates:
        - get_vibe_model() returns correct model string
        - get_batch_model() returns correct model string
        - should_auto_analyze() respects batch flag
        - should_auto_analyze(is_batch=False) returns auto_vibe_analysis
        - should_auto_analyze(is_batch=True) returns batch_auto_analyze
        - should_extract_features() returns auto_audio_features value
        - get_cost_limit() returns max_cost_per_request value

        These helper methods simplify accessing preferences in other services.
        They avoid direct field access and provide clearer semantics.
        """
        # Import models
        from app.services.preferences_service import PreferencesService
        from app.schemas.preferences import UserPreferenceUpdate

        # Arrange: Create service and set specific preferences
        service = PreferencesService(db_session)
        await service.update_preferences(UserPreferenceUpdate(
            vibe_analysis_model="qwen/qwen3-235b-a22b-2507",
            batch_processing_model="qwen/qwen3-7b-it",
            auto_vibe_analysis=True,
            batch_auto_analyze=False,
            auto_audio_features=True,
            max_cost_per_request=0.05
        ))

        # Act & Assert: Test model getters
        vibe_model = await service.get_vibe_model()
        assert vibe_model == "qwen/qwen3-235b-a22b-2507", \
            "get_vibe_model() should return vibe_analysis_model"

        batch_model = await service.get_batch_model()
        assert batch_model == "qwen/qwen3-7b-it", \
            "get_batch_model() should return batch_processing_model"

        # Act & Assert: Test auto-analyze logic (single sample)
        should_analyze_single = await service.should_auto_analyze(is_batch=False)
        assert should_analyze_single is True, \
            "should_auto_analyze(is_batch=False) should return auto_vibe_analysis"

        # Act & Assert: Test auto-analyze logic (batch)
        should_analyze_batch = await service.should_auto_analyze(is_batch=True)
        assert should_analyze_batch is False, \
            "should_auto_analyze(is_batch=True) should return batch_auto_analyze"

        # Act & Assert: Test feature extraction flag
        should_extract = await service.should_extract_features()
        assert should_extract is True, \
            "should_extract_features() should return auto_audio_features"

        # Act & Assert: Test cost limit getter
        cost_limit = await service.get_cost_limit()
        assert cost_limit == 0.05, \
            "get_cost_limit() should return max_cost_per_request"

        # Test with None cost limit
        await service.update_preferences(UserPreferenceUpdate(
            max_cost_per_request=None
        ))
        cost_limit_none = await service.get_cost_limit()
        assert cost_limit_none is None, \
            "get_cost_limit() should return None when not set"

    @pytest.mark.asyncio
    async def test_get_available_models(self):
        """
        Test 4: Get available models returns static data.

        Validates:
        - Static method works without database connection
        - Returns expected model count (2 models: 7B and 235B)
        - Model metadata includes required fields:
          - model_id (string)
          - name (human-readable string)
          - input_cost (float, per-token cost)
          - output_cost (float, per-token cost)
          - description (string, model capabilities)
        - Both expected models are present

        This static method provides UI with available model options
        and pricing information for cost estimation.
        """
        # Import models
        from app.services.preferences_service import PreferencesService
        from app.schemas.preferences import AvailableModelsResponse

        # Act: Get available models (no database required)
        response = await PreferencesService.get_available_models()

        # Assert: Verify response type
        assert isinstance(response, AvailableModelsResponse), \
            "Response must be AvailableModelsResponse instance"

        # Assert: Verify model count
        assert len(response.models) == 2, \
            "Should return exactly 2 models (7B and 235B)"

        # Assert: Verify both expected models are present
        model_ids = [m.model_id for m in response.models]
        assert "qwen/qwen3-7b-it" in model_ids, \
            "Should include qwen3-7b-it model"
        assert "qwen/qwen3-235b-a22b-2507" in model_ids, \
            "Should include qwen3-235b-a22b-2507 model"

        # Assert: Validate model metadata structure
        for model in response.models:
            assert model.model_id, "Model must have model_id"
            assert model.name, "Model must have human-readable name"
            assert model.input_cost > 0, "Input cost must be positive"
            assert model.output_cost > 0, "Output cost must be positive"
            assert model.description, "Model must have description"

        # Assert: Verify 235B model is more expensive than 7B
        model_7b = next(m for m in response.models if "7b" in m.model_id.lower())
        model_235b = next(m for m in response.models if "235b" in m.model_id.lower())

        assert model_235b.input_cost > model_7b.input_cost, \
            "235B model should have higher input cost than 7B"
        assert model_235b.output_cost > model_7b.output_cost, \
            "235B model should have higher output cost than 7B"


# Additional helper to verify models don't exist yet (RED phase)
def test_imports_will_fail():
    """
    Meta-test to document that imports should fail in RED phase.

    This test documents the expected ImportError that will occur when
    running these tests before implementation.
    """
    with pytest.raises(ImportError):
        from app.services.preferences_service import PreferencesService

    with pytest.raises(ImportError):
        from app.schemas.preferences import UserPreferenceResponse

    with pytest.raises(ImportError):
        from app.schemas.preferences import UserPreferenceUpdate

    with pytest.raises(ImportError):
        from app.schemas.preferences import AvailableModelsResponse
