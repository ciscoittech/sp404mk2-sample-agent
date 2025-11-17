# Kit Selection Unmount Bug - Debugging Documentation Index

## 🎯 Quick Navigation

**Need to test right now?** → Start with `DEBUG_QUICK_TEST.md`

**Want to understand the changes?** → Read `DEBUG_PATCH_SUMMARY.md`

**Need visual explanation?** → See `DEBUG_FLOW_DIAGRAM.md`

**Want all technical details?** → Check `DEBUG_KIT_UNMOUNT_APPLIED.md`

---

## 📚 Documentation Files

### 1. **DEBUG_QUICK_TEST.md** ⚡ START HERE
**Purpose**: Quick 30-second test guide
**Use when**: You just want to reproduce and capture the bug
**Contains**:
- Quick start commands
- What to look for in console
- Key log entries to capture
- Visual examples of normal vs bug behavior
- Quick fix recommendations

**Time to read**: 2 minutes

---

### 2. **DEBUG_PATCH_SUMMARY.md** 📋 OVERVIEW
**Purpose**: Complete overview of debugging patch
**Use when**: You want to understand what was changed and why
**Contains**:
- Status and file modification summary
- Testing instructions
- Expected root cause analysis
- Fix recommendations for each scenario
- Cleanup instructions
- Tester checklist

**Time to read**: 5 minutes

---

### 3. **DEBUG_FLOW_DIAGRAM.md** 🎨 VISUAL GUIDE
**Purpose**: Visual explanation of event flow
**Use when**: You want to understand HOW the bug happens
**Contains**:
- Complete event flow diagram
- Debug log timeline
- Component state flow charts
- React Query refetch flow
- Fix comparison (before/after)
- Visual state diagrams
- Console log examples

**Time to read**: 5 minutes

---

### 4. **DEBUG_KIT_UNMOUNT_APPLIED.md** 🔧 TECHNICAL
**Purpose**: Complete technical reference
**Use when**: You need detailed implementation info
**Contains**:
- Detailed file modification list
- Testing instructions
- Log prefix meanings
- Expected log sequences (normal vs bug)
- Root cause deep dive
- Fix options with code examples
- Revert instructions

**Time to read**: 10 minutes

---

### 5. **DEBUGGING_PATCH_KIT_UNMOUNT.md** 📝 ORIGINAL PLAN
**Purpose**: Original patch specification
**Use when**: You want to see the original plan/diff
**Contains**:
- Line-by-line change descriptions
- Before/after code snippets
- Explanation of each log entry
- What each change captures
- Expected log sequences

**Time to read**: 15 minutes

---

## 🚀 Recommended Reading Order

### For Testers
1. `DEBUG_QUICK_TEST.md` - Quick start
2. `DEBUG_FLOW_DIAGRAM.md` - Understand what to look for
3. `DEBUG_PATCH_SUMMARY.md` - Report findings

### For Developers
1. `DEBUG_PATCH_SUMMARY.md` - Overview
2. `DEBUG_FLOW_DIAGRAM.md` - Understand the bug
3. `DEBUG_KIT_UNMOUNT_APPLIED.md` - Implementation details
4. `DEBUGGING_PATCH_KIT_UNMOUNT.md` - Original specification

### For Quick Fix
1. `DEBUG_QUICK_TEST.md` - Reproduce bug
2. `DEBUG_PATCH_SUMMARY.md` → Section "Likely Fix"
3. Apply the fix (usually adding `placeholderData`)

---

## 🎯 Common Scenarios

### Scenario 1: "I need to test this NOW"
→ Open `DEBUG_QUICK_TEST.md`
→ Follow the 5 steps
→ Capture console logs
→ Report back

### Scenario 2: "I captured the logs, what do they mean?"
→ Open `DEBUG_FLOW_DIAGRAM.md`
→ Compare your logs to the examples
→ Identify which scenario matches
→ Open `DEBUG_PATCH_SUMMARY.md` → Section "Likely Fix"

### Scenario 3: "I want to understand the code changes"
→ Open `DEBUG_KIT_UNMOUNT_APPLIED.md`
→ Review "Files Modified" section
→ Check TypeScript compilation status
→ Review fix options

### Scenario 4: "How do I fix this?"
→ Open `DEBUG_PATCH_SUMMARY.md`
→ Go to "Likely Fix (After Confirming Root Cause)"
→ Choose Option 1 (placeholderData) - simplest
→ Apply the 1-line change
→ Re-test

### Scenario 5: "I fixed it, how do I clean up?"
→ Open `DEBUG_PATCH_SUMMARY.md`
→ Go to "Cleanup (After Bug Fixed)"
→ Follow cleanup instructions
→ Or keep logging for future debugging

---

## 📊 File Status

| File | Status | TypeScript | Purpose |
|------|--------|-----------|---------|
| `react-app/src/pages/KitsPage.tsx` | ✅ Modified | ✅ No errors | Kit selection state tracking |
| `react-app/src/components/kits/PadGrid.tsx` | ✅ Modified | ✅ No errors | Component lifecycle tracking |
| `react-app/src/components/kits/SampleBrowser.tsx` | ✅ Modified | ✅ No errors | Component lifecycle tracking |
| `react-app/src/hooks/useKits.ts` | ✅ Modified | ✅ No errors | Mutation/query tracking |

**Total Debug Code**: ~150 lines of strategic console.log statements
**TypeScript Compilation**: ✅ Passes with no errors
**Ready for Testing**: ✅ Yes

---

## 🔍 What Each File Tells You

### KitsPage.tsx Logs
**Tell you**: When state changes, what triggers re-renders, render decisions

**Look for**:
- `[KIT]` - User interactions
- `[STATE]` - State changes (especially selectedKit becoming undefined)
- `[QUERY]` - Data refetches
- `[RENDER]` - Conditional render decisions

### PadGrid.tsx Logs
**Tell you**: When component mounts/unmounts, when props change

**Look for**:
- `[PADGRID] Component MOUNTED` - Component appeared
- `[PADGRID] Component UNMOUNTING` - Component disappeared (THE BUG)
- `[PADGRID] Kit prop changed` - New kit data received

### SampleBrowser.tsx Logs
**Tell you**: When sidebar mounts/unmounts

**Look for**:
- `[SAMPLEBROWSER] Component MOUNTED`
- `[SAMPLEBROWSER] Component UNMOUNTING`

### useKits.ts Logs
**Tell you**: When mutations complete, when queries invalidate

**Look for**:
- `[MUTATION] createKit success`
- `[MUTATION] Invalidating kits lists query` - LIKELY TRIGGER
- `[MUTATION] assignSample success`
- `[MUTATION] removeSample success`

---

## 🎯 Expected Root Cause

**90% Confidence: Query Invalidation**

The bug is most likely caused by:
1. Mutation calls `queryClient.invalidateQueries({ queryKey: queryKeys.kits.lists() })`
2. React Query refetches the kits list
3. During refetch, `kits.data` temporarily becomes `undefined`
4. `currentKit = kits?.items?.find(...)` returns `undefined`
5. Conditional render switches to empty state
6. PadGrid unmounts

**Fix**: Add `placeholderData: (previousData) => previousData` to the `useKits` query.

---

## 🔧 Quick Fix Preview

**File**: `/react-app/src/hooks/useKits.ts`

**Line**: ~8-11 (in the `useKits` function)

**Change**:
```typescript
export function useKits(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.kits.list(params),
    queryFn: () => kitsApi.list(params),
    placeholderData: (previousData) => previousData, // ← ADD THIS LINE
  });
}
```

**Impact**: Prevents `kits.data` from becoming `undefined` during refetch, keeping `currentKit` defined.

**Risk**: Very low - this is a standard React Query pattern for preventing flash of empty states.

---

## 📞 Support

### If you get stuck:
1. Check `DEBUG_QUICK_TEST.md` for troubleshooting
2. Review `DEBUG_FLOW_DIAGRAM.md` to understand expected behavior
3. Capture full console logs and share for analysis

### If logs don't match expected patterns:
1. Capture complete console output
2. Note exact user actions taken
3. Include browser/environment info
4. Share in issue tracker with logs

---

## ✅ Success Criteria

### Bug is Fixed When:
- [ ] User clicks kit button
- [ ] PadGrid and SampleBrowser mount
- [ ] Components stay mounted (no unmount after 1-2 seconds)
- [ ] User can interact with pads
- [ ] Assigning samples doesn't cause unmount
- [ ] Creating new kits doesn't cause unmount
- [ ] No `[STATE] WARNING: selectedKit is undefined!` in logs

---

## 🎉 Next Steps After Fix

1. ✅ Verify fix works
2. ✅ Test edge cases (rapid kit switching, multiple mutations)
3. ✅ Optionally clean up debug logging
4. ✅ Update issue tracker
5. ✅ Document the fix in changelog
6. ✅ Consider adding unit tests for state preservation

---

**Created**: 2025-11-16
**Status**: Ready for Testing
**Estimated Time to Fix**: 5 minutes (after confirming root cause)
**Difficulty**: Easy (1-line change)
