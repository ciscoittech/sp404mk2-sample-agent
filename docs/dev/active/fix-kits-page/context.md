# Fix Kits Page - Technical Context

## Current Implementation Status

### Backend (FastAPI)
**File**: `/backend/app/api/v1/endpoints/kits.py`

- ✅ All kits endpoints implemented
- ✅ Response structure includes `kits`, `total`, `skip`, `limit`
- ✅ Database queries working correctly

**Endpoint Response** (lines 150-155):
```python
@router.get("/", response_model=KitListResponse)
async def list_kits(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    # Returns: {"kits": [...], "total": int, "skip": int, "limit": int}
```

### Frontend (React)
**Files**:
- `/react-app/src/api/kits.ts` - API client
- `/react-app/src/hooks/useSamples.ts` - React Query hooks
- `/react-app/src/pages/KitsPage.tsx` - Page component

**Current API Client** (kits.ts, lines 13-18):
```typescript
list: async (params?: { page?: number; limit?: number; skip?: number }) => {
  const { data } = await apiClient.get<KitListResponse>('/kits', { params });
  return data;  // Returns data as-is from backend
}
```

This returns `{kits: [...], total: number}` but the code tries to access `.items`.

## Component Architecture

### Kits Page Structure
```
KitsPage.tsx
├── useSampleQuery() - Get samples to add to kits
├── useKits() - Get list of kits
├── PadGrid - Display kit pads (4 banks × 12 pads)
├── SampleBrowser - Side panel for selecting samples
└── Kit management buttons (create, delete, rename)
```

### Error Locations
**Line 160**: `const hasMoreKits = kits.items && kits.items.length > 0;`
**Line 221**: `return kits.items.map(...)`
**Line 225**: `return kits.items.length > 0 ? ...`

All assume `items` field exists.

## Type Definitions

### Backend Response Schema
**File**: `/backend/app/schemas/kits.py:150-158`

```python
class KitListResponse(BaseModel):
    kits: List[KitInfo]
    total: int
    skip: int
    limit: int
```

### Frontend Type Definition
**File**: `/react-app/src/api/kits.ts:1-30`

```typescript
export interface Kit {
  id: number;
  name: string;
  description?: string;
  samples: PadAssignment[];
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface KitListResponse {
  items: Kit[];  // ← This expects "items" but backend sends "kits"
  total: number;
}
```

## Available Components

### Working Components
- **PadGrid** - 4 banks × 12 pads layout (fully functional)
- **Pad** - Individual pad with drag-and-drop (fully functional)
- **SampleBrowser** - Sample search/filter sidebar (fully functional)

### Working Hooks
- `useKits()` - Fetch kit list
- `useCreateKit()` - Create new kit
- `useUpdateKit()` - Update kit metadata
- `useDeleteKit()` - Delete kit
- `useAssignSample()` - Assign sample to pad
- `useSamples()` - Fetch samples for browsing

All hooks are working correctly - the issue is only in the API response adapter.

## Database Schema

**Kits table structure**:
```sql
CREATE TABLE kits (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE kit_samples (
  id INTEGER PRIMARY KEY,
  kit_id INTEGER NOT NULL,
  sample_id INTEGER NOT NULL,
  pad_number INTEGER,  -- 0-47 for 4 banks × 12 pads
  created_at TIMESTAMP,
  FOREIGN KEY (kit_id) REFERENCES kits(id),
  FOREIGN KEY (sample_id) REFERENCES samples(id)
);
```

## API Integration Points

### Kits API Endpoints
- `GET /api/v1/kits` - List all kits (needs adapter fix)
- `POST /api/v1/kits` - Create new kit
- `GET /api/v1/kits/{id}` - Get single kit
- `PATCH /api/v1/kits/{id}` - Update kit
- `DELETE /api/v1/kits/{id}` - Delete kit
- `POST /api/v1/kits/{id}/samples` - Assign sample to pad
- `DELETE /api/v1/kits/{id}/samples/{pad}` - Remove sample from pad

### Samples API (for kit context)
- `GET /api/v1/samples` - Get user's samples (for browsing/assigning)

## Environment & Dependencies

**Frontend Stack**:
- React 18
- React Router v6
- React Query (TanStack Query)
- Axios
- TypeScript

**Backend Stack**:
- FastAPI
- SQLAlchemy async ORM
- Pydantic v2

**Database**: PostgreSQL (localhost:5433)

## Known Issues & Notes

### Secondary Issue (After Fix)
**Type mismatch in Kit samples**:
- Frontend expects `PadAssignment` with `sample_id`
- Backend returns `PadAssignmentInfo` with additional fields

This is lower priority since it won't cause crashes - just may need tweaking after the main fix is applied.

## Timeline

- **Fix Implementation**: 5-10 minutes
- **Testing**: 5-10 minutes
- **Verification**: 5 minutes

**Total**: ~30 minutes including testing

## Dependencies

- No new dependencies needed
- No breaking changes
- No database migrations needed
