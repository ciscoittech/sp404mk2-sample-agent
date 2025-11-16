# Embeddings Generation - Quick Start

## Prerequisites Checklist

- [ ] OpenRouter API key in `.env` (`OPENROUTER_API_KEY`)
- [ ] Turso database created and configured
- [ ] Turso credentials in `.env` (`TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`)
- [ ] Embeddings table created in Turso (run `create_embeddings_table.sql`)

## Step-by-Step Setup

### 1. Configure OpenRouter

```bash
# Add to backend/.env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get key: https://openrouter.ai/keys

### 2. Setup Turso Database

```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Create database
turso db create sp404-samples

# Get URL
turso db show sp404-samples --url
# Output: libsql://sp404-samples-yourusername.turso.io

# Create token
turso db tokens create sp404-samples
# Output: eyJhbGciOi...

# Add to backend/.env
TURSO_DATABASE_URL=libsql://sp404-samples-yourusername.turso.io
TURSO_AUTH_TOKEN=eyJhbGciOi...

# Create table
turso db shell sp404-samples < backend/scripts/create_embeddings_table.sql
```

### 3. Verify Setup

```bash
cd backend

# Check database connection
python -c "from app.db.turso import test_connection; print('OK' if test_connection() else 'FAIL')"

# Check sample count
sqlite3 sp404_samples.db "SELECT COUNT(*) FROM samples WHERE id IN (SELECT sample_id FROM vibe_analyses);"
```

## Usage

### Dry-Run (Recommended First)

```bash
# Estimate total cost
python scripts/generate_embeddings.py --dry-run --all

# Expected: ~$0.08 for 2,437 samples
```

### Generate Embeddings

```bash
# Process all samples
python scripts/generate_embeddings.py --all

# Or test with small batch first
python scripts/generate_embeddings.py --sample-ids 1-10
```

### If Interrupted

```bash
# Resume from last checkpoint
python scripts/generate_embeddings.py --resume
```

## Expected Output

```
╭─────────────────────────────────────────────────── Configuration ─────────────────────────────────────────────────────╮
│ Embedding Generation                                                                                                  │
│                                                                                                                       │
│ Total samples: 2,437                                                                                                 │
│ Last processed: 0                                                                                                    │
│ Resume from: 1                                                                                                       │
│ Batch size: 100                                                                                                      │
│ Previous cost: $0.0000                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

⠸ Processed 523/2,437 (21.5%) ($0.0167) ━━━━━━━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  21% 0:04:32

    Embedding Generation Summary
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

## Troubleshooting

### "TURSO_DATABASE_URL environment variable must be set"
→ Add Turso credentials to `.env` file (see Setup step 2)

### "OPENROUTER_API_KEY environment variable must be set"
→ Add OpenRouter API key to `.env` file (see Setup step 1)

### "Failed to store embedding"
→ Check Turso table exists: `turso db shell sp404-samples "SELECT COUNT(*) FROM sample_embeddings;"`

### Rate limiting errors
→ Script will automatically retry with backoff. If persistent, check OpenRouter dashboard.

## Cost Summary

- **Model**: OpenAI text-embedding-3-small
- **Pricing**: $0.02 per 1M tokens
- **Average**: 325 tokens per sample
- **Total samples**: 2,437
- **Estimated cost**: **$0.08**

## Next Steps After Generation

1. Verify embeddings in Turso:
```bash
turso db shell sp404-samples "SELECT COUNT(*) FROM sample_embeddings;"
```

2. Test semantic search:
```python
from app.db.turso import get_turso_client
turso = get_turso_client()
results = turso.query("SELECT sample_id FROM sample_embeddings LIMIT 5")
print(results)
```

3. Integrate into search API endpoints

## Full Documentation

- **Usage Guide**: `EMBEDDING_GENERATION_USAGE.md`
- **Completion Report**: `EMBEDDING_GENERATION_COMPLETION.md`
- **This Quick Start**: `EMBEDDINGS_QUICK_START.md`
