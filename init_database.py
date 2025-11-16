#!/usr/bin/env python3
"""Initialize database from project root."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.db.base import engine, Base
from app.models import (
    User, Sample, VibeAnalysis, SampleEmbedding, Kit, KitSample, Batch,
    ApiUsage, UserPreference, YouTubeChannel, YouTubePlaylist, YouTubeVideo,
    ChannelCrawlHistory, YouTubeQuotaUsage, SP404Export, SP404ExportSample
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
