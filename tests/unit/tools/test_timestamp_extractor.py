"""
Unit tests for Timestamp Extractor Tool.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.tools.timestamp_extractor import (
    TimestampExtractor,
    extract_youtube_timestamps,
    extract_fire_samples
)


class TestTimestampExtractor:
    """Test suite for Timestamp Extractor Tool."""
    
    @pytest.fixture
    def extractor(self):
        """Create a timestamp extractor instance."""
        return TimestampExtractor()
    
    @pytest.fixture
    def mock_video_comments(self):
        """Mock YouTube video comments with timestamps."""
        return [
            {
                "text": "Fire beats! 0:15 - Boom bap drums\n1:30 - Jazz break\n3:45 - Funk groove",
                "author": "BeatDigger",
                "likes": 45
            },
            {
                "text": "Timestamps:\n[00:00] Intro\n[02:30] Main break\n[04:15] Outro",
                "author": "SampleHunter",
                "likes": 23
            },
            {
                "text": "Best part at 2:30!",
                "author": "User123",
                "likes": 5
            }
        ]
    
    @pytest.fixture
    def mock_video_description(self):
        """Mock video description with timestamps."""
        return """Classic drum breaks collection.
        
Tracklist:
00:00 - Funky Drummer break
01:45 - Amen Break variation
03:20 - Think Break
05:00 - Apache Break

All samples are royalty-free.
        """
    
    def test_timestamp_extraction_from_text(self, extractor):
        """Test extracting timestamps from text."""
        text = "Check out 0:15 for drums and 2:30 for the bass drop"
        
        timestamps = extractor.extract_timestamps_from_text(text)
        
        assert len(timestamps) == 2
        assert timestamps[0]["timestamp"] == "0:15"
        assert timestamps[0]["seconds"] == 15
        assert "drums" in timestamps[0]["description"]
        
        assert timestamps[1]["timestamp"] == "2:30"
        assert timestamps[1]["seconds"] == 150
        assert "bass drop" in timestamps[1]["description"]
    
    def test_various_timestamp_formats(self, extractor):
        """Test parsing various timestamp formats."""
        test_cases = [
            ("0:15", 15),
            ("1:30", 90),
            ("10:45", 645),
            ("1:02:30", 3750),
            ("[00:15]", 15),
            ("(2:30)", 150),
            ("@ 3:45", 225),
            ("5:00 -", 300),
            ("- 0:30", 30)
        ]
        
        for timestamp_str, expected_seconds in test_cases:
            text = f"Sample at {timestamp_str} is fire"
            timestamps = extractor.extract_timestamps_from_text(text)
            
            assert len(timestamps) > 0
            assert timestamps[0]["seconds"] == expected_seconds
    
    def test_timestamp_with_descriptions(self, extractor):
        """Test extracting timestamps with descriptions."""
        text = """0:00 - Intro drums
        1:30 Jazz break (90 BPM)
        3:45: Funk groove sample"""
        
        timestamps = extractor.extract_from_text(text)
        
        assert len(timestamps) == 3
        assert timestamps[0]["description"] == "Intro drums"
        assert timestamps[1]["description"] == "Jazz break (90 BPM)"
        assert timestamps[2]["description"] == "Funk groove sample"
    
    @pytest.mark.asyncio
    async def test_extract_from_youtube(self, extractor, mock_video_comments, mock_video_description):
        """Test extracting timestamps from YouTube video."""
        with patch.object(extractor, 'extract_from_youtube_metadata', 
                         return_value={
                             "video_id": "test123",
                             "title": "Test Video",
                             "description": mock_video_description,
                             "timestamps": [
                                 {"seconds": 0, "timestamp": "0:00", "description": "Funky Drummer break"},
                                 {"seconds": 105, "timestamp": "1:45", "description": "Amen Break variation"}
                             ]
                         }):
            
            result = await extractor.extract_from_youtube_metadata("test123")
            
            assert "timestamps" in result
            timestamps = result["timestamps"]
            assert len(timestamps) > 0
            
            # Check if timestamps from description are included
            assert any(t["description"] == "Funky Drummer break" for t in timestamps)
            assert any(t["description"] == "Amen Break variation" for t in timestamps)
    
    def test_timestamp_deduplication(self, extractor):
        """Test deduplication of similar timestamps."""
        timestamps = [
            {"seconds": 15, "time": "0:15", "description": "Drums", "source": "desc"},
            {"seconds": 15, "time": "0:15", "description": "Drum break", "source": "comment"},
            {"seconds": 90, "time": "1:30", "description": "Bass", "source": "desc"},
            {"seconds": 91, "time": "1:31", "description": "Bass drop", "source": "comment"}
        ]
        
        deduplicated = extractor._deduplicate_timestamps(timestamps)
        
        # Should merge similar timestamps (within 5 seconds)
        assert len(deduplicated) == 2
        
        # Should keep the more detailed description
        assert any(t["description"] == "Drum break" for t in deduplicated)
        assert any("Bass" in t["description"] for t in deduplicated)
    
    def test_confidence_scoring(self, extractor):
        """Test confidence scoring for timestamps."""
        # High confidence - multiple sources
        timestamp1 = {
            "seconds": 30,
            "time": "0:30",
            "description": "Main break",
            "sources": ["description", "comment1", "comment2"]
        }
        
        confidence1 = extractor._calculate_confidence(timestamp1)
        assert confidence1 > 0.8
        
        # Low confidence - single source
        timestamp2 = {
            "seconds": 120,
            "time": "2:00",
            "description": "Maybe a break",
            "sources": ["comment_low_likes"]
        }
        
        confidence2 = extractor._calculate_confidence(timestamp2)
        assert confidence2 < 0.5
        assert confidence2 < confidence1
    
    def test_timestamp_sorting(self, extractor):
        """Test timestamp sorting."""
        unsorted_timestamps = [
            {"seconds": 90, "time": "1:30", "description": "Bass"},
            {"seconds": 15, "time": "0:15", "description": "Drums"},
            {"seconds": 300, "time": "5:00", "description": "Outro"},
            {"seconds": 0, "time": "0:00", "description": "Intro"}
        ]
        
        sorted_timestamps = extractor._sort_timestamps(unsorted_timestamps)
        
        # Check ascending order
        for i in range(len(sorted_timestamps) - 1):
            assert sorted_timestamps[i]["seconds"] <= sorted_timestamps[i + 1]["seconds"]
    
    def test_sample_type_detection(self, extractor):
        """Test detecting sample type from description."""
        test_cases = [
            ("Boom bap drums at 90 BPM", "drums"),
            ("Funky bass line", "bass"),
            ("Jazz piano chords", "melodic"),
            ("Vocal chop", "vocal"),
            ("808 sub bass", "bass"),
            ("Snare roll", "drums"),
            ("String section", "melodic"),
            ("Random sound", "unknown")
        ]
        
        for description, expected_type in test_cases:
            sample_type = extractor._detect_sample_type(description)
            assert sample_type == expected_type
    
    def test_bpm_extraction(self, extractor):
        """Test BPM extraction from descriptions."""
        test_cases = [
            ("Drum break 90 BPM", 90),
            ("120bpm house groove", 120),
            ("Slow funk @ 75 bpm", 75),
            ("Fast breaks (160 BPM)", 160),
            ("No BPM mentioned", None)
        ]
        
        for description, expected_bpm in test_cases:
            bpm = extractor._extract_bpm(description)
            assert bpm == expected_bpm
    
    @pytest.mark.asyncio
    async def test_batch_extraction(self, extractor):
        """Test batch extraction from multiple URLs."""
        urls = [
            "https://youtube.com/watch?v=test1",
            "https://youtube.com/watch?v=test2"
        ]
        
        mock_results = [
            {"timestamps": [{"seconds": 15, "time": "0:15", "description": "Drums"}]},
            {"timestamps": [{"seconds": 30, "time": "0:30", "description": "Bass"}]}
        ]
        
        with patch.object(extractor, 'extract_from_youtube',
                         side_effect=mock_results):
            
            results = await extractor.batch_extract(urls)
            
            assert len(results) == 2
            assert results[0]["url"] == urls[0]
            assert results[1]["url"] == urls[1]
            assert "timestamps" in results[0]
            assert "timestamps" in results[1]
    
    def test_format_for_download(self, extractor):
        """Test formatting timestamps for download tools."""
        timestamps = [
            {"seconds": 15, "time": "0:15", "description": "Drums", "confidence": 0.9},
            {"seconds": 90, "time": "1:30", "description": "Bass", "confidence": 0.7}
        ]
        
        formatted = extractor.format_for_download(
            timestamps,
            video_url="https://youtube.com/watch?v=test123",
            min_confidence=0.8
        )
        
        assert len(formatted) == 1  # Only high confidence
        assert formatted[0]["start_time"] == 15
        assert formatted[0]["end_time"] == 25  # Default 10 second duration
        assert formatted[0]["filename"].endswith("_drums.wav")
    
    def test_comment_quality_filtering(self, extractor):
        """Test filtering comments by quality."""
        comments = [
            {"text": "Timestamps: 0:15 drums", "likes": 100, "author": "Trusted"},
            {"text": "0:30 maybe something", "likes": 0, "author": "Random"},
            {"text": "Fire at 1:00!", "likes": 50, "author": "User"}
        ]
        
        # Should prioritize high-like comments
        quality_scores = [extractor._score_comment_quality(c) for c in comments]
        
        assert quality_scores[0] > quality_scores[1]  # More likes = higher quality
        assert quality_scores[2] > quality_scores[1]  # 50 likes > 0 likes
    
    def test_error_handling(self, extractor):
        """Test error handling."""
        # Invalid timestamp format
        result = extractor.extract_from_text("Bad timestamp at 99:99:99")
        assert len(result) == 0  # Should skip invalid timestamps
        
        # Empty text
        result = extractor.extract_from_text("")
        assert result == []
        
        # None input
        result = extractor.extract_from_text(None)
        assert result == []


class TestTimestampParsing:
    """Test timestamp parsing utilities."""
    
    def test_parse_timestamp_method(self):
        """Test the parse_timestamp method."""
        extractor = TimestampExtractor()
        assert extractor.parse_timestamp("0:15") == 15
        assert extractor.parse_timestamp("1:30") == 90
        assert extractor.parse_timestamp("1:02:30") == 3750


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_extract_youtube_timestamps_function(self):
        """Test the extract_youtube_timestamps convenience function."""
        with patch('src.tools.timestamp_extractor.TimestampExtractor') as MockExtractor:
            mock_instance = MockExtractor.return_value
            mock_instance.extract_from_youtube_metadata = AsyncMock(
                return_value={"timestamps": [{"timestamp": "0:15", "description": "test", "seconds": 15}]}
            )
            
            result = await extract_youtube_timestamps(
                video_url="https://youtube.com/watch?v=test"
            )
            
            assert "timestamps" in result
            assert len(result["timestamps"]) == 1