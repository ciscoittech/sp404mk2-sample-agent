"""
Populate database with demo samples for testing
"""
import asyncio
import uuid
import sys
import os
import json
from datetime import datetime
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, AsyncSessionLocal
from app.db.base import Base
from app.models import User, Sample, VibeAnalysis


async def create_demo_samples():
    """Create demo samples with vibe analysis"""
    async with AsyncSessionLocal() as db:
        # First, check if we have a demo user
        result = await db.execute(
            text("SELECT id FROM users WHERE email = 'demo@example.com'")
        )
        user = result.fetchone()
        
        if not user:
            print("Creating demo user...")
            await db.execute(
                text("""
                    INSERT INTO users (email, username, hashed_password, is_active)
                    VALUES ('demo@example.com', 'demo', 'hashed_password_here', 1)
                """)
            )
            await db.commit()
            
            result = await db.execute(
                text("SELECT id FROM users WHERE email = 'demo@example.com'")
            )
            user = result.fetchone()
        
        user_id = user[0]
        print(f"Using user ID: {user_id}")
        
        # Demo samples data
        demo_samples = [
            {
                "title": "Vintage Jazz Drums",
                "genre": "Jazz",
                "bpm": 120.0,
                "musical_key": "Am",
                "tags": ["drums", "jazz", "vintage", "120bpm"],
                "vibe": {
                    "mood": ["warm", "groovy", "nostalgic"],
                    "energy": "medium",
                    "era": "1960s",
                    "texture": "analog warmth with tape saturation",
                    "color": "#8B4513"
                }
            },
            {
                "title": "Trap Hi-Hats",
                "genre": "Hip-Hop",
                "bpm": 140.0,
                "musical_key": None,
                "tags": ["drums", "trap", "hi-hats", "modern"],
                "vibe": {
                    "mood": ["aggressive", "sharp", "modern"],
                    "energy": "high",
                    "era": "2020s",
                    "texture": "crispy digital with slight distortion",
                    "color": "#FF0000"
                }
            },
            {
                "title": "Soul Piano Chord",
                "genre": "Soul",
                "bpm": 85.0,
                "musical_key": "C",
                "tags": ["piano", "soul", "chord", "melodic"],
                "vibe": {
                    "mood": ["soulful", "warm", "emotional"],
                    "energy": "low",
                    "era": "1970s",
                    "texture": "rich harmonic content with vintage reverb",
                    "color": "#FFD700"
                }
            },
            {
                "title": "Boom Bap Kick",
                "genre": "Hip-Hop",
                "bpm": 90.0,
                "musical_key": None,
                "tags": ["drums", "kick", "boom-bap", "classic"],
                "vibe": {
                    "mood": ["punchy", "gritty", "classic"],
                    "energy": "medium",
                    "era": "1990s",
                    "texture": "compressed with vinyl character",
                    "color": "#4B0082"
                }
            },
            {
                "title": "Ambient Pad",
                "genre": "Electronic",
                "bpm": None,
                "musical_key": "Dm",
                "tags": ["pad", "ambient", "atmospheric", "electronic"],
                "vibe": {
                    "mood": ["ethereal", "spacious", "dreamy"],
                    "energy": "low",
                    "era": "modern",
                    "texture": "lush reverb with subtle movement",
                    "color": "#87CEEB"
                }
            }
        ]
        
        # Insert samples
        for sample_data in demo_samples:
            # Check if sample already exists
            result = await db.execute(
                text("SELECT id FROM samples WHERE title = :title"),
                {"title": sample_data["title"]}
            )
            existing = result.fetchone()
            
            if existing:
                print(f"Sample {sample_data['title']} already exists, skipping...")
                continue
            
            # Create sample
            sample_id = str(uuid.uuid4())
            file_path = f"uploads/{user_id}/{sample_id}.wav"
            
            await db.execute(
                text("""
                    INSERT INTO samples (
                        user_id, title, file_path, file_size,
                        duration, genre, bpm, musical_key, tags, created_at
                    ) VALUES (
                        :user_id, :title, :file_path, :file_size,
                        :duration, :genre, :bpm, :musical_key, :tags, :created_at
                    )
                """),
                {
                    "user_id": user_id,
                    "title": sample_data["title"],
                    "file_path": file_path,
                    "file_size": 1024 * 1024,  # 1MB dummy size
                    "duration": 2.5,  # 2.5 seconds dummy duration
                    "genre": sample_data["genre"],
                    "bpm": sample_data["bpm"],
                    "musical_key": sample_data["musical_key"],
                    "tags": json.dumps(sample_data["tags"]),
                    "created_at": datetime.utcnow()
                }
            )
            
            # Get the newly created sample ID
            result = await db.execute(
                text("SELECT id FROM samples WHERE title = :title AND user_id = :user_id"),
                {"title": sample_data["title"], "user_id": user_id}
            )
            sample_row = result.fetchone()
            sample_id = sample_row[0]
            
            # Create vibe analysis
            vibe_data = sample_data["vibe"]
            # Map energy levels to 0-1 scale
            energy_map = {"low": 0.3, "medium": 0.6, "high": 0.9}
            energy_level = energy_map.get(vibe_data["energy"], 0.5)
            
            await db.execute(
                text("""
                    INSERT INTO vibe_analyses (
                        sample_id, mood_primary, mood_secondary, energy_level,
                        texture_tags, characteristics, confidence_score,
                        model_version, created_at
                    ) VALUES (
                        :sample_id, :mood_primary, :mood_secondary, :energy_level,
                        :texture_tags, :characteristics, :confidence_score,
                        :model_version, :created_at
                    )
                """),
                {
                    "sample_id": sample_id,
                    "mood_primary": vibe_data["mood"][0] if vibe_data["mood"] else "neutral",
                    "mood_secondary": vibe_data["mood"][1] if len(vibe_data["mood"]) > 1 else None,
                    "energy_level": energy_level,
                    "texture_tags": json.dumps([vibe_data["texture"]]),
                    "characteristics": json.dumps({
                        "era": vibe_data["era"],
                        "color": vibe_data["color"],
                        "all_moods": vibe_data["mood"]
                    }),
                    "confidence_score": 0.85,
                    "model_version": "demo-v1",
                    "created_at": datetime.utcnow()
                }
            )
            
            print(f"✅ Created sample: {sample_data['title']}")
        
        await db.commit()
        print("\n✅ Demo samples created successfully!")


if __name__ == "__main__":
    asyncio.run(create_demo_samples())