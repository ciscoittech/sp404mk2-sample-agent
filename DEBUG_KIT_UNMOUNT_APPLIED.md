# Kit Selection Unmount Debugging - APPLIED PATCH

## Status: ✅ DEBUGGING PATCH APPLIED

All debugging logging has been successfully applied to the codebase.

---

## Files Modified

### 1. `/react-app/src/pages/KitsPage.tsx`
**Changes Applied:**
- ✅ Added `useEffect` import
- ✅ Added logging to track kits query data changes
- ✅ Added logging to track selectedKit state changes with warning for undefined
- ✅ Added logging to kit button click handler
- ✅ Added logging to PadGrid conditional render decision
- ✅ Added logging to SampleBrowser conditional render decision

### 2. `/react-app/src/components/kits/PadGrid.tsx`
**Changes Applied:**
- ✅ Added `useEffect` import
- ✅ Added logging for component mount/unmount lifecycle
- ✅ Added logging for kit prop changes

### 3. `/react-app/src/components/kits/SampleBrowser.tsx`
**Changes Applied:**
- ✅ Added `useEffect` import
- ✅ Added logging for component mount/unmount lifecycle

### 4. `/react-app/src/hooks/useKits.ts`
**Changes Applied:**
- ✅ Added logging to `createKit` mutation success with invalidation warning
- ✅ Added logging to `assignSample` mutation success
- ✅ Added logging to `removeSample` mutation success

---

## How to Test

### Step 1: Start the Development Server
```bash
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app
npm run dev
```

### Step 2: Open Browser Console
1. Open the application in your browser
2. Open Developer Tools (F12 or Cmd+Option+I)
3. Go to the Console tab
4. Clear the console (Cmd+K or Ctrl+L)

### Step 3: Reproduce the Bug
1. Navigate to the Kits page
2. Click on a kit button to select it
3. Watch the console logs in real-time
4. Observe if the PadGrid unmounts 1-2 seconds later

---

## Log Prefixes and What They Mean

### [KIT] - Kit Selection
- `Kit button clicked` - User clicked a kit button, shows which kit

### [STATE] - State Changes
- `selectedKit changed` - The selectedKit state variable changed
- `WARNING: selectedKit is undefined!` - Critical: This will cause unmount

### [QUERY] - React Query Data
- `Kits data changed` - The kits query data refetched or updated

### [RENDER] - Render Decisions
- `Conditional render check` - Decision to show/hide PadGrid
- `SampleBrowser conditional` - Decision to show/hide SampleBrowser

### [MUTATION] - Mutation Events
- `createKit success` - New kit created, triggering invalidation
- `assignSample success` - Sample assigned to pad, triggering invalidation
- `removeSample success` - Sample removed from pad, triggering invalidation
- `Invalidating kits lists query` - About to refetch all kits (WATCH THIS)
- `Query invalidation complete` - Invalidation finished

### [PADGRID] - Component Lifecycle
- `Component MOUNTED` - PadGrid just appeared in DOM
- `Kit prop changed` - PadGrid received new kit data
- `Component UNMOUNTING` - PadGrid being removed from DOM (THE BUG!)

### [SAMPLEBROWSER] - Component Lifecycle
- `Component MOUNTED` - SampleBrowser just appeared in DOM
- `Component UNMOUNTING` - SampleBrowser being removed from DOM (THE BUG!)

---

## Expected Normal Behavior Logs

When clicking a kit button (SHOULD work like this):

```
[KIT] Kit button clicked: kitId= 1 kitName= My First Kit timestamp= 2025-11-16T...
[STATE] selectedKit changed: {newValue: 1, timestamp: ..., kitsAvailable: 2, currentKitExists: true}
[RENDER] Conditional render check: {hasCurrentKit: true, selectedKit: 1, decision: 'SHOWING PadGrid'}
[RENDER] SampleBrowser conditional: {hasCurrentKit: true, decision: 'SHOWING SampleBrowser'}
[PADGRID] Component MOUNTED: {kitId: 1, kitName: 'My First Kit', samplesCount: 0}
[SAMPLEBROWSER] Component MOUNTED: {timestamp: ...}
```

---

## Expected Bug Behavior Logs

If the bug happens (components unmount 1-2 seconds later):

```
[KIT] Kit button clicked: kitId= 1 kitName= My First Kit timestamp= ...
[STATE] selectedKit changed: {newValue: 1, ...}
[RENDER] Conditional render check: {hasCurrentKit: true, decision: 'SHOWING PadGrid'}
[PADGRID] Component MOUNTED: {kitId: 1, ...}
[SAMPLEBROWSER] Component MOUNTED: {...}

... 1-2 seconds later ...

[MUTATION] createKit success: {newKitId: 1, ...}  <-- OR assignSample, etc.
[MUTATION] Invalidating kits lists query - WARNING: This will refetch ALL kits
[MUTATION] Query invalidation complete
[QUERY] Kits data changed: {kitsCount: 2, ...}
[STATE] selectedKit changed: {newValue: undefined, ...}  <-- ROOT CAUSE!
[STATE] WARNING: selectedKit is undefined! This will unmount the builder.
[RENDER] Conditional render check: {hasCurrentKit: false, decision: 'SHOWING empty state'}
[PADGRID] Component UNMOUNTING: {reason: 'Component being removed from DOM'}
[SAMPLEBROWSER] Component UNMOUNTING: {reason: 'Component being removed from DOM'}
```

---

## What to Look For

### 1. The Unmount Trigger
Look for the exact log entry that shows `selectedKit` becoming `undefined`:
```
[STATE] selectedKit changed: {newValue: undefined, ...}
[STATE] WARNING: selectedKit is undefined! This will unmount the builder.
```

### 2. What Happened Right Before
Look at the 3-5 log entries BEFORE the selectedKit became undefined:
- Was it a mutation? (`[MUTATION]`)
- Was it a query refetch? (`[QUERY] Kits data changed`)
- Was it a render? (`[RENDER]`)

### 3. Timing Information
Note the timestamps to see exact delay:
- Time of kit button click
- Time of unmount
- Time of any mutations/queries in between

---

## Most Likely Root Causes (Based on Code Analysis)

### 1. Query Invalidation Resetting State (HIGH PROBABILITY)
**Symptom**: You'll see this sequence:
```
[MUTATION] Invalidating kits lists query - WARNING: This will refetch ALL kits
[QUERY] Kits data changed: {kitsCount: ..., ...}
[STATE] selectedKit changed: {newValue: undefined, ...}
```

**Why**: When `queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() })` runs, it refetches the kits list. During the refetch, React Query might temporarily set the data to `undefined` or stale data, causing `currentKit` to become undefined.

**Fix**:
- Use optimistic updates instead of full refetch
- Preserve `selectedKit` state during refetches
- Use `queryClient.setQueryData` for immediate cache updates

### 2. Parent Component Re-render (MEDIUM PROBABILITY)
**Symptom**: You'll see:
```
[PADGRID] Component UNMOUNTING: ...
[PADGRID] Component MOUNTED: ...  (immediate remount with same kit)
```

**Why**: Something higher in the component tree is forcing a full re-render, causing child components to unmount and remount.

**Fix**:
- Add React.memo() to components
- Check parent component state management
- Add stable key props

### 3. Race Condition in Mutations (LOW PROBABILITY)
**Symptom**: Multiple mutations firing in rapid succession:
```
[MUTATION] assignSample success
[MUTATION] createKit success
[MUTATION] removeSample success
```

**Why**: If multiple mutations fire quickly, they might invalidate queries in a way that causes state loss.

**Fix**:
- Debounce mutations
- Queue mutations instead of firing simultaneously
- Use optimistic UI updates

---

## Next Steps After Identifying Root Cause

### If It's Query Invalidation (Most Likely)

**Problem**: `invalidateQueries` causes full refetch, resetting state during refetch window.

**Solution Options**:

1. **Option A: Preserve State During Refetch**
```typescript
// In KitsPage.tsx
const { data: kits, isLoading, isRefetching } = useKits();

// Keep the old currentKit during refetch
const currentKit = useMemo(() => {
  if (isRefetching && selectedKit) {
    // During refetch, try to keep old data
    return kits?.items?.find((k) => k.id === selectedKit);
  }
  return kits?.items?.find((k) => k.id === selectedKit);
}, [kits, selectedKit, isRefetching]);
```

2. **Option B: Use Optimistic Updates**
```typescript
// In useKits.ts - assignSample
onSuccess: (response, { kitId, assignment }) => {
  // Update cache directly instead of refetching
  queryClient.setQueryData(
    queryKeys.kits.detail(kitId),
    (old) => {
      if (!old) return old;
      return {
        ...old,
        samples: [...old.samples, assignment]
      };
    }
  );
  // Don't invalidate - we already updated the cache
},
```

3. **Option C: Use placeholderData**
```typescript
// In useKits.ts - list kits
export function useKits(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.kits.list(params),
    queryFn: () => kitsApi.list(params),
    placeholderData: (previousData) => previousData, // Keep old data during refetch
  });
}
```

### If It's Parent Re-render

**Solution**: Memoize components
```typescript
// In kits/PadGrid.tsx
export const PadGrid = React.memo(function PadGrid({ kit, onAssignSample, onRemoveSample }: PadGridProps) {
  // ... component code
});

// In kits/SampleBrowser.tsx
export const SampleBrowser = React.memo(function SampleBrowser({ onAddToKit }: SampleBrowserProps) {
  // ... component code
});
```

### If It's Race Condition

**Solution**: Queue mutations
```typescript
// Create a mutation queue
const mutationQueue = useRef<Promise<any>>(Promise.resolve());

const handleAssignSample = async (...args) => {
  mutationQueue.current = mutationQueue.current.then(() =>
    assignSample.mutateAsync(...)
  );
  return mutationQueue.current;
};
```

---

## Testing the Fix

After applying the fix:

1. **Remove the debug logging** (or keep for future debugging)
2. **Test the user flow**:
   - Create a new kit
   - Click to select it
   - Verify PadGrid stays mounted
   - Assign samples to pads
   - Verify no unmounting happens
3. **Check edge cases**:
   - Rapidly clicking between kits
   - Assigning multiple samples quickly
   - Creating kit while one is selected

---

## Reverting Debug Logging (Optional)

If you want to remove the debug logging after identifying the issue:

1. **Remove all console.log statements** with prefixes:
   - `[KIT]`
   - `[STATE]`
   - `[QUERY]`
   - `[RENDER]`
   - `[MUTATION]`
   - `[PADGRID]`
   - `[SAMPLEBROWSER]`

2. **Remove added useEffect hooks** that only contain logging

3. **Restore IIFE wrappers** to simple conditionals:
```typescript
// Change this:
{(() => {
  console.log(...);
  return currentKit ? <PadGrid /> : <EmptyState />;
})()}

// Back to this:
{currentKit ? <PadGrid /> : <EmptyState />}
```

---

## Summary

This debugging patch adds comprehensive logging to trace the exact moment and reason why the KitBuilder interface unmounts. The logs are designed to show:

1. **WHEN** the unmount happens (exact timestamp)
2. **WHY** it happens (what state change or event triggered it)
3. **WHAT** the sequence of events was leading up to it
4. **WHERE** the root cause is (mutation, query, state change, etc.)

Run the test, collect the console logs, and analyze the sequence to identify the exact root cause. The most likely culprit is query invalidation causing a refetch that temporarily resets the kits data to undefined, which causes `currentKit` to become undefined, which triggers the conditional render to show the empty state instead of the PadGrid.
