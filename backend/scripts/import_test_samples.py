#!/usr/bin/env python3
"""
Import test samples directly into the database
"""
import asyncio
from pathlib import Path
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append('/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.sample import Sample
from app.core.config import settings


async def import_test_samples():
    """Import test samples with mock AI analysis"""
    # Create database session
    engine = create_async_engine(settings.DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as db:
        # Test samples directory
        test_dir = Path("/app/test_batch_collection")
        
        if not test_dir.exists():
            print(f"Test directory not found: {test_dir}")
            return
        
        # Sample AI analysis results (would come from batch processor)
        sample_analyses = {
            "ambient_pad_D.wav": {
                "mood": ["calm", "ethereal", "spacious"],
                "genre": "ambient",
                "era": "modern",
                "energy_level": "low",
                "descriptors": ["atmospheric", "dreamy", "floating", "warm"],
                "best_use": "pad",
                "bpm": 80
            },
            "deep_bass_Bb.wav": {
                "mood": ["dark", "powerful", "groovy"],
                "genre": "hip-hop",
                "era": "2010s",
                "energy_level": "medium",
                "descriptors": ["deep", "punchy", "sub-heavy", "modern"],
                "best_use": "bass",
                "bpm": 90
            },
            "ethereal_pad_A.wav": {
                "mood": ["mystical", "peaceful", "introspective"],
                "genre": "ambient",
                "era": "2020s",
                "energy_level": "low",
                "descriptors": ["ethereal", "angelic", "soft", "evolving"],
                "best_use": "pad",
                "bpm": 75
            },
            "funky_drums_120bpm.wav": {
                "mood": ["energetic", "fun", "groovy"],
                "genre": "funk",
                "era": "1970s",
                "energy_level": "high",
                "descriptors": ["funky", "tight", "vintage", "punchy"],
                "best_use": "drums",
                "bpm": 120
            },
            "groovy_bass_C.wav": {
                "mood": ["confident", "smooth", "rhythmic"],
                "genre": "funk",
                "era": "1980s",
                "energy_level": "medium-high",
                "descriptors": ["groovy", "walking", "warm", "analog"],
                "best_use": "bass",
                "bpm": 105
            },
            "slow_drums_90bpm.wav": {
                "mood": ["laid-back", "chill", "contemplative"],
                "genre": "lo-fi hip-hop",
                "era": "2020s",
                "energy_level": "low-medium",
                "descriptors": ["dusty", "boom-bap", "vintage", "crunchy"],
                "best_use": "drums",
                "bpm": 90
            },
            "trap_drums_140bpm.wav": {
                "mood": ["aggressive", "intense", "modern"],
                "genre": "trap",
                "era": "2020s",
                "energy_level": "high",
                "descriptors": ["hard-hitting", "crisp", "rattling", "808-heavy"],
                "best_use": "drums",
                "bpm": 140
            },
            "warm_pad_F.wav": {
                "mood": ["nostalgic", "warm", "comforting"],
                "genre": "ambient",
                "era": "1990s",
                "energy_level": "low",
                "descriptors": ["analog", "lush", "evolving", "vintage"],
                "best_use": "pad",
                "bpm": 70
            }
        }
        
        imported_count = 0
        
        # Import each audio file
        for audio_file in test_dir.glob("*.wav"):
            filename = audio_file.name
            analysis = sample_analyses.get(filename, {})
            
            # Extract info from filename
            parts = filename.replace(".wav", "").split("_")
            if "bpm" in filename:
                # Extract BPM from filename like "funky_drums_120bpm.wav"
                for part in parts:
                    if "bpm" in part:
                        try:
                            bpm = int(part.replace("bpm", ""))
                            analysis["bpm"] = bpm
                        except:
                            pass
            
            # Extract key if in filename
            key = None
            for part in parts:
                if len(part) <= 2 and part[0].isupper():
                    key = part
                    break
            
            # Create sample
            sample = Sample(
                user_id=1,  # Demo user
                title=filename.replace("_", " ").replace(".wav", "").title(),
                file_path=str(audio_file),
                file_size=audio_file.stat().st_size,
                duration=4.0,  # Mock duration
                bpm=analysis.get("bpm"),
                musical_key=key,
                genre=analysis.get("genre"),
                tags=[analysis.get("genre", ""), analysis.get("best_use", "")] + analysis.get("descriptors", [])[:2],
                analyzed_at=datetime.utcnow(),
                extra_metadata={
                    'vibe_analysis': {
                        'mood_primary': analysis.get("mood", ["unknown"])[0],
                        'mood_tags': analysis.get("mood", []),
                        'era': analysis.get("era"),
                        'genre': analysis.get("genre"),
                        'energy_level': analysis.get("energy_level"),
                        'descriptors': analysis.get("descriptors", []),
                        'compatibility_tags': [],
                        'best_use': analysis.get("best_use"),
                        'confidence': 0.85,
                        'source': 'test_import'
                    }
                }
            )
            
            db.add(sample)
            imported_count += 1
            print(f"Imported: {filename}")
        
        # Commit all
        await db.commit()
        print(f"\nSuccessfully imported {imported_count} samples!")


if __name__ == "__main__":
    asyncio.run(import_test_samples())