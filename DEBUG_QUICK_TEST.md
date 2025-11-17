# Quick Debug Test Guide - Kit Unmount Issue

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start the app
cd react-app && npm run dev

# 2. Open browser at http://localhost:3000
# 3. Open DevTools Console (F12)
# 4. Navigate to Kits page
# 5. Click a kit button
# 6. Watch console logs
```

---

## 🔍 What to Look For in Console

### ✅ NORMAL (Working Correctly)
```
[KIT] Kit button clicked: kitId= 1
[STATE] selectedKit changed: {newValue: 1}
[PADGRID] Component MOUNTED
[SAMPLEBROWSER] Component MOUNTED
(No unmount happens)
```

### ❌ BUG (Unmounting After 1-2 Seconds)
```
[KIT] Kit button clicked: kitId= 1
[PADGRID] Component MOUNTED

... 1-2 seconds later ...

[STATE] WARNING: selectedKit is undefined!  👈 ROOT CAUSE
[PADGRID] Component UNMOUNTING
```

---

## 🎯 Key Log Entries to Capture

1. **The moment you click the kit button**
   - Look for: `[KIT] Kit button clicked`

2. **When selectedKit becomes undefined**
   - Look for: `[STATE] WARNING: selectedKit is undefined!`

3. **What happened RIGHT BEFORE selectedKit became undefined**
   - Usually 2-3 lines above the WARNING
   - Look for: `[MUTATION]` or `[QUERY]` entries

4. **The exact unmount log**
   - Look for: `[PADGRID] Component UNMOUNTING`

---

## 📋 Quick Checklist

- [ ] App is running on http://localhost:3000
- [ ] Browser console is open and cleared
- [ ] You can see the Kits page
- [ ] There are kits available to click
- [ ] You clicked a kit button
- [ ] You watched the console for 5 seconds after clicking
- [ ] You captured/screenshot the console logs

---

## 📸 What to Report Back

**Copy/paste the entire console log output** starting from:
```
[KIT] Kit button clicked...
```

Through to:
```
[PADGRID] Component UNMOUNTING...
```

**Include timestamps** to show the delay between events.

---

## 🔧 Most Likely Fix (After Confirming Bug)

If you see the pattern above, the fix is likely:

**File**: `/react-app/src/hooks/useKits.ts`

**Change**: In `useAssignSample`, `useRemoveSample`, and `useCreateKit`, replace:
```typescript
queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() });
```

With:
```typescript
// Don't invalidate the list - use optimistic update instead
// This prevents the kits data from temporarily becoming undefined
```

Or add `placeholderData` to preserve old data during refetch:
```typescript
// In useKits hook
export function useKits(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.kits.list(params),
    queryFn: () => kitsApi.list(params),
    placeholderData: (previousData) => previousData, // 👈 ADD THIS
  });
}
```

---

## 📞 Need Help?

If you see different log patterns than described above, capture the full console output and we'll analyze the actual sequence of events.
