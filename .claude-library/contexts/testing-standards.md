# Testing Standards - SP404MK2 Sample Agent

## Testing Philosophy

### MVP-Level Testing Principles

1. **2-5 Tests Per Feature** (NOT 20+)
   - Happy path (1 test)
   - Common error case (1-2 tests)
   - Edge case if critical (1 test)
   - Integration test (1 test)

2. **Real Integrations, NO Mocks**
   - Use real SQLite database (in-memory or temp file)
   - Use real audio files (test fixtures)
   - Use real API calls (with retry/timeout)
   - Mocks allowed only for external services you don't control

3. **Quality Over Quantity**
   - Test critical business logic
   - Don't test framework code (FastAPI, SQLAlchemy internals)
   - Don't test simple getters/setters
   - Focus on integration points

4. **Avoid Enterprise Complexity**
   - No test matrices for simple CRUD
   - No 80% coverage requirements for utilities
   - No exhaustive unit tests for simple functions
   - Test what matters, not what's easy to test

## Test Structure

### Backend Tests (`backend/tests/`)
```
backend/tests/
├── conftest.py              # Shared fixtures
├── fixtures/                # Test data
│   ├── kick.wav            # Test audio file
│   ├── snare.wav
│   └── hihat.wav
├── api/                     # API endpoint tests
│   ├── test_samples.py
│   ├── test_batch.py
│   └── test_preferences.py
├── services/                # Service layer tests
│   ├── test_audio_features_service.py
│   ├── test_openrouter_service.py
│   └── test_hybrid_analysis_service.py
├── models/                  # Model tests
│   └── test_sample_models.py
└── schemas/                 # Schema tests
    └── test_sample_schemas.py
```

### E2E Tests (`frontend/tests/e2e/`)
```
frontend/tests/e2e/
├── test-samples-page.spec.js
├── test-batch-page.spec.js
├── test-usage-page.spec.js
└── test-settings-page.spec.js
```

## Fixtures (conftest.py)

### Database Session
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

@pytest.fixture
async def db_session():
    """In-memory database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()
```

### Test Audio Files
```python
from pathlib import Path

@pytest.fixture
def test_audio_file():
    """Path to test audio file."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    return str(fixtures_dir / "kick.wav")

@pytest.fixture
def test_audio_files():
    """Multiple test audio files."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    return [
        str(fixtures_dir / "kick.wav"),
        str(fixtures_dir / "snare.wav"),
        str(fixtures_dir / "hihat.wav")
    ]
```

### Pre-Created Database Records
```python
@pytest.fixture
async def sample_in_db(db_session, test_audio_file):
    """Pre-created sample in database."""
    sample = Sample(
        name="Test Sample",
        file_path=test_audio_file,
        genre="hip-hop",
        duration=2.5
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample

@pytest.fixture
async def samples_in_db(db_session, test_audio_files):
    """Multiple pre-created samples."""
    samples = []
    for i, file_path in enumerate(test_audio_files):
        sample = Sample(
            name=f"Test Sample {i+1}",
            file_path=file_path,
            genre="hip-hop"
        )
        db_session.add(sample)
        samples.append(sample)

    await db_session.commit()
    for sample in samples:
        await db_session.refresh(sample)

    return samples
```

### HTTP Client
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    """Async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

## Service Tests (MVP-Level)

### Example: Audio Features Service
```python
class TestAudioFeaturesService:
    """Test audio feature extraction (3 tests - MVP level)."""

    async def test_extract_features_success(self, test_audio_file):
        """Happy path - successful extraction."""
        service = AudioFeaturesService()

        features = await service.extract_features(test_audio_file)

        # Verify essential features present
        assert "bpm" in features
        assert "key" in features
        assert "spectral_centroid" in features
        assert features["bpm"] > 0
        assert features["duration"] > 0

    async def test_extract_features_invalid_file(self):
        """Error case - invalid file."""
        service = AudioFeaturesService()

        with pytest.raises(Exception):  # librosa will raise
            await service.extract_features("/nonexistent/file.wav")

    async def test_extract_features_integration(self, sample_in_db, db_session):
        """Integration test - full workflow with database."""
        service = AudioFeaturesService()

        # Extract features
        features = await service.extract_features(sample_in_db.file_path)

        # Save to database
        audio_features = AudioFeatures(
            sample_id=sample_in_db.id,
            **features
        )
        db_session.add(audio_features)
        await db_session.commit()

        # Verify saved correctly
        result = await db_session.execute(
            select(AudioFeatures).where(AudioFeatures.sample_id == sample_in_db.id)
        )
        saved = result.scalar_one()
        assert saved.bpm == features["bpm"]
        assert saved.key == features["key"]
```

## API Tests (MVP-Level)

### Example: Samples API
```python
class TestSamplesAPI:
    """Test samples API (3-4 tests - MVP level)."""

    async def test_create_sample_success(self, client, test_audio_file):
        """Happy path - successful creation."""
        with open(test_audio_file, 'rb') as f:
            response = await client.post(
                "/api/v1/samples",
                files={"audio_file": f},
                data={"name": "Test Sample", "genre": "hip-hop"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Sample"
        assert data["genre"] == "hip-hop"
        assert data["id"] is not None

    async def test_create_sample_invalid_file(self, client):
        """Error case - invalid file type."""
        response = await client.post(
            "/api/v1/samples",
            files={"audio_file": b"not audio data"},
            data={"name": "Invalid"}
        )

        assert response.status_code == 400

    async def test_create_sample_htmx_response(self, client, test_audio_file):
        """Integration - HTMX template response."""
        with open(test_audio_file, 'rb') as f:
            response = await client.post(
                "/api/v1/samples",
                files={"audio_file": f},
                data={"name": "Test Sample"},
                headers={"HX-Request": "true"}
            )

        assert response.status_code == 200
        assert "sample-card" in response.text  # Check template rendered
        assert "Test Sample" in response.text

    async def test_list_samples_pagination(self, client, samples_in_db):
        """Integration - pagination works correctly."""
        response = await client.get("/api/v1/samples?page=1&page_size=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Page size respected
```

## E2E Tests (Playwright)

### Example: Samples Page
```javascript
import { test, expect } from '@playwright/test';

test.describe('Samples Page', () => {

    test('upload sample and verify display', async ({ page }) => {
        await page.goto('http://localhost:8100/pages/samples.html');

        // Click upload button
        await page.click('#upload-btn');

        // Fill form
        await page.setInputFiles('input[name="audio_file"]', 'tests/fixtures/kick.wav');
        await page.fill('input[name="name"]', 'Test Kick');
        await page.selectOption('select[name="genre"]', 'hip-hop');

        // Submit
        await page.click('button[type="submit"]');

        // Verify sample appears in grid
        await expect(page.locator('#sample-grid')).toContainText('Test Kick');
    });

    test('vibe analysis updates in real-time', async ({ page }) => {
        await page.goto('http://localhost:8100/pages/samples.html');

        // Click analyze button
        await page.click('button[data-action="analyze"]');

        // Wait for WebSocket connection
        await page.waitForSelector('#analysis-status:has-text("Analyzing")');

        // Wait for completion
        await page.waitForSelector('#analysis-status:has-text("Complete")', {
            timeout: 10000
        });

        // Verify vibe tags appear
        await expect(page.locator('.vibe-tags')).toBeVisible();
    });
});
```

## Test Markers

```python
import pytest

# Mark slow tests
@pytest.mark.slow
async def test_batch_processing_1000_samples():
    """Process 1000 samples (>5 seconds)."""
    pass

# Mark integration tests
@pytest.mark.integration
async def test_full_workflow():
    """Test complete workflow with database."""
    pass

# Mark unit tests
@pytest.mark.unit
def test_sanitize_filename():
    """Test filename sanitization (fast, isolated)."""
    pass
```

## Running Tests

### Backend Tests
```bash
# All tests
pytest backend/tests/ -v

# Specific test file
pytest backend/tests/services/test_audio_features_service.py -v

# Specific test
pytest backend/tests/api/test_samples.py::test_create_sample_success -v

# With coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Fast tests only (skip slow)
pytest backend/tests/ -m "not slow" -v

# Integration tests only
pytest backend/tests/ -m "integration" -v
```

### E2E Tests
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

## Coverage Targets (Pragmatic)

### High Priority (>80% coverage)
- Services with business logic
- API endpoints
- Database operations

### Medium Priority (>50% coverage)
- Models and schemas
- Utilities with complex logic

### Low Priority (test only if bugs found)
- Simple CRUD operations
- Getters/setters
- Configuration files

## Anti-Patterns to Avoid

❌ **Over-Testing Simple Code**
```python
# DON'T write 10 tests for simple getter
def test_sample_name_get():
    sample = Sample(name="Test")
    assert sample.name == "Test"
```

❌ **Using Mocks for Database**
```python
# DON'T mock database - use real database
@patch('sqlalchemy.ext.asyncio.AsyncSession')
async def test_create_sample(mock_db):
    pass
```

❌ **Testing Framework Code**
```python
# DON'T test FastAPI's validation
async def test_pydantic_validates_email():
    pass
```

✅ **Test Business Logic**
```python
# DO test your business logic
async def test_hybrid_analysis_combines_audio_and_ai():
    """Test that hybrid analysis correctly combines both phases."""
    pass
```

## Success Criteria
- 2-5 tests per feature
- Critical paths tested
- Real integrations (no unnecessary mocks)
- Tests are fast (<5 seconds each)
- Tests are isolated
- All tests pass
