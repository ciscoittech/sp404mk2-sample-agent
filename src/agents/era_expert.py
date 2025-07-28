"""
Era Expert Agent - Musical production history and era-specific knowledge.
Provides deep insights into recording techniques, equipment, and sonic characteristics across decades.
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from ..logging_config import AgentLogger
from ..tools import database
from ..tools.audio import analyze_frequency_content, detect_bpm, get_duration
from .base import Agent, AgentResult, AgentStatus


# Pydantic models for structured era analysis
class EraEquipment(BaseModel):
    """Equipment characteristic of an era."""
    category: str = Field(description="Equipment category (console, synth, etc)")
    models: List[str] = Field(description="Specific models used")
    significance: str = Field(description="Why this equipment mattered")


class EraTechniques(BaseModel):
    """Production techniques of an era."""
    recording: List[str] = Field(description="Recording techniques")
    mixing: List[str] = Field(description="Mixing approaches")
    effects: List[str] = Field(description="Common effects and processing")


class EraCharacteristics(BaseModel):
    """Sonic characteristics of an era."""
    frequency_profile: str = Field(description="Typical frequency content")
    dynamics: str = Field(description="Dynamic range and compression")
    spatial: str = Field(description="Stereo image characteristics")
    artifacts: List[str] = Field(description="Era-specific artifacts (tape hiss, etc)")


class EraAnalysisResult(BaseModel):
    """Complete era analysis result."""
    detected_era: Optional[str]
    confidence: float = Field(ge=0.0, le=1.0)
    key_equipment: List[EraEquipment]
    techniques: EraTechniques
    sonic_characteristics: EraCharacteristics
    genre_context: Dict[str, str]
    search_queries: List[str]
    modern_recreation: Dict[str, List[str]]


class EraExpertAgent(Agent):
    """Agent specialized in musical production history and era detection."""
    
    def __init__(self):
        """Initialize the Era Expert Agent."""
        super().__init__("era_expert")
        self.logger = AgentLogger(self.name)
        
        # Era knowledge database
        self.era_database = {
            "1950s-1960s": {
                "equipment": {
                    "tape": ["Ampex 350/351", "Studer J37"],
                    "consoles": ["Early Neve", "EMI REDD"],
                    "mics": ["Neumann U47", "RCA 44-BX"],
                    "reverb": ["Live chambers", "EMT 140 plate"]
                },
                "techniques": {
                    "recording": ["Live to 2-track", "Minimal overdubs"],
                    "mixing": ["Mono mixing", "Early stereo"],
                    "effects": ["Natural room ambience", "Tape saturation"]
                },
                "sonic_signature": {
                    "frequency": "Warm, midrange-focused",
                    "dynamics": "Natural dynamics, minimal compression",
                    "spatial": "Mono or narrow stereo",
                    "artifacts": ["Tape hiss", "Tube warmth", "Room tone"]
                },
                "search_terms": ["vintage warmth", "tube saturation", "live room", "mono mix"]
            },
            "1970s": {
                "equipment": {
                    "consoles": ["Neve 8078", "SSL 4000", "MCI"],
                    "synths": ["Minimoog", "ARP 2600", "Rhodes", "Clavinet"],
                    "drums": ["Ludwig kits", "Linn LM-1"],
                    "effects": ["Tape delay", "Spring reverb", "Mu-Tron"]
                },
                "techniques": {
                    "recording": ["16/24 track recording", "Isolated recording"],
                    "mixing": ["Heavy compression", "Wide stereo"],
                    "effects": ["1176/LA-2A compression", "Tape delay"]
                },
                "sonic_signature": {
                    "frequency": "Analog warmth with clarity",
                    "dynamics": "Punchy, compressed drums",
                    "spatial": "Wide stereo field",
                    "artifacts": ["Tape saturation", "Analog compression"]
                },
                "genres": ["Funk", "Disco", "Soul", "Rock"],
                "search_terms": ["analog warmth", "vintage compression", "70s funk", "tape saturation"]
            },
            "1980s": {
                "equipment": {
                    "digital": ["Fairlight CMI", "Synclavier", "DX7"],
                    "drums": ["Simmons", "Roland TR-808", "LinnDrum"],
                    "reverb": ["Lexicon 224", "AMS RMX16"],
                    "samplers": ["Akai S900", "E-MU SP-12"]
                },
                "techniques": {
                    "recording": ["MIDI sequencing", "Digital sampling"],
                    "mixing": ["Gated reverb", "Digital effects"],
                    "effects": ["Chorus/flanger", "Digital delays"]
                },
                "sonic_signature": {
                    "frequency": "Bright, crystalline highs",
                    "dynamics": "Heavy processing, less natural",
                    "spatial": "Huge reverbs, artificial space",
                    "artifacts": ["Digital aliasing", "Synthetic textures"]
                },
                "search_terms": ["80s reverb", "gated drums", "DX7 bass", "digital brightness"]
            },
            "1990s": {
                "equipment": {
                    "samplers": ["MPC2000/3000", "SP-1200", "ASR-10"],
                    "daws": ["Early Pro Tools", "Cubase"],
                    "effects": ["Eventide H3000", "TC Electronic"],
                    "vinyl": ["Technics 1200 turntables"]
                },
                "techniques": {
                    "recording": ["Sampling from vinyl", "Chopping/time-stretching"],
                    "mixing": ["Bit reduction", "Low-pass filtering"],
                    "effects": ["Parallel compression", "Vinyl simulation"]
                },
                "sonic_signature": {
                    "frequency": "Filtered highs, warm mids",
                    "dynamics": "Hip-hop compression, boom bap punch",
                    "spatial": "Centered drums, wide samples",
                    "artifacts": ["12-bit crunch", "Vinyl crackle", "Sample artifacts"]
                },
                "genres": ["Hip-Hop", "R&B", "Trip-Hop"],
                "search_terms": ["boom bap", "golden era", "dusty samples", "vinyl crackle"]
            },
            "2000s-2010s": {
                "equipment": {
                    "software": ["Ableton", "FL Studio", "Logic"],
                    "plugins": ["Waves", "UAD emulations"],
                    "controllers": ["MPD", "Maschine", "Push"],
                    "limiters": ["L2", "Ozone"]
                },
                "techniques": {
                    "recording": ["In-the-box production", "Pitch correction"],
                    "mixing": ["Loudness war mastering", "Sidechain compression"],
                    "effects": ["Plugin chains", "Trap hi-hats"]
                },
                "sonic_signature": {
                    "frequency": "Hyped lows and highs",
                    "dynamics": "Over-compressed, loud",
                    "spatial": "Wide, processed stereo",
                    "artifacts": ["Digital perfection", "Autotune artifacts"]
                },
                "search_terms": ["modern production", "trap drums", "EDM drops", "sidechain"]
            }
        }
        
        # Genre-specific studios and producers
        self.genre_knowledge = {
            "motown": {
                "era": "1960s",
                "studio": "Hitsville U.S.A.",
                "producers": ["Berry Gordy", "Smokey Robinson"],
                "signature": "Direct-input bass, tambourine on 2&4"
            },
            "philadelphia_soul": {
                "era": "1970s",
                "studio": "Sigma Sound Studios",
                "producers": ["Gamble & Huff"],
                "signature": "Lush strings, MFSB rhythm section"
            },
            "golden_era_hiphop": {
                "era": "1990s",
                "studios": ["D&D", "Battery", "Unique"],
                "producers": ["DJ Premier", "Pete Rock", "Large Professor"],
                "signature": "Filtered jazz loops, hard drums"
            }
        }
    
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Analyze samples for era characteristics and provide historical context.
        
        Args:
            task_id: Unique task identifier
            file_paths: Audio files to analyze for era detection
            target_era: Specific era to analyze for
            genre: Musical genre for context
            enhance_search: Whether to generate era-specific search queries
            
        Returns:
            AgentResult with era analysis
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting era analysis")
        started_at = datetime.now(timezone.utc)
        
        try:
            file_paths = kwargs.get("file_paths", [])
            target_era = kwargs.get("target_era")
            genre = kwargs.get("genre", "")
            enhance_search = kwargs.get("enhance_search", True)
            
            results = []
            
            # Analyze files if provided
            if file_paths:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        analysis = await self._analyze_era_characteristics(file_path)
                        results.append(analysis)
            
            # Provide era information if requested
            if target_era:
                era_info = self._get_era_information(target_era, genre)
                
                # Generate enhanced search queries
                if enhance_search:
                    search_queries = self._generate_era_search_queries(
                        target_era, genre, kwargs.get("base_query", "")
                    )
                    era_info["enhanced_searches"] = search_queries
                
                results.append(era_info)
            
            # Log results (skip if database not configured)
            try:
                await database.add_agent_log({
                    "task_id": task_id,
                    "agent_type": self.name,
                    "log_level": "info",
                    "message": f"Completed era analysis",
                    "context": {
                        "files_analyzed": len(file_paths),
                        "target_era": target_era
                    }
                })
            except Exception:
                pass  # Skip logging if database not available
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result={
                    "analyses": results,
                    "summary": self._generate_summary(results)
                },
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.exception(f"Era analysis failed: {str(e)}")
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _analyze_era_characteristics(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio file for era-specific characteristics."""
        # Get audio properties
        frequency_analysis = analyze_frequency_content(file_path)
        duration = get_duration(file_path)
        
        # Detect era based on sonic characteristics
        detected_era, confidence = self._detect_era_from_audio(frequency_analysis)
        
        # Get era information
        era_info = self._get_era_information(detected_era) if detected_era else {}
        
        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "detected_era": detected_era,
            "confidence": confidence,
            "frequency_analysis": frequency_analysis,
            "era_characteristics": era_info.get("characteristics", {}),
            "probable_equipment": era_info.get("equipment", {}),
            "production_notes": self._generate_production_notes(detected_era, frequency_analysis)
        }
    
    def _detect_era_from_audio(
        self,
        frequency_analysis: Dict[str, float]
    ) -> Tuple[Optional[str], float]:
        """Detect era based on frequency characteristics."""
        # Mock detection based on frequency profile
        # In production, this would use more sophisticated analysis
        
        spectral_centroid = frequency_analysis.get("spectral_centroid", 2000)
        spectral_rolloff = frequency_analysis.get("spectral_rolloff", 4000)
        
        # Simple heuristics for era detection
        if spectral_centroid < 1500 and spectral_rolloff < 3000:
            # Limited high frequencies suggests older recording
            return "1950s-1960s", 0.7
        elif spectral_centroid < 2500 and spectral_rolloff < 5000:
            # Warm analog sound
            return "1970s", 0.75
        elif spectral_centroid > 3000 and spectral_rolloff > 7000:
            # Bright digital sound
            return "1980s", 0.7
        elif 2000 < spectral_centroid < 3000:
            # Balanced but potentially filtered (sampling era)
            return "1990s", 0.65
        else:
            # Modern production
            return "2000s-2010s", 0.6
    
    def _get_era_information(
        self,
        era: str,
        genre: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed information about an era."""
        era_data = self.era_database.get(era, {})
        
        if not era_data:
            return {}
        
        # Build structured response
        result = {
            "era": era,
            "equipment": self._format_equipment(era_data.get("equipment", {})),
            "techniques": era_data.get("techniques", {}),
            "characteristics": era_data.get("sonic_signature", {}),
            "search_terms": era_data.get("search_terms", []),
            "genres": era_data.get("genres", [])
        }
        
        # Add genre-specific information
        if genre:
            genre_info = self._get_genre_context(genre, era)
            if genre_info:
                result["genre_context"] = genre_info
        
        # Add modern recreation tips
        result["modern_recreation"] = self._get_modern_recreation_tips(era)
        
        return result
    
    def _format_equipment(self, equipment: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Format equipment information."""
        formatted = []
        
        significance_map = {
            "tape": "Defined the warmth and saturation of the era",
            "consoles": "Shaped the tonal balance and workflow",
            "synths": "Created the signature sounds and textures",
            "drums": "Established the rhythmic foundation",
            "samplers": "Revolutionized music production",
            "reverb": "Defined the spatial characteristics"
        }
        
        for category, models in equipment.items():
            formatted.append({
                "category": category,
                "models": models,
                "significance": significance_map.get(category, f"Key {category} of the era")
            })
        
        return formatted
    
    def _generate_era_search_queries(
        self,
        era: str,
        genre: str,
        base_query: str
    ) -> List[str]:
        """Generate era-specific search queries."""
        queries = []
        era_data = self.era_database.get(era, {})
        
        # Base query variations
        if base_query:
            queries.append(f"{base_query} {era}")
            
            # Add era-specific terms
            for term in era_data.get("search_terms", []):
                queries.append(f"{base_query} {term}")
            
            # Add equipment-specific queries
            equipment = era_data.get("equipment", {})
            for category, models in equipment.items():
                if models:
                    queries.append(f"{base_query} {models[0]}")
        
        # Genre-specific queries
        if genre:
            if era == "1970s" and "soul" in genre.lower():
                queries.extend([
                    f"{genre} Philadelphia sound",
                    f"{genre} Motown bass",
                    f"{genre} MFSB rhythm"
                ])
            elif era == "1990s" and "hip" in genre.lower():
                queries.extend([
                    f"{genre} boom bap MPC",
                    f"{genre} SP-1200 drums",
                    f"{genre} golden era samples"
                ])
        
        # Add studio/producer queries
        if genre in self.genre_knowledge:
            info = self.genre_knowledge[genre]
            if info["era"] == era:
                for producer in info["producers"][:2]:
                    queries.append(f"{base_query} {producer} style")
        
        return queries[:10]  # Limit to 10 queries
    
    def _get_genre_context(self, genre: str, era: str) -> Optional[Dict[str, Any]]:
        """Get genre-specific context for an era."""
        # Normalize genre name
        genre_key = genre.lower().replace(" ", "_").replace("-", "_")
        
        if genre_key in self.genre_knowledge:
            info = self.genre_knowledge[genre_key]
            if info["era"] == era:
                return {
                    "studio": info["studio"],
                    "producers": info["producers"],
                    "signature_sound": info["signature"],
                    "cultural_context": f"{genre} peaked in the {era}"
                }
        
        return None
    
    def _get_modern_recreation_tips(self, era: str) -> Dict[str, List[str]]:
        """Get tips for recreating era sounds with modern tools."""
        recreation_tips = {
            "1950s-1960s": {
                "plugins": ["UAD Studer A800", "Waves J37", "Softube Tube-Tech"],
                "techniques": ["Record in mono", "Use room mics", "Gentle tape saturation"],
                "tips": ["Less is more", "Commit to sounds", "Natural dynamics"]
            },
            "1970s": {
                "plugins": ["UAD Neve 1073", "Waves SSL", "Arturia analog emulations"],
                "techniques": ["Parallel compression", "Analog-style EQ", "Tape delay"],
                "tips": ["Push the preamps", "Use bus compression", "Wide stereo image"]
            },
            "1980s": {
                "plugins": ["Arturia DX7 V", "D16 LuSH-101", "Valhalla VintageVerb"],
                "techniques": ["Gated reverb", "Chorus on everything", "Digital delays"],
                "tips": ["Embrace the brightness", "Big reverbs", "Layer synths"]
            },
            "1990s": {
                "plugins": ["XLN RC-20", "Decimort 2", "Vinyl simulator"],
                "techniques": ["Bit reduction", "Vinyl simulation", "MPC-style swing"],
                "tips": ["Sample in mono", "Filter the highs", "Add vinyl crackle"]
            },
            "2000s-2010s": {
                "plugins": ["FabFilter bundle", "Serum", "Ozone"],
                "techniques": ["Sidechain compression", "Multiband processing", "Loudness"],
                "tips": ["Clean digital sound", "Perfect timing", "Maximum loudness"]
            }
        }
        
        return recreation_tips.get(era, {})
    
    def _generate_production_notes(
        self,
        era: Optional[str],
        frequency_analysis: Dict[str, float]
    ) -> str:
        """Generate production notes based on analysis."""
        notes = []
        
        if era:
            era_data = self.era_database.get(era, {})
            signature = era_data.get("sonic_signature", {})
            
            # Frequency observations
            spectral_centroid = frequency_analysis.get("spectral_centroid", 0)
            if spectral_centroid < 2000:
                notes.append("Limited high frequency content suggests vintage equipment or intentional filtering")
            elif spectral_centroid > 3000:
                notes.append("Extended high frequencies indicate modern recording or digital sources")
            
            # Era-specific notes
            if era == "1990s":
                notes.append("Consider this might be sampled from vinyl - check for pitch variations")
            elif era == "1970s":
                notes.append("Analog warmth detected - likely recorded to tape with vintage preamps")
            
            # Add signature characteristics
            if signature.get("artifacts"):
                notes.append(f"Listen for: {', '.join(signature['artifacts'])}")
        
        return ". ".join(notes) if notes else "No specific production notes."
    
    def _generate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of era analyses."""
        if not analyses:
            return {}
        
        # Count detected eras
        era_counts = {}
        for analysis in analyses:
            if "detected_era" in analysis and analysis["detected_era"]:
                era = analysis["detected_era"]
                era_counts[era] = era_counts.get(era, 0) + 1
        
        # Find predominant era
        predominant_era = max(era_counts.items(), key=lambda x: x[1])[0] if era_counts else None
        
        # Collect all search terms
        all_search_terms = []
        for analysis in analyses:
            if "search_terms" in analysis:
                all_search_terms.extend(analysis["search_terms"])
        
        return {
            "total_analyzed": len(analyses),
            "detected_eras": era_counts,
            "predominant_era": predominant_era,
            "recommended_searches": list(set(all_search_terms))[:10]
        }


# Convenience functions
async def analyze_era(
    file_paths: Optional[List[str]] = None,
    target_era: Optional[str] = None,
    genre: Optional[str] = None,
    enhance_search: bool = True
) -> Dict[str, Any]:
    """Analyze samples for era characteristics."""
    agent = EraExpertAgent()
    result = await agent.execute(
        task_id=f"era_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        file_paths=file_paths or [],
        target_era=target_era,
        genre=genre,
        enhance_search=enhance_search
    )
    return result.result if result.status == AgentStatus.SUCCESS else {"error": result.error}


async def get_era_search_queries(
    era: str,
    genre: str,
    base_query: str = ""
) -> List[str]:
    """Get era-specific search queries."""
    agent = EraExpertAgent()
    return agent._generate_era_search_queries(era, genre, base_query)