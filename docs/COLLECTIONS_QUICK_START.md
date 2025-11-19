# Collections API - Quick Start Guide

**For Developers:** Get started with the Collections API in 5 minutes.

---

## 1. Start the Server

```bash
cd backend
../venv/bin/python run.py
```

Server runs on: `http://localhost:8100`

---

## 2. Get Authentication Token

```bash
# Login (or register if first time)
curl -X POST http://localhost:8100/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response:
# {"access_token": "eyJ...", "token_type": "bearer"}

# Save token
export TOKEN="eyJ..."
```

---

## 3. Create Your First Collection

### Manual Collection
```bash
curl -X POST http://localhost:8100/api/v1/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Favorite Samples",
    "description": "Hand-picked samples"
  }'
```

### Smart Collection
```bash
curl -X POST http://localhost:8100/api/v1/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High BPM Jazz",
    "description": "Jazz samples over 140 BPM",
    "is_smart": true,
    "smart_rules": {
      "genres": ["Jazz"],
      "bpm_min": 140
    }
  }'
```

---

## 4. Add Samples to Collection

**First, upload some samples:**
```bash
# Upload a sample
curl -X POST http://localhost:8100/api/v1/samples \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/sample.wav" \
  -F "title=Jazz Piano Loop" \
  -F "genre=Jazz" \
  -F "bpm=145"

# Response includes sample ID
```

**Then add to collection:**
```bash
curl -X POST http://localhost:8100/api/v1/collections/1/samples \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sample_ids": [1, 2, 3]}'
```

---

## 5. List Collections

```bash
curl -X GET http://localhost:8100/api/v1/collections \
  -H "Authorization: Bearer $TOKEN"
```

**With pagination:**
```bash
curl -X GET "http://localhost:8100/api/v1/collections?skip=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. Get Collection Details

```bash
curl -X GET http://localhost:8100/api/v1/collections/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes:**
- Collection metadata
- List of samples in collection
- Sub-collections (if any)

---

## 7. View Samples in Collection

```bash
curl -X GET http://localhost:8100/api/v1/collections/1/samples \
  -H "Authorization: Bearer $TOKEN"
```

---

## Common Operations

### Update Collection
```bash
curl -X PUT http://localhost:8100/api/v1/collections/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "description": "New description"}'
```

### Delete Collection
```bash
curl -X DELETE http://localhost:8100/api/v1/collections/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Remove Sample from Collection
```bash
curl -X DELETE http://localhost:8100/api/v1/collections/1/samples/5 \
  -H "Authorization: Bearer $TOKEN"
```

### Re-evaluate Smart Collection
```bash
curl -X POST http://localhost:8100/api/v1/collections/1/evaluate \
  -H "Authorization: Bearer $TOKEN"
```

---

## Smart Collection Examples

### All Hip-Hop Samples
```json
{
  "name": "Hip-Hop Collection",
  "is_smart": true,
  "smart_rules": {
    "genres": ["Hip-Hop", "Trap", "Boom Bap"]
  }
}
```

### 90-100 BPM Range
```json
{
  "name": "Low BPM Samples",
  "is_smart": true,
  "smart_rules": {
    "bpm_min": 90,
    "bpm_max": 100
  }
}
```

### Vintage Jazz with High Confidence
```json
{
  "name": "High Quality Vintage Jazz",
  "is_smart": true,
  "smart_rules": {
    "genres": ["Jazz"],
    "tags": ["vintage", "vinyl"],
    "min_confidence": 80
  }
}
```

### Multi-Genre High Energy
```json
{
  "name": "High Energy Samples",
  "is_smart": true,
  "smart_rules": {
    "genres": ["House", "Techno", "Drum & Bass"],
    "bpm_min": 140,
    "tags": ["energetic", "upbeat"]
  }
}
```

---

## React Integration (Phase 2C)

**Example React Query Hook:**
```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

// List collections
const { data: collections } = useQuery({
  queryKey: ['collections'],
  queryFn: () => fetch('/api/v1/collections', {
    headers: { Authorization: `Bearer ${token}` }
  }).then(r => r.json())
});

// Create collection
const createCollection = useMutation({
  mutationFn: (data) => fetch('/api/v1/collections', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  }).then(r => r.json())
});

// Usage
createCollection.mutate({
  name: "My Collection",
  description: "A new collection"
});
```

---

## API Reference

**Full documentation:** See `/docs/COLLECTIONS_API.md`

**Base URL:** `/api/v1/collections`

**Endpoints:**
- `POST /` - Create collection
- `GET /` - List collections
- `GET /{id}` - Get collection
- `PUT /{id}` - Update collection
- `DELETE /{id}` - Delete collection
- `POST /{id}/samples` - Add samples
- `DELETE /{id}/samples/{sample_id}` - Remove sample
- `GET /{id}/samples` - Get collection samples
- `POST /{id}/evaluate` - Re-evaluate smart collection

---

## Testing

**Run tests:**
```bash
cd backend
../venv/bin/pytest tests/test_collection_api.py -v
```

**Run with coverage:**
```bash
../venv/bin/pytest tests/test_collection_api.py --cov=app.services.collection_service --cov=app.api.v1.endpoints.collections
```

---

## Troubleshooting

### 401 Unauthorized
- Check token is valid: `echo $TOKEN`
- Token might be expired (re-login)

### 404 Not Found
- Collection might not exist
- You might not own the collection (returns 404, not 403)

### 400 Bad Request
- Check request body format
- Smart collections can't have samples manually added
- Sample IDs must exist and belong to you

---

## Next Steps

1. ✅ **Explore API** - Try all endpoints
2. ✅ **Test Smart Rules** - Create smart collections
3. ✅ **Upload Samples** - Build your library
4. 🔄 **Build Frontend** - Phase 2C React components
5. 🔄 **Add Features** - Collection export, sharing, etc.

---

**Happy Collecting!**
