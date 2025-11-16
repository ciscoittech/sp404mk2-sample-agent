# /test Command - Test Execution & Coverage

Run tests, analyze coverage, and improve test quality following MVP-level testing philosophy.

## Usage
```
/test
/test "api"
/test "services/audio_features_service"
/test "e2e"
```

## Workflow

### Stage 1: Test Execution

```markdown
**Senior Engineer** - Run tests
- Prompt: "Run the test suite for: {scope or 'all tests'}. Execute Pytest for backend tests and Playwright for E2E tests. Report results including pass/fail counts, errors, and any warnings."
- Tools: Bash
- Commands:
  - Backend: `pytest backend/tests/ -v --cov=backend/app`
  - Specific: `pytest backend/tests/{path} -v`
  - E2E: `cd frontend && npm run test:e2e`
  - Coverage: `pytest --cov=backend/app --cov-report=html`
- Output: Test results and coverage report
```

### Stage 2: Analysis (if failures detected)

```markdown
**Testing Specialist** - Analyze failures
- Prompt: "Analyze the test failures from Stage 1. For each failure, identify:
  1. What test failed and why
  2. Is it a test issue or code issue?
  3. What needs to be fixed?
  Provide specific recommendations for fixes."
- Tools: Read, Grep
- Output: Failure analysis with recommendations
```

### Stage 3: Fix Implementation (if needed)

Based on failure analysis, route to appropriate agent:

#### Code Fix Needed
```markdown
**Senior Engineer** - Fix code
- Prompt: "Fix the code issues causing test failures: {failure_description}. Make minimal changes to make tests pass. Don't modify tests unless they are incorrect."
- Tools: All tools (*)
- Output: Fixed code
```

#### Test Fix Needed
```markdown
**Testing Specialist** - Fix tests
- Prompt: "Fix the test issues: {failure_description}. Update tests to match correct behavior or fix incorrect test expectations. Ensure tests follow MVP-level philosophy (2-5 tests, real integrations)."
- Tools: Read, Edit
- Output: Fixed tests
```

### Stage 4: Coverage Analysis (optional)

```markdown
**Testing Specialist** - Analyze coverage
- Prompt: "Analyze test coverage for: {scope}. Identify critical code paths that lack tests. Recommend 2-5 MVP-level tests that would improve coverage for the most important features. Don't suggest over-testing simple utilities."
- Tools: Read, Grep, Bash
- Output: Coverage analysis with recommendations
```

### Stage 5: Test Improvement (optional)

```markdown
**Testing Specialist** → **Senior Engineer** - Add tests
- Prompt: "Implement the recommended tests from Stage 4. Follow MVP-level philosophy:
  - 2-5 tests per feature
  - Real database, real files
  - Focus on critical paths
  - Integration tests preferred
Write tests and verify they pass."
- Tools: All tools (*)
- Output: New tests
```

## Test Scopes

### Backend Tests
```bash
# All backend tests
pytest backend/tests/ -v

# Specific service
pytest backend/tests/services/test_audio_features_service.py -v

# Specific test
pytest backend/tests/api/test_samples.py::test_create_sample -v

# With coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Fast (skip slow tests)
pytest backend/tests/ -m "not slow" -v
```

### Frontend E2E Tests
```bash
# All E2E tests
cd frontend && npm run test:e2e

# Specific browser
npm run test:e2e -- --project=chromium

# Headed mode (see browser)
npm run test:e2e -- --headed

# Debug mode
npm run test:e2e -- --debug
```

### Test Markers
```python
@pytest.mark.slow          # Slow tests (>5 seconds)
@pytest.mark.integration   # Integration tests (database, API)
@pytest.mark.unit          # Unit tests (fast, isolated)
@pytest.mark.e2e           # End-to-end tests (Playwright)
```

## Test Quality Checklist

### MVP-Level Standards
- [ ] **2-5 tests per feature** (not 20+)
- [ ] **Real integrations** (real database, real files, NO mocks)
- [ ] **Critical paths covered** (happy path + 1-2 error cases)
- [ ] **Fixtures used** for shared test data
- [ ] **Tests are fast** (<5 seconds each for unit/integration)
- [ ] **Tests are isolated** (no dependencies between tests)

### Anti-Patterns to Avoid
- ❌ Testing framework code (FastAPI, SQLAlchemy)
- ❌ Testing simple getters/setters
- ❌ Exhaustive test matrices for simple CRUD
- ❌ Using mocks for database or file I/O
- ❌ Requiring 80% coverage for utilities
- ❌ Over-testing to reach arbitrary coverage goals

## Coverage Targets (Pragmatic)

### High Priority (>80% coverage)
- Services with business logic (audio analysis, AI integration)
- API endpoints (request/response handling)
- Database operations (queries, migrations)

### Medium Priority (>50% coverage)
- Models and schemas
- Utilities with complex logic
- Error handling paths

### Low Priority (test only if bugs found)
- Simple CRUD operations
- Getters/setters
- Configuration files
- Constants

## Test Debugging

### Debug Failing Test
```bash
# Run with verbose output
pytest backend/tests/path/to/test.py::test_name -vv

# Run with print statements visible
pytest backend/tests/path/to/test.py::test_name -s

# Drop into debugger on failure
pytest backend/tests/path/to/test.py::test_name --pdb

# Show local variables on failure
pytest backend/tests/path/to/test.py::test_name -l
```

### Debug E2E Test
```bash
# Run in headed mode
npm run test:e2e -- --headed

# Debug mode (step through)
npm run test:e2e -- --debug

# Slow motion (see what's happening)
npm run test:e2e -- --slow-mo=1000
```

## Common Test Patterns

### Service Test (MVP-Level)
```python
class TestAudioFeaturesService:
    """Test audio feature extraction (3 tests - MVP level)."""

    async def test_extract_features_success(self, test_audio_file):
        """Happy path - successful extraction."""
        service = AudioFeaturesService()
        features = await service.extract_features(test_audio_file)

        assert features["bpm"] > 0
        assert features["key"] in ["C", "C#", "D", ...]

    async def test_extract_features_invalid_file(self):
        """Error case - invalid file."""
        service = AudioFeaturesService()

        with pytest.raises(Exception):
            await service.extract_features("/nonexistent.wav")

    async def test_extract_features_integration(self, db_session, sample_in_db):
        """Integration test - full workflow."""
        service = AudioFeaturesService()

        features = await service.extract_features(sample_in_db.file_path)

        # Save to database
        audio_features = AudioFeatures(sample_id=sample_in_db.id, **features)
        db_session.add(audio_features)
        await db_session.commit()

        # Verify saved correctly
        result = await db_session.execute(
            select(AudioFeatures).where(AudioFeatures.sample_id == sample_in_db.id)
        )
        saved = result.scalar_one()
        assert saved.bpm == features["bpm"]
```

### API Test (MVP-Level)
```python
class TestSamplesAPI:
    """Test samples API (3 tests - MVP level)."""

    async def test_create_sample_success(self, client, test_audio_file):
        """Happy path - successful creation."""
        with open(test_audio_file, 'rb') as f:
            response = await client.post(
                "/api/v1/samples",
                files={"audio_file": f},
                data={"name": "Test"}
            )

        assert response.status_code == 200
        assert response.json()["name"] == "Test"

    async def test_create_sample_invalid_file(self, client):
        """Error case - invalid file."""
        response = await client.post(
            "/api/v1/samples",
            files={"audio_file": b"not audio"},
            data={"name": "Invalid"}
        )

        assert response.status_code == 400

    async def test_create_sample_htmx(self, client, test_audio_file):
        """Integration - HTMX response."""
        with open(test_audio_file, 'rb') as f:
            response = await client.post(
                "/api/v1/samples",
                files={"audio_file": f},
                data={"name": "Test"},
                headers={"HX-Request": "true"}
            )

        assert response.status_code == 200
        assert "sample-card" in response.text
```

## Success Criteria
- All tests pass
- Coverage appropriate for code criticality
- No over-testing of simple code
- Real integrations (no unnecessary mocks)
- Tests are fast and isolated
- Critical paths well-covered
