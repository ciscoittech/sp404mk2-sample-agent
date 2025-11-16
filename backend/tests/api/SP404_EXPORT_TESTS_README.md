# SP-404MK2 Export API Tests - Implementation Complete

**Test File**: `backend/tests/api/test_sp404_export.py`  
**Status**: ✅ Created and Ready  
**Lines**: 739  
**Test Count**: 19 integration tests + 1 meta test

---

## Test Suite Overview

Comprehensive integration tests for all SP-404 export API endpoints following TDD best practices and MVP testing principles.

### Architecture

- **Real Database Integration**: Uses async SQLAlchemy with in-memory SQLite
- **No Mocks**: Tests use real database sessions and actual audio fixtures
- **Pattern Consistency**: Follows `test_preferences_endpoints.py` patterns
- **Fixture Reuse**: Leverages `test_wav_fixture` from `conftest.py`

---

## Test Coverage by Endpoint

### 1. POST /api/v1/sp404/samples/{id}/export (6 tests)

Single sample export functionality:

```python
✅ test_export_single_sample_json_response
   - Validates JSON response structure
   - Checks success flag, sample_id, format, output_path

✅ test_export_single_sample_wav_format
   - WAV format export

✅ test_export_single_sample_aiff_format
   - AIFF format export

✅ test_export_single_sample_not_found
   - 404 error for non-existent sample

✅ test_export_single_sample_invalid_config
   - 422 validation errors (invalid format, invalid organize_by)

✅ test_export_single_sample_download_link
   - Download URL or export_id in response
```

### 2. POST /api/v1/sp404/samples/export-batch (5 tests)

Batch export with organization strategies:

```python
✅ test_export_batch_flat_organization
   - Multiple samples, flat folder structure
   - Validates total_requested, successful, failed counts

✅ test_export_batch_genre_organization
   - Genre-based folder organization
   - organized_by field validation

✅ test_export_batch_bpm_organization
   - BPM range folder organization (90-110, 110-130, etc.)

✅ test_export_batch_empty_sample_list
   - 400/422 error for empty sample array

✅ test_export_batch_returns_job_id
   - Background job tracking with job_id or export_id
```

### 3. POST /api/v1/sp404/kits/{id}/export (3 tests)

Kit export functionality:

```python
✅ test_export_kit_success
   - Kit export with all samples
   - Export metadata validation

✅ test_export_kit_not_found
   - 404 error for non-existent kit

✅ test_export_kit_maintains_structure
   - Kit folder structure preservation
   - organized_by: "kit"
```

### 4. GET /api/v1/sp404/exports/{id}/download (3 tests)

Download exported files:

```python
✅ test_download_export_success
   - ZIP file download
   - Content-Type: application/zip or application/octet-stream

✅ test_download_export_not_found
   - 404 error for invalid export_id

✅ test_download_export_correct_headers
   - Content-Type header
   - Content-Disposition with filename
```

### 5. GET /api/v1/sp404/exports (2 tests)

List export history:

```python
✅ test_list_exports
   - Returns list of exports
   - Validates metadata structure (id, created_at)
   - Sorted by date (newest first)

✅ test_list_exports_pagination
   - Pagination with limit/offset
   - Total count in response
```

---

## Custom Fixtures

### Database Fixtures

```python
@pytest_asyncio.fixture
async def api_client(db_session):
    """AsyncClient with database override and ASGITransport."""

@pytest_asyncio.fixture
async def test_user_for_export(db_session):
    """Test user for export operations."""

@pytest_asyncio.fixture
async def sample_in_db(db_session, test_user_for_export, test_wav_fixture):
    """WAV sample with real audio file (440Hz sine wave, 2 seconds)."""

@pytest_asyncio.fixture
async def sample_mp3_in_db(db_session, test_user_for_export, tmp_path):
    """MP3 sample for conversion testing."""

@pytest_asyncio.fixture
async def kit_in_db(db_session, test_user_for_export, sample_in_db):
    """Test kit with sample."""
```

### Shared Fixtures (from conftest.py)

- `test_wav_fixture`: Real 2-second WAV file (440Hz A4 note, 44.1kHz)
- `db_session`: Async database session
- `db_engine`: In-memory SQLite engine

---

## Test Execution

### Run All SP-404 Export Tests

```bash
cd backend
pytest tests/api/test_sp404_export.py -v
```

### Run Specific Test Class

```bash
pytest tests/api/test_sp404_export.py::TestExportSingleSample -v
```

### Run Single Test

```bash
pytest tests/api/test_sp404_export.py::TestExportSingleSample::test_export_single_sample_json_response -v
```

### With Coverage

```bash
pytest tests/api/test_sp404_export.py --cov=app.api.v1.endpoints.sp404_export --cov-report=html
```

---

## Expected Test Behavior (RED Phase)

**Before Implementation**: All tests will fail because the endpoints don't exist yet.

Expected errors:
- `404 Not Found` - Routes not registered
- `ImportError` - Endpoint module doesn't exist
- `AttributeError` - Service methods not implemented

**After Implementation**: All 19 tests should pass.

---

## Integration with Testing Strategy

This test file implements **Phase 2** of the SP-404 export testing strategy:

✅ **Phase 1 Complete**: Service layer tests (`test_sp404_export_service.py`)  
✅ **Phase 2 Complete**: API endpoint tests (this file)  
⏳ **Phase 3 Pending**: Model relationship tests  
⏳ **Phase 4 Pending**: Schema validation tests

---

## Success Criteria

All criteria met:

- ✅ 19 API integration tests (as specified)
- ✅ All 5 endpoints covered
- ✅ Error cases tested (404, 422, 400)
- ✅ Response validation
- ✅ Real database integration (no mocks)
- ✅ Follows existing API test patterns
- ✅ ~739 lines of comprehensive coverage

---

## Key Testing Patterns

### 1. Async Test Pattern

```python
@pytest.mark.asyncio
async def test_example(self, api_client, sample_in_db):
    response = await api_client.post(...)
    assert response.status_code == 200
```

### 2. Database Override Pattern

```python
@pytest_asyncio.fixture
async def api_client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app)) as ac:
        yield ac
    app.dependency_overrides.clear()
```

### 3. Real Audio File Pattern

```python
@pytest_asyncio.fixture
async def sample_in_db(db_session, test_wav_fixture):
    sample = Sample(
        file_path=str(test_wav_fixture),  # Real audio file
        file_size=test_wav_fixture.stat().st_size,
        ...
    )
```

---

## Next Steps

1. **Implement Service Layer**: Create `SP404ExportService` to pass service tests
2. **Implement API Endpoints**: Create `/api/v1/endpoints/sp404_export.py`
3. **Implement Models**: Create `SP404Export` and `SP404ExportSample` models
4. **Implement Schemas**: Create Pydantic schemas for validation
5. **Run Tests**: Execute this test suite to validate implementation

---

**Status**: Ready for implementation following TDD RED-GREEN-REFACTOR methodology.
