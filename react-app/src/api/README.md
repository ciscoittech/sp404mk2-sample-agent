# API Client Layer

Complete API integration for FastAPI backend communication.

## Structure

```
src/
├── api/
│   ├── client.ts         # Axios client with interceptors
│   ├── samples.ts        # Samples endpoint functions
│   ├── kits.ts          # Kits endpoint functions
│   ├── preferences.ts   # User preferences endpoints
│   └── index.ts         # Barrel export
├── hooks/
│   ├── useSamples.ts    # React Query hooks for samples
│   ├── useKits.ts       # React Query hooks for kits
│   └── usePreferences.ts # React Query hooks for preferences
├── lib/
│   └── queryClient.ts   # React Query configuration & keys
└── types/
    └── api.ts           # TypeScript type definitions
```

## Usage Examples

### Fetching Samples

```typescript
import { useSamples } from '@/hooks/useSamples';

function SampleList() {
  const { data, isLoading, error } = useSamples({
    page: 1,
    limit: 20,
    genre: 'hip-hop',
    bpm_min: 80,
    bpm_max: 120,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data?.items.map(sample => (
        <div key={sample.id}>{sample.title}</div>
      ))}
    </div>
  );
}
```

### Creating a Kit

```typescript
import { useCreateKit } from '@/hooks/useKits';

function CreateKitButton() {
  const createKit = useCreateKit();

  const handleCreate = () => {
    createKit.mutate({
      name: 'My New Kit',
      description: 'A dope kit',
      is_public: false,
    }, {
      onSuccess: (kit) => {
        console.log('Kit created:', kit.id);
      },
    });
  };

  return (
    <button onClick={handleCreate} disabled={createKit.isPending}>
      {createKit.isPending ? 'Creating...' : 'Create Kit'}
    </button>
  );
}
```

### Assigning Sample to Pad

```typescript
import { useAssignSample } from '@/hooks/useKits';

function PadAssigner({ kitId }: { kitId: number }) {
  const assignSample = useAssignSample();

  const handleAssign = (sampleId: number) => {
    assignSample.mutate({
      kitId,
      assignment: {
        sample_id: sampleId,
        pad_bank: 'A',
        pad_number: 1,
        volume: 0.8,
      },
    });
  };

  return <button onClick={() => handleAssign(123)}>Assign to A1</button>;
}
```

### Direct API Calls (without hooks)

```typescript
import { samplesApi, kitsApi } from '@/api';

// Fetch samples
const samples = await samplesApi.list({ genre: 'jazz' });

// Get single sample
const sample = await samplesApi.getById(123);

// Upload sample
const file = document.querySelector('input[type="file"]').files[0];
const newSample = await samplesApi.upload(file, {
  title: 'My Sample',
  genre: 'hip-hop',
});

// Create kit
const kit = await kitsApi.create({ name: 'My Kit' });

// Build kit with AI
const aiKit = await kitsApi.buildWithAI('Create a lo-fi hip-hop kit');
```

## Query Keys

Consistent cache management using structured query keys:

```typescript
import { queryKeys } from '@/lib/queryClient';

// Samples
queryKeys.samples.all              // ['samples']
queryKeys.samples.lists()          // ['samples', 'list']
queryKeys.samples.list({ genre })  // ['samples', 'list', { genre }]
queryKeys.samples.detail(123)      // ['samples', 'detail', 123]

// Kits
queryKeys.kits.all                 // ['kits']
queryKeys.kits.lists()             // ['kits', 'list']
queryKeys.kits.detail(456)         // ['kits', 'detail', 456]

// Preferences
queryKeys.preferences.all          // ['preferences']
```

## Error Handling

All API calls include automatic error handling:

```typescript
const { data, error } = useSamples();

if (error) {
  // Error is typed as AxiosError
  console.error('API Error:', error.response?.data);
}
```

## Configuration

### Base URL
Configured in `src/api/client.ts`:
- Development: `/api/v1` (proxied to `http://127.0.0.1:8100`)
- Production: Set `VITE_API_URL` environment variable

### Proxy Setup
Vite proxy configured in `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': 'http://127.0.0.1:8100',
    '/ws': {
      target: 'ws://127.0.0.1:8100',
      ws: true,
    },
  },
}
```

## Type Safety

All API responses are fully typed:

```typescript
import type { Sample, Kit, PaginatedResponse } from '@/types/api';

// Sample type includes all fields
const sample: Sample = {
  id: 1,
  user_id: 1,
  title: 'My Sample',
  file_path: '/path/to/file.wav',
  tags: ['hip-hop', 'drums'],
  audio_features: { bpm: 90, key: 'C', scale: 'minor' },
  ai_analysis: {
    genre_tags: ['hip-hop'],
    mood_tags: ['dark', 'atmospheric'],
    description: 'Dark atmospheric drums',
    confidence: 0.95,
  },
};
```

## Backend API Endpoints

### Samples
- `GET /api/v1/samples` - List samples (paginated, filterable)
- `GET /api/v1/samples/{id}` - Get sample by ID
- `POST /api/v1/samples` - Upload sample
- `PATCH /api/v1/samples/{id}` - Update sample
- `DELETE /api/v1/samples/{id}` - Delete sample
- `POST /api/v1/samples/{id}/analyze` - Analyze with AI
- `GET /api/v1/samples/{id}/audio-features` - Get audio features

### Kits
- `GET /api/v1/kits` - List kits
- `GET /api/v1/kits/{id}` - Get kit by ID
- `POST /api/v1/kits` - Create kit
- `PATCH /api/v1/kits/{id}` - Update kit
- `DELETE /api/v1/kits/{id}` - Delete kit
- `POST /api/v1/kits/{id}/assign` - Assign sample to pad
- `DELETE /api/v1/kits/{id}/pads/{bank}/{number}` - Remove sample
- `GET /api/v1/kits/{id}/export` - Export kit
- `POST /api/v1/kits/build` - Build kit with AI

### Preferences
- `GET /api/v1/preferences` - Get user preferences
- `PATCH /api/v1/preferences` - Update preferences

## Testing API Integration

Start the backend server:
```bash
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent
./venv/bin/python backend/run.py
```

Start the React app:
```bash
cd react-app
npm run dev
```

Access at: http://localhost:5173 (proxied to backend at :8100)
