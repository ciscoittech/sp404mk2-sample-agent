# User Journey Testing: Drag-Drop Kit Builder with 10-Bank Support

**Test Date**: 2025-11-16
**Build Version**: React + FastAPI (Async)
**Database**: PostgreSQL with 6,557 samples
**Target**: 160-pad kit builder (10 banks A-J × 16 pads)
**Audio System**: Global AudioContext with WaveSurfer for audio isolation

---

## Overview

This document specifies 8 critical user journeys for the SP-404MK2 drag-drop kit builder. Each journey includes:
- **Preconditions**: Initial state required
- **Steps**: Detailed actions user takes
- **Expected Behavior**: What should happen at each step
- **Pass Criteria**: How to verify success
- **Screenshots**: Visual confirmation points

---

## Journey 1: Application Load and Navigation to Kits Page

**Preconditions**:
- Browser: Chrome/Chromium
- URL: http://localhost:5173/
- Backend: Running on http://localhost:8000
- Database: Connected with sample data

**Steps**:

1. Open http://localhost:5173/ in browser
   - **Expected**: Dashboard page loads with logo, navigation menu visible
   - **Visual**: Main layout with sidebar nav on left

2. Verify page loads without console errors
   - **Expected**: Console has no red error messages
   - **Check**: Open Chrome DevTools Console tab

3. Click "Kits" in navigation menu
   - **Expected**: Navigate to /kits page
   - **Visual**: Page shows "Kits" title, kit list or empty state

4. Verify Kits page loads
   - **Expected**: Page displays kit creation UI or existing kits list
   - **Check**: No loading spinners visible, page interactive

**Pass Criteria**:
- ✅ Dashboard loads without errors
- ✅ Navigation menu visible and clickable
- ✅ Kits page loads on click
- ✅ No console errors in DevTools
- ✅ Page is interactive (buttons responsive)

---

## Journey 2: Browse Samples and Apply Filters

**Preconditions**:
- On Kits page or Samples page
- Backend API responding
- Sample database populated (6,557 samples)

**Steps**:

1. Navigate to Samples page
   - **Expected**: Samples page loads with filter panel on left
   - **Visual**: Genre filters, BPM slider, search box visible

2. Apply genre filter (e.g., "Hip-Hop")
   - **Expected**: Sample list updates to show only Hip-Hop samples
   - **Check**: Count changes in UI, samples have "Hip-Hop" tags

3. Adjust BPM slider (e.g., 80-100 BPM)
   - **Expected**: Sample list updates to show only 80-100 BPM samples
   - **Check**: BPM values in displayed samples fall within range

4. Search for keyword (e.g., "kick")
   - **Expected**: Sample list filters to show only samples matching "kick"
   - **Check**: All visible samples have "kick" in title or tags

5. Clear all filters
   - **Expected**: Samples reset to full library view
   - **Check**: Count increases, various genres and BPMs visible again

**Pass Criteria**:
- ✅ Samples page loads with filters
- ✅ Genre filter reduces sample count appropriately
- ✅ BPM slider filters by tempo range
- ✅ Search works with keyword matching
- ✅ Clear filters restores full list
- ✅ No API errors in Network tab

---

## Journey 3: Drag Sample from Library to Pad in Bank A

**Preconditions**:
- On Kits page with a kit open (or create new kit first)
- Pad grid visible with banks A-J tabs
- Sample library or samples panel visible
- Samples available for drag

**Steps**:

1. Click bank "A" tab to ensure bank A pads visible
   - **Expected**: Grid shows pads A1-A16 in 4 columns
   - **Visual**: Tab is highlighted/active

2. Identify a sample to drag (e.g., "Kick 01")
   - **Expected**: Sample visible in samples panel/drawer
   - **Check**: Sample title visible with BPM/key metadata

3. Drag sample to pad A1
   - **Action**: Click and hold on sample, drag to pad A1 box, release
   - **Expected**: Sample appears in pad A1
   - **Visual**: Pad A1 now shows sample title/waveform

4. Verify no console errors occurred
   - **Expected**: Console shows no errors during drag
   - **Check**: DevTools Console tab clean

5. Verify drop handler executed
   - **Expected**: Network tab shows sample assignment API call
   - **Check**: POST request to `/kits/{kitId}/pads` successful

**Pass Criteria**:
- ✅ Drag initiates without errors
- ✅ Sample visibly placed in pad A1
- ✅ No console errors during drag-drop
- ✅ API request succeeds (200 response)
- ✅ Pad displays correct sample metadata

---

## Journey 4: Play Sample from Pad (Verify Audio Isolation)

**Preconditions**:
- Sample assigned to pad A1 (from Journey 3)
- Audio context initialized
- System volume enabled
- Browser audio permissions granted

**Steps**:

1. Click play button on pad A1
   - **Expected**: Audio plays through speakers/headphones
   - **Visual**: Play button changes to pause icon
   - **Audio**: Sample audio audible

2. While A1 is still playing, click play button on pad A2
   - **Expected**: A1 stops automatically, A2 begins playing
   - **Check**: Only one audio stream playing at a time
   - **Audio**: Hear A2 audio clearly, A1 fades out

3. Verify console shows AudioContext stopAllExcept call
   - **Expected**: Console logs show player isolation working
   - **Check**: DevTools shows AudioContext managing playback

4. Click pause on A2
   - **Expected**: Audio stops immediately
   - **Visual**: Pause button shows play icon again

**Pass Criteria**:
- ✅ Pad audio plays successfully
- ✅ Previous audio stops when new pad plays
- ✅ Only one audio stream at a time
- ✅ No audio artifacts or overlaps
- ✅ AudioContext isolation working (verified in logs)

---

## Journey 5: Drop Sample on Pad 1 and View Recommendations

**Preconditions**:
- Kits page open with kit
- Bank A visible with pads A1-A16
- Sample library available with melodic samples
- Recommendation API working

**Steps**:

1. Identify a melodic loop sample (e.g., with BPM and key metadata)
   - **Expected**: Sample shows BPM and musical key in metadata
   - **Check**: Info panel displays these values

2. Drag this melodic sample to pad A1
   - **Expected**: Sample placed in A1
   - **Visual**: A1 shows sample name and waveform

3. Verify RecommendationDropdown appears
   - **Expected**: Dropdown menu appears below pad A1 showing recommendations
   - **Visual**: Shows list of 15 samples with BPM/key/genre badges
   - **Check**: Samples are filtered by BPM (±10) and key compatibility

4. Review recommendation samples
   - **Expected**: Each recommendation shows:
     - Sample title
     - BPM (highlighted if within ±10 of seed sample)
     - Musical key (highlighted if compatible)
     - Genre/tags
   - **Check**: Visible samples match criteria

5. Click "Preview" on a recommendation
   - **Expected**: Sample plays through audio system
   - **Check**: Single audio plays, previous audio stops

6. Click "Add to Pad" on a recommendation
   - **Expected**: Sample added to next available pad (A2)
   - **Visual**: Recommendation dropdown shows success message
   - **Check**: API call succeeds

7. Verify recommendations only appear on pad A1
   - **Expected**: Drag sample to pad A2 - no dropdown appears
   - **Check**: Recommendation feature is pad-1-only

**Pass Criteria**:
- ✅ Recommendation dropdown appears after drop on pad 1
- ✅ Shows 15 samples (or all available if < 15)
- ✅ Samples filtered by BPM ±10
- ✅ Samples filtered by musical key compatibility
- ✅ Preview functionality works (audio isolation preserved)
- ✅ Add-to-Pad successfully assigns sample
- ✅ Recommendations ONLY show on pad 1, not other pads
- ✅ No console errors during recommendation flow

---

## Journey 6: Switch Between Banks A-J and Verify All Pads Work

**Preconditions**:
- Kits page with kit containing some samples
- All 10 bank tabs visible (A, B, C, D, E, F, G, H, I, J)

**Steps**:

1. Verify current bank is A
   - **Expected**: Bank A tab highlighted
   - **Visual**: Pads A1-A16 displayed in grid

2. Click bank B tab
   - **Expected**: View switches to B1-B16 pads
   - **Visual**: Tab B highlighted, grid shows B pads

3. Drag a sample to pad B5
   - **Expected**: Sample assigned to B5
   - **Check**: API call succeeds, sample visible in B5

4. Click bank C tab
   - **Expected**: View switches to C1-C16 pads
   - **Visual**: Tab C highlighted, grid shows C pads

5. Click bank J tab (last bank)
   - **Expected**: View switches to J1-J16 pads
   - **Visual**: Tab J highlighted, grid shows J pads with 16 pads visible

6. Drag a sample to pad J16 (last pad)
   - **Expected**: Sample assigned to J16 successfully
   - **Check**: API call succeeds, pad updates

7. Verify all 10 banks are clickable
   - **Expected**: Clicking each tab (A→J) works without errors
   - **Check**: No console errors during bank switching

8. Return to bank A
   - **Expected**: Previous samples (A1 assignment) still visible
   - **Check**: Data persists across bank switches

**Pass Criteria**:
- ✅ All 10 bank tabs present and clickable (A-J)
- ✅ Each bank shows correct 16 pads
- ✅ Drag-drop works on all banks
- ✅ Samples persist when switching banks
- ✅ Bank J accessible with full 16-pad support
- ✅ No type errors for banks E-J (fixed TypeScript issue)
- ✅ Total 160 pads supported (10 × 16)

---

## Journey 7: Remove Sample from Pad

**Preconditions**:
- Kits page with samples assigned to multiple pads
- Example: Pad A1 contains "Kick 01"

**Steps**:

1. Locate pad A1 with assigned sample
   - **Expected**: Pad shows sample title and waveform
   - **Visual**: Sample metadata displayed in pad

2. Right-click or long-press pad A1
   - **Expected**: Context menu appears with "Remove" option
   - **Check**: Menu visible

3. Click "Remove" option
   - **Expected**: Sample removed from pad
   - **Visual**: Pad A1 becomes empty (blank state)
   - **Check**: API call to delete assignment succeeds

4. Verify remove works on multiple pads
   - **Expected**: Can remove samples from any pad A-J
   - **Check**: Multiple removals succeed

5. Verify undo or confirmation works (if implemented)
   - **Expected**: Either confirmation dialog or undo option
   - **Check**: User protected from accidental deletes

**Pass Criteria**:
- ✅ Remove option accessible (context menu or button)
- ✅ Sample successfully removed from pad
- ✅ Pad shows empty/blank state
- ✅ API delete call succeeds
- ✅ Works across all 10 banks
- ✅ Confirmation or undo available if implemented

---

## Journey 8: Create Complete Kit with 8 Drums + 7 Melodic Samples

**Preconditions**:
- Kits page with new or empty kit
- Full sample library available with diverse samples
- Metadata complete (BPM, key, genre, tags)

**Steps**:

1. Start with melodic loop in pad A1
   - **Action**: Drag melodic sample to A1
   - **Expected**: Sample placed in A1
   - **Check**: Sample has BPM (e.g., 89 BPM) and key

2. View recommendations for pad A1
   - **Expected**: Recommendation dropdown shows 15 suggestions
   - **Check**: Filtered by seed sample's BPM and key

3. Select and add 8 drum sounds from recommendations
   - **Action**: Click "Add to Pad" on drum samples (kicks, snares, toms, hats, perc)
   - **Expected**: Each click adds sample to next available pad (A2→A9)
   - **Check**: Pads show drum samples
   - **Verify**: 8 different drum sounds added across pads

4. Select and add 7 melodic samples from recommendations
   - **Action**: Continue clicking "Add to Pad" on melodic recommendations
   - **Expected**: Samples added to pads A10→A16
   - **Check**: Samples show compatible BPM/key/genre

5. Verify pad assignment count
   - **Expected**: 15 pads filled (A1→A15) with seed + 8 drums + 7 melodic
   - **Count**: UI shows "15/16 pads filled" or similar

6. Play samples sequentially
   - **Action**: Click play on each pad A1→A15
   - **Expected**: Each sample plays without overlap
   - **Audio**: Clear, well-matched drum beats and melodic elements
   - **Check**: Audio isolation working for all 15 samples

7. Save/persist kit
   - **Expected**: Kit data saved to database
   - **Check**: Reload page and kit data still present

8. Optionally complete additional banks
   - **Action**: Switch to bank B, repeat for different melodic vibe
   - **Expected**: Can create multiple complete kits across 10 banks

**Pass Criteria**:
- ✅ 15 samples successfully assigned (1 seed + 8 drums + 7 melodic)
- ✅ Drums include variety: kicks, snares, toms, hats, percussion
- ✅ Melodic samples compatible with seed (BPM ±10, key match)
- ✅ All samples play without overlap (audio isolation)
- ✅ Kit data persists across page reloads
- ✅ Can create multiple complete kits across different banks
- ✅ Total capacity: 160 pads can support multiple complete kits

---

## Test Execution Instructions

### Setup
1. Open Chrome DevTools (F12)
2. Open Tabs: Console, Network, Elements
3. Start backend: `./venv/bin/python backend/run.py`
4. Start frontend: `npm run dev` (on port 5173)
5. Open http://localhost:5173/

### For Each Journey
1. Take screenshot at "Visual" checkpoints
2. Check console for errors (red messages)
3. Check Network tab for failed API calls (4xx/5xx status)
4. Document actual behavior vs expected
5. Note any deviations in test results file

### Test Results Tracking
Use `docs/USER_JOURNEY_TEST_RESULTS.md` to document:
- Journey number
- Step number
- Expected behavior
- Actual behavior
- Pass/Fail
- Screenshots
- Console errors
- Network issues
- Priority (High/Medium/Low)

---

## Success Criteria

All 8 journeys PASS when:
- ✅ Each step executes without console errors
- ✅ Visual elements appear as expected
- ✅ API calls succeed (200 responses)
- ✅ Audio isolation functions correctly
- ✅ Bank switching works for A-J (not just A-D)
- ✅ Drag-drop functions across all 160 pads
- ✅ Recommendations appear only on pad 1
- ✅ Data persists across page reloads

---

## Notes

- **Audio Testing**: Requires system volume and audio output device
- **Network Throttling**: Can test with "Slow 4G" in DevTools for realistic conditions
- **Cross-Browser**: Should test on Chrome and Firefox if time permits
- **Mobile**: Not currently tested; desktop-only focus
- **Edge Cases**: Test with empty kit, max kit, rapid clicks, rapid bank switching

