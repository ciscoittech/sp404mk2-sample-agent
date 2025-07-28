"""
Basic functionality tests to verify the system works.
"""

import pytest
import asyncio
from pathlib import Path

# Test basic imports
def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.agents.groove_analyst import GrooveAnalystAgent
        from src.agents.era_expert import EraExpertAgent
        from src.agents.sample_relationship import SampleRelationshipAgent
        from src.tools.youtube_search import YouTubeSearcher
        from src.tools.timestamp_extractor import TimestampExtractor
        from src.tools.intelligent_organizer import IntelligentOrganizer
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_agent_creation():
    """Test that agents can be created."""
    from src.agents.groove_analyst import GrooveAnalystAgent
    from src.agents.era_expert import EraExpertAgent
    from src.agents.sample_relationship import SampleRelationshipAgent
    
    groove_agent = GrooveAnalystAgent()
    assert groove_agent.name == "groove_analyst"
    
    era_agent = EraExpertAgent()
    assert era_agent.name == "era_expert"
    
    relationship_agent = SampleRelationshipAgent()
    assert relationship_agent.name == "sample_relationship"


def test_tool_creation():
    """Test that tools can be created."""
    from src.tools.youtube_search import YouTubeSearcher
    from src.tools.timestamp_extractor import TimestampExtractor
    from src.tools.intelligent_organizer import IntelligentOrganizer
    
    searcher = YouTubeSearcher()
    assert searcher is not None
    
    extractor = TimestampExtractor()
    assert extractor is not None
    
    organizer = IntelligentOrganizer("/tmp/test")
    assert organizer is not None


@pytest.mark.asyncio
async def test_agent_execute_empty():
    """Test that agents handle empty inputs gracefully."""
    from src.agents.groove_analyst import GrooveAnalystAgent
    
    agent = GrooveAnalystAgent()
    
    # Test with nonexistent file
    result = await agent.execute(
        task_id="test_basic",
        file_paths=["nonexistent.wav"]
    )
    
    assert result is not None
    assert hasattr(result, 'status')
    assert hasattr(result, 'result')


def test_models():
    """Test that Pydantic models work correctly."""
    from src.agents.groove_analyst import (
        GrooveCharacteristics,
        TimingAnalysis,
        GrooveAnalysisResult
    )
    
    # Test GrooveCharacteristics
    groove = GrooveCharacteristics(
        swing_percentage=65.0,
        timing_feel="behind",
        pocket_score=8.5,
        humanization_level="human",
        ghost_note_density="medium"
    )
    assert groove.swing_percentage == 65.0
    
    # Test TimingAnalysis
    timing = TimingAnalysis(
        average_deviation_ms=15.0,
        swing_ratio="67:33",
        push_pull_ms=-5.0,
        consistency=0.85
    )
    assert timing.swing_ratio == "67:33"


def test_youtube_searcher_instance():
    """Test YouTubeSearcher can be instantiated."""
    from src.tools.youtube_search import YouTubeSearcher
    
    searcher = YouTubeSearcher()
    assert hasattr(searcher, 'search')
    assert hasattr(searcher, '_calculate_quality_score')


def test_timestamp_extractor_instance():
    """Test TimestampExtractor can be instantiated."""
    from src.tools.timestamp_extractor import TimestampExtractor
    
    extractor = TimestampExtractor()
    assert hasattr(extractor, 'parse_timestamp')
    assert hasattr(extractor, 'extract_timestamps_from_text')
    
    # Test basic timestamp parsing
    seconds = extractor.parse_timestamp("1:30")
    assert seconds == 90


def test_intelligent_organizer_instance(tmp_path):
    """Test IntelligentOrganizer can be instantiated."""
    from src.tools.intelligent_organizer import IntelligentOrganizer
    
    organizer = IntelligentOrganizer(str(tmp_path))
    assert organizer.base_path == Path(tmp_path)
    assert hasattr(organizer, 'organize_samples')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])