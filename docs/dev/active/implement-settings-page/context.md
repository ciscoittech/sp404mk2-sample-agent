# Implement Settings Page - Technical Context

## Current Implementation Status

### SettingsPage Component
**File**: `/react-app/src/pages/SettingsPage.tsx`
**Status**: Placeholder only (lines 14-18)

```typescript
export function SettingsPage() {
  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      <div className="rounded-lg border border-border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          Settings interface will be added here
        </p>
      </div>
    </div>
  );
}
```

### UserPreferences Type Mismatch
**File**: `/react-app/src/types/api.ts:75-79`
**Status**: ❌ INCORRECT - Does not match backend schema

**Current (Wrong)**:
```typescript
export interface UserPreferences {
  ai_model: 'qwen3-7b' | 'qwen3-235b';
  auto_analysis: boolean;
  theme: 'dark' | 'light';
}
```

**Backend Schema (Actual)**:
```json
{
  "id": number,
  "vibe_analysis_model": "qwen3-7b" | "qwen3-235b",
  "auto_vibe_analysis": boolean,
  "auto_audio_features": boolean,
  "batch_processing_model": "qwen3-7b" | "qwen3-235b",
  "batch_auto_analyze": boolean,
  "max_cost_per_request": number | null,
  "default_export_format": "wav" | "aiff",
  "default_export_organization": "flat" | "genre" | "bpm" | "kit",
  "auto_sanitize_filenames": boolean,
  "created_at": datetime,
  "updated_at": datetime
}
```

## Backend API Endpoints Status

### GET /api/v1/preferences
**Location**: `/backend/app/api/v1/endpoints/preferences.py:line`
**Status**: ✅ Fully implemented

**Response**: Complete UserPreferences object with all 10 settings fields

**Error Handling**:
- 404 if preferences not found (but always created for new users)
- Returns default preferences if none exist

### PATCH /api/v1/preferences
**Status**: ✅ Fully implemented

**Request**:
- Content-Type: application/json
- Body: Partial update of any fields

```json
{
  "vibe_analysis_model": "qwen3-235b",
  "auto_vibe_analysis": true,
  "max_cost_per_request": 0.001
}
```

**Response**: Updated UserPreferences object

**Validation**:
- Models must be valid: qwen3-7b or qwen3-235b
- BPM must be 40-200 if provided
- Cost must be positive number if provided
- Export format: wav or aiff only
- Organization: flat, genre, bpm, or kit only

### GET /api/v1/preferences/models
**Status**: ✅ Fully implemented

**Response**:
```json
{
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

## React Hooks Ready

### usePreferences Hook
**File**: `/react-app/src/hooks/usePreferences.ts`
**Status**: ✅ Implemented

```typescript
export function usePreferences() {
  return useQuery({
    queryKey: queryKeys.preferences.all(),
    queryFn: () => preferencesApi.get(),
  });
}
```

**Features**:
- Automatic refetch on focus
- Cache management
- Error handling
- Loading state

### useUpdatePreferences Hook
**File**: `/react-app/src/hooks/usePreferences.ts`
**Status**: ✅ Implemented

```typescript
export function useUpdatePreferences() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updates: Partial<UserPreferences>) =>
      preferencesApi.update(updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.preferences.all() });
    },
  });
}
```

**Features**:
- Automatic cache invalidation
- Error handling
- Loading/pending state
- Automatic refetch after save

## Available UI Components

### Existing Components Ready to Use
**Location**: `/react-app/src/components/ui/`

- **Card** - Container for sections
- **Input** - Text inputs (title, number fields)
- **Label** - Form labels with proper association
- **Select** - Dropdown selection (for model, format, organization)
- **Switch** - Toggle switches for boolean settings (may need to check if @radix-ui/react-switch exists)
- **Button** - Primary/secondary action buttons
- **Alert** - Error/info messages
- **Spinner/Loader** - Loading indicators
- **Badge** - Tag/label display (for pricing info)

### Toast Notifications
**Library**: sonner (already installed)
**Import**: `import { toast } from 'sonner'`

**Usage**:
```typescript
toast.success('Settings saved successfully!');
toast.error('Failed to save settings');
toast.loading('Saving...');
```

## Settings Categories and Fields

### Category 1: AI Analysis Settings
**Purpose**: Configure AI model for vibe analysis

**Fields**:
- `vibe_analysis_model` - Select from available models
  - Type: string ('qwen3-7b' | 'qwen3-235b')
  - UI: Dropdown with model details and pricing
  - Display: "Qwen 3 7B (Fast, $0.00001/sample)" vs "Qwen 3 235B (Accurate, $0.00005/sample)"

- `auto_vibe_analysis` - Toggle automatic analysis
  - Type: boolean
  - UI: Switch toggle
  - Label: "Automatically analyze uploaded samples"
  - Help: "Analyzes vibe/style of samples when uploaded"

- `max_cost_per_request` - Prevent runaway costs
  - Type: number | null
  - UI: Number input with suffix "$"
  - Label: "Maximum cost per analysis (optional)"
  - Help: "Leave empty for no limit"
  - Validation: Positive number if provided

### Category 2: Audio Features Settings
**Purpose**: Control audio feature extraction

**Fields**:
- `auto_audio_features` - Toggle automatic extraction
  - Type: boolean
  - UI: Switch toggle
  - Label: "Auto-extract audio features (BPM, key)"
  - Help: "Detects BPM, musical key, and spectral features"

- `batch_processing_model` - Select model for batch jobs
  - Type: string ('qwen3-7b' | 'qwen3-235b')
  - UI: Dropdown (same as vibe analysis model)
  - Label: "Model for batch processing"
  - Help: "Used when processing multiple samples at once"

- `batch_auto_analyze` - Toggle batch auto-analysis
  - Type: boolean
  - UI: Switch toggle
  - Label: "Auto-analyze batch uploads"
  - Help: "Process all samples in batch immediately"

### Category 3: Export Settings
**Purpose**: Configure sample export preferences

**Fields**:
- `default_export_format` - WAV or AIFF
  - Type: string ('wav' | 'aiff')
  - UI: Radio buttons or dropdown
  - Options:
    - wav - "WAV (Universal, smaller file size)"
    - aiff - "AIFF (Higher quality, larger file size)"

- `default_export_organization` - Organization strategy
  - Type: string ('flat' | 'genre' | 'bpm' | 'kit')
  - UI: Dropdown
  - Options:
    - flat - "Flat (All samples in one folder)"
    - genre - "By Genre (Separate folder per genre)"
    - bpm - "By BPM (Grouped by tempo ranges)"
    - kit - "By Kit (Organized into sample kits)"

- `auto_sanitize_filenames` - Remove special characters
  - Type: boolean
  - UI: Switch toggle
  - Label: "Auto-sanitize filenames"
  - Help: "Removes special characters for SP-404MK2 compatibility"

## API Client Functions

### preferences.ts
**File**: `/react-app/src/api/preferences.ts`
**Status**: May need to add getModels() function

**Existing functions**:
```typescript
export const preferencesApi = {
  get: async () => { /* fetch preferences */ },
  update: async (updates: Partial<UserPreferences>) => { /* patch preferences */ }
};
```

**May need to add**:
```typescript
getModels: async () => {
  const { data } = await apiClient.get('/preferences/models');
  return data.models;
}
```

## Form State Management

### State Variables Needed
```typescript
// Current preferences (from hook)
const { data: preferences, isLoading } = usePreferences();

// Form state (local copy for editing)
const [formData, setFormData] = useState<Partial<UserPreferences>>({});

// Mutation for saving
const updateMutation = useUpdatePreferences();

// Available models
const [models, setModels] = useState<Model[]>([]);
```

### State Synchronization
1. On component mount: Load preferences from hook
2. Initialize formData with preferences values
3. Track which fields have been modified
4. On save: Only send modified fields to API
5. On success: Reset formData to current preferences

## UI Layout Recommendations

### Option A: Sectioned (Recommended)
```
Settings Page
├── Header "Preferences"
│   └── Description text
├── Section 1: AI Analysis Settings
│   ├── Model selector (with pricing)
│   ├── Auto-analyze toggle
│   └── Max cost input
├── Section 2: Audio Processing
│   ├── Auto features toggle
│   ├── Batch model selector
│   └── Batch auto-analyze toggle
├── Section 3: Export Preferences
│   ├── Format radio buttons
│   ├── Organization dropdown
│   └── Sanitize filenames toggle
└── Save button (bottom)
```

### Option B: Tabbed
```
Settings Page
├── Tabs: AI Analysis | Audio Processing | Export
└── Each tab contains relevant settings
```

**Recommended**: Option A (sectioned) for better UX and less clicking

## Styling Guidelines

### Colors
- **Primary**: Use theme primary color for save button
- **Secondary**: Use muted color for help text
- **Error**: Use red for validation errors
- **Success**: Use green for success notifications

### Spacing
- Sections separated by horizontal divider or margin
- Fields within section: 1rem gap
- Form label to input: 0.5rem gap
- Help text below input: 0.25rem gap

### Dark Mode
- All components support dark mode via Tailwind
- Use `bg-card` for backgrounds
- Use `text-foreground` for text
- Use `border-border` for borders

## Form Validation

### Client-side Validation
```typescript
const validateForm = (): boolean => {
  if (formData.max_cost_per_request !== undefined &&
      formData.max_cost_per_request <= 0) {
    toast.error('Max cost must be positive');
    return false;
  }

  // All other validations...
  return true;
};
```

### Server Validation
- Backend validates all field values
- Returns specific error messages via Pydantic
- Frontend displays errors via toast notifications

## Loading and Error States

### Loading States
- Show spinner while fetching preferences
- Disable all form inputs while preferences loading
- Show spinner on save button while mutation pending
- Disable form inputs while saving

### Error States
- Display error toast with message from backend
- Show error alert in form if needed
- Keep form data intact to allow retry
- Add retry button if appropriate

## Post-Save Actions

### On Success
- Show success toast: "Settings saved successfully!"
- Disable save button (no unsaved changes)
- Highlight changed fields briefly (optional)
- Auto-dismiss success notification after 3 seconds

### On Error
- Show error toast with backend message
- Keep save button enabled for retry
- Don't clear form data
- Log error for debugging

## Related Components

### Existing Settings UI (if any)
Check if any settings UI already exists in:
- `/react-app/src/components/settings/`
- Dashboard user menu
- Profile page

### Settings in Other Pages
Check if other pages reference preferences:
- Sample upload page (auto-analysis setting)
- Sample analysis page (model selection)
- Export page (export format/organization)

## Performance Considerations

- Preferences loaded once on app init (via layout)
- Queries cached by React Query
- No heavy processing needed
- Network calls: 2 (fetch preferences, fetch models) + 1 per save

## Browser Compatibility

- All Radix UI components work in modern browsers
- Switch component may need polyfill for older Safari
- Form submission via fetch API (works everywhere)

## Security Notes

- No sensitive data in preferences (settings only)
- All input validated on backend
- No direct database access from frontend
- CORS configured for dev environment

## Dependencies Summary

**No new packages needed!**

All required dependencies already in project:
- ✅ react-query (for hooks)
- ✅ Radix UI components (for form UI)
- ✅ sonner (for toast notifications)
- ✅ TypeScript (for types)

**Potential Addition** (if not present):
- @radix-ui/react-switch - for toggle switches
  - Check if exists: `npm ls @radix-ui/react-switch`
  - If missing: `npm install @radix-ui/react-switch`

## Data Types

### UserPreferences (Correct - To Be Implemented)
```typescript
export interface UserPreferences {
  id: number;
  vibe_analysis_model: 'qwen3-7b' | 'qwen3-235b';
  auto_vibe_analysis: boolean;
  auto_audio_features: boolean;
  batch_processing_model: 'qwen3-7b' | 'qwen3-235b';
  batch_auto_analyze: boolean;
  max_cost_per_request?: number;
  default_export_format: 'wav' | 'aiff';
  default_export_organization: 'flat' | 'genre' | 'bpm' | 'kit';
  auto_sanitize_filenames: boolean;
  created_at: string;
  updated_at: string;
}
```

### Model Type
```typescript
export interface Model {
  id: string;
  name: string;
  description: string;
  cost_per_sample: number;
}
```

## Testing Resources

### Test Data
- Fresh user account has default preferences
- Can test with modified preferences persisting across page reloads
- Can test error cases by using invalid values (backend validates)

### Manual Testing Checklist
1. Load settings page - should see current values
2. Change each field type - form updates
3. Click save - mutation fires, success toast appears
4. Refresh page - new values persist
5. Try invalid input (negative cost) - should error on submit
6. Check models dropdown loads - shows both available models
7. Test on mobile - form should be responsive

## Integration Points

### Used By
- Sample upload page (references auto_analysis_model)
- Batch processing (uses batch_processing_model)
- Export system (uses default_export_format/organization)

### Updates Needed
- May need to add settings link to main navigation/user menu
- May need settings icon in dashboard header

## Success Metrics

✅ Settings page loads without errors
✅ Can view all preference settings
✅ Can change any setting field
✅ Changes persist after save and page refresh
✅ Can see available AI models with pricing
✅ Error handling for invalid inputs
✅ Loading states while saving
✅ Success notification on save
✅ Settings match across sessions
✅ Responsive design on mobile
