# Embedding Generation Script

## Overview

Generate and populate vector embeddings for all samples in the database. This script creates semantic embeddings from vibe analysis data and stores them in Turso for similarity search.

## Features

- **Batch Processing**: Processes 100 samples at a time for efficiency
- **Progress Tracking**: Resumable with checkpoint-based progress
- **Cost Estimation**: Dry-run mode to preview costs before processing
- **Error Handling**: Graceful failure handling with detailed logging
- **Flexible Selection**: Process all samples or specific sample IDs

## Prerequisites

### Services Required

1. **EmbeddingService** (Currently being created by another agent)
   - OpenRouter API integration
   - text-embedding-3-small model
   - Cost tracking and token estimation

2. **Turso Database**
   - Table: `sample_embeddings`
   - Columns: `sample_id`, `vibe_vector` (BLOB), `embedding_source` (TEXT), `created_at` (TIMESTAMP)

3. **PostgreSQL/SQLite Database**
   - Tables: `samples`, `vibe_analyses`
   - 2,328 samples with vibe analysis data

## Cost Estimation

**Model**: OpenRouter `text-embedding-3-small`
**Pricing**: ~$0.02 per 1M tokens

**Estimated Costs**:
- Average sample: ~200 tokens
- 100 samples: $0.0007 (~$0.000007 per sample)
- 2,328 samples: $0.016 total (full database)

## Usage

### Dry Run (Cost Estimation Only)

```bash
# Estimate cost for all samples
python backend/scripts/generate_embeddings.py --all --dry-run

# Estimate cost for specific samples
python backend/scripts/generate_embeddings.py --sample-ids 1-100 --dry-run
```

**Example Output**:
```
Processing 100 specific samples
Using database: /path/to/backend/sp404_samples.db
╭─────────────────────────────────────────────────── Configuration ──────────────────────────────────────────────────────╮
│ Embedding Generation (DRY RUN)                                                                                         │
│                                                                                                                        │
│ Total samples: 100                                                                                                     │
│ Last processed: 0                                                                                                      │
│ Resume from: 1                                                                                                         │
│ Batch size: 100                                                                                                        │
│ Previous cost: $0.0000                                                                                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  Processed 100/100 ($0.0007) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
    Cost Estimation Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric          ┃ Value     ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Total Samples   │ 100       │
│ Successful      │ 100       │
│ Failed          │ 0         │
│ Success Rate    │ 100.0%    │
│ Total Cost      │ $0.0007   │
│ Avg Cost/Sample │ $0.000007 │
└─────────────────┴───────────┘
```

### Process All Samples (Fresh Start)

```bash
# Process all samples from beginning
python backend/scripts/generate_embeddings.py --all

# Process all samples and reset progress
python backend/scripts/generate_embeddings.py --all --reset
```

### Resume from Checkpoint

```bash
# Continue from last processed sample
python backend/scripts/generate_embeddings.py --resume
```

### Process Specific Samples

```bash
# Single sample
python backend/scripts/generate_embeddings.py --sample-ids 1

# Multiple samples
python backend/scripts/generate_embeddings.py --sample-ids 1,2,3,100

# Sample range
python backend/scripts/generate_embeddings.py --sample-ids 1-100

# Mixed notation
python backend/scripts/generate_embeddings.py --sample-ids 1,5,10-20,100-200
```

## Embedding Source Text Format

The script creates embedding source text by combining sample metadata and vibe analysis:

```
Title: {title}
Genre: {genre}
BPM: {bpm}
Key: {musical_key}
Mood: {mood_primary}, {mood_secondary}
Energy: {energy_level}
Tags: {vibe_tags}
Description: {raw_analysis}
```

**Example**:
```
Title: Jazz Piano Loop
Genre: Jazz
BPM: 95
Key: Dm
Mood: mellow, contemplative
Energy: 0.45
Tags: smooth, melodic, vintage
Description: A warm, contemplative jazz piano loop with rich chord progressions...
```

## Progress Tracking

Progress is saved to `backend/scripts/embeddings_progress.json`:

```json
{
  "last_processed_id": 1523,
  "total_processed": 1523,
  "total_cost_usd": 0.0106,
  "total_tokens": 304600,
  "failures": [],
  "started_at": "2025-11-16T18:00:00Z",
  "updated_at": "2025-11-16T18:15:00Z"
}
```

### Resume After Interruption

If the script is interrupted (Ctrl+C, network error, etc.), simply run:

```bash
python backend/scripts/generate_embeddings.py --resume
```

The script will continue from `last_processed_id + 1`.

## Error Handling

### API Failures
- **OpenRouter API errors**: Exponential backoff retry (3 attempts)
- **Rate limiting**: Automatic retry with backoff
- **Invalid API key**: Immediate failure with clear error message

### Database Failures
- **Turso connection issues**: Reconnect and retry
- **Invalid vibe data**: Skip sample and log warning
- **Missing vibe analysis**: Uses basic metadata only

### Validation Failures
- **Invalid embedding dimensions**: Logs error and skips sample
- **NaN/infinite values**: Validation check before storage

### Failed Samples
Failed samples are logged in progress file:

```json
{
  "failures": [
    {"sample_id": 523, "timestamp": "2025-11-16T18:05:32Z"},
    {"sample_id": 891, "timestamp": "2025-11-16T18:08:15Z"}
  ]
}
```

## Performance

**Expected Performance** (once EmbeddingService is implemented):
- **Processing Speed**: ~10-15 samples/second (batch API)
- **Total Time**: 2,328 samples in ~3-5 minutes
- **Memory Usage**: <200 MB (batch processing)
- **Cost**: ~$0.016 for full database

## Turso Storage

Embeddings are stored as binary blobs in Turso:

```sql
CREATE TABLE sample_embeddings (
    sample_id INTEGER PRIMARY KEY,
    vibe_vector BLOB NOT NULL,        -- 1536 float32 values (6,144 bytes)
    embedding_source TEXT,             -- Original text used for embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Vector Format
- **Type**: BLOB (binary large object)
- **Encoding**: Little-endian float32 array
- **Dimensions**: 1536 floats (OpenAI text-embedding-3-small)
- **Size**: 6,144 bytes per embedding

## Validation

The script validates embeddings before storage:

1. **Dimension Check**: Must be exactly 1536 dimensions
2. **Value Check**: No NaN or infinite values
3. **Type Check**: All values must be float or int

## Dependencies

### Python Packages
- `sqlalchemy`: Database queries
- `rich`: Terminal UI and progress bars
- `tiktoken`: Token counting for cost estimation
- `struct`: Binary vector encoding
- `libsql_client`: Turso database client

### Environment Variables
- `TURSO_DATABASE_URL`: Turso database URL
- `TURSO_AUTH_TOKEN`: Turso authentication token
- `OPENROUTER_API_KEY`: OpenRouter API key (for EmbeddingService)

## Troubleshooting

### Issue: "EmbeddingService not yet implemented"

**Solution**: Wait for EmbeddingService to be created by other agent. Currently, the script only supports dry-run mode for cost estimation.

### Issue: "Turso credentials not found"

**Solution**: Set environment variables:
```bash
export TURSO_DATABASE_URL="libsql://your-db.turso.io"
export TURSO_AUTH_TOKEN="your_token_here"
```

### Issue: "Database connection failed"

**Solution**: Check database file exists:
```bash
ls -lh backend/sp404_samples.db
```

### Issue: "Progress file corrupted"

**Solution**: Delete and restart:
```bash
rm backend/scripts/embeddings_progress.json
python backend/scripts/generate_embeddings.py --all --reset
```

## Next Steps

Once **EmbeddingService** is implemented:

1. **Test with Small Batch**:
   ```bash
   python backend/scripts/generate_embeddings.py --sample-ids 1-10
   ```

2. **Verify Turso Storage**:
   ```python
   from app.db.turso import get_turso_client
   turso = get_turso_client()
   result = turso.query("SELECT COUNT(*) FROM sample_embeddings")
   print(f"Embeddings stored: {result[0]}")
   ```

3. **Full Database Processing**:
   ```bash
   python backend/scripts/generate_embeddings.py --all
   ```

4. **Verify Embedding Quality**:
   - Test similarity search
   - Validate embedding dimensions
   - Check embedding source text accuracy

## Related Documentation

- **EmbeddingService**: `backend/app/services/embedding_service.py` (to be created)
- **Turso Setup**: `backend/app/db/turso.py`
- **Sample Models**: `backend/app/models/sample.py`, `backend/app/models/vibe_analysis.py`

## Support

For issues or questions:
1. Check this README
2. Review error logs in terminal output
3. Inspect `embeddings_progress.json` for failure details
4. Test with `--dry-run` flag to isolate issues
