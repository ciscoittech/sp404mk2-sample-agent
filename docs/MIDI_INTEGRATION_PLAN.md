# MIDI Integration Plan

**Status:** Research Complete - Not Yet Implemented
**Feasibility:** ✅ EASY to MEDIUM
**Estimated Effort:** 1-2 days for MVP
**Last Updated:** 2025-11-17

---

## Executive Summary

MIDI pad triggering is **feasible and straightforward** to implement using existing open-source libraries. The Web MIDI API is mature and well-supported in Chrome/Edge browsers (70% market coverage). Integration maps cleanly to the existing kit system architecture.

**Key Benefits:**
- Physical MIDI controller triggers samples from kits
- Velocity-sensitive playback (hit harder = louder)
- Low latency (<10ms achievable)
- Zero additional backend infrastructure needed
- Works with existing React + FastAPI stack

**Key Limitations:**
- Safari/iOS not supported (30% of users)
- Requires HTTPS in production (localhost OK for dev)
- User must grant browser MIDI permission

---

## Browser Support

| Browser | Desktop | Mobile | Status |
|---------|---------|--------|--------|
| Chrome | ✅ v43+ | ⚠️ Android only | Production-ready |
| Edge | ✅ v79+ | ❌ | Chromium-based |
| Opera | ✅ v30+ | ⚠️ Limited | Chromium-based |
| Brave | ✅ Full | ❌ | Chromium-based |
| Firefox | ⚠️ Partial | ❌ | Experimental |
| Safari | ❌ | ❌ | **Not supported** |

**Recommendation:** Target Chrome/Edge desktop users. Show compatibility warning for Safari users.

---

## Recommended Technology Stack

### Primary Library: webmidi.js

**NPM:** `npm install webmidi`
**GitHub:** https://github.com/djipco/webmidi
**Docs:** https://webmidijs.org/
**Version:** 3.1.13+

**Why webmidi.js:**
- ✅ Actively maintained (2.3M+ downloads/month)
- ✅ TypeScript support built-in
- ✅ High-level API (abstracts MIDI complexity)
- ✅ Event-driven architecture (`noteon`, `noteoff`)
- ✅ Excellent documentation
- ✅ Works in browser AND Node.js

### Audio Playback Strategy

**Use Web Audio API** (not WaveSurfer.js) for MIDI-triggered samples:
- Low latency playback
- Velocity-sensitive volume control
- Multiple simultaneous samples
- Pre-loaded AudioBuffers for instant triggering

**Keep WaveSurfer.js** for:
- Sample browsing/preview UI
- Existing sample pages
- Waveform visualization

---

## MIDI Note Mapping

### Standard GM Drums (Channel 10)

**Note Range:** 36-51 (C2 to D#3)
**Velocity:** 0-127 (how hard pad is hit)

| MIDI Note | GM Drum | SP-404MK2 Pad | Kit Position |
|-----------|---------|---------------|--------------|
| 36 | Kick | Pad 1 | Bottom-left |
| 37 | Side Stick | Pad 2 | |
| 38 | Snare | Pad 3 | |
| 39 | Hand Clap | Pad 4 | |
| 40 | Electric Snare | Pad 5 | |
| 41 | Low Tom | Pad 6 | |
| 42 | Closed Hi-Hat | Pad 7 | |
| 43 | Low Tom | Pad 8 | |
| 44 | Pedal Hi-Hat | Pad 9 | |
| 45 | Mid Tom | Pad 10 | |
| 46 | Open Hi-Hat | Pad 11 | |
| 47 | Mid Tom | Pad 12 | |
| 48 | High Tom | Pad 13 | |
| 49 | Crash Cymbal | Pad 14 | |
| 50 | High Tom | Pad 15 | |
| 51 | Ride Cymbal | Pad 16 | Top-right |

### Compatible Controllers

**Akai MPD Series:**
- Default start note: 36 (C2)
- 16 velocity-sensitive pads
- USB MIDI class-compliant (no drivers)

**Novation Launchpad:**
- Configurable note mapping
- Can be set to drum mode (36-51)

**Roland SP-404MK2:**
- Note Range: 36-51
- MIDI Mode A: Bank-per-channel
- MIDI Mode B: Condensed
- **Must enable:** PAD Note Out = ON in settings

---

## Implementation Plan

### Phase 1: MIDI Foundation (4-6 hours)

**Goal:** Detect MIDI devices and log input

**Tasks:**
1. Install `webmidi` package
2. Create `MidiContext.tsx` (similar to AudioContext pattern)
3. Create `useMidi.ts` hook for device management
4. Add MIDI device selector to Settings page
5. Implement browser compatibility detection
6. Test: Log MIDI messages to console

**Files to Create:**
- `react-app/src/contexts/MidiContext.tsx`
- `react-app/src/hooks/useMidi.ts`
- `react-app/src/components/midi/MidiDeviceSelector.tsx`
- `react-app/src/components/midi/MidiStatusIndicator.tsx`

**Files to Modify:**
- `react-app/src/pages/SettingsPage.tsx`
- `react-app/src/main.tsx` (wrap with MidiProvider)
- `react-app/package.json`

**Deliverable:** MIDI messages logged when pads are hit

---

### Phase 2: Sample Triggering (4-6 hours)

**Goal:** MIDI notes trigger sample playback

**Tasks:**
1. Create `WebAudioSampler.ts` service
2. Preload samples into AudioBuffers
3. Create `useMidiPadTrigger.ts` hook
4. Map MIDI notes 36-51 to kit pads
5. Implement velocity-sensitive playback
6. Add visual feedback (highlight pads on hit)
7. Test with physical controller

**Files to Create:**
- `react-app/src/services/WebAudioSampler.ts`
- `react-app/src/hooks/useMidiPadTrigger.ts`
- `react-app/src/hooks/useMidiSampler.ts`

**Files to Modify:**
- `react-app/src/pages/KitsPage.tsx`
- `react-app/src/components/kits/PadGrid.tsx`

**Deliverable:** Physical MIDI controller triggers samples from active kit

---

### Phase 3: Polish & Edge Cases (2-3 hours)

**Goal:** Production-ready experience

**Tasks:**
1. HTTPS requirement detection
2. Permission denied error handling
3. AudioContext autoplay policy handling
4. Lazy loading for large kits
5. Memory management (buffer cleanup)
6. Connection status indicator
7. Documentation updates

**Files to Modify:**
- Error handling in all MIDI components
- Update `CLAUDE.md` with MIDI features
- Add user-facing docs

**Deliverable:** Polished MIDI integration ready for production

---

## Code Architecture

### Context Structure

```typescript
// MidiContext.tsx
interface MidiContextValue {
  isEnabled: boolean;
  inputs: Input[];
  selectedInput: Input | null;
  selectInput: (input: Input) => void;
  error: string | null;
}
```

### Hook Pattern

```typescript
// useMidiPadTrigger.ts
interface PadMapping {
  [midiNote: number]: {
    sampleId: string;
    sampleUrl: string;
  };
}

useMidiPadTrigger(
  midiInput: Input | null,
  padMapping: PadMapping,
  onTrigger: (sampleUrl: string, velocity: number) => void
)
```

### Integration with Existing Kit System

```typescript
// KitsPage.tsx
const padMapping = useMemo(() => {
  const mapping: PadMapping = {};
  kit?.pads.forEach((pad, index) => {
    const midiNote = 36 + index; // Notes 36-51
    mapping[midiNote] = {
      sampleId: pad.sample_id,
      sampleUrl: `/api/v1/samples/${pad.sample_id}/audio`
    };
  });
  return mapping;
}, [kit]);

useMidiPadTrigger(selectedInput, padMapping, handleSampleTrigger);
```

---

## Example Code Snippets

### Basic MIDI Setup

```typescript
// useMidi.ts
import { WebMidi, Input } from 'webmidi';

export function useMidi() {
  const [isEnabled, setIsEnabled] = useState(false);
  const [inputs, setInputs] = useState<Input[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    WebMidi.enable()
      .then(() => {
        setIsEnabled(true);
        setInputs(WebMidi.inputs);
      })
      .catch(err => setError(err.message));

    return () => {
      if (WebMidi.enabled) WebMidi.disable();
    };
  }, []);

  return { isEnabled, inputs, error };
}
```

### MIDI Sampler Hook

```typescript
// useMidiSampler.ts
export function useMidiSampler(
  midiInput: Input | null,
  samples: Map<number, Sample>
) {
  const audioContextRef = useRef<AudioContext>();

  // Initialize AudioContext
  useEffect(() => {
    audioContextRef.current = new AudioContext();
    return () => audioContextRef.current?.close();
  }, []);

  // Handle MIDI input
  useEffect(() => {
    if (!midiInput || !audioContextRef.current) return;

    const handleNoteOn = (e: InputEventNoteon) => {
      const note = e.note.number;
      const velocity = e.rawVelocity / 127;

      const sample = samples.get(note);
      if (!sample?.buffer) return;

      const source = audioContextRef.current!.createBufferSource();
      const gainNode = audioContextRef.current!.createGain();

      source.buffer = sample.buffer;
      gainNode.gain.value = velocity;

      source.connect(gainNode).connect(audioContextRef.current!.destination);
      source.start(0);
    };

    midiInput.addListener('noteon', handleNoteOn);
    return () => midiInput.removeListener('noteon', handleNoteOn);
  }, [midiInput, samples]);
}
```

### Browser Compatibility Check

```typescript
function checkMidiSupport() {
  if (!navigator.requestMIDIAccess) {
    return {
      supported: false,
      reason: 'Web MIDI API not available. Please use Chrome or Edge.'
    };
  }

  if (/Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent)) {
    return {
      supported: false,
      reason: 'Safari does not support Web MIDI. Please use Chrome or Edge.'
    };
  }

  return { supported: true };
}
```

---

## Performance Considerations

### Sample Loading Strategy

**Problem:** Loading 16 samples × 16 banks = 256 samples could cause memory issues

**Solution:** Lazy loading
```typescript
// Load samples on demand
useEffect(() => {
  if (activeKitId) {
    loadSamplesForKit(activeKitId);
  }
}, [activeKitId]);
```

### Latency Optimization

**Target:** <10ms latency (imperceptible to users)

**Techniques:**
1. Pre-decode all samples into AudioBuffers
2. Use Web Audio API (lower latency than HTML5 Audio)
3. Keep AudioContext running (avoid suspension)
4. Minimize processing chain (direct buffer → gain → destination)

### Memory Management

```typescript
// Clean up buffers when switching kits
useEffect(() => {
  return () => {
    buffers.forEach(buffer => {
      // AudioBuffers are garbage collected automatically
      // Just clear references
    });
    buffers.clear();
  };
}, [activeKitId]);
```

---

## Error Handling

### HTTPS Requirement

```typescript
if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
  showWarning('MIDI requires HTTPS. Please access via https://...');
}
```

### Permission Denied

```typescript
WebMidi.enable()
  .catch(err => {
    if (err.name === 'SecurityError') {
      showError('MIDI access denied. Please grant permission in browser settings.');
    }
  });
```

### AudioContext Autoplay Policy

```typescript
// Resume on first user interaction
if (audioContext.state === 'suspended') {
  audioContext.resume();
}
```

---

## Testing Strategy

### Manual Testing Checklist

**Phase 1:**
- [ ] MIDI device appears in Settings dropdown
- [ ] Device selection persists across page refreshes
- [ ] Console logs show note on/off messages
- [ ] Multiple devices can be detected

**Phase 2:**
- [ ] MIDI note triggers correct sample
- [ ] Velocity affects volume (soft/hard hits)
- [ ] Visual feedback shows pad activation
- [ ] No audio dropouts or glitches
- [ ] Multiple pads can play simultaneously

**Phase 3:**
- [ ] Safari users see compatibility warning
- [ ] HTTP users see HTTPS requirement warning
- [ ] Permission denied handled gracefully
- [ ] Large kits load without memory issues
- [ ] Tab switching doesn't break functionality

### Hardware Testing

**Required Equipment:**
- Akai MPD218/226/232 (or similar)
- Novation Launchpad (any model)
- Roland SP-404MK2 (if available)

**Test Scenarios:**
1. Single pad hits (verify correct sample)
2. Rapid pad hits (verify no audio glitches)
3. Velocity test (soft vs hard hits)
4. Multi-pad chords (verify polyphony)
5. Kit switching while playing

---

## Future Enhancements (Optional)

### Phase 4: Advanced Features

**MIDI Learn:**
- Click pad, hit MIDI note to assign
- Custom note mappings per kit

**Performance Recording:**
- Record MIDI input as performance
- Export to MIDI file
- Playback recorded performances

**Multi-Channel Support:**
- Different kits on different MIDI channels
- Bank switching via program change

**Velocity Curves:**
- Adjust velocity sensitivity
- Linear, logarithmic, exponential curves

**Latency Calibration:**
- Measure system latency
- Apply compensation offset

---

## Integration with Existing Features

### Leverage Current Architecture

**Kit System:**
- Already has pad → sample mapping
- Perfect structure for MIDI note mapping

**Audio Context:**
- Extend with MIDI context
- Parallel pattern: `<MidiProvider><AudioProvider>...</>`

**Sample API:**
- Fetch sample audio for buffering
- Reuse existing streaming endpoints

**Settings Page:**
- Add MIDI device selection
- MIDI preferences (latency, velocity)

### New Components Needed

1. **MidiProvider** (Context)
2. **MidiDeviceSelector** (UI component)
3. **MidiStatusIndicator** (Connection status)
4. **PadVisualizer** (Shows MIDI activity)
5. **WebAudioSampler** (Service layer)

---

## Cost Analysis

| Aspect | Cost | Notes |
|--------|------|-------|
| Development Time | 1-2 days | MVP implementation |
| Library License | $0 | webmidi.js is MIT licensed |
| Backend Changes | $0 | No backend changes needed |
| Infrastructure | $0 | Runs entirely in browser |
| Ongoing Maintenance | Low | Stable API, mature library |

**Total Cost:** Development time only (1-2 days)

---

## Success Criteria

### MVP Launch Criteria

✅ Physical MIDI controller triggers kit samples
✅ Velocity-sensitive playback
✅ Visual feedback on pad hits
✅ MIDI device selection in Settings
✅ Browser compatibility warnings
✅ Low latency (<10ms)
✅ Supports 16 pads (notes 36-51)
✅ Works with Akai MPD/Launchpad/SP-404MK2

### Nice-to-Have (Post-MVP)

⭐ MIDI learn feature
⭐ Performance recording
⭐ Multi-channel support
⭐ Velocity curve adjustment
⭐ Latency calibration tool

---

## Resources

### Documentation
- Web MIDI API Spec: https://www.w3.org/TR/webmidi/
- MDN Web MIDI: https://developer.mozilla.org/en-US/docs/Web/API/Web_MIDI_API
- webmidi.js Docs: https://webmidijs.org/docs/
- Existing research: `/docs/WEB_MIDI_RESEARCH.md`

### Libraries
- **webmidi.js:** `npm install webmidi` (RECOMMENDED)
- **web-midi-hooks:** `npm install web-midi-hooks` (optional React wrapper)

### Example Projects
- MIDIano: https://github.com/Bewelge/MIDIano
- WebMIDICon: https://github.com/dtinth/WebMIDICon
- Piano-Trainer: https://github.com/philippotto/Piano-Trainer

### Project Files to Reference
- `/react-app/src/hooks/useAudioPlayer.ts` - Audio pattern
- `/react-app/src/contexts/AudioContext.tsx` - Context pattern
- `/react-app/src/pages/KitsPage.tsx` - Kit structure
- `/docs/WEB_MIDI_RESEARCH.md` - Comprehensive MIDI research

---

## Decision Log

**2025-11-17:** Initial research completed
- ✅ Web MIDI API feasible for this use case
- ✅ webmidi.js selected as primary library
- ✅ Web Audio API chosen for sample playback
- ✅ Implementation deferred - documented for future work

---

## Next Steps (When Ready to Implement)

1. Review this document
2. Install `webmidi` package
3. Create proof-of-concept (Phase 1)
4. Test with physical MIDI controller
5. Iterate based on user feedback
6. Launch MVP to Chrome/Edge users

---

**Status:** Ready for implementation when needed. All research complete.
