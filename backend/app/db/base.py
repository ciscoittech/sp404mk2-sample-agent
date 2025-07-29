"""
Database base configuration
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from app.models import User, Sample, VibeAnalysis, Kit, KitSample  # noqa

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session