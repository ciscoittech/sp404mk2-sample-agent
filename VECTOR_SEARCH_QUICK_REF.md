# Vector Search Quick Reference

## API Endpoints

### Search by Vibe
```bash
GET /api/v1/search/vibe?query=dark+moody+loop
```

**Parameters**:
- `query` (required): Natural language search
- `limit` (20): Max results (1-100)
- `min_similarity` (0.7): Threshold (0-1)
- `bpm_min`, `bpm_max`: BPM range
- `genre`: Genre filter
- `energy_min`, `energy_max`: Energy (0-1)
- `danceability_min`, `danceability_max`: Danceability (0-1)

### Similar Samples
```bash
GET /api/v1/search/similar/123
```

**Parameters**:
- `limit` (10): Max results (1-50)
- `min_similarity` (0.8): Threshold (0-1)

## Example Queries

```bash
# Basic search
curl "http://localhost:8100/api/v1/search/vibe?query=energetic+trap+drums"

# With filters
curl "http://localhost:8100/api/v1/search/vibe?query=chill+jazz&bpm_min=80&bpm_max=100&energy_max=0.6"

# Similar samples
curl "http://localhost:8100/api/v1/search/similar/456?limit=5"

# Pretty JSON
curl "http://localhost:8100/api/v1/search/vibe?query=dark+bass" | jq .
```

## Cost

- **Per query**: ~$0.000001 (0.0001¢)
- **10K queries**: ~$0.01 (1¢)
- **1M queries**: ~$1.00

## Python Usage

```python
from app.services.embedding_service import EmbeddingService
from app.services.vibe_search_service import VibeSearchService

# Generate embedding
embedding = await embedding_service.generate_embedding("dark moody loop")

# Search samples
results = await vibe_search_service.search_by_vibe(
    query="energetic drums",
    limit=10,
    bpm_min=120,
    bpm_max=140
)

# Similar samples
similar = await vibe_search_service.get_similar_samples(
    sample_id=123,
    limit=5
)
```

## Files

- **Service**: `backend/app/services/embedding_service.py`
- **Search**: `backend/app/services/vibe_search_service.py`
- **Endpoint**: `backend/app/api/v1/endpoints/vibe_search.py`
- **Config**: `backend/app/core/config.py` (vector search settings)
- **Test**: `backend/scripts/test_vibe_search.py`

## Testing

```bash
# Test embeddings
./venv/bin/python backend/scripts/test_vibe_search.py

# Start server
./venv/bin/python backend/run.py

# Test endpoint
curl "http://localhost:8100/api/v1/search/vibe?query=test&limit=5"
```

## Next Steps (Data Processing)

1. Generate embeddings for 2,328 existing samples
2. Insert into Turso `sample_embeddings` table
3. Verify vector search returns results
