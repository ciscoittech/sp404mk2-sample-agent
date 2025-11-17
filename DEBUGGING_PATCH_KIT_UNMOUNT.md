# Kit Selection State Unmount Debugging Patch

## Problem
Kit builder interface unmounts 1-2 seconds after mounting when kit button is clicked. Need to trace exact sequence of events leading to unmount.

## Files to Modify

### 1. KitsPage.tsx - Kit Selection State Tracking

**Location**: `/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app/src/pages/KitsPage.tsx`

#### Change 1: Add logging to kit button click handler (Line 170)

**BEFORE:**
```tsx
<Button
  variant={selectedKit === kit.id ? 'default' : 'outline'}
  onClick={() => setSelectedKit(kit.id)}
  className="pr-8"
>
  {kit.name}
</Button>
```

**AFTER:**
```tsx
<Button
  variant={selectedKit === kit.id ? 'default' : 'outline'}
  onClick={() => {
    console.log('[KIT] Kit button clicked: kitId=', kit.id, 'kitName=', kit.name, 'timestamp=', new Date().toISOString());
    setSelectedKit(kit.id);
  }}
  className="pr-8"
>
  {kit.name}
</Button>
```

**What this logs**: Exact moment user clicks a kit button, which kit was clicked, and timestamp.

---

#### Change 2: Add useEffect to track selectedKit state changes (After line 33)

**BEFORE:**
```tsx
const removeSample = useRemoveSample();

const currentKit = kits?.items?.find((k) => k.id === selectedKit);
```

**AFTER:**
```tsx
const removeSample = useRemoveSample();

// DEBUG: Track selectedKit state changes
React.useEffect(() => {
  console.log('[STATE] selectedKit changed:', {
    newValue: selectedKit,
    timestamp: new Date().toISOString(),
    kitsAvailable: kits?.items?.length || 0,
    currentKitExists: !!kits?.items?.find((k) => k.id === selectedKit)
  });

  if (selectedKit === undefined) {
    console.log('[STATE] WARNING: selectedKit is undefined! This will unmount the builder.');
  }
}, [selectedKit, kits]);

const currentKit = kits?.items?.find((k) => k.id === selectedKit);
```

**What this logs**: Every time selectedKit state changes, logs new value and whether it will cause unmount.

---

#### Change 3: Add logging to currentKit conditional render (Line 210)

**BEFORE:**
```tsx
{currentKit ? (
  <PadGrid
    kit={currentKit}
    onAssignSample={handleAssignSample}
    onRemoveSample={handleRemoveSample}
  />
) : (
  <div className="h-full flex items-center justify-center">
```

**AFTER:**
```tsx
{(() => {
  console.log('[RENDER] Conditional render check:', {
    hasCurrentKit: !!currentKit,
    selectedKit,
    timestamp: new Date().toISOString(),
    decision: currentKit ? 'SHOWING PadGrid' : 'SHOWING empty state'
  });
  return currentKit ? (
    <PadGrid
      kit={currentKit}
      onAssignSample={handleAssignSample}
      onRemoveSample={handleRemoveSample}
    />
  ) : (
    <div className="h-full flex items-center justify-center">
```

**What this logs**: Every render cycle, logs whether PadGrid will be shown or hidden.

---

#### Change 4: Add logging to SampleBrowser conditional render (Line 237)

**BEFORE:**
```tsx
{/* Sample Browser Sidebar */}
{currentKit && (
  <div className="w-96 flex-shrink-0">
```

**AFTER:**
```tsx
{/* Sample Browser Sidebar */}
{(() => {
  console.log('[RENDER] SampleBrowser conditional:', {
    hasCurrentKit: !!currentKit,
    timestamp: new Date().toISOString(),
    decision: currentKit ? 'SHOWING SampleBrowser' : 'HIDING SampleBrowser'
  });
  return currentKit && (
    <div className="w-96 flex-shrink-0">
```

**What this logs**: Whether SampleBrowser will be rendered or hidden.

---

#### Change 5: Add logging to kits query data changes (After line 30)

**BEFORE:**
```tsx
const { data: kits, isLoading } = useKits();
const createKit = useCreateKit();
```

**AFTER:**
```tsx
const { data: kits, isLoading } = useKits();

// DEBUG: Track kits data changes
React.useEffect(() => {
  console.log('[QUERY] Kits data changed:', {
    kitsCount: kits?.items?.length || 0,
    isLoading,
    timestamp: new Date().toISOString(),
    kitIds: kits?.items?.map(k => k.id) || []
  });
}, [kits, isLoading]);

const createKit = useCreateKit();
```

**What this logs**: Every time the kits query data changes, which could trigger re-renders.

---

### 2. useKits.ts - Query Invalidation Tracking

**Location**: `/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app/src/hooks/useKits.ts`

#### Change 6: Add logging to assignSample mutation (Line 85-88)

**BEFORE:**
```tsx
onSuccess: (_, { kitId }) => {
  queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
},
```

**AFTER:**
```tsx
onSuccess: (_, { kitId }) => {
  console.log('[MUTATION] assignSample success - invalidating queries:', {
    kitId,
    timestamp: new Date().toISOString(),
    queryKey: queryKeys.kits.detail(kitId)
  });
  queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
  console.log('[MUTATION] Query invalidation complete');
},
```

**What this logs**: When sample assignment triggers query invalidation (which could refetch and reset state).

---

#### Change 7: Add logging to removeSample mutation (Line 105-107)

**BEFORE:**
```tsx
onSuccess: (_, { kitId }) => {
  queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
},
```

**AFTER:**
```tsx
onSuccess: (_, { kitId }) => {
  console.log('[MUTATION] removeSample success - invalidating queries:', {
    kitId,
    timestamp: new Date().toISOString()
  });
  queryClient.invalidateQueries({ queryKey: queryKeys.kits.detail(kitId) });
  console.log('[MUTATION] Query invalidation complete');
},
```

**What this logs**: When sample removal triggers query invalidation.

---

#### Change 8: Add logging to createKit mutation (Line 30-32)

**BEFORE:**
```tsx
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
},
```

**AFTER:**
```tsx
onSuccess: (newKit) => {
  console.log('[MUTATION] createKit success:', {
    newKitId: newKit.id,
    timestamp: new Date().toISOString()
  });
  console.log('[MUTATION] Invalidating kits lists query');
  queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
  console.log('[MUTATION] WARNING: This will refetch ALL kits - might reset state');
},
```

**What this logs**: When creating a kit triggers a full kits list refetch (THIS IS LIKELY THE CULPRIT).

---

### 3. PadGrid.tsx - Component Lifecycle

**Location**: `/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app/src/components/kits/PadGrid.tsx`

#### Change 9: Add mount/unmount logging (After line 13, inside component)

**BEFORE:**
```tsx
export function PadGrid({ kit, onAssignSample, onRemoveSample }: PadGridProps) {
  const [activeBank, setActiveBank] = useState<'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J'>('A');

  const getPadAssignment = (bank: string, number: number) => {
```

**AFTER:**
```tsx
export function PadGrid({ kit, onAssignSample, onRemoveSample }: PadGridProps) {
  const [activeBank, setActiveBank] = useState<'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J'>('A');

  // DEBUG: Track component lifecycle
  React.useEffect(() => {
    console.log('[PADGRID] Component MOUNTED:', {
      kitId: kit.id,
      kitName: kit.name,
      samplesCount: kit.samples.length,
      timestamp: new Date().toISOString()
    });

    return () => {
      console.log('[PADGRID] Component UNMOUNTING:', {
        kitId: kit.id,
        kitName: kit.name,
        timestamp: new Date().toISOString(),
        reason: 'Component being removed from DOM'
      });
    };
  }, []);

  // DEBUG: Track kit prop changes
  React.useEffect(() => {
    console.log('[PADGRID] Kit prop changed:', {
      kitId: kit.id,
      kitName: kit.name,
      samplesCount: kit.samples.length,
      timestamp: new Date().toISOString()
    });
  }, [kit]);

  const getPadAssignment = (bank: string, number: number) => {
```

**What this logs**: When PadGrid mounts, unmounts, and when its kit prop changes.

---

### 4. SampleBrowser.tsx - Component Lifecycle

**Location**: `/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app/src/components/kits/SampleBrowser.tsx`

#### Change 10: Add mount/unmount logging (After line 18, inside component)

**BEFORE:**
```tsx
export function SampleBrowser({ onAddToKit }: SampleBrowserProps) {
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState<string>();
  const [bpmRange, setBpmRange] = useState<[number, number]>();

  const { data: samples, isLoading } = useSamples({
```

**AFTER:**
```tsx
export function SampleBrowser({ onAddToKit }: SampleBrowserProps) {
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState<string>();
  const [bpmRange, setBpmRange] = useState<[number, number]>();

  // DEBUG: Track component lifecycle
  React.useEffect(() => {
    console.log('[SAMPLEBROWSER] Component MOUNTED:', {
      timestamp: new Date().toISOString()
    });

    return () => {
      console.log('[SAMPLEBROWSER] Component UNMOUNTING:', {
        timestamp: new Date().toISOString(),
        reason: 'Component being removed from DOM'
      });
    };
  }, []);

  const { data: samples, isLoading } = useSamples({
```

**What this logs**: When SampleBrowser mounts and unmounts.

---

## How to Apply This Patch

1. **Add React import** to all modified files if not already present:
   ```tsx
   import React from 'react';
   ```

2. **Apply changes sequentially** to each file

3. **Test the debugging**:
   - Open browser console (F12)
   - Click on a kit button
   - Watch the console logs in real-time
   - Observe the exact sequence of events

## Expected Log Sequence (Normal Behavior)

```
[KIT] Kit button clicked: kitId=1 kitName=Test Kit timestamp=...
[STATE] selectedKit changed: {newValue: 1, ...}
[RENDER] Conditional render check: {hasCurrentKit: true, decision: 'SHOWING PadGrid'}
[RENDER] SampleBrowser conditional: {hasCurrentKit: true, decision: 'SHOWING SampleBrowser'}
[PADGRID] Component MOUNTED: {kitId: 1, ...}
[SAMPLEBROWSER] Component MOUNTED: {...}
```

## Expected Log Sequence (Bug - Unmount Happening)

```
[KIT] Kit button clicked: kitId=1 kitName=Test Kit timestamp=...
[STATE] selectedKit changed: {newValue: 1, ...}
[RENDER] Conditional render check: {hasCurrentKit: true, decision: 'SHOWING PadGrid'}
[PADGRID] Component MOUNTED: {kitId: 1, ...}
[SAMPLEBROWSER] Component MOUNTED: {...}

... 1-2 seconds later ...

[MUTATION] createKit success: ... <-- OR assignSample, etc.
[MUTATION] Invalidating kits lists query
[MUTATION] WARNING: This will refetch ALL kits - might reset state
[QUERY] Kits data changed: {kitsCount: 2, ...}
[STATE] selectedKit changed: {newValue: undefined, ...} <-- CULPRIT!
[STATE] WARNING: selectedKit is undefined! This will unmount the builder.
[RENDER] Conditional render check: {hasCurrentKit: false, decision: 'SHOWING empty state'}
[PADGRID] Component UNMOUNTING: {reason: 'Component being removed from DOM'}
[SAMPLEBROWSER] Component UNMOUNTING: {reason: 'Component being removed from DOM'}
```

## What to Look For

1. **Exact moment selectedKit becomes undefined**
2. **What event precedes it** (mutation? query refetch?)
3. **Timing between events** (is it exactly after a query invalidation?)
4. **Whether kits data changes** (does refetch cause state reset?)

## Most Likely Root Causes

Based on code analysis, these are the most likely culprits:

### 1. Query Invalidation After Mutations (HIGH PROBABILITY)
- `useAssignSample` invalidates `queryKeys.kits.detail(kitId)`
- `useCreateKit` invalidates `queryKeys.kits.lists()`
- **Problem**: If the list query refetches, it might be resetting component state

### 2. State Not Preserved During Refetch (MEDIUM PROBABILITY)
- React Query might be causing re-render with stale data
- `currentKit` becomes undefined during refetch window

### 3. Parent Component Re-render (LOW PROBABILITY)
- Something higher up the tree is forcing full page re-render
- State is lost during parent remount

## Next Steps After Identifying Root Cause

Once logs show the exact sequence:

1. **If it's query invalidation**:
   - Change to optimistic updates instead of full refetch
   - Use `queryClient.setQueryData` to update cache directly
   - Preserve `selectedKit` state during refetches

2. **If it's component unmounting**:
   - Find what's causing parent unmount
   - Add key props to prevent unnecessary unmounts

3. **If it's state timing**:
   - Add defensive checks for `currentKit` existence
   - Implement loading states during refetch
