# Similarity Search UI - Phase 3 Implementation

## Overview

Implemented the Similarity Search UI layer for the SP-404MK2 Sample Agent. This feature allows users to find similar samples based on vibe, musical characteristics, and audio features using the existing backend endpoint.

## Components Created

### 1. SimilarSamplesPanel (~150 lines)
**File**: `src/components/similarity/SimilarSamplesPanel.tsx`

**Features**:
- Slide-in panel from right side (Radix UI Sheet)
- "Finding Similar Samples..." loading state with skeleton cards
- Lists up to 10 similar samples
- Empty state for no results
- Error state with retry button
- ScrollArea for smooth scrolling
- Results count display
- Close button (X icon)

**Integration**: Triggered from SampleCard "Find Similar" button

### 2. MatchingVisualization (~245 lines)
**File**: `src/components/similarity/MatchingVisualization.tsx`

**Features**:
- **Compact version**: 3 colored dots showing top similarity scores
  - Green (>80%): Perfect match
  - Yellow (60-80%): Good match
  - Orange (40-60%): Partial match
  - Red (<40%): Weak match
- **Expandable version**: Full modal with detailed breakdown
  - Similarity score summary
  - Score bars for Vibe, Energy, Danceability, Acousticness
  - Detailed attribute table (BPM, Key, Genre, Mood, Energy, Tags)
  - Color-coded legend
- Interactive tooltips
- Dark mode support

**Data Displayed**:
- Vibe similarity (from embedding)
- Energy level
- Danceability
- Acousticness
- BPM, Musical Key, Genre
- Mood (primary/secondary)
- Vibe tags

### 3. SimilarSampleResult (~150 lines)
**File**: `src/components/similarity/SimilarSampleResult.tsx`

**Features**:
- Single similar sample result card
- Similarity score badge (color-coded)
- Sample metadata (title, duration, BPM, key, genre, mood)
- Compact matching visualization (3 dots)
- Add to collection button
- Preview button (plays sample on click)
- Hover effects with action buttons
- Vibe tags display

**Interactions**:
- Click anywhere → Play preview
- Click score/dots → Show MatchingVisualization modal
- Click "Add to Collection" → Open collection menu
- Hover → Show action buttons

## API Integration

### API Client Updates
**File**: `src/api/samples.ts`

Added `findSimilar` method:
```typescript
findSimilar: async (id: number, options?: { limit?: number }) => {
  const params = new URLSearchParams();
  if (options?.limit) {
    params.append('limit', String(options.limit));
  }
  const { data } = await apiClient.get<SimilarSamplesResponse>(
    `/search/similar/${id}?${params}`
  );
  return data.results;
}
```

**Endpoint**: `GET /api/v1/search/similar/{id}?limit=10`
**Backend Router**: Mounted at `/api/v1/search` (vibe_search router)

### Type Definitions
**File**: `src/types/api.ts`

Added types:
```typescript
export interface SimilarityResult {
  id: number;
  title: string;
  bpm?: number;
  musical_key?: string;
  genre?: string;
  duration?: number;
  similarity: number; // 0.0-1.0
  mood?: string;
  mood_secondary?: string;
  energy_level?: number;
  danceability?: number;
  vibe_tags: string[];
  acousticness?: number;
  instrumentalness?: number;
  preview_url: string;
  full_url: string;
}

export interface SimilarSamplesResponse {
  reference_sample_id: number;
  results: SimilarityResult[];
  count: number;
}
```

### React Query Hooks
**File**: `src/hooks/useSimilarity.ts`

Created `useSimilarSamples` hook:
```typescript
export function useSimilarSamples(
  sampleId: number | null,
  options?: { limit?: number }
) {
  return useQuery({
    queryKey: queryKeys.samples.similar(sampleId!),
    queryFn: () => samplesApi.findSimilar(sampleId!, options),
    enabled: !!sampleId,
  });
}
```

**Cache Key**: Added to `src/lib/queryClient.ts`:
```typescript
similar: (id: number) => [...queryKeys.samples.all, 'similar', id] as const
```

## SampleCard Integration

**File**: `src/components/samples/SampleCard.tsx`

Added:
- Import of `SimilarSamplesPanel` and `Search` icon
- State: `const [similarPanelOpen, setSimilarPanelOpen] = useState(false)`
- "Find Similar" button in card header (appears on hover)
- `SimilarSamplesPanel` component at end of card

Button location: After PinButton, before AddToCollection, before Play

## Styling & UX

### Color Scheme
- **Green (#10b981)**: >80% match (Perfect)
- **Yellow (#f59e0b)**: 60-80% match (Good)
- **Orange (#f97316)**: 40-60% match (Partial)
- **Red (#ef4444)**: <40% match (Weak)

### Animations
- Panel slide-in from right (Sheet component)
- Hover effects with shadow on result cards
- Smooth transitions for action buttons
- Skeleton loading animation

### Responsive Design
- Mobile: Full width sheet
- Tablet/Desktop: Max width 512px (sm:max-w-lg)
- Touch-friendly button sizes
- Scroll area for long result lists

### Dark Mode
- Fully supported via Tailwind CSS theme
- Color-coded badges work in both modes
- Text colors adjusted for readability

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support (Sheet component)
- Screen reader friendly
- Focus management
- Semantic HTML structure

## Testing Checklist

### Manual Testing Scenarios
1. ✅ Click "Find Similar" button on sample card
2. ✅ Panel opens with loading state (skeleton cards)
3. ✅ Results load and display with similarity scores
4. ✅ Click result to preview audio
5. ✅ Click colored dots to expand matching visualization
6. ✅ View detailed similarity breakdown in modal
7. ✅ Add result to collection via dropdown
8. ✅ Close panel via X button or clicking outside
9. ✅ Empty state displays when no similar samples found
10. ✅ Error state displays with retry button on failure
11. ✅ Hover effects work on result cards
12. ✅ Dark mode styling is correct

### Type Safety
- ✅ TypeScript compilation passes (`npx tsc --noEmit`)
- ✅ Build succeeds (`npm run build`)
- ✅ All types properly defined and imported
- ✅ No type errors in components

### Integration Points
- ✅ SampleCard integration working
- ✅ API client method added
- ✅ React Query hooks created
- ✅ Cache keys configured
- ✅ Backend endpoint verified (`/api/v1/search/similar/{id}`)

## File Structure

```
react-app/src/
├── components/
│   ├── similarity/
│   │   ├── index.ts                      # Barrel export
│   │   ├── SimilarSamplesPanel.tsx       # Main panel component
│   │   ├── SimilarSampleResult.tsx       # Single result card
│   │   └── MatchingVisualization.tsx     # Similarity visualization
│   └── samples/
│       └── SampleCard.tsx                # Updated with "Find Similar" button
├── hooks/
│   └── useSimilarity.ts                  # React Query hook
├── api/
│   └── samples.ts                        # Updated with findSimilar method
├── types/
│   └── api.ts                            # Updated with SimilarityResult types
└── lib/
    └── queryClient.ts                    # Updated with similarity cache key
```

## Line Counts

- **SimilarSamplesPanel**: ~150 lines
- **MatchingVisualization**: ~245 lines
- **SimilarSampleResult**: ~150 lines
- **Hook (useSimilarity)**: ~15 lines
- **API Client Update**: ~12 lines
- **Type Definitions**: ~25 lines
- **SampleCard Integration**: ~15 lines
- **Total**: ~612 lines

## Dependencies Used

All existing dependencies, no new packages required:
- @radix-ui/react-dialog (Dialog, Sheet)
- @tanstack/react-query (useQuery)
- lucide-react (Icons)
- Tailwind CSS (Styling)
- shadcn/ui components (Badge, Button, Card, Table, ScrollArea)

## Backend Compatibility

The UI is fully compatible with the existing backend endpoint:

**Endpoint**: `GET /api/v1/search/similar/{sample_id}?limit=10`
**Router**: `vibe_search.router` mounted at `/search`
**Response**: `SimilarSamplesResponse` with results array

No backend changes required.

## Next Steps

The Similarity Search UI (Phase 3) is complete. The implementation:

1. ✅ Exposes the existing backend endpoint in the UI
2. ✅ Provides intuitive similarity visualization
3. ✅ Integrates seamlessly with existing components
4. ✅ Follows project patterns and conventions
5. ✅ Includes proper error handling and loading states
6. ✅ Supports dark mode and accessibility
7. ✅ Type-safe and well-tested

Ready for Phase 4 (Metadata schema and extraction service).

## Usage Example

```typescript
// From any component with a sample ID
import { SimilarSamplesPanel } from '@/components/similarity';

function MyComponent({ sampleId }: { sampleId: number }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        Find Similar Samples
      </Button>

      <SimilarSamplesPanel
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        sampleId={sampleId}
        onSelect={(selectedId) => {
          console.log('Selected sample:', selectedId);
        }}
      />
    </>
  );
}
```

## Known Limitations

1. Audio preview uses `full_url` which points to download endpoint (may be slow for large files)
2. Similarity calculation is entirely backend-driven (no client-side scoring)
3. No pagination support yet (fixed limit of 10 results)
4. onSelect callback only passes sampleId (not full Sample object)

These are minor and don't impact the core functionality.
