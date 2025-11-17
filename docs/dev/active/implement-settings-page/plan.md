# Implement Settings Page - Implementation Plan

**Priority**: MEDIUM (UX enhancement)
**Effort**: 3-4 hours
**Status**: Ready for implementation
**Dependencies**: Complete Upload page first (recommended)

## Problem Statement

Settings page currently shows only a placeholder:
```
"Settings interface will be added here"
```

Users cannot configure:
- AI model selection for analysis
- Auto-analysis settings
- Export preferences
- Cost limits

## Solution Overview

Build a comprehensive Settings page by:
1. **Fix TypeScript types** - Update UserPreferences interface to match backend
2. **Build settings form UI** - Create sections for different settings categories
3. **Implement model selector** - Show available models with pricing
4. **Add form controls** - Toggle switches, dropdowns, number inputs
5. **Wire up mutations** - Connect update hook for saving changes

## Why This Is Needed

**Backend is ready**:
✅ Preferences API endpoints implemented
✅ Database schema supports all settings
✅ Validation and error handling in place

**Frontend is ready**:
✅ usePreferences hook implemented
✅ useUpdatePreferences hook implemented
✅ All UI components available

**What's missing**:
❌ Type definition mismatch (TypeScript interface outdated)
❌ Settings form UI not built
❌ Model selector not implemented
❌ Form submission logic not wired up

## Technical Details

### Settings Categories

#### 1. AI Analysis Settings
**Purpose**: Configure AI model for vibe analysis
- **Vibe analysis model** - Select from available models
  - Qwen3-7B (fast, ~$0.00001/sample)
  - Qwen3-235B (accurate, ~$0.00005/sample)
- **Auto vibe analysis** - Toggle automatic analysis
- **Max cost per request** - Prevent runaway costs

#### 2. Audio Features Settings
**Purpose**: Control audio feature extraction
- **Auto audio features** - Toggle automatic extraction
- **Batch processing model** - Select model for batch jobs
- **Auto-analyze batches** - Toggle batch auto-analysis

#### 3. Export Settings
**Purpose**: Configure sample export preferences
- **Default export format** - WAV or AIFF
- **Default organization** - flat, genre, BPM, kit
- **Auto-sanitize filenames** - Remove special characters

## API Specification

### Backend Endpoints Status

**GET /api/v1/preferences** (Fully implemented)
```
Returns: {
  id: number,
  vibe_analysis_model: string,
  auto_vibe_analysis: boolean,
  auto_audio_features: boolean,
  batch_processing_model: string,
  batch_auto_analyze: boolean,
  max_cost_per_request: number | null,
  default_export_format: string,
  default_export_organization: string,
  auto_sanitize_filenames: boolean,
  created_at: datetime,
  updated_at: datetime
}
```

**PATCH /api/v1/preferences** (Fully implemented)
```
Accepts: Partial update of any preference field
Supports JSON and form-encoded data
```

**GET /api/v1/preferences/models** (Need to wire up)
```
Returns: {
  "models": [
    {
      "id": "qwen3-7b",
      "name": "Qwen 3 7B",
      "description": "Fast and cheap",
      "cost_per_sample": 0.00001
    },
    {
      "id": "qwen3-235b",
      "name": "Qwen 3 235B",
      "description": "Most accurate",
      "cost_per_sample": 0.00005
    }
  ]
}
```

## Type Definition Mismatch

### Current (Incorrect)
**File**: `/react-app/src/types/api.ts:75-79`
```typescript
export interface UserPreferences {
  ai_model: 'qwen3-7b' | 'qwen3-235b';
  auto_analysis: boolean;
  theme: 'dark' | 'light';
}
```

### Should Be (Correct)
```typescript
export interface UserPreferences {
  id: number;
  vibe_analysis_model: string;
  auto_vibe_analysis: boolean;
  auto_audio_features: boolean;
  batch_processing_model: string;
  batch_auto_analyze: boolean;
  max_cost_per_request?: number;
  default_export_format: 'wav' | 'aiff';
  default_export_organization: 'flat' | 'genre' | 'bpm' | 'kit';
  auto_sanitize_filenames: boolean;
  created_at: string;
  updated_at: string;
}
```

## UI Layout

### Recommended Design: Tabbed/Sectioned Layout
```
Settings Page
├── Header "Preferences"
│   └── "Manage your sample analysis and export settings"
├── Section 1: AI Analysis
│   ├── Model selector (dropdown with pricing)
│   ├── Auto-analyze toggle
│   └── Max cost input
├── Section 2: Audio Processing
│   ├── Batch model selector
│   ├── Auto batch toggle
│   └── Cost display
├── Section 3: Export Preferences
│   ├── Format radio buttons (WAV/AIFF)
│   ├── Organization dropdown
│   └── Filename sanitization toggle
└── Save button (sticky footer or per-section)
```

## Files to Modify/Create

1. **`/react-app/src/types/api.ts`** - Update UserPreferences
   - Fix field names to match backend
   - Add all missing fields

2. **`/react-app/src/api/preferences.ts`** - Add model fetching
   - Add `getAvailableModels()` function
   - Wire up to preferences endpoint

3. **`/react-app/src/pages/SettingsPage.tsx`** - Build settings UI
   - Import hooks and components
   - Add form state management
   - Build UI sections
   - Wire up save functionality

4. **Optional**: `/react-app/src/components/settings/ModelSelector.tsx`
   - Reusable component for model selection
   - Show pricing and description
   - Could be used elsewhere

## Features to Implement

### Must Have
- ✅ Display current preferences
- ✅ Update any preference field
- ✅ Show available AI models
- ✅ Save changes with confirmation
- ✅ Error handling and validation

### Nice to Have
- 🔲 Explain each setting with help text
- 🔲 Show cost estimates
- 🔲 Preset configurations (fast/accurate/balanced)
- 🔲 Settings history/changelog

## Success Criteria

✅ Settings page loads without errors
✅ Can view all preference settings
✅ Can change any setting field
✅ Changes persist after save
✅ Can see available AI models with pricing
✅ Error handling for invalid inputs
✅ Loading states while saving
✅ Success notification on save
✅ Settings match across sessions

## Testing Strategy

### Manual Testing
1. Navigate to Settings page
2. View current preferences
3. Change each setting type:
   - Toggle switches
   - Dropdown selection
   - Number input
4. Click save
5. Verify toast notification
6. Refresh page - settings should persist
7. Change settings back
8. Test invalid inputs (if applicable)
9. Test network error handling

### Expected Behavior
- Initial load shows current preferences (or defaults)
- Changes update form state immediately
- Save button submits changes to API
- Success toast shows after save
- Page reflects new values
- Closing and reopening shows saved values

## Dependencies

**New Packages**: None (all UI components exist)
**Switch Component**: May need to add if not present
- Check if `@radix-ui/react-switch` exists
- If not: `npm install @radix-ui/react-switch`

**Existing to Use**:
- ✅ React Query mutations (for updates)
- ✅ Radix UI components (for form)
- ✅ sonner (for toast notifications)
- ✅ TypeScript (for types)

## Timeline

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Fix TypeScript types | 30 min |
| 2 | Build form sections | 60 min |
| 3 | Implement model selector | 45 min |
| 4 | Wire up mutations | 45 min |
| 5 | Testing & polish | 30 min |
| | **Total** | **~3.5 hours** |

## Rollback Plan

If needed:
1. Revert changes to SettingsPage.tsx and types.ts
2. Restore placeholder HTML
3. No data loss (only UI changes)

## Next Steps

1. Complete Upload page first
2. Fix TypeScript types
3. Build settings form UI
4. Wire up save functionality
5. Test end-to-end

## Stretch Goals (If Time Permits)

- Add help tooltips for each setting
- Show estimated analysis cost for current model
- Add quick presets (Fast/Accurate/Balanced)
- Add settings export/import
