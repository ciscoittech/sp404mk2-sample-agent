# Running Kit Builder Tests

## Quick Start

```bash
# From project root
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent

# Activate virtual environment (if needed)
source venv/bin/activate

# Run all kit builder tests
pytest backend/tests/services/test_kit_service.py \
       backend/tests/api/test_kit_endpoints.py \
       backend/tests/integration/test_kit_workflow.py -v
```

## Individual Test Files

```bash
# Service layer tests (30 tests)
pytest backend/tests/services/test_kit_service.py -v

# API endpoint tests (29 tests)
pytest backend/tests/api/test_kit_endpoints.py -v

# Integration workflow tests (8 tests)
pytest backend/tests/integration/test_kit_workflow.py -v
```

## Specific Test Patterns

```bash
# Run only kit creation tests
pytest backend/tests/services/test_kit_service.py::test_create_kit_success -v

# Run only recommendation tests
pytest backend/tests/services/test_kit_service.py -k "recommendation" -v

# Run only validation error tests
pytest backend/tests/ -k "invalid" -v

# Run only export tests
pytest backend/tests/ -k "export" -v
```

## Coverage Report

```bash
# Run with coverage
pytest backend/tests/services/test_kit_service.py \
       backend/tests/api/test_kit_endpoints.py \
       backend/tests/integration/test_kit_workflow.py \
       --cov=backend/app/services/kit_service \
       --cov=backend/app/api/v1/endpoints/kits \
       --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Expected Results

### Red Phase (Current - Before Implementation)
```
FAILED backend/tests/services/test_kit_service.py::test_create_kit_success - ImportError: cannot import name 'KitService'
...
========= 67 failed in X.XXs =========
```

### Green Phase (After Implementation)
```
backend/tests/services/test_kit_service.py::test_create_kit_success PASSED
backend/tests/services/test_kit_service.py::test_create_kit_name_too_long PASSED
...
========= 67 passed in X.XXs =========
```

## Test Categories

### Service Tests (30)
- Kit CRUD operations (11 tests)
- Pad assignment operations (10 tests)
- Recommendation algorithm (7 tests)
- Export system (2 tests)

### API Tests (29)
- List/create kits (7 tests)
- Get/update/delete kit (6 tests)
- Assign/remove samples (7 tests)
- Recommendations (3 tests)
- Export (4 tests)
- HTMX support (1 test)

### Integration Tests (8)
- Complete workflows
- Multi-step operations
- Cross-service coordination

## Debugging Failed Tests

```bash
# Run with verbose output and show locals
pytest backend/tests/services/test_kit_service.py::test_create_kit_success -vv --tb=long

# Run with print statements visible
pytest backend/tests/services/test_kit_service.py::test_create_kit_success -s

# Run with pdb debugger on failure
pytest backend/tests/services/test_kit_service.py::test_create_kit_success --pdb
```

## Database State

All tests use in-memory SQLite database:
- Fresh database for each test
- No persistence between tests
- No cleanup needed
- Fast execution

## Fixtures Available

See `backend/tests/conftest.py` for:
- `test_kit` - Basic kit
- `test_sample` - Generic sample
- `sample_kick_short` - Kick drum (0.5s)
- `sample_snare_short` - Snare drum (0.4s)
- `sample_hat_closed` - Closed hat (0.3s)
- `sample_loop_long` - Loop sample (5s)
- `sample_85bpm`, `sample_90bpm`, `sample_140bpm` - BPM matching
- `sample_hiphop`, `sample_jazz` - Genre matching
- And more...

## Continuous Integration

```bash
# Run all tests in CI mode
pytest backend/tests/ --maxfail=1 --disable-warnings -q

# Run with JUnit XML for CI systems
pytest backend/tests/ --junitxml=test-results.xml
```
