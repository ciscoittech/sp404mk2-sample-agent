# OpenRouter Service Tests - TDD RED Phase

## Overview

This directory contains **4 failing tests** for the OpenRouter Service, following Test-Driven Development (TDD) RED-GREEN-REFACTOR methodology.

## Current Status: RED Phase ✅

All tests are **correctly failing** with `ModuleNotFoundError` because the service hasn't been implemented yet.

```bash
$ pytest tests/services/test_openrouter_service.py -v

tests/services/test_openrouter_service.py::test_chat_completion_real_api ERROR
tests/services/test_openrouter_service.py::test_cost_tracking_in_database ERROR
tests/services/test_openrouter_service.py::test_invalid_api_key_raises_error FAILED
tests/services/test_openrouter_service.py::test_end_to_end_vibe_analysis ERROR
tests/services/test_openrouter_service.py::test_imports_will_fail PASSED
```

## Test Files

```
tests/services/
├── __init__.py                         # Package marker
├── conftest.py                         # Service-specific fixtures
├── test_openrouter_service.py         # 4 failing tests
├── TEST_EXECUTION_NOTES.md            # Detailed test documentation
└── README.md                          # This file
```

## The 4 Tests

### 1. `test_chat_completion_real_api` (REAL_INTEGRATION_TEST)
- Makes actual API call to OpenRouter with Qwen3-7B
- Validates request/response handling, token counting, cost calculation
- **Expected cost**: ~$0.000002 per run

### 2. `test_cost_tracking_in_database` (REAL_INTEGRATION_TEST)
- Verifies automatic logging to ApiUsage table
- Tests integration with UsageTrackingService
- Validates cost accuracy in database
- **Expected cost**: ~$0.000010 per run

### 3. `test_invalid_api_key_raises_error`
- Tests authentication error handling
- Validates OpenRouterError exception with status code 401
- No real API call (uses invalid key)
- **Expected cost**: $0 (auth fails before charging)

### 4. `test_end_to_end_vibe_analysis` (REAL_INTEGRATION_TEST)
- Simulates complete vibe analysis workflow
- Uses larger 235B parameter model
- Tests multi-message conversation and JSON parsing
- **Expected cost**: ~$0.000100 per run

**Total cost per test run**: ~$0.000112 (negligible)

## Quick Start

### Run the tests (they will fail):

```bash
cd backend
../venv/bin/python -m pytest tests/services/test_openrouter_service.py -v
```

### Expected output:

```
ModuleNotFoundError: No module named 'app.services.openrouter_service'
```

This is **correct** - tests should fail until the service is implemented.

## Environment Setup

Required environment variables:

```bash
# In backend/.env or export
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
SECRET_KEY=test-secret-key
```

## Next Steps

1. ✅ **RED Phase Complete**: Tests are failing as expected
2. ⏳ **GREEN Phase**: Implement `OpenRouterService` to make tests pass
3. ⏳ **REFACTOR Phase**: Optimize code while keeping tests green

## Implementation Requirements

Based on the tests, the `OpenRouterService` must implement:

### Models (Pydantic/dataclasses)
- `OpenRouterRequest` - Request payload with model, messages, temperature, max_tokens
- `OpenRouterResponse` - Response with content, usage, model, cost, request_id
- `OpenRouterError` - Custom exception with status_code, message, response_body

### Service Class
```python
class OpenRouterService:
    def __init__(self, usage_tracking_service: UsageTrackingService):
        ...

    async def chat_completion(self, request: OpenRouterRequest) -> OpenRouterResponse:
        """
        Make chat completion request to OpenRouter API.
        Automatically logs usage to database via UsageTrackingService.
        """
        ...
```

### Key Features
- HTTP client using `httpx.AsyncClient`
- OpenRouter API authentication (Bearer token)
- Request/response serialization
- Token counting from API response
- Cost calculation based on model pricing
- Automatic UsageTrackingService integration
- Error handling with custom exceptions
- Request ID tracking

## Testing Strategy

### MVP Level (4 tests)
- 3 REAL_INTEGRATION_TESTS (actual API calls)
- 1 error handling test (mocked invalid key)
- Focus on critical paths
- Balance coverage with development speed

### Why Real API Calls?
- Validates actual behavior (mocks can lie)
- Catches integration issues early
- Verifies cost calculations with real tokens
- Documents expected API behavior

### Cost Management
- Tests use minimal token counts
- Total cost per run: ~$0.0001
- CI/CD can cache responses (future enhancement)

## Documentation

See [`TEST_EXECUTION_NOTES.md`](./TEST_EXECUTION_NOTES.md) for:
- Detailed test descriptions
- Troubleshooting guide
- Expected behaviors in each phase
- Cost estimates and breakdowns
- Performance considerations

## Hand-off to Coder Agent

The Coder Agent should:

1. Create `backend/app/services/openrouter_service.py`
2. Implement all models and service class
3. Integrate with `UsageTrackingService`
4. Run tests until all pass (GREEN phase)
5. Refactor for quality (REFACTOR phase)

The tests define the complete contract - implementation must satisfy all assertions.
