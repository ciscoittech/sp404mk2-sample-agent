# Kit Selection Unmount Debugging Patch - COMPLETE

## ✅ Status: READY FOR TESTING

All debugging instrumentation has been successfully applied to the codebase. TypeScript compilation passes with no errors.

---

## 📦 What Was Added

### Comprehensive Console Logging System

Strategic debug logging added at every critical state change and lifecycle event to trace the exact moment and reason the KitBuilder interface unmounts.

**Log Categories:**
- `[KIT]` - Kit selection events
- `[STATE]` - React state changes
- `[QUERY]` - React Query data changes
- `[RENDER]` - Component render decisions
- `[MUTATION]` - API mutation events
- `[PADGRID]` - PadGrid lifecycle
- `[SAMPLEBROWSER]` - SampleBrowser lifecycle

---

## 📁 Modified Files

### Core Files (4 files modified)

1. **`/react-app/src/pages/KitsPage.tsx`**
   - Added useEffect to track kits query data changes
   - Added useEffect to track selectedKit state changes
   - Added logging to kit button click handler
   - Added logging to conditional render decisions
   - ✅ TypeScript: No errors

2. **`/react-app/src/components/kits/PadGrid.tsx`**
   - Added lifecycle logging (mount/unmount)
   - Added kit prop change logging
   - ✅ TypeScript: No errors

3. **`/react-app/src/components/kits/SampleBrowser.tsx`**
   - Added lifecycle logging (mount/unmount)
   - ✅ TypeScript: No errors

4. **`/react-app/src/hooks/useKits.ts`**
   - Added mutation success logging for createKit
   - Added mutation success logging for assignSample
   - Added mutation success logging for removeSample
   - ✅ TypeScript: No errors

### Documentation Files (3 files created)

1. **`DEBUGGING_PATCH_KIT_UNMOUNT.md`**
   - Complete patch documentation
   - Line-by-line change descriptions
   - Expected log sequences
   - Root cause analysis guide

2. **`DEBUG_KIT_UNMOUNT_APPLIED.md`**
   - Applied changes summary
   - Testing instructions
   - Log interpretation guide
   - Fix recommendations for each scenario

3. **`DEBUG_QUICK_TEST.md`**
   - Quick start guide (30 seconds to test)
   - Visual examples of normal vs bug behavior
   - Checklist for testers
   - Quick fix recommendations

---

## 🚀 How to Test (Quick Version)

```bash
# 1. Start the app
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app
npm run dev

# 2. Open browser (usually http://localhost:5173 or http://localhost:3000)
# 3. Open DevTools Console (F12)
# 4. Navigate to Kits page
# 5. Click a kit button
# 6. Watch console logs for 5 seconds
```

### What You'll See

**If working correctly (no bug):**
```
[KIT] Kit button clicked: kitId= 1
[STATE] selectedKit changed: {newValue: 1}
[PADGRID] Component MOUNTED
[SAMPLEBROWSER] Component MOUNTED
```

**If bug occurs (unmount after 1-2 seconds):**
```
[KIT] Kit button clicked: kitId= 1
[PADGRID] Component MOUNTED

... 1-2 seconds later ...

[STATE] WARNING: selectedKit is undefined!
[PADGRID] Component UNMOUNTING
[SAMPLEBROWSER] Component UNMOUNTING
```

---

## 🔍 What to Look For

### Critical Log Entry
The most important log to find is:
```
[STATE] WARNING: selectedKit is undefined! This will unmount the builder.
```

This indicates the exact moment `selectedKit` state becomes `undefined`, triggering the conditional render to hide the PadGrid and SampleBrowser.

### Sequence Analysis
Look at the 3-5 log entries **immediately before** the WARNING to see what triggered it:

- `[MUTATION] Invalidating kits lists query` → Query invalidation caused it
- `[QUERY] Kits data changed` → Data refetch caused it
- `[RENDER] Conditional render check` → Parent re-render caused it

---

## 🎯 Expected Root Cause

Based on code analysis, the most likely root cause is:

**Query Invalidation Causing Temporary State Loss**

**Sequence:**
1. User clicks kit button → `selectedKit` set to kit ID
2. PadGrid and SampleBrowser mount
3. A mutation fires (createKit, assignSample, or removeSample)
4. Mutation calls `queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() })`
5. React Query refetches the kits list
6. During refetch, `kits` data temporarily becomes `undefined` or stale
7. `currentKit = kits?.items?.find((k) => k.id === selectedKit)` returns `undefined`
8. Conditional render switches to empty state
9. PadGrid and SampleBrowser unmount

---

## 🔧 Likely Fix (After Confirming Root Cause)

### Option 1: Add placeholderData (Recommended)

**File**: `/react-app/src/hooks/useKits.ts`

```typescript
export function useKits(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.kits.list(params),
    queryFn: () => kitsApi.list(params),
    placeholderData: (previousData) => previousData, // 👈 ADD THIS LINE
  });
}
```

This preserves the old kits data during refetch, preventing `currentKit` from becoming undefined.

### Option 2: Use Optimistic Updates

Instead of invalidating queries (which causes refetch), update the cache directly:

**File**: `/react-app/src/hooks/useKits.ts`

```typescript
// In useAssignSample
onSuccess: (response, { kitId, assignment }) => {
  queryClient.setQueryData(
    queryKeys.kits.detail(kitId),
    (old) => {
      if (!old) return old;
      return {
        ...old,
        samples: [...old.samples, { ...assignment, sample: response.sample }]
      };
    }
  );
  // Remove the invalidateQueries call
},
```

### Option 3: Memoize currentKit with Refetch Guard

**File**: `/react-app/src/pages/KitsPage.tsx`

```typescript
import { useMemo } from 'react';

// Inside KitsPage component:
const { data: kits, isLoading, isRefetching } = useKits();

const currentKit = useMemo(() => {
  // If we're refetching and have a selectedKit, try to preserve old data
  if (isRefetching && selectedKit) {
    const found = kits?.items?.find((k) => k.id === selectedKit);
    if (!found) {
      // During refetch, kits might be stale - that's OK, keep showing old data
      return kits?.items?.find((k) => k.id === selectedKit);
    }
    return found;
  }
  return kits?.items?.find((k) => k.id === selectedKit);
}, [kits, selectedKit, isRefetching]);
```

---

## 📊 Test Results Template

When reporting back, please provide:

### Environment
- [ ] App URL: _______________
- [ ] Browser: _______________
- [ ] React version: _______________

### Observations
- [ ] Did the bug occur? YES / NO
- [ ] Time between click and unmount: _____ seconds
- [ ] Number of logs between mount and unmount: _____

### Console Logs
```
(Paste full console log here from [KIT] button click to [PADGRID] unmount)
```

### Root Cause Identified
- [ ] Query invalidation
- [ ] Parent re-render
- [ ] Race condition
- [ ] Other: _______________

---

## 🧹 Cleanup (After Bug Fixed)

Once the bug is fixed and verified, you can optionally remove the debug logging:

### Quick Cleanup
```bash
# Search for all console.log with debug prefixes
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app
grep -r "console.log('\[KIT\]" src/
grep -r "console.log('\[STATE\]" src/
grep -r "console.log('\[QUERY\]" src/
grep -r "console.log('\[RENDER\]" src/
grep -r "console.log('\[MUTATION\]" src/
grep -r "console.log('\[PADGRID\]" src/
grep -r "console.log('\[SAMPLEBROWSER\]" src/
```

Then manually remove the logging statements and any debug-only useEffect hooks.

### Or Keep for Production Debugging
The logging is harmless and could be useful for future debugging. Consider:
- Wrapping in `if (process.env.NODE_ENV === 'development')`
- Converting to a proper logging library
- Keeping as-is for easier troubleshooting

---

## 📚 Documentation Reference

- **Full Patch Details**: `DEBUGGING_PATCH_KIT_UNMOUNT.md`
- **Applied Changes**: `DEBUG_KIT_UNMOUNT_APPLIED.md`
- **Quick Test Guide**: `DEBUG_QUICK_TEST.md`
- **This Summary**: `DEBUG_PATCH_SUMMARY.md`

---

## ✅ Checklist for Tester

- [ ] Read `DEBUG_QUICK_TEST.md` for quick start
- [ ] Start the development server
- [ ] Open browser console
- [ ] Navigate to Kits page
- [ ] Click a kit button
- [ ] Observe console logs for 5 seconds
- [ ] Capture/screenshot the console output
- [ ] Identify if bug occurs (look for WARNING log)
- [ ] Note what happened right before the unmount
- [ ] Report findings with console logs
- [ ] Apply recommended fix if root cause confirmed
- [ ] Verify fix works
- [ ] Optionally clean up debug logging

---

## 🎯 Next Actions

1. **TEST**: Run the test scenario and capture console logs
2. **ANALYZE**: Review logs to confirm root cause
3. **FIX**: Apply the recommended fix (likely placeholderData)
4. **VERIFY**: Re-test to confirm bug is resolved
5. **CLEANUP**: Optionally remove debug logging
6. **DOCUMENT**: Update issue tracker with findings and fix

---

**Created**: 2025-11-16
**Status**: Ready for Testing
**TypeScript**: ✅ No errors
**Files Modified**: 4
**Docs Created**: 3
**Total Lines of Debug Code**: ~150 lines of strategic logging
