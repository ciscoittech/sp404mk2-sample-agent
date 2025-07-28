"""
Sample Relationship Agent - Musical compatibility and relationship analysis.
Analyzes how samples work together harmonically, rhythmically, and spectrally.
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ..logging_config import AgentLogger
from ..tools import database
from ..tools.audio import detect_bpm, detect_key, analyze_frequency_content, get_duration
from .base import Agent, AgentResult, AgentStatus


# Pydantic models for compatibility analysis
class HarmonicAnalysis(BaseModel):
    """Harmonic compatibility analysis."""
    key_relationship: str = Field(description="Interval relationship between keys")
    interval_semitones: int = Field(description="Semitone distance")
    compatibility_score: float = Field(ge=0.0, le=10.0)
    suggestion: Optional[str] = Field(description="Transposition suggestion")


class RhythmicAnalysis(BaseModel):
    """Rhythmic compatibility analysis."""
    bpm_compatibility: float = Field(ge=0.0, le=100.0, description="BPM match percentage")
    tempo_relationship: str = Field(description="Same/half/double/polyrhythmic")
    groove_match: float = Field(ge=0.0, le=10.0)
    timing_alignment: str = Field(description="ahead/behind/matched")


class FrequencyAnalysis(BaseModel):
    """Frequency/spectral compatibility analysis."""
    overlap_areas: List[str] = Field(description="Frequency ranges with overlap")
    masking_risk: str = Field(description="low/medium/high")
    complementary_score: float = Field(ge=0.0, le=10.0)
    eq_suggestions: List[str] = Field(description="EQ adjustment suggestions")


class CompatibilityResult(BaseModel):
    """Complete compatibility analysis result."""
    sample1_path: str
    sample2_path: str
    overall_score: float = Field(ge=0.0, le=10.0)
    harmonic: HarmonicAnalysis
    rhythmic: RhythmicAnalysis
    frequency: FrequencyAnalysis
    energy_compatibility: float = Field(ge=0.0, le=10.0)
    recommendations: List[str]
    best_arrangement: str
    relationship_type: str


class SampleRelationshipAgent(Agent):
    """Agent specialized in analyzing musical relationships between samples."""
    
    def __init__(self):
        """Initialize the Sample Relationship Agent."""
        super().__init__("sample_relationship")
        self.logger = AgentLogger(self.name)
        
        # Key relationship scoring matrix (in semitones)
        self.key_relationships = {
            0: ("Unison", 10.0),          # Same key
            12: ("Octave", 10.0),         # Octave
            7: ("Perfect 5th", 9.0),      # Perfect 5th
            5: ("Perfect 4th", 8.5),      # Perfect 4th
            9: ("Major 6th", 7.0),        # Relative minor
            3: ("Minor 3rd", 7.0),        # Minor 3rd
            4: ("Major 3rd", 6.5),        # Major 3rd
            8: ("Minor 6th", 6.0),        # Minor 6th
            2: ("Major 2nd", 5.0),        # Major 2nd
            10: ("Minor 7th", 4.5),       # Minor 7th
            11: ("Major 7th", 4.0),       # Major 7th
            1: ("Minor 2nd", 2.0),        # Minor 2nd
            6: ("Tritone", 3.0)           # Tritone
        }
        
        # Frequency ranges for analysis
        self.frequency_ranges = {
            "sub_bass": (20, 60),
            "bass": (60, 250),
            "low_mid": (250, 500),
            "mid": (500, 2000),
            "high_mid": (2000, 4000),
            "high": (4000, 20000)
        }
        
        # Genre-specific rules
        self.genre_rules = {
            "hip-hop": {
                "kick_808_tune": True,
                "sample_drum_swing": True,
                "vocal_space": (1000, 3000)
            },
            "jazz": {
                "walking_bass_comp": True,
                "horn_key_alternate": True,
                "drum_dynamics_lead": True
            },
            "electronic": {
                "single_sub_element": True,
                "synth_filter_separation": True,
                "stereo_percussion": True
            }
        }
    
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Analyze compatibility between samples.
        
        Args:
            task_id: Unique task identifier
            sample_pairs: List of (sample1_path, sample2_path) tuples
            analysis_depth: 'quick', 'standard', or 'deep'
            genre: Musical genre for context-specific rules
            check_type: 'harmonic', 'rhythmic', 'frequency', or 'all'
            
        Returns:
            AgentResult with compatibility analyses
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting sample relationship analysis")
        started_at = datetime.now(timezone.utc)
        
        try:
            sample_pairs = kwargs.get("sample_pairs", [])
            if not sample_pairs:
                raise ValueError("No sample pairs provided for analysis")
            
            analysis_depth = kwargs.get("analysis_depth", "standard")
            genre = kwargs.get("genre", "general")
            check_type = kwargs.get("check_type", "all")
            
            # Analyze each pair
            analyses = []
            for sample1_path, sample2_path in sample_pairs:
                if not os.path.exists(sample1_path) or not os.path.exists(sample2_path):
                    self.logger.warning(f"Sample files not found: {sample1_path} or {sample2_path}")
                    continue
                
                analysis = await self._analyze_compatibility(
                    sample1_path, sample2_path, analysis_depth, genre, check_type
                )
                analyses.append(analysis)
            
            # Generate kit suggestions if multiple samples
            kit_suggestions = None
            if len(sample_pairs) > 1:
                kit_suggestions = self._suggest_kit_arrangement(analyses)
            
            # Log results (skip if database not configured)
            try:
                await database.add_agent_log({
                    "task_id": task_id,
                    "agent_type": self.name,
                    "log_level": "info",
                    "message": f"Analyzed {len(analyses)} sample pairs",
                    "context": {
                        "pairs_analyzed": len(analyses),
                        "analysis_depth": analysis_depth,
                        "genre": genre
                    }
                })
            except Exception:
                pass  # Skip logging if database not available
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result={
                    "analyses": analyses,
                    "kit_suggestions": kit_suggestions,
                    "summary": self._generate_summary(analyses)
                },
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.exception(f"Relationship analysis failed: {str(e)}")
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _analyze_compatibility(
        self,
        sample1_path: str,
        sample2_path: str,
        depth: str,
        genre: str,
        check_type: str
    ) -> Dict[str, Any]:
        """Analyze compatibility between two samples."""
        # Get basic properties for both samples
        sample1_props = await self._get_sample_properties(sample1_path)
        sample2_props = await self._get_sample_properties(sample2_path)
        
        # Perform compatibility checks
        harmonic = None
        rhythmic = None
        frequency = None
        
        if check_type in ["all", "harmonic"]:
            harmonic = self._analyze_harmonic_compatibility(sample1_props, sample2_props)
        
        if check_type in ["all", "rhythmic"]:
            rhythmic = self._analyze_rhythmic_compatibility(sample1_props, sample2_props)
        
        if check_type in ["all", "frequency"]:
            frequency = self._analyze_frequency_compatibility(sample1_props, sample2_props)
        
        # Calculate energy compatibility
        energy_score = self._calculate_energy_compatibility(sample1_props, sample2_props)
        
        # Calculate overall score
        scores = []
        if harmonic:
            scores.append(harmonic.compatibility_score * 0.4)
        if rhythmic:
            scores.append(rhythmic.groove_match * 0.3)
        if frequency:
            scores.append(frequency.complementary_score * 0.2)
        scores.append(energy_score * 0.1)
        
        overall_score = sum(scores) / (len(scores) / 10)  # Normalize to 0-10
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            harmonic, rhythmic, frequency, overall_score, genre
        )
        
        # Determine relationship type
        relationship_type = self._determine_relationship_type(
            harmonic, rhythmic, frequency, overall_score
        )
        
        # Generate arrangement suggestion
        best_arrangement = self._suggest_arrangement(
            sample1_props, sample2_props, relationship_type, genre
        )
        
        return {
            "sample1_path": sample1_path,
            "sample2_path": sample2_path,
            "sample1_name": os.path.basename(sample1_path),
            "sample2_name": os.path.basename(sample2_path),
            "overall_score": round(overall_score, 1),
            "harmonic": harmonic.dict() if harmonic else None,
            "rhythmic": rhythmic.dict() if rhythmic else None,
            "frequency": frequency.dict() if frequency else None,
            "energy_compatibility": round(energy_score, 1),
            "recommendations": recommendations,
            "best_arrangement": best_arrangement,
            "relationship_type": relationship_type
        }
    
    async def _get_sample_properties(self, file_path: str) -> Dict[str, Any]:
        """Get all relevant properties of a sample."""
        # Get audio analysis
        bpm_result = detect_bpm(file_path)
        key_result = detect_key(file_path)
        frequency_analysis = analyze_frequency_content(file_path)
        duration = get_duration(file_path)
        
        return {
            "file_path": file_path,
            "bpm": bpm_result["bpm"],
            "bpm_confidence": bpm_result["confidence"],
            "key": key_result["key"],
            "key_confidence": key_result["confidence"],
            "frequency": frequency_analysis,
            "duration": duration,
            "energy": self._estimate_energy(frequency_analysis)
        }
    
    def _analyze_harmonic_compatibility(
        self,
        sample1: Dict[str, Any],
        sample2: Dict[str, Any]
    ) -> HarmonicAnalysis:
        """Analyze harmonic compatibility between samples."""
        key1 = sample1["key"]
        key2 = sample2["key"]
        
        # Extract root notes (simplified - in production, use proper key parsing)
        root1 = self._extract_root_note(key1)
        root2 = self._extract_root_note(key2)
        
        # Calculate semitone distance
        semitone_distance = abs(root2 - root1) % 12
        
        # Get relationship and score
        relationship, score = self.key_relationships.get(
            semitone_distance,
            ("Unknown", 5.0)
        )
        
        # Adjust score based on confidence
        confidence_factor = (sample1["key_confidence"] + sample2["key_confidence"]) / 2
        adjusted_score = score * confidence_factor
        
        # Generate suggestion
        suggestion = None
        if adjusted_score < 6.0:
            if semitone_distance <= 6:
                suggestion = f"Transpose sample 2 up {semitone_distance} semitones"
            else:
                suggestion = f"Transpose sample 2 down {12 - semitone_distance} semitones"
        
        return HarmonicAnalysis(
            key_relationship=relationship,
            interval_semitones=semitone_distance,
            compatibility_score=adjusted_score,
            suggestion=suggestion
        )
    
    def _analyze_rhythmic_compatibility(
        self,
        sample1: Dict[str, Any],
        sample2: Dict[str, Any]
    ) -> RhythmicAnalysis:
        """Analyze rhythmic compatibility between samples."""
        bpm1 = sample1["bpm"]
        bpm2 = sample2["bpm"]
        
        # Check for exact match
        if abs(bpm1 - bpm2) < 0.5:
            bpm_compatibility = 100.0
            tempo_relationship = "Same tempo"
            groove_match = 10.0
        # Check for half/double time
        elif abs(bpm1 - bpm2 * 2) < 1 or abs(bpm1 * 2 - bpm2) < 1:
            bpm_compatibility = 90.0
            tempo_relationship = "Half/Double time"
            groove_match = 9.0
        # Check if within 5 BPM
        elif abs(bpm1 - bpm2) <= 5:
            bpm_compatibility = 80.0 - abs(bpm1 - bpm2) * 2
            tempo_relationship = "Close tempo"
            groove_match = 8.0 - abs(bpm1 - bpm2) * 0.4
        else:
            # Calculate compatibility for different tempos
            tempo_diff = abs(bpm1 - bpm2)
            bpm_compatibility = max(0, 100 - tempo_diff)
            tempo_relationship = "Different tempo"
            groove_match = max(0, 10 - tempo_diff / 10)
        
        # Mock timing alignment (in production, analyze actual timing)
        timing_alignment = "matched"  # Simplified
        
        return RhythmicAnalysis(
            bpm_compatibility=bpm_compatibility,
            tempo_relationship=tempo_relationship,
            groove_match=groove_match,
            timing_alignment=timing_alignment
        )
    
    def _analyze_frequency_compatibility(
        self,
        sample1: Dict[str, Any],
        sample2: Dict[str, Any]
    ) -> FrequencyAnalysis:
        """Analyze frequency/spectral compatibility."""
        freq1 = sample1["frequency"]
        freq2 = sample2["frequency"]
        
        # Identify overlap areas
        overlap_areas = []
        masking_score = 0
        
        # Compare spectral centroids
        centroid_diff = abs(freq1["spectral_centroid"] - freq2["spectral_centroid"])
        
        if centroid_diff < 500:
            overlap_areas.append("Heavy mid-range overlap")
            masking_score += 3
        elif centroid_diff < 1000:
            overlap_areas.append("Moderate frequency overlap")
            masking_score += 2
        else:
            overlap_areas.append("Good frequency separation")
            masking_score += 1
        
        # Check specific ranges
        for range_name, (low, high) in self.frequency_ranges.items():
            if self._check_frequency_overlap(freq1, freq2, low, high):
                overlap_areas.append(f"{range_name} overlap")
        
        # Determine masking risk
        if masking_score >= 3:
            masking_risk = "high"
        elif masking_score >= 2:
            masking_risk = "medium"
        else:
            masking_risk = "low"
        
        # Calculate complementary score
        complementary_score = 10.0 - (masking_score * 2.5)
        complementary_score = max(0, min(10, complementary_score))
        
        # Generate EQ suggestions
        eq_suggestions = self._generate_eq_suggestions(freq1, freq2, overlap_areas)
        
        return FrequencyAnalysis(
            overlap_areas=overlap_areas,
            masking_risk=masking_risk,
            complementary_score=complementary_score,
            eq_suggestions=eq_suggestions
        )
    
    def _calculate_energy_compatibility(
        self,
        sample1: Dict[str, Any],
        sample2: Dict[str, Any]
    ) -> float:
        """Calculate energy/dynamic compatibility."""
        energy1 = sample1["energy"]
        energy2 = sample2["energy"]
        
        # Similar energy levels are generally compatible
        energy_diff = abs(energy1 - energy2)
        
        if energy_diff < 0.2:
            return 9.0  # Very similar energy
        elif energy_diff < 0.5:
            return 7.0  # Compatible energy
        elif energy_diff < 1.0:
            return 5.0  # Contrasting but usable
        else:
            return 3.0  # Very different energy levels
    
    def _generate_recommendations(
        self,
        harmonic: Optional[HarmonicAnalysis],
        rhythmic: Optional[RhythmicAnalysis],
        frequency: Optional[FrequencyAnalysis],
        overall_score: float,
        genre: str
    ) -> List[str]:
        """Generate specific recommendations."""
        recommendations = []
        
        # Overall compatibility
        if overall_score >= 8:
            recommendations.append("Excellent compatibility - use together immediately")
        elif overall_score >= 6:
            recommendations.append("Good compatibility with minor adjustments")
        elif overall_score >= 4:
            recommendations.append("Moderate compatibility - requires careful arrangement")
        else:
            recommendations.append("Low compatibility - consider alternatives")
        
        # Harmonic recommendations
        if harmonic and harmonic.suggestion:
            recommendations.append(f"Harmonic: {harmonic.suggestion}")
        
        # Rhythmic recommendations
        if rhythmic and rhythmic.bpm_compatibility < 80:
            recommendations.append("Rhythmic: Consider time-stretching to match tempo")
        
        # Frequency recommendations
        if frequency and frequency.masking_risk == "high":
            recommendations.append("Frequency: Apply EQ to create separation")
            recommendations.extend(frequency.eq_suggestions[:2])
        
        # Genre-specific recommendations
        if genre == "hip-hop" and harmonic:
            recommendations.append("Ensure 808/kick are tuned to the same key")
        elif genre == "jazz":
            recommendations.append("Leave space for improvisation between elements")
        
        return recommendations
    
    def _determine_relationship_type(
        self,
        harmonic: Optional[HarmonicAnalysis],
        rhythmic: Optional[RhythmicAnalysis],
        frequency: Optional[FrequencyAnalysis],
        overall_score: float
    ) -> str:
        """Determine the type of relationship between samples."""
        if overall_score >= 8:
            return "Perfect Match"
        elif harmonic and harmonic.compatibility_score >= 8:
            return "Harmonic Partners"
        elif rhythmic and rhythmic.groove_match >= 8:
            return "Rhythmic Lock"
        elif frequency and frequency.complementary_score >= 8:
            return "Frequency Complement"
        elif overall_score >= 6:
            return "Compatible Blend"
        elif overall_score >= 4:
            return "Creative Tension"
        else:
            return "Challenging Combination"
    
    def _suggest_arrangement(
        self,
        sample1: Dict[str, Any],
        sample2: Dict[str, Any],
        relationship_type: str,
        genre: str
    ) -> str:
        """Suggest how to arrange the samples together."""
        arrangements = {
            "Perfect Match": "Layer both samples simultaneously for rich texture",
            "Harmonic Partners": "Use as verse/chorus alternation or call/response",
            "Rhythmic Lock": "Layer for polyrhythmic interest, pan separately",
            "Frequency Complement": "Full arrangement - each fills the other's gaps",
            "Compatible Blend": "Alternate sections, use automation for smooth transitions",
            "Creative Tension": "Use sparingly for dramatic effect or breakdowns",
            "Challenging Combination": "Consider using in different song sections"
        }
        
        base_arrangement = arrangements.get(relationship_type, "Experimental usage")
        
        # Add genre-specific tips
        if genre == "hip-hop":
            base_arrangement += ". Ensure drums hit hard, samples support the groove."
        elif genre == "jazz":
            base_arrangement += ". Allow breathing room, think conversation not competition."
        elif genre == "electronic":
            base_arrangement += ". Use filters and effects to create movement."
        
        return base_arrangement
    
    def _suggest_kit_arrangement(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest optimal arrangement for multiple samples."""
        if not analyses:
            return {}
        
        # Find best overall match
        best_pair = max(analyses, key=lambda x: x["overall_score"])
        
        # Group by compatibility
        high_compat = [a for a in analyses if a["overall_score"] >= 7]
        medium_compat = [a for a in analyses if 4 <= a["overall_score"] < 7]
        low_compat = [a for a in analyses if a["overall_score"] < 4]
        
        return {
            "best_combination": {
                "samples": [best_pair["sample1_name"], best_pair["sample2_name"]],
                "score": best_pair["overall_score"],
                "usage": best_pair["best_arrangement"]
            },
            "compatibility_groups": {
                "immediate_use": len(high_compat),
                "needs_work": len(medium_compat),
                "avoid": len(low_compat)
            },
            "kit_recommendation": self._generate_kit_recommendation(analyses)
        }
    
    def _generate_kit_recommendation(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate overall kit building recommendation."""
        avg_score = np.mean([a["overall_score"] for a in analyses])
        
        if avg_score >= 7:
            return "Excellent kit cohesion - these samples work beautifully together"
        elif avg_score >= 5:
            return "Good kit potential - apply suggested adjustments for best results"
        else:
            return "Challenging kit - consider replacing low-scoring combinations"
    
    def _extract_root_note(self, key_string: str) -> int:
        """Extract root note as semitone number (C=0)."""
        # Simplified key parsing - in production, use proper music theory library
        note_map = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        
        # Extract just the note part
        for note, value in note_map.items():
            if key_string.startswith(note):
                return value
        
        return 0  # Default to C
    
    def _estimate_energy(self, frequency_analysis: Dict[str, float]) -> float:
        """Estimate energy level from frequency analysis."""
        # Simple energy estimation based on spectral characteristics
        centroid = frequency_analysis.get("spectral_centroid", 2000)
        bandwidth = frequency_analysis.get("spectral_bandwidth", 1000)
        
        # Normalize to 0-1 range
        energy = (centroid / 5000) * 0.5 + (bandwidth / 3000) * 0.5
        return min(1.0, energy)
    
    def _check_frequency_overlap(
        self,
        freq1: Dict[str, float],
        freq2: Dict[str, float],
        low: float,
        high: float
    ) -> bool:
        """Check if two samples have significant overlap in a frequency range."""
        # Simplified overlap detection
        # In production, analyze actual frequency content in range
        centroid1 = freq1.get("spectral_centroid", 0)
        centroid2 = freq2.get("spectral_centroid", 0)
        
        return (low <= centroid1 <= high) and (low <= centroid2 <= high)
    
    def _generate_eq_suggestions(
        self,
        freq1: Dict[str, float],
        freq2: Dict[str, float],
        overlap_areas: List[str]
    ) -> List[str]:
        """Generate specific EQ suggestions."""
        suggestions = []
        
        if "Heavy mid-range overlap" in overlap_areas:
            suggestions.append("Cut 500-2kHz on one sample by 3-6dB")
            suggestions.append("Boost complementary frequencies on each")
        
        if "sub_bass overlap" in overlap_areas:
            suggestions.append("High-pass one sample at 100Hz")
            suggestions.append("Keep only one sub-bass element")
        
        if "high_mid overlap" in overlap_areas:
            suggestions.append("Use different filter slopes for separation")
            suggestions.append("Pan samples to opposite sides")
        
        return suggestions
    
    def _generate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of all compatibility analyses."""
        if not analyses:
            return {}
        
        scores = [a["overall_score"] for a in analyses]
        
        return {
            "total_analyzed": len(analyses),
            "average_compatibility": round(np.mean(scores), 1),
            "best_match": max(scores),
            "worst_match": min(scores),
            "compatibility_distribution": {
                "excellent": len([s for s in scores if s >= 8]),
                "good": len([s for s in scores if 6 <= s < 8]),
                "moderate": len([s for s in scores if 4 <= s < 6]),
                "poor": len([s for s in scores if s < 4])
            }
        }


# Convenience functions
async def analyze_sample_compatibility(
    sample_pairs: List[Tuple[str, str]],
    genre: str = "general",
    check_type: str = "all"
) -> Dict[str, Any]:
    """Analyze compatibility between sample pairs."""
    agent = SampleRelationshipAgent()
    result = await agent.execute(
        task_id=f"compat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        sample_pairs=sample_pairs,
        genre=genre,
        check_type=check_type
    )
    return result.result if result.status == AgentStatus.SUCCESS else {"error": result.error}


async def check_harmonic_compatibility(sample1: str, sample2: str) -> Dict[str, Any]:
    """Quick harmonic compatibility check."""
    return await analyze_sample_compatibility(
        [(sample1, sample2)],
        check_type="harmonic"
    )