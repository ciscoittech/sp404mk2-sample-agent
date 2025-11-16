# Audio Player Quick Start Guide

Get up and running with the audio player in 5 minutes.

## 1. Test the Player

Start the dev server:
```bash
cd react-app
npm run dev
```

Visit: **http://localhost:5173/test/audio**

This opens the comprehensive test page with:
- Full sample player
- Compact player
- Waveform visualizer
- Keyboard shortcuts reference
- Testing checklist

## 2. Use in Your Component

### Simple Waveform
```tsx
import { WaveformVisualizer } from '@/components/audio';

<WaveformVisualizer
  audioUrl="http://localhost:8100/api/v1/public/samples/1/download"
  height={128}
  showControls={true}
/>
```

### Complete Sample Player
```tsx
import { SamplePlayer } from '@/components/audio/SamplePlayer';

<SamplePlayer
  sample={sample}
  showMetadata={true}
  onPlay={() => console.log('Playing')}
/>
```

### Compact for Grids
```tsx
<WaveformVisualizer
  audioUrl={sample.file_url}
  height={64}
  showControls={false}
/>
```

## 3. Keyboard Shortcuts

Focus the player and use:
- **Space** - Play/Pause
- **← →** - Skip 5 seconds
- **↑ ↓** - Volume control
- **M** - Mute/Unmute

## 4. Custom Player

```tsx
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { AudioControls } from '@/components/audio';

function MyPlayer({ audioUrl }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [state, controls] = useAudioPlayer({
    audioUrl,
    containerRef,
    height: 128,
    onReady: () => console.log('Ready to play'),
  });

  return (
    <div>
      <div ref={containerRef} />
      <AudioControls state={state} controls={controls} />
    </div>
  );
}
```

## 5. Sample Data Structure

Your samples need:
```typescript
{
  id: number;
  title: string;
  file_url: string;  // Important: URL to audio file
  duration?: number;
  bpm?: number;
  musical_key?: string;
  genre?: string;
  tags: string[];
}
```

## 6. Integration with SampleCard

Already integrated! The existing SampleCard lazy-loads waveforms:

```tsx
import { SampleCard } from '@/components/samples/SampleCard';

<SampleCard
  sample={sample}
  onPlay={(s) => handlePlay(s)}
  onAddToKit={(s) => handleAddToKit(s)}
/>
```

## 7. Next Steps

- ✅ Test on `/test/audio` page
- ✅ Verify backend API serves audio files
- ✅ Check keyboard shortcuts work
- ✅ Test on mobile/tablet
- ✅ Integrate with kit builder

## 8. Common Issues

### Audio doesn't load
Check that `sample.file_url` is correct:
```
http://localhost:8100/api/v1/public/samples/{id}/download
```

### Keyboard shortcuts don't work
Click the player to focus it first.

### Memory leaks
All components auto-cleanup. But if you see issues:
```tsx
// WaveSurfer is automatically destroyed on unmount
useEffect(() => {
  return () => {
    // Cleanup happens here automatically
  };
}, []);
```

## 9. Performance Tips

**For grids with many samples**:
```tsx
// Use intersection observer (already in SampleCard)
const [isInView, setIsInView] = useState(false);

// Only load waveform when visible
{isInView && <WaveformVisualizer audioUrl={url} />}
```

**For better initial load**:
```tsx
// Disable controls for faster render
<WaveformVisualizer showControls={false} height={64} />
```

## 10. Full Documentation

For complete API reference, see:
- **AUDIO_PLAYER_README.md** - Full documentation
- **AUDIO_PLAYER_IMPLEMENTATION.md** - Technical details

---

**That's it!** You now have a production-ready audio player with waveform visualization.

Happy coding! 🎵
