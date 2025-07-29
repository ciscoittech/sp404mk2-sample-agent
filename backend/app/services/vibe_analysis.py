"""Vibe analysis service for samples."""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random

from app.models.sample import Sample


class VibeAnalysisService:
    """Service for analyzing sample vibes."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_sample(self, sample_id: int) -> Dict:
        """Analyze a sample's vibe characteristics."""
        sample = await self.db.get(Sample, sample_id)
        if not sample:
            raise ValueError(f"Sample {sample_id} not found")
        
        # Simulate analysis based on sample metadata
        # In a real implementation, this would analyze the audio file
        moods = ["energetic", "melancholic", "aggressive", "chill", "mysterious", "uplifting"]
        textures = [
            ["punchy", "crisp", "bright", "digital"],
            ["dusty", "vinyl", "warm", "nostalgic"],
            ["harsh", "distorted", "raw", "gritty"],
            ["smooth", "soft", "ambient", "ethereal"],
            ["dark", "brooding", "atmospheric", "deep"],
            ["vibrant", "colorful", "dynamic", "lively"]
        ]
        
        mood_index = hash(sample.title) % len(moods)
        mood = moods[mood_index]
        
        return {
            "sample_id": sample_id,
            "mood": mood,
            "mood_primary": mood,
            "mood_secondary": random.choice([m for m in moods if m != mood]),
            "mood_confidence": 0.75 + random.random() * 0.2,
            "energy": 0.3 + random.random() * 0.6,
            "energy_level": 0.3 + random.random() * 0.6,
            "energy_variance": random.random() * 0.3,
            "danceability": 0.4 + random.random() * 0.5,
            "acousticness": random.random() * 0.7,
            "instrumentalness": random.random() * 0.9,
            "textures": random.sample(textures[mood_index], 3),
            "texture_tags": random.sample(textures[mood_index], 3),
            "compatible_genres": self._get_compatible_genres(mood),
            "bpm": sample.bpm or self._estimate_bpm(mood),
            "key": sample.musical_key or self._estimate_key(mood)
        }
    
    def _get_compatible_genres(self, mood: str) -> List[str]:
        """Get genres compatible with a mood."""
        genre_map = {
            "energetic": ["house", "drum & bass", "trap", "techno"],
            "melancholic": ["lo-fi hip hop", "jazz", "soul", "ambient"],
            "aggressive": ["metal", "hardcore", "industrial", "trap"],
            "chill": ["downtempo", "chillout", "lounge", "ambient"],
            "mysterious": ["experimental", "dark ambient", "trip hop"],
            "uplifting": ["trance", "progressive house", "future bass"]
        }
        return genre_map.get(mood, ["electronic"])
    
    def _estimate_bpm(self, mood: str) -> float:
        """Estimate BPM based on mood."""
        bpm_ranges = {
            "energetic": (120, 140),
            "melancholic": (70, 90),
            "aggressive": (140, 180),
            "chill": (60, 90),
            "mysterious": (80, 110),
            "uplifting": (128, 138)
        }
        min_bpm, max_bpm = bpm_ranges.get(mood, (90, 120))
        return round(min_bpm + random.random() * (max_bpm - min_bpm), 1)
    
    def _estimate_key(self, mood: str) -> str:
        """Estimate musical key based on mood."""
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        modes = ["major", "minor"]
        
        # Melancholic and mysterious moods tend toward minor keys
        if mood in ["melancholic", "mysterious", "aggressive"]:
            mode = "minor"
        elif mood in ["uplifting", "energetic"]:
            mode = "major"
        else:
            mode = random.choice(modes)
        
        return f"{random.choice(keys)} {mode}"
    
    async def calculate_compatibility(
        self, 
        sample1_id: int, 
        sample2_id: int
    ) -> float:
        """Calculate compatibility between two samples."""
        analysis1 = await self.analyze_sample(sample1_id)
        analysis2 = await self.analyze_sample(sample2_id)
        
        # Simple compatibility calculation
        score = 0.0
        
        # Mood compatibility
        mood1 = analysis1.get("mood_primary", analysis1.get("mood"))
        mood2 = analysis2.get("mood_primary", analysis2.get("mood"))
        if mood1 == mood2:
            score += 0.4
        elif self._are_moods_compatible(mood1, mood2):
            score += 0.2
        
        # Energy compatibility (prefer similar energy levels)
        energy1 = analysis1.get("energy_level", analysis1.get("energy", 0.5))
        energy2 = analysis2.get("energy_level", analysis2.get("energy", 0.5))
        energy_diff = abs(energy1 - energy2)
        score += max(0, 0.3 - energy_diff)
        
        # BPM compatibility (prefer harmonically related BPMs)
        bpm_ratio = analysis1["bpm"] / analysis2["bpm"]
        if 0.95 <= bpm_ratio <= 1.05:  # Very close BPMs
            score += 0.3
        elif any(abs(bpm_ratio - r) < 0.05 for r in [0.5, 2.0, 0.75, 1.33]):
            # Harmonically related (half-time, double-time, etc.)
            score += 0.2
        
        return min(1.0, score)
    
    def _are_moods_compatible(self, mood1: str, mood2: str) -> bool:
        """Check if two moods are compatible."""
        compatible_pairs = {
            ("energetic", "uplifting"),
            ("melancholic", "chill"),
            ("mysterious", "chill"),
            ("aggressive", "energetic")
        }
        return (mood1, mood2) in compatible_pairs or (mood2, mood1) in compatible_pairs