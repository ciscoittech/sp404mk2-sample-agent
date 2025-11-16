# Preferences API Endpoint Test Details

Comprehensive breakdown of all test scenarios for the Preferences API endpoints.

## Test 1: GET /api/v1/preferences - JSON Response

**Purpose**: Verify default preferences are created and returned as JSON

**Test Scenario**:
- Request without HX-Request header
- First access creates defaults in database
- Returns complete preference object with timestamps

**Assertions** (12 total):
- Status code: 200 OK
- Content-Type: application/json
- Response has all required fields (id, models, flags, timestamps)
- Default values match specification
  - id = 1 (single-row design)
  - vibe_analysis_model = "qwen/qwen3-7b-it"
  - auto_vibe_analysis = True
  - auto_audio_features = True
  - batch_processing_model = "qwen/qwen3-7b-it"
  - batch_auto_analyze = False
  - max_cost_per_request = None
- created_at and updated_at timestamps exist

---

## Test 2: GET /api/v1/preferences - HTMX Response

**Purpose**: Verify HTMX requests receive HTML form instead of JSON

**Test Scenario**:
- Request with HX-Request: true header
- Same endpoint, different response format
- Template rendering validation

**Assertions** (5 total):
- Status code: 200 OK
- Content-Type: text/html
- Response contains <form> element
- Form includes vibe_analysis_model field
- Form includes auto_vibe_analysis field
- Form includes batch_processing_model field

**Expected Template**: `preferences/preferences-form.html`

---

## Test 3: PATCH /api/v1/preferences - JSON Update

**Purpose**: Verify preference updates work with JSON payload

**Test Scenario**:
1. GET initial preferences
2. PATCH to update vibe_analysis_model
3. Verify response shows updated value
4. GET again to confirm database persistence

**Assertions** (8 total):
- Status code: 200 OK
- Content-Type: application/json
- Updated field shows new value
- Unchanged fields remain the same
- updated_at timestamp increases
- Changes persist across GET requests
- Database transaction succeeds

**Update Payload**:
```json
{
  "vibe_analysis_model": "qwen/qwen3-235b-a22b-2507"
}
```

---

## Test 4: PATCH /api/v1/preferences - HTMX Update

**Purpose**: Verify HTMX form submissions update preferences and return HTML

**Test Scenario**:
- PATCH with form-encoded data
- HX-Request header present
- Returns HTML success message instead of JSON

**Assertions** (6 total):
- Status code: 200 OK
- Content-Type: text/html
- HTML contains success/saved message
- Database update verified via GET
- Boolean fields parsed correctly from form data

**Form Payload**:
```
vibe_analysis_model=qwen/qwen3-235b-a22b-2507
auto_vibe_analysis=true
batch_auto_analyze=true
```

**Expected Template**: `preferences/preferences-success.html`

---

## Test 5: PATCH /api/v1/preferences - Partial Updates

**Purpose**: Verify partial updates work correctly without affecting other fields

**Test Scenario**:
1. Update only vibe_analysis_model
2. Verify only that field changed
3. Update only batch_auto_analyze
4. Verify both updates persisted (cumulative)
5. Update max_cost_per_request
6. Verify all three updates present

**Assertions** (9 total):
- First update: Only specified field changes
- Second update: Previous update persists + new change
- Third update: All previous updates persist + new change
- Each update increments updated_at timestamp
- String, boolean, and float fields all work
- None/null values are handled correctly

**Key Validation**: Uses Pydantic's `exclude_unset=True` to ignore unspecified fields

---

## Test 6: PATCH /api/v1/preferences - Validation Errors

**Purpose**: Verify invalid data is rejected with proper error messages

**Test Scenario**:
- Invalid model_id format (no '/' separator)
- Negative max_cost_per_request
- Zero max_cost_per_request
- Database remains unchanged after errors

**Assertions** (7 total):
- Invalid model format: 422 Unprocessable Entity
- Negative cost: 422 Unprocessable Entity
- Zero cost: 422 Unprocessable Entity
- Error responses include "detail" field
- Database unchanged after validation failures

**Invalid Payloads**:
```json
{"vibe_analysis_model": "invalid-model"}  // No '/' separator
{"max_cost_per_request": -0.05}           // Negative
{"max_cost_per_request": 0}               // Zero
```

**Validation Rules**:
- Model IDs must contain '/' (format: provider/model-name)
- max_cost_per_request must be positive or None

---

## Test 7: GET /api/v1/preferences/models - Model List

**Purpose**: Verify available models endpoint returns all model metadata

**Test Scenario**:
- GET request to /preferences/models
- No authentication required (static data)
- Returns list of available AI models with pricing

**Assertions** (11 total):
- Status code: 200 OK
- Content-Type: application/json
- Response has "models" field
- Models is a list
- Model count = 2 (7B and 235B)
- Each model has required fields:
  - model_id (string)
  - name (string)
  - input_cost (number)
  - output_cost (number)
  - description (string)
- Both expected models present:
  - qwen/qwen3-7b-it
  - qwen/qwen3-235b-a22b-2507

**Response Structure**:
```json
{
  "models": [
    {
      "model_id": "qwen/qwen3-7b-it",
      "name": "Qwen 7B (Fast)",
      "input_cost": 0.0000001,
      "output_cost": 0.0000001,
      "description": "Fast and cost-effective..."
    },
    {
      "model_id": "qwen/qwen3-235b-a22b-2507",
      "name": "Qwen 235B (Deep)",
      "input_cost": 0.0000008,
      "output_cost": 0.0000008,
      "description": "Powerful model for deep analysis..."
    }
  ]
}
```

---

## Test 8: GET /api/v1/preferences/models - Pricing Validation

**Purpose**: Verify pricing data is accurate and consistent

**Test Scenario**:
- GET models list
- Validate pricing relationships
- Ensure realistic per-token costs

**Assertions** (8 total):
- Both models found (7B and 235B)
- All costs are positive
- 235B input_cost > 7B input_cost
- 235B output_cost > 7B output_cost
- Costs are reasonable (< $1 per token)
- Pricing enables accurate cost estimation

**Expected Pricing Relationship**:
```
235B model > 7B model (more expensive)
All costs > 0
All costs < 1.0 (per-token micro-pricing)
```

---

## Test 9: Meta-Test - Endpoints Don't Exist

**Purpose**: Confirm we're in RED phase (TDD)

**Test Scenario**:
- Attempt to import preferences endpoint module
- Expect ImportError or AttributeError

**Assertion**:
- Import fails (module doesn't exist yet)

**Status**: PASSES (confirms RED phase)

---

## Summary Statistics

- **Total Tests**: 9 (8 endpoint tests + 1 meta-test)
- **Total Assertions**: ~76 assertions
- **Endpoints Covered**: 3 (GET, PATCH, GET /models)
- **Response Types**: JSON and HTML (HTMX)
- **Database Integration**: Real AsyncSession (no mocks)
- **Validation Tests**: 3 invalid input scenarios

## Test Patterns Used

1. **Dual Response Testing**: JSON vs HTMX based on headers
2. **Real Database Integration**: AsyncSession with rollback
3. **Persistence Verification**: GET after PATCH to confirm changes
4. **Sequential Updates**: Testing cumulative partial updates
5. **Validation Coverage**: Invalid model IDs, negative costs
6. **Fixture Reuse**: api_client fixture for all tests

## Ready for GREEN Phase

When Phase 3 (Coder) implements the endpoints:
- All 8 endpoint tests should PASS
- 1 meta-test will FAIL (module exists now)
- Total expected: 8 PASS, 1 FAIL
