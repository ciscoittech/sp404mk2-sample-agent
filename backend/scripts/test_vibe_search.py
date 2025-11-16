"""
Test script for vibe search functionality.

Tests embedding generation and vector search endpoints.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.embedding_service import EmbeddingService
from app.services.usage_tracking_service import UsageTrackingService
from app.db.base import AsyncSessionLocal


async def test_embedding_generation():
    """Test generating embeddings for sample text."""
    print("\n=== Testing Embedding Generation ===\n")

    async with AsyncSessionLocal() as db:
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Test single embedding
        text = "dark moody atmospheric loop"
        print(f"Input text: '{text}'")

        try:
            embedding = await embedding_service.generate_embedding(text)
            print(f"✅ Generated embedding: {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
            print(f"   Last 5 values: {embedding[-5:]}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

        # Test batch embeddings
        print("\n--- Testing Batch Embeddings ---\n")
        texts = [
            "energetic trap drums",
            "chill jazz piano",
            "aggressive 808 bass"
        ]
        print(f"Input texts: {texts}")

        try:
            embeddings = await embedding_service.generate_batch_embeddings(texts)
            print(f"✅ Generated {len(embeddings)} embeddings")
            for i, emb in enumerate(embeddings):
                print(f"   Embedding {i+1}: {len(emb)} dimensions")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("VIBE SEARCH SYSTEM TEST")
    print("="*60)

    # Test embedding generation
    success = await test_embedding_generation()

    if success:
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nNext Steps:")
        print("1. Start the FastAPI server: ./venv/bin/python backend/run.py")
        print("2. Test the API endpoint with curl (see below)")
        print("\nExample curl commands:")
        print("\n# Search by vibe")
        print('curl "http://localhost:8100/api/v1/search/vibe?query=dark%20moody%20loop&limit=5"')
        print("\n# Search with filters")
        print('curl "http://localhost:8100/api/v1/search/vibe?query=energetic%20drums&bpm_min=120&bpm_max=140&energy_min=0.7"')
        print("\n# Get similar samples")
        print('curl "http://localhost:8100/api/v1/search/similar/123?limit=10"')
        print("\n" + "="*60)
    else:
        print("\n" + "="*60)
        print("❌ TESTS FAILED")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
