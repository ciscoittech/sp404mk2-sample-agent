# SP404MK2 Sample Agent - Testing Guide

## Overview

This guide covers the comprehensive testing strategy for the SP404MK2 Sample Agent project. We follow Test-Driven Development (TDD) principles with a focus on reliability and maintainability.

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── mocks/               # Mock data and utilities
│   ├── __init__.py
│   └── audio.py         # Audio-related mocks
├── unit/                # Unit tests
│   ├── agents/          # Agent unit tests
│   └── tools/           # Tool unit tests
├── integration/         # Integration tests
│   └── test_discovery_pipeline.py
└── e2e/                 # End-to-end tests
    └── test_full_workflow.py
```

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test suites
make test-unit
make test-integration
make test-e2e
```

### Using the Test Runner

```bash
# Run all tests with coverage
python run_tests.py

# Run only unit tests
python run_tests.py unit

# Run specific test file
python run_tests.py specific tests/unit/agents/test_groove_analyst.py

# Run fast tests only (exclude slow)
python run_tests.py fast
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/agents/test_groove_analyst.py

# Run tests matching pattern
pytest -k "test_groove"

# Run with coverage
pytest --cov=src --cov-report=html
```

## Test Categories

### Unit Tests

Unit tests verify individual components in isolation:

- **Agent Tests**: Test each agent's logic and analysis capabilities
- **Tool Tests**: Test YouTube search, timestamp extraction, organization logic
- **Utility Tests**: Test helper functions and data models

Example:
```python
async def test_groove_detection(agent, mock_audio_files):
    """Test groove type detection."""
    result = await agent.execute(
        task_id="test_001",
        file_paths=[mock_audio_files["drum_90bpm.wav"]["path"]]
    )
    assert result.result["analyses"][0]["groove_type"] == "boom_bap"
```

### Integration Tests

Integration tests verify component interactions:

- **Pipeline Tests**: Test complete discovery and analysis workflows
- **Agent Coordination**: Test multiple agents working together
- **Data Flow**: Test data passing between components

Example:
```python
async def test_search_analyze_organize_workflow():
    """Test complete workflow from search to organization."""
    # Search for samples
    search_results = await searcher.search("boom bap drums")
    
    # Analyze with agents
    groove_result = await groove_agent.execute(file_paths=downloaded_files)
    
    # Organize samples
    org_result = await organizer.organize_samples(
        sample_paths=file_paths,
        strategy="musical"
    )
```

### End-to-End Tests

E2E tests verify complete user scenarios:

- **User Workflows**: Test from chat input to organized samples
- **Error Scenarios**: Test error handling and recovery
- **Performance**: Test with large datasets

## Mock Data

We use comprehensive mocks to avoid external dependencies:

### Audio File Mocks
```python
mock_audio_files = {
    "drum_90bpm.wav": {
        "path": "/test/drum_90bpm.wav",
        "bpm": 90.0,
        "key": "C major",
        "duration": 4.0,
        "energy": 0.75
    }
}
```

### API Response Mocks
```python
mock_youtube_results = [
    {
        "title": "90s Boom Bap Drum Breaks",
        "url": "https://youtube.com/watch?v=abc123",
        "quality_score": 0.85
    }
]
```

## Test Markers

We use pytest markers for test categorization:

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.e2e          # End-to-end tests
@pytest.mark.slow         # Tests that take > 5 seconds
@pytest.mark.asyncio      # Async tests
```

## Coverage Requirements

- **Target**: 80% overall coverage
- **Critical paths**: 95% coverage required
- **New code**: Must include tests

View coverage report:
```bash
# Generate HTML report
make coverage

# Open in browser
open htmlcov/index.html
```

## CI/CD Integration

Tests run automatically on:
- Every push to main/develop branches
- All pull requests
- Nightly builds (includes slow tests)

GitHub Actions workflow:
- Runs on Python 3.9, 3.10, 3.11
- Includes linting and type checking
- Uploads coverage to Codecov
- Generates test reports

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Mock external dependencies

### 2. Clear Test Names
```python
# Good
def test_groove_analyst_detects_boom_bap_pattern():

# Bad
def test_1():
```

### 3. Arrange-Act-Assert Pattern
```python
async def test_example():
    # Arrange
    agent = GrooveAnalystAgent()
    test_file = "drum_break.wav"
    
    # Act
    result = await agent.execute(file_paths=[test_file])
    
    # Assert
    assert result.status == "SUCCESS"
```

### 4. Use Fixtures
```python
@pytest.fixture
def mock_audio_data():
    """Reusable audio data for tests."""
    return {
        "sample_rate": 44100,
        "duration": 4.0,
        "audio": np.zeros(44100 * 4)
    }
```

### 5. Test Edge Cases
- Empty inputs
- Invalid data
- API failures
- Concurrent operations

## Debugging Tests

### Run single test with output
```bash
pytest -s -v tests/unit/agents/test_groove_analyst.py::TestGrooveAnalyst::test_swing_detection
```

### Use pdb debugger
```python
def test_something():
    import pdb; pdb.set_trace()  # Debugger will stop here
    result = function_under_test()
```

### View test logs
```bash
pytest --log-cli-level=DEBUG
```

## Adding New Tests

1. **Create test file** in appropriate directory
2. **Import required modules** and fixtures
3. **Write test class** grouping related tests
4. **Add test methods** following naming convention
5. **Run tests** to ensure they pass
6. **Check coverage** for the new code

Example template:
```python
"""
Unit tests for NewFeature.
"""

import pytest
from unittest.mock import Mock, patch

from src.module import NewFeature


class TestNewFeature:
    """Test suite for NewFeature."""
    
    @pytest.fixture
    def feature(self):
        """Create feature instance."""
        return NewFeature()
    
    def test_basic_functionality(self, feature):
        """Test basic feature behavior."""
        result = feature.process("input")
        assert result == "expected_output"
    
    @pytest.mark.asyncio
    async def test_async_operation(self, feature):
        """Test async feature behavior."""
        result = await feature.async_process("input")
        assert result.status == "SUCCESS"
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure project is installed with `pip install -e .`
2. **Async warnings**: Use `@pytest.mark.asyncio` decorator
3. **Mock not working**: Check patch path matches import path
4. **Flaky tests**: Add retries or fix race conditions

### Getting Help

- Check test output for detailed error messages
- Review similar tests for examples
- Consult pytest documentation
- Ask in project discussions

## Performance Testing

For performance-critical code:

```python
@pytest.mark.slow
async def test_large_batch_performance():
    """Test performance with 100+ samples."""
    samples = generate_large_sample_set(100)
    
    start_time = time.time()
    result = await process_samples(samples)
    execution_time = time.time() - start_time
    
    assert execution_time < 5.0  # Should complete within 5 seconds
    assert len(result) == 100
```

## Continuous Improvement

- Review test failures in CI/CD
- Add tests for bug fixes
- Refactor tests alongside code
- Update mocks when APIs change
- Monitor coverage trends

Remember: Good tests are as important as good code!