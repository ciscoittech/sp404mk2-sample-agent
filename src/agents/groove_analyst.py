"""
Groove Analyst Agent - Deep rhythm and timing analysis for samples.
Uses specialist knowledge to analyze groove, swing, and rhythmic feel.
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ..logging_config import AgentLogger
from ..tools import database
from ..tools.audio import detect_bpm, get_duration, analyze_frequency_content
from .base import Agent, AgentResult, AgentStatus


# Pydantic models for structured groove analysis
class TimingAnalysis(BaseModel):
    """Detailed timing analysis results."""
    average_deviation_ms: float = Field(description="Average deviation from grid in milliseconds")
    swing_ratio: str = Field(description="Ratio of first to second eighth note")
    push_pull_ms: float = Field(description="How far ahead/behind the beat (negative=behind)")
    consistency: float = Field(description="Timing consistency score 0-1")


class GrooveCharacteristics(BaseModel):
    """Musical groove characteristics."""
    swing_percentage: float = Field(ge=50.0, le=75.0, description="Swing percentage")
    timing_feel: str = Field(description="behind/on/ahead of beat")
    pocket_score: float = Field(ge=0.0, le=10.0, description="How well it sits in the pocket")
    humanization_level: str = Field(description="mechanical/tight/loose/human/drunk")
    ghost_note_density: str = Field(description="low/medium/high")


class GrooveAnalysisResult(BaseModel):
    """Complete groove analysis result."""
    file_path: str
    bpm: float
    bpm_confidence: float
    groove: GrooveCharacteristics
    timing: TimingAnalysis
    musical_description: str
    similar_to: List[str] = Field(description="Similar artists/producers")
    recommendations: List[str] = Field(description="Usage recommendations")
    era_classification: Optional[str] = Field(description="Detected era/period")


class GrooveAnalystAgent(Agent):
    """Agent specialized in rhythm and groove analysis."""
    
    def __init__(self):
        """Initialize the Groove Analyst Agent."""
        super().__init__("groove_analyst")
        self.logger = AgentLogger(self.name)
        
        # Groove reference database
        self.groove_references = {
            "dilla": {
                "swing_range": (62, 68),
                "timing": "drunk",
                "description": "Off-kilter, drunk swing with intentional timing variations",
                "keywords": ["wonky", "off-grid", "MPC3000"]
            },
            "questlove": {
                "swing_range": (58, 62),
                "timing": "behind",
                "description": "Deep pocket, consistently behind the beat",
                "keywords": ["pocket", "laid back", "roots"]
            },
            "purdie": {
                "swing_range": (55, 60),
                "timing": "on",
                "description": "Tight shuffle with ghost notes on 2e and 4e",
                "keywords": ["shuffle", "ghost notes", "funky"]
            },
            "programmed": {
                "swing_range": (50, 52),
                "timing": "on",
                "description": "Machine-perfect quantization",
                "keywords": ["quantized", "rigid", "mechanical"]
            }
        }
        
        # Era characteristics
        self.era_grooves = {
            "1960s": {"swing": (55, 65), "humanization": "human", "rushing": True},
            "1970s": {"swing": (56, 62), "humanization": "tight", "rushing": False},
            "1980s": {"swing": (50, 55), "humanization": "mechanical", "rushing": False},
            "1990s": {"swing": (58, 68), "humanization": "loose", "rushing": False},
            "2000s": {"swing": (50, 65), "humanization": "mixed", "rushing": False}
        }
    
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Analyze groove and rhythm characteristics of audio samples.
        
        Args:
            task_id: Unique task identifier
            file_paths: List of audio file paths to analyze
            analysis_depth: 'basic', 'detailed', or 'forensic'
            compare_grooves: Whether to compare multiple files
            
        Returns:
            AgentResult with groove analysis
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting groove analysis")
        started_at = datetime.now(timezone.utc)
        
        try:
            file_paths = kwargs.get("file_paths", [])
            if not file_paths:
                raise ValueError("No audio files provided for analysis")
            
            analysis_depth = kwargs.get("analysis_depth", "detailed")
            compare_grooves = kwargs.get("compare_grooves", False)
            
            # Analyze each file
            analyses = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    self.logger.warning(f"File not found: {file_path}")
                    continue
                
                analysis = await self._analyze_groove(file_path, analysis_depth)
                analyses.append(analysis)
            
            # Compare grooves if requested
            comparison = None
            if compare_grooves and len(analyses) > 1:
                comparison = self._compare_grooves(analyses)
            
            # Log results (skip if database not configured)
            try:
                await database.add_agent_log({
                    "task_id": task_id,
                    "agent_type": self.name,
                    "log_level": "info",
                    "message": f"Analyzed {len(analyses)} files",
                    "context": {
                        "files_analyzed": len(analyses),
                        "analysis_depth": analysis_depth
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
                    "comparison": comparison,
                    "summary": self._generate_summary(analyses)
                },
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.exception(f"Groove analysis failed: {str(e)}")
            
            try:
                await database.add_agent_log({
                    "task_id": task_id,
                    "agent_type": self.name,
                    "log_level": "error",
                    "message": f"Analysis failed: {str(e)}"
                })
            except Exception:
                pass  # Skip logging if database not available
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _analyze_groove(
        self,
        file_path: str,
        depth: str = "detailed"
    ) -> Dict[str, Any]:
        """Analyze groove characteristics of a single file."""
        # Get basic audio properties
        bpm_result = detect_bpm(file_path)
        duration = get_duration(file_path)
        
        # Mock advanced analysis (in production, use actual onset detection)
        timing_analysis = self._analyze_timing(file_path, bpm_result["bpm"])
        groove_chars = self._calculate_groove_characteristics(timing_analysis, bpm_result["bpm"])
        
        # Find similar artists
        similar_artists = self._find_similar_grooves(groove_chars)
        
        # Detect era
        era = self._classify_era(groove_chars)
        
        # Generate musical description
        description = self._generate_description(groove_chars, timing_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(groove_chars, bpm_result["bpm"])
        
        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "duration": duration,
            "bpm": bpm_result["bpm"],
            "bpm_confidence": bpm_result["confidence"],
            "groove": {
                "swing_percentage": groove_chars.swing_percentage,
                "timing_feel": groove_chars.timing_feel,
                "pocket_score": groove_chars.pocket_score,
                "humanization_level": groove_chars.humanization_level,
                "ghost_note_density": groove_chars.ghost_note_density
            },
            "timing": {
                "average_deviation_ms": timing_analysis.average_deviation_ms,
                "swing_ratio": timing_analysis.swing_ratio,
                "push_pull_ms": timing_analysis.push_pull_ms,
                "consistency": timing_analysis.consistency
            },
            "musical_description": description,
            "similar_to": similar_artists,
            "recommendations": recommendations,
            "era_classification": era
        }
    
    def _analyze_timing(self, file_path: str, bpm: float) -> TimingAnalysis:
        """Analyze timing characteristics (mock implementation)."""
        # In production, this would use onset detection and grid analysis
        # For now, generate plausible mock data
        
        # Simulate based on file name patterns
        file_name = os.path.basename(file_path).lower()
        
        if "dilla" in file_name or "wonky" in file_name:
            deviation = 25.0
            swing_ratio = "65:35"
            push_pull = 15.0
            consistency = 0.6
        elif "straight" in file_name or "quantized" in file_name:
            deviation = 3.0
            swing_ratio = "50:50"
            push_pull = 0.0
            consistency = 0.95
        else:
            # Random realistic values
            deviation = 8.0 + (hash(file_name) % 10)
            swing_pct = 50 + (hash(file_name) % 25)
            swing_ratio = f"{swing_pct}:{100-swing_pct}"
            push_pull = -5.0 + (hash(file_name) % 10)
            consistency = 0.7 + (hash(file_name) % 30) / 100
        
        return TimingAnalysis(
            average_deviation_ms=deviation,
            swing_ratio=swing_ratio,
            push_pull_ms=push_pull,
            consistency=consistency
        )
    
    def _calculate_groove_characteristics(
        self,
        timing: TimingAnalysis,
        bpm: float
    ) -> GrooveCharacteristics:
        """Calculate groove characteristics from timing analysis."""
        # Extract swing percentage from ratio
        swing_parts = timing.swing_ratio.split(":")
        swing_pct = float(swing_parts[0])
        
        # Determine timing feel
        if timing.push_pull_ms < -10:
            timing_feel = "behind"
        elif timing.push_pull_ms > 10:
            timing_feel = "ahead"
        else:
            timing_feel = "on"
        
        # Calculate pocket score (0-10)
        # Better pocket = consistent timing with slight behind feel
        pocket_score = 10.0
        pocket_score -= abs(timing.push_pull_ms + 15) / 10  # Optimal at -15ms
        pocket_score -= (1 - timing.consistency) * 5
        pocket_score = max(0, min(10, pocket_score))
        
        # Determine humanization level
        if timing.average_deviation_ms < 5:
            humanization = "mechanical"
        elif timing.average_deviation_ms < 10:
            humanization = "tight"
        elif timing.average_deviation_ms < 20:
            humanization = "loose"
        elif timing.average_deviation_ms < 30:
            humanization = "human"
        else:
            humanization = "drunk"
        
        # Ghost note density (mock)
        if bpm > 120:
            ghost_density = "high"
        elif bpm > 90:
            ghost_density = "medium"
        else:
            ghost_density = "low"
        
        return GrooveCharacteristics(
            swing_percentage=swing_pct,
            timing_feel=timing_feel,
            pocket_score=pocket_score,
            humanization_level=humanization,
            ghost_note_density=ghost_density
        )
    
    def _find_similar_grooves(self, groove: GrooveCharacteristics) -> List[str]:
        """Find similar artists/producers based on groove characteristics."""
        similar = []
        
        for artist, ref in self.groove_references.items():
            # Check swing range
            if ref["swing_range"][0] <= groove.swing_percentage <= ref["swing_range"][1]:
                # Check timing feel
                if groove.timing_feel == ref["timing"]:
                    similar.append(artist.title())
                elif groove.humanization_level == ref["timing"]:
                    similar.append(f"{artist.title()} (similar feel)")
        
        # Add descriptive references
        if groove.swing_percentage > 65:
            similar.append("Heavy swing/shuffle drummers")
        if groove.pocket_score > 8:
            similar.append("Deep pocket players")
        if groove.humanization_level == "drunk":
            similar.append("Experimental beat makers")
        
        return similar[:3]  # Top 3 matches
    
    def _classify_era(self, groove: GrooveCharacteristics) -> Optional[str]:
        """Classify the era based on groove characteristics."""
        best_match = None
        best_score = 0
        
        for era, chars in self.era_grooves.items():
            score = 0
            
            # Check swing range
            if chars["swing"][0] <= groove.swing_percentage <= chars["swing"][1]:
                score += 2
            
            # Check humanization
            if groove.humanization_level == chars["humanization"]:
                score += 2
            elif groove.humanization_level in ["loose", "human"] and chars["humanization"] == "mixed":
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = era
        
        return best_match if best_score >= 2 else None
    
    def _generate_description(
        self,
        groove: GrooveCharacteristics,
        timing: TimingAnalysis
    ) -> str:
        """Generate a musical description of the groove."""
        descriptions = []
        
        # Describe the basic feel
        if groove.swing_percentage > 65:
            descriptions.append("Heavy swing feel with strong triplet subdivision")
        elif groove.swing_percentage > 58:
            descriptions.append("Medium swing creating a bouncy, head-nodding groove")
        elif groove.swing_percentage > 52:
            descriptions.append("Subtle swing adding just a touch of bounce")
        else:
            descriptions.append("Straight, even eighth notes")
        
        # Describe timing
        if groove.timing_feel == "behind":
            descriptions.append("Playing behind the beat creates a laid-back, relaxed feel")
        elif groove.timing_feel == "ahead":
            descriptions.append("Pushing ahead of the beat adds urgency and drive")
        
        # Describe pocket
        if groove.pocket_score > 8:
            descriptions.append("Sits deep in the pocket with incredible groove")
        elif groove.pocket_score > 6:
            descriptions.append("Good pocket feel that locks in nicely")
        
        # Describe humanization
        if groove.humanization_level == "drunk":
            descriptions.append("Intentionally loose timing creates that 'Dilla' drunken feel")
        elif groove.humanization_level == "human":
            descriptions.append("Natural human timing variations add life and character")
        elif groove.humanization_level == "mechanical":
            descriptions.append("Machine-precise timing for a modern, produced sound")
        
        return ". ".join(descriptions)
    
    def _generate_recommendations(
        self,
        groove: GrooveCharacteristics,
        bpm: float
    ) -> List[str]:
        """Generate usage recommendations."""
        recommendations = []
        
        # BPM-based recommendations
        if 85 <= bpm <= 95:
            recommendations.append("Perfect for hip-hop production and head-nodding beats")
        elif 120 <= bpm <= 130:
            recommendations.append("Great for house music or uptempo hip-hop")
        
        # Swing-based recommendations
        if groove.swing_percentage > 62:
            recommendations.append("Layer with straight drums for rhythmic contrast")
            recommendations.append("Use for jazz-influenced or neo-soul productions")
        else:
            recommendations.append("Works well for modern trap or electronic production")
        
        # Pocket recommendations
        if groove.pocket_score > 7:
            recommendations.append("This groove can carry an entire track - less is more")
        
        # Humanization recommendations
        if groove.humanization_level in ["loose", "human", "drunk"]:
            recommendations.append("Preserve the natural timing when chopping")
            recommendations.append("Avoid additional quantization to maintain feel")
        
        return recommendations
    
    def _compare_grooves(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple grooves for compatibility."""
        if len(analyses) < 2:
            return None
        
        comparisons = []
        
        for i in range(len(analyses)):
            for j in range(i + 1, len(analyses)):
                groove1 = analyses[i]["groove"]
                groove2 = analyses[j]["groove"]
                
                # Calculate compatibility
                swing_diff = abs(groove1["swing_percentage"] - groove2["swing_percentage"])
                timing_match = groove1["timing_feel"] == groove2["timing_feel"]
                
                compatibility_score = 10.0
                compatibility_score -= swing_diff / 5  # -1 point per 5% difference
                if not timing_match:
                    compatibility_score -= 2
                
                compatibility_score = max(0, min(10, compatibility_score))
                
                comparisons.append({
                    "file1": analyses[i]["file_name"],
                    "file2": analyses[j]["file_name"],
                    "compatibility_score": compatibility_score,
                    "swing_difference": swing_diff,
                    "timing_match": timing_match,
                    "recommendation": self._get_compatibility_recommendation(
                        compatibility_score, swing_diff
                    )
                })
        
        return {
            "comparisons": comparisons,
            "best_pair": max(comparisons, key=lambda x: x["compatibility_score"])
        }
    
    def _get_compatibility_recommendation(
        self,
        score: float,
        swing_diff: float
    ) -> str:
        """Get recommendation for groove compatibility."""
        if score > 8:
            return "Excellent match - these grooves will lock together perfectly"
        elif score > 6:
            return "Good compatibility - minor adjustments may enhance the blend"
        elif score > 4:
            return "Moderate compatibility - use creatively for contrast"
        else:
            return "Low compatibility - best used in different sections"
    
    def _generate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of all analyses."""
        if not analyses:
            return {}
        
        # Calculate averages
        avg_swing = np.mean([a["groove"]["swing_percentage"] for a in analyses])
        avg_pocket = np.mean([a["groove"]["pocket_score"] for a in analyses])
        
        # Find most common characteristics
        timing_feels = [a["groove"]["timing_feel"] for a in analyses]
        most_common_feel = max(set(timing_feels), key=timing_feels.count)
        
        # Identify standouts
        deepest_pocket = max(analyses, key=lambda x: x["groove"]["pocket_score"])
        most_swing = max(analyses, key=lambda x: x["groove"]["swing_percentage"])
        
        return {
            "total_analyzed": len(analyses),
            "average_swing": round(avg_swing, 1),
            "average_pocket_score": round(avg_pocket, 1),
            "predominant_feel": most_common_feel,
            "standout_grooves": {
                "deepest_pocket": deepest_pocket["file_name"],
                "most_swing": most_swing["file_name"]
            }
        }


# Convenience function for standalone use
async def analyze_groove(
    file_paths: List[str],
    analysis_depth: str = "detailed",
    compare: bool = False
) -> Dict[str, Any]:
    """Analyze groove characteristics of audio files."""
    agent = GrooveAnalystAgent()
    result = await agent.execute(
        task_id=f"groove_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        file_paths=file_paths,
        analysis_depth=analysis_depth,
        compare_grooves=compare
    )
    return result.result if result.status == AgentStatus.SUCCESS else {"error": result.error}