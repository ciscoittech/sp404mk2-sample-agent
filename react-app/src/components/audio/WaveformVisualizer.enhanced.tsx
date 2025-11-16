import { useRef, useEffect, memo } from 'react';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { AudioControls } from './AudioControls';
import { Loader2 } from 'lucide-react';

interface WaveformVisualizerProps {
  audioUrl: string;
  height?: number;
  showControls?: boolean;
  compact?: boolean;
  autoPlay?: boolean;
  onReady?: () => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  onError?: (error: Error) => void;
}

function WaveformVisualizerComponent({
  audioUrl,
  height = 128,
  showControls = true,
  compact = false,
  autoPlay = false,
  onReady,
  onPlay,
  onPause,
  onFinish,
  onError,
}: WaveformVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const [state, controls] = useAudioPlayer({
    audioUrl,
    containerRef,
    height,
    waveColor: 'rgb(100, 116, 139)',
    progressColor: 'rgb(31, 199, 255)',
    cursorColor: 'rgb(21, 184, 87)',
    onReady: () => {
      if (autoPlay) {
        controls.play();
      }
      onReady?.();
    },
    onPlay,
    onPause,
    onFinish,
    onError,
  });

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle if the wrapper is in focus or contains the active element
      if (!wrapperRef.current?.contains(document.activeElement)) {
        return;
      }

      switch (e.key) {
        case ' ':
          e.preventDefault();
          controls.togglePlay();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          controls.skip(-5);
          break;
        case 'ArrowRight':
          e.preventDefault();
          controls.skip(5);
          break;
        case 'ArrowUp':
          e.preventDefault();
          controls.setVolume(Math.min(1, state.volume + 0.1));
          break;
        case 'ArrowDown':
          e.preventDefault();
          controls.setVolume(Math.max(0, state.volume - 0.1));
          break;
        case 'm':
        case 'M':
          e.preventDefault();
          controls.setVolume(state.volume === 0 ? 1 : 0);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [controls, state.volume]);

  return (
    <div
      ref={wrapperRef}
      tabIndex={0}
      className="focus:outline-none focus:ring-2 focus:ring-primary/50 rounded-lg"
      role="region"
      aria-label="Audio player"
    >
      {state.isLoading && (
        <div className="flex items-center justify-center bg-secondary/50 rounded-md" style={{ height }}>
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}

      <div
        ref={containerRef}
        className={`rounded-md overflow-hidden bg-secondary/50 ${state.isLoading ? 'hidden' : ''}`}
        style={{ height }}
      />

      {showControls && !state.isLoading && (
        <div className="mt-3">
          <AudioControls
            state={state}
            controls={controls}
            compact={compact}
            showVolume={!compact}
            showSpeed={!compact}
            showSkip={!compact}
          />
        </div>
      )}
    </div>
  );
}

export const WaveformVisualizer = memo(WaveformVisualizerComponent);
