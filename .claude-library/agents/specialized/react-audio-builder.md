# React Audio Player Builder Agent

**Purpose**: Build professional audio player with waveform visualization using wavesurfer.js
**Expertise**: Web Audio API, wavesurfer.js, React hooks, audio playback, waveform rendering
**When to Use**: Implementing audio playback features, waveform visualizations
**Output**: Complete audio player component with controls and visualization

---

## What This Agent Does

This agent builds a production-quality audio player by:

1. **Integrating wavesurfer.js** - Set up waveform visualization library
2. **Creating Audio Components** - WaveformVisualizer, AudioControls, Player
3. **Implementing Playback** - Play, pause, seek, volume, speed controls
4. **Managing State** - Audio context, current track, playback position
5. **Optimizing Performance** - Lazy loading, caching, Web Workers
6. **Adding Keyboard Shortcuts** - Space, arrows, volume controls

---

## When to Activate

**Use this agent when**:
- Building audio playback features
- Integrating wavesurfer.js
- Creating waveform visualizations
- Implementing audio player controls
- Need professional music production UI

**Success Criteria**:
- ✅ Audio files play smoothly
- ✅ Waveform renders accurately
- ✅ Controls are responsive (<100ms)
- ✅ Keyboard shortcuts work
- ✅ Volume and speed controls functional
- ✅ Works across browsers (Chrome, Firefox, Safari)

---

## Agent Workflow

### Phase 1: Install Dependencies (5 min)
```bash
cd react-app
npm install wavesurfer.js@7
npm install @types/wavesurfer.js -D
```

### Phase 2: Create Waveform Component (30 min)
```typescript
// src/components/audio/WaveformVisualizer.tsx
import { useEffect, useRef } from 'react';
import WaveSurfer from 'wavesurfer.js';

interface WaveformVisualizerProps {
  audioUrl: string;
  onReady?: (duration: number) => void;
  onTimeUpdate?: (currentTime: number) => void;
  onFinish?: () => void;
}

export function WaveformVisualizer({
  audioUrl,
  onReady,
  onTimeUpdate,
  onFinish,
}: WaveformVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Create WaveSurfer instance
    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: 'hsl(var(--muted-foreground))',
      progressColor: 'hsl(var(--primary))',
      cursorColor: 'hsl(var(--accent))',
      height: 120,
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      responsive: true,
      normalize: true,
    });

    // Event listeners
    ws.on('ready', () => {
      onReady?.(ws.getDuration());
    });

    ws.on('audioprocess', () => {
      onTimeUpdate?.(ws.getCurrentTime());
    });

    ws.on('finish', () => {
      onFinish?.();
    });

    // Load audio
    ws.load(audioUrl);

    wavesurferRef.current = ws;

    // Cleanup
    return () => {
      ws.destroy();
    };
  }, [audioUrl]);

  return (
    <div className="relative w-full">
      <div ref={containerRef} className="w-full" />
    </div>
  );
}
```

### Phase 3: Create Audio Controls (30 min)
```typescript
// src/components/audio/AudioControls.tsx
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';
import { useState } from 'react';

interface AudioControlsProps {
  isPlaying: boolean;
  volume: number;
  playbackRate: number;
  onPlayPause: () => void;
  onVolumeChange: (volume: number) => void;
  onPlaybackRateChange: (rate: number) => void;
}

export function AudioControls({
  isPlaying,
  volume,
  playbackRate,
  onPlayPause,
  onVolumeChange,
  onPlaybackRateChange,
}: AudioControlsProps) {
  const [isMuted, setIsMuted] = useState(false);

  const handleMuteToggle = () => {
    if (isMuted) {
      onVolumeChange(0.7);
      setIsMuted(false);
    } else {
      onVolumeChange(0);
      setIsMuted(true);
    }
  };

  return (
    <div className="flex items-center gap-4">
      {/* Play/Pause */}
      <Button
        size="icon"
        variant="ghost"
        onClick={onPlayPause}
        aria-label={isPlaying ? 'Pause' : 'Play'}
      >
        {isPlaying ? (
          <Pause className="h-5 w-5" />
        ) : (
          <Play className="h-5 w-5" />
        )}
      </Button>

      {/* Volume */}
      <div className="flex items-center gap-2 min-w-[120px]">
        <Button
          size="icon"
          variant="ghost"
          onClick={handleMuteToggle}
          aria-label={isMuted ? 'Unmute' : 'Mute'}
        >
          {isMuted || volume === 0 ? (
            <VolumeX className="h-4 w-4" />
          ) : (
            <Volume2 className="h-4 w-4" />
          )}
        </Button>
        <Slider
          value={[volume * 100]}
          onValueChange={([v]) => onVolumeChange(v / 100)}
          max={100}
          step={1}
          className="w-20"
        />
      </div>

      {/* Playback Speed */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Speed:</span>
        <select
          value={playbackRate}
          onChange={(e) => onPlaybackRateChange(parseFloat(e.target.value))}
          className="text-sm bg-background border border-input rounded px-2 py-1"
        >
          <option value="0.5">0.5x</option>
          <option value="0.75">0.75x</option>
          <option value="1">1x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2x</option>
        </select>
      </div>
    </div>
  );
}
```

### Phase 4: Create Audio Player Hook (30 min)
```typescript
// src/hooks/useAudioPlayer.ts
import { useState, useRef, useCallback } from 'react';
import WaveSurfer from 'wavesurfer.js';

export function useAudioPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.7);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const wavesurferRef = useRef<WaveSurfer | null>(null);

  const handlePlayPause = useCallback(() => {
    if (!wavesurferRef.current) return;

    if (isPlaying) {
      wavesurferRef.current.pause();
    } else {
      wavesurferRef.current.play();
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleVolumeChange = useCallback((newVolume: number) => {
    if (!wavesurferRef.current) return;
    wavesurferRef.current.setVolume(newVolume);
    setVolume(newVolume);
  }, []);

  const handlePlaybackRateChange = useCallback((rate: number) => {
    if (!wavesurferRef.current) return;
    wavesurferRef.current.setPlaybackRate(rate);
    setPlaybackRate(rate);
  }, []);

  const handleSeek = useCallback((timeInSeconds: number) => {
    if (!wavesurferRef.current) return;
    wavesurferRef.current.seekTo(timeInSeconds / duration);
  }, [duration]);

  return {
    isPlaying,
    volume,
    playbackRate,
    currentTime,
    duration,
    wavesurferRef,
    handlePlayPause,
    handleVolumeChange,
    handlePlaybackRateChange,
    handleSeek,
    setCurrentTime,
    setDuration,
    setIsPlaying,
  };
}
```

### Phase 5: Integrate with Sample Card (20 min)
```typescript
// Update src/components/samples/SampleCard.tsx
import { WaveformVisualizer } from '@/components/audio/WaveformVisualizer';
import { AudioControls } from '@/components/audio/AudioControls';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';

export function SampleCard({ sample }: { sample: Sample }) {
  const {
    isPlaying,
    volume,
    playbackRate,
    currentTime,
    duration,
    wavesurferRef,
    handlePlayPause,
    handleVolumeChange,
    handlePlaybackRateChange,
    setCurrentTime,
    setDuration,
  } = useAudioPlayer();

  return (
    <Card>
      <CardHeader>
        <h3>{sample.title}</h3>
      </CardHeader>
      <CardContent>
        <WaveformVisualizer
          audioUrl={sample.file_url}
          onReady={setDuration}
          onTimeUpdate={setCurrentTime}
        />
        <AudioControls
          isPlaying={isPlaying}
          volume={volume}
          playbackRate={playbackRate}
          onPlayPause={handlePlayPause}
          onVolumeChange={handleVolumeChange}
          onPlaybackRateChange={handlePlaybackRateChange}
        />
        <div className="text-sm text-muted-foreground">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </CardContent>
    </Card>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

### Phase 6: Add Keyboard Shortcuts (15 min)
```typescript
// src/hooks/useAudioKeyboardShortcuts.ts
import { useEffect } from 'react';

export function useAudioKeyboardShortcuts(
  onPlayPause: () => void,
  onSeek: (delta: number) => void,
  onVolumeChange: (delta: number) => void
) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Space: Play/Pause
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        onPlayPause();
      }

      // Left Arrow: -5 seconds
      if (e.code === 'ArrowLeft') {
        e.preventDefault();
        onSeek(-5);
      }

      // Right Arrow: +5 seconds
      if (e.code === 'ArrowRight') {
        e.preventDefault();
        onSeek(5);
      }

      // Up Arrow: +10% volume
      if (e.code === 'ArrowUp') {
        e.preventDefault();
        onVolumeChange(0.1);
      }

      // Down Arrow: -10% volume
      if (e.code === 'ArrowDown') {
        e.preventDefault();
        onVolumeChange(-0.1);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onPlayPause, onSeek, onVolumeChange]);
}
```

---

## Testing Checklist

### Basic Playback
- [ ] Audio plays when clicking play button
- [ ] Audio pauses when clicking pause button
- [ ] Waveform renders correctly
- [ ] Progress cursor moves during playback

### Controls
- [ ] Volume slider adjusts volume (0-100%)
- [ ] Mute button toggles audio on/off
- [ ] Playback speed selector works (0.5x - 2x)
- [ ] Time display shows current/total time

### Waveform
- [ ] Waveform loads within 2 seconds
- [ ] Click on waveform seeks to position
- [ ] Progress color shows playback position
- [ ] Waveform is responsive (resizes with window)

### Keyboard Shortcuts
- [ ] Space bar toggles play/pause
- [ ] Left arrow seeks backward 5 seconds
- [ ] Right arrow seeks forward 5 seconds
- [ ] Up arrow increases volume
- [ ] Down arrow decreases volume

### Performance
- [ ] No lag when clicking controls
- [ ] Smooth waveform rendering (60fps)
- [ ] Audio doesn't stutter or skip
- [ ] CPU usage < 10% during playback

---

## Common Issues & Fixes

### Waveform Not Rendering
**Fix**: Ensure container has width
```css
.waveform-container {
  width: 100%;
  min-height: 120px;
}
```

### Audio CORS Errors
**Fix**: Ensure backend sends correct headers
```python
@app.get("/samples/{id}/download")
async def download_sample(id: int):
    return FileResponse(
        path,
        headers={"Access-Control-Allow-Origin": "*"}
    )
```

### Memory Leaks
**Fix**: Always destroy wavesurfer on unmount
```typescript
useEffect(() => {
  // ... create wavesurfer
  return () => {
    ws.destroy();
  };
}, [audioUrl]);
```

---

## Success Validation

**Audio Player Complete When**:
1. ✅ All audio samples play smoothly
2. ✅ Waveforms render accurately
3. ✅ All controls work as expected
4. ✅ Keyboard shortcuts functional
5. ✅ No performance issues
6. ✅ Works in Chrome, Firefox, Safari

---

**Agent Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: Ready for deployment
