"""
Example usage of VibeSearchService for vector-based sample search.

This demonstrates how to use the service for natural language sample discovery.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.services.embedding_service import EmbeddingService
from app.services.usage_tracking_service import UsageTrackingService
from app.services.vibe_search_service import VibeSearchService, SearchError
from app.core.config import settings


async def main():
    """Example usage of vibe search service."""

    # Setup database connection
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as db:
        # Initialize services
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Create vibe search service
        search_service = VibeSearchService(
            embedding_service=embedding_service,
            db=db
        )

        print("=" * 60)
        print("VIBE SEARCH SERVICE - EXAMPLE USAGE")
        print("=" * 60)

        # Example 1: Basic search
        print("\n[Example 1] Basic search for 'dark moody loop'")
        print("-" * 60)
        try:
            results = await search_service.search_by_vibe(
                query="dark moody loop",
                limit=5
            )

            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   BPM: {result.get('bpm', 'N/A')}")
                print(f"   Genre: {result.get('genre', 'N/A')}")
                print(f"   Similarity: {result['similarity']:.4f}")
                print(f"   Mood: {result.get('mood_primary', 'N/A')}")
                print()

        except SearchError as e:
            print(f"Search failed: {e.message}")

        # Example 2: Search with filters
        print("\n[Example 2] Search with BPM and energy filters")
        print("-" * 60)
        try:
            results = await search_service.search_by_vibe(
                query="upbeat energetic drum break",
                limit=5,
                filters={
                    "bpm_min": 120,
                    "bpm_max": 140,
                    "energy_min": 0.7
                }
            )

            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   BPM: {result.get('bpm', 'N/A')}")
                print(f"   Energy: {result.get('energy_level', 'N/A')}")
                print(f"   Similarity: {result['similarity']:.4f}")
                print()

        except SearchError as e:
            print(f"Search failed: {e.message}")

        # Example 3: Find similar samples
        print("\n[Example 3] Find samples similar to sample #1")
        print("-" * 60)
        try:
            results = await search_service.find_similar(
                sample_id=1,
                limit=3
            )

            print(f"Found {len(results)} similar samples:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   BPM: {result.get('bpm', 'N/A')}")
                print(f"   Genre: {result.get('genre', 'N/A')}")
                print(f"   Similarity: {result['similarity']:.4f}")
                print()

        except SearchError as e:
            print(f"Similar search failed: {e.message}")

        # Example 4: Multiple filter combinations
        print("\n[Example 4] Complex filtering - Hip-hop samples with specific vibe")
        print("-" * 60)
        try:
            results = await search_service.search_by_vibe(
                query="smooth jazz sample for sampling",
                limit=5,
                filters={
                    "genre": "hip-hop",
                    "bpm_min": 80,
                    "bpm_max": 100,
                    "danceability_min": 0.5
                }
            )

            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   BPM: {result.get('bpm', 'N/A')}")
                print(f"   Danceability: {result.get('danceability', 'N/A')}")
                print(f"   Similarity: {result['similarity']:.4f}")
                print()

        except SearchError as e:
            print(f"Search failed: {e.message}")

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
