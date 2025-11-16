# EmbeddingService Integration Guide

## Overview

This guide shows how to integrate the `EmbeddingService` (once created) into the embedding generation script.

## Required EmbeddingService Interface

The `EmbeddingService` must implement the following interface:

```python
# backend/app/services/embedding_service.py

from typing import List
from app.services.openrouter_service import OpenRouterService
from app.services.usage_tracking_service import UsageTrackingService

class EmbeddingService:
    """
    Service for generating text embeddings using OpenRouter API.

    Uses text-embedding-3-small model for semantic vector generation.
    """

    def __init__(self):
        """Initialize embedding service with OpenRouter client."""
        # Initialize dependencies (usage tracking, etc.)
        pass

    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Generate embedding vector for input text.

        Args:
            text: Text to embed (max ~8,000 tokens)
            model: Embedding model to use

        Returns:
            List of 1,536 floats (embedding vector)

        Raises:
            OpenRouterError: On API failures
            ValueError: On invalid input
        """
        # Call OpenRouter API
        # Return embedding as List[float]
        pass

    async def estimate_cost(self, text: str) -> float:
        """
        Estimate cost for embedding generation.

        Args:
            text: Text to embed

        Returns:
            Estimated cost in USD

        Note:
            text-embedding-3-small: ~$0.02 per 1M tokens
        """
        tokens = len(text) // 4  # Rough estimate
        cost = (tokens / 1_000_000) * 0.02
        return cost
```

## Integration Steps

### Step 1: Import EmbeddingService

**File**: `backend/scripts/generate_embeddings.py`
**Line**: 48

```python
# Current (TODO comment):
# TODO: Import EmbeddingService once created by other agent
# from app.services.embedding_service import EmbeddingService

# Change to:
from app.services.embedding_service import EmbeddingService
```

### Step 2: Initialize EmbeddingService

**File**: `backend/scripts/generate_embeddings.py`
**Line**: 381-383

```python
# Current:
# Initialize services
# TODO: Initialize EmbeddingService once created
# embedding_service = EmbeddingService()

# Change to:
# Initialize services
embedding_service = EmbeddingService()
```

### Step 3: Uncomment Embedding Generation Logic

**File**: `backend/scripts/generate_embeddings.py`
**Function**: `generate_embeddings_batch`
**Lines**: 309-344

```python
# Current:
if dry_run:
    # Estimate tokens and cost
    estimated_tokens = len(source_text) // 4
    estimated_cost = (estimated_tokens / 1_000_000) * 0.02
    total_cost += estimated_cost
    successful += 1
else:
    # Generate embedding via API
    # TODO: Replace with actual EmbeddingService call
    # embedding = await embedding_service.generate_embedding(source_text)
    # For now, raise NotImplementedError
    raise NotImplementedError(
        "EmbeddingService not yet implemented. "
        "Waiting for embedding service to be created by other agent."
    )

# Change to:
if dry_run:
    # Estimate tokens and cost
    estimated_tokens = len(source_text) // 4
    estimated_cost = (estimated_tokens / 1_000_000) * 0.02
    total_cost += estimated_cost
    successful += 1
else:
    # Generate embedding via API
    embedding = await embedding_service.generate_embedding(source_text)

    # Validate embedding
    if not validate_embedding(embedding):
        raise ValueError("Invalid embedding generated")

    # Store in Turso
    success = await store_embedding_in_turso(sample.id, embedding, source_text)
    if not success:
        raise Exception("Failed to store embedding")

    # Track progress
    cost = await embedding_service.estimate_cost(source_text)
    progress.update(sample.id, cost=cost, tokens=len(source_text) // 4)
    total_cost += cost
    successful += 1
```

### Step 4: Update Type Hint

**File**: `backend/scripts/generate_embeddings.py`
**Line**: 284

```python
# Current:
async def generate_embeddings_batch(
    samples: List[Tuple[Sample, Optional[VibeAnalysis]]],
    embedding_service,  # TODO: Type hint once EmbeddingService is created
    progress: ProgressTracker,
    dry_run: bool = False
) -> Tuple[int, int, float]:

# Change to:
async def generate_embeddings_batch(
    samples: List[Tuple[Sample, Optional[VibeAnalysis]]],
    embedding_service: EmbeddingService,
    progress: ProgressTracker,
    dry_run: bool = False
) -> Tuple[int, int, float]:
```

### Step 5: Pass EmbeddingService to Batch Function

**File**: `backend/scripts/generate_embeddings.py`
**Lines**: 426-430

```python
# Current:
# TODO: Uncomment when EmbeddingService is ready
# successful, failed, batch_cost = await generate_embeddings_batch(
#     samples, embedding_service, progress, dry_run
# )

# For now, just do dry run simulation
successful = len(samples)
failed = 0
batch_cost = 0.0
for sample, vibe in samples:
    source_text = create_embedding_source_text(sample, vibe)
    estimated_tokens = len(source_text) // 4
    batch_cost += (estimated_tokens / 1_000_000) * 0.02

# Change to:
successful, failed, batch_cost = await generate_embeddings_batch(
    samples, embedding_service, progress, dry_run
)
```

## Complete Integration Diff

```diff
--- a/backend/scripts/generate_embeddings.py
+++ b/backend/scripts/generate_embeddings.py
@@ -45,8 +45,7 @@ from app.models.sample import Sample
 from app.models.vibe_analysis import VibeAnalysis
 from app.db.turso import get_turso_client

-# TODO: Import EmbeddingService once created by other agent
-# from app.services.embedding_service import EmbeddingService
+from app.services.embedding_service import EmbeddingService

 console = Console()

@@ -281,7 +280,7 @@ async def store_embedding_in_turso(

 async def generate_embeddings_batch(
     samples: List[Tuple[Sample, Optional[VibeAnalysis]]],
-    embedding_service,  # TODO: Type hint once EmbeddingService is created
+    embedding_service: EmbeddingService,
     progress: ProgressTracker,
     dry_run: bool = False
 ) -> Tuple[int, int, float]:
@@ -310,31 +309,23 @@ async def generate_embeddings_batch(
                 console.print(f"[dim]Sample {sample.id}: ~{estimated_tokens} tokens, ~${estimated_cost:.6f}[/dim]")
             else:
                 # Generate embedding via API
-                # TODO: Replace with actual EmbeddingService call
-                # embedding = await embedding_service.generate_embedding(source_text)
-                # For now, raise NotImplementedError
-                raise NotImplementedError(
-                    "EmbeddingService not yet implemented. "
-                    "Waiting for embedding service to be created by other agent."
-                )
+                embedding = await embedding_service.generate_embedding(source_text)

                 # Validate embedding
-                # if not validate_embedding(embedding):
-                #     raise ValueError("Invalid embedding generated")
+                if not validate_embedding(embedding):
+                    raise ValueError("Invalid embedding generated")

                 # Store in Turso
-                # success = await store_embedding_in_turso(sample.id, embedding, source_text)
-                # if not success:
-                #     raise Exception("Failed to store embedding")
+                success = await store_embedding_in_turso(sample.id, embedding, source_text)
+                if not success:
+                    raise Exception("Failed to store embedding")

                 # Track progress
-                # cost = 0.00002  # Approximate cost per embedding
-                # progress.update(sample.id, cost=cost, tokens=len(source_text) // 4)
-                # total_cost += cost
-                # successful += 1
+                cost = await embedding_service.estimate_cost(source_text)
+                progress.update(sample.id, cost=cost, tokens=len(source_text) // 4)
+                total_cost += cost
+                successful += 1

         except Exception as e:
             console.print(f"[red]Failed to process sample {sample.id}: {e}[/red]")
@@ -378,8 +369,7 @@ async def process_all_samples(
     AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

     # Initialize services
-    # TODO: Initialize EmbeddingService once created
-    # embedding_service = EmbeddingService()
+    embedding_service = EmbeddingService()

     # Get total sample count
     async with AsyncSessionLocal() as session:
@@ -423,18 +413,9 @@ async def process_all_samples(
                     sample_ids=sample_ids
                 )

                 if not samples:
                     break

                 # Process batch
-                # TODO: Uncomment when EmbeddingService is ready
-                # successful, failed, batch_cost = await generate_embeddings_batch(
-                #     samples, embedding_service, progress, dry_run
-                # )
-
-                # For now, just do dry run simulation
-                successful = len(samples)
-                failed = 0
-                batch_cost = 0.0
-                for sample, vibe in samples:
-                    source_text = create_embedding_source_text(sample, vibe)
-                    estimated_tokens = len(source_text) // 4
-                    batch_cost += (estimated_tokens / 1_000_000) * 0.02
+                successful, failed, batch_cost = await generate_embeddings_batch(
+                    samples, embedding_service, progress, dry_run
+                )

                 total_successful += successful
```

## Testing After Integration

### 1. Test with Small Batch

```bash
# Test with 10 samples
python backend/scripts/generate_embeddings.py --sample-ids 1-10
```

**Expected Output**:
```
Processing 10 specific samples
Using database: /path/to/backend/sp404_samples.db
╭─────────────────────────────────────────────────── Configuration ──────────────────────────────────────────────────────╮
│ Embedding Generation                                                                                                   │
│                                                                                                                        │
│ Total samples: 10                                                                                                      │
│ Last processed: 0                                                                                                      │
│ Resume from: 1                                                                                                         │
│ Batch size: 100                                                                                                        │
│ Previous cost: $0.0000                                                                                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  Processed 10/10 ($0.0003) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:05
    Embedding Generation Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric          ┃ Value     ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Total Samples   │ 10        │
│ Successful      │ 10        │
│ Failed          │ 0         │
│ Success Rate    │ 100.0%    │
│ Total Cost      │ $0.0003   │
│ Avg Cost/Sample │ $0.000032 │
└─────────────────┴───────────┘
```

### 2. Verify Turso Storage

```python
from app.db.turso import get_turso_client

turso = get_turso_client()

# Count embeddings
result = turso.query("SELECT COUNT(*) FROM sample_embeddings")
print(f"Total embeddings: {result[0]}")

# Check first embedding
result = turso.query(
    "SELECT sample_id, LENGTH(vibe_vector), embedding_source FROM sample_embeddings LIMIT 1"
)
print(f"Sample ID: {result[0]['sample_id']}")
print(f"Vector size: {result[0]['LENGTH(vibe_vector)']} bytes")
print(f"Source text: {result[0]['embedding_source'][:100]}...")
```

### 3. Process Full Database

```bash
# Generate embeddings for all 2,437 samples
python backend/scripts/generate_embeddings.py --all
```

**Expected Time**: 3-5 minutes
**Expected Cost**: ~$0.08

## Troubleshooting

### Issue: "Module 'embedding_service' not found"

**Solution**: Ensure EmbeddingService is created at:
```
backend/app/services/embedding_service.py
```

### Issue: "EmbeddingService missing 'generate_embedding' method"

**Solution**: Verify EmbeddingService implements required interface:
```python
async def generate_embedding(self, text: str) -> List[float]
```

### Issue: "Invalid embedding dimensions"

**Solution**: Check EmbeddingService returns 1,536 floats:
```python
embedding = await service.generate_embedding("test")
assert len(embedding) == 1536
```

### Issue: "Turso insert failed"

**Solution**: Verify table exists:
```sql
-- Create table if missing
CREATE TABLE IF NOT EXISTS sample_embeddings (
    sample_id INTEGER PRIMARY KEY,
    vibe_vector BLOB NOT NULL,
    embedding_source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Optimization

### Batch API Calls

If EmbeddingService supports batch embedding generation:

```python
# Add to EmbeddingService
async def generate_embeddings_batch(
    self,
    texts: List[str]
) -> List[List[float]]:
    """Generate embeddings for multiple texts in one API call."""
    pass
```

This could reduce processing time from 5 minutes to <1 minute.

### Parallel Processing

For even faster processing:

```python
import asyncio

# Process multiple batches in parallel
tasks = [
    generate_embeddings_batch(batch, service, progress)
    for batch in batches
]
results = await asyncio.gather(*tasks)
```

## Summary

Integration requires:
1. ✅ Remove TODO comments (5 locations)
2. ✅ Uncomment working code
3. ✅ Add type hint for `embedding_service`
4. ✅ Test with small batch
5. ✅ Verify Turso storage
6. ✅ Process full database

**Total Code Changes**: ~30 lines (removing comments/TODOs)
**Testing Time**: ~5 minutes
**Full Processing**: ~5 minutes for 2,437 samples

Once integrated, the script will be fully functional and ready for production use.
