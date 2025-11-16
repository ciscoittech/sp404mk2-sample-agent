# Vibe Search System - PostgreSQL Deployment Guide

**Status**: Ready for Production
**Architecture**: PostgreSQL + NumPy Vector Search
**Cost**: $0 for vector calculations (local Python)

---

## Quick Start (Development)

```bash
# 1. Create .env from example
cp .env.example .env

# 2. Update PostgreSQL credentials to match docker-compose.yml
# POSTGRES_PASSWORD=changeme123

# 3. Start PostgreSQL
docker-compose up -d postgres
sleep 10  # Wait for database to be ready

# 4. Run Alembic migration
./venv/bin/alembic upgrade head

# 5. Generate embeddings for samples
./venv/bin/python backend/scripts/generate_embeddings.py --all

# 6. Start backend
./venv/bin/python backend/run.py

# 7. Access vibe search API
curl -X POST http://localhost:8100/api/v1/vibe-search/search \
  -H "Content-Type: application/json" \
  -d '{"query": "dark moody loop", "limit": 5}'
```

---

## API Reference

### Search by Natural Language
```http
POST /api/v1/vibe-search/search
Content-Type: application/json

{
  "query": "dark moody loop",
  "limit": 5,
  "filters": {
    "bpm_min": 80,
    "bpm_max": 120,
    "genre": "hip-hop",
    "energy_min": 0.3,
    "energy_max": 0.8,
    "danceability_min": 0.4,
    "danceability_max": 0.7
  }
}
```

**Response**:
```json
[
  {
    "id": 42,
    "title": "Dark Jazz Loop",
    "bpm": 95,
    "genre": "jazz",
    "similarity": 0.92,
    "mood_primary": "dark",
    "mood_secondary": "moody",
    "energy_level": 0.45,
    "danceability": 0.55,
    "tags": ["jazz", "loop", "dark"]
  }
]
```

### Find Similar Samples
```http
GET /api/v1/vibe-search/similar/42?limit=10
```

---

## Data Flow

```
User Query
    ↓
[EmbeddingService] → OpenRouter API → 1536-dim embedding vector
    ↓
[VibeSearchService] queries PostgreSQL
    ↓
Load all embeddings from sample_embeddings table
    ↓
[NumPy] calculates cosine similarity (fast, local)
    ↓
Filter by thresholds (≥0.7 similarity)
    ↓
Enrich with metadata from samples + vibe_analysis tables
    ↓
Sort by similarity score
    ↓
Return results
```

---

## Performance Expectations

### Single Query Performance
| Metric | Local | Deployed |
|--------|-------|----------|
| Vector generation | ~100ms | ~100ms |
| Similarity calculation | <5ms | <5ms |
| Database queries | <5ms | ~50ms |
| **Total** | ~110ms | ~155ms |

### Scalability
- **100 samples**: <1ms similarity calculation
- **1,000 samples**: <10ms similarity calculation
- **10,000 samples**: <100ms similarity calculation
- **100,000+ samples**: <1s similarity calculation (still acceptable)

### Cost Efficiency
- OpenRouter embeddings: ~$0.02 per 1M tokens
- 2,328 current samples: ~$0.05 total cost to embed
- Per-sample cost: $0.00002 (negligible)

---

## Database Schema

### sample_embeddings Table
```sql
CREATE TABLE sample_embeddings (
    id INTEGER PRIMARY KEY,
    sample_id INTEGER NOT NULL UNIQUE,
    vibe_vector FLOAT8[] NOT NULL,  -- 1536-dimensional array
    embedding_source VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    FOREIGN KEY (sample_id) REFERENCES samples(id),
    INDEX idx_sample_embeddings_sample_id (sample_id)
);
```

### Embedding Vector Details
- **Dimensions**: 1536
- **Model**: OpenRouter text-embedding-3-small
- **Type**: ARRAY(Float) in PostgreSQL
- **Size**: ~12.3 KB per embedding (1536 floats × 8 bytes)
- **Total for 2,328 samples**: ~28.6 MB

---

## Troubleshooting

### PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Verify credentials in .env match docker-compose.yml
grep POSTGRES .env
grep POSTGRES docker-compose.yml

# Check PostgreSQL logs
docker logs sp404-postgres
```

### Embeddings Not Generating
```bash
# Check OpenRouter API key
grep OPENROUTER_API_KEY .env

# Test embedding service
./venv/bin/python -c "
from app.services.embedding_service import EmbeddingService
import asyncio
async def test():
    service = EmbeddingService(None)
    vec = await service.generate_embedding('test')
    print(f'Generated {len(vec)}-dim vector')
asyncio.run(test())
"
```

### No Results from Search
```bash
# Verify embeddings exist
psql postgresql://sp404_user:changeme123@localhost:5432/sp404_samples
SELECT COUNT(*) FROM sample_embeddings;

# Check query is valid
SELECT query FROM vibe_analysis LIMIT 5;
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/models/sample_embedding.py` | SQLAlchemy model for embeddings |
| `backend/app/services/vibe_search_service.py` | Core search logic with numpy |
| `backend/app/services/embedding_service.py` | Vector generation via OpenRouter |
| `backend/app/api/v1/endpoints/vibe_search.py` | REST API endpoints |
| `backend/scripts/generate_embeddings.py` | Batch embedding generation |
| `backend/alembic/versions/20251116_184500_*.py` | Database migration |

---

## Production Deployment

### Environment Variables Required
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/sp404_samples

# API
OPENROUTER_API_KEY=your-key-here
API_HOST=0.0.0.0
API_PORT=8100

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENVIRONMENT=production
```

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# Verify migration ran
docker-compose logs backend | grep upgrade

# Test API
curl http://localhost:8100/api/v1/health
```

### Database Backup
```bash
# Backup embeddings and metadata
docker exec sp404-postgres pg_dump -U sp404_user sp404_samples > backup.sql

# Restore from backup
docker exec -i sp404-postgres psql -U sp404_user sp404_samples < backup.sql
```

---

## Future Improvements

1. **Batch Search** - Search multiple queries in one request
2. **Caching** - Redis cache for frequently searched queries
3. **Similarity Thresholds** - User-configurable threshold per request
4. **Vector Quantization** - Compress embeddings for faster search
5. **Hybrid Search** - Combine vector + full-text search

---

## Support

For issues or questions, refer to:
- `TURSO_TO_POSTGRESQL_MIGRATION.md` - Migration details
- `backend/app/services/example_vibe_search.py` - Usage examples
- `backend/tests/services/` - Test cases
