"""Initialize database with tables and sample data."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.db.base import Base, engine
from backend.app.db.init_db import init_db


async def main():
    """Initialize database."""
    print("Creating database tables...")
    
    # Import all models to ensure they're registered
    from backend.app.models import User, Sample, VibeAnalysis, Kit, KitSample  # noqa
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    
    # Initialize with sample data
    print("Creating sample data...")
    await init_db()
    print("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())