# FilterPanel Backend Integration Guide

How to connect the FilterPanel component to the FastAPI backend.

## Backend API Endpoint

The FilterPanel is designed to work with this FastAPI endpoint structure:

```python
# backend/app/api/v1/endpoints/public.py

from typing import Optional
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/api/samples")
async def get_samples(
    # Genre filter (multi-select)
    genres: Optional[str] = Query(None, description="Comma-separated genres"),

    # BPM range
    bpm_min: Optional[int] = Query(60, ge=60, le=180),
    bpm_max: Optional[int] = Query(180, ge=60, le=180),

    # Musical key
    key: Optional[str] = Query(None, regex="^[A-G](#|b)?$"),
    key_mode: Optional[str] = Query(None, regex="^(major|minor)$"),

    # Tags (multi-select)
    tags: Optional[str] = Query(None, description="Comma-separated tags"),

    # Pagination
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get samples with optional filters.

    Example: /api/samples?genres=Hip-Hop,Jazz&bpm_min=90&bpm_max=120&tags=Vintage,Warm
    """
    # Parse comma-separated values
    genre_list = genres.split(",") if genres else None
    tag_list = tags.split(",") if tags else None

    # Build database query
    query = db.query(Sample)

    if genre_list:
        query = query.filter(Sample.genre.in_(genre_list))

    if bpm_min and bpm_max:
        query = query.filter(
            Sample.bpm >= bpm_min,
            Sample.bpm <= bpm_max
        )

    if key:
        query = query.filter(Sample.key == key)
        if key_mode:
            query = query.filter(Sample.key_mode == key_mode)

    if tag_list:
        # Assuming tags are stored as JSON array or separate table
        query = query.filter(Sample.tags.overlap(tag_list))

    # Execute query
    total = query.count()
    samples = query.offset(skip).limit(limit).all()

    return {
        "samples": samples,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

## React Integration with TanStack Query

### 1. Create API Hook

```typescript
// src/hooks/useSamples.ts

import { useQuery } from '@tanstack/react-query';
import { SampleFilters } from '@/components/samples';

interface Sample {
  id: number;
  name: string;
  genre: string;
  bpm: number;
  key?: string;
  key_mode?: string;
  tags: string[];
  file_path: string;
}

interface SamplesResponse {
  samples: Sample[];
  total: number;
  skip: number;
  limit: number;
}

function buildQueryString(filters: SampleFilters): string {
  const params = new URLSearchParams();

  // Genres (array → comma-separated)
  if (filters.genres && filters.genres.length > 0) {
    params.append('genres', filters.genres.join(','));
  }

  // BPM range
  if (filters.bpm_min !== undefined) {
    params.append('bpm_min', filters.bpm_min.toString());
  }
  if (filters.bpm_max !== undefined) {
    params.append('bpm_max', filters.bpm_max.toString());
  }

  // Musical key
  if (filters.key) {
    params.append('key', filters.key);
    if (filters.key_mode) {
      params.append('key_mode', filters.key_mode);
    }
  }

  // Tags (array → comma-separated)
  if (filters.tags && filters.tags.length > 0) {
    params.append('tags', filters.tags.join(','));
  }

  return params.toString();
}

export function useSamples(filters: SampleFilters, skip = 0, limit = 50) {
  const queryString = buildQueryString(filters);

  return useQuery<SamplesResponse>({
    queryKey: ['samples', filters, skip, limit],
    queryFn: async () => {
      const params = new URLSearchParams(queryString);
      params.append('skip', skip.toString());
      params.append('limit', limit.toString());

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/samples?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch samples');
      }

      return response.json();
    },
    // Stale time: 5 minutes
    staleTime: 5 * 60 * 1000,
  });
}
```

### 2. Samples Page Component

```typescript
// src/pages/SamplesPage.tsx

import { useState } from 'react';
import { FilterPanel, SampleFilters, SampleGrid } from '@/components/samples';
import { useSamples } from '@/hooks/useSamples';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

export function SamplesPage() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  const [page, setPage] = useState(0);
  const limit = 50;

  // Fetch samples with current filters
  const { data, isLoading, isError, error } = useSamples(
    filters,
    page * limit,
    limit
  );

  return (
    <div className="flex min-h-screen">
      {/* Sidebar with filters */}
      <aside className="w-80 border-r bg-background p-4 overflow-y-auto sticky top-0 h-screen">
        <FilterPanel
          filters={filters}
          onChange={setFilters}
        />
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Sample Library</h1>
          {data && (
            <p className="text-muted-foreground mt-2">
              Showing {data.samples.length} of {data.total} samples
            </p>
          )}
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {/* Error state */}
        {isError && (
          <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
            <p className="text-destructive">
              Error loading samples: {error.message}
            </p>
          </div>
        )}

        {/* Samples grid */}
        {data && (
          <>
            <SampleGrid samples={data.samples} />

            {/* Pagination */}
            <div className="mt-8 flex items-center justify-center gap-4">
              <Button
                variant="outline"
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page + 1} of {Math.ceil(data.total / limit)}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(data.total / limit) - 1}
              >
                Next
              </Button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
```

### 3. Mobile Responsive Version

```typescript
// src/pages/SamplesPage.tsx (mobile version)

import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { SlidersHorizontal } from 'lucide-react';

export function SamplesPageResponsive() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });
  const [filterSheetOpen, setFilterSheetOpen] = useState(false);

  const { data, isLoading } = useSamples(filters);

  return (
    <div className="min-h-screen">
      {/* Mobile filter button */}
      <div className="sticky top-0 z-10 bg-background border-b p-4 md:hidden">
        <Sheet open={filterSheetOpen} onOpenChange={setFilterSheetOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" className="w-full">
              <SlidersHorizontal className="h-4 w-4 mr-2" />
              Filters {filters.genres && `(${filters.genres.length})`}
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-80 overflow-y-auto">
            <FilterPanel
              filters={filters}
              onChange={(newFilters) => {
                setFilters(newFilters);
                setFilterSheetOpen(false); // Close after applying
              }}
              className="mt-6"
            />
          </SheetContent>
        </Sheet>
      </div>

      <div className="flex">
        {/* Desktop sidebar */}
        <aside className="hidden md:block w-80 border-r p-4 sticky top-0 h-screen overflow-y-auto">
          <FilterPanel filters={filters} onChange={setFilters} />
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          {/* ... same as above ... */}
        </main>
      </div>
    </div>
  );
}
```

## URL State Synchronization

For shareable filter URLs:

```typescript
// src/hooks/useFilterState.ts

import { useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { SampleFilters } from '@/components/samples';

export function useFilterState() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize from URL
  const [filters, setFilters] = useState<SampleFilters>(() => {
    const genres = searchParams.get('genres')?.split(',').filter(Boolean);
    const bpm_min = searchParams.get('bpm_min');
    const bpm_max = searchParams.get('bpm_max');
    const key = searchParams.get('key') || undefined;
    const key_mode = searchParams.get('key_mode') as 'major' | 'minor' | undefined;
    const tags = searchParams.get('tags')?.split(',').filter(Boolean);

    return {
      genres: genres?.length ? genres : undefined,
      bpm_min: bpm_min ? parseInt(bpm_min) : 60,
      bpm_max: bpm_max ? parseInt(bpm_max) : 180,
      key,
      key_mode,
      tags: tags?.length ? tags : undefined,
    };
  });

  // Sync to URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();

    if (filters.genres?.length) {
      params.set('genres', filters.genres.join(','));
    }
    if (filters.bpm_min !== 60) {
      params.set('bpm_min', filters.bpm_min.toString());
    }
    if (filters.bpm_max !== 180) {
      params.set('bpm_max', filters.bpm_max.toString());
    }
    if (filters.key) {
      params.set('key', filters.key);
    }
    if (filters.key_mode) {
      params.set('key_mode', filters.key_mode);
    }
    if (filters.tags?.length) {
      params.set('tags', filters.tags.join(','));
    }

    setSearchParams(params, { replace: true });
  }, [filters, setSearchParams]);

  return [filters, setFilters] as const;
}

// Usage in component:
const [filters, setFilters] = useFilterState();
```

## Available Tags from Backend

Fetch available tags from backend:

```typescript
// src/hooks/useAvailableTags.ts

import { useQuery } from '@tanstack/react-query';

export function useAvailableTags() {
  return useQuery<string[]>({
    queryKey: ['available-tags'],
    queryFn: async () => {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/tags`
      );
      return response.json();
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

// Usage:
function SamplesPage() {
  const { data: availableTags } = useAvailableTags();

  return (
    <FilterPanel
      filters={filters}
      onChange={setFilters}
      availableTags={availableTags}
    />
  );
}
```

Backend endpoint:

```python
@router.get("/api/tags")
async def get_available_tags():
    """Get all unique tags across all samples."""
    tags = db.query(Sample.tags).distinct().all()
    # Flatten and deduplicate
    all_tags = set()
    for (tag_array,) in tags:
        all_tags.update(tag_array)
    return sorted(all_tags)
```

## Real-time Filter Stats

Show count of samples per filter option:

```python
@router.get("/api/filter-stats")
async def get_filter_stats():
    """Get counts for each filter option."""
    genre_counts = (
        db.query(Sample.genre, func.count(Sample.id))
        .group_by(Sample.genre)
        .all()
    )

    tag_counts = (
        db.query(Sample.tags, func.count(Sample.id))
        .group_by(Sample.tags)
        .all()
    )

    return {
        "genres": {genre: count for genre, count in genre_counts},
        "tags": {tag: count for tag, count in tag_counts},
        "bpm_range": {
            "min": db.query(func.min(Sample.bpm)).scalar(),
            "max": db.query(func.max(Sample.bpm)).scalar(),
        }
    }
```

Use in UI:

```typescript
function GenreButton({ genre, count }: { genre: string; count: number }) {
  return (
    <button>
      <span>{genre}</span>
      <Badge variant="secondary">{count}</Badge>
    </button>
  );
}
```

## Performance Optimization

### Debounced Filter Changes

```typescript
import { useDebouncedCallback } from 'use-debounce';

function SamplesPage() {
  const [localFilters, setLocalFilters] = useState(filters);

  const debouncedSetFilters = useDebouncedCallback(
    (newFilters) => setFilters(newFilters),
    300 // 300ms delay
  );

  const handleFilterChange = (newFilters: SampleFilters) => {
    setLocalFilters(newFilters); // Immediate UI update
    debouncedSetFilters(newFilters); // Debounced API call
  };

  return (
    <FilterPanel
      filters={localFilters}
      onChange={handleFilterChange}
    />
  );
}
```

### Cache Filter Results

```typescript
const { data } = useQuery({
  queryKey: ['samples', filters],
  queryFn: fetchSamples,
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 30 * 60 * 1000, // 30 minutes
});
```

## Environment Setup

```env
# .env
VITE_API_URL=http://localhost:8100
```

## Error Handling

```typescript
const { data, error, isError } = useSamples(filters);

if (isError) {
  if (error.message.includes('400')) {
    // Invalid filter parameters
    toast.error('Invalid filter parameters');
  } else if (error.message.includes('500')) {
    // Server error
    toast.error('Server error. Please try again.');
  } else {
    // Network error
    toast.error('Network error. Please check your connection.');
  }
}
```

## Testing Integration

```typescript
// src/components/samples/__tests__/FilterPanel.integration.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SamplesPage } from '@/pages/SamplesPage';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/samples', (req, res, ctx) => {
    const genres = req.url.searchParams.get('genres');

    return res(
      ctx.json({
        samples: [
          { id: 1, name: 'Sample 1', genre: 'Hip-Hop' },
        ],
        total: 1,
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('filters samples by genre', async () => {
  const queryClient = new QueryClient();

  render(
    <QueryClientProvider client={queryClient}>
      <SamplesPage />
    </QueryClientProvider>
  );

  // Click Hip-Hop genre
  const hipHopButton = screen.getByRole('button', { name: /hip-hop/i });
  await userEvent.click(hipHopButton);

  // Wait for filtered results
  await waitFor(() => {
    expect(screen.getByText('Sample 1')).toBeInTheDocument();
  });
});
```

This integration guide provides everything needed to connect the FilterPanel to your backend API!
