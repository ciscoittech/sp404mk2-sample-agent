import { useState } from 'react';
import { ChevronDown, Play, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useRecommendations } from '@/hooks/useKits';
import type { Sample } from '@/types/api';

interface RecommendationDropdownProps {
  kitId: number;
  padNumber: number;
  onSelectSample: (sample: Sample) => void;
  onClose: () => void;
}

export function RecommendationDropdown({
  kitId,
  padNumber,
  onSelectSample,
  onClose,
}: RecommendationDropdownProps) {
  const { data: recommendations, isLoading, error } = useRecommendations(kitId, padNumber);
  const [previewingId, setPreviewingId] = useState<number | null>(null);

  if (error) {
    return (
      <div className="absolute top-full left-0 right-0 mt-2 bg-destructive/10 border border-destructive rounded-lg p-3 z-50">
        <p className="text-sm text-destructive">Failed to load recommendations</p>
        <Button variant="ghost" size="sm" onClick={onClose} className="mt-2">
          Close
        </Button>
      </div>
    );
  }

  return (
    <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
      <div className="sticky top-0 bg-card border-b border-border p-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Recommended Samples</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-6 w-6"
          >
            <ChevronDown className="h-4 w-4 rotate-180" />
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="p-4 text-center text-muted-foreground">
          Loading recommendations...
        </div>
      ) : recommendations && recommendations.length > 0 ? (
        <div className="divide-y divide-border">
          {recommendations.map((sample: Sample) => (
            <div key={sample.id} className="p-3 hover:bg-accent/50 transition-colors">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{sample.title}</p>
                  <div className="flex gap-2 flex-wrap mt-1">
                    {sample.bpm && (
                      <Badge variant="secondary" className="text-xs font-mono">
                        {Math.round(sample.bpm)} BPM
                      </Badge>
                    )}
                    {sample.musical_key && (
                      <Badge variant="secondary" className="text-xs">
                        {sample.musical_key}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => {
                    if (previewingId === sample.id) {
                      setPreviewingId(null);
                    } else {
                      setPreviewingId(sample.id);
                      // In real implementation, would trigger audio preview
                      // audioContext.stopAllExcept(playerId);
                    }
                  }}
                >
                  <Play className="h-3 w-3 mr-1" />
                  {previewingId === sample.id ? 'Stop' : 'Preview'}
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  className="flex-1"
                  onClick={() => {
                    onSelectSample(sample);
                    onClose();
                  }}
                >
                  <Plus className="h-3 w-3 mr-1" />
                  Add
                </Button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-center text-muted-foreground text-sm">
          No recommendations found
        </div>
      )}
    </div>
  );
}
