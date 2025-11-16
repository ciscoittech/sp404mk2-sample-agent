# VibeSearchService - Quick Reference

## Import and Initialize

```python
from app.db.turso import get_turso_client
from app.services.embedding_service import EmbeddingService
from app.services.vibe_search_service import VibeSearchService, SearchError

# Initialize
search_service = VibeSearchService(
    embedding_service=embedding_service,
    db=db_session,
    turso_client=get_turso_client()
)
```

## Method 1: Search by Natural Language Query

```python
# Basic search
results = await search_service.search_by_vibe(
    query="dark moody loop",
    limit=20
)

# With filters
results = await search_service.search_by_vibe(
    query="upbeat energetic drums",
    limit=10,
    filters={
        "bpm_min": 120,
        "bpm_max": 140,
        "genre": "hip-hop",
        "energy_min": 0.7,
        "energy_max": 1.0,
        "danceability_min": 0.6
    }
)
```

## Method 2: Find Similar Samples

```python
# Find samples similar to sample #123
similar = await search_service.find_similar(
    sample_id=123,
    limit=10
)
```

## Result Format

```python
{
    "id": 123,
    "title": "Dark Hip Hop Loop",
    "bpm": 85.0,
    "musical_key": "Am",
    "genre": "hip-hop",
    "duration": 8.5,
    "similarity": 0.92,  # Cosine similarity score
    "file_path": "/path/to/sample.wav",
    "tags": ["dark", "moody"],
    "mood_primary": "dark",
    "mood_secondary": "melancholic",
    "energy_level": 0.65,
    "danceability": 0.72,
    "acousticness": 0.45,
    "instrumentalness": 0.88,
    "vibe_tags": ["dark", "moody", "atmospheric"]
}
```

## Available Filters

| Filter | Type | Range | Description |
|--------|------|-------|-------------|
| `bpm_min` | float | 0-300 | Minimum BPM |
| `bpm_max` | float | 0-300 | Maximum BPM |
| `genre` | string | - | Exact genre match |
| `energy_min` | float | 0.0-1.0 | Minimum energy level |
| `energy_max` | float | 0.0-1.0 | Maximum energy level |
| `danceability_min` | float | 0.0-1.0 | Minimum danceability |
| `danceability_max` | float | 0.0-1.0 | Maximum danceability |

## Error Handling

```python
try:
    results = await search_service.search_by_vibe(query="dark loop")
except SearchError as e:
    print(f"Search failed: {e.message}")
    print(f"Query: {e.query}")
```

## Example Queries

| Query | Description |
|-------|-------------|
| `"dark moody loop"` | Find atmospheric, dark samples |
| `"upbeat energetic drums"` | High-energy percussion |
| `"smooth jazz sample"` | Melodic, mellow samples |
| `"aggressive trap beat"` | Hard-hitting trap elements |
| `"vintage soul vocals"` | Classic soul vocal samples |
| `"ambient pad texture"` | Atmospheric background sounds |

## Performance

- Vector search: ~50-100ms
- Metadata enrichment: ~20-50ms
- Total: ~100-200ms for 20 results
- Similarity threshold: 0.7 (default)

## Example Script

Run the complete example:

```bash
./venv/bin/python backend/app/services/example_vibe_search.py
```

## Files

- **Service:** `/backend/app/services/vibe_search_service.py`
- **Example:** `/backend/app/services/example_vibe_search.py`
- **Docs:** `/backend/VIBE_SEARCH_IMPLEMENTATION.md`
- **Quick Ref:** `/backend/VIBE_SEARCH_QUICK_REF.md`
