import { memo } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Gauge } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import type { AudioPlayerState, AudioPlayerControls } from '@/hooks/useAudioPlayer';

interface AudioControlsProps {
  state: AudioPlayerState;
  controls: AudioPlayerControls;
  compact?: boolean;
  showVolume?: boolean;
  showSpeed?: boolean;
  showSkip?: boolean;
}

function AudioControlsComponent({
  state,
  controls,
  compact = false,
  showVolume = true,
  showSpeed = true,
  showSkip = true,
}: AudioControlsProps) {
  const formatTime = (seconds: number) => {
    if (!isFinite(seconds)) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isMuted = state.volume === 0;

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={controls.togglePlay}
          disabled={state.isLoading}
        >
          {state.isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
        </Button>
        <div className="text-xs text-muted-foreground font-mono">
          {formatTime(state.currentTime)} / {formatTime(state.duration)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Main controls */}
      <div className="flex items-center gap-2">
        {/* Skip backward */}
        {showSkip && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => controls.skip(-5)}
                  disabled={state.isLoading}
                >
                  <SkipBack className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Skip backward 5s</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}

        {/* Play/Pause */}
        <Button
          variant="default"
          size="icon"
          className="h-10 w-10"
          onClick={controls.togglePlay}
          disabled={state.isLoading}
        >
          {state.isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
        </Button>

        {/* Skip forward */}
        {showSkip && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => controls.skip(5)}
                  disabled={state.isLoading}
                >
                  <SkipForward className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Skip forward 5s</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}

        {/* Time display */}
        <div className="flex-1 text-sm text-muted-foreground font-mono">
          {formatTime(state.currentTime)} / {formatTime(state.duration)}
        </div>

        {/* Volume control */}
        {showVolume && (
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => controls.setVolume(isMuted ? 1 : 0)}
            >
              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </Button>
            <Slider
              value={[state.volume * 100]}
              max={100}
              step={1}
              onValueChange={([value]) => controls.setVolume(value / 100)}
              className="w-24"
            />
          </div>
        )}

        {/* Playback speed */}
        {showSpeed && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 gap-1 px-2"
                  onClick={() => {
                    const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];
                    const currentIndex = speeds.indexOf(state.playbackRate);
                    const nextIndex = (currentIndex + 1) % speeds.length;
                    controls.setPlaybackRate(speeds[nextIndex]);
                  }}
                >
                  <Gauge className="h-3 w-3" />
                  <span className="text-xs font-mono">{state.playbackRate}x</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Playback speed: {state.playbackRate}x</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>

      {/* Progress bar */}
      <Slider
        value={[state.currentTime]}
        max={state.duration || 100}
        step={0.1}
        onValueChange={([value]) => controls.seek(value)}
        className="w-full"
        disabled={state.isLoading}
      />

      {/* Error display */}
      {state.error && (
        <div className="text-xs text-destructive bg-destructive/10 px-2 py-1 rounded">
          {state.error}
        </div>
      )}
    </div>
  );
}

export const AudioControls = memo(AudioControlsComponent);
