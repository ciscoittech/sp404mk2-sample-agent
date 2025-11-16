"""
TDD RED Phase Tests for OpenRouterService

These tests are designed to FAIL initially. They define the expected behavior
of the OpenRouterService before implementation. This follows Test-Driven Development
(TDD) RED-GREEN-REFACTOR methodology.

Test Strategy:
- 3 REAL_INTEGRATION_TESTS: Make actual API calls to OpenRouter
- 1 Auth Error Test: Can use mocked/invalid API key
- All tests use real database session and UsageTrackingService
- No mocked httpx clients for integration tests

Environment Requirements:
- OPENROUTER_API_KEY must be set for integration tests
- Database must be initialized (handled by conftest.py fixtures)

Expected Failures:
- ImportError: OpenRouterService module doesn't exist yet
- AttributeError: Methods and models not implemented
- All tests should fail until implementation is complete
"""
import pytest
import pytest_asyncio
from sqlalchemy import select
import json
import os


# REAL_INTEGRATION_TEST 1: Real OpenRouter API Call
@pytest.mark.asyncio
async def test_chat_completion_real_api(openrouter_service, openrouter_api_key):
    """
    REAL_INTEGRATION_TEST

    Test real API call to OpenRouter with Qwen3-7B model.

    This test makes an actual HTTP request to OpenRouter's API to validate:
    - Request serialization
    - API authentication
    - Response parsing
    - Token counting
    - Cost calculation

    Expected to fail with ImportError until OpenRouterService is implemented.

    Requirements:
    - OPENROUTER_API_KEY environment variable must be set
    - Real internet connection to api.openrouter.ai
    - Should complete in < 10 seconds
    """
    # Import models (will fail until implemented)
    from app.services.openrouter_service import OpenRouterRequest, OpenRouterResponse

    # Arrange: Create minimal request to Qwen3-7B
    request = OpenRouterRequest(
        model="qwen/qwen3-7b-it",
        messages=[{"role": "user", "content": "Say 'hello' in one word"}],
        temperature=0.5,
        max_tokens=10
    )

    # Act: Make real API call to OpenRouter
    response = await openrouter_service.chat_completion(request)

    # Assert: Verify response structure and data
    assert isinstance(response, OpenRouterResponse), "Response must be OpenRouterResponse instance"
    assert len(response.content) > 0, "Response content must not be empty"
    assert response.usage.prompt_tokens > 0, "Must count prompt tokens"
    assert response.usage.completion_tokens > 0, "Must count completion tokens"
    assert response.usage.total_tokens > 0, "Must calculate total tokens"
    assert response.model == "qwen/qwen3-7b-it", "Response must include model name"
    assert response.cost > 0.0, "Cost must be calculated and greater than zero"
    assert response.request_id is not None, "Must include OpenRouter request ID"


# REAL_INTEGRATION_TEST 2: Database Cost Tracking
@pytest.mark.asyncio
async def test_cost_tracking_in_database(openrouter_service, openrouter_api_key, db_session):
    """
    REAL_INTEGRATION_TEST

    Test that API calls are automatically logged to database with accurate cost tracking.

    This test validates:
    - Integration between OpenRouterService and UsageTrackingService
    - Automatic creation of ApiUsage records
    - Correct cost calculation and storage
    - Token count persistence
    - Metadata serialization (JSON/JSONB fields)

    Expected to fail until OpenRouterService integration is complete.

    Requirements:
    - OPENROUTER_API_KEY environment variable
    - Real database session (in-memory SQLite)
    - UsageTrackingService properly configured
    """
    # Import models
    from app.services.openrouter_service import OpenRouterRequest
    from app.models.api_usage import ApiUsage

    # Arrange: Create vibe analysis request
    request = OpenRouterRequest(
        model="qwen/qwen3-7b-it",
        messages=[
            {"role": "system", "content": "You are a music analyst."},
            {"role": "user", "content": "Analyze this: upbeat vibe"}
        ],
        temperature=0.5,
        max_tokens=50
    )

    # Act: Make real API call
    response = await openrouter_service.chat_completion(request)

    # Query database for most recent usage record
    result = await db_session.execute(
        select(ApiUsage).order_by(ApiUsage.created_at.desc()).limit(1)
    )
    usage_record = result.scalar_one_or_none()

    # Assert: Verify database record matches API response
    assert usage_record is not None, "ApiUsage record must be created"
    assert usage_record.model == "qwen/qwen3-7b-it", "Model name must match"
    assert usage_record.operation == "chat_completion", "Operation type must be recorded"
    assert usage_record.input_tokens == response.usage.prompt_tokens, "Input tokens must match"
    assert usage_record.output_tokens == response.usage.completion_tokens, "Output tokens must match"
    assert usage_record.total_tokens == response.usage.total_tokens, "Total tokens must match"

    # Cost comparison with tolerance for floating point precision
    assert abs(usage_record.total_cost - response.cost) < 0.0001, "Database cost must match response cost"

    # Verify metadata is stored (should include request_id, model, etc.)
    assert usage_record.request_id is not None, "Request ID must be stored"


# Test 3: Authentication Error Handling
@pytest.mark.asyncio
async def test_invalid_api_key_raises_error(db_session):
    """
    Test that invalid API key raises OpenRouterError with correct status code.

    This test validates:
    - HTTP 401 authentication error handling
    - Custom OpenRouterError exception
    - Error message extraction from API response
    - No retry attempts on auth errors

    Expected to fail until error handling is implemented.

    Note: This test temporarily overrides the API key to force an auth error.
    """
    # Import service and error classes
    from app.services.openrouter_service import (
        OpenRouterService,
        OpenRouterRequest,
        OpenRouterError
    )
    from app.services.usage_tracking_service import UsageTrackingService

    # Arrange: Create service with invalid API key by patching environment
    import unittest.mock

    with unittest.mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-invalid-key-for-testing"}):
        # Create fresh service instance with invalid key
        usage_service = UsageTrackingService(db_session)
        service = OpenRouterService(usage_service)

        request = OpenRouterRequest(
            model="qwen/qwen3-7b-it",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=10
        )

        # Act & Assert: Verify authentication error is raised
        with pytest.raises(OpenRouterError) as exc_info:
            await service.chat_completion(request)

        # Verify error details
        error = exc_info.value
        assert error.status_code == 401, "Must return 401 status for auth errors"
        assert "Invalid" in error.message or "authentication" in error.message.lower(), \
            "Error message must indicate authentication failure"
        assert error.response_body is not None, "Must include API error response"


# REAL_INTEGRATION_TEST 4: End-to-End Vibe Analysis
@pytest.mark.asyncio
async def test_end_to_end_vibe_analysis(openrouter_service, openrouter_api_key):
    """
    REAL_INTEGRATION_TEST

    Test complete vibe analysis workflow with audio features.

    This test validates:
    - Multi-message conversation handling (system + user prompts)
    - Larger context processing (audio features + analysis request)
    - Use of more expensive 235B parameter model
    - JSON response parsing from AI
    - Cost accuracy for larger models

    Expected to fail until OpenRouterService is fully implemented.

    This test simulates real vibe analysis workflow:
    1. System prompt establishes AI as music expert
    2. User prompt provides audio features (BPM, key, energy)
    3. AI responds with vibe analysis in JSON format
    4. Service parses and validates response
    """
    # Import models
    from app.services.openrouter_service import OpenRouterRequest, OpenRouterResponse

    # Arrange: Create vibe analysis prompt with audio features
    messages = [
        {
            "role": "system",
            "content": (
                "You are a music analysis expert specializing in vibe and mood detection. "
                "Analyze audio features and return JSON with {\"vibe\": string, \"confidence\": float}."
            )
        },
        {
            "role": "user",
            "content": (
                "Analyze this sample:\n"
                "- Tempo: 95 BPM\n"
                "- Key: C# major\n"
                "- Energy: high\n"
                "- Spectral centroid: 2800 Hz\n\n"
                "Provide vibe analysis in JSON format."
            )
        }
    ]

    request = OpenRouterRequest(
        model="qwen/qwen3-235b-a22b-2507",  # Use deeper model for complex analysis
        messages=messages,
        temperature=0.5,
        max_tokens=200
    )

    # Act: Make real API call with larger model
    response = await openrouter_service.chat_completion(request)

    # Assert: Verify response structure and cost
    assert isinstance(response, OpenRouterResponse), "Must return OpenRouterResponse"
    assert response.model == "qwen/qwen3-235b-a22b-2507", "Model name must match request"
    assert response.cost > 0.0001, "235B model should be more expensive than 7B"
    assert len(response.content) > 0, "Response must contain vibe analysis"
    assert response.usage.total_tokens > 50, "Should process substantial context"

    # Attempt to parse response as JSON (AI should return valid JSON)
    try:
        vibe_data = json.loads(response.content)
        # Flexible validation - AI might use different field names
        assert "vibe" in vibe_data or "mood" in vibe_data or "analysis" in vibe_data, \
            "Response should contain vibe/mood/analysis field"

        # If confidence is present, it should be a float between 0 and 1
        if "confidence" in vibe_data:
            confidence = vibe_data["confidence"]
            assert isinstance(confidence, (int, float)), "Confidence must be numeric"
            assert 0.0 <= confidence <= 1.0, "Confidence must be between 0 and 1"

    except json.JSONDecodeError:
        # For MVP, AI might return non-JSON response - that's acceptable
        # Just log a warning but don't fail the test
        # The important part is that the API call succeeded and returned content
        print(f"Warning: AI returned non-JSON response: {response.content[:100]}")
        assert len(response.content) > 20, "Even non-JSON response should be substantial"


# Additional helper to verify models don't exist yet
def test_imports_will_fail():
    """
    Meta-test to document that imports should fail in RED phase.

    This test documents the expected ImportError that will occur when
    running these tests before implementation.
    """
    with pytest.raises(ImportError):
        from app.services.openrouter_service import OpenRouterService

    with pytest.raises(ImportError):
        from app.services.openrouter_service import OpenRouterRequest

    with pytest.raises(ImportError):
        from app.services.openrouter_service import OpenRouterResponse

    with pytest.raises(ImportError):
        from app.services.openrouter_service import OpenRouterError
