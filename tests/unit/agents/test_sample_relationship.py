"""
Unit tests for Sample Relationship Agent.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.agents.sample_relationship import (
    SampleRelationshipAgent,
    HarmonicAnalysis,
    RhythmicAnalysis,
    FrequencyAnalysis,
    CompatibilityResult,
    analyze_sample_compatibility,
    check_harmonic_compatibility
)
from src.agents.base import AgentStatus


class TestSampleRelationshipAgent:
    """Test suite for Sample Relationship Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a Sample Relationship Agent instance."""
        return SampleRelationshipAgent()
    
    @pytest.fixture
    def mock_sample_properties(self):
        """Mock sample properties for testing."""
        return {
            "kick": {
                "file_path": "kick.wav",
                "bpm": 90.0,
                "bpm_confidence": 0.95,
                "key": "C major",
                "key_confidence": 0.9,
                "frequency": {
                    "spectral_centroid": 150.0,
                    "spectral_bandwidth": 200.0,
                    "spectral_rolloff": 500.0
                },
                "duration": 0.5,
                "energy": 0.8
            },
            "bass": {
                "file_path": "bass.wav",
                "bpm": 90.0,
                "bpm_confidence": 0.93,
                "key": "C major",
                "key_confidence": 0.88,
                "frequency": {
                    "spectral_centroid": 250.0,
                    "spectral_bandwidth": 300.0,
                    "spectral_rolloff": 1000.0
                },
                "duration": 2.0,
                "energy": 0.7
            },
            "melody": {
                "file_path": "melody.wav",
                "bpm": 90.0,
                "bpm_confidence": 0.9,
                "key": "G major",
                "key_confidence": 0.85,
                "frequency": {
                    "spectral_centroid": 1500.0,
                    "spectral_bandwidth": 1000.0,
                    "spectral_rolloff": 3000.0
                },
                "duration": 4.0,
                "energy": 0.6
            }
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes with correct properties."""
        assert agent.name == "sample_relationship"
        assert hasattr(agent, "key_relationships")
        assert hasattr(agent, "frequency_ranges")
        assert hasattr(agent, "genre_rules")
        
        # Check key relationships
        assert agent.key_relationships[0][0] == "Unison"
        assert agent.key_relationships[0][1] == 10.0
        assert agent.key_relationships[6][0] == "Tritone"
        assert agent.key_relationships[6][1] == 3.0
    
    @pytest.mark.asyncio
    async def test_compatibility_analysis_success(self, agent, mock_audio_files):
        """Test successful compatibility analysis between samples."""
        sample_pairs = [
            (mock_audio_files["drum_90bpm.wav"]["path"], 
             mock_audio_files["bass_120bpm.wav"]["path"])
        ]
        
        result = await agent.execute(
            task_id="test_rel_001",
            sample_pairs=sample_pairs,
            genre="hip-hop"
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert "analyses" in result.result
        assert len(result.result["analyses"]) == 1
        
        analysis = result.result["analyses"][0]
        assert "overall_score" in analysis
        assert 0 <= analysis["overall_score"] <= 10
        assert "harmonic" in analysis
        assert "rhythmic" in analysis
        assert "frequency" in analysis
    
    def test_harmonic_analysis(self, agent, mock_sample_properties):
        """Test harmonic compatibility analysis."""
        # Test unison (same key)
        harmonic = agent._analyze_harmonic_compatibility(
            mock_sample_properties["kick"],
            mock_sample_properties["bass"]
        )
        
        assert isinstance(harmonic, HarmonicAnalysis)
        assert harmonic.key_relationship == "Unison"
        assert harmonic.interval_semitones == 0
        assert harmonic.compatibility_score >= 9.0
        assert harmonic.suggestion is None
        
        # Test perfect 5th (C to G)
        harmonic = agent._analyze_harmonic_compatibility(
            mock_sample_properties["bass"],
            mock_sample_properties["melody"]
        )
        
        assert harmonic.key_relationship == "Perfect 5th"
        assert harmonic.interval_semitones == 7
        assert harmonic.compatibility_score >= 7.0
    
    def test_rhythmic_analysis(self, agent, mock_sample_properties):
        """Test rhythmic compatibility analysis."""
        # Test same BPM
        rhythmic = agent._analyze_rhythmic_compatibility(
            mock_sample_properties["kick"],
            mock_sample_properties["bass"]
        )
        
        assert isinstance(rhythmic, RhythmicAnalysis)
        assert rhythmic.bpm_compatibility == 100.0
        assert rhythmic.tempo_relationship == "Same tempo"
        assert rhythmic.groove_match == 10.0
        
        # Test different BPM (90 vs simulated 180)
        sample2 = mock_sample_properties["bass"].copy()
        sample2["bpm"] = 180.0
        
        rhythmic = agent._analyze_rhythmic_compatibility(
            mock_sample_properties["kick"],
            sample2
        )
        
        assert rhythmic.tempo_relationship == "Half/Double time"
        assert rhythmic.bpm_compatibility >= 90.0
    
    def test_frequency_analysis(self, agent, mock_sample_properties):
        """Test frequency compatibility analysis."""
        # Test kick vs bass (potential sub conflict)
        frequency = agent._analyze_frequency_compatibility(
            mock_sample_properties["kick"],
            mock_sample_properties["bass"]
        )
        
        assert isinstance(frequency, FrequencyAnalysis)
        assert frequency.masking_risk in ["low", "medium", "high"]
        assert isinstance(frequency.overlap_areas, list)
        assert isinstance(frequency.eq_suggestions, list)
        
        # Test bass vs melody (good separation)
        frequency = agent._analyze_frequency_compatibility(
            mock_sample_properties["bass"],
            mock_sample_properties["melody"]
        )
        
        assert frequency.masking_risk == "low"
        assert frequency.complementary_score >= 7.0
    
    def test_energy_compatibility(self, agent, mock_sample_properties):
        """Test energy level compatibility calculation."""
        # Similar energy (0.8 vs 0.7)
        energy_score = agent._calculate_energy_compatibility(
            mock_sample_properties["kick"],
            mock_sample_properties["bass"]
        )
        
        assert energy_score >= 7.0  # Should be compatible
        
        # Different energy (0.8 vs 0.6)
        energy_score = agent._calculate_energy_compatibility(
            mock_sample_properties["kick"],
            mock_sample_properties["melody"]
        )
        
        assert energy_score >= 5.0  # Moderate compatibility
    
    def test_recommendations_generation(self, agent):
        """Test recommendation generation based on analysis."""
        # High compatibility
        harmonic = HarmonicAnalysis(
            key_relationship="Perfect 5th",
            interval_semitones=7,
            compatibility_score=9.0,
            suggestion=None
        )
        
        rhythmic = RhythmicAnalysis(
            bpm_compatibility=95.0,
            tempo_relationship="Same tempo",
            groove_match=9.5,
            timing_alignment="matched"
        )
        
        frequency = FrequencyAnalysis(
            overlap_areas=["Good frequency separation"],
            masking_risk="low",
            complementary_score=8.5,
            eq_suggestions=[]
        )
        
        recommendations = agent._generate_recommendations(
            harmonic, rhythmic, frequency, 8.5, "hip-hop"
        )
        
        assert len(recommendations) > 0
        assert any("Excellent compatibility" in r for r in recommendations)
        assert any("808" in r for r in recommendations)  # Genre-specific
    
    def test_relationship_type_determination(self, agent):
        """Test relationship type classification."""
        # Test perfect match
        rel_type = agent._determine_relationship_type(
            HarmonicAnalysis("Unison", 0, 10.0, None),
            RhythmicAnalysis(100.0, "Same tempo", 10.0, "matched"),
            FrequencyAnalysis([], "low", 9.0, []),
            9.0
        )
        assert rel_type == "Perfect Match"
        
        # Test harmonic partners
        rel_type = agent._determine_relationship_type(
            HarmonicAnalysis("Perfect 5th", 7, 8.5, None),
            RhythmicAnalysis(80.0, "Close tempo", 6.0, "matched"),
            FrequencyAnalysis([], "medium", 6.0, []),
            7.0
        )
        assert rel_type == "Harmonic Partners"
    
    def test_arrangement_suggestions(self, agent, mock_sample_properties):
        """Test arrangement suggestions based on relationship."""
        arrangement = agent._suggest_arrangement(
            mock_sample_properties["kick"],
            mock_sample_properties["bass"],
            "Perfect Match",
            "hip-hop"
        )
        
        assert isinstance(arrangement, str)
        assert "layer" in arrangement.lower()
        assert "drums" in arrangement.lower()
    
    @pytest.mark.asyncio
    async def test_kit_suggestions(self, agent, mock_audio_files):
        """Test kit building suggestions for multiple samples."""
        sample_pairs = [
            (mock_audio_files["drum_90bpm.wav"]["path"],
             mock_audio_files["bass_120bpm.wav"]["path"]),
            (mock_audio_files["drum_90bpm.wav"]["path"],
             mock_audio_files["jazz_drums_93bpm.wav"]["path"])
        ]
        
        result = await agent.execute(
            task_id="test_rel_002",
            sample_pairs=sample_pairs
        )
        
        assert result.status == AgentStatus.SUCCESS
        assert "kit_suggestions" in result.result
        
        kit = result.result["kit_suggestions"]
        assert "best_combination" in kit
        assert "compatibility_groups" in kit
        assert "kit_recommendation" in kit
    
    def test_key_extraction(self, agent):
        """Test root note extraction from key strings."""
        assert agent._extract_root_note("C major") == 0
        assert agent._extract_root_note("G major") == 7
        assert agent._extract_root_note("F# minor") == 6
        assert agent._extract_root_note("Unknown") == 0  # Default
    
    def test_frequency_overlap_detection(self, agent):
        """Test frequency overlap detection."""
        freq1 = {"spectral_centroid": 1500.0}
        freq2 = {"spectral_centroid": 1600.0}
        
        # Should detect overlap in mid range
        overlap = agent._check_frequency_overlap(
            freq1, freq2, 500, 2000  # Mid range
        )
        assert overlap is True
        
        # Should not detect overlap in sub range
        overlap = agent._check_frequency_overlap(
            freq1, freq2, 20, 60  # Sub range
        )
        assert overlap is False
    
    def test_eq_suggestions(self, agent):
        """Test EQ suggestion generation."""
        overlap_areas = ["Heavy mid-range overlap", "sub_bass overlap"]
        
        suggestions = agent._generate_eq_suggestions(
            {"spectral_centroid": 1500.0},
            {"spectral_centroid": 1600.0},
            overlap_areas
        )
        
        assert len(suggestions) > 0
        assert any("500-2kHz" in s for s in suggestions)
        assert any("100Hz" in s for s in suggestions)


class TestCompatibilityModels:
    """Test Pydantic models for compatibility analysis."""
    
    def test_harmonic_analysis_model(self):
        """Test HarmonicAnalysis model validation."""
        analysis = HarmonicAnalysis(
            key_relationship="Perfect 5th",
            interval_semitones=7,
            compatibility_score=8.5,
            suggestion="Transpose up 2 semitones"
        )
        
        assert analysis.key_relationship == "Perfect 5th"
        assert 0 <= analysis.compatibility_score <= 10
    
    def test_rhythmic_analysis_model(self):
        """Test RhythmicAnalysis model validation."""
        analysis = RhythmicAnalysis(
            bpm_compatibility=85.5,
            tempo_relationship="Close tempo",
            groove_match=7.5,
            timing_alignment="matched"
        )
        
        assert 0 <= analysis.bpm_compatibility <= 100
        assert 0 <= analysis.groove_match <= 10
    
    def test_frequency_analysis_model(self):
        """Test FrequencyAnalysis model validation."""
        analysis = FrequencyAnalysis(
            overlap_areas=["mid range", "high mid"],
            masking_risk="medium",
            complementary_score=6.5,
            eq_suggestions=["Cut 2kHz on sample 1"]
        )
        
        assert analysis.masking_risk in ["low", "medium", "high"]
        assert 0 <= analysis.complementary_score <= 10


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_analyze_compatibility_function(self, mock_audio_files):
        """Test the analyze_sample_compatibility convenience function."""
        sample_pairs = [(
            mock_audio_files["drum_90bpm.wav"]["path"],
            mock_audio_files["bass_120bpm.wav"]["path"]
        )]
        
        result = await analyze_sample_compatibility(
            sample_pairs=sample_pairs,
            genre="electronic"
        )
        
        assert "analyses" in result
        assert len(result["analyses"]) == 1
        assert "overall_score" in result["analyses"][0]
    
    @pytest.mark.asyncio
    async def test_check_harmonic_function(self, mock_audio_files):
        """Test the check_harmonic_compatibility convenience function."""
        result = await check_harmonic_compatibility(
            mock_audio_files["drum_90bpm.wav"]["path"],
            mock_audio_files["bass_120bpm.wav"]["path"]
        )
        
        assert "analyses" in result
        assert result["analyses"][0]["harmonic"] is not None