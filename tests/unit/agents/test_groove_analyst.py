"""
Unit tests for Groove Analyst Agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.agents.groove_analyst import (
    GrooveAnalystAgent,
    GrooveAnalysisResult,
    TimingAnalysis,
    analyze_groove
)
from src.agents.base import AgentStatus


class TestGrooveAnalystAgent:
    """Test suite for Groove Analyst Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a Groove Analyst Agent instance."""
        return GrooveAnalystAgent()
    
    @pytest.fixture
    def mock_bpm_result(self):
        """Mock BPM detection result."""
        return {"bpm": 93.5, "confidence": 0.92}
    
    @pytest.fixture
    def mock_onset_times(self):
        """Mock onset detection times."""
        # Simulate swing pattern onsets
        return [0.0, 0.4, 0.65, 1.05, 1.3, 1.7, 1.95, 2.35]
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes with correct properties."""
        assert agent.name == "groove_analyst"
        assert hasattr(agent, "groove_references")
        assert "dilla" in agent.groove_references
        assert "questlove" in agent.groove_references
    
    @pytest.mark.asyncio
    async def test_execute_single_file(self, agent, mock_audio_files):
        """Test analyzing a single audio file."""
        test_file = mock_audio_files["jazz_drums_93bpm.wav"]["path"]
        
        result = await agent.execute(
            task_id="test_001",
            file_paths=[test_file]
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert result.agent_name == "groove_analyst"
        assert "analyses" in result.result
        assert len(result.result["analyses"]) == 1
        
        analysis = result.result["analyses"][0]
        assert analysis["file_path"] == test_file
        assert analysis["bpm"] == 93.0
        assert "swing_percentage" in analysis
        assert "groove_type" in analysis
    
    @pytest.mark.asyncio
    async def test_execute_multiple_files(self, agent, mock_audio_files):
        """Test analyzing multiple audio files."""
        test_files = [
            mock_audio_files["drum_90bpm.wav"]["path"],
            mock_audio_files["jazz_drums_93bpm.wav"]["path"]
        ]
        
        result = await agent.execute(
            task_id="test_002",
            file_paths=test_files,
            analysis_depth="quick"
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert len(result.result["analyses"]) == 2
        
        # Check summary
        summary = result.result.get("summary", {})
        assert "files_analyzed" in summary
        assert summary["files_analyzed"] == 2
    
    @pytest.mark.asyncio
    async def test_swing_detection(self, agent):
        """Test swing percentage calculation."""
        # Test straight timing (50% swing)
        straight_onsets = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
        swing_pct = agent._calculate_swing_percentage(straight_onsets)
        assert 48 <= swing_pct <= 52  # Allow small margin
        
        # Test triplet swing (67% swing)
        triplet_onsets = [0.0, 0.67, 1.0, 1.67, 2.0, 2.67]
        swing_pct = agent._calculate_swing_percentage(triplet_onsets)
        assert 65 <= swing_pct <= 69
    
    @pytest.mark.asyncio
    async def test_groove_type_classification(self, agent):
        """Test groove type classification."""
        # Test boom bap classification
        groove_type = agent._classify_groove_type(90.0, 65.5, "behind")
        assert groove_type == "boom_bap"
        
        # Test trap classification
        groove_type = agent._classify_groove_type(140.0, 51.0, "on")
        assert groove_type == "trap"
        
        # Test swing classification
        groove_type = agent._classify_groove_type(120.0, 68.0, "behind")
        assert groove_type == "swing"
    
    @pytest.mark.asyncio
    async def test_artist_similarity(self, agent):
        """Test artist similarity matching."""
        # Test Dilla-like characteristics
        similarities = agent._calculate_artist_similarity(
            swing_percentage=65.0,
            timing_feel="behind",
            micro_timing={"kick": 0.015, "snare": -0.01}
        )
        
        assert "dilla" in similarities
        assert similarities["dilla"] > 0.7  # High similarity
        
        # Test Metro Boomin-like characteristics
        similarities = agent._calculate_artist_similarity(
            swing_percentage=51.0,
            timing_feel="on",
            micro_timing={"kick": 0.001, "snare": 0.0}
        )
        
        assert "metro_boomin" in similarities
        assert similarities["metro_boomin"] > 0.7
    
    @pytest.mark.asyncio
    async def test_production_tips_generation(self, agent):
        """Test production tips generation."""
        tips = agent._generate_production_tips(
            groove_type="boom_bap",
            swing_percentage=66.0,
            closest_references=["dilla", "pete_rock"]
        )
        
        assert isinstance(tips, list)
        assert len(tips) > 0
        assert any("swing" in tip.lower() for tip in tips)
        assert any("groove" in tip.lower() for tip in tips)
    
    @pytest.mark.asyncio
    async def test_deep_analysis(self, agent, mock_audio_files):
        """Test deep analysis mode."""
        test_file = mock_audio_files["drum_90bpm.wav"]["path"]
        
        result = await agent.execute(
            task_id="test_003",
            file_paths=[test_file],
            analysis_depth="deep"
        )
        
        assert result.status == AgentStatus.SUCCESS
        analysis = result.result["analyses"][0]
        
        # Deep analysis should include more details
        assert "micro_timing_std" in analysis
        assert "groove_consistency" in analysis
        assert "complexity_rating" in analysis
    
    @pytest.mark.asyncio
    async def test_reference_artists_filter(self, agent, mock_audio_files):
        """Test filtering by reference artists."""
        test_file = mock_audio_files["drum_90bpm.wav"]["path"]
        
        result = await agent.execute(
            task_id="test_004",
            file_paths=[test_file],
            reference_artists=["dilla", "questlove"]
        )
        
        assert result.status == AgentStatus.SUCCESS
        analysis = result.result["analyses"][0]
        
        # Should only include specified artists
        refs = analysis["closest_references"]
        assert all(ref["artist"] in ["dilla", "questlove"] for ref in refs)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling for invalid files."""
        result = await agent.execute(
            task_id="test_005",
            file_paths=["nonexistent.wav"]
        )
        
        # Should handle gracefully
        assert result.status == AgentStatus.SUCCESS
        assert len(result.result["analyses"]) == 0
    
    @pytest.mark.asyncio
    async def test_summary_generation(self, agent, mock_audio_files):
        """Test summary generation for multiple files."""
        test_files = [
            mock_audio_files["drum_90bpm.wav"]["path"],
            mock_audio_files["jazz_drums_93bpm.wav"]["path"]
        ]
        
        result = await agent.execute(
            task_id="test_006",
            file_paths=test_files
        )
        
        summary = result.result["summary"]
        assert "average_swing" in summary
        assert "dominant_groove" in summary
        assert "bpm_range" in summary
        assert summary["files_analyzed"] == 2


class TestGrooveAnalysisModel:
    """Test Groove Analysis Pydantic model."""
    
    def test_model_validation(self):
        """Test model validates correctly."""
        analysis = GrooveAnalysisResult(
            file_path="test.wav",
            bpm=120.0,
            bpm_confidence=0.95,
            swing_percentage=55.5,
            groove_type="straight",
            timing_feel="on",
            micro_timing={"kick": 0.0, "snare": 0.001},
            humanization_score=0.8,
            complexity_rating="medium",
            closest_references=[{"artist": "metro_boomin", "similarity": 0.85}],
            production_tips=["Keep it simple"]
        )
        
        assert analysis.bpm == 120.0
        assert 0 <= analysis.swing_percentage <= 100
        assert analysis.groove_type in ["straight", "swing", "shuffle", "boom_bap", "trap", "samba", "afrobeat"]


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_analyze_groove_function(self, mock_audio_files):
        """Test the analyze_groove convenience function."""
        test_files = [mock_audio_files["drum_90bpm.wav"]["path"]]
        
        result = await analyze_groove(
            file_paths=test_files,
            analysis_depth="standard"
        )
        
        assert "analyses" in result
        assert len(result["analyses"]) == 1
        assert result["analyses"][0]["bpm"] == 90.0
    
