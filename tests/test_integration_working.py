"""
Working integration tests for SP404MK2 Sample Agent.
These tests verify that components work together correctly.
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


class TestAgentIntegration:
    """Test agents working together."""
    
    @pytest.mark.asyncio
    async def test_groove_and_era_agents_together(self):
        """Test groove and era agents analyzing the same file."""
        groove_agent = GrooveAnalystAgent()
        era_agent = EraExpertAgent()
        
        # Create mock audio data
        mock_audio = Mock()
        mock_sr = 44100
        
        with patch('src.tools.audio.detect_bpm', return_value=93.0):
            with patch('librosa.load', return_value=(mock_audio, mock_sr)):
                with patch('librosa.beat.beat_track', return_value=(93.0, [0, 0.65, 1.29, 1.94])):
                    with patch('librosa.onset.onset_detect', return_value=[0, 0.65, 1.29, 1.94]):
                        
                        # Run groove analysis
                        groove_result = await groove_agent.execute(
                            task_id="int_test_001",
                            file_paths=["test.wav"]
                        )
                        
                        # Run era analysis
                        era_result = await era_agent.execute(
                            task_id="int_test_002",
                            file_paths=["test.wav"]
                        )
                        
                        assert groove_result.status.value == "success"
                        assert era_result.status.value == "success"
    
    @pytest.mark.asyncio
    async def test_youtube_search_and_timestamp_extraction(self):
        """Test YouTube search followed by timestamp extraction."""
        searcher = YouTubeSearcher()
        extractor = TimestampExtractor()
        
        # Mock YouTube search results
        mock_search_results = [
            {
                "title": "90s Boom Bap Drums",
                "url": "https://youtube.com/watch?v=test123",
                "channel": "Sample Diggers",
                "duration": "5:30",
                "views": 10000,
                "upload_date": "2023-01-01",
                "quality_score": 0.85
            }
        ]
        
        with patch.object(searcher, '_youtube_api_search', return_value={"items": []}):
            with patch.object(searcher, '_process_search_results', return_value=mock_search_results):
                
                # Search for samples
                results = await searcher.search("boom bap drums", max_results=1)
                assert len(results) == 1
                assert results[0]["quality_score"] > 0.8
                
                # Extract timestamps from description
                mock_description = """
                Tracklist:
                0:00 - Intro drums
                0:30 - Classic boom bap break
                1:45 - Jazz-influenced pattern
                3:00 - Outro
                """
                
                timestamps = extractor.extract_timestamps_from_text(mock_description)
                assert len(timestamps) > 0
                assert timestamps[0]["seconds"] == 0
                assert "Intro drums" in timestamps[0]["description"]
    
    @pytest.mark.asyncio
    async def test_sample_relationship_analysis(self):
        """Test analyzing relationships between samples."""
        relationship_agent = SampleRelationshipAgent()
        
        # Mock sample data
        with patch('src.tools.audio.detect_bpm', side_effect=[90.0, 93.0]):
            with patch('src.tools.audio.detect_key', side_effect=[
                {"key": "C", "scale": "major", "confidence": 0.9},
                {"key": "G", "scale": "major", "confidence": 0.85}
            ]):
                with patch('src.tools.audio.analyze_frequency_content', return_value={
                    "spectral_centroid": 1500.0,
                    "spectral_bandwidth": 2000.0,
                    "spectral_rolloff": 4000.0,
                    "spectral_flatness": 0.5,
                    "zero_crossing_rate": 0.1
                }):
                    
                    result = await relationship_agent.execute(
                        task_id="int_test_003",
                        sample_pairs=[("drum1.wav", "drum2.wav")]
                    )
                    
                    assert result.status.value == "success"
                    assert "analyses" in result.result
    
    @pytest.mark.asyncio
    async def test_intelligent_organization(self, tmp_path):
        """Test intelligent organization of samples."""
        organizer = IntelligentOrganizer(str(tmp_path))
        
        # Create test files
        test_files = []
        for i in range(3):
            file_path = tmp_path / f"sample_{i}.wav"
            file_path.touch()
            test_files.append(str(file_path))
        
        # Mock audio analysis
        with patch('src.tools.audio.detect_bpm', side_effect=[90.0, 120.0, 93.0]):
            with patch('src.tools.audio.detect_key', return_value={"key": "C", "scale": "major"}):
                with patch('src.tools.audio.get_duration', return_value=4.0):
                    
                    # Test musical organization
                    result = await organizer.organize_samples(
                        sample_paths=test_files,
                        strategy="musical",
                        copy_files=False  # Don't actually copy
                    )
                    
                    assert "organization_plan" in result
                    assert "summary" in result
                    assert result["summary"]["total_samples"] == 3


class TestToolIntegration:
    """Test tools working together."""
    
    def test_timestamp_extractor_parsing(self):
        """Test timestamp extraction and parsing."""
        extractor = TimestampExtractor()
        
        # Test various timestamp formats
        test_text = """
        Check these timestamps:
        0:15 - Kick drum
        [1:30] Bass drop
        2:45: Snare pattern
        (3:00) Hi-hats
        """
        
        timestamps = extractor.extract_timestamps_from_text(test_text)
        
        assert len(timestamps) >= 4
        assert all("seconds" in ts for ts in timestamps)
        assert all("description" in ts for ts in timestamps)
        
        # Verify parsing
        assert extractor.parse_timestamp("1:30") == 90
        assert extractor.parse_timestamp("0:45") == 45
        assert extractor.parse_timestamp("1:02:30") == 3750
    
    @pytest.mark.asyncio
    async def test_youtube_search_quality_filtering(self):
        """Test YouTube search with quality filtering."""
        searcher = YouTubeSearcher()
        
        # Mock videos with different quality scores
        mock_videos = [
            {
                "title": "High Quality Drum Samples",
                "channel": "Pro Samples",
                "views": 100000,
                "duration": "3:45",
                "upload_date": "2024-01-01",
                "url": "https://youtube.com/watch?v=high",
                "quality_score": 0.9
            },
            {
                "title": "Random Beat Making Stream",
                "channel": "Amateur Hour",
                "views": 50,
                "duration": "2:35:00",
                "upload_date": "2024-01-01",
                "url": "https://youtube.com/watch?v=low",
                "quality_score": 0.3
            }
        ]
        
        with patch.object(searcher, '_youtube_api_search', return_value={"items": []}):
            with patch.object(searcher, '_process_search_results', return_value=mock_videos):
                
                # Search with high quality threshold
                results = await searcher.search(
                    "drum samples",
                    quality_threshold=0.8
                )
                
                assert len(results) == 1
                assert results[0]["quality_score"] >= 0.8
                assert "High Quality" in results[0]["title"]


class TestWorkflowIntegration:
    """Test complete workflows."""
    
    @pytest.mark.asyncio
    async def test_discovery_to_analysis_workflow(self):
        """Test discovering samples and analyzing them."""
        searcher = YouTubeSearcher()
        groove_agent = GrooveAnalystAgent()
        
        # Mock search results
        with patch.object(searcher, '_youtube_api_search', return_value={"items": []}):
            with patch.object(searcher, '_process_search_results', return_value=[
                {"title": "Test Sample", "url": "https://youtube.com/watch?v=test", "quality_score": 0.9}
            ]):
                
                # Step 1: Search
                search_results = await searcher.search("jazz drums")
                assert len(search_results) > 0
                
                # Step 2: Simulate download (mock file)
                mock_file = "downloaded_sample.wav"
                
                # Step 3: Analyze
                with patch('src.tools.audio.detect_bpm', return_value=120.0):
                    with patch('librosa.load', return_value=(Mock(), 44100)):
                        with patch('librosa.beat.beat_track', return_value=(120.0, [0, 0.5, 1.0, 1.5])):
                            
                            analysis_result = await groove_agent.execute(
                                task_id="workflow_001",
                                file_paths=[mock_file]
                            )
                            
                            assert analysis_result.status.value == "success"
    
    @pytest.mark.asyncio
    async def test_multi_agent_analysis_workflow(self):
        """Test multiple agents analyzing the same samples."""
        groove_agent = GrooveAnalystAgent()
        era_agent = EraExpertAgent()
        
        test_files = ["sample1.wav", "sample2.wav"]
        
        # Mock all required audio analysis functions
        with patch('src.tools.audio.detect_bpm', return_value=90.0):
            with patch('librosa.load', return_value=(Mock(), 44100)):
                with patch('librosa.beat.beat_track', return_value=(90.0, [0, 0.67, 1.33, 2.0])):
                    with patch('librosa.onset.onset_detect', return_value=[0, 0.67, 1.33, 2.0]):
                        with patch('librosa.feature.spectral_centroid', return_value=[[2000]]):
                        
                            # Run both agents concurrently
                            groove_task = groove_agent.execute("multi_001", file_paths=test_files)
                            era_task = era_agent.execute("multi_002", file_paths=test_files)
                            
                            groove_result, era_result = await asyncio.gather(groove_task, era_task)
                            
                            assert groove_result.status.value == "success"
                            assert era_result.status.value == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])