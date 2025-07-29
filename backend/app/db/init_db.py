"""
Initialize database tables
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import engine, Base
from app.models import User, Sample, VibeAnalysis, Kit, KitSample, Batch  # Import all models to register them

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created")

if __name__ == "__main__":
    asyncio.run(init_db())