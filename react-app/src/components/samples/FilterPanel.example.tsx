/**
 * FilterPanel Usage Examples
 *
 * This file demonstrates how to use the FilterPanel component
 * in different scenarios within the Samples page.
 */

import { useState } from 'react';
import { FilterPanel, SampleFilters } from './FilterPanel';

/**
 * Example 1: Basic Usage with State Management
 *
 * The simplest way to use FilterPanel is with local state.
 * The component is controlled - you manage the filter state.
 */
export function BasicFilterExample() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  // This handler receives updated filters whenever they change
  const handleFilterChange = (newFilters: SampleFilters) => {
    setFilters(newFilters);
    // Optionally trigger sample refetch here
    console.log('Filters updated:', newFilters);
  };

  return (
    <div className="w-80">
      <FilterPanel filters={filters} onChange={handleFilterChange} />
    </div>
  );
}

/**
 * Example 2: Sidebar Layout
 *
 * Use FilterPanel in a sidebar with custom styling
 */
export function SidebarFilterExample() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-80 border-r bg-background p-4 overflow-y-auto">
      <FilterPanel
        filters={filters}
        onChange={setFilters}
        className="sticky top-0"
      />
    </aside>
  );
}

/**
 * Example 3: With Custom Available Tags
 *
 * Pass custom tags fetched from your API
 */
export function CustomTagsExample() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  // These could come from an API call
  const availableTags = [
    'Custom Tag 1',
    'Custom Tag 2',
    'Special',
    'Featured',
    'New',
  ];

  return (
    <div className="w-80">
      <FilterPanel
        filters={filters}
        onChange={setFilters}
        availableTags={availableTags}
      />
    </div>
  );
}

/**
 * Example 4: Integrated with Sample Fetching
 *
 * Real-world example showing integration with data fetching
 */
export function IntegratedExample() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });

  // This function would trigger your sample fetch
  const fetchSamples = (filters: SampleFilters) => {
    const params = new URLSearchParams();

    if (filters.genres && filters.genres.length > 0) {
      params.append('genres', filters.genres.join(','));
    }
    if (filters.bpm_min) {
      params.append('bpm_min', filters.bpm_min.toString());
    }
    if (filters.bpm_max) {
      params.append('bpm_max', filters.bpm_max.toString());
    }
    if (filters.key) {
      params.append('key', filters.key);
    }
    if (filters.key_mode) {
      params.append('key_mode', filters.key_mode);
    }
    if (filters.tags && filters.tags.length > 0) {
      params.append('tags', filters.tags.join(','));
    }

    console.log(`Fetching: /api/samples?${params.toString()}`);
    // fetch(`/api/samples?${params.toString()}`).then(...)
  };

  const handleFilterChange = (newFilters: SampleFilters) => {
    setFilters(newFilters);
    fetchSamples(newFilters);
  };

  return (
    <div className="flex gap-6">
      {/* Sidebar with filters */}
      <aside className="w-80 shrink-0">
        <FilterPanel filters={filters} onChange={handleFilterChange} />
      </aside>

      {/* Main content area */}
      <main className="flex-1">
        <h1>Samples</h1>
        {/* Sample grid would go here */}
      </main>
    </div>
  );
}

/**
 * Example 5: With URL Query Params
 *
 * Sync filters with URL for shareable links
 */
export function URLSyncExample() {
  const [filters, setFilters] = useState<SampleFilters>(() => {
    // Initialize from URL params
    const params = new URLSearchParams(window.location.search);
    return {
      genres: params.get('genres')?.split(','),
      bpm_min: params.get('bpm_min') ? parseInt(params.get('bpm_min')!) : 60,
      bpm_max: params.get('bpm_max') ? parseInt(params.get('bpm_max')!) : 180,
      key: params.get('key') || undefined,
      key_mode: (params.get('key_mode') as 'major' | 'minor') || undefined,
      tags: params.get('tags')?.split(','),
    };
  });

  const handleFilterChange = (newFilters: SampleFilters) => {
    setFilters(newFilters);

    // Update URL
    const params = new URLSearchParams();
    if (newFilters.genres?.length) params.set('genres', newFilters.genres.join(','));
    if (newFilters.bpm_min) params.set('bpm_min', newFilters.bpm_min.toString());
    if (newFilters.bpm_max) params.set('bpm_max', newFilters.bpm_max.toString());
    if (newFilters.key) params.set('key', newFilters.key);
    if (newFilters.key_mode) params.set('key_mode', newFilters.key_mode);
    if (newFilters.tags?.length) params.set('tags', newFilters.tags.join(','));

    window.history.pushState({}, '', `?${params.toString()}`);
  };

  return (
    <div className="w-80">
      <FilterPanel filters={filters} onChange={handleFilterChange} />
    </div>
  );
}

/**
 * Example 6: Responsive Mobile Sheet
 *
 * Use shadcn/ui Sheet for mobile filter panel
 */
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { SlidersHorizontal } from 'lucide-react';

export function MobileSheetExample() {
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });
  const [open, setOpen] = useState(false);

  const handleFilterChange = (newFilters: SampleFilters) => {
    setFilters(newFilters);
    // Optionally close sheet after applying
    // setOpen(false);
  };

  return (
    <>
      {/* Desktop: Sidebar */}
      <aside className="hidden md:block w-80">
        <FilterPanel filters={filters} onChange={handleFilterChange} />
      </aside>

      {/* Mobile: Sheet */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button variant="outline" size="sm" className="md:hidden">
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            Filters
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80 overflow-y-auto">
          <FilterPanel
            filters={filters}
            onChange={handleFilterChange}
            className="mt-6"
          />
        </SheetContent>
      </Sheet>
    </>
  );
}

/**
 * TypeScript Usage Tips:
 *
 * 1. The SampleFilters interface is exported, use it for type safety:
 *    import { SampleFilters } from '@/components/samples';
 *
 * 2. All filter properties are optional - handle undefined values:
 *    if (filters.genres?.length > 0) { ... }
 *
 * 3. BPM defaults to 60-180 if not specified
 *
 * 4. Genres and tags are arrays - check length before using
 *
 * 5. Key mode only appears if a key is selected
 */
