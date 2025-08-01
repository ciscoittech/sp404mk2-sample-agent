# SP404MK2 Sample Agent Testing Guide

This guide covers testing strategies, test scripts, and quality assurance for the SP404MK2 Sample Agent system, including the new Web UI with TDD/E2E testing.

## Table of Contents
1. [Testing Infrastructure](#testing-infrastructure)
2. [Test Scripts Overview](#test-scripts-overview)
3. [Running Tests](#running-tests)
4. [Testing Individual Components](#testing-individual-components)
5. [Integration Testing](#integration-testing)
6. [Performance Testing](#performance-testing)
7. [Test Data](#test-data)
8. [Web UI Testing](#web-ui-testing)

---

## Testing Infrastructure

### Backend Testing Stack
- **Framework**: pytest with pytest-asyncio
- **Coverage**: pytest-cov (minimum 80% requirement)
- **Mocking**: pytest-mock, factory-boy, faker
- **Linting**: ruff, black, mypy
- **Database**: SQLite in-memory for tests

### Frontend Testing Stack
- **E2E Framework**: Playwright
- **Build Tool**: Vite
- **Test Browsers**: Chrome, Firefox, Safari, Mobile
- **Visual Testing**: Screenshot comparisons

### CI/CD Pipeline
- **Platform**: GitHub Actions
- **Parallel Execution**: Backend and Frontend tests run concurrently
- **Coverage Reporting**: Codecov integration
- **Automated Checks**: Linting, type checking, security scanning

---

## Test Scripts Overview

The project includes comprehensive test scripts for each major component:

| Test Script | Purpose | Key Features Tested |
|------------|---------|-------------------|
| `test_groove_analyst.py` | Groove analysis testing | BPM detection, swing analysis, artist matching |
| `test_era_expert.py` | Era detection testing | Era identification, search enhancement, knowledge base |
| `test_sample_relationship.py` | Compatibility testing | Harmonic/rhythmic/frequency analysis, kit building |
| `test_intelligent_organizer.py` | Organization testing | All strategies, SP-404 templates, batch processing |

---

## Running Tests

### Basic Test Execution

```bash
# Test individual components
python test_groove_analyst.py
python test_era_expert.py
python test_sample_relationship.py
python test_intelligent_organizer.py

# Test conversational interface
python sp404_chat.py
# Type: "test mode" to run built-in tests
```

### Comprehensive Test Suite

```bash
# Create a test runner script
cat > run_all_tests.py << 'EOF'
import asyncio
import subprocess
import sys

async def run_all_tests():
    tests = [
        "test_groove_analyst.py",
        "test_era_expert.py", 
        "test_sample_relationship.py",
        "test_intelligent_organizer.py"
    ]
    
    for test in tests:
        print(f"\n{'='*60}")
        print(f"Running {test}")
        print('='*60)
        result = subprocess.run([sys.executable, test])
        if result.returncode != 0:
            print(f"FAILED: {test}")
            return False
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(run_all_tests())
EOF

python run_all_tests.py
```

---

## Testing Individual Components

### Groove Analyst Testing

**Test rhythm detection accuracy:**
```python
# Create test samples with known BPMs
test_samples = [
    ("samples/drum_loop_120bpm.wav", 120),
    ("samples/break_93bpm.wav", 93),
    ("samples/trap_140bpm.wav", 140)
]

for sample, expected_bpm in test_samples:
    result = await analyze_groove([sample])
    actual_bpm = result["analyses"][0]["bpm"]
    tolerance = 2.0  # +/- 2 BPM
    assert abs(actual_bpm - expected_bpm) < tolerance
```

**Test swing detection:**
```python
# Test with samples of known swing percentages
swing_samples = {
    "straight_beat.wav": (50, 55),      # Expected 50-55%
    "light_swing.wav": (55, 62),        # Expected 55-62%
    "heavy_swing.wav": (65, 75),        # Expected 65-75%
}

for sample, (min_swing, max_swing) in swing_samples.items():
    result = await analyze_groove([sample])
    swing = result["analyses"][0]["swing_percentage"]
    assert min_swing <= swing <= max_swing
```

### Era Expert Testing

**Test era detection:**
```python
# Test with samples from known eras
era_samples = {
    "motown_bass_1965.wav": "1950s-1960s",
    "funk_drums_1975.wav": "1970s",
    "dx7_synth_1985.wav": "1980s",
    "mpc_beat_1995.wav": "1990s"
}

for sample, expected_era in era_samples.items():
    result = await analyze_era([sample])
    detected = result["analyses"][0]["detected_era"]
    assert detected == expected_era
```

**Test search enhancement:**
```python
# Test query generation
queries = await get_era_search_queries(
    era="1970s",
    genre="soul",
    base_query="bass lines"
)

# Should include era-specific terms
assert any("funk" in q.lower() for q in queries)
assert any("1970" in q for q in queries)
```

### Sample Relationship Testing

**Test compatibility scoring:**
```python
# Test known compatible samples
compatible_pairs = [
    ("kick_C_90bpm.wav", "bass_C_90bpm.wav"),  # Same key, same BPM
    ("melody_C.wav", "pad_Am.wav"),             # Relative keys
]

for sample1, sample2 in compatible_pairs:
    result = await analyze_sample_compatibility([(sample1, sample2)])
    score = result["analyses"][0]["overall_score"]
    assert score >= 7.0  # Should be highly compatible
```

**Test frequency masking detection:**
```python
# Test samples with frequency conflicts
conflicting_pairs = [
    ("sub_bass_heavy.wav", "kick_subby.wav"),  # Both have sub content
    ("lead_bright.wav", "pad_bright.wav"),      # Both in high frequencies
]

for sample1, sample2 in conflicting_pairs:
    result = await analyze_sample_compatibility([(sample1, sample2)])
    masking = result["analyses"][0]["frequency"]["masking_risk"]
    assert masking in ["medium", "high"]
```

### Organization Testing

**Test organization strategies:**
```python
# Test each strategy
strategies = ["musical", "genre", "groove", "compatibility", "sp404", "project"]
test_samples = ["sample1.wav", "sample2.wav", "sample3.wav"]

for strategy in strategies:
    result = await organize_samples(
        test_samples,
        strategy=strategy,
        copy_files=False  # Dry run
    )
    assert "organization_plan" in result
    assert len(result["organization_plan"]) > 0
```

**Test SP-404 bank creation:**
```python
# Test with enough samples for a full kit
drum_samples = [
    "kick1.wav", "kick2.wav", "snare1.wav", "snare2.wav",
    "hihat1.wav", "hihat2.wav", "crash.wav", "ride.wav",
    # ... more samples
]

result = await create_sp404_banks(
    drum_samples,
    template="hip_hop_kit"
)

# Check bank structure
assert "SP404_Bank_A" in result["organization_plan"]
assert len(result["organization_plan"]["SP404_Bank_A"]) == 4  # 4 pads per bank
```

---

## Integration Testing

### End-to-End Discovery Test

```python
async def test_full_discovery_pipeline():
    # 1. Search for samples
    searcher = YouTubeSearcher()
    results = await searcher.search("jazz drums 90 bpm", max_results=5)
    assert len(results) > 0
    
    # 2. Extract timestamps (if video has them)
    extractor = TimestampExtractor()
    timestamps = await extractor.extract_timestamps(results[0]["url"])
    
    # 3. Download samples
    if timestamps:
        await extractor.extract_segments(
            results[0]["url"],
            output_dir="test_samples/",
            timestamps=timestamps[:2]  # First 2 segments
        )
    
    # 4. Analyze downloaded samples
    samples = glob.glob("test_samples/*.wav")
    groove_result = await analyze_groove(samples)
    assert groove_result["analyses"][0]["bpm"] > 0
    
    # 5. Organize samples
    org_result = await organize_samples(
        samples,
        strategy="musical",
        output_dir="test_organized/"
    )
    assert org_result["statistics"]["files_organized"] > 0
```

### Multi-Agent Coordination Test

```python
async def test_agent_coordination():
    test_samples = ["sample1.wav", "sample2.wav", "sample3.wav"]
    
    # Run all agents on same samples
    groove_task = analyze_groove(test_samples)
    era_task = analyze_era(test_samples)
    compat_task = analyze_sample_compatibility([
        (test_samples[0], test_samples[1]),
        (test_samples[1], test_samples[2])
    ])
    
    # Execute concurrently
    groove, era, compat = await asyncio.gather(
        groove_task, era_task, compat_task
    )
    
    # Verify all completed
    assert all(result.get("analyses") for result in [groove, era, compat])
```

---

## Performance Testing

### Batch Processing Test

```python
import time

async def test_batch_performance():
    # Test different batch sizes
    batch_sizes = [10, 20, 50, 100]
    samples = ["sample.wav"] * 100  # Reuse same sample
    
    for size in batch_sizes:
        batch = samples[:size]
        
        start = time.time()
        result = await analyze_groove(batch)
        duration = time.time() - start
        
        print(f"Batch size {size}: {duration:.2f} seconds")
        print(f"Per sample: {duration/size:.3f} seconds")
```

### Memory Usage Test

```python
import psutil
import os

async def test_memory_usage():
    process = psutil.Process(os.getpid())
    
    # Baseline memory
    baseline = process.memory_info().rss / 1024 / 1024  # MB
    
    # Process large batch
    large_batch = ["sample.wav"] * 200
    await organize_samples(large_batch, strategy="musical")
    
    # Peak memory
    peak = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Memory usage: {baseline:.1f}MB -> {peak:.1f}MB")
    print(f"Increase: {peak - baseline:.1f}MB")
```

---

## Test Data

### Creating Test Samples

```python
# Generate test samples with known properties
import numpy as np
import soundfile as sf

def create_test_sample(bpm, duration_sec, filename):
    """Create a simple drum pattern with exact BPM."""
    sample_rate = 44100
    beat_duration = 60.0 / bpm  # seconds per beat
    
    # Create click track
    samples = int(duration_sec * sample_rate)
    audio = np.zeros(samples)
    
    # Add clicks on beats
    beat_samples = int(beat_duration * sample_rate)
    for i in range(0, samples, beat_samples):
        # Short click sound
        click_duration = int(0.01 * sample_rate)
        audio[i:i+click_duration] = 0.5
    
    sf.write(filename, audio, sample_rate)

# Create test set
for bpm in [60, 90, 120, 140, 170]:
    create_test_sample(bpm, 4.0, f"test_{bpm}bpm.wav")
```

### Test Sample Categories

Create a test dataset with:

1. **Rhythm Samples**
   - Different BPMs (60-200)
   - Various swing percentages
   - Different time signatures

2. **Era Samples**
   - Vintage recordings (mono, limited frequency)
   - Modern productions (wide stereo, full frequency)
   - Era-specific processing (tape, digital, etc.)

3. **Harmonic Samples**
   - All 12 keys
   - Major and minor modes
   - Different instruments

4. **Problem Samples**
   - Very short (<0.5s)
   - Very long (>10min)
   - Non-musical (speech, noise)
   - Corrupted files

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        sudo apt-get install -y ffmpeg
    
    - name: Run tests
      env:
        OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
      run: |
        python run_all_tests.py
```

---

## Test Coverage

### Measuring Coverage

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m pytest tests/
coverage report
coverage html  # Generate HTML report
```

### Coverage Goals
- Core functionality: 90%+
- Agent logic: 85%+
- Error handling: 80%+
- Utilities: 75%+

---

## Debugging Tests

### Enable Debug Output

```python
# In test scripts
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific test
def test_with_debug():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Your test code
    logger.debug(f"Result: {result}")
```

### Mock External Services

```python
# Mock YouTube API for testing
from unittest.mock import patch

@patch('src.tools.youtube_search.YouTubeSearcher.search')
async def test_with_mock_youtube(mock_search):
    mock_search.return_value = [
        {"title": "Test Video", "url": "http://example.com"}
    ]
    
    # Your test using YouTube search
```

---

## Best Practices

1. **Test with real audio files** when possible
2. **Use small test files** to speed up tests
3. **Test edge cases** (empty files, wrong formats)
4. **Verify error handling** not just success cases
5. **Document expected vs actual** in assertions
6. **Clean up test files** after tests complete
7. **Use async properly** in test functions
8. **Test in isolation** before integration tests

---

## Web UI Testing

### TDD Workflow for Backend API

#### 1. Write Test First (Red Phase)
```python
# backend/tests/unit/test_sample_endpoints.py
@pytest.mark.unit
async def test_create_sample_endpoint(client, authenticated_user, sample_file):
    """Test sample creation endpoint - written BEFORE implementation."""
    response = await client.post(
        "/api/v1/samples",
        files={"file": ("test.wav", sample_file, "audio/wav")},
        data={"title": "TDD Test Sample", "genre": "hip-hop"},
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "TDD Test Sample"
    assert data["genre"] == "hip-hop"
    assert "id" in data
    assert "file_url" in data
```

#### 2. Implement Minimum Code (Green Phase)
```python
# backend/app/api/v1/endpoints/samples.py
@router.post("/", response_model=SampleResponse, status_code=201)
async def create_sample(
    title: str = Form(...),
    genre: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Minimal implementation to pass the test."""
    # Just enough code to make test pass
    return SampleResponse(
        id=1,
        title=title,
        genre=genre,
        file_url=f"/uploads/{file.filename}"
    )
```

#### 3. Refactor
- Add proper file storage
- Implement database persistence
- Add validation and error handling
- Keep tests passing!

### E2E Testing for Frontend

#### Setting Up E2E Tests
```bash
cd frontend
npm install
npx playwright install
```

#### Writing E2E Tests
```javascript
// frontend/tests/e2e/sample-upload.spec.js
const { test, expect, helpers } = require('./fixtures');

test.describe('Sample Upload', () => {
  test('user can upload a sample', async ({ authenticatedPage }) => {
    // Navigate to upload page
    await authenticatedPage.goto('/pages/samples.html');
    await authenticatedPage.click('[data-testid="upload-button"]');
    
    // Fill form
    await authenticatedPage.fill('[name="title"]', 'E2E Test Beat');
    await authenticatedPage.setInputFiles(
      'input[type="file"]',
      'tests/fixtures/test-beat.wav'
    );
    
    // Submit
    await authenticatedPage.click('[data-testid="submit-upload"]');
    
    // Wait for HTMX response
    await helpers.waitForHTMX(authenticatedPage);
    
    // Verify success
    await expect(authenticatedPage.locator('.toast-success'))
      .toContainText('Sample uploaded successfully');
    
    // Verify sample appears in list
    await expect(authenticatedPage.locator('[data-testid="sample-card"]'))
      .toContainText('E2E Test Beat');
  });
});
```

### Running Web UI Tests

#### Backend Tests
```bash
cd backend

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Watch mode (install pytest-watch first)
ptw
```

#### Frontend E2E Tests
```bash
cd frontend

# Install dependencies
npm install

# Run all E2E tests
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run specific test file
npm run test:e2e sample-upload.spec.js

# Debug mode with inspector
npm run test:e2e:debug
```

### CI/CD Integration

The project includes GitHub Actions workflow that:

1. **Runs on every push/PR**
2. **Parallel execution** of backend and frontend tests
3. **Multiple browser testing** for E2E
4. **Coverage requirements** (80% minimum)
5. **Security scanning** with Trivy

### Test Data Factories

#### Backend Test Data
```python
# backend/tests/conftest.py
from factory import Factory, Faker

class SampleFactory(Factory):
    class Meta:
        model = dict
    
    title = Faker('sentence', nb_words=3)
    bpm = Faker('random_int', min=60, max=180)
    genre = Faker('random_element', 
                  elements=['hip-hop', 'jazz', 'electronic'])

# Usage in tests
sample = SampleFactory()
samples = SampleFactory.create_batch(10)
```

#### Frontend Test Fixtures
```javascript
// frontend/tests/e2e/fixtures.js
exports.testSamples = [
  {
    id: 1,
    title: 'Test Jazz Drums',
    bpm: 93,
    genre: 'jazz',
    duration: 4200
  },
  // ... more test data
];
```

### Best Practices for Web UI Testing

1. **Use data-testid attributes** for reliable element selection
2. **Mock external services** in integration tests
3. **Use page objects** for complex E2E tests
4. **Run tests in parallel** where possible
5. **Keep tests independent** - each test should be able to run alone
6. **Use fixtures** for consistent test data
7. **Screenshot on failure** for debugging
8. **Test accessibility** alongside functionality

### Visual Regression Testing

```javascript
// Visual comparison tests
test('sample card appearance', async ({ page }) => {
  await page.goto('/pages/samples.html');
  await helpers.waitForHTMX(page);
  
  // Take screenshot for comparison
  await expect(page.locator('[data-testid="sample-card"]').first())
    .toHaveScreenshot('sample-card.png');
});
```

### Performance Testing for Web UI

```javascript
// Measure page load performance
test('sample library loads quickly', async ({ page }) => {
  const startTime = Date.now();
  
  await page.goto('/pages/samples.html');
  await page.waitForLoadState('networkidle');
  
  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(3000); // Under 3 seconds
  
  // Check Core Web Vitals
  const metrics = await page.evaluate(() => ({
    lcp: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime,
    fid: performance.getEntriesByType('first-input')[0]?.processingStart,
    cls: performance.getEntriesByType('layout-shift')
      .reduce((sum, entry) => sum + entry.value, 0)
  }));
  
  expect(metrics.lcp).toBeLessThan(2500); // LCP under 2.5s
  expect(metrics.cls).toBeLessThan(0.1);  // CLS under 0.1
});
```

---

*For contributing new tests, see [CONTRIBUTING.md](../CONTRIBUTING.md)*