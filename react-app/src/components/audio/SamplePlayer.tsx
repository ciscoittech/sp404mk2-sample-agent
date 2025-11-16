import { memo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { WaveformVisualizer } from './WaveformVisualizer.enhanced';
import type { Sample } from '@/types/api';

interface SamplePlayerProps {
  sample: Sample;
  autoPlay?: boolean;
  showMetadata?: boolean;
  compact?: boolean;
  onReady?: () => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
}

function SamplePlayerComponent({
  sample,
  autoPlay = false,
  showMetadata = true,
  compact = false,
  onReady,
  onPlay,
  onPause,
  onFinish,
}: SamplePlayerProps) {
  if (compact) {
    return (
      <div className="space-y-2">
        <WaveformVisualizer
          audioUrl={sample.file_url}
          height={64}
          showControls={true}
          compact={true}
          autoPlay={autoPlay}
          onReady={onReady}
          onPlay={onPlay}
          onPause={onPause}
          onFinish={onFinish}
        />
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{sample.title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <WaveformVisualizer
          audioUrl={sample.file_url}
          height={128}
          showControls={true}
          compact={false}
          autoPlay={autoPlay}
          onReady={onReady}
          onPlay={onPlay}
          onPause={onPause}
          onFinish={onFinish}
        />

        {showMetadata && (
          <div className="space-y-3">
            {/* Audio features */}
            <div className="flex items-center gap-2 text-xs flex-wrap">
              {sample.bpm && (
                <Badge variant="secondary" className="font-mono">
                  {Math.round(sample.bpm)} BPM
                </Badge>
              )}
              {sample.musical_key && (
                <Badge variant="secondary" className="font-mono">
                  {sample.musical_key}
                </Badge>
              )}
              {sample.genre && <Badge variant="outline">{sample.genre}</Badge>}
              {sample.duration && (
                <Badge variant="outline" className="font-mono">
                  {formatDuration(sample.duration)}
                </Badge>
              )}
            </div>

            {/* Tags */}
            {sample.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {sample.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export const SamplePlayer = memo(SamplePlayerComponent);
