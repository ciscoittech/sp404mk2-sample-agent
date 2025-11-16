#!/usr/bin/env python3
"""Test script for OpenRouter embedding API."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import EmbeddingService
from app.services.usage_tracking_service import UsageTrackingService
from app.core.database import AsyncSessionLocal


async def test_api():
    try:
        async with AsyncSessionLocal() as session:
            usage_service = UsageTrackingService(session)
            embedding_service = EmbeddingService(usage_service)

            print("Testing OpenRouter API with nomic-embed-text-v1.5...")
            vector = await embedding_service.generate_embedding("dark moody loop jazz sample")

            print(f"✅ API working! Generated {len(vector)}-dim vector")
            print(f"First 5 values: {vector[:5]}")
            print(f"Vector magnitude: {sum(x**2 for x in vector)**0.5:.4f}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api())
