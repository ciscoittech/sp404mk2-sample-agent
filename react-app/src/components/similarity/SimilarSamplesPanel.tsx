import { memo } from 'react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Loader2, Music2, TrendingUp } from 'lucide-react';
import { SimilarSampleResult } from './SimilarSampleResult';
import { useSimilarSamples } from '@/hooks/useSimilarity';

interface SimilarSamplesPanelProps {
  isOpen: boolean;
  onClose: () => void;
  sampleId: number | null;
  onSelect?: (sampleId: number) => void;
}

function SimilarSamplesPanelComponent({
  isOpen,
  onClose,
  sampleId,
  onSelect,
}: SimilarSamplesPanelProps) {
  const { data: similarSamples, isLoading, error } = useSimilarSamples(sampleId, { limit: 10 });

  const handleSelectSample = (sampleId: number) => {
    onSelect?.(sampleId);
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Similar Samples
          </SheetTitle>
          <SheetDescription>
            Samples with similar audio features and characteristics
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 h-[calc(100vh-120px)]">
          {/* Loading state */}
          {isLoading && (
            <div className="space-y-3">
              <div className="flex items-center justify-center py-12">
                <div className="text-center space-y-3">
                  <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
                  <p className="text-sm text-muted-foreground">Finding similar samples...</p>
                </div>
              </div>

              {/* Skeleton cards */}
              {Array.from({ length: 5 }).map((_, i) => (
                <div
                  key={i}
                  className="border rounded-lg p-3 space-y-3 animate-pulse"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-6 bg-secondary rounded" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-secondary rounded w-3/4" />
                      <div className="h-3 bg-secondary rounded w-1/2" />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <div className="h-5 bg-secondary rounded w-16" />
                    <div className="h-5 bg-secondary rounded w-12" />
                    <div className="h-5 bg-secondary rounded w-20" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-3">
                <Music2 className="h-12 w-12 text-muted-foreground/50 mx-auto" />
                <div>
                  <p className="font-medium">Failed to load similar samples</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {error instanceof Error ? error.message : 'Unknown error'}
                  </p>
                </div>
                <Button variant="outline" onClick={() => window.location.reload()}>
                  Try Again
                </Button>
              </div>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && (!similarSamples || similarSamples.length === 0) && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-3">
                <Music2 className="h-12 w-12 text-muted-foreground/50 mx-auto" />
                <div>
                  <p className="font-medium">No similar samples found</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Try analyzing more samples or adjusting your filters
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {!isLoading && !error && similarSamples && similarSamples.length > 0 && (
            <ScrollArea className="h-full pr-4">
              <div className="space-y-3">
                {/* Results count */}
                <div className="text-sm text-muted-foreground">
                  Found {similarSamples.length} similar sample{similarSamples.length !== 1 ? 's' : ''}
                </div>

                {/* Results list */}
                {similarSamples.map((result) => (
                  <SimilarSampleResult
                    key={result.id}
                    result={result}
                    onSelect={handleSelectSample}
                  />
                ))}

                {/* Load more hint */}
                {similarSamples.length >= 10 && (
                  <div className="text-center py-4">
                    <p className="text-xs text-muted-foreground">
                      Showing top 10 matches
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

export const SimilarSamplesPanel = memo(SimilarSamplesPanelComponent);
