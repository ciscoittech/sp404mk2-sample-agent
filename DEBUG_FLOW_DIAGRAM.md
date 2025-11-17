# Kit Selection Unmount Debug Flow - Visual Guide

## 🔍 Complete Event Flow with Debug Logging

```
USER ACTION: Click Kit Button
     │
     ├──> [KIT] Kit button clicked: kitId=1
     │
     ├──> setSelectedKit(1)
     │
     ├──> [STATE] selectedKit changed: {newValue: 1}
     │
     ├──> React re-renders KitsPage
     │
     ├──> [RENDER] Conditional render check: {hasCurrentKit: true, decision: 'SHOWING PadGrid'}
     │
     ├──> PadGrid component mounts
     │
     ├──> [PADGRID] Component MOUNTED: {kitId: 1, kitName: 'My Kit'}
     │
     ├──> SampleBrowser component mounts
     │
     └──> [SAMPLEBROWSER] Component MOUNTED


🟢 NORMAL FLOW STOPS HERE - Components stay mounted
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


🔴 BUG FLOW CONTINUES (1-2 seconds later)

TRIGGER EVENT: Something causes selectedKit to reset
     │
     ├──> POSSIBLE TRIGGER #1: Query Invalidation
     │         │
     │         ├──> User assigns sample to pad
     │         │
     │         ├──> [MUTATION] assignSample success - invalidating queries
     │         │
     │         ├──> queryClient.invalidateQueries(kits.lists())
     │         │
     │         ├──> React Query refetches kits list
     │         │
     │         ├──> [QUERY] Kits data changed: {kitsCount: 2}
     │         │
     │         ├──> During refetch, kits.data temporarily = undefined
     │         │
     │         └──> currentKit = undefined (because kits?.items is undefined)
     │
     ├──> POSSIBLE TRIGGER #2: Parent Re-render
     │         │
     │         ├──> Something higher in tree forces re-render
     │         │
     │         ├──> KitsPage unmounts and remounts
     │         │
     │         └──> selectedKit state lost (not persisted)
     │
     └──> POSSIBLE TRIGGER #3: State Management Bug
               │
               ├──> Some code somewhere calls setSelectedKit(undefined)
               │
               └──> State reset happens unexpectedly


REGARDLESS OF TRIGGER, RESULT IS:
     │
     ├──> selectedKit becomes undefined
     │
     ├──> [STATE] selectedKit changed: {newValue: undefined}
     │
     ├──> [STATE] WARNING: selectedKit is undefined! This will unmount the builder.
     │
     ├──> currentKit = kits?.items?.find((k) => k.id === undefined)
     │
     ├──> currentKit = undefined
     │
     ├──> React re-renders KitsPage
     │
     ├──> [RENDER] Conditional render check: {hasCurrentKit: false, decision: 'SHOWING empty state'}
     │
     ├──> PadGrid component unmounts
     │
     ├──> [PADGRID] Component UNMOUNTING: {reason: 'Component being removed from DOM'}
     │
     ├──> SampleBrowser component unmounts
     │
     └──> [SAMPLEBROWSER] Component UNMOUNTING
```

---

## 🎯 Debug Log Timeline

```
TIME    | LOG CATEGORY    | MESSAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
00:00.0 | [KIT]          | Kit button clicked: kitId= 1 kitName= My Kit
00:00.1 | [STATE]        | selectedKit changed: {newValue: 1, currentKitExists: true}
00:00.2 | [RENDER]       | Conditional render check: {hasCurrentKit: true, decision: 'SHOWING PadGrid'}
00:00.3 | [PADGRID]      | Component MOUNTED: {kitId: 1, samplesCount: 0}
00:00.4 | [SAMPLEBROWSER]| Component MOUNTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 BUG OCCURS HERE (1-2 seconds gap)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
00:01.5 | [MUTATION]     | createKit success: {newKitId: 2} ← LIKELY TRIGGER
00:01.6 | [MUTATION]     | Invalidating kits lists query - WARNING: This will refetch ALL kits
00:01.7 | [MUTATION]     | Query invalidation complete
00:01.8 | [QUERY]        | Kits data changed: {kitsCount: 2, isLoading: false}
00:01.9 | [STATE]        | selectedKit changed: {newValue: undefined} ← ROOT CAUSE
00:02.0 | [STATE]        | WARNING: selectedKit is undefined! This will unmount the builder.
00:02.1 | [RENDER]       | Conditional render check: {hasCurrentKit: false, decision: 'SHOWING empty state'}
00:02.2 | [PADGRID]      | Component UNMOUNTING: {kitId: 1}
00:02.3 | [SAMPLEBROWSER]| Component UNMOUNTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 Component State Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         KitsPage                            │
│                                                             │
│  State: selectedKit = 1                                     │
│  Derived: currentKit = kits.items.find(k => k.id === 1)    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Conditional Render:                                  │  │
│  │                                                        │  │
│  │  {currentKit ? (                                       │  │
│  │    <PadGrid kit={currentKit} />                        │  │
│  │  ) : (                                                 │  │
│  │    <EmptyState />                                      │  │
│  │  )}                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  When: selectedKit = undefined                             │
│  Then: currentKit = undefined                              │
│  Result: Shows <EmptyState /> instead of <PadGrid />       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 React Query Refetch Flow

```
┌────────────────────────────────────────────────────────────┐
│                  React Query State                         │
│                                                            │
│  BEFORE REFETCH:                                           │
│  ┌──────────────────────────────────────────┐             │
│  │ kits.data = {                            │             │
│  │   items: [                               │             │
│  │     {id: 1, name: 'My Kit', samples: []} │             │
│  │   ],                                     │             │
│  │   total: 1                               │             │
│  │ }                                        │             │
│  │ kits.isLoading = false                   │             │
│  └──────────────────────────────────────────┘             │
│                                                            │
│  MUTATION TRIGGERS: invalidateQueries()                    │
│                                                            │
│  DURING REFETCH (⚠️ CRITICAL MOMENT):                      │
│  ┌──────────────────────────────────────────┐             │
│  │ kits.data = undefined  ← BUG HAPPENS     │             │
│  │ kits.isLoading = true                    │             │
│  │ kits.isRefetching = true                 │             │
│  └──────────────────────────────────────────┘             │
│                                                            │
│  AFTER REFETCH:                                            │
│  ┌──────────────────────────────────────────┐             │
│  │ kits.data = {                            │             │
│  │   items: [                               │             │
│  │     {id: 1, name: 'My Kit', samples: []},│             │
│  │     {id: 2, name: 'New Kit', samples: []}│             │
│  │   ],                                     │             │
│  │   total: 2                               │             │
│  │ }                                        │             │
│  │ kits.isLoading = false                   │             │
│  └──────────────────────────────────────────┘             │
└────────────────────────────────────────────────────────────┘
```

---

## 🔧 Fix Comparison

### ❌ Current Code (Has Bug)

```typescript
// In useKits.ts
export function useKits() {
  return useQuery({
    queryKey: queryKeys.kits.list(),
    queryFn: () => kitsApi.list(),
    // No placeholderData - data becomes undefined during refetch
  });
}

// In KitsPage.tsx
const { data: kits } = useKits();
const currentKit = kits?.items?.find((k) => k.id === selectedKit);
// When kits.data is undefined during refetch, currentKit = undefined
// Triggers unmount
```

### ✅ Fixed Code (No Bug)

```typescript
// In useKits.ts
export function useKits() {
  return useQuery({
    queryKey: queryKeys.kits.list(),
    queryFn: () => kitsApi.list(),
    placeholderData: (previousData) => previousData, // ← FIX
    // Keeps old data during refetch, preventing undefined
  });
}

// In KitsPage.tsx
const { data: kits } = useKits();
const currentKit = kits?.items?.find((k) => k.id === selectedKit);
// Even during refetch, kits.data has old data
// currentKit stays defined, no unmount
```

---

## 🎨 Visual State Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     NORMAL FLOW                             │
└─────────────────────────────────────────────────────────────┘

 [Initial State]
      │
      │  User clicks kit
      ▼
 [selectedKit = 1]
      │
      │  Derive currentKit
      ▼
 [currentKit = {id: 1}]
      │
      │  Conditional render
      ▼
 [Render PadGrid]
      │
      │  PadGrid mounts
      ▼
 [✅ STABLE STATE]


┌─────────────────────────────────────────────────────────────┐
│                      BUG FLOW                               │
└─────────────────────────────────────────────────────────────┘

 [Stable State]
      │
      │  Mutation fires
      ▼
 [Query Invalidation]
      │
      │  React Query refetches
      ▼
 [kits.data = undefined] ← CRITICAL MOMENT
      │
      │  Re-derive currentKit
      ▼
 [currentKit = undefined] ← ROOT CAUSE
      │
      │  Conditional render
      ▼
 [Render EmptyState]
      │
      │  PadGrid unmounts
      ▼
 [❌ BUG STATE]
      │
      │  Refetch completes
      ▼
 [kits.data = {...}]
      │
      │  But selectedKit is still undefined!
      ▼
 [Stuck in EmptyState]
```

---

## 🎯 Key Takeaway

**The bug happens because:**

1. `kits.data` temporarily becomes `undefined` during React Query refetch
2. This causes `currentKit` to become `undefined`
3. The conditional render switches to showing the empty state
4. PadGrid and SampleBrowser unmount
5. Even after refetch completes, `selectedKit` is still set, but user sees empty state

**The fix:**

Add `placeholderData: (previousData) => previousData` to the query to keep old data during refetch, preventing the temporary `undefined` state.

---

## 📝 Console Log Examples

### Example 1: Bug Triggered by createKit

```
[KIT] Kit button clicked: kitId= 1 kitName= Test Kit timestamp= 2025-11-16T04:00:00.000Z
[STATE] selectedKit changed: {newValue: 1, timestamp: ..., kitsAvailable: 1, currentKitExists: true}
[RENDER] Conditional render check: {hasCurrentKit: true, selectedKit: 1, decision: 'SHOWING PadGrid'}
[PADGRID] Component MOUNTED: {kitId: 1, kitName: 'Test Kit', samplesCount: 0}
[SAMPLEBROWSER] Component MOUNTED: {timestamp: 2025-11-16T04:00:00.500Z}

// User creates a new kit while viewing Kit 1
[MUTATION] createKit success: {newKitId: 2, timestamp: 2025-11-16T04:00:01.500Z}
[MUTATION] Invalidating kits lists query - WARNING: This will refetch ALL kits
[MUTATION] Query invalidation complete
[QUERY] Kits data changed: {kitsCount: 2, isLoading: false, kitIds: [1, 2]}
[STATE] selectedKit changed: {newValue: undefined, kitsAvailable: 2, currentKitExists: false}
[STATE] WARNING: selectedKit is undefined! This will unmount the builder.
[RENDER] Conditional render check: {hasCurrentKit: false, selectedKit: undefined, decision: 'SHOWING empty state'}
[PADGRID] Component UNMOUNTING: {kitId: 1, kitName: 'Test Kit', reason: 'Component being removed from DOM'}
[SAMPLEBROWSER] Component UNMOUNTING: {timestamp: 2025-11-16T04:00:02.000Z}
```

### Example 2: Bug Triggered by assignSample

```
[KIT] Kit button clicked: kitId= 1 kitName= My Kit timestamp= 2025-11-16T04:00:00.000Z
[STATE] selectedKit changed: {newValue: 1}
[PADGRID] Component MOUNTED: {kitId: 1}
[SAMPLEBROWSER] Component MOUNTED

// User assigns a sample to pad A1
[MUTATION] assignSample success - invalidating queries: {kitId: 1}
[MUTATION] Query invalidation complete
[PADGRID] Kit prop changed: {kitId: 1, samplesCount: 1}  ← Sample added
[QUERY] Kits data changed: {kitsCount: 1}
[STATE] WARNING: selectedKit is undefined!
[PADGRID] Component UNMOUNTING
[SAMPLEBROWSER] Component UNMOUNTING
```

---

This visual guide shows the complete event flow with all debug logging points. Use it alongside the console logs to trace the exact sequence of events.
