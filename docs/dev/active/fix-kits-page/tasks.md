# Fix Kits Page - Task Checklist

## Implementation Tasks

### Task 1: Modify API Response Adapter
- [ ] Open `/react-app/src/api/kits.ts`
- [ ] Locate the `list()` function (around line 13-18)
- [ ] Modify return statement to transform `kits` → `items`:
  ```typescript
  list: async (params?: { page?: number; limit?: number; skip?: number }) => {
    const { data } = await apiClient.get<any>('/kits', { params });
    return {
      items: data.kits,  // Add this line: transform kits → items
      total: data.total,
      skip: data.skip,
      limit: data.limit
    };
  }
  ```
- [ ] Save file

### Task 2: Browser Testing
- [ ] Reload Vite dev server (or auto-reload should trigger)
- [ ] Open http://localhost:5173/kits in browser
- [ ] Verify page loads without errors
- [ ] Check browser console - should see NO errors
- [ ] Verify page displays either:
  - Empty state message (if no kits exist)
  - Kit list with samples (if kits exist)

### Task 3: Functional Testing
- [ ] Verify sample grid renders properly
- [ ] Try creating a new kit (if create button exists)
- [ ] Try navigating to other pages and back to kits
- [ ] Verify no crashes occur

### Task 4: Code Review
- [ ] Verify no other files reference old response structure
- [ ] Check if any unit tests need updating
- [ ] Verify TypeScript types match new response
- [ ] Confirm no breaking changes to other API calls

## Verification Checklist

### Pre-Fix State
- [x] Page is blank
- [x] Console shows error: "Cannot read properties of undefined (reading 'length')"
- [x] React error boundary activates

### Post-Fix Expected State
- [ ] Page loads successfully
- [ ] No console errors
- [ ] Empty state displays OR kit list displays (with 0+ kits)
- [ ] All buttons and interactions work
- [ ] Can navigate away and return to kits page

## Potential Issues to Watch

### If Fix Doesn't Work
1. Check if Vite hot reload picked up the change
   - Manual page refresh may be needed
2. Verify file was saved correctly
3. Check for TypeScript compilation errors in Vite console
4. Inspect network tab - verify API response includes `kits` field

### Secondary Issues
After fix, may encounter:
- Type mismatches in `Kit` interface for `samples` field
- Missing fields in `PadAssignment` type
- These are NON-BLOCKING and can be fixed in follow-up

## Success Metrics

✅ **Critical**: Page loads without JavaScript errors
✅ **Critical**: No React error boundary warning
✅ **High**: Page displays content (empty state or kit list)
✅ **High**: Can interact with page elements
✅ **Medium**: Can navigate to/from kits page without issues

## Rollback Instructions

If something goes wrong:
1. Revert the change in `kits.ts` list() function
2. Return to original: `return data;`
3. Page will crash again but confirms fix was the issue

## Time Estimates

| Task | Estimate | Actual |
|------|----------|--------|
| Code change | 5 min | |
| Browser reload | 2 min | |
| Visual verification | 5 min | |
| Functional testing | 10 min | |
| Code review | 5 min | |
| **Total** | **~30 min** | |

## Sign-Off

- [ ] All tasks completed
- [ ] All verification checks passed
- [ ] No regressions observed
- [ ] Ready for Upload page implementation
