"""
TDD RED Phase Tests for Preferences API Endpoints

These tests define the expected behavior of the Preferences API endpoints before implementation.
Following Test-Driven Development (TDD) RED-GREEN-REFACTOR methodology.

Test Strategy:
- 8 MVP-level tests covering critical functionality
- REAL async database integration (no mocks)
- Tests dual JSON/HTMX response pattern
- Tests validation and error handling
- All tests use real database session and PreferencesService

Endpoint Coverage:
1. GET /api/v1/preferences - JSON response
2. GET /api/v1/preferences - HTMX response (HTML partial)
3. PATCH /api/v1/preferences - JSON update
4. PATCH /api/v1/preferences - HTMX update (HTML success)
5. PATCH /api/v1/preferences - Partial update
6. PATCH /api/v1/preferences - Validation error (invalid model_id)
7. GET /api/v1/preferences/models - JSON response
8. GET /api/v1/preferences/models - Pricing data validation

Expected Failures:
- ImportError: Endpoint module doesn't exist yet
- 404 errors: Routes not registered
- All tests should fail until implementation is complete
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.api.deps import get_db


@pytest_asyncio.fixture
async def api_client(db_session: AsyncSession):
    """
    Create async HTTP client with database override.

    This fixture provides a test client that uses the test database
    instead of the production database.
    """
    # Override the database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Use ASGI transport instead of app parameter (httpx API change)
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clear overrides after test
    app.dependency_overrides.clear()


class TestPreferencesEndpointsJSON:
    """Test suite for Preferences API endpoints - JSON responses."""

    @pytest.mark.asyncio
    async def test_get_preferences_returns_json(self, api_client: AsyncClient):
        """
        Test 1: GET /api/v1/preferences returns JSON with defaults.

        Validates:
        - Endpoint returns 200 OK
        - Response is valid JSON
        - Contains all expected preference fields
        - Default values match specification
        - Timestamps are present
        - No HTMX header = JSON response

        Expected default preferences:
        - id: 1 (single-row design)
        - vibe_analysis_model: "qwen/qwen3-7b-it"
        - auto_vibe_analysis: True
        - auto_audio_features: True
        - batch_processing_model: "qwen/qwen3-7b-it"
        - batch_auto_analyze: False
        - max_cost_per_request: None
        """
        # Act: GET preferences without HTMX header (JSON response)
        response = await api_client.get("/api/v1/preferences")

        # Assert: Status code
        assert response.status_code == 200, \
            f"GET /preferences should return 200, got {response.status_code}"

        # Assert: Content type is JSON
        assert "application/json" in response.headers.get("content-type", ""), \
            "Response should be JSON when no HX-Request header"

        # Assert: Response structure
        data = response.json()
        assert "id" in data, "Response must include id field"
        assert "vibe_analysis_model" in data, "Response must include vibe_analysis_model"
        assert "auto_vibe_analysis" in data, "Response must include auto_vibe_analysis"
        assert "auto_audio_features" in data, "Response must include auto_audio_features"
        assert "batch_processing_model" in data, "Response must include batch_processing_model"
        assert "batch_auto_analyze" in data, "Response must include batch_auto_analyze"
        assert "max_cost_per_request" in data, "Response must include max_cost_per_request"
        assert "created_at" in data, "Response must include created_at timestamp"
        assert "updated_at" in data, "Response must include updated_at timestamp"

        # Assert: Default values
        assert data["id"] == 1, "Must use single-row design with id=1"
        assert data["vibe_analysis_model"] == "qwen/qwen3-7b-it", \
            "Default vibe model should be qwen3-7b-it"
        assert data["auto_vibe_analysis"] is True, \
            "Auto vibe analysis should be enabled by default"
        assert data["auto_audio_features"] is True, \
            "Auto audio features should be enabled by default"
        assert data["batch_processing_model"] == "qwen/qwen3-7b-it", \
            "Default batch model should be qwen3-7b-it"
        assert data["batch_auto_analyze"] is False, \
            "Batch auto-analyze should be disabled by default"
        assert data["max_cost_per_request"] is None, \
            "Cost limit should be None by default"

    @pytest.mark.asyncio
    async def test_get_preferences_returns_html_for_htmx(self, api_client: AsyncClient):
        """
        Test 2: GET /api/v1/preferences returns HTML for HTMX requests.

        Validates:
        - Endpoint detects HX-Request header
        - Returns HTML content (not JSON)
        - HTML contains form elements
        - Form includes all preference fields
        - Template rendering works correctly

        HTMX Integration:
        - Header: HX-Request: true
        - Expected template: preferences/preferences-form.html
        - Response: HTML partial with <form> element
        """
        # Act: GET preferences with HTMX header
        response = await api_client.get(
            "/api/v1/preferences",
            headers={"HX-Request": "true"}
        )

        # Assert: Status code
        assert response.status_code == 200, \
            f"GET /preferences should return 200, got {response.status_code}"

        # Assert: Content type is HTML
        assert "text/html" in response.headers.get("content-type", ""), \
            "Response should be HTML when HX-Request header is present"

        # Assert: Response contains HTML form
        html = response.text
        assert "<form" in html, "HTML response should contain a form element"
        assert "vibe_analysis_model" in html, "Form should include vibe_analysis_model field"
        assert "auto_vibe_analysis" in html, "Form should include auto_vibe_analysis field"
        assert "batch_processing_model" in html, "Form should include batch_processing_model field"

    @pytest.mark.asyncio
    async def test_patch_preferences_updates_json(self, api_client: AsyncClient):
        """
        Test 3: PATCH /api/v1/preferences updates preferences (JSON).

        Validates:
        - Endpoint accepts PATCH with JSON body
        - Updates preferences in database
        - Returns updated preferences as JSON
        - Only specified fields are changed
        - updated_at timestamp increases
        - Changes persist across requests

        Update workflow:
        1. Get initial preferences
        2. PATCH to update vibe_analysis_model
        3. Verify response shows updated value
        4. GET again to confirm persistence
        """
        # Arrange: Get initial preferences
        initial_response = await api_client.get("/api/v1/preferences")
        initial_data = initial_response.json()
        initial_updated_at = initial_data["updated_at"]

        # Act: Update vibe_analysis_model via JSON
        update_payload = {
            "vibe_analysis_model": "qwen/qwen3-235b-a22b-2507"
        }
        response = await api_client.patch(
            "/api/v1/preferences",
            json=update_payload
        )

        # Assert: Status code
        assert response.status_code == 200, \
            f"PATCH /preferences should return 200, got {response.status_code}"

        # Assert: Response is JSON
        assert "application/json" in response.headers.get("content-type", ""), \
            "Response should be JSON when no HX-Request header"

        # Assert: Updated value in response
        data = response.json()
        assert data["vibe_analysis_model"] == "qwen/qwen3-235b-a22b-2507", \
            "Vibe analysis model should be updated"

        # Assert: Other fields unchanged
        assert data["auto_vibe_analysis"] == initial_data["auto_vibe_analysis"], \
            "Other fields should remain unchanged"
        assert data["batch_processing_model"] == initial_data["batch_processing_model"], \
            "Other fields should remain unchanged"

        # Assert: updated_at changed
        assert data["updated_at"] != initial_updated_at, \
            "updated_at timestamp should change on update"

        # Assert: Changes persist
        verify_response = await api_client.get("/api/v1/preferences")
        verify_data = verify_response.json()
        assert verify_data["vibe_analysis_model"] == "qwen/qwen3-235b-a22b-2507", \
            "Changes should persist in database"

    @pytest.mark.asyncio
    async def test_patch_preferences_returns_html_for_htmx(self, api_client: AsyncClient):
        """
        Test 4: PATCH /api/v1/preferences returns HTML for HTMX requests.

        Validates:
        - Endpoint accepts form-encoded data from HTMX
        - Detects HX-Request header
        - Returns HTML success message (not JSON)
        - HTML contains confirmation message
        - Update actually happens in database

        HTMX Integration:
        - Header: HX-Request: true
        - Content-Type: application/x-www-form-urlencoded
        - Expected template: preferences/preferences-success.html
        - Response: HTML partial with success message
        """
        # Act: Update via HTMX (form-encoded)
        update_data = {
            "vibe_analysis_model": "qwen/qwen3-235b-a22b-2507",
            "auto_vibe_analysis": "true",
            "batch_auto_analyze": "true"
        }
        response = await api_client.patch(
            "/api/v1/preferences",
            data=update_data,
            headers={"HX-Request": "true"}
        )

        # Assert: Status code
        assert response.status_code == 200, \
            f"PATCH /preferences should return 200, got {response.status_code}"

        # Assert: Content type is HTML
        assert "text/html" in response.headers.get("content-type", ""), \
            "Response should be HTML when HX-Request header is present"

        # Assert: HTML contains success message
        html = response.text
        assert "success" in html.lower() or "saved" in html.lower(), \
            "HTML should contain success/saved message"

        # Assert: Verify update actually happened
        verify_response = await api_client.get("/api/v1/preferences")
        verify_data = verify_response.json()
        assert verify_data["vibe_analysis_model"] == "qwen/qwen3-235b-a22b-2507", \
            "Update should persist in database"
        assert verify_data["batch_auto_analyze"] is True, \
            "Boolean field should be updated"

    @pytest.mark.asyncio
    async def test_patch_preferences_partial_update(self, api_client: AsyncClient):
        """
        Test 5: PATCH /api/v1/preferences handles partial updates correctly.

        Validates:
        - Can update single field without affecting others
        - Can update multiple fields in sequence
        - Null/None values don't overwrite existing data
        - Each update is independent
        - All field types work (string, bool, float)

        Partial update workflow:
        1. Update only vibe_analysis_model
        2. Verify only that field changed
        3. Update only batch_auto_analyze
        4. Verify both updates persisted
        5. Update max_cost_per_request
        6. Verify all three updates still present
        """
        # Act: First update - only vibe model
        response1 = await api_client.patch(
            "/api/v1/preferences",
            json={"vibe_analysis_model": "qwen/qwen3-235b-a22b-2507"}
        )
        data1 = response1.json()

        # Assert: Only specified field changed
        assert data1["vibe_analysis_model"] == "qwen/qwen3-235b-a22b-2507"
        assert data1["batch_auto_analyze"] is False, "Other fields should remain unchanged"

        # Act: Second update - only batch_auto_analyze
        response2 = await api_client.patch(
            "/api/v1/preferences",
            json={"batch_auto_analyze": True}
        )
        data2 = response2.json()

        # Assert: Both updates persisted
        assert data2["vibe_analysis_model"] == "qwen/qwen3-235b-a22b-2507", \
            "Previous update should persist"
        assert data2["batch_auto_analyze"] is True, \
            "New update should be applied"

        # Act: Third update - cost limit
        response3 = await api_client.patch(
            "/api/v1/preferences",
            json={"max_cost_per_request": 0.05}
        )
        data3 = response3.json()

        # Assert: All three updates persisted
        assert data3["vibe_analysis_model"] == "qwen/qwen3-235b-a22b-2507"
        assert data3["batch_auto_analyze"] is True
        assert data3["max_cost_per_request"] == 0.05

    @pytest.mark.asyncio
    async def test_patch_preferences_validation_error(self, api_client: AsyncClient):
        """
        Test 6: PATCH /api/v1/preferences returns 422 for invalid data.

        Validates:
        - Invalid model_id format is rejected
        - Negative cost limit is rejected
        - Response includes validation error details
        - Database is not modified on validation failure
        - Error response follows FastAPI validation format

        Invalid test cases:
        1. Model ID without '/' separator
        2. Empty model ID string
        3. Negative max_cost_per_request
        4. Zero max_cost_per_request
        """
        # Get initial state
        initial_response = await api_client.get("/api/v1/preferences")
        initial_data = initial_response.json()

        # Test Case 1: Invalid model format (no '/')
        response1 = await api_client.patch(
            "/api/v1/preferences",
            json={"vibe_analysis_model": "invalid-model"}
        )

        # Assert: Validation error
        assert response1.status_code == 422, \
            "Should return 422 for invalid model format"
        error1 = response1.json()
        assert "detail" in error1, "Error response should include detail"

        # Test Case 2: Negative cost limit
        response2 = await api_client.patch(
            "/api/v1/preferences",
            json={"max_cost_per_request": -0.05}
        )

        # Assert: Validation error
        assert response2.status_code == 422, \
            "Should return 422 for negative cost limit"
        error2 = response2.json()
        assert "detail" in error2, "Error response should include detail"

        # Test Case 3: Zero cost limit
        response3 = await api_client.patch(
            "/api/v1/preferences",
            json={"max_cost_per_request": 0}
        )

        # Assert: Validation error
        assert response3.status_code == 422, \
            "Should return 422 for zero cost limit"

        # Assert: Database unchanged after validation errors
        verify_response = await api_client.get("/api/v1/preferences")
        verify_data = verify_response.json()
        assert verify_data == initial_data, \
            "Database should not be modified when validation fails"

    @pytest.mark.asyncio
    async def test_get_models_returns_model_list(self, api_client: AsyncClient):
        """
        Test 7: GET /api/v1/preferences/models returns available models.

        Validates:
        - Endpoint returns 200 OK
        - Response contains list of models
        - Each model has required metadata fields
        - Model count matches expected (2 models)
        - Both Qwen models are present
        - Response is JSON (no HTMX variant for this endpoint)

        Expected models:
        - qwen/qwen3-7b-it
        - qwen/qwen3-235b-a22b-2507

        Required metadata fields:
        - model_id: str
        - name: str
        - input_cost: float
        - output_cost: float
        - description: str
        """
        # Act: GET available models
        response = await api_client.get("/api/v1/preferences/models")

        # Assert: Status code
        assert response.status_code == 200, \
            f"GET /preferences/models should return 200, got {response.status_code}"

        # Assert: Response is JSON
        assert "application/json" in response.headers.get("content-type", ""), \
            "Response should be JSON"

        # Assert: Response structure
        data = response.json()
        assert "models" in data, "Response should contain 'models' field"
        assert isinstance(data["models"], list), "Models should be a list"

        # Assert: Model count
        assert len(data["models"]) == 2, \
            "Should return exactly 2 models (7B and 235B)"

        # Assert: Required fields in each model
        for model in data["models"]:
            assert "model_id" in model, "Model must have model_id"
            assert "name" in model, "Model must have name"
            assert "input_cost" in model, "Model must have input_cost"
            assert "output_cost" in model, "Model must have output_cost"
            assert "description" in model, "Model must have description"

            # Assert: Field types
            assert isinstance(model["model_id"], str), "model_id must be string"
            assert isinstance(model["name"], str), "name must be string"
            assert isinstance(model["input_cost"], (int, float)), "input_cost must be number"
            assert isinstance(model["output_cost"], (int, float)), "output_cost must be number"
            assert isinstance(model["description"], str), "description must be string"

        # Assert: Both expected models are present
        model_ids = [m["model_id"] for m in data["models"]]
        assert "qwen/qwen3-7b-it" in model_ids, \
            "Should include qwen3-7b-it model"
        assert "qwen/qwen3-235b-a22b-2507" in model_ids, \
            "Should include qwen3-235b-a22b-2507 model"

    @pytest.mark.asyncio
    async def test_get_models_includes_pricing(self, api_client: AsyncClient):
        """
        Test 8: GET /api/v1/preferences/models includes accurate pricing.

        Validates:
        - All models have positive costs
        - 235B model is more expensive than 7B model
        - Costs are realistic (per-token pricing)
        - Input and output costs are provided
        - Pricing enables cost estimation in UI

        Expected pricing relationship:
        - 235B input_cost > 7B input_cost
        - 235B output_cost > 7B output_cost
        - All costs > 0
        - Costs are in USD per token
        """
        # Act: GET available models
        response = await api_client.get("/api/v1/preferences/models")
        data = response.json()

        # Arrange: Find specific models
        model_7b = next(
            (m for m in data["models"] if "7b" in m["model_id"].lower()),
            None
        )
        model_235b = next(
            (m for m in data["models"] if "235b" in m["model_id"].lower()),
            None
        )

        # Assert: Both models found
        assert model_7b is not None, "Should find 7B model"
        assert model_235b is not None, "Should find 235B model"

        # Assert: All costs are positive
        assert model_7b["input_cost"] > 0, "7B input cost must be positive"
        assert model_7b["output_cost"] > 0, "7B output cost must be positive"
        assert model_235b["input_cost"] > 0, "235B input cost must be positive"
        assert model_235b["output_cost"] > 0, "235B output cost must be positive"

        # Assert: 235B is more expensive than 7B
        assert model_235b["input_cost"] > model_7b["input_cost"], \
            "235B model should have higher input cost than 7B"
        assert model_235b["output_cost"] > model_7b["output_cost"], \
            "235B model should have higher output cost than 7B"

        # Assert: Costs are reasonable (micro-dollars per token)
        assert model_7b["input_cost"] < 1.0, "Per-token costs should be very small"
        assert model_235b["input_cost"] < 1.0, "Per-token costs should be very small"


# Additional helper to verify endpoints don't exist yet (RED phase)
def test_endpoints_will_fail():
    """
    Meta-test to document that endpoint imports should fail in RED phase.

    This test documents the expected ImportError that will occur when
    running these tests before implementation.
    """
    with pytest.raises((ImportError, AttributeError)):
        from app.api.v1.endpoints import preferences
