import { memo, useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Play, Music, Plus, Search } from 'lucide-react';
import { ErrorBoundary } from '@/components/shared/ErrorBoundary';
import { PinButton } from './PinButton';
import { AddToCollectionMenu } from '@/components/collections/AddToCollectionMenu';
import { SimilarSamplesPanel } from '@/components/similarity';
import { useAudioPreview } from '@/hooks/useAudioPreview';
import type { Sample } from '@/types/api';

// Lazy load waveform component for better initial render performance
const WaveformVisualizer = memo(({ audioUrl, height, showControls }: {
  audioUrl: string;
  height?: number;
  showControls?: boolean;
}) => {
  const [Component, setComponent] = useState<any>(null);

  useEffect(() => {
    import('@/components/audio/WaveformVisualizer').then(mod => {
      setComponent(() => mod.WaveformVisualizer);
    });
  }, []);

  if (!Component) {
    return (
      <div className="h-16 bg-secondary/50 rounded-md flex items-center justify-center animate-pulse">
        <div className="flex gap-1">
          {Array.from({ length: 30 }).map((_, i) => (
            <div
              key={i}
              className="w-1 bg-muted-foreground/20 rounded-full"
              style={{ height: `${Math.random() * 40 + 20}px` }}
            />
          ))}
        </div>
      </div>
    );
  }

  return <Component audioUrl={audioUrl} height={height} showControls={showControls} />;
});

WaveformVisualizer.displayName = 'LazyWaveformVisualizer';

interface SampleCardProps {
  sample: Sample;
  onPlay?: (sample: Sample) => void;
  onAddToKit?: (sample: Sample) => void;
  draggable?: boolean;
}

function SampleCardComponent({ sample, onPlay, onAddToKit, draggable = false }: SampleCardProps) {
  const [isInView, setIsInView] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [similarPanelOpen, setSimilarPanelOpen] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const audioPreview = useAudioPreview(sample.file_url);

  const handleDragStart = (e: React.DragEvent) => {
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('application/json', JSON.stringify(sample));
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  // Intersection observer for lazy loading/unloading waveforms
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Load waveform when entering viewport (with 100px margin)
        // Unload waveform when leaving viewport to free audio resources
        setIsInView(entry.isIntersecting);
      },
      { rootMargin: '100px' }
    );

    if (cardRef.current) {
      observer.observe(cardRef.current);
    }

    return () => {
      observer.disconnect();
      // Ensure waveform is unloaded when component unmounts
      setIsInView(false);
    };
  }, []);

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card
      ref={cardRef}
      draggable={draggable}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      className={`
        group hover:border-primary/50 transition-all duration-200
        ${draggable ? 'cursor-grab active:cursor-grabbing' : ''}
        ${isDragging ? 'opacity-50 scale-95' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base truncate">{sample.title}</CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              {formatDuration(sample.duration)}
            </p>
          </div>
          <div className="flex items-center gap-1">
            <PinButton sample={sample} />
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => setSimilarPanelOpen(true)}
              title="Find similar samples"
            >
              <Search className="h-4 w-4" />
            </Button>
            <AddToCollectionMenu
              sampleId={sample.id}
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
            />
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => {
                audioPreview.play();
                onPlay?.(sample);
              }}
            >
              <Play className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Waveform with lazy loading and hover effect */}
        <div
          className={`
            h-16 rounded-md overflow-hidden bg-secondary/50
            transition-all duration-300
            ${isHovered ? 'shadow-[0_0_15px_rgba(31,199,255,0.3)] ring-1 ring-primary/30' : ''}
          `}
        >
          {isInView ? (
            <ErrorBoundary>
              <WaveformVisualizer
                audioUrl={sample.file_url}
                height={64}
                showControls={false}
              />
            </ErrorBoundary>
          ) : (
            <div className="h-full flex items-center justify-center">
              <Music className="h-6 w-6 text-muted-foreground" />
            </div>
          )}
        </div>

        {/* Audio features */}
        <div className="flex items-center gap-2 text-xs">
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
          {sample.genre && (
            <Badge variant="outline">{sample.genre}</Badge>
          )}
        </div>

        {/* Tags */}
        {sample.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {sample.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {sample.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{sample.tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Actions */}
        <Button
          variant="outline"
          size="sm"
          className="w-full"
          onClick={() => onAddToKit?.(sample)}
        >
          <Plus className="h-3 w-3 mr-1" />
          Add to Kit
        </Button>
      </CardContent>

      {/* Similar Samples Panel */}
      <SimilarSamplesPanel
        isOpen={similarPanelOpen}
        onClose={() => setSimilarPanelOpen(false)}
        sampleId={sample.id}
        onSelect={(sampleId) => {
          // Could potentially load the sample and call onPlay here
          console.log('Selected similar sample:', sampleId);
        }}
      />
    </Card>
  );
}

// Memoize to prevent unnecessary re-renders in sample grids
export const SampleCard = memo(SampleCardComponent);
