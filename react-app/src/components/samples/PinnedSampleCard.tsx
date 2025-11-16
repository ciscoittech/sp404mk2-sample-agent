import { memo, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Play, Pause, X, Pin } from 'lucide-react';
import { WaveformVisualizer } from '@/components/audio/WaveformVisualizer';
import { ErrorBoundary } from '@/components/shared/ErrorBoundary';
import type { Sample } from '@/types/api';
import { usePinnedSamples } from '@/stores/pinnedSamplesStore';

interface PinnedSampleCardProps {
  sample: Sample;
}

const formatDuration = (seconds?: number) => {
  if (!seconds) return '--:--';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const PinnedSampleCard = memo(({ sample }: PinnedSampleCardProps) => {
  const { unpinSample } = usePinnedSamples();
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <Card className="group border-primary/30 bg-card/80 backdrop-blur-sm">
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header with title and controls */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <Pin className="h-3 w-3 text-primary flex-shrink-0" />
                <h4 className="text-sm font-medium truncate">{sample.title}</h4>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                {formatDuration(sample.duration)}
              </p>
            </div>

            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 flex-shrink-0"
              onClick={() => unpinSample(sample.id)}
              title="Unpin sample"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Waveform */}
          <div className="h-12">
            <ErrorBoundary fallback={
              <div className="h-12 bg-secondary/50 rounded-md flex items-center justify-center">
                <p className="text-xs text-muted-foreground">Unable to load</p>
              </div>
            }>
              <WaveformVisualizer
                audioUrl={sample.file_url!}
                height={48}
                showControls={false}
              />
            </ErrorBoundary>
          </div>

          {/* Metadata badges */}
          <div className="flex flex-wrap items-center gap-2">
            {sample.bpm && (
              <Badge variant="secondary" className="text-xs">
                {Math.round(sample.bpm)} BPM
              </Badge>
            )}
            {sample.musical_key && (
              <Badge variant="secondary" className="text-xs">
                {sample.musical_key}
              </Badge>
            )}
            {sample.genre && (
              <Badge variant="outline" className="text-xs">
                {sample.genre}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

PinnedSampleCard.displayName = 'PinnedSampleCard';
