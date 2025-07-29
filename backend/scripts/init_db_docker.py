"""Initialize database with tables and sample data - Docker version."""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, '/app/backend')

# Set environment variables if not already set
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///./data/sp404.db')

from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base import Base
from app.db.init_db import init_db


async def main():
    """Initialize database."""
    print("Creating database tables...")
    
    # Create engine
    engine = create_async_engine(os.environ['DATABASE_URL'], echo=False)
    
    # Import all models to ensure they're registered
    import app.models  # This will import all models
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    
    # Initialize with sample data
    print("Creating sample data...")
    await init_db()
    print("Database initialization complete!")
    
    # Dispose of the engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())