# Implement Upload Page - Implementation Plan

**Priority**: HIGH (Core feature)
**Effort**: 2 hours
**Status**: Ready for implementation
**Dependencies**: Fix Kits page first (optional but recommended)

## Problem Statement

Upload page currently shows only a placeholder:
```
"Upload interface will be added here"
```

Users cannot upload new samples to the system.

## Solution Overview

Complete upload page implementation by:
1. **Integrating existing `UploadDropZone` component** (90% complete, just needs import)
2. **Adding optional metadata form** (genre, BPM, key, tags)
3. **Connecting upload hooks and notifications** (success/error feedback)
4. **Adding post-upload actions** (analyze, view sample)

## Why This Works

✅ **Existing Assets**:
- UploadDropZone component is COMPLETE and fully functional
- Backend API endpoints are READY
- React hooks (useUploadSample) are READY
- TypeScript types are DEFINED

❌ **What's Missing**:
- Just the integration in UploadPage.tsx
- Optional metadata form UI
- Toast notifications for feedback

## Technical Details

### Backend API Status
**Endpoint**: `POST /api/v1/public/samples/`
**Location**: `/backend/app/api/v1/endpoints/public.py:118-195`
**Status**: ✅ Fully implemented and tested

**Accepts**:
- `file` (UploadFile) - Audio file (.wav, .mp3, .flac, .aiff, .m4a, .ogg)
- `title` (string) - Required
- `genre` (string, optional) - Hip-Hop, Trap, Jazz, Soul, Electronic, etc.
- `bpm` (number, optional) - 40-200
- `musical_key` (string, optional) - C, C#, D, etc.
- `tags` (JSON string, optional) - ["tag1", "tag2"]

**Returns**: `Sample` object with all metadata

### Existing Component: UploadDropZone
**File**: `/react-app/src/components/upload/UploadDropZone.tsx`
**Status**: ✅ COMPLETE and ready to use

**Features**:
- Drag-and-drop file upload interface
- File validation (50MB max, 20 files)
- Audio format filtering
- Upload progress UI
- File list with remove functionality
- Complete error handling

**Props**:
```typescript
interface UploadDropZoneProps {
  onFilesSelected?: (files: File[]) => void;  // Callback when files added
  maxFileSize?: number;  // Default 50MB
  maxFiles?: number;  // Default 20
  acceptedFormats?: string[];  // Default audio formats
}
```

### React Hooks Ready
**File**: `/react-app/src/hooks/useSamples.ts:33-43`

```typescript
export function useUploadSample() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ file, metadata }: { file: File; metadata?: Partial<Sample> }) =>
      samplesApi.upload(file, metadata),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.lists() });
    },
  });
}
```

## Implementation Phases

### Phase 1: Component Integration (20 min)
Replace placeholder with UploadDropZone component

### Phase 2: Metadata Form (40 min)
Add optional fields for genre, BPM, key, tags

### Phase 3: Upload Logic (30 min)
Wire up upload mutation and file submission

### Phase 4: Notifications & UX (30 min)
- Success/error toast notifications
- Loading states
- Post-upload actions (view sample, analyze, upload more)

## Files to Modify

1. **`/react-app/src/pages/UploadPage.tsx`** - Main file (~100 lines of new code)
   - Import UploadDropZone
   - Import useUploadSample hook
   - Add state management for form
   - Add toast notifications
   - Add metadata form UI

2. **Potentially add**: `/react-app/src/components/upload/MetadataForm.tsx` (optional, can be inline)
   - Reusable metadata form component
   - Genre dropdown
   - BPM input
   - Key selector
   - Tags input

## Features to Implement

### Must Have
- ✅ File upload via drag-and-drop
- ✅ Metadata form (genre, BPM, key, tags)
- ✅ Upload submission
- ✅ Success/error notifications
- ✅ Post-upload feedback (sample details, analyze button)

### Nice to Have
- 🔲 Auto-analyze after upload option
- 🔲 Upload history
- 🔲 Bulk upload progress bar
- 🔲 Sample preview after upload

## Success Criteria

✅ Upload page loads without errors
✅ Can drag-and-drop audio files
✅ Can fill in optional metadata
✅ Submit button sends to API
✅ Success notification appears
✅ New sample appears in Sample Library
✅ Error handling for invalid files/metadata
✅ Clean UX with loading states

## Testing Strategy

### Manual Testing
1. Navigate to upload page
2. Drag/drop audio file
3. Fill in metadata (optional)
4. Click upload
5. Verify success notification
6. Check Sample Library - new sample should appear
7. Try with missing title (should error)
8. Try with invalid file format (should reject)

### Browser DevTools Testing
- Network tab: Verify POST request to `/api/v1/public/samples/`
- Console: No errors
- Performance: Should complete in <2 seconds

## Rollback Plan

If needed:
1. Revert UploadPage.tsx to placeholder
2. Comment out UploadDropZone import
3. No database changes, so safe to rollback

## Dependencies

**New packages needed**: None
**Existing packages used**:
- react-dropzone (already in UploadDropZone)
- sonner (toast notifications - already in project)
- Radix UI components (already in project)

## Timeline

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Component integration | 20 min |
| 2 | Metadata form | 40 min |
| 3 | Upload logic | 30 min |
| 4 | Notifications & UX | 30 min |
| | **Total** | **~2 hours** |

## Next Steps

1. Complete Kits page fix first (quick win)
2. Review existing UploadDropZone component
3. Implement UploadPage integration
4. Test end-to-end
5. Move to Settings page
