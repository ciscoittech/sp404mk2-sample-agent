# Implement Upload Page - Technical Context

## Current Implementation Status

### UploadPage Component
**File**: `/react-app/src/pages/UploadPage.tsx`
**Status**: Placeholder only (lines 14-18)

```typescript
export function UploadPage() {
  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      <div className="rounded-lg border border-border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          Upload interface will be added here
        </p>
      </div>
    </div>
  );
}
```

### UploadDropZone Component
**File**: `/react-app/src/components/upload/UploadDropZone.tsx`
**Status**: ✅ COMPLETE and fully functional

**What it does**:
```typescript
export function UploadDropZone({
  onFilesSelected,
  maxFileSize = 50 * 1024 * 1024, // 50MB
  maxFiles = 20,
  acceptedFormats = ['audio/wav', 'audio/mpeg', 'audio/flac', ...]
}: UploadDropZoneProps) {
  // Handles drag-and-drop
  // Validates file size and format
  // Shows upload progress
  // Manages file list (add/remove)
  // Returns selected files via callback
}
```

**Features implemented**:
- ✅ Drag-and-drop zone
- ✅ Click to browse files
- ✅ File type validation
- ✅ File size validation
- ✅ Multiple file support
- ✅ Remove individual files
- ✅ Visual feedback
- ✅ Error handling

### Backend Upload Endpoint
**File**: `/backend/app/api/v1/endpoints/public.py:118-195`
**Status**: ✅ Fully implemented

**Endpoint**: `POST /api/v1/public/samples/`

**Request**:
```
Content-Type: multipart/form-data

file: File (binary audio data)
title: string (required, min 1 char)
genre: string (optional)
bpm: string or number (optional, 40-200)
musical_key: string (optional)
tags: string (optional, JSON array format)
```

**Response** (200 OK):
```json
{
  "id": 6,
  "user_id": 1,
  "title": "New Sample",
  "genre": "hip-hop",
  "bpm": 95.0,
  "musical_key": "Am",
  "tags": ["new", "sample"],
  "file_path": "samples/...",
  "file_url": "/api/v1/public/samples/6/download",
  "created_at": "2025-11-16T...",
  "duration": 3.45,
  "file_size": 138240
}
```

**Validation**:
- Title: Required, 1-255 characters
- Genre: Must be one of predefined genres OR custom string
- BPM: 40-200 (will be converted from string to float)
- Musical Key: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
- Tags: JSON array of strings, or comma-separated string
- File: .wav, .mp3, .flac, .aiff, .m4a, .ogg (validated by MIME type)

### React Upload Hook
**File**: `/react-app/src/hooks/useSamples.ts:33-43`

```typescript
export function useUploadSample() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ file, metadata }: {
      file: File;
      metadata?: Partial<Sample>
    }) => samplesApi.upload(file, metadata),
    onSuccess: () => {
      // Auto-refresh sample list after successful upload
      queryClient.invalidateQueries({ queryKey: queryKeys.samples.lists() });
    },
  });
}
```

### API Client Upload Method
**File**: `/react-app/src/api/samples.ts:27-41`

```typescript
upload: async (file: File, metadata?: Partial<Sample>) => {
  const formData = new FormData();
  formData.append('file', file);
  if (metadata) {
    Object.entries(metadata).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        // Convert arrays to JSON strings for form submission
        formData.append(key, String(value));
      }
    });
  }
  const { data } = await apiClient.post<Sample>('/samples', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
```

## Available UI Components

### Existing Components Ready to Use
**Location**: `/react-app/src/components/ui/`

- **Button** - CTA buttons
- **Input** - Text inputs for title, BPM
- **Label** - Form labels
- **Select** - Genre dropdown
- **Textarea** - For tags input
- **Card** - Container for sections
- **Alert** - For error messages
- **Spinner/Loader** - Loading states
- **Toast** - Via sonner library

### Related Custom Components
- **SampleCard** - Display uploaded sample (for preview)
- **FilterPanel** - Genre/filter UI (can reuse for metadata)

## Data Types

### Sample Type
**File**: `/react-app/src/types/api.ts:40-70`

```typescript
export interface Sample {
  id: number;
  title: string;
  genre?: string;
  bpm?: number;
  musical_key?: string;
  tags: string[];
  user_id: number;
  file_path: string;
  file_size?: number;
  duration?: number;
  created_at: string;
  analyzed_at?: string;
  last_accessed_at?: string;
  file_url?: string;
  vibe_analysis?: VibeAnalysisResponse;
}
```

### Upload Form Data Type (to create)
```typescript
interface SampleUploadForm {
  title: string;           // Required
  genre?: string;          // Optional
  bpm?: number;            // Optional, 40-200
  musical_key?: string;    // Optional
  tags?: string[];         // Optional
}
```

## Available Genres
From FilterPanel.tsx, supported genres:
```
Hip-Hop, Trap, Jazz, Soul, Electronic, House,
Drum & Bass, Lo-Fi, Ambient, Funk, Disco, R&B,
Techno, Dubstep
```

## Error Handling

### Validation Errors (400)
```json
{
  "detail": "title: must be 1-255 characters"
}
```

### File Type Errors
Backend rejects: .txt, .pdf, .doc, images, etc.
Only accepts: .wav, .mp3, .flac, .aiff, .m4a, .ogg

### Network Errors
Handled by React Query mutation error state

## Toast Notification Setup

**Library**: sonner (already installed)
**Import**: `import { toast } from 'sonner'`

**Usage**:
```typescript
toast.success('Sample uploaded successfully!');
toast.error('Upload failed: invalid file type');
toast.loading('Uploading...');
```

## Related Features

### Post-Upload Actions
1. **View Sample** - Link to sample in Sample Library
2. **Analyze Sample** - Trigger AI analysis
3. **Upload Another** - Reset form for next upload
4. **View Details** - Show uploaded sample metadata

### Auto-Analysis (Optional)
The backend supports analyzing samples post-upload:
```
POST /api/v1/public/samples/{sample_id}/analyze
```

Could add checkbox: "Auto-analyze after upload?"

## Page Layout Options

### Option A: Upload Form Only
```
UploadPage
├── Title "Upload Samples"
├── UploadDropZone (full width)
└── Metadata form below
```

### Option B: Multi-section Layout
```
UploadPage
├── Upload section
│   ├── UploadDropZone
│   └── Metadata form
├── Recent uploads
│   └── List of just-uploaded samples
└── Help section
```

### Option C: Sidebar Layout
```
UploadPage
├── Left sidebar
│   └── Upload form
└── Right content
    └── UploadDropZone + help
```

Recommended: **Option A** (simple and clean)

## Performance Considerations

- Large file uploads (50MB max) may take time - show progress
- Metadata parsing (JSON tags) is instant
- Sample list refresh is automatic via React Query
- No heavy processing needed client-side

## Browser Compatibility

- UploadDropZone uses standard File API (works in all modern browsers)
- FormData API for multipart submission (standard)
- Drag-and-drop supported in Chrome, Firefox, Safari, Edge

## Dependencies Summary

**No new packages needed!**

All required dependencies already in project:
- ✅ react-dropzone (in UploadDropZone)
- ✅ sonner (for toast notifications)
- ✅ react-query (for mutations)
- ✅ Radix UI components (for form UI)
- ✅ TypeScript (for types)

## Testing Resources

### Test Files Location
`/react-app/src/api/__tests__/`

### Example Test Data
Available sample files in `/samples/` directory:
- jazz_dark_1.wav
- trap_energy_1.wav
- hiphop_chill_1.wav
- soul_moody_1.wav
- electronic_upbeat_1.wav

## Security Notes

- File size limit: 50MB (enforced client + server)
- Allowed formats: audio only (enforced server)
- CORS configured for localhost:5173 (safe for dev)
- All inputs sanitized by Pydantic on backend
- No direct file path exposure to users
