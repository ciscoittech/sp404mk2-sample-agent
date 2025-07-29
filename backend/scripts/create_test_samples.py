"""
Create test sample data for development
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User
from app.models.sample import Sample
from app.core.security import get_password_hash
import random

async def create_test_data():
    async for db in get_db():
        # Create test user if not exists
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email="test@example.com",
                username="testuser",
                hashed_password=get_password_hash("testpass123"),
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Create test samples
        genres = ["hip-hop", "jazz", "electronic", "soul", "trap"]
        moods = ["chill", "energetic", "dark", "uplifting", "mysterious"]
        
        for i in range(50):
            sample = Sample(
                title=f"Sample {i+1} - {random.choice(moods)}",
                file_path=f"/fake/path/sample_{i+1}.wav",
                genre=random.choice(genres),
                bpm=random.randint(60, 180),
                musical_key=random.choice(["C", "D", "E", "F", "G", "A", "B"]) + random.choice(["", "m", "maj", "min"]),
                tags=[random.choice(moods), random.choice(["drums", "bass", "melody", "vocals", "fx"])],
                user_id=user.id
            )
            db.add(sample)
        
        await db.commit()
        print("Created 50 test samples")
        return

if __name__ == "__main__":
    asyncio.run(create_test_data())