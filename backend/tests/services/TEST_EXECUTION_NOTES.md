# OpenRouter Service Test Execution Notes

## Overview

This document describes the 4 TDD RED phase tests for the OpenRouter Service. These tests are **designed to fail** until the service is implemented.

## Test Files Created

```
backend/tests/services/
├── __init__.py                     # Package marker
├── conftest.py                     # Service-specific fixtures
├── test_openrouter_service.py     # 4 failing tests
└── TEST_EXECUTION_NOTES.md        # This file
```

## Prerequisites

### 1. Environment Setup

Create `.env` file in backend directory (or export variables):

```bash
# Required for integration tests
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Database (handled by test fixtures, but good to have)
DATABASE_URL=sqlite+aiosqlite:///:memory:

# Required for JWT/auth (may be needed by other services)
SECRET_KEY=test-secret-key-for-development
```

### 2. Dependencies

Ensure these are installed (should be in requirements.txt):

```bash
pip install pytest pytest-asyncio pytest-cov httpx sqlalchemy[asyncio] aiosqlite
```

### 3. Database Setup

The tests use in-memory SQLite database created automatically by fixtures in `tests/conftest.py`. No manual database initialization required.

## Test Descriptions

### Test 1: Real OpenRouter API Call (REAL_INTEGRATION_TEST)

**Purpose**: Validate basic API communication with Qwen3-7B model

**What it tests**:
- Request serialization to OpenRouter API format
- HTTPS connection to api.openrouter.ai
- Response parsing and deserialization
- Token counting (prompt, completion, total)
- Cost calculation based on model pricing
- Request ID tracking

**Expected behavior when FAILING**:
```python
ImportError: cannot import name 'OpenRouterService' from 'app.services.openrouter_service'
```

**Expected behavior when PASSING**:
- HTTP 200 response from OpenRouter
- Response contains AI-generated text
- Token counts are positive integers
- Cost is calculated correctly (> $0.00)
- Completes in < 10 seconds

### Test 2: Database Cost Tracking (REAL_INTEGRATION_TEST)

**Purpose**: Verify automatic logging to ApiUsage table

**What it tests**:
- Integration with UsageTrackingService
- Automatic ApiUsage record creation
- Correct token count persistence
- Accurate cost storage (input/output/total)
- Request metadata serialization
- Database transaction handling

**Expected behavior when FAILING**:
```python
ImportError: cannot import name 'OpenRouterRequest' from 'app.services.openrouter_service'
```

**Expected behavior when PASSING**:
- ApiUsage record exists in database
- Model name matches request
- Token counts match API response
- Costs match within 0.0001 tolerance
- Request ID is stored
- Timestamps are recorded

### Test 3: Authentication Error Handling

**Purpose**: Validate error handling for invalid API keys

**What it tests**:
- HTTP 401 error detection
- Custom OpenRouterError exception
- Error message extraction
- No retry attempts on auth failures
- Proper exception attributes (status_code, message, response_body)

**Expected behavior when FAILING**:
```python
ImportError: cannot import name 'OpenRouterError' from 'app.services.openrouter_service'
```

**Expected behavior when PASSING**:
- OpenRouterError raised (not generic exception)
- status_code == 401
- Error message indicates auth failure
- response_body contains API error details
- No database record created for failed auth

### Test 4: End-to-End Vibe Analysis (REAL_INTEGRATION_TEST)

**Purpose**: Simulate complete vibe analysis workflow

**What it tests**:
- Multi-message conversation (system + user prompts)
- Larger context handling (~200 tokens)
- More expensive model (235B parameter Qwen3)
- JSON response parsing
- Cost comparison between models (235B > 7B)
- Real-world prompt engineering

**Expected behavior when FAILING**:
```python
ImportError: cannot import name 'OpenRouterResponse' from 'app.services.openrouter_service'
```

**Expected behavior when PASSING**:
- API call succeeds with 235B model
- Response contains vibe analysis
- Cost is higher than 7B model
- JSON parsing succeeds (or graceful fallback)
- Total tokens > 50 (substantial context)
- Vibe/mood/analysis fields present

## Running the Tests

### Run all OpenRouter service tests:

```bash
# From backend/ directory
pytest tests/services/test_openrouter_service.py -v

# Expected output (RED phase):
# ======================== FAILURES =========================
# __________ test_chat_completion_real_api __________
# ImportError: cannot import name 'OpenRouterService'...
#
# __________ test_cost_tracking_in_database __________
# ImportError: cannot import name 'OpenRouterRequest'...
#
# __________ test_invalid_api_key_raises_error __________
# ImportError: cannot import name 'OpenRouterService'...
#
# __________ test_end_to_end_vibe_analysis __________
# ImportError: cannot import name 'OpenRouterResponse'...
#
# ========== 4 failed in 0.05s ==========
```

### Run with verbose output:

```bash
pytest tests/services/test_openrouter_service.py -vv -s
```

### Run single test:

```bash
pytest tests/services/test_openrouter_service.py::test_chat_completion_real_api -v
```

### Run with coverage:

```bash
pytest tests/services/ --cov=app.services.openrouter_service --cov-report=html
```

### Skip integration tests (run only auth error test):

```bash
# You can add this marker later if needed
pytest tests/services/test_openrouter_service.py -k "invalid_api_key" -v
```

## Expected Test Execution Timeline

### RED Phase (Current):
- **All 4 tests FAIL**: ImportError on service/model imports
- Duration: < 1 second (immediate import failures)

### GREEN Phase (After Implementation):
- **All 4 tests PASS**: Real API calls succeed
- Duration: 10-30 seconds (depends on API response time)
- Costs: ~$0.001-0.002 per test run (3 API calls)

### REFACTOR Phase (Optimization):
- Tests still pass with improved code
- May run faster with connection pooling
- Costs remain the same

## Cost Estimates

Real API calls will incur small costs:

| Test | Model | Est. Tokens | Est. Cost |
|------|-------|-------------|-----------|
| Test 1 | Qwen3-7B | ~20 tokens | $0.000002 |
| Test 2 | Qwen3-7B | ~100 tokens | $0.000010 |
| Test 3 | N/A (auth error) | 0 tokens | $0.000000 |
| Test 4 | Qwen3-235B | ~250 tokens | $0.000100 |
| **Total** | | **~370 tokens** | **~$0.000112** |

**Note**: Actual costs may vary based on OpenRouter pricing. These are estimates.

## Troubleshooting

### Issue: `OPENROUTER_API_KEY not set in environment`

**Solution**:
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
# Or add to .env file
```

### Issue: `ImportError: cannot import name 'OpenRouterService'`

**Expected**: This is the RED phase - tests should fail until service is implemented.

### Issue: `httpx.ConnectError: Connection refused`

**Possible causes**:
- No internet connection
- Firewall blocking api.openrouter.ai
- OpenRouter API is down (rare)

**Solution**: Check network connectivity and try again.

### Issue: Test passes but no database record

**Possible causes**:
- Database session not committed
- Wrong database queried
- Transaction rollback in fixture

**Solution**: Verify UsageTrackingService integration and session handling.

## Next Steps

After these tests are created:

1. **Verify tests fail**: Run tests to confirm RED phase
2. **Hand off to Coder Agent**: Implement OpenRouterService to make tests pass
3. **Verify tests pass**: Run tests again to confirm GREEN phase
4. **Refactor if needed**: Improve code while keeping tests passing

## Test Maintenance

### When to update these tests:

- OpenRouter API changes response format
- New models are added to service
- Cost tracking requirements change
- Error handling improvements needed

### What NOT to change:

- Test assertions (these define the contract)
- Integration test markers (keep real API calls)
- Database validation logic (ensure cost tracking works)

## Additional Notes

### Why REAL_INTEGRATION_TESTS?

These tests use real API calls (not mocked) because:

1. **Validate actual behavior**: Mocks can lie, real APIs don't
2. **Catch integration issues**: Network, serialization, auth problems
3. **Verify cost calculation**: Real token counts = real cost validation
4. **Document expected behavior**: Real responses show what to expect

### Why only 4 tests?

This is **MVP-level testing** per project guidelines:
- Covers critical paths (happy path + error handling)
- Validates integration with database
- Tests both small (7B) and large (235B) models
- Balances coverage with development speed

### Performance Considerations

- Integration tests are slower (10-30s total)
- Run during development, not on every save
- CI/CD should run these on PR/merge only
- Consider caching API responses for faster local dev (future enhancement)
