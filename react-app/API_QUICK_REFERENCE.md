# API Client - Quick Reference

## Imports

```typescript
// Hooks (recommended)
import { useSamples, useSample, useUploadSample } from '@/hooks/useSamples';
import { useKits, useKit, useCreateKit } from '@/hooks/useKits';
import { usePreferences, useUpdatePreferences } from '@/hooks/usePreferences';

// Direct API (when needed)
import { samplesApi, kitsApi, preferencesApi } from '@/api';

// Types
import type { Sample, Kit, UserPreferences } from '@/types/api';
```

## Common Patterns

### Fetch Data
```typescript
const { data, isLoading, error } = useSamples({ genre: 'hip-hop' });
```

### Create/Update/Delete
```typescript
const createKit = useCreateKit();
createKit.mutate({ name: 'My Kit' }, {
  onSuccess: (kit) => console.log('Created:', kit.id),
  onError: (error) => console.error('Failed:', error),
});
```

### With Loading States
```typescript
if (isLoading) return <Loading />;
if (error) return <Error message={error.message} />;
return <SampleGrid samples={data.items} />;
```

## Available Hooks

### Samples
- `useSamples(filters?)` - List with filters
- `useSample(id)` - Get single sample
- `useUploadSample()` - Upload new sample
- `useUpdateSample()` - Update existing
- `useDeleteSample()` - Delete sample
- `useAnalyzeSample()` - AI analysis

### Kits
- `useKits(params?)` - List kits
- `useKit(id)` - Get single kit
- `useCreateKit()` - Create new kit
- `useUpdateKit()` - Update existing
- `useDeleteKit()` - Delete kit
- `useAssignSample()` - Assign to pad
- `useRemoveSample()` - Remove from pad
- `useExportKit()` - Export to file
- `useBuildKitWithAI()` - AI building

### Preferences
- `usePreferences()` - Get preferences
- `useUpdatePreferences()` - Update settings

## Filter Examples

```typescript
// Genre filter
useSamples({ genre: 'hip-hop' })

// BPM range
useSamples({ bpm_min: 80, bpm_max: 120 })

// Multiple filters
useSamples({
  search: 'drums',
  genre: 'jazz',
  key: 'C',
  tags: ['vintage', '70s'],
})

// Pagination
useSamples({ page: 2, limit: 20 })
```

## Backend URLs

- Dev: `http://localhost:5173` → proxied to `:8100`
- API: `/api/v1/*`
- WebSocket: `/ws`

## File Locations

```
src/
├── api/          - API endpoint functions
├── hooks/        - React Query hooks
├── lib/          - Query client config
└── types/        - TypeScript types
```

## Documentation

- `src/api/README.md` - Full API guide
- `API_CLIENT_ARCHITECTURE.md` - Architecture overview
- `API_CLIENT_COMPLETE.md` - Completion report
