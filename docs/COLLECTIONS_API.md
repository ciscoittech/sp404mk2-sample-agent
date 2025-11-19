# Collections API Documentation

**Phase 2B: Complete Collections API Implementation**

## Overview

The Collections API provides endpoints for organizing samples into hierarchical collections with support for manual and smart (rule-based) collections.

---

## Endpoints

### Base URL
```
/api/v1/collections
```

All endpoints require authentication via Bearer token.

---

## Create Collection

**POST** `/api/v1/collections`

Create a new collection (manual or smart).

### Request Body
```json
{
  "name": "Jazz Samples",
  "description": "My favorite jazz samples",
  "parent_collection_id": null,
  "is_smart": false,
  "smart_rules": null
}
```

**Smart Collection Example:**
```json
{
  "name": "High BPM Jazz",
  "description": "Jazz samples over 140 BPM",
  "is_smart": true,
  "smart_rules": {
    "genres": ["Jazz", "Fusion"],
    "bpm_min": 140.0,
    "bpm_max": 180.0,
    "tags": ["vintage", "acoustic"],
    "min_confidence": 70
  }
}
```

### Response (201 Created)
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Jazz Samples",
  "description": "My favorite jazz samples",
  "parent_collection_id": null,
  "is_smart": false,
  "smart_rules": null,
  "sample_count": 0,
  "created_at": "2025-11-17T10:00:00Z",
  "updated_at": "2025-11-17T10:00:00Z"
}
```

---

## List Collections

**GET** `/api/v1/collections`

List all collections for the authenticated user.

### Query Parameters
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 50, max: 100) - Number of results
- `include_smart` (bool, default: true) - Include smart collections

### Response (200 OK)
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Jazz Samples",
      "description": "My favorite jazz samples",
      "parent_collection_id": null,
      "is_smart": false,
      "smart_rules": null,
      "sample_count": 15,
      "created_at": "2025-11-17T10:00:00Z",
      "updated_at": "2025-11-17T10:30:00Z"
    }
  ],
  "total": 1
}
```

---

## Get Collection

**GET** `/api/v1/collections/{collection_id}`

Get detailed collection information with samples and sub-collections.

### Response (200 OK)
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Jazz Samples",
  "description": "My favorite jazz samples",
  "parent_collection_id": null,
  "is_smart": false,
  "smart_rules": null,
  "sample_count": 2,
  "created_at": "2025-11-17T10:00:00Z",
  "updated_at": "2025-11-17T10:30:00Z",
  "samples": [
    {
      "id": 10,
      "title": "Jazz Piano Loop",
      "genre": "Jazz",
      "bpm": 120.0,
      "duration": 8.5,
      "added_at": "2025-11-17T10:15:00Z"
    }
  ],
  "sub_collections": []
}
```

---

## Update Collection

**PUT** `/api/v1/collections/{collection_id}`

Update collection metadata.

### Request Body
```json
{
  "name": "Updated Name",
  "description": "New description",
  "smart_rules": {
    "genres": ["Jazz"],
    "bpm_min": 100.0
  }
}
```

### Response (200 OK)
Same as Get Collection response.

---

## Delete Collection

**DELETE** `/api/v1/collections/{collection_id}`

Delete a collection (cascades to sub-collections).

### Response (200 OK)
```json
{
  "success": true
}
```

---

## Add Samples to Collection

**POST** `/api/v1/collections/{collection_id}/samples`

Add multiple samples to a manual collection.

### Request Body
```json
{
  "sample_ids": [1, 2, 3, 4, 5]
}
```

### Response (200 OK)
```json
{
  "count": 5
}
```

**Errors:**
- `400` - Collection is a smart collection (cannot manually add)
- `400` - Some samples not found or unauthorized
- `404` - Collection not found

---

## Remove Sample from Collection

**DELETE** `/api/v1/collections/{collection_id}/samples/{sample_id}`

Remove a sample from a manual collection.

### Response (200 OK)
```json
{
  "success": true
}
```

**Errors:**
- `400` - Collection is a smart collection
- `404` - Sample not found in collection

---

## Get Collection Samples

**GET** `/api/v1/collections/{collection_id}/samples`

Get paginated samples in a collection.

### Query Parameters
- `skip` (int, default: 0)
- `limit` (int, default: 50, max: 100)

### Response (200 OK)
```json
{
  "items": [
    {
      "id": 1,
      "title": "Sample 1",
      "genre": "Jazz",
      "bpm": 120.0,
      "file_url": "/api/v1/samples/1/download"
    }
  ],
  "total": 15
}
```

---

## Evaluate Smart Collection

**POST** `/api/v1/collections/{collection_id}/evaluate`

Re-evaluate smart collection rules and update samples.

### Response (200 OK)
```json
{
  "count": 12,
  "updated_at": "2025-11-17T11:00:00Z"
}
```

**Errors:**
- `400` - Collection is not a smart collection
- `404` - Collection not found

---

## Smart Rules Schema

Smart collections use rules to automatically include samples.

### Available Rules

```typescript
{
  genres?: string[]           // Match any of these genres
  bpm_min?: number            // Minimum BPM
  bpm_max?: number            // Maximum BPM
  tags?: string[]             // Match samples with any of these tags
  min_confidence?: number     // Minimum confidence score (0-100)
  sample_types?: string[]     // Reserved for future use
}
```

### Rule Logic

- **Genres**: Sample must have a genre matching one in the list
- **BPM Range**: Sample BPM must be within min/max (inclusive)
- **Tags**: Sample must have at least one matching tag
- **Confidence**: Sample must have at least one confidence score (BPM, genre, or key) meeting the threshold

All rules are combined with AND logic.

---

## Authorization

All endpoints check:
1. User is authenticated (Bearer token)
2. Collection belongs to the authenticated user
3. Samples belong to the authenticated user (when adding/removing)

**Error Responses:**
- `401` - Not authenticated
- `403` - Forbidden (inactive user)
- `404` - Not found (or unauthorized access to another user's collection)

---

## Implementation Details

### Service Layer
**File:** `backend/app/services/collection_service.py`

- `CollectionService` - Business logic for all collection operations
- Handles authorization checks
- Manages smart collection evaluation
- Updates denormalized `sample_count` field

### Schemas
**File:** `backend/app/schemas/collection_schemas.py`

- `CollectionCreate` - Create request
- `CollectionUpdate` - Update request
- `CollectionResponse` - Basic collection response
- `CollectionDetailResponse` - Detailed response with samples/sub-collections
- `SmartRulesSchema` - Smart collection rules
- `AddSamplesRequest` - Bulk add samples request

### Endpoints
**File:** `backend/app/api/v1/endpoints/collections.py`

- 8 REST endpoints
- Full CRUD operations
- Smart collection support
- Pagination support

---

## Testing

**File:** `backend/tests/test_collection_api.py`

Comprehensive test suite covering:
- Collection CRUD operations
- Sample add/remove operations
- Smart collection creation and evaluation
- Authorization checks
- Pagination

**Run Tests:**
```bash
pytest backend/tests/test_collection_api.py -v
```

---

## Next Steps: Phase 2C

React frontend components will consume these endpoints:

1. **CollectionsPage** - Main collections browser
2. **CollectionCard** - Collection display with sample count
3. **CreateCollectionModal** - Create/edit collection form
4. **SmartRulesEditor** - Visual rule builder
5. **SampleCard Enhancement** - Add "Add to Collection" action
6. **SampleBrowser Filter** - Filter by collection

---

## Database Models

### Collection Table
```sql
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    parent_collection_id INTEGER REFERENCES collections(id),
    is_smart BOOLEAN DEFAULT FALSE,
    smart_rules JSON DEFAULT '{}',
    sample_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### CollectionSample Association Table
```sql
CREATE TABLE collection_samples (
    collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
    sample_id INTEGER REFERENCES samples(id) ON DELETE CASCADE,
    order INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (collection_id, sample_id)
);
```

---

## Performance Considerations

1. **Indexes**: Applied on `user_id`, `is_smart`, `parent_collection_id`
2. **Pagination**: All list endpoints support skip/limit
3. **Eager Loading**: `selectinload()` used for relationships
4. **Denormalization**: `sample_count` cached on collection for fast display
5. **Smart Collection Evaluation**: Runs on create/update, not on every read

---

## Future Enhancements

1. **Bulk Operations**: Delete multiple collections at once
2. **Collection Templates**: Pre-built smart collection rules
3. **Collection Sharing**: Share collections between users
4. **Export Collections**: Export collection as ZIP or SP-404 project
5. **Collection Stats**: Track most-used collections, growth over time
6. **Drag & Drop Ordering**: Custom sample ordering in manual collections
