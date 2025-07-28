"""
Simplified unit tests for Groove Analyst Agent that match actual implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.agents.groove_analyst import (
    GrooveAnalystAgent,
    GrooveAnalysisResult,
    TimingAnalysis,
    GrooveCharacteristics,
    analyze_groove
)
from src.agents.base import AgentStatus


class TestGrooveAnalystAgentSimple:
    """Simplified test suite for Groove Analyst Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a Groove Analyst Agent instance."""
        return GrooveAnalystAgent()
    
    @pytest.fixture
    def mock_audio_analysis(self):
        """Mock audio analysis results."""
        return {
            "bpm": 90.0,
            "bpm_confidence": 0.95,
            "onset_times": [0.0, 0.667, 1.333, 2.0],
            "beat_times": [0.0, 0.667, 1.333, 2.0],
            "tempo": 90.0
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "groove_analyst"
        assert hasattr(agent, "groove_references")
        assert isinstance(agent.groove_references, dict)
    
    @pytest.mark.asyncio
    async def test_execute_with_mocked_analysis(self, agent, mock_audio_analysis):
        """Test execute with mocked audio analysis."""
        with patch('src.tools.audio.load_audio', return_value=(Mock(), 44100)):
            with patch('src.tools.audio.detect_bpm', return_value=90.0):
                with patch('librosa.beat.beat_track', return_value=(90.0, [0.0, 0.667, 1.333, 2.0])):
                    with patch('librosa.onset.onset_detect', return_value=[0.0, 0.667, 1.333, 2.0]):
                        
                        result = await agent.execute(
                            task_id="test_001",
                            file_paths=["test.wav"]
                        )
                        
                        assert result.status == AgentStatus.SUCCESS
                        assert result.agent_name == "groove_analyst"
                        assert "analyses" in result.result
    
    @pytest.mark.asyncio
    async def test_empty_file_list(self, agent):
        """Test handling empty file list."""
        result = await agent.execute(
            task_id="test_002",
            file_paths=[]
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert result.result["analyses"] == []
    
    @pytest.mark.asyncio
    async def test_nonexistent_file(self, agent):
        """Test handling nonexistent files."""
        result = await agent.execute(
            task_id="test_003",
            file_paths=["nonexistent.wav"]
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert len(result.result["analyses"]) == 0


class TestGrooveCharacteristics:
    """Test GrooveCharacteristics model."""
    
    def test_model_creation(self):
        """Test creating GrooveCharacteristics."""
        groove = GrooveCharacteristics(
            swing_percentage=65.0,
            humanization=0.8,
            complexity=0.7,
            pocket_depth=0.9,
            groove_consistency=0.85,
            dominant_pattern="boom_bap"
        )
        
        assert groove.swing_percentage == 65.0
        assert groove.dominant_pattern == "boom_bap"


class TestTimingAnalysis:
    """Test TimingAnalysis model."""
    
    def test_model_creation(self):
        """Test creating TimingAnalysis."""
        timing = TimingAnalysis(
            feel="behind",
            micro_timing_std=0.015,
            swing_ratio=1.67,
            human_vs_machine=0.8,
            timing_consistency=0.9,
            subdivision_feel="16th"
        )
        
        assert timing.feel == "behind"
        assert timing.swing_ratio == 1.67


@pytest.mark.asyncio
async def test_analyze_groove_convenience():
    """Test analyze_groove convenience function."""
    with patch('src.agents.groove_analyst.GrooveAnalystAgent') as MockAgent:
        mock_instance = MockAgent.return_value
        mock_instance.execute = AsyncMock(
            return_value=Mock(
                result={"analyses": [{"bpm": 90.0}]}
            )
        )
        
        result = await analyze_groove(file_paths=["test.wav"])
        
        assert "analyses" in result
        assert result["analyses"][0]["bpm"] == 90.0