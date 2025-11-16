import { SampleGrid } from '@/components/samples/SampleGrid';
import { FilterPanel } from '@/components/samples/FilterPanel';
import { PinnedSamplesSection } from '@/components/samples/PinnedSamplesSection';
import type { SampleFilters } from '@/components/samples/FilterPanel';
import { useSamples } from '@/hooks/useSamples';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Loader2, Upload } from 'lucide-react';
import { useState, useMemo } from 'react';
import type { Sample } from '@/types/api';

export function SamplesPage() {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<SampleFilters>({
    bpm_min: 60,
    bpm_max: 180,
  });
  const [showOnlyRecommended, setShowOnlyRecommended] = useState(false);
  const [recommendedSamples, setRecommendedSamples] = useState<Sample[]>([]);

  // Calculate active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.genres && filters.genres.length > 0) count += filters.genres.length;
    if (filters.bpm_min !== 60 || filters.bpm_max !== 180) count += 1;
    if (filters.key) count += 1;
    if (filters.tags && filters.tags.length > 0) count += filters.tags.length;
    return count;
  }, [filters]);

  // Build query params from filters
  const queryParams = useMemo(() => {
    return {
      search: search || undefined,
      genre: filters.genres?.[0], // API accepts single genre
      bpm_min: filters.bpm_min,
      bpm_max: filters.bpm_max,
      key: filters.key,
      tags: filters.tags,
      limit: 50,
    };
  }, [search, filters]);

  const { data, isLoading, error } = useSamples(queryParams);

  const handlePlay = (sample: Sample) => {
    console.log('Play sample:', sample.title);
    // TODO: Implement audio player
  };

  const handleAddToKit = (sample: Sample) => {
    console.log('Add to kit:', sample.title);
    // TODO: Implement add to kit
  };

  const handleClearFilters = () => {
    setFilters({
      bpm_min: 60,
      bpm_max: 180,
    });
  };

  const handleShowRecommended = (samples: Sample[]) => {
    setRecommendedSamples(samples);
    setShowOnlyRecommended(true);
  };

  // Determine which samples to display
  const samplesToDisplay = useMemo(() => {
    if (showOnlyRecommended && recommendedSamples.length > 0) {
      return recommendedSamples;
    }
    return data?.items || [];
  }, [showOnlyRecommended, recommendedSamples, data]);

  return (
    <div className="container mx-auto px-4 py-6 max-w-[1800px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold">Sample Library</h2>
          <p className="text-muted-foreground mt-2">
            {data?.total ? `${data.total} samples available` : 'Browse your audio samples'}
          </p>
        </div>
        <Button className="gap-2">
          <Upload className="h-4 w-4" />
          Upload Samples
        </Button>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
        {/* Left Sidebar - Filters */}
        <aside className="space-y-4">
          <FilterPanel
            filters={filters}
            onChange={setFilters}
            className="sticky top-4"
          />
        </aside>

        {/* Right Content - Search and Samples */}
        <main className="space-y-4">
          {/* Search Bar */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search samples..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            {activeFilterCount > 0 && (
              <Button
                variant="outline"
                onClick={handleClearFilters}
                className="gap-2"
              >
                Clear Filters
                <Badge variant="secondary" className="ml-1">
                  {activeFilterCount}
                </Badge>
              </Button>
            )}
          </div>

          {/* Pinned Samples Section */}
          <PinnedSamplesSection
            allSamples={data?.items || []}
            onRecommendedSamplesFilter={handleShowRecommended}
          />

          {/* Show recommended filter badge */}
          {showOnlyRecommended && (
            <div className="flex items-center gap-2">
              <Badge variant="default" className="gap-2">
                Showing {recommendedSamples.length} recommended samples
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowOnlyRecommended(false)}
              >
                Show All
              </Button>
            </div>
          )}

          {/* Content States */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
              <p className="text-sm text-destructive">
                Error loading samples: {error.message}
              </p>
            </div>
          )}

          {data && !isLoading && samplesToDisplay.length === 0 && (
            <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-12 text-center">
              <p className="text-muted-foreground">
                {activeFilterCount > 0 || search || showOnlyRecommended
                  ? 'No samples found matching your filters'
                  : 'No samples available. Upload some to get started!'}
              </p>
            </div>
          )}

          {data && !isLoading && samplesToDisplay.length > 0 && (
            <SampleGrid
              samples={samplesToDisplay}
              onPlay={handlePlay}
              onAddToKit={handleAddToKit}
            />
          )}
        </main>
      </div>
    </div>
  );
}
