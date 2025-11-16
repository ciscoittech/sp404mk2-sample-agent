# EmbeddingService Integration Guide

## Quick Start

### 1. Add to API Dependencies

```python
# backend/app/api/dependencies.py
from app.services.embedding_service import EmbeddingService
from app.services.usage_tracking_service import UsageTrackingService

async def get_embedding_service(
    db: AsyncSession = Depends(get_db)
) -> EmbeddingService:
    """Dependency for embedding service."""
    usage_service = UsageTrackingService(db)
    return EmbeddingService(usage_service)
```

### 2. Create API Endpoint

```python
# backend/app/api/v1/endpoints/embeddings.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.embedding_service import EmbeddingService, EmbeddingError
from app.api.dependencies import get_embedding_service

router = APIRouter()


class EmbeddingRequest(BaseModel):
    text: str


class BatchEmbeddingRequest(BaseModel):
    texts: List[str]


@router.post("/embeddings/generate")
async def generate_embedding(
    request: EmbeddingRequest,
    service: EmbeddingService = Depends(get_embedding_service)
):
    """Generate embedding for a single text."""
    try:
        embedding = await service.generate_embedding(request.text)
        return {
            "embedding": embedding,
            "dimensions": len(embedding)
        }
    except EmbeddingError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/embeddings/batch")
async def generate_batch_embeddings(
    request: BatchEmbeddingRequest,
    service: EmbeddingService = Depends(get_embedding_service)
):
    """Generate embeddings for multiple texts."""
    try:
        embeddings = await service.generate_batch_embeddings(request.texts)
        return {
            "embeddings": embeddings,
            "count": len(embeddings),
            "dimensions": len(embeddings[0]) if embeddings else 0
        }
    except EmbeddingError as e:
        raise HTTPException(status_code=500, detail=e.message)
```

### 3. Use in Sample Processing

```python
# backend/app/services/sample_service.py
from app.services.embedding_service import EmbeddingService

class SampleService:
    def __init__(
        self,
        db: AsyncSession,
        embedding_service: EmbeddingService
    ):
        self.db = db
        self.embedding_service = embedding_service

    async def generate_sample_embedding(self, sample_id: int):
        """Generate and store embedding for a sample."""
        # Get sample
        sample = await self.db.get(Sample, sample_id)
        if not sample:
            raise ValueError("Sample not found")

        # Build text representation
        text_parts = []
        if sample.title:
            text_parts.append(f"Title: {sample.title}")
        if sample.description:
            text_parts.append(f"Description: {sample.description}")
        if sample.tags:
            text_parts.append(f"Tags: {', '.join(sample.tags)}")
        if sample.genre:
            text_parts.append(f"Genre: {sample.genre}")

        text = " | ".join(text_parts)

        # Generate embedding
        embedding = await self.embedding_service.generate_embedding(text)

        # Store in database (assuming you have a vector column)
        sample.embedding = embedding
        await self.db.commit()

        return embedding

    async def search_similar_samples(
        self,
        query_text: str,
        limit: int = 10,
        threshold: float = 0.7
    ):
        """Search for samples similar to query text."""
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query_text)

        # Use Turso's vector_distance function
        # This is a simplified example - adjust for your schema
        from sqlalchemy import text as sql_text

        query = sql_text("""
            SELECT
                id,
                title,
                description,
                vector_distance(embedding, :query_embedding) as distance
            FROM samples
            WHERE embedding IS NOT NULL
            ORDER BY distance ASC
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "query_embedding": str(query_embedding),
                "limit": limit
            }
        )

        return result.fetchall()
```

### 4. Batch Process Existing Samples

```python
# backend/scripts/generate_embeddings.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import AsyncSessionLocal
from app.services.embedding_service import EmbeddingService
from app.services.usage_tracking_service import UsageTrackingService
from app.models.sample import Sample

async def generate_all_embeddings():
    """Generate embeddings for all samples in batches."""
    async with AsyncSessionLocal() as db:
        # Initialize services
        usage_service = UsageTrackingService(db)
        embedding_service = EmbeddingService(usage_service)

        # Get all samples without embeddings
        result = await db.execute(
            select(Sample).where(Sample.embedding.is_(None))
        )
        samples = result.scalars().all()

        print(f"Found {len(samples)} samples without embeddings")

        # Process in batches of 50
        batch_size = 50
        for i in range(0, len(samples), batch_size):
            batch = samples[i:i + batch_size]

            # Build texts
            texts = []
            for sample in batch:
                parts = []
                if sample.title:
                    parts.append(f"Title: {sample.title}")
                if sample.description:
                    parts.append(f"Description: {sample.description}")
                if sample.tags:
                    parts.append(f"Tags: {', '.join(sample.tags)}")
                texts.append(" | ".join(parts))

            # Generate embeddings
            embeddings = await embedding_service.generate_batch_embeddings(texts)

            # Update samples
            for sample, embedding in zip(batch, embeddings):
                sample.embedding = embedding

            await db.commit()

            print(f"Processed {i + len(batch)}/{len(samples)} samples")

if __name__ == "__main__":
    asyncio.run(generate_all_embeddings())
```

## Integration with Turso LibSQL

### 1. Add Vector Column to Sample Model

```python
# backend/app/models/sample.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import JSON

class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    tags = Column(JSON)

    # Vector embedding (stored as JSON array)
    embedding = Column(JSON, nullable=True)
```

### 2. Create Migration

```python
# alembic/versions/xxx_add_embedding_column.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('samples',
        sa.Column('embedding', sa.JSON(), nullable=True)
    )

def downgrade():
    op.drop_column('samples', 'embedding')
```

### 3. Use Vector Search in Turso

```python
# Example: Vector similarity search
from sqlalchemy import text as sql_text

async def search_by_similarity(
    db: AsyncSession,
    query_embedding: List[float],
    limit: int = 10
):
    """Search samples using vector similarity."""
    query = sql_text("""
        SELECT
            id,
            title,
            description,
            tags,
            vector_distance(embedding, :query_vec) as similarity
        FROM samples
        WHERE embedding IS NOT NULL
        ORDER BY similarity ASC
        LIMIT :limit
    """)

    result = await db.execute(
        query,
        {
            "query_vec": str(query_embedding),
            "limit": limit
        }
    )

    return result.fetchall()
```

## Cost Management

### Monitor Embedding Costs

```python
# Get embedding generation costs
from app.services.usage_tracking_service import UsageTrackingService

async def get_embedding_stats(db: AsyncSession):
    """Get embedding usage statistics."""
    usage_service = UsageTrackingService(db)

    summary = await usage_service.get_usage_summary()

    embedding_ops = summary['by_operation'].get('embedding_generation', {})

    print(f"Embedding operations: {embedding_ops.get('count', 0)}")
    print(f"Total cost: ${embedding_ops.get('cost', 0):.6f}")
```

### Estimate Costs Before Processing

```python
# Estimate cost for batch processing
num_samples = 10000
avg_tokens_per_sample = 130  # ~100 words
total_tokens = num_samples * avg_tokens_per_sample

# $0.02 per 1M tokens
cost_per_token = 0.02 / 1_000_000
estimated_cost = total_tokens * cost_per_token

print(f"Estimated cost for {num_samples} samples: ${estimated_cost:.6f}")
# Output: Estimated cost for 10000 samples: $0.026000
```

## Testing

```python
# tests/services/test_embedding_service.py
import pytest
from app.services.embedding_service import EmbeddingService, EmbeddingError

@pytest.mark.asyncio
async def test_generate_embedding(embedding_service):
    """Test single embedding generation."""
    text = "Test sample description"
    embedding = await embedding_service.generate_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_generate_batch_embeddings(embedding_service):
    """Test batch embedding generation."""
    texts = ["Sample 1", "Sample 2", "Sample 3"]
    embeddings = await embedding_service.generate_batch_embeddings(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)


@pytest.mark.asyncio
async def test_empty_text_error(embedding_service):
    """Test error handling for empty text."""
    with pytest.raises(EmbeddingError) as exc_info:
        await embedding_service.generate_embedding("")

    assert "empty" in str(exc_info.value).lower()
```

## Performance Tips

1. **Batch Processing**: Always use `generate_batch_embeddings()` for multiple texts
   - 50% faster than individual calls
   - Lower API overhead

2. **Caching**: Cache embeddings for frequently searched queries
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def get_cached_embedding(text: str):
       # Cache frequently used embeddings
       pass
   ```

3. **Async Processing**: Process embeddings in background
   ```python
   import asyncio

   async def process_embeddings_background(sample_ids: List[int]):
       tasks = [generate_sample_embedding(sid) for sid in sample_ids]
       await asyncio.gather(*tasks)
   ```

---

**Ready to Use**: Service is fully implemented and ready for integration
**Next Steps**: Add API endpoints, create migrations, write tests
