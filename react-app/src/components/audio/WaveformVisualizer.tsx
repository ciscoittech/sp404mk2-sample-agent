import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, ZoomIn, ZoomOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';

interface WaveformVisualizerProps {
  audioUrl: string;
  height?: number;
  showControls?: boolean;
}

export function WaveformVisualizer({ audioUrl, height = 128, showControls = true }: WaveformVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (!containerRef.current) return;

    let wavesurfer: WaveSurfer | null = null;

    try {
      wavesurfer = WaveSurfer.create({
        container: containerRef.current,
        waveColor: 'rgb(100, 116, 139)',
        progressColor: 'rgb(31, 199, 255)',
        cursorColor: 'rgb(21, 184, 87)',
        barWidth: 2,
        barRadius: 3,
        height,
        normalize: true,
      });

      wavesurfer.load(audioUrl);

      wavesurfer.on('ready', () => {
        setDuration(wavesurfer!.getDuration());
      });

      wavesurfer.on('audioprocess', () => {
        setCurrentTime(wavesurfer!.getCurrentTime());
      });

      wavesurfer.on('play', () => setIsPlaying(true));
      wavesurfer.on('pause', () => setIsPlaying(false));

      // Handle errors but don't throw - AbortErrors are expected when components unmount
      wavesurfer.on('error', (error) => {
        if (error.name !== 'AbortError') {
          console.error('WaveSurfer error:', error);
        }
      });

      wavesurferRef.current = wavesurfer;
    } catch (error) {
      console.error('Failed to create WaveSurfer:', error);
      throw error; // Re-throw to trigger ErrorBoundary
    }

    return () => {
      if (wavesurfer) {
        try {
          wavesurfer.destroy();
        } catch (error) {
          // Ignore AbortErrors during cleanup - they're expected when component unmounts during loading
          if (error instanceof Error && error.name !== 'AbortError') {
            console.error('Error destroying WaveSurfer:', error);
          }
        }
      }
    };
  }, [audioUrl, height]);

  useEffect(() => {
    // Only zoom if audio is loaded (duration > 0)
    if (wavesurferRef.current && duration > 0) {
      wavesurferRef.current.zoom(zoom);
    }
  }, [zoom, duration]);

  const togglePlay = () => {
    wavesurferRef.current?.playPause();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isReady = duration > 0;

  return (
    <div className={showControls ? "space-y-4" : ""}>
      <div
        ref={containerRef}
        className="rounded-lg overflow-hidden bg-secondary cursor-pointer hover:bg-secondary/80 transition-colors"
        onClick={() => !showControls && togglePlay()}
        title={!showControls ? (isPlaying ? "Pause" : "Play") : undefined}
      />

      {showControls && (
        <>
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={togglePlay}
              disabled={!isReady}
            >
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>

            <div className="flex-1">
              <div className="text-xs text-muted-foreground">
                {formatTime(currentTime)} / {formatTime(duration)}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setZoom(Math.max(1, zoom - 10))}
              >
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setZoom(Math.min(100, zoom + 10))}
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <Slider
            value={[currentTime]}
            max={duration}
            step={0.1}
            onValueChange={([value]) => {
              wavesurferRef.current?.seekTo(value / duration);
            }}
            className="w-full"
          />
        </>
      )}
    </div>
  );
}
