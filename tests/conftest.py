"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("TURSO_URL", "libsql://test.turso.io")
    monkeypatch.setenv("TURSO_TOKEN", "test-token")


# Audio file fixtures
@pytest.fixture
def mock_audio_files():
    """Mock audio file data."""
    return {
        "drum_90bpm.wav": {
            "path": "tests/fixtures/audio/drum_90bpm.wav",
            "bpm": 90.0,
            "bpm_confidence": 0.95,
            "key": "C minor",
            "key_confidence": 0.87,
            "duration": 4.0,
            "frequency": {
                "spectral_centroid": 1500.0,
                "spectral_bandwidth": 2000.0,
                "spectral_rolloff": 4000.0
            }
        },
        "bass_120bpm.wav": {
            "path": "tests/fixtures/audio/bass_120bpm.wav",
            "bpm": 120.0,
            "bpm_confidence": 0.92,
            "key": "G major",
            "key_confidence": 0.90,
            "duration": 2.0,
            "frequency": {
                "spectral_centroid": 300.0,
                "spectral_bandwidth": 500.0,
                "spectral_rolloff": 1000.0
            }
        },
        "jazz_drums_93bpm.wav": {
            "path": "tests/fixtures/audio/jazz_drums_93bpm.wav",
            "bpm": 93.0,
            "bpm_confidence": 0.88,
            "key": "A minor",
            "key_confidence": 0.75,
            "duration": 8.0,
            "frequency": {
                "spectral_centroid": 2000.0,
                "spectral_bandwidth": 3000.0,
                "spectral_rolloff": 6000.0
            }
        }
    }


# YouTube search fixtures
@pytest.fixture
def mock_youtube_results():
    """Mock YouTube search results."""
    return [
        {
            "id": "abc123",
            "title": "90s Boom Bap Drum Breaks Vol. 1",
            "url": "https://youtube.com/watch?v=abc123",
            "channel": "Sample Diggers",
            "duration": "5:23",
            "views": 125000,
            "upload_date": "2023-05-15",
            "description": "Classic boom bap breaks...",
            "quality_score": 0.85
        },
        {
            "id": "def456",
            "title": "Jazz Drum Solos 1970s",
            "url": "https://youtube.com/watch?v=def456",
            "channel": "Jazz Archives",
            "duration": "12:45",
            "views": 45000,
            "upload_date": "2022-11-20",
            "description": "Rare jazz drum solos from the 70s...",
            "quality_score": 0.78
        }
    ]


# Timestamp fixtures
@pytest.fixture
def mock_timestamps():
    """Mock timestamp data."""
    return [
        {
            "time": "0:45",
            "time_seconds": 45.0,
            "description": "sick drum break",
            "fire_count": 3,
            "quality_score": 0.9
        },
        {
            "time": "2:30",
            "time_seconds": 150.0,
            "description": "jazz drum solo",
            "fire_count": 2,
            "quality_score": 0.8
        }
    ]


# OpenRouter API fixtures
@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API responses."""
    return {
        "choices": [{
            "message": {
                "content": "I'll help you find boom bap drums. Here are some searches..."
            }
        }]
    }


# Agent fixtures
@pytest.fixture
async def mock_groove_agent():
    """Mock Groove Analyst Agent."""
    agent = AsyncMock()
    agent.execute.return_value = Mock(
        status="SUCCESS",
        result={
            "analyses": [{
                "file_path": "test.wav",
                "bpm": 90.0,
                "swing_percentage": 65.5,
                "groove_type": "boom_bap",
                "timing_feel": "behind"
            }]
        }
    )
    return agent


@pytest.fixture
async def mock_era_agent():
    """Mock Era Expert Agent."""
    agent = AsyncMock()
    agent.execute.return_value = Mock(
        status="SUCCESS",
        result={
            "analyses": [{
                "detected_era": "1990s",
                "confidence": 0.85,
                "production_notes": "Classic boom bap production"
            }]
        }
    )
    return agent


# File system fixtures
@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir


# Mock audio analysis functions
@pytest.fixture(autouse=True)
def mock_audio_tools(monkeypatch, mock_audio_files):
    """Mock audio analysis tools."""
    
    def mock_detect_bpm(file_path):
        filename = os.path.basename(file_path)
        if filename in mock_audio_files:
            data = mock_audio_files[filename]
            return {"bpm": data["bpm"], "confidence": data["bpm_confidence"]}
        return {"bpm": 120.0, "confidence": 0.5}
    
    def mock_detect_key(file_path):
        filename = os.path.basename(file_path)
        if filename in mock_audio_files:
            data = mock_audio_files[filename]
            return {"key": data["key"], "confidence": data["key_confidence"]}
        return {"key": "C major", "confidence": 0.5}
    
    def mock_analyze_frequency(file_path):
        filename = os.path.basename(file_path)
        if filename in mock_audio_files:
            return mock_audio_files[filename]["frequency"]
        return {
            "spectral_centroid": 2000.0,
            "spectral_bandwidth": 1500.0,
            "spectral_rolloff": 4000.0
        }
    
    def mock_get_duration(file_path):
        filename = os.path.basename(file_path)
        if filename in mock_audio_files:
            return mock_audio_files[filename]["duration"]
        return 1.0
    
    # Patch the functions
    monkeypatch.setattr("src.tools.audio.detect_bpm", mock_detect_bpm)
    monkeypatch.setattr("src.tools.audio.detect_key", mock_detect_key)
    monkeypatch.setattr("src.tools.audio.analyze_frequency_content", mock_analyze_frequency)
    monkeypatch.setattr("src.tools.audio.get_duration", mock_get_duration)


# Database fixtures
@pytest.fixture
def mock_database(monkeypatch):
    """Mock database operations."""
    async def mock_add_log(*args, **kwargs):
        return {"id": "test-id"}
    
    async def mock_query(*args, **kwargs):
        return []
    
    monkeypatch.setattr("src.tools.database.add_agent_log", mock_add_log)
    monkeypatch.setattr("src.tools.database.query", mock_query)