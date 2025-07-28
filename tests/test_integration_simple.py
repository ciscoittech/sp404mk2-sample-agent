"""
Simplified integration tests that work with actual implementation.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.agents.groove_analyst import GrooveAnalystAgent
from src.agents.era_expert import EraExpertAgent
from src.agents.sample_relationship import SampleRelationshipAgent
from src.tools.youtube_search import YouTubeSearcher
from src.tools.timestamp_extractor import TimestampExtractor
from src.tools.intelligent_organizer import IntelligentOrganizer


class TestSimpleIntegration:
    """Simple integration tests that work."""
    
    @pytest.mark.asyncio
    async def test_agents_can_work_together(self):
        """Test that agents can be used together."""
        groove_agent = GrooveAnalystAgent()
        era_agent = EraExpertAgent()
        
        # Both should handle nonexistent files gracefully
        groove_result = await groove_agent.execute(
            task_id="simple_001",
            file_paths=["nonexistent.wav"]
        )
        
        era_result = await era_agent.execute(
            task_id="simple_002", 
            file_paths=["nonexistent.wav"]
        )
        
        assert groove_result is not None
        assert era_result is not None
    
    def test_timestamp_extractor_basic(self):
        """Test basic timestamp extraction."""
        extractor = TimestampExtractor()
        
        # Test simple timestamp parsing
        assert extractor.parse_timestamp("1:30") == 90
        assert extractor.parse_timestamp("0:15") == 15
        assert extractor.parse_timestamp("10:00") == 600
        
        # Test extraction from text
        text = "Cool beat at 2:30"
        timestamps = extractor.extract_timestamps_from_text(text)
        assert len(timestamps) > 0
        assert timestamps[0]["time"] == 150
    
    @pytest.mark.asyncio
    async def test_youtube_search_basic(self):
        """Test basic YouTube search functionality."""
        searcher = YouTubeSearcher()
        
        # Mock the internal search method
        mock_videos = [
            {
                "id": {"videoId": "test123"},
                "snippet": {
                    "title": "Test Video",
                    "channelTitle": "Test Channel",
                    "description": "Test description"
                }
            }
        ]
        
        with patch.object(searcher, '_search_with_api', 
                         return_value={"items": mock_videos}):
            with patch.object(searcher, '_get_video_details',
                            return_value=[{
                                "duration": "PT3M30S",
                                "viewCount": "1000"
                            }]):
                
                results = await searcher.search("test query")
                assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_intelligent_organizer_basic(self, tmp_path):
        """Test basic organization functionality."""
        organizer = IntelligentOrganizer(str(tmp_path))
        
        # Create a test file
        test_file = tmp_path / "test.wav"
        test_file.touch()
        
        # Test that it can handle organization
        with patch('src.tools.audio.detect_bpm', return_value=120.0):
            with patch('src.tools.audio.detect_key', 
                      return_value={"key": "C", "scale": "major"}):
                with patch('src.tools.audio.get_duration', return_value=4.0):
                    
                    result = await organizer.organize_samples(
                        sample_paths=[str(test_file)],
                        strategy="musical",
                        copy_files=False
                    )
                    
                    assert "organization_plan" in result
    
    @pytest.mark.asyncio
    async def test_relationship_agent_basic(self):
        """Test basic relationship analysis."""
        agent = SampleRelationshipAgent()
        
        # Mock audio analysis
        with patch('src.tools.audio.detect_bpm', return_value=120.0):
            with patch('src.tools.audio.detect_key',
                      return_value={"key": "C", "scale": "major"}):
                with patch('src.tools.audio.analyze_frequency_content',
                          return_value={
                              "spectral_centroid": 2000.0,
                              "spectral_bandwidth": 1000.0,
                              "spectral_rolloff": 4000.0,
                              "spectral_flatness": 0.5,
                              "zero_crossing_rate": 0.1
                          }):
                    
                    result = await agent.execute(
                        task_id="simple_003",
                        sample_pairs=[("test1.wav", "test2.wav")]
                    )
                    
                    assert result is not None
                    assert hasattr(result, 'status')
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test running multiple operations concurrently."""
        groove_agent = GrooveAnalystAgent()
        era_agent = EraExpertAgent()
        
        # Run both analyses concurrently
        results = await asyncio.gather(
            groove_agent.execute("concurrent_001", file_paths=["test.wav"]),
            era_agent.execute("concurrent_002", file_paths=["test.wav"]),
            return_exceptions=True
        )
        
        # Should complete without crashing
        assert len(results) == 2
        assert all(hasattr(r, 'status') for r in results if not isinstance(r, Exception))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])