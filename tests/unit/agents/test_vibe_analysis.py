"""
Unit tests for Vibe Analysis Agent - TDD approach.
These tests are written BEFORE the implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime

# This import will fail until we implement the agent
from src.agents.vibe_analysis import VibeAnalysisAgent, SampleVibe, VibeDescriptor


class TestVibeAnalysisAgent:
    """Test suite for Vibe Analysis Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a vibe analysis agent instance."""
        return VibeAnalysisAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct properties."""
        assert agent.name == "VibeAnalyst"
        assert agent.description == "I analyze the vibe, mood, and character of audio samples"
        assert hasattr(agent, 'batch_size')
        assert agent.batch_size == 5  # Process 5 samples per API call
        assert hasattr(agent, 'rate_limit')
        assert agent.rate_limit == 5  # 5 requests per minute
    
    def test_vibe_descriptor_model(self):
        """Test the VibeDescriptor data model."""
        vibe = VibeDescriptor(
            mood=["dark", "atmospheric", "tense"],
            era="1970s",
            genre="jazz-funk",
            energy_level="medium",
            descriptors=["vintage", "analog", "warm"]
        )
        
        assert len(vibe.mood) == 3
        assert vibe.era == "1970s"
        assert vibe.genre == "jazz-funk"
        assert vibe.energy_level == "medium"
        assert "vintage" in vibe.descriptors
    
    def test_sample_vibe_model(self):
        """Test the SampleVibe data model."""
        sample = SampleVibe(
            filename="Adrian Younge Presents Venice Dawn.wav",
            bpm=85,
            key="Cm",
            vibe=VibeDescriptor(
                mood=["cinematic", "moody", "nostalgic"],
                era="modern-vintage",
                genre="soul",
                energy_level="low",
                descriptors=["lush", "orchestral", "analog"]
            ),
            compatibility_tags=["film-score", "downtempo", "night-vibes"],
            best_use="melodic-layer",
            confidence=0.85
        )
        
        assert sample.filename == "Adrian Younge Presents Venice Dawn.wav"
        assert sample.bpm == 85
        assert sample.key == "Cm"
        assert "cinematic" in sample.vibe.mood
        assert sample.best_use == "melodic-layer"
        assert sample.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_analyze_single_sample(self, agent):
        """Test analyzing a single sample."""
        sample_data = {
            "filename": "test_sample.wav",
            "bpm": 90,
            "key": "Am",
            "spectral_centroid": 1500.0,
            "spectral_rolloff": 4000.0
        }
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': '''
                        {
                            "mood": ["melancholic", "introspective", "warm"],
                            "era": "1990s",
                            "genre": "trip-hop",
                            "energy_level": "low",
                            "descriptors": ["dusty", "vinyl", "atmospheric"],
                            "compatibility_tags": ["chill", "night", "emotional"],
                            "best_use": "atmospheric-pad"
                        }
                        '''
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            result = await agent.analyze_vibe(sample_data)
            
            assert isinstance(result, SampleVibe)
            assert result.filename == "test_sample.wav"
            assert "melancholic" in result.vibe.mood
            assert result.vibe.genre == "trip-hop"
            assert result.best_use == "atmospheric-pad"
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, agent):
        """Test analyzing multiple samples in a batch."""
        samples = [
            {"filename": f"sample_{i}.wav", "bpm": 90 + i, "key": "C"}
            for i in range(5)
        ]
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': '''
                        [
                            {
                                "filename": "sample_0.wav",
                                "mood": ["energetic", "uplifting"],
                                "era": "modern",
                                "genre": "electronic",
                                "energy_level": "high",
                                "descriptors": ["digital", "clean"],
                                "compatibility_tags": ["dance", "club"],
                                "best_use": "drums"
                            },
                            {
                                "filename": "sample_1.wav",
                                "mood": ["dark", "mysterious"],
                                "era": "1980s",
                                "genre": "synthwave",
                                "energy_level": "medium",
                                "descriptors": ["analog", "retro"],
                                "compatibility_tags": ["night-drive", "cyberpunk"],
                                "best_use": "bassline"
                            }
                        ]
                        '''
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            results = await agent.analyze_batch(samples)
            
            assert len(results) >= 2
            assert all(isinstance(r, SampleVibe) for r in results)
            assert results[0].vibe.genre == "electronic"
            assert results[1].vibe.genre == "synthwave"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, agent):
        """Test that rate limiting is respected."""
        # Track sleep calls
        sleep_times = []
        
        async def mock_sleep(seconds):
            sleep_times.append(seconds)
            # Don't actually sleep in tests
            return
        
        with patch('asyncio.sleep', side_effect=mock_sleep):
            with patch('httpx.AsyncClient.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'choices': [{
                        'message': {'content': '{"mood": ["test"], "era": "test", "genre": "test"}'}
                    }]
                }
                mock_post.return_value = mock_response
                
                # Set last request time to trigger rate limiting
                agent.last_request_time = datetime.now()
                
                # Make a request that should trigger rate limiting
                await agent.analyze_vibe({"filename": "test.wav", "bpm": 120, "key": "C"})
                
                # Check that rate limiting was applied
                assert len(sleep_times) > 0
                assert any(t >= 11 for t in sleep_times)  # Should wait at least 11 seconds
    
    def test_create_batch_prompt(self, agent):
        """Test batch prompt creation."""
        samples = [
            {
                "filename": "jazz_sample.wav",
                "bpm": 85,
                "key": "Bb",
                "spectral_centroid": 1200.0
            },
            {
                "filename": "funk_sample.wav", 
                "bpm": 105,
                "key": "E",
                "spectral_centroid": 2500.0
            }
        ]
        
        prompt = agent.create_batch_prompt(samples)
        
        assert "jazz_sample.wav" in prompt
        assert "funk_sample.wav" in prompt
        assert "85" in prompt  # BPM
        assert "105" in prompt  # BPM
        assert "vibe" in prompt.lower()
        assert "compatibility" in prompt.lower()
    
    def test_parse_vibe_response(self, agent):
        """Test parsing AI response into vibe objects."""
        response = '''
        {
            "filename": "test.wav",
            "mood": ["groovy", "funky", "upbeat"],
            "era": "1970s",
            "genre": "funk",
            "energy_level": "high",
            "descriptors": ["classic", "raw", "authentic"],
            "compatibility_tags": ["party", "dance", "old-school"],
            "best_use": "drums"
        }
        '''
        
        vibe = agent.parse_vibe_response(response, "test.wav", 120, "C")
        
        assert isinstance(vibe, SampleVibe)
        assert vibe.filename == "test.wav"
        assert "groovy" in vibe.vibe.mood
        assert vibe.vibe.genre == "funk"
        assert vibe.best_use == "drums"
        assert vibe.bpm == 120
        assert vibe.key == "C"
    
    def test_vibe_compatibility_scoring(self, agent):
        """Test scoring compatibility between vibes."""
        vibe1 = VibeDescriptor(
            mood=["dark", "mysterious", "tense"],
            era="1980s",
            genre="synthwave",
            energy_level="medium",
            descriptors=["analog", "retro", "atmospheric"]
        )
        
        vibe2 = VibeDescriptor(
            mood=["dark", "brooding", "mysterious"],
            era="1980s", 
            genre="darkwave",
            energy_level="medium",
            descriptors=["analog", "vintage", "moody"]
        )
        
        vibe3 = VibeDescriptor(
            mood=["happy", "uplifting", "bright"],
            era="2020s",
            genre="pop",
            energy_level="high",
            descriptors=["digital", "clean", "modern"]
        )
        
        # Similar vibes should score high
        score1 = agent.calculate_compatibility(vibe1, vibe2)
        assert score1 > 0.6  # Adjusted threshold
        
        # Different vibes should score low
        score2 = agent.calculate_compatibility(vibe1, vibe3)
        assert score2 < 0.3
    
    @pytest.mark.asyncio
    async def test_find_complementary_samples(self, agent):
        """Test finding samples that work well together."""
        samples = [
            SampleVibe(
                filename="dark_pad.wav",
                bpm=85,
                key="Am",
                vibe=VibeDescriptor(
                    mood=["dark", "atmospheric"],
                    era="modern",
                    genre="ambient",
                    energy_level="low",
                    descriptors=["spacious", "ethereal"]
                ),
                compatibility_tags=["night", "chill"],
                best_use="pad"
            ),
            SampleVibe(
                filename="dark_drums.wav",
                bpm=85,
                key="Am",
                vibe=VibeDescriptor(
                    mood=["dark", "driving"],
                    era="modern",
                    genre="trip-hop",
                    energy_level="medium",
                    descriptors=["punchy", "groove"]
                ),
                compatibility_tags=["night", "urban"],
                best_use="drums"
            ),
            SampleVibe(
                filename="happy_melody.wav",
                bpm=120,
                key="C",
                vibe=VibeDescriptor(
                    mood=["happy", "uplifting"],
                    era="modern",
                    genre="pop",
                    energy_level="high",
                    descriptors=["bright", "cheerful"]
                ),
                compatibility_tags=["day", "positive"],
                best_use="melody"
            )
        ]
        
        # Find samples that complement the dark pad
        complementary = await agent.find_complementary(samples[0], samples)
        
        assert len(complementary) >= 1
        assert samples[1] in complementary  # Dark drums should complement
        assert samples[2] not in complementary  # Happy melody should not
    
    def test_error_handling(self, agent):
        """Test error handling for invalid inputs."""
        # Test with missing required fields
        with pytest.raises(ValueError):
            agent.parse_vibe_response("{}", "", 0, "")
        
        # Test with invalid JSON
        with pytest.raises(Exception):
            agent.parse_vibe_response("not json", "test.wav", 120, "C")
    
    @pytest.mark.asyncio
    async def test_cache_integration(self, agent):
        """Test that analysis results are cached."""
        sample = {"filename": "cached.wav", "bpm": 100, "key": "D"}
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': '{"mood": ["test"], "era": "test", "genre": "test", "energy_level": "medium", "descriptors": ["test"]}'
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            # First call should hit API
            result1 = await agent.analyze_vibe(sample)
            assert mock_post.call_count == 1
            
            # Second call should use cache
            result2 = await agent.analyze_vibe(sample)
            assert mock_post.call_count == 1  # No additional call
            
            # Results should be identical
            assert result1.filename == result2.filename
            assert result1.vibe.mood == result2.vibe.mood