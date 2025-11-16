# Embeddings Generation Script - Usage Guide

## Overview

The `generate_embeddings.py` script processes all samples in your PostgreSQL/SQLite database and generates vector embeddings for semantic search using OpenRouter's text-embedding-3-small model.

## Prerequisites

### 1. OpenRouter API Key

The script uses OpenRouter API for embedding generation. Ensure your `.env` file contains:

```bash
OPENROUTER_API_KEY=your_api_key_here
```

Get your API key from: https://openrouter.ai/keys

### 2. Turso Database Credentials

The script stores embeddings in a Turso (LibSQL) database for edge-distributed vector search. Add to your `.env`:

```bash
TURSO_DATABASE_URL=libsql://your-database-name.turso.io
TURSO_AUTH_TOKEN=your_turso_auth_token_here
```

**Setup Turso:**

```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Create database
turso db create sp404-samples

# Get database URL
turso db show sp404-samples --url

# Create auth token
turso db tokens create sp404-samples

# Create embeddings table
turso db shell sp404-samples < backend/scripts/create_embeddings_table.sql
```

**Create embeddings table schema:**

```sql
-- backend/scripts/create_embeddings_table.sql
CREATE TABLE IF NOT EXISTS sample_embeddings (
    sample_id INTEGER PRIMARY KEY,
    vibe_vector BLOB NOT NULL,
    embedding_source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sample_embeddings_created ON sample_embeddings(created_at);
```

### 3. Sample Data

Ensure your database has samples with vibe analysis. Check sample count:

```bash
cd backend
sqlite3 sp404_samples.db "SELECT COUNT(*) FROM samples;"
sqlite3 sp404_samples.db "SELECT COUNT(*) FROM vibe_analyses;"
```

## Usage

### Cost Estimation (Dry Run)

**Recommended first step** - estimate costs before running:

```bash
# Estimate cost for all samples
python backend/scripts/generate_embeddings.py --dry-run --all

# Estimate cost for specific samples
python backend/scripts/generate_embeddings.py --dry-run --sample-ids 1-100
```

**Expected Output:**

```
Cost Estimation Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric          ┃ Value     ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Total Samples   │ 2,437     │
│ Successful      │ 2,437     │
│ Failed          │ 0         │
│ Success Rate    │ 100.0%    │
│ Total Cost      │ $0.0790   │
│ Avg Cost/Sample │ $0.000032 │
└─────────────────┴───────────┘
```

### Generate Embeddings

#### Process All Samples

```bash
python backend/scripts/generate_embeddings.py --all
```

#### Process Specific Sample IDs

```bash
# Single samples
python backend/scripts/generate_embeddings.py --sample-ids 1,2,3,10,25

# Ranges
python backend/scripts/generate_embeddings.py --sample-ids 100-200

# Mixed
python backend/scripts/generate_embeddings.py --sample-ids 1,5,10-20,100-200
```

#### Resume from Checkpoint

If the script was interrupted, resume from the last processed sample:

```bash
python backend/scripts/generate_embeddings.py --resume
```

Progress is saved to: `backend/scripts/embeddings_progress.json`

#### Reset and Start Fresh

```bash
python backend/scripts/generate_embeddings.py --reset --all
```

## Progress Tracking

The script automatically saves progress after each batch to `embeddings_progress.json`:

```json
{
  "last_processed_id": 523,
  "total_processed": 523,
  "total_cost_usd": 0.0167,
  "total_tokens": 130250,
  "failures": [],
  "started_at": "2025-11-16T18:00:00Z",
  "updated_at": "2025-11-16T18:05:00Z"
}
```

You can safely resume after interruptions using `--resume`.

## Features

### Automatic Retry Logic

- **3 retries** per sample with exponential backoff
- Handles rate limiting (HTTP 429) automatically
- Continues processing even if individual samples fail

### Error Handling

- Skips samples with missing vibe analysis (uses only basic metadata)
- Validates embedding dimensions (1536 for text-embedding-3-small)
- Checks for NaN or infinite values
- Logs all failures to progress file

### Cost Tracking

- Real-time cost estimation during processing
- Tracks both tokens and USD costs
- Integration with UsageTrackingService for database logging
- Average cost: ~$0.000032 per sample

### Batch Processing

- Processes 100 samples at a time for efficiency
- Commits to Turso after each successful embedding
- Progress bar with estimated time remaining

## Output

**During Processing:**

```
╭─────────────────────────────────────────────────── Configuration ────────────────────────────────────────────────────╮
│ Embedding Generation                                                                                                 │
│                                                                                                                      │
│ Total samples: 2,437                                                                                                │
│ Last processed: 0                                                                                                   │
│ Resume from: 1                                                                                                      │
│ Batch size: 100                                                                                                     │
│ Previous cost: $0.0000                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

⠸ Processed 523/2,437 (21.5%) ($0.0167) ━━━━━━━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  21% 0:04:32
```

**Final Summary:**

```
    Embedding Generation Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric          ┃ Value     ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Total Samples   │ 2,437     │
│ Successful      │ 2,435     │
│ Failed          │ 2         │
│ Success Rate    │ 99.9%     │
│ Total Cost      │ $0.0790   │
│ Avg Cost/Sample │ $0.000032 │
└─────────────────┴───────────┘

Failed samples: 2
Sample IDs: 523, 1045
```

## Embedding Source Text Format

Each sample's embedding is generated from:

```
Title: {sample.title}
Genre: {sample.genre}
BPM: {sample.bpm}
Key: {sample.musical_key}
Mood: {vibe.mood_primary}, {vibe.mood_secondary}
Energy: {vibe.energy_level}
Tags: {', '.join(vibe.texture_tags)}
Description: {vibe.characteristics.raw_analysis}
Sample Tags: {', '.join(sample.tags)}
```

## Database Schema

**Turso `sample_embeddings` table:**

```sql
CREATE TABLE sample_embeddings (
    sample_id INTEGER PRIMARY KEY,
    vibe_vector BLOB NOT NULL,          -- 1536-dimension float32 vector
    embedding_source TEXT,              -- Original text used for embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Vector format:**

- 1536 dimensions (OpenAI text-embedding-3-small)
- Stored as little-endian float32 binary blob
- 6,144 bytes per embedding (1536 × 4 bytes)

## Cost Breakdown

**OpenRouter text-embedding-3-small pricing:**

- $0.02 per 1M input tokens
- No output tokens (embeddings only)

**Estimated costs:**

- Average ~200 tokens per sample
- 2,437 samples × 200 tokens = 487,400 tokens
- Total cost: **~$0.08**

**Actual observed costs (dry-run):**

- 2,437 samples
- Average 325 tokens per sample
- Total cost: **$0.079**

## Troubleshooting

### "TURSO_DATABASE_URL environment variable must be set"

Add Turso credentials to `.env` file (see Prerequisites above).

### "OPENROUTER_API_KEY environment variable must be set"

Add OpenRouter API key to `.env` file.

### "Failed to store embedding for sample X"

Check Turso connection and table schema. Run:

```bash
turso db shell sp404-samples "SELECT COUNT(*) FROM sample_embeddings;"
```

### Rate Limiting (HTTP 429)

The script automatically retries with exponential backoff. If you see many rate limit errors:

1. Reduce `BATCH_SIZE` in the script (default: 100)
2. Add delays between batches
3. Check OpenRouter dashboard for quota limits

### Missing Vibe Analysis

Samples without vibe analysis will use only basic metadata (title, genre, BPM, key, tags). This is normal and expected.

## Advanced Usage

### Custom Batch Size

Edit `BATCH_SIZE` constant in the script:

```python
BATCH_SIZE = 50  # Process 50 samples at a time instead of 100
```

### Custom Retry Logic

Edit `max_retries` parameter:

```python
successful, failed, batch_cost = await generate_embeddings_batch(
    samples, embedding_service, progress, dry_run, max_retries=5
)
```

### Reset Progress

Delete the progress file to start fresh:

```bash
rm backend/scripts/embeddings_progress.json
python backend/scripts/generate_embeddings.py --all
```

## Integration with Search

After generating embeddings, use them for semantic search:

```python
from app.db.turso import get_turso_client

# Get embedding for search query
query_embedding = await embedding_service.generate_embedding("dark moody hip hop sample")

# Search Turso for similar samples
turso = get_turso_client()
results = turso.query("""
    SELECT sample_id,
           vector_distance_cos(vibe_vector, ?) as similarity
    FROM sample_embeddings
    WHERE similarity > 0.7
    ORDER BY similarity DESC
    LIMIT 10
""", [query_embedding])
```

## Summary

1. **Dry-run first**: Always estimate costs with `--dry-run --all`
2. **Configure Turso**: Set up Turso database and credentials
3. **Run generation**: Use `--all` or `--sample-ids` to process samples
4. **Monitor progress**: Check `embeddings_progress.json` for status
5. **Resume if needed**: Use `--resume` to continue after interruptions

**Total expected cost for 2,437 samples: ~$0.08**
