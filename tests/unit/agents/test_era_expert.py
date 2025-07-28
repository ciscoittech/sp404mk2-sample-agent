"""
Unit tests for Era Expert Agent.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.agents.era_expert import (
    EraExpertAgent,
    EraAnalysisResult,
    analyze_era,
    get_era_search_queries
)
from src.agents.base import AgentStatus
from tests.mocks.audio import MockFrequencyData


class TestEraExpertAgent:
    """Test suite for Era Expert Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create an Era Expert Agent instance."""
        return EraExpertAgent()
    
    @pytest.fixture
    def mock_frequency_1970s(self):
        """Mock frequency data for 1970s sound."""
        return {
            "spectral_centroid": 2200.0,
            "spectral_bandwidth": 2500.0,
            "spectral_rolloff": 4500.0
        }
    
    @pytest.fixture
    def mock_frequency_1990s(self):
        """Mock frequency data for 1990s sound."""
        return {
            "spectral_centroid": 2800.0,
            "spectral_bandwidth": 2000.0,
            "spectral_rolloff": 3500.0  # Filtered highs
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes with correct properties."""
        assert agent.name == "era_expert"
        assert hasattr(agent, "era_database")
        assert "1970s" in agent.era_database
        assert "1990s" in agent.era_database
        assert hasattr(agent, "genre_knowledge")
    
    @pytest.mark.asyncio
    async def test_era_detection_from_audio(self, agent, mock_audio_files):
        """Test era detection from audio file."""
        test_file = mock_audio_files["jazz_drums_93bpm.wav"]["path"]
        
        result = await agent.execute(
            task_id="test_era_001",
            file_paths=[test_file]
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert "analyses" in result.result
        
        analysis = result.result["analyses"][0]
        assert "detected_era" in analysis
        assert "confidence" in analysis
        assert 0 <= analysis["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_era_information_retrieval(self, agent):
        """Test getting information about a specific era."""
        result = await agent.execute(
            task_id="test_era_002",
            target_era="1970s",
            genre="funk"
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert len(result.result["analyses"]) == 1
        
        era_info = result.result["analyses"][0]
        assert era_info["era"] == "1970s"
        assert "equipment" in era_info
        assert "techniques" in era_info
        assert "characteristics" in era_info
        assert "search_terms" in era_info
    
    @pytest.mark.asyncio
    async def test_search_query_enhancement(self, agent):
        """Test search query enhancement for era."""
        result = await agent.execute(
            task_id="test_era_003",
            target_era="1990s",
            genre="hip-hop",
            base_query="drum breaks",
            enhance_search=True
        )
        
        assert result.status == AgentStatus.SUCCESS
        era_info = result.result["analyses"][0]
        assert "enhanced_searches" in era_info
        
        # Should include era-specific terms
        searches = era_info["enhanced_searches"]
        assert any("MPC" in q for q in searches)
        assert any("boom bap" in q for q in searches)
        assert any("1990" in q for q in searches)
    
    def test_era_detection_logic(self, agent):
        """Test era detection based on frequency characteristics."""
        # Test 1970s detection
        era, confidence = agent._detect_era_from_audio({
            "spectral_centroid": 2200.0,
            "spectral_rolloff": 4500.0
        })
        assert era == "1970s"
        assert confidence >= 0.7
        
        # Test 1990s detection
        era, confidence = agent._detect_era_from_audio({
            "spectral_centroid": 2800.0,
            "spectral_rolloff": 3500.0
        })
        assert era == "1990s"
        assert confidence >= 0.6
        
        # Test 1980s detection (bright)
        era, confidence = agent._detect_era_from_audio({
            "spectral_centroid": 3500.0,
            "spectral_rolloff": 8000.0
        })
        assert era == "1980s"
        assert confidence >= 0.7
    
    def test_equipment_formatting(self, agent):
        """Test equipment information formatting."""
        equipment_data = {
            "consoles": ["Neve 8078", "SSL 4000"],
            "synths": ["Minimoog", "Rhodes"],
            "drums": ["Linn LM-1"]
        }
        
        formatted = agent._format_equipment(equipment_data)
        
        assert isinstance(formatted, list)
        assert all("category" in item for item in formatted)
        assert all("models" in item for item in formatted)
        assert all("significance" in item for item in formatted)
    
    def test_genre_context_matching(self, agent):
        """Test genre-specific context retrieval."""
        # Test exact match
        context = agent._get_genre_context("hip_hop", "1990s")
        assert context is not None
        assert "producers" in context
        assert any("DJ Premier" in p for p in context["producers"])
        
        # Test normalized genre name
        context = agent._get_genre_context("hip-hop", "1990s")
        assert context is not None
        
        # Test mismatched era
        context = agent._get_genre_context("hip_hop", "1970s")
        assert context is None
    
    def test_modern_recreation_tips(self, agent):
        """Test modern recreation tips generation."""
        tips = agent._get_modern_recreation_tips("1970s")
        
        assert "plugins" in tips
        assert "techniques" in tips
        assert "tips" in tips
        assert any("Neve" in p for p in tips["plugins"])
        assert any("analog" in t.lower() for t in tips["techniques"])
        
        # Test unknown era
        tips = agent._get_modern_recreation_tips("2050s")
        assert tips == {}
    
    def test_production_notes_generation(self, agent):
        """Test production notes based on analysis."""
        # Test vintage notes
        notes = agent._generate_production_notes(
            "1970s",
            {"spectral_centroid": 1800.0}
        )
        assert "vintage" in notes.lower() or "analog" in notes.lower()
        
        # Test modern notes
        notes = agent._generate_production_notes(
            "2000s-2010s",
            {"spectral_centroid": 3500.0}
        )
        assert "modern" in notes.lower() or "digital" in notes.lower()
    
    @pytest.mark.asyncio
    async def test_summary_generation(self, agent, mock_audio_files):
        """Test summary generation for multiple analyses."""
        test_files = [
            mock_audio_files["drum_90bpm.wav"]["path"],
            mock_audio_files["jazz_drums_93bpm.wav"]["path"]
        ]
        
        result = await agent.execute(
            task_id="test_era_004",
            file_paths=test_files
        )
        
        summary = result.result.get("summary", {})
        assert "total_analyzed" in summary
        assert "detected_eras" in summary
        assert summary["total_analyzed"] == 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling for invalid files."""
        result = await agent.execute(
            task_id="test_era_005",
            file_paths=["nonexistent.wav"]
        )
        
        # Should handle gracefully
        assert result.status == AgentStatus.SUCCESS
        assert result.result["analyses"] == []


class TestEraSearchQueries:
    """Test search query generation."""
    
    def test_base_query_enhancement(self):
        """Test enhancing a base query with era terms."""
        agent = EraExpertAgent()
        
        queries = agent._generate_era_search_queries(
            era="1970s",
            genre="soul",
            base_query="bass lines"
        )
        
        assert len(queries) > 0
        assert any("bass lines 1970s" in q for q in queries)
        assert any("Fender" in q for q in queries)  # Era-specific equipment
        assert any("funk" in q.lower() for q in queries)  # Related genre
    
    def test_genre_specific_queries(self):
        """Test genre-specific query generation."""
        agent = EraExpertAgent()
        
        # Test hip-hop in 1990s
        queries = agent._generate_era_search_queries(
            era="1990s",
            genre="hip-hop",
            base_query=""
        )
        
        assert any("boom bap" in q for q in queries)
        assert any("MPC" in q for q in queries)
        assert any("golden era" in q for q in queries)
    
    def test_query_limit(self):
        """Test that queries are limited to reasonable number."""
        agent = EraExpertAgent()
        
        queries = agent._generate_era_search_queries(
            era="1970s",
            genre="jazz",
            base_query="drum solos"
        )
        
        assert len(queries) <= 10  # Should limit to 10 queries


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_analyze_era_function(self, mock_audio_files):
        """Test the analyze_era convenience function."""
        test_files = [mock_audio_files["drum_90bpm.wav"]["path"]]
        
        result = await analyze_era(
            file_paths=test_files,
            enhance_search=False
        )
        
        assert "analyses" in result
        assert len(result["analyses"]) == 1
        assert "detected_era" in result["analyses"][0]
    
    @pytest.mark.asyncio
    async def test_get_search_queries_function(self):
        """Test the get_era_search_queries convenience function."""
        queries = await get_era_search_queries(
            era="1980s",
            genre="electronic",
            base_query="synth bass"
        )
        
        assert isinstance(queries, list)
        assert len(queries) > 0
        assert any("DX7" in q for q in queries)  # 80s synth