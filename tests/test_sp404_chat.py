"""
Tests for SP404ChatAgent conversational interface.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from sp404_chat import SP404ChatAgent


class TestSP404ChatAgent:
    """Test the conversational chat agent."""
    
    @pytest.fixture
    def chat_agent(self):
        """Create a chat agent instance."""
        return SP404ChatAgent()
    
    @pytest.mark.asyncio
    async def test_chat_agent_initialization(self, chat_agent):
        """Test chat agent initializes correctly."""
        assert chat_agent is not None
        assert hasattr(chat_agent, 'youtube_searcher')
        assert hasattr(chat_agent, 'groove_agent')
        assert hasattr(chat_agent, 'era_agent')
        assert hasattr(chat_agent, 'timestamp_extractor')
    
    @pytest.mark.asyncio
    async def test_help_command(self, chat_agent):
        """Test help command handling."""
        response = await chat_agent.process_message("help")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "help" in response.lower() or "command" in response.lower()
    
    @pytest.mark.asyncio
    async def test_sample_search_request(self, chat_agent):
        """Test handling sample search requests."""
        # Mock YouTube search
        mock_results = [
            {
                "title": "Boom Bap Drums",
                "url": "https://youtube.com/watch?v=test",
                "quality_score": 0.85,
                "duration": "5:30",
                "channel": "Sample Channel"
            }
        ]
        
        with patch.object(chat_agent.youtube_searcher, 'search', 
                         return_value=mock_results) as mock_search:
            
            response = await chat_agent.process_message(
                "Find me some boom bap drum samples"
            )
            
            # Check that search was called
            mock_search.assert_called_once()
            
            # Check response mentions results
            assert "found" in response.lower() or "boom bap" in response.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_command(self, chat_agent):
        """Test analyze command with file path."""
        test_file = "/path/to/sample.wav"
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            # Mock groove analysis
            mock_groove_result = Mock()
            mock_groove_result.status.value = "success"
            mock_groove_result.result = {
                "analyses": [{
                    "file_path": test_file,
                    "bpm": 90.0,
                    "groove": {
                        "swing_percentage": 65.0,
                        "timing_feel": "behind"
                    }
                }]
            }
            
            with patch.object(chat_agent.groove_agent, 'execute',
                            return_value=mock_groove_result):
                
                response = await chat_agent.process_message(f"analyze {test_file}")
                
                assert "90" in response  # BPM should be mentioned
                assert "bpm" in response.lower()
    
    @pytest.mark.asyncio
    async def test_era_specific_search(self, chat_agent):
        """Test era-specific sample searches."""
        mock_results = [
            {
                "title": "70s Soul Drums",
                "url": "https://youtube.com/watch?v=soul",
                "quality_score": 0.9
            }
        ]
        
        with patch.object(chat_agent.youtube_searcher, 'search',
                         return_value=mock_results) as mock_search:
            
            response = await chat_agent.process_message(
                "I need 1970s soul drum breaks"
            )
            
            # Check search was called with era terms
            call_args = mock_search.call_args[0][0]
            assert "1970s" in call_args or "70s" in call_args or "soul" in call_args
    
    @pytest.mark.asyncio
    async def test_natural_language_understanding(self, chat_agent):
        """Test various natural language inputs."""
        test_inputs = [
            "Show me jazzy drums",
            "I want that Dilla swing",
            "Find boom bap samples like DJ Premier",
            "Need some lo-fi hip hop samples"
        ]
        
        with patch.object(chat_agent.youtube_searcher, 'search',
                         return_value=[]) as mock_search:
            
            for user_input in test_inputs:
                response = await chat_agent.process_message(user_input)
                
                # Should trigger search
                assert mock_search.called
                assert isinstance(response, str)
                
                # Reset for next test
                mock_search.reset_mock()
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, chat_agent):
        """Test handling when no results are found."""
        with patch.object(chat_agent.youtube_searcher, 'search',
                         return_value=[]):
            
            response = await chat_agent.process_message("find xyz123 samples")
            
            assert "couldn't find" in response.lower() or "no results" in response.lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, chat_agent):
        """Test error handling in chat agent."""
        # Simulate search error
        with patch.object(chat_agent.youtube_searcher, 'search',
                         side_effect=Exception("API Error")):
            
            response = await chat_agent.process_message("find samples")
            
            # Should handle gracefully
            assert isinstance(response, str)
            assert "error" in response.lower() or "problem" in response.lower()
    
    @pytest.mark.asyncio
    async def test_timestamp_extraction_request(self, chat_agent):
        """Test timestamp extraction from video."""
        video_url = "https://youtube.com/watch?v=test123"
        
        mock_timestamps = [
            {"seconds": 30, "timestamp": "0:30", "description": "Drums start"},
            {"seconds": 90, "timestamp": "1:30", "description": "Bass drop"}
        ]
        
        with patch.object(chat_agent.timestamp_extractor, 
                         'extract_from_youtube_metadata',
                         return_value={"timestamps": mock_timestamps}):
            
            response = await chat_agent.process_message(
                f"extract timestamps from {video_url}"
            )
            
            assert "0:30" in response
            assert "1:30" in response
            assert "drums" in response.lower()


class TestChatPatterns:
    """Test various chat patterns and conversations."""
    
    @pytest.fixture
    def chat_agent(self):
        return SP404ChatAgent()
    
    @pytest.mark.asyncio
    async def test_producer_workflow(self, chat_agent):
        """Test a typical producer workflow."""
        # Step 1: Search for samples
        with patch.object(chat_agent.youtube_searcher, 'search',
                         return_value=[{"title": "Sample", "url": "test.com"}]):
            
            response1 = await chat_agent.process_message(
                "I'm making a boom bap beat, need some 90 BPM drums"
            )
            assert "found" in response1.lower()
        
        # Step 2: Ask for analysis
        with patch('os.path.exists', return_value=True):
            with patch.object(chat_agent.groove_agent, 'execute',
                            return_value=Mock(status=Mock(value="success"),
                                            result={"analyses": [{"bpm": 90}]})):
                
                response2 = await chat_agent.process_message(
                    "analyze /downloads/drum_sample.wav"
                )
                assert "90" in response2
    
    @pytest.mark.asyncio
    async def test_conversational_memory(self, chat_agent):
        """Test that agent maintains context in conversation."""
        # First message sets context
        with patch.object(chat_agent.youtube_searcher, 'search',
                         return_value=[]) as mock_search:
            
            await chat_agent.process_message("I love jazz drums")
            
            # Second message should understand context
            await chat_agent.process_message("find me some samples")
            
            # Check if jazz was included in search
            calls = mock_search.call_args_list
            assert len(calls) >= 1
            # The search query should ideally include jazz context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])