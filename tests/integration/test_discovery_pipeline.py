"""
Integration tests for the discovery pipeline.
Tests how components work together.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.tools.youtube_search import YouTubeSearcher
from src.agents.groove_analyst import GrooveAnalystAgent
from src.agents.era_expert import EraExpertAgent
from src.tools.intelligent_organizer import IntelligentOrganizer


class TestDiscoveryPipeline:
    """Test the complete discovery pipeline."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_analyze_organize_workflow(self, mock_youtube_results, mock_audio_files, temp_output_dir):
        """Test complete workflow from search to organization."""
        
        # Step 1: Search for samples
        searcher = YouTubeSearcher()
        with patch.object(searcher, '_youtube_api_search', 
                         return_value={"items": []}):
            with patch.object(searcher, '_process_search_results', 
                             return_value=mock_youtube_results):
                
                search_results = await searcher.search(
                    "boom bap drums 90 bpm",
                    max_results=2
                )
                
                assert len(search_results) == 2
        
        # Step 2: Simulate downloaded files
        downloaded_files = list(mock_audio_files.values())[:2]
        file_paths = [f["path"] for f in downloaded_files]
        
        # Step 3: Analyze with Groove Analyst
        groove_agent = GrooveAnalystAgent()
        groove_result = await groove_agent.execute(
            task_id="test_pipeline_001",
            file_paths=file_paths
        )
        
        assert groove_result.status == "SUCCESS"
        assert len(groove_result.result["analyses"]) == 2
        
        # Step 4: Analyze with Era Expert
        era_agent = EraExpertAgent()
        era_result = await era_agent.execute(
            task_id="test_pipeline_002",
            file_paths=file_paths
        )
        
        assert era_result.status == "SUCCESS"
        
        # Step 5: Organize samples
        organizer = IntelligentOrganizer(str(temp_output_dir))
        
        # Mock file operations
        with patch('shutil.copy2'):
            org_result = await organizer.organize_samples(
                sample_paths=file_paths,
                strategy="musical",
                analyze_relationships=False,  # Skip for speed
                copy_files=True
            )
            
            assert "organization_plan" in org_result
            assert len(org_result["organization_plan"]) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_data_flow(self, mock_audio_files):
        """Test data flow between agents."""
        
        file_path = mock_audio_files["drum_90bpm.wav"]["path"]
        
        # Groove analysis
        groove_agent = GrooveAnalystAgent()
        groove_result = await groove_agent.execute(
            task_id="test_flow_001",
            file_paths=[file_path]
        )
        
        groove_data = groove_result.result["analyses"][0]
        assert groove_data["bpm"] == 90.0
        
        # Era analysis  
        era_agent = EraExpertAgent()
        era_result = await era_agent.execute(
            task_id="test_flow_002",
            file_paths=[file_path],
            genre="hip-hop"  # Use groove data to inform genre
        )
        
        era_data = era_result.result["analyses"][0]
        assert "detected_era" in era_data
        
        # Use both results to enhance search
        enhanced_query = f"{groove_data['groove_type']} {era_data.get('detected_era', '')} drums"
        assert len(enhanced_query) > 10  # Should have meaningful content
    
    @pytest.mark.asyncio
    @pytest.mark.integration 
    async def test_error_propagation(self):
        """Test how errors propagate through the pipeline."""
        
        # Simulate YouTube search failure
        searcher = YouTubeSearcher()
        with patch.object(searcher, '_youtube_api_search',
                         side_effect=Exception("API Error")):
            with patch.object(searcher, '_scrape_youtube_search',
                             return_value=[]):  # Scraping also fails
                
                results = await searcher.search("test query")
                assert results == []  # Should handle gracefully
        
        # Try to analyze non-existent files
        groove_agent = GrooveAnalystAgent()
        result = await groove_agent.execute(
            task_id="test_error_001",
            file_paths=["nonexistent.wav"]
        )
        
        # Should complete but with no analyses
        assert result.status == "SUCCESS"
        assert len(result.result["analyses"]) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_agent_execution(self, mock_audio_files):
        """Test running multiple agents concurrently."""
        import asyncio
        
        file_paths = [f["path"] for f in list(mock_audio_files.values())[:2]]
        
        # Create agent tasks
        groove_agent = GrooveAnalystAgent()
        era_agent = EraExpertAgent()
        
        # Run concurrently
        groove_task = groove_agent.execute("concurrent_001", file_paths=file_paths)
        era_task = era_agent.execute("concurrent_002", file_paths=file_paths)
        
        results = await asyncio.gather(groove_task, era_task)
        
        # Both should succeed
        assert all(r.status == "SUCCESS" for r in results)
        assert len(results[0].result["analyses"]) == 2
        assert len(results[1].result["analyses"]) == 2


class TestOrganizationStrategies:
    """Test different organization strategies working together."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multi_strategy_organization(self, mock_audio_files, temp_output_dir):
        """Test organizing with different strategies."""
        
        file_paths = [f["path"] for f in mock_audio_files.values()]
        organizer = IntelligentOrganizer(str(temp_output_dir))
        
        strategies = ["musical", "groove", "genre"]
        results = {}
        
        for strategy in strategies:
            with patch('shutil.copy2'):
                result = await organizer.organize_samples(
                    sample_paths=file_paths,
                    strategy=strategy,
                    analyze_relationships=False,
                    copy_files=False  # Just plan
                )
                results[strategy] = result
        
        # Each strategy should produce different organization
        plans = [r["organization_plan"] for r in results.values()]
        
        # Check that strategies produce different structures
        assert len(set(str(p) for p in plans)) > 1  # Not all identical
        
        # All should organize all files
        for strategy, result in results.items():
            total_files = sum(len(files) for files in result["organization_plan"].values())
            assert total_files == len(file_paths)