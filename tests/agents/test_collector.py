"""Tests for Collector Agent with AI capabilities."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
from datetime import datetime

from src.agents.collector import CollectorAgent
from src.agents.base import AgentStatus


class TestCollectorAgent:
    """Test suite for Collector Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a Collector Agent instance."""
        return CollectorAgent()
    
    @pytest.fixture
    def search_params(self):
        """Sample parameters for search tasks."""
        return {
            "genre": "jazz",
            "style": "bebop",
            "bpm_range": (120, 140),
            "era": "1950s",
            "max_results": 10,
            "quality_threshold": 0.8
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.name == "collector"
        assert agent.status == AgentStatus.IDLE
        assert hasattr(agent, 'ai_agent')
        assert agent.ai_agent is not None
    
    @pytest.mark.asyncio
    async def test_generate_search_queries(self, agent, search_params):
        """Test AI-powered search query generation."""
        task_id = "test_task_001"
        
        with patch.object(agent.ai_agent, 'run') as mock_ai:
            # Mock AI response with search queries
            mock_ai.return_value = MagicMock(
                data={
                    "queries": [
                        "jazz bebop drum breaks 120-140 bpm 1950s",
                        "charlie parker drum samples vintage",
                        "dizzy gillespie rhythm section loops"
                    ],
                    "reasoning": "Focused on bebop era with specific tempo range"
                }
            )
            
            result = await agent.execute(task_id, **search_params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "search_queries" in result.result
            assert len(result.result["search_queries"]) == 3
            
            # Verify AI was called with proper context
            mock_ai.assert_called_once()
            call_args = mock_ai.call_args[1]
            assert "genre" in str(call_args)
            assert "bebop" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_youtube_search_integration(self, agent, search_params):
        """Test YouTube search for samples."""
        task_id = "test_task_002"
        
        with patch.object(agent.ai_agent, 'run') as mock_ai, \
             patch('src.agents.collector.search_youtube') as mock_search:
            
            mock_ai.return_value = MagicMock(
                data={"queries": ["jazz drum breaks"]}
            )
            
            mock_search.return_value = [
                {
                    "url": "https://youtube.com/watch?v=test1",
                    "title": "Jazz Drum Breaks Collection",
                    "duration": 300,
                    "views": 10000
                },
                {
                    "url": "https://youtube.com/watch?v=test2",
                    "title": "Bebop Rhythms Sample Pack",
                    "duration": 240,
                    "views": 5000
                }
            ]
            
            result = await agent.execute(task_id, **search_params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "sources" in result.result
            assert len(result.result["sources"]) >= 2
            assert all("url" in source for source in result.result["sources"])
    
    @pytest.mark.asyncio
    async def test_ai_categorization(self, agent):
        """Test AI-powered content categorization."""
        task_id = "test_task_003"
        params = {
            "sources": [
                {"url": "https://youtube.com/watch?v=1", "title": "Funky Breaks Vol 1"},
                {"url": "https://youtube.com/watch?v=2", "title": "Classical Piano Samples"},
                {"url": "https://youtube.com/watch?v=3", "title": "Hip Hop Drums 90 BPM"}
            ],
            "target_genre": "hip-hop"
        }
        
        with patch.object(agent.ai_agent, 'run') as mock_ai:
            mock_ai.return_value = MagicMock(
                data={
                    "categorized": [
                        {
                            "url": "https://youtube.com/watch?v=1",
                            "category": "funk",
                            "relevance": 0.7,
                            "reason": "Funk breaks often used in hip-hop"
                        },
                        {
                            "url": "https://youtube.com/watch?v=2",
                            "category": "classical",
                            "relevance": 0.2,
                            "reason": "Not suitable for hip-hop production"
                        },
                        {
                            "url": "https://youtube.com/watch?v=3",
                            "category": "hip-hop",
                            "relevance": 0.95,
                            "reason": "Perfect match for requirements"
                        }
                    ]
                }
            )
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "categorized_sources" in result.result
            
            # Should filter by relevance
            high_relevance = [s for s in result.result["categorized_sources"] 
                            if s["relevance"] > 0.5]
            assert len(high_relevance) == 2
    
    @pytest.mark.asyncio
    async def test_quality_assessment(self, agent):
        """Test AI-powered quality assessment of sources."""
        task_id = "test_task_004"
        params = {
            "sources": [
                {
                    "url": "https://youtube.com/watch?v=1",
                    "title": "High Quality Drum Samples WAV",
                    "description": "Professional studio recordings"
                }
            ],
            "assess_quality": True
        }
        
        with patch.object(agent.ai_agent, 'run') as mock_ai:
            mock_ai.return_value = MagicMock(
                data={
                    "quality_scores": [
                        {
                            "url": "https://youtube.com/watch?v=1",
                            "quality_score": 0.9,
                            "factors": {
                                "title_indicates_quality": True,
                                "professional_description": True,
                                "format_mentioned": "WAV"
                            }
                        }
                    ]
                }
            )
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["sources"][0]["quality_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_url_validation(self, agent):
        """Test URL validation and availability checking."""
        task_id = "test_task_005"
        params = {
            "sources": [
                {"url": "https://youtube.com/watch?v=valid"},
                {"url": "https://youtube.com/watch?v=invalid"},
                {"url": "not-a-valid-url"}
            ],
            "validate_urls": True
        }
        
        with patch('src.agents.collector.validate_url') as mock_validate:
            mock_validate.side_effect = [True, False, False]
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["valid_sources"] == 1
            assert result.result["invalid_sources"] == 2
    
    @pytest.mark.asyncio
    async def test_download_size_estimation(self, agent):
        """Test estimation of download sizes."""
        task_id = "test_task_006"
        params = {
            "sources": [
                {"url": "https://youtube.com/watch?v=1", "duration": 300},
                {"url": "https://youtube.com/watch?v=2", "duration": 180}
            ],
            "estimate_sizes": True
        }
        
        with patch('src.agents.collector.estimate_download_size') as mock_estimate:
            mock_estimate.side_effect = [52_000_000, 31_000_000]  # ~52MB, ~31MB
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "total_estimated_size" in result.result
            assert result.result["total_estimated_size"] == 83_000_000
            assert all("estimated_size" in s for s in result.result["sources"])
    
    @pytest.mark.asyncio
    async def test_ai_model_cost_tracking(self, agent, search_params):
        """Test tracking of AI model usage costs."""
        task_id = "test_task_007"
        
        with patch.object(agent.ai_agent, 'run') as mock_ai, \
             patch('src.agents.collector.database.add_agent_log') as mock_log:
            
            # Mock AI response with token usage
            mock_response = MagicMock(
                data={"queries": ["test query"]},
                usage=MagicMock(
                    input_tokens=100,
                    output_tokens=50,
                    total_tokens=150
                )
            )
            mock_ai.return_value = mock_response
            
            result = await agent.execute(task_id, **search_params)
            
            assert result.status == AgentStatus.SUCCESS
            
            # Check that token usage was logged
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            token_log = next((log for log in log_calls 
                            if "tokens_used" in log.get("context", {})), None)
            assert token_log is not None
            assert token_log["context"]["tokens_used"] == 150
    
    @pytest.mark.asyncio
    async def test_batch_source_discovery(self, agent):
        """Test discovering sources from multiple platforms."""
        task_id = "test_task_008"
        params = {
            "genre": "electronic",
            "platforms": ["youtube", "soundcloud", "freesound"],
            "max_per_platform": 5
        }
        
        with patch.object(agent.ai_agent, 'run') as mock_ai, \
             patch('src.agents.collector.search_youtube') as mock_yt, \
             patch('src.agents.collector.search_soundcloud') as mock_sc, \
             patch('src.agents.collector.search_freesound') as mock_fs:
            
            mock_ai.return_value = MagicMock(
                data={"queries": ["electronic samples"]}
            )
            
            mock_yt.return_value = [{"url": f"yt_{i}", "platform": "youtube"} 
                                  for i in range(5)]
            mock_sc.return_value = [{"url": f"sc_{i}", "platform": "soundcloud"} 
                                  for i in range(5)]
            mock_fs.return_value = [{"url": f"fs_{i}", "platform": "freesound"} 
                                  for i in range(5)]
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert len(result.result["sources"]) == 15
            
            # Check platform distribution
            platforms = [s["platform"] for s in result.result["sources"]]
            assert platforms.count("youtube") == 5
            assert platforms.count("soundcloud") == 5
            assert platforms.count("freesound") == 5
    
    @pytest.mark.asyncio
    async def test_smart_filtering(self, agent):
        """Test AI-powered smart filtering of results."""
        task_id = "test_task_009"
        params = {
            "sources": [{"url": f"url_{i}", "title": f"Sample {i}"} 
                       for i in range(20)],
            "filter_criteria": {
                "min_quality": 0.7,
                "exclude_duplicates": True,
                "prefer_variety": True
            },
            "max_results": 10
        }
        
        with patch.object(agent.ai_agent, 'run') as mock_ai:
            # AI selects diverse, high-quality samples
            mock_ai.return_value = MagicMock(
                data={
                    "filtered": [
                        {"url": f"url_{i}", "keep": i % 2 == 0, "reason": "Quality/variety"}
                        for i in range(20)
                    ]
                }
            )
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert len(result.result["filtered_sources"]) <= 10
    
    @pytest.mark.asyncio
    async def test_error_handling_ai_failure(self, agent, search_params):
        """Test handling of AI model failures."""
        task_id = "test_task_010"
        
        with patch.object(agent.ai_agent, 'run') as mock_ai:
            mock_ai.side_effect = Exception("AI service unavailable")
            
            result = await agent.execute(task_id, **search_params)
            
            assert result.status == AgentStatus.FAILED
            assert "AI service unavailable" in result.error
    
    @pytest.mark.asyncio
    async def test_create_collection_summary(self, agent):
        """Test creating AI-generated collection summary."""
        task_id = "test_task_011"
        params = {
            "sources": [
                {"url": "url1", "title": "Jazz Drums", "category": "jazz"},
                {"url": "url2", "title": "Funk Bass", "category": "funk"},
                {"url": "url3", "title": "Soul Keys", "category": "soul"}
            ],
            "create_summary": True
        }
        
        with patch.object(agent.ai_agent, 'run') as mock_ai:
            mock_ai.return_value = MagicMock(
                data={
                    "summary": {
                        "description": "Diverse collection spanning jazz, funk, and soul",
                        "recommended_use": "Perfect for neo-soul and jazz-fusion production",
                        "key_characteristics": ["vintage", "organic", "groove-oriented"],
                        "total_sources": 3
                    }
                }
            )
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "collection_summary" in result.result
            assert "recommended_use" in result.result["collection_summary"]