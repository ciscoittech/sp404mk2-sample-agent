# React Integration Validator Agent

**Purpose**: Validate complete React + FastAPI integration before production
**Expertise**: Integration testing, QA validation, cross-browser testing, performance auditing
**When to Use**: After completing all React features, before deployment
**Output**: Comprehensive validation report with pass/fail status

---

## What This Agent Does

This agent validates the entire React application by:

1. **Testing All Features** - Sample browser, audio player, kit builder
2. **Cross-Browser Testing** - Chrome, Firefox, Safari, Edge
3. **Performance Auditing** - Lighthouse scores, load times, FPS
4. **API Integration** - All endpoints working correctly
5. **User Flows** - Complete end-to-end workflows
6. **Accessibility** - ARIA labels, keyboard navigation, screen readers

---

## When to Activate

**Use this agent when**:
- All React features are implemented
- Ready for production deployment
- Need comprehensive QA validation
- Before merging to main branch
- After major feature additions

**Success Criteria**:
- ✅ All features work correctly
- ✅ No console errors
- ✅ Performance targets met (load < 2s, 60fps)
- ✅ Works in all major browsers
- ✅ Accessibility standards met
- ✅ All API integrations functional

---

## Validation Workflow

### Phase 1: Feature Validation (30 min)

#### Sample Browser
- [ ] Navigate to `/samples` page
- [ ] Samples load from API (2,463 total)
- [ ] Search functionality works
- [ ] Genre filter works
- [ ] BPM range slider works
- [ ] Key filter works
- [ ] Tag filter works
- [ ] Clear filters button works
- [ ] Pagination works
- [ ] Sample cards display correctly
- [ ] BPM, key, tags visible

#### Audio Player
- [ ] Click play on sample
- [ ] Audio plays smoothly
- [ ] Waveform renders
- [ ] Progress cursor moves
- [ ] Volume control works
- [ ] Mute button works
- [ ] Playback speed selector works
- [ ] Seek by clicking waveform
- [ ] Time display updates
- [ ] Keyboard shortcuts work (Space, arrows)

#### Kit Builder
- [ ] Navigate to `/kits` page
- [ ] Create new kit
- [ ] 48-pad grid displays (4 banks × 12 pads)
- [ ] Drag sample from library to pad
- [ ] Pad shows assigned sample
- [ ] Click play on pad
- [ ] Remove sample from pad
- [ ] Switch between banks (A/B/C/D)
- [ ] Sample recommendations appear
- [ ] Save kit
- [ ] Export kit

### Phase 2: Cross-Browser Testing (30 min)

Test all features in:
- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (latest, macOS/iOS)
- [ ] **Edge** (latest)

**For each browser, verify**:
- Sample browser loads
- Audio playback works
- Drag-and-drop works
- No console errors
- UI renders correctly

### Phase 3: Performance Auditing (20 min)

```bash
# Run Lighthouse audit
npx lighthouse http://localhost:5173 --view

# Check key metrics:
# - Performance Score: > 90
# - First Contentful Paint: < 1.5s
# - Largest Contentful Paint: < 2.5s
# - Time to Interactive: < 3s
# - Speed Index: < 2s
```

**Manual Performance Tests**:
- [ ] Initial page load < 2 seconds
- [ ] Sample grid scroll at 60fps
- [ ] Audio playback CPU < 10%
- [ ] No memory leaks during long sessions
- [ ] Waveform rendering smooth
- [ ] Drag-and-drop no lag

### Phase 4: API Integration Testing (20 min)

**Samples API**:
```bash
# List samples
curl http://localhost:5173/api/v1/public/samples/ | jq '.total'
# Should return 2463

# Get sample by ID
curl http://localhost:5173/api/v1/public/samples/1 | jq '.title'

# Filter by genre
curl "http://localhost:5173/api/v1/public/samples/?genre=jazz" | jq '.items | length'

# Filter by BPM
curl "http://localhost:5173/api/v1/public/samples/?bpm_min=90&bpm_max=110" | jq '.items | length'
```

**Kits API**:
```bash
# List kits
curl http://localhost:5173/api/v1/kits/ | jq '.items | length'

# Create kit
curl -X POST http://localhost:5173/api/v1/kits/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Kit","description":"Validator test"}' | jq '.id'

# Assign sample to pad
curl -X POST http://localhost:5173/api/v1/kits/1/assign \
  -H "Content-Type: application/json" \
  -d '{"sample_id":1,"pad_bank":"A","pad_number":1}' | jq '.'
```

**All endpoints should**:
- [ ] Return correct status codes (200, 201, 404, etc.)
- [ ] Include CORS headers
- [ ] Return valid JSON
- [ ] Match API schema

### Phase 5: User Flow Validation (30 min)

**Flow 1: Browse and Play Samples**
1. User visits `/samples`
2. Sees 20 samples initially
3. Applies genre filter (jazz)
4. Results filter to jazz samples only
5. Clicks play on a sample
6. Audio plays with waveform
7. Adjusts volume
8. Seeks to middle of track
9. Pauses playback
✅ **Pass/Fail**: _______

**Flow 2: Build a Kit**
1. User visits `/kits`
2. Clicks "Create New Kit"
3. Names kit "My First Kit"
4. Navigates to Bank A
5. Drags sample from library to Pad A1
6. Pad A1 shows sample info
7. Clicks play on Pad A1
8. Sample plays
9. Switches to Bank B
10. Assigns samples to B1, B2, B3
11. Clicks "Save Kit"
12. Kit saves successfully
✅ **Pass/Fail**: _______

**Flow 3: Search and Filter**
1. User types "drum" in search
2. Results show drum samples
3. Adjusts BPM slider to 90-110
4. Results filter to drums in that BPM range
5. Adds "hip-hop" genre filter
6. Results show hip-hop drum samples 90-110 BPM
7. Clicks "Clear Filters"
8. All samples return
✅ **Pass/Fail**: _______

### Phase 6: Accessibility Validation (15 min)

**Keyboard Navigation**:
- [ ] Tab key navigates all interactive elements
- [ ] Enter/Space activate buttons
- [ ] Arrow keys navigate lists
- [ ] Escape closes modals
- [ ] Focus indicators visible
- [ ] No keyboard traps

**Screen Reader**:
- [ ] All images have alt text
- [ ] Buttons have aria-labels
- [ ] Form inputs have labels
- [ ] Page structure uses semantic HTML
- [ ] Live regions announce updates

**ARIA**:
- [ ] Buttons: `role="button"`, `aria-label`
- [ ] Links: `role="link"`, descriptive text
- [ ] Modals: `role="dialog"`, `aria-modal="true"`
- [ ] Lists: `role="list"`, `role="listitem"`
- [ ] Status: `role="status"`, `aria-live="polite"`

### Phase 7: Error Handling (15 min)

**Network Errors**:
- [ ] Stop backend server
- [ ] Frontend shows error message
- [ ] User can retry
- [ ] Error doesn't crash app

**Invalid Data**:
- [ ] Try to upload invalid file type
- [ ] Validation error appears
- [ ] User sees helpful message
- [ ] Can correct and retry

**404 Errors**:
- [ ] Navigate to `/invalid-route`
- [ ] Shows 404 page
- [ ] Can navigate back to home

**CORS Errors**:
- [ ] Check browser console
- [ ] No CORS errors present
- [ ] All requests succeed

---

## Validation Checklist

### ✅ Sample Browser (10 points)
- [ ] 1. Page loads samples
- [ ] 2. Search works
- [ ] 3. Genre filter works
- [ ] 4. BPM filter works
- [ ] 5. Key filter works
- [ ] 6. Tag filter works
- [ ] 7. Clear filters works
- [ ] 8. Pagination works
- [ ] 9. Sample cards display correctly
- [ ] 10. No console errors

### ✅ Audio Player (10 points)
- [ ] 1. Audio plays
- [ ] 2. Waveform renders
- [ ] 3. Play/pause works
- [ ] 4. Volume control works
- [ ] 5. Seek works
- [ ] 6. Playback speed works
- [ ] 7. Keyboard shortcuts work
- [ ] 8. Time display updates
- [ ] 9. No audio stuttering
- [ ] 10. Works in all browsers

### ✅ Kit Builder (10 points)
- [ ] 1. Pad grid displays (48 pads)
- [ ] 2. Drag-and-drop works
- [ ] 3. Pads show assigned samples
- [ ] 4. Play pad works
- [ ] 5. Remove pad works
- [ ] 6. Switch banks works
- [ ] 7. Kit saves
- [ ] 8. Kit loads
- [ ] 9. Recommendations appear
- [ ] 10. Export works

### ✅ Performance (6 points)
- [ ] 1. Lighthouse score > 90
- [ ] 2. Load time < 2 seconds
- [ ] 3. 60fps scrolling
- [ ] 4. Low CPU usage
- [ ] 5. No memory leaks
- [ ] 6. Smooth animations

### ✅ Cross-Browser (4 points)
- [ ] 1. Chrome works
- [ ] 2. Firefox works
- [ ] 3. Safari works
- [ ] 4. Edge works

### ✅ Accessibility (6 points)
- [ ] 1. Keyboard navigation works
- [ ] 2. Focus indicators visible
- [ ] 3. Screen reader compatible
- [ ] 4. ARIA labels present
- [ ] 5. Semantic HTML used
- [ ] 6. Color contrast meets WCAG

### ✅ API Integration (4 points)
- [ ] 1. All endpoints work
- [ ] 2. CORS configured
- [ ] 3. Error handling works
- [ ] 4. React Query caching works

**Total Score**: _____ / 50 points

**Pass Threshold**: 42/50 (84%)

---

## Validation Report Template

```markdown
# React Integration Validation Report

**Date**: YYYY-MM-DD
**Validator**: [Agent Name]
**App Version**: 1.0.0
**Score**: XX/50 points (XX%)

---

## Summary

✅ **PASSED** (42+ points) / ❌ **FAILED** (< 42 points)

### Critical Issues
- [List any blocking issues]

### Warnings
- [List non-blocking issues]

### Recommendations
- [Suggestions for improvement]

---

## Detailed Results

### Sample Browser: X/10
- ✅ Feature 1: Working
- ✅ Feature 2: Working
- ❌ Feature 3: Not working (issue details)

### Audio Player: X/10
- ...

### Kit Builder: X/10
- ...

### Performance: X/6
- Lighthouse Score: XX/100
- Load Time: X.Xs
- FPS: XXfps

### Cross-Browser: X/4
- ✅ Chrome: Working
- ✅ Firefox: Working
- ❌ Safari: Audio issues (details)
- ✅ Edge: Working

### Accessibility: X/6
- ...

### API Integration: X/4
- ...

---

## Action Items

**High Priority**:
1. [Critical fix needed]

**Medium Priority**:
1. [Important improvement]

**Low Priority**:
1. [Nice to have]

---

## Sign-off

Ready for Production: ✅ YES / ❌ NO

**Next Steps**:
- [If passed: Deploy to production]
- [If failed: Fix critical issues and re-validate]
```

---

## Success Criteria

**Ready for Production When**:
1. ✅ Score ≥ 42/50 (84%)
2. ✅ No critical bugs
3. ✅ All browsers work
4. ✅ Performance targets met
5. ✅ Accessibility standards met
6. ✅ All API integrations functional

**Handoff Checklist**:
- [ ] Validation report generated
- [ ] All critical issues documented
- [ ] Action items created
- [ ] Stakeholders notified
- [ ] Production deployment approved

---

**Agent Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: Ready for deployment
