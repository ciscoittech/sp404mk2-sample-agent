"""
Example usage of EmbeddingService for vector search.

This demonstrates how to use the EmbeddingService to generate embeddings
for text-based semantic search.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding_service import EmbeddingService, EmbeddingError
from app.services.usage_tracking_service import UsageTrackingService
from app.db.base import AsyncSessionLocal


async def example_single_embedding():
    """Example: Generate embedding for a single text."""
    print("\n=== Example 1: Single Embedding ===")

    async with AsyncSessionLocal() as db:
        # Initialize services
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Generate embedding for a sample description
        text = "Vintage drum break with hard-hitting kick and crisp snare"

        try:
            embedding = await embedding_service.generate_embedding(text)

            print(f"Input: {text}")
            print(f"Generated embedding with {len(embedding)} dimensions")
            print(f"First 5 values: {embedding[:5]}")
            print("✅ Success!")

        except EmbeddingError as e:
            print(f"❌ Error: {e.message}")
            if e.status_code:
                print(f"   Status code: {e.status_code}")


async def example_batch_embeddings():
    """Example: Generate embeddings for multiple texts at once."""
    print("\n=== Example 2: Batch Embeddings ===")

    async with AsyncSessionLocal() as db:
        # Initialize services
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Multiple sample descriptions
        texts = [
            "808 bass drop with sub frequencies",
            "Jazzy piano loop in C minor",
            "Vocal chop with reverb and delay",
            "Analog synth pad warm atmospheric",
            "Trap hi-hat roll pattern 140 BPM"
        ]

        try:
            embeddings = await embedding_service.generate_batch_embeddings(texts)

            print(f"Generated {len(embeddings)} embeddings")
            for i, (text, emb) in enumerate(zip(texts, embeddings)):
                print(f"  {i+1}. {text[:50]}: {len(emb)} dims")

            print("✅ Success!")

        except EmbeddingError as e:
            print(f"❌ Error: {e.message}")


async def example_semantic_search():
    """Example: Use embeddings for semantic search."""
    print("\n=== Example 3: Semantic Search ===")

    async with AsyncSessionLocal() as db:
        # Initialize services
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Search query
        query = "hard hitting drums"

        # Sample library (in production, these would be in database)
        samples = [
            "Vintage drum break with punchy kick",
            "Soft ambient pad texture",
            "Aggressive trap snare",
            "Mellow guitar pluck",
            "Heavy 808 bass hit"
        ]

        try:
            # Generate embedding for query
            query_embedding = await embedding_service.generate_embedding(query)

            # Generate embeddings for all samples
            sample_embeddings = await embedding_service.generate_batch_embeddings(samples)

            # Calculate cosine similarity (simplified)
            print(f"Query: '{query}'")
            print("\nTop matches:")

            # In production, use libsql vector_distance() or numpy
            # This is just a demonstration
            for i, sample in enumerate(samples):
                # You would calculate similarity here
                print(f"  - {sample}")

            print("✅ Success!")

        except EmbeddingError as e:
            print(f"❌ Error: {e.message}")


async def example_error_handling():
    """Example: Proper error handling."""
    print("\n=== Example 4: Error Handling ===")

    async with AsyncSessionLocal() as db:
        # Initialize services
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Test with empty string
        try:
            embedding = await embedding_service.generate_embedding("")
        except EmbeddingError as e:
            print(f"✅ Caught empty text error: {e.message}")

        # Test with empty list
        try:
            embeddings = await embedding_service.generate_batch_embeddings([])
        except EmbeddingError as e:
            print(f"✅ Caught empty list error: {e.message}")

        # Test with all empty strings
        try:
            embeddings = await embedding_service.generate_batch_embeddings(["", "  ", "\n"])
        except EmbeddingError as e:
            print(f"✅ Caught all-empty error: {e.message}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("EmbeddingService Usage Examples")
    print("=" * 60)

    await example_single_embedding()
    await example_batch_embeddings()
    await example_semantic_search()
    await example_error_handling()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
