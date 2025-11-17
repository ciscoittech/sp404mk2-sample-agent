# Fix Kits Page - Implementation Plan

**Priority**: CRITICAL (Currently broken - crashes on load)
**Effort**: 30 minutes
**Status**: Ready for implementation

## Problem Statement

The Kits page crashes when loaded with error:
```
Cannot read properties of undefined (reading 'length')
React error: An error occurred in the <KitsPage> component
```

**Root Cause**: API response structure mismatch
- Backend returns response with `kits` field
- Frontend code expects `items` field
- Causes undefined array access at lines 160, 221, 225 in KitsPage.tsx

## Solution Overview

Add a simple response adapter in the kits API client to transform backend response format to match frontend expectations. This is a **one-file, 5-line fix**.

## Technical Details

### Backend API Response
**Endpoint**: `GET /api/v1/kits`
**Returns**:
```json
{
  "kits": [
    { "id": 1, "name": "Kit Name", "samples": [...] }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Frontend Expectation
```typescript
{
  items: Kit[],
  total: number
}
```

### The Fix
In `/react-app/src/api/kits.ts`, modify the `list()` function to transform the response:

```typescript
list: async (params?: { page?: number; limit?: number; skip?: number }) => {
  const { data } = await apiClient.get<any>('/kits', { params });
  return {
    items: data.kits,  // Transform: kits → items
    total: data.total,
    skip: data.skip,
    limit: data.limit
  };
}
```

## Files to Modify

1. **`/react-app/src/api/kits.ts`** - Add response adapter
   - Lines: Around line 13-18 in the list function
   - Change: 1 function body modification
   - Risk: Very low (isolated API layer change)

## Testing Strategy

### Before Fix
- Navigate to http://localhost:5173/kits
- Observe: Blank page, console error

### After Fix
- Navigate to http://localhost:5173/kits
- Verify: Page loads without errors
- Verify: Sample grid renders (empty state if no kits)
- Verify: Browser console has no errors

## Success Criteria

✅ Kits page loads without errors
✅ Page displays empty state or kit list (if kits exist)
✅ No console errors
✅ All kit operations respond to API correctly

## Rollback Plan

If needed, revert the change in kits.ts list() function - single function change makes rollback trivial.

## Next Steps

1. Apply the 5-line fix to kits.ts
2. Run browser tests
3. Verify page loads cleanly
4. Move to Upload page implementation
