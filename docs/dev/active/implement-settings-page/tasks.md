# Implement Settings Page - Task Checklist

## Phase 1: Type Definitions and API Setup (30 min)

### Task 1.1: Fix TypeScript Type Definition
- [ ] Open `/react-app/src/types/api.ts`
- [ ] Locate UserPreferences interface (around line 75-79)
- [ ] Replace with correct interface:
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
- [ ] Save file
- [ ] Verify TypeScript compilation (check Vite console for errors)

### Task 1.2: Add Model Type Definition
- [ ] Add to `/react-app/src/types/api.ts`:
  ```typescript
  export interface Model {
    id: string;
    name: string;
    description: string;
    cost_per_sample: number;
  }

  export interface ModelsResponse {
    models: Model[];
  }
  ```
- [ ] Save file

### Task 1.3: Add getModels Function to API Client
- [ ] Open `/react-app/src/api/preferences.ts`
- [ ] Add function to preferencesApi:
  ```typescript
  getModels: async () => {
    const { data } = await apiClient.get<ModelsResponse>('/preferences/models');
    return data.models;
  }
  ```
- [ ] Verify no TypeScript errors

### Task 1.4: Verify Preference Hooks Exist
- [ ] Check `/react-app/src/hooks/usePreferences.ts` exists
- [ ] Verify usePreferences() hook exists
- [ ] Verify useUpdatePreferences() hook exists
- [ ] If missing, create hooks or import from correct location

## Phase 2: Settings Page UI Structure (60 min)

### Task 2.1: Create Basic Page Layout
- [ ] Open `/react-app/src/pages/SettingsPage.tsx`
- [ ] Replace placeholder with basic structure:
  ```typescript
  import { usePreferences, useUpdatePreferences } from '@/hooks/usePreferences';
  import { preferencesApi } from '@/api/preferences';
  import { useState, useEffect } from 'react';
  import { toast } from 'sonner';
  import { Button } from '@/components/ui/button';
  import { Card } from '@/components/ui/card';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
  import { Switch } from '@/components/ui/switch';

  export function SettingsPage() {
    const { data: preferences, isLoading } = usePreferences();
    const updateMutation = useUpdatePreferences();
    const [formData, setFormData] = useState<Partial<UserPreferences>>({});
    const [models, setModels] = useState<Model[]>([]);

    // Will populate in Phase 3
    return (
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        <h1 className="text-3xl font-bold mb-2">Preferences</h1>
        <p className="text-muted-foreground mb-6">Manage your sample analysis and export settings</p>

        {/* Sections will be added in next task */}
      </div>
    );
  }
  ```
- [ ] Save file
- [ ] Verify no TypeScript errors

### Task 2.2: Add Page Header and Loading State
- [ ] Add loading check at top of component:
  ```typescript
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        <div className="flex justify-center items-center h-64">
          <p className="text-muted-foreground">Loading preferences...</p>
        </div>
      </div>
    );
  }
  ```
- [ ] Add useEffect to initialize formData when preferences load:
  ```typescript
  useEffect(() => {
    if (preferences) {
      setFormData(preferences);
    }
  }, [preferences]);
  ```
- [ ] Add useEffect to fetch models:
  ```typescript
  useEffect(() => {
    preferencesApi.getModels().then(setModels);
  }, []);
  ```
- [ ] Save file

### Task 2.3: Create AI Analysis Settings Section
- [ ] Add section card after header:
  ```typescript
  <Card className="p-6 mb-6">
    <h2 className="text-xl font-semibold mb-4">AI Analysis Settings</h2>

    {/* Model selector */}
    <div className="mb-4">
      <Label htmlFor="vibe-model">Vibe Analysis Model</Label>
      <Select value={formData.vibe_analysis_model} onValueChange={(value) => setFormData({...formData, vibe_analysis_model: value as any})}>
        <SelectTrigger id="vibe-model">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {models.map(m => (
            <SelectItem key={m.id} value={m.id}>
              {m.name} (~${m.cost_per_sample}/sample)
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <p className="text-sm text-muted-foreground mt-1">Model used to analyze vibe and style of samples</p>
    </div>

    {/* Auto-analyze toggle */}
    <div className="flex items-center justify-between mb-4">
      <div>
        <Label htmlFor="auto-vibe">Automatically analyze samples on upload</Label>
        <p className="text-sm text-muted-foreground">Analyzes vibe/style when new samples are uploaded</p>
      </div>
      <Switch
        id="auto-vibe"
        checked={formData.auto_vibe_analysis || false}
        onCheckedChange={(checked) => setFormData({...formData, auto_vibe_analysis: checked})}
      />
    </div>

    {/* Max cost input */}
    <div>
      <Label htmlFor="max-cost">Maximum cost per analysis (optional)</Label>
      <Input
        id="max-cost"
        type="number"
        step="0.001"
        placeholder="Leave empty for unlimited"
        value={formData.max_cost_per_request || ''}
        onChange={(e) => setFormData({...formData, max_cost_per_request: e.target.value ? parseFloat(e.target.value) : undefined})}
      />
      <p className="text-sm text-muted-foreground mt-1">Prevents unexpectedly high costs. Leave blank for no limit.</p>
    </div>
  </Card>
  ```
- [ ] Save file

### Task 2.4: Create Audio Processing Settings Section
- [ ] Add section card after AI Analysis:
  ```typescript
  <Card className="p-6 mb-6">
    <h2 className="text-xl font-semibold mb-4">Audio Processing Settings</h2>

    {/* Auto features toggle */}
    <div className="flex items-center justify-between mb-4">
      <div>
        <Label htmlFor="auto-features">Auto-extract audio features</Label>
        <p className="text-sm text-muted-foreground">Detects BPM, musical key, and spectral features</p>
      </div>
      <Switch
        id="auto-features"
        checked={formData.auto_audio_features || false}
        onCheckedChange={(checked) => setFormData({...formData, auto_audio_features: checked})}
      />
    </div>

    {/* Batch model selector */}
    <div className="mb-4">
      <Label htmlFor="batch-model">Batch Processing Model</Label>
      <Select value={formData.batch_processing_model} onValueChange={(value) => setFormData({...formData, batch_processing_model: value as any})}>
        <SelectTrigger id="batch-model">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {models.map(m => (
            <SelectItem key={m.id} value={m.id}>
              {m.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <p className="text-sm text-muted-foreground mt-1">Model used when processing multiple samples at once</p>
    </div>

    {/* Batch auto-analyze toggle */}
    <div className="flex items-center justify-between">
      <div>
        <Label htmlFor="batch-auto">Auto-analyze batch uploads</Label>
        <p className="text-sm text-muted-foreground">Processes all samples in batch immediately</p>
      </div>
      <Switch
        id="batch-auto"
        checked={formData.batch_auto_analyze || false}
        onCheckedChange={(checked) => setFormData({...formData, batch_auto_analyze: checked})}
      />
    </div>
  </Card>
  ```
- [ ] Save file

### Task 2.5: Create Export Settings Section
- [ ] Add section card after Audio Processing:
  ```typescript
  <Card className="p-6 mb-6">
    <h2 className="text-xl font-semibold mb-4">Export Preferences</h2>

    {/* Export format */}
    <div className="mb-4">
      <Label htmlFor="export-format">Default Export Format</Label>
      <Select value={formData.default_export_format} onValueChange={(value) => setFormData({...formData, default_export_format: value as any})}>
        <SelectTrigger id="export-format">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="wav">WAV (Universal, smaller file size)</SelectItem>
          <SelectItem value="aiff">AIFF (Higher quality, larger file size)</SelectItem>
        </SelectContent>
      </Select>
    </div>

    {/* Organization */}
    <div className="mb-4">
      <Label htmlFor="org-strategy">Organization Strategy</Label>
      <Select value={formData.default_export_organization} onValueChange={(value) => setFormData({...formData, default_export_organization: value as any})}>
        <SelectTrigger id="org-strategy">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="flat">Flat (All samples in one folder)</SelectItem>
          <SelectItem value="genre">By Genre (Separate folder per genre)</SelectItem>
          <SelectItem value="bpm">By BPM (Grouped by tempo ranges)</SelectItem>
          <SelectItem value="kit">By Kit (Organized into sample kits)</SelectItem>
        </SelectContent>
      </Select>
      <p className="text-sm text-muted-foreground mt-1">How to organize exported samples</p>
    </div>

    {/* Sanitize filenames */}
    <div className="flex items-center justify-between">
      <div>
        <Label htmlFor="sanitize">Auto-sanitize filenames</Label>
        <p className="text-sm text-muted-foreground">Removes special characters for SP-404MK2 compatibility</p>
      </div>
      <Switch
        id="sanitize"
        checked={formData.auto_sanitize_filenames || false}
        onCheckedChange={(checked) => setFormData({...formData, auto_sanitize_filenames: checked})}
      />
    </div>
  </Card>
  ```
- [ ] Save file

## Phase 3: Wire Up Mutations and Handlers (45 min)

### Task 3.1: Create Form Validation Function
- [ ] Add validation function to SettingsPage component:
  ```typescript
  const validateForm = (): boolean => {
    if (formData.max_cost_per_request !== undefined) {
      if (formData.max_cost_per_request <= 0) {
        toast.error('Max cost must be positive number');
        return false;
      }
    }

    // Required fields
    if (!formData.vibe_analysis_model) {
      toast.error('Please select a vibe analysis model');
      return false;
    }

    if (!formData.batch_processing_model) {
      toast.error('Please select a batch processing model');
      return false;
    }

    if (!formData.default_export_format) {
      toast.error('Please select export format');
      return false;
    }

    if (!formData.default_export_organization) {
      toast.error('Please select organization strategy');
      return false;
    }

    return true;
  };
  ```

### Task 3.2: Create Save Handler
- [ ] Add save handler function:
  ```typescript
  const handleSave = async () => {
    if (!validateForm()) return;

    // Only send fields that differ from original
    const updates = Object.entries(formData).reduce((acc, [key, value]) => {
      if (preferences && preferences[key as keyof UserPreferences] !== value) {
        acc[key as keyof UserPreferences] = value;
      }
      return acc;
    }, {} as Partial<UserPreferences>);

    if (Object.keys(updates).length === 0) {
      toast.info('No changes to save');
      return;
    }

    updateMutation.mutate(updates);
  };
  ```

### Task 3.3: Add Save Button
- [ ] Add button section after all form sections:
  ```typescript
  <div className="flex gap-3">
    <Button
      onClick={handleSave}
      disabled={updateMutation.isPending}
      className="w-full"
    >
      {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
    </Button>
  </div>
  ```
- [ ] Save file

### Task 3.4: Add Mutation Side Effects
- [ ] Add useEffect for success:
  ```typescript
  useEffect(() => {
    if (updateMutation.isSuccess) {
      toast.success('Settings saved successfully!');
      // Preferences will auto-update via hook
    }
  }, [updateMutation.isSuccess]);
  ```
- [ ] Add useEffect for errors:
  ```typescript
  useEffect(() => {
    if (updateMutation.isError) {
      const error = updateMutation.error as AxiosError;
      const message = error.response?.data?.detail || 'Failed to save settings';
      toast.error(String(message));
    }
  }, [updateMutation.isError]);
  ```
- [ ] Save file

## Phase 4: Polish and Testing (30 min)

### Task 4.1: Add Disable State to Form
- [ ] Wrap all form inputs with disabled state:
  ```typescript
  disabled={updateMutation.isPending || isLoading}
  ```
- [ ] Apply to all Input, Select, and Switch components
- [ ] Verify inputs are properly disabled while saving

### Task 4.2: Check Switch Component Installation
- [ ] Verify @radix-ui/react-switch exists:
  ```bash
  npm ls @radix-ui/react-switch
  ```
- [ ] If not installed:
  ```bash
  npm install @radix-ui/react-switch
  ```
- [ ] Verify it exists in `/react-app/src/components/ui/switch.tsx`
- [ ] If not, may need to create or import from Radix directly

### Task 4.3: Visual Polish
- [ ] Check spacing between sections (consistent 1.5rem gaps)
- [ ] Verify label text is clear and helpful
- [ ] Ensure help text is visible (text-sm, muted-foreground)
- [ ] Check dark mode colors (use theme variables)
- [ ] Verify responsive layout (test at 375px width)

### Task 4.4: Accessibility Review
- [ ] All inputs have associated labels (htmlFor match)
- [ ] Switch components have proper accessibility
- [ ] Tab order is logical (top to bottom)
- [ ] Error messages are clear and actionable
- [ ] Focus states are visible

### Task 4.5: Manual Testing

#### Test 4.5.1: Load and Display
- [ ] Navigate to http://localhost:5173/settings
- [ ] Page loads without errors
- [ ] Loading spinner appears briefly
- [ ] All form sections visible
- [ ] Current preferences display correctly

#### Test 4.5.2: Form Interaction
- [ ] Click model dropdown - shows both models with pricing
- [ ] Toggle switch - immediately updates state
- [ ] Change number input - value updates
- [ ] Select dropdown option - value changes

#### Test 4.5.3: Validation
- [ ] Try to save with empty model fields - shows error
- [ ] Try to save with negative cost - shows error
- [ ] Enter valid data - save succeeds

#### Test 4.5.4: Save and Persistence
- [ ] Change a setting
- [ ] Click save
- [ ] Wait for success toast
- [ ] Refresh page
- [ ] New value persists
- [ ] Change back to original
- [ ] Save again
- [ ] Verify change

#### Test 4.5.5: Error Handling
- [ ] Check network tab - POST to /api/v1/preferences
- [ ] Try invalid data - backend validates
- [ ] Disconnect network - shows error
- [ ] Reconnect - can retry save

#### Test 4.5.6: Edge Cases
- [ ] Set max cost to 0.001 - saves successfully
- [ ] Set max cost to very large number - saves successfully
- [ ] Leave max cost empty - saves successfully
- [ ] Toggle all switches - each saves independently
- [ ] Switch all dropdowns - values persist

### Task 4.6: Mobile Testing
- [ ] Resize viewport to 375px width
- [ ] All sections stack vertically
- [ ] Form inputs are large enough to tap
- [ ] Buttons are clickable
- [ ] No horizontal scroll needed
- [ ] Text is readable

### Task 4.7: Code Review
- [ ] No TypeScript errors in Vite console
- [ ] No JavaScript console errors
- [ ] No unused imports or variables
- [ ] Proper error handling throughout
- [ ] Loading states for all async operations
- [ ] No memory leaks (cleanup if needed)
- [ ] Comments explain complex logic

## Verification Checklist

### Pre-Implementation
- [x] Types need fixing (10 fields vs 3)
- [x] API endpoints are implemented (GET and PATCH)
- [x] Hooks are implemented (usePreferences, useUpdatePreferences)
- [x] UI components available (Card, Input, Label, Select, Switch)
- [x] Models endpoint implemented (/preferences/models)

### Post-Implementation Expected
- [ ] Settings page loads without errors
- [ ] Current preferences display in form
- [ ] Can change any setting field
- [ ] Changes persist after save
- [ ] Models display with pricing information
- [ ] Success/error notifications work
- [ ] Form validation prevents invalid saves
- [ ] Loading states show during save
- [ ] Page responsive on mobile
- [ ] Accessibility standards met

## Success Metrics

✅ **Critical**: Page loads without errors
✅ **Critical**: Can view and modify all preferences
✅ **Critical**: Changes persist after save
✅ **High**: Success/error notifications work
✅ **High**: Form validation prevents invalid input
✅ **Medium**: Models display with pricing
✅ **Medium**: Responsive design on mobile
✅ **Medium**: Loading states show during save

## Troubleshooting

### If Settings Don't Load
1. Check Network tab - verify GET to /api/v1/preferences
2. Check response includes all fields (id, vibe_analysis_model, etc.)
3. Verify types match backend response
4. Check browser console for fetch errors

### If Save Fails
1. Check Network tab - verify POST to /api/v1/preferences
2. Check request body includes changed fields
3. Check response status and error message
4. Verify all required fields are present before save

### If Models Dropdown Empty
1. Check Network tab - verify GET to /api/v1/preferences/models
2. Check response includes models array
3. Verify models state is set correctly
4. Check browser console for fetch errors

### If Switch Component Missing
1. Verify installation: `npm ls @radix-ui/react-switch`
2. If missing: `npm install @radix-ui/react-switch`
3. Verify component file exists in `/react-app/src/components/ui/switch.tsx`
4. Import from correct path

## Time Estimates

| Phase | Task | Estimate | Actual |
|-------|------|----------|--------|
| 1 | Type definitions and API | 30 min | |
| 2 | UI structure and sections | 60 min | |
| 3 | Mutations and handlers | 45 min | |
| 4 | Polish and testing | 30 min | |
| | **Total** | **~2.5-3 hours** | |

## Sign-Off

- [ ] All phases completed
- [ ] All manual tests passed
- [ ] No console errors or warnings
- [ ] Accessibility verified
- [ ] Code review passed
- [ ] Ready for production use
