"""
Unit tests for YouTube Search Tool.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.tools.youtube_search import YouTubeSearcher


class TestYouTubeSearcher:
    """Test suite for YouTube Search Tool."""
    
    @pytest.fixture
    def searcher(self):
        """Create a YouTube searcher instance."""
        return YouTubeSearcher()
    
    @pytest.fixture
    def mock_search_response(self):
        """Mock YouTube API search response."""
        return {
            "items": [
                {
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "90s Boom Bap Drum Breaks Vol. 1",
                        "channelTitle": "Sample Diggers",
                        "description": "Classic boom bap drum breaks from the golden era...",
                        "publishedAt": "2023-05-15T10:00:00Z"
                    },
                    "contentDetails": {"duration": "PT5M23S"},
                    "statistics": {"viewCount": "125000"}
                },
                {
                    "id": {"videoId": "def456"},
                    "snippet": {
                        "title": "How to Make Boom Bap Beats - Tutorial",
                        "channelTitle": "Beat School",
                        "description": "Learn how to create boom bap beats...",
                        "publishedAt": "2023-08-20T15:30:00Z"
                    },
                    "contentDetails": {"duration": "PT15M45S"},
                    "statistics": {"viewCount": "50000"}
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_search_basic(self, searcher, mock_search_response, mock_youtube_results):
        """Test basic search functionality."""
        with patch.object(searcher, '_youtube_api_search', 
                         return_value=mock_search_response):
            results = await searcher.search("boom bap drums")
            
            assert len(results) > 0
            assert results[0]["title"] == mock_youtube_results[0]["title"]
            assert "quality_score" in results[0]
            assert results[0]["url"].startswith("https://youtube.com/watch?v=")
    
    @pytest.mark.asyncio
    async def test_quality_scoring(self, searcher):
        """Test quality score calculation."""
        video = {
            "title": "Drum Breaks Sample Pack 90 BPM",
            "views": 100000,
            "duration": "4:30",
            "channel": "Sample Diggers",
            "upload_date": datetime.now().isoformat()
        }
        
        score = searcher._calculate_quality_score(video)
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should be good quality
        
        # Test low quality
        video_low = {
            "title": "My first beat attempt",
            "views": 50,
            "duration": "0:15",
            "channel": "Random User",
            "upload_date": datetime.now().isoformat()
        }
        
        score_low = searcher._calculate_quality_score(video_low)
        assert score_low < score  # Should be lower
    
    @pytest.mark.asyncio
    async def test_quality_filtering(self, searcher, mock_youtube_results):
        """Test filtering by quality threshold."""
        # Mock videos with different quality scores
        videos = [
            {**mock_youtube_results[0], "quality_score": 0.8},
            {**mock_youtube_results[1], "quality_score": 0.4}
        ]
        
        with patch.object(searcher, '_youtube_api_search', 
                         return_value={"items": []}):
            with patch.object(searcher, '_process_search_results', 
                             return_value=videos):
                
                # High threshold
                results = await searcher.search(
                    "test query",
                    quality_threshold=0.7
                )
                assert len(results) == 1
                assert results[0]["quality_score"] >= 0.7
                
                # Low threshold
                results = await searcher.search(
                    "test query",
                    quality_threshold=0.3
                )
                assert len(results) == 2
    
    def test_duration_parsing(self, searcher):
        """Test YouTube duration parsing."""
        assert searcher._parse_duration("PT5M23S") == "5:23"
        assert searcher._parse_duration("PT1H2M30S") == "1:02:30"
        assert searcher._parse_duration("PT45S") == "0:45"
        assert searcher._parse_duration("PT2H") == "2:00:00"
    
    def test_duration_scoring(self, searcher):
        """Test duration-based quality scoring."""
        # Optimal duration (30s - 5min)
        score_optimal = searcher._score_duration("2:30")
        assert score_optimal == 1.0
        
        # Too short
        score_short = searcher._score_duration("0:10")
        assert score_short < 1.0
        
        # Too long
        score_long = searcher._score_duration("25:00")
        assert score_long < 1.0
        
        # Edge cases
        assert searcher._score_duration("0:30") == 1.0
        assert searcher._score_duration("5:00") == 1.0
    
    def test_channel_reputation(self, searcher):
        """Test channel reputation scoring."""
        # Known good channels
        assert searcher._get_channel_reputation("Sample Diggers") > 0.5
        assert searcher._get_channel_reputation("Vinyl Frontier") > 0.5
        
        # Unknown channel
        assert searcher._get_channel_reputation("Random User 123") == 0.5
    
    def test_title_relevance(self, searcher):
        """Test title relevance scoring."""
        # High relevance
        score_high = searcher._score_title_relevance(
            "Boom Bap Drum Breaks Sample Pack 90 BPM"
        )
        assert score_high > 0.7
        
        # Low relevance (tutorial)
        score_low = searcher._score_title_relevance(
            "How to Make Beats - Beginner Tutorial"
        )
        assert score_low < 0.5
        
        # Negative keywords
        score_negative = searcher._score_title_relevance(
            "Reacting to Old School Hip Hop"
        )
        assert score_negative < 0.3
    
    @pytest.mark.asyncio
    async def test_era_specific_search(self, searcher):
        """Test era-specific search enhancements."""
        # Should add era-specific terms
        with patch.object(searcher, '_youtube_api_search', 
                         return_value={"items": []}):
            with patch.object(searcher, '_build_search_query') as mock_build:
                await searcher.search(
                    "drum breaks",
                    era="1990s",
                    genre="hip-hop"
                )
                
                # Check if era terms were added
                call_args = mock_build.call_args[0][0]
                assert "drum breaks" in call_args
    
    @pytest.mark.asyncio
    async def test_max_results_limit(self, searcher):
        """Test max results limiting."""
        # Create many mock results
        many_videos = [
            {"title": f"Video {i}", "quality_score": 0.8}
            for i in range(100)
        ]
        
        with patch.object(searcher, '_youtube_api_search', 
                         return_value={"items": []}):
            with patch.object(searcher, '_process_search_results', 
                             return_value=many_videos):
                
                results = await searcher.search(
                    "test",
                    max_results=10
                )
                
                assert len(results) == 10
    
    @pytest.mark.asyncio
    async def test_error_handling(self, searcher):
        """Test error handling in search."""
        # API error
        with patch.object(searcher, '_youtube_api_search', 
                         side_effect=Exception("API Error")):
            results = await searcher.search("test query")
            assert results == []  # Should return empty list
    
    def test_search_query_building(self, searcher):
        """Test search query construction."""
        # Basic query
        query = searcher._build_search_query("boom bap drums")
        assert query == "boom bap drums"
        
        # With filters
        query = searcher._build_search_query(
            "drums",
            genre="jazz",
            era="1970s"
        )
        assert "drums" in query
        assert "jazz" in query or "1970s" in query
    
    @pytest.mark.asyncio
    async def test_fallback_scraping(self, searcher):
        """Test fallback to scraping when API fails."""
        with patch.object(searcher, '_youtube_api_search', 
                         side_effect=Exception("API Error")):
            with patch.object(searcher, '_scrape_youtube_search', 
                             return_value=[{"title": "Scraped Result"}]):
                
                results = await searcher.search("test query")
                
                # Should fall back to scraping
                assert len(results) == 1
                assert results[0]["title"] == "Scraped Result"
    
    def test_view_count_parsing(self, searcher):
        """Test parsing various view count formats."""
        assert searcher._parse_view_count("1,234,567 views") == 1234567
        assert searcher._parse_view_count("1.2M views") == 1200000
        assert searcher._parse_view_count("500K views") == 500000
        assert searcher._parse_view_count("No views") == 0


class TestQualityScoringDetails:
    """Detailed tests for quality scoring algorithm."""
    
    @pytest.fixture
    def searcher(self):
        return YouTubeSearcher()
    
    def test_comprehensive_scoring(self, searcher):
        """Test comprehensive quality scoring."""
        # High quality video
        high_quality = {
            "title": "Rare Jazz Drum Breaks 1970s Vinyl Rip",
            "views": 250000,
            "duration": "3:45",
            "channel": "Crate Diggers",
            "upload_date": "2023-01-15",
            "description": "Fire drum breaks with timestamps 🔥🔥🔥"
        }
        
        score = searcher._calculate_quality_score(high_quality)
        assert score > 0.8
        
        # Medium quality
        medium_quality = {
            "title": "Random Beats Collection",
            "views": 5000,
            "duration": "8:00",
            "channel": "Unknown Producer",
            "upload_date": "2020-06-01",
            "description": "Some beats I made"
        }
        
        score_medium = searcher._calculate_quality_score(medium_quality)
        assert 0.4 < score_medium < 0.7
        
        # Low quality
        low_quality = {
            "title": "My Beat Making Stream VOD",
            "views": 100,
            "duration": "2:35:00",
            "channel": "Streamer123",
            "upload_date": "2024-01-01",
            "description": "Stream archive"
        }
        
        score_low = searcher._calculate_quality_score(low_quality)
        assert score_low < 0.4