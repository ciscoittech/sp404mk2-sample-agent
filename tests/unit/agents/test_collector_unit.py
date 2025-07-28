"""
Unit tests for Collector Agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from src.agents.collector import CollectorAgent
from src.agents.base import AgentStatus


class TestCollectorAgent:
    """Test suite for Collector Agent."""
    
    @pytest.fixture
    def collector(self):
        """Create a collector agent instance."""
        return CollectorAgent()
    
    def test_agent_initialization(self, collector):
        """Test agent initializes correctly."""
        assert collector.name == "Collector"
        assert collector.description == "I find and collect samples based on search criteria"
        assert collector.status == AgentStatus.IDLE
        assert hasattr(collector, 'youtube_search')
        assert hasattr(collector, 'download_tool')
    
    @patch('src.agents.collector.YouTubeSearch')
    def test_youtube_search_initialization(self, mock_youtube_class):
        """Test YouTube search tool is initialized."""
        mock_instance = Mock()
        mock_youtube_class.return_value = mock_instance
        
        collector = CollectorAgent()
        
        mock_youtube_class.assert_called_once()
        assert collector.youtube_search == mock_instance
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_search_samples_basic(self, mock_post, collector):
        """Test basic sample search functionality."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'I found 5 great jazz samples from the 1970s...'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Mock YouTube search
        collector.youtube_search.search_videos = AsyncMock(return_value=[
            {
                'title': 'Rare 70s Jazz Breaks',
                'url': 'https://youtube.com/watch?v=test1',
                'channel': 'Vinyl Frontier',
                'duration': '10:30',
                'views': '50K'
            }
        ])
        
        result = await collector.search_samples(
            query="jazz drum breaks 1970s",
            count=5
        )
        
        assert collector.status == AgentStatus.IDLE
        assert isinstance(result, str)
        assert "found" in result.lower()
        mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_samples_error_handling(self, collector):
        """Test error handling in search."""
        # Mock API error
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("API Error")
            
            result = await collector.search_samples(
                query="test query",
                count=5
            )
            
            assert collector.status == AgentStatus.ERROR
            assert "error" in result.lower()
    
    def test_get_status(self, collector):
        """Test status reporting."""
        status = collector.get_status()
        
        assert status['name'] == "Collector"
        assert status['status'] == "idle"
        assert 'description' in status
        assert isinstance(status['tools'], list)
        assert len(status['tools']) == 2
    
    @pytest.mark.asyncio
    async def test_analyze_url(self, collector):
        """Test URL analysis."""
        # Mock the analyze method
        collector.youtube_search.get_video_metadata = AsyncMock(return_value={
            'title': 'Test Video',
            'channel': 'Test Channel',
            'duration': '5:00',
            'description': 'Test description'
        })
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': 'This video contains great samples...'
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            result = await collector.analyze_url('https://youtube.com/watch?v=test')
            
            assert isinstance(result, str)
            assert collector.status == AgentStatus.IDLE
    
    @pytest.mark.asyncio
    async def test_download_samples(self, collector):
        """Test sample download functionality."""
        # Mock download tool
        collector.download_tool.download_audio = AsyncMock(return_value={
            'success': True,
            'file_path': '/downloads/test.wav',
            'metadata': {
                'title': 'Test Download',
                'duration': 300
            }
        })
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': 'Successfully downloaded the sample...'
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            result = await collector.download_samples([
                'https://youtube.com/watch?v=test1'
            ])
            
            assert isinstance(result, str)
            assert collector.status == AgentStatus.IDLE
            collector.download_tool.download_audio.assert_called()
    
    def test_status_changes(self, collector):
        """Test status changes during operations."""
        assert collector.status == AgentStatus.IDLE
        
        collector.status = AgentStatus.WORKING
        assert collector.status == AgentStatus.WORKING
        
        collector.status = AgentStatus.ERROR
        assert collector.status == AgentStatus.ERROR
        
        collector.status = AgentStatus.IDLE
        assert collector.status == AgentStatus.IDLE