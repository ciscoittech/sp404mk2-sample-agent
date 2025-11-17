# Implement Upload Page - Task Checklist

## Phase 1: Component Integration (20 min)

### Task 1.1: Import Required Components
- [ ] Open `/react-app/src/pages/UploadPage.tsx`
- [ ] Add imports at top:
  ```typescript
  import { UploadDropZone } from '@/components/upload/UploadDropZone';
  import { useUploadSample } from '@/hooks/useSamples';
  import { toast } from 'sonner';
  import { useState } from 'react';
  ```

### Task 1.2: Replace Placeholder with UploadDropZone
- [ ] Remove the placeholder `<div>` with message text
- [ ] Add UploadDropZone component:
  ```typescript
  <UploadDropZone onFilesSelected={handleFilesSelected} />
  ```
- [ ] Add handler function:
  ```typescript
  const handleFilesSelected = (files: File[]) => {
    // Will populate in Phase 3
  };
  ```

### Task 1.3: Test Initial Render
- [ ] Save file
- [ ] Navigate to http://localhost:5173/upload
- [ ] Verify drag-and-drop zone appears
- [ ] Try dragging a file (should not upload yet)

## Phase 2: Metadata Form (40 min)

### Task 2.1: Add Form State
- [ ] Add state variables to UploadPage:
  ```typescript
  const [formData, setFormData] = useState({
    title: '',
    genre: '',
    bpm: '',
    musical_key: '',
    tags: ''
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  ```

### Task 2.2: Create Metadata Form UI
- [ ] Add form HTML below UploadDropZone:
  - Title input (required, max 255 chars)
  - Genre dropdown (optional)
  - BPM input (optional, number)
  - Musical Key dropdown (optional)
  - Tags textarea (optional, comma-separated)
- [ ] Add form styling using Card, Input, Label, Select components

### Task 2.3: Add Form Handlers
- [ ] Create `handleInputChange` for form fields
- [ ] Create `handleFilesSelected` to store files
- [ ] Add form validation function:
  ```typescript
  const validateForm = (): boolean => {
    if (!formData.title.trim()) {
      toast.error('Title is required');
      return false;
    }
    if (formData.title.length > 255) {
      toast.error('Title must be 255 characters or less');
      return false;
    }
    // Add BPM validation (40-200 if provided)
    return true;
  };
  ```

### Task 2.4: Test Metadata Form
- [ ] Verify form appears below upload zone
- [ ] Test typing in each field
- [ ] Test dropdown selections work
- [ ] Verify form state updates correctly

## Phase 3: Upload Logic (30 min)

### Task 3.1: Set Up Upload Mutation
- [ ] Initialize upload hook:
  ```typescript
  const uploadMutation = useUploadSample();
  ```

### Task 3.2: Create Upload Handler
- [ ] Create `handleUpload` function:
  ```typescript
  const handleUpload = async () => {
    if (!validateForm()) return;
    if (selectedFiles.length === 0) {
      toast.error('Please select a file');
      return;
    }

    const file = selectedFiles[0];
    const metadata = {
      title: formData.title,
      genre: formData.genre || undefined,
      bpm: formData.bpm ? parseFloat(formData.bpm) : undefined,
      musical_key: formData.musical_key || undefined,
      tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : undefined
    };

    uploadMutation.mutate({ file, metadata });
  };
  ```

### Task 3.3: Add Upload Button
- [ ] Add button below form:
  ```typescript
  <Button
    onClick={handleUpload}
    disabled={uploadMutation.isPending}
    className="w-full"
  >
    {uploadMutation.isPending ? 'Uploading...' : 'Upload Sample'}
  </Button>
  ```

### Task 3.4: Test Upload Flow
- [ ] Select a file via drag-and-drop
- [ ] Fill in title (required)
- [ ] Click upload button
- [ ] Verify API call is made (check Network tab)
- [ ] Verify file is sent correctly (multipart/form-data)

## Phase 4: Notifications & UX (30 min)

### Task 4.1: Add Success/Error Notifications
- [ ] Add mutation side effects:
  ```typescript
  useEffect(() => {
    if (uploadMutation.isSuccess) {
      toast.success('Sample uploaded successfully!');
      // Reset form
      setFormData({ title: '', genre: '', bpm: '', musical_key: '', tags: '' });
      setSelectedFiles([]);
    }
  }, [uploadMutation.isSuccess]);

  useEffect(() => {
    if (uploadMutation.isError) {
      const error = uploadMutation.error as AxiosError;
      const message = error.response?.data?.detail || 'Upload failed';
      toast.error(message);
    }
  }, [uploadMutation.isError]);
  ```

### Task 4.2: Add Loading States
- [ ] Disable form inputs while uploading:
  ```typescript
  disabled={uploadMutation.isPending}
  ```
- [ ] Show loading indicator on button
- [ ] Add visual feedback for upload progress

### Task 4.3: Add Post-Upload Actions (Optional)
- [ ] Add "View Sample" button after success
- [ ] Add "Upload Another" button to reset form
- [ ] Link to newly uploaded sample in Sample Library

### Task 4.4: Add Error Display
- [ ] Show error message near form
- [ ] Highlight invalid fields (if validation fails)
- [ ] Clear errors when user fixes them

## Phase 5: Polish & Testing (20 min)

### Task 5.1: Visual Polish
- [ ] Ensure form styling matches design system
- [ ] Check spacing and alignment
- [ ] Verify responsive layout on mobile
- [ ] Test dark mode colors

### Task 5.2: Accessibility
- [ ] All form inputs have proper labels
- [ ] Error messages are announced to screen readers
- [ ] Keyboard navigation works (Tab through form)
- [ ] Button has proper focus state

### Task 5.3: Manual Testing
- [ ] Test with valid data - should upload
- [ ] Test without title - should show error
- [ ] Test with invalid BPM (>200) - should error
- [ ] Test with non-audio file - should reject at API
- [ ] Test network error handling
- [ ] Test successful upload appears in Sample Library
- [ ] Test uploading multiple files sequentially

### Task 5.4: Code Review Checklist
- [ ] No TypeScript errors
- [ ] No console warnings
- [ ] Proper error handling
- [ ] Loading states work correctly
- [ ] Form resets after success
- [ ] No memory leaks (cleanup effects if needed)

## Verification Checklist

### Pre-Implementation
- [x] UploadDropZone component exists and is complete
- [x] useUploadSample hook exists and works
- [x] Backend upload endpoint is implemented
- [x] All required UI components available

### Post-Implementation Expected
- [ ] Upload page loads without errors
- [ ] Drag-and-drop zone accepts files
- [ ] Metadata form is visible and functional
- [ ] Upload button submits form data
- [ ] Success toast appears after upload
- [ ] New sample appears in Sample Library
- [ ] Error handling works for invalid inputs
- [ ] Form resets after successful upload
- [ ] Accessibility standards met

## Success Metrics

✅ **Critical**: Page loads without errors
✅ **Critical**: Can upload file with required metadata
✅ **Critical**: New sample appears in library after upload
✅ **High**: Success/error notifications work
✅ **High**: Form validation prevents invalid submissions
✅ **Medium**: Loading states show during upload
✅ **Medium**: Responsive design on mobile

## Troubleshooting

### If Upload Fails
1. Check Network tab - verify POST to `/api/v1/public/samples/`
2. Check response status and error message
3. Verify title field is not empty
4. Verify file format is audio (.wav, .mp3, .flac, etc.)
5. Check browser console for JavaScript errors

### If Form Doesn't Update
1. Verify state setter is being called
2. Check onChange handlers are attached to inputs
3. Verify formData state is initialized

### If New Sample Doesn't Appear
1. Check React Query cache - may need manual refresh
2. Verify Sample Library page refetch (useEffect dependency)
3. Check browser console for query errors
4. Try navigating away and back to Sample Library

## Time Estimates

| Phase | Task | Estimate | Actual |
|-------|------|----------|--------|
| 1 | Component integration | 20 min | |
| 2 | Metadata form | 40 min | |
| 3 | Upload logic | 30 min | |
| 4 | Notifications & UX | 30 min | |
| 5 | Polish & testing | 20 min | |
| | **Total** | **~2 hours** | |

## Sign-Off

- [ ] All phases completed
- [ ] All manual tests passed
- [ ] No console errors or warnings
- [ ] Accessibility verified
- [ ] Code review passed
- [ ] Ready for Settings page implementation
