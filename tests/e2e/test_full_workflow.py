"""
End-to-end tests for the complete SP404MK2 Sample Agent workflow.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import json

from sp404_chat import SP404ChatAgent
from src.tools.youtube_search import YouTubeSearcher
from src.agents.groove_analyst import GrooveAnalystAgent
from src.agents.era_expert import EraExpertAgent
from src.agents.sample_relationship import SampleRelationshipAgent
from src.tools.timestamp_extractor import TimestampExtractor
from src.tools.intelligent_organizer import IntelligentOrganizer


class TestFullWorkflow:
    """Test complete workflow from user request to organized samples."""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_boom_bap_discovery_workflow(self, mock_youtube_results, mock_audio_files, temp_output_dir):
        """Test discovering and organizing boom bap samples."""
        
        # Step 1: User interacts with chat interface
        chat = SP404ChatAgent()
        
        with patch.object(chat.youtube_searcher, 'search',
                         return_value=mock_youtube_results[:2]):
            
            response = await chat.process_message(
                "Find me some 90s boom bap drum breaks around 90 BPM"
            )
            
            assert "boom bap" in response.lower()
            assert "90" in response
            assert "found" in response.lower()
        
        # Step 2: Extract timestamps from discovered videos
        extractor = TimestampExtractor()
        
        mock_timestamps = [
            {"seconds": 15, "time": "0:15", "description": "Classic boom bap break"},
            {"seconds": 45, "time": "0:45", "description": "DJ Premier style drums"}
        ]
        
        with patch.object(extractor, 'extract_from_youtube',
                         return_value={"timestamps": mock_timestamps}):
            
            timestamps = await extractor.extract_from_youtube(
                mock_youtube_results[0]["url"]
            )
            
            assert len(timestamps["timestamps"]) == 2
        
        # Step 3: Analyze samples with agents
        sample_files = list(mock_audio_files.values())[:2]
        file_paths = [f["path"] for f in sample_files]
        
        # Groove analysis
        groove_agent = GrooveAnalystAgent()
        groove_result = await groove_agent.execute(
            task_id="e2e_groove_001",
            file_paths=file_paths
        )
        
        assert groove_result.status == "SUCCESS"
        groove_data = groove_result.result["analyses"][0]
        assert groove_data["groove_type"] == "boom_bap"
        assert groove_data["swing_percentage"] > 10
        
        # Era analysis
        era_agent = EraExpertAgent()
        era_result = await era_agent.execute(
            task_id="e2e_era_001",
            file_paths=file_paths,
            genre="hip-hop"
        )
        
        assert era_result.status == "SUCCESS"
        era_data = era_result.result["analyses"][0]
        assert "1990s" in era_data["detected_era"]
        
        # Step 4: Check sample compatibility
        relationship_agent = SampleRelationshipAgent()
        compatibility_result = await relationship_agent.execute(
            task_id="e2e_rel_001",
            sample_pairs=[(file_paths[0], file_paths[1])]
        )
        
        assert compatibility_result.status == "SUCCESS"
        compatibility = compatibility_result.result["analyses"][0]
        assert compatibility["overall_score"] > 6.0  # Good compatibility
        
        # Step 5: Organize samples
        organizer = IntelligentOrganizer(str(temp_output_dir))
        
        with patch('shutil.copy2'):
            # Organize by SP404 template
            sp404_result = await organizer.organize_samples(
                sample_paths=file_paths,
                strategy="sp404",
                sp404_template="boom_bap",
                metadata=[
                    {
                        "path": file_paths[0],
                        "type": "drums",
                        "groove_type": "boom_bap",
                        "bpm": 90.0
                    },
                    {
                        "path": file_paths[1],
                        "type": "drums",
                        "groove_type": "boom_bap",
                        "bpm": 93.0
                    }
                ]
            )
            
            assert "pad_assignments" in sp404_result
            assert len(sp404_result["pad_assignments"]) == 2
            
            # Verify bank structure
            assert any("A1" in a["pad"] for a in sp404_result["pad_assignments"])
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_genre_specific_workflow(self, temp_output_dir):
        """Test workflow for specific genre requirements."""
        
        # Test jazz workflow
        chat = SP404ChatAgent()
        
        mock_jazz_results = [
            {
                "title": "Rare Jazz Breaks 1970s",
                "url": "https://youtube.com/watch?v=jazz123",
                "quality_score": 0.9
            }
        ]
        
        with patch.object(chat.youtube_searcher, 'search',
                         return_value=mock_jazz_results):
            
            response = await chat.process_message(
                "I need vintage jazz drum breaks from the 70s with brush playing"
            )
            
            assert "jazz" in response.lower()
            assert "1970s" in response or "70s" in response.lower()
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_intelligent_suggestions_workflow(self, mock_audio_files):
        """Test workflow with intelligent agent suggestions."""
        
        # Simulate user has some samples
        existing_samples = [
            mock_audio_files["drum_90bpm.wav"]["path"],
            mock_audio_files["bass_120bpm.wav"]["path"]
        ]
        
        # Get compatibility suggestions
        relationship_agent = SampleRelationshipAgent()
        result = await relationship_agent.execute(
            task_id="e2e_suggest_001",
            sample_pairs=[(existing_samples[0], existing_samples[1])]
        )
        
        analysis = result.result["analyses"][0]
        recommendations = analysis["recommendations"]
        
        # Should suggest tempo adjustment
        assert any("tempo" in r.lower() for r in recommendations)
        
        # Get era-based search suggestions
        era_agent = EraExpertAgent()
        era_result = await era_agent.execute(
            task_id="e2e_suggest_002",
            file_paths=[existing_samples[0]],
            enhance_search=True
        )
        
        era_data = era_result.result["analyses"][0]
        assert "enhanced_searches" in era_data
        assert len(era_data["enhanced_searches"]) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_error_recovery_workflow(self):
        """Test workflow handles errors gracefully."""
        
        chat = SP404ChatAgent()
        
        # Test with API failure
        with patch.object(chat.youtube_searcher, '_youtube_api_search',
                         side_effect=Exception("API Error")):
            with patch.object(chat.youtube_searcher, '_scrape_youtube_search',
                             return_value=[]):
                
                response = await chat.process_message(
                    "Find drum samples"
                )
                
                # Should handle gracefully
                assert "error" in response.lower() or "couldn't find" in response.lower()
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_batch_processing_workflow(self, mock_audio_files, temp_output_dir):
        """Test processing multiple samples in batch."""
        
        # Get all sample files
        all_files = [f["path"] for f in mock_audio_files.values()]
        
        # Batch groove analysis
        groove_agent = GrooveAnalystAgent()
        groove_result = await groove_agent.execute(
            task_id="e2e_batch_001",
            file_paths=all_files
        )
        
        assert len(groove_result.result["analyses"]) == len(all_files)
        
        # Batch organization
        organizer = IntelligentOrganizer(str(temp_output_dir))
        
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=all_files,
                strategy="groove",
                analyze_relationships=False  # Speed up test
            )
            
            # Should organize into groove categories
            plan = result["organization_plan"]
            assert "boom_bap" in str(plan).lower()
            assert "swing" in str(plan).lower()


class TestUserScenarios:
    """Test specific user scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_beginner_user_scenario(self):
        """Test workflow for a beginner user."""
        
        chat = SP404ChatAgent()
        
        # Beginner asks general question
        with patch.object(chat, '_handle_general_help') as mock_help:
            mock_help.return_value = "I can help you find samples!"
            
            response = await chat.process_message(
                "How do I find good samples?"
            )
            
            assert "help" in response.lower()
            assert mock_help.called
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_advanced_user_scenario(self, mock_audio_files):
        """Test workflow for an advanced user with specific needs."""
        
        # Advanced user wants specific analysis
        groove_agent = GrooveAnalystAgent()
        era_agent = EraExpertAgent()
        
        file_path = mock_audio_files["jazz_drums_93bpm.wav"]["path"]
        
        # Detailed groove analysis
        groove_result = await groove_agent.execute(
            task_id="e2e_advanced_001",
            file_paths=[file_path],
            detailed_analysis=True
        )
        
        groove_data = groove_result.result["analyses"][0]
        assert "micro_timing" in groove_data
        assert "humanization_score" in groove_data
        
        # Era-specific equipment info
        era_result = await era_agent.execute(
            task_id="e2e_advanced_002",
            target_era="1970s",
            genre="jazz",
            include_equipment=True
        )
        
        era_data = era_result.result["analyses"][0]
        assert "equipment" in era_data
        assert "techniques" in era_data
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_producer_workflow(self, mock_audio_files, temp_output_dir):
        """Test workflow for a music producer building a track."""
        
        # Producer has a concept
        target_bpm = 95
        target_key = "A minor"
        genre = "lo-fi hip-hop"
        
        # Find compatible samples
        all_samples = list(mock_audio_files.values())
        compatible_samples = []
        
        for sample in all_samples:
            # Check BPM compatibility (within 10%)
            if abs(sample["bpm"] - target_bpm) / target_bpm < 0.1:
                compatible_samples.append(sample["path"])
        
        # Analyze relationships
        if len(compatible_samples) >= 2:
            relationship_agent = SampleRelationshipAgent()
            
            pairs = [(compatible_samples[0], compatible_samples[1])]
            result = await relationship_agent.execute(
                task_id="e2e_producer_001",
                sample_pairs=pairs,
                genre=genre
            )
            
            # Get suggestions for the track
            analysis = result.result["analyses"][0]
            assert "arrangement" in analysis
            assert "recommendations" in analysis
        
        # Organize for project
        organizer = IntelligentOrganizer(str(temp_output_dir))
        
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=compatible_samples,
                strategy="project",
                project_name="LoFi_Beat_001"
            )
            
            assert "LoFi_Beat_001" in str(result["organization_plan"]).lower()


class TestIntegrationPoints:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_chat_to_agents_integration(self):
        """Test chat interface properly calls agents."""
        
        chat = SP404ChatAgent()
        
        # Mock all agent calls
        with patch.object(chat, 'groove_agent') as mock_groove:
            with patch.object(chat, 'era_agent') as mock_era:
                
                mock_groove.execute = AsyncMock(
                    return_value=Mock(result={"analyses": [{"groove_type": "boom_bap"}]})
                )
                mock_era.execute = AsyncMock(
                    return_value=Mock(result={"analyses": [{"detected_era": "1990s"}]})
                )
                
                # Process with agents
                with patch('os.path.exists', return_value=True):
                    response = await chat.process_message(
                        "analyze /path/to/sample.wav"
                    )
                
                # Should call both agents
                assert mock_groove.execute.called
                assert mock_era.execute.called
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_timestamp_to_download_integration(self):
        """Test timestamp extraction leads to proper download format."""
        
        extractor = TimestampExtractor()
        
        timestamps = [
            {"seconds": 30, "time": "0:30", "description": "Fire break", "confidence": 0.9},
            {"seconds": 90, "time": "1:30", "description": "Smooth groove", "confidence": 0.8}
        ]
        
        formatted = extractor.format_for_download(
            timestamps,
            video_url="https://youtube.com/watch?v=test123"
        )
        
        assert len(formatted) == 2
        assert all("url" in f for f in formatted)
        assert all("start_time" in f for f in formatted)
        assert all("filename" in f for f in formatted)
        
        # Filenames should be descriptive
        assert "fire_break" in formatted[0]["filename"].lower()
        assert "smooth_groove" in formatted[1]["filename"].lower()


class TestPerformance:
    """Test performance and scalability."""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_large_batch_performance(self, temp_output_dir):
        """Test performance with large number of samples."""
        
        # Create mock data for 100 samples
        large_sample_set = [
            {
                "path": f"/samples/sample_{i}.wav",
                "bpm": 90 + (i % 40),  # BPMs from 90-130
                "type": ["drums", "bass", "melodic"][i % 3]
            }
            for i in range(100)
        ]
        
        organizer = IntelligentOrganizer(str(temp_output_dir))
        
        start_time = asyncio.get_event_loop().time()
        
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=[s["path"] for s in large_sample_set],
                strategy="musical",
                metadata=large_sample_set,
                analyze_relationships=False  # Skip for performance
            )
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time
        assert execution_time < 5.0  # 5 seconds max
        
        # Should organize all samples
        total_organized = sum(
            len(files) for files in result["organization_plan"].values()
        )
        assert total_organized == 100