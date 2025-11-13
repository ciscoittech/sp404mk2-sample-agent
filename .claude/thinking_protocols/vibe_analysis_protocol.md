# Vibe Analysis Thinking Protocol

## Purpose
This protocol guides AI agents through analyzing the emotional, textural, and musical characteristics of audio samples for the SP-404MK2 workflow.

## 5-Step Thinking Process

### STEP 1: Analyze Musical Characteristics
First, examine the technical musical attributes and what they indicate:

**Questions to consider:**
- What does the BPM suggest about energy level and use case?
- What does the key signature tell us about emotional quality?
- What does the spectral centroid indicate about tonal character?
- Are there obvious rhythmic patterns or textures?
- What instrumentation can be inferred from spectral data?

**Example reasoning:**
```
"The BPM of 90 suggests a mid-tempo groove - not lazy, not frantic.
This falls in the classic boom-bap range (85-95 BPM).
The spectral centroid of 1200 Hz indicates warmth in the mid-range,
suggesting analog sources or warm instruments rather than bright digital synths."
```

### STEP 2: Consider Era and Production Context
Connect the musical characteristics to time periods and production techniques:

**Questions to consider:**
- What era does this BPM/spectrum combination suggest?
- What production techniques were common in that period?
- What gear might have been used?
- What genre movements align with these characteristics?

**Era indicators:**
- **1960s-70s**: Live drums (100-120 BPM), analog warmth, mono mixing
- **1980s**: Drum machines (808, LinnDrum), gated reverb, wide stereo
- **1990s**: Samplers (MPC, SP-1200), boom-bap (85-95 BPM), dusty lo-fi
- **2000s**: Digital clarity, faster tempos (trap: 140+ BPM), heavy bass
- **Modern**: Any BPM, hyper-processed or ultra-lo-fi, genre-blending

**Example reasoning:**
```
"90 BPM + warm spectral profile + live drum characteristics = likely 1990s or
neo-soul/boom-bap production. This was the era of MPC-style production,
sample-heavy hip-hop, and organic instrumentation layered with vinyl samples."
```

### STEP 3: Identify Mood and Emotional Qualities
Synthesize technical data into emotional descriptors:

**Mood framework:**
- **Energy**: low (chil, ambient) / medium (groovy, steady) / high (energetic, aggressive)
- **Valence**: dark (minor, tense) / neutral (ambiguous) / bright (major, uplifting)
- **Texture**: smooth (clean) / rough (distorted, gritty) / dusty (lo-fi, vintage)
- **Movement**: static (pads, drones) / flowing (arpeggios) / rhythmic (drums, loops)

**Common mood combinations:**
- **Dark + Low Energy + Rough** = Brooding, ominous, gritty
- **Bright + High Energy + Smooth** = Uplifting, exciting, polished
- **Neutral + Medium Energy + Dusty** = Nostalgic, warm, vintage
- **Dark + Medium Energy + Dusty** = Reflective, moody, atmospheric

**Example reasoning:**
```
"The combination of C minor (dark/serious), 90 BPM (medium energy),
and warm spectral profile (smooth-to-dusty texture) creates a reflective,
grounded mood. Not sad, but contemplative. Not aggressive, but purposeful.
This is the sonic space of introspective hip-hop, neo-soul, and jazzy beats."
```

### STEP 4: Determine Best Use Case
Based on all factors, recommend how a producer should use this sample:

**Use case categories:**
- **Foundation/Drums**: Primary rhythmic element, loop-able groove
- **Bass**: Sub-bass, bass line, low-end foundation
- **Melody**: Lead melodic element, hook, top-line
- **Harmony**: Chords, pads, harmonic bed
- **Texture**: Atmosphere, ambience, background
- **Transition**: Riser, drop, break, fill

**Considerations:**
- Mid-tempo grooves (85-100 BPM) → Foundation drums for hip-hop/neo-soul
- Fast loops (130+ BPM) → Drum breaks, transition elements
- Sparse, tonal samples → Melodic or harmonic layers
- Dense, percussive samples → Rhythmic foundation
- Ambient, evolving sounds → Texture and atmosphere

**Example reasoning:**
```
"Given the 90 BPM groove, warm character, and likely live drum source,
this sample works best as a foundation loop for verse sections.
It's steady enough to carry a track but has character to stay interesting.
The mid-range warmth means it can sit under melodies without frequency clash.
Use case: Drum foundation for boom-bap, lo-fi, or neo-soul production."
```

### STEP 5: Identify Compatibility and Complementary Samples
Think about what other samples would work well with this one:

**Compatibility factors:**
- **BPM**: Same tempo or harmonically related (half-time, double-time)
- **Key**: Same key, relative major/minor, or compatible keys (circle of fifths)
- **Era**: Similar production techniques and sonic character
- **Texture**: Complementary textures (smooth + gritty, clean + dusty)
- **Frequency**: Different frequency ranges to avoid masking
- **Role**: Different use cases to fill out arrangement

**Complementary pairing strategies:**
- **Drums + Bass**: Match BPM exactly, key can differ slightly
- **Drums + Melody**: Same key preferred, complementary energy
- **Multiple melodic layers**: Different octaves, complementary rhythms
- **Texture layers**: Foreground + background elements

**Example reasoning:**
```
"For this 90 BPM, C minor drum foundation, look for:
1. Bass samples: 80-100 BPM, C minor or Eb major, sub-100 Hz focus
2. Melodic samples: 90 BPM, C minor, mid-high frequency (1-4 kHz)
3. Texture samples: Vinyl crackle, tape hiss, ambient room tone
4. Complementary drums: Ghost notes, hi-hats, percussion in same tempo

Avoid: Aggressive, high-energy samples (energy mismatch)
Avoid: Bright major key samples unless going for tension (mood clash)
Seek: Other 90s-era samples with similar dusty, organic character"
```

## Output Format

After completing the 5-step thinking process, structure your output as JSON:

```json
{
  "mood": ["descriptor1", "descriptor2", "descriptor3"],
  "era": "time_period",
  "genre": "primary_genre",
  "energy_level": "low|medium|high",
  "descriptors": ["adjective1", "adjective2", "adjective3", "adjective4", "adjective5"],
  "compatibility_tags": ["tag1", "tag2", "tag3"],
  "best_use": "use_case"
}
```

## Common Pitfalls to Avoid

❌ **Jumping to conclusions without reasoning**
```
Bad: "This is a boom-bap sample."
Good: "The 90 BPM + warm analog character + live drums suggests boom-bap era production."
```

❌ **Generic descriptors without specificity**
```
Bad: mood = ["good", "nice", "cool"]
Good: mood = ["reflective", "warm", "grounded"]
```

❌ **Ignoring technical constraints**
```
Bad: Recommending 140 BPM samples as compatible with 90 BPM foundation
Good: Recommending 85-95 BPM samples or 45 BPM (half-time) samples
```

❌ **Mood/energy mismatches**
```
Bad: Describing C minor, slow sample as "uplifting and cheerful"
Good: Describing C minor, slow sample as "contemplative and serious"
```

❌ **Era anachronisms**
```
Bad: "1970s sample with heavy 808 bass" (808 released in 1980)
Good: "1970s sample with live bass" or "1980s sample with 808 bass"
```

## Example Complete Analysis

**Input:**
```
Filename: soul_break_vintage_01.wav
BPM: 93
Key: D minor
Spectral Centroid: 1150 Hz
```

**Thinking Process:**
```
STEP 1: Musical Characteristics
- BPM 93 is mid-tempo, classic hip-hop/soul range
- D minor suggests serious, emotional quality (not dark, not bright)
- Spectral centroid 1150 Hz = warm, mid-focused, analog character
- "soul_break" in name confirms live drum origin

STEP 2: Era and Production
- Warm spectrum + live drums + "vintage" = 1960s-70s recording
- 93 BPM fits soul, funk, early hip-hop sampling era
- Likely vinyl-sourced, might have tape saturation
- Classic breakbeat characteristics

STEP 3: Mood and Emotion
- D minor + mid-tempo = serious but not depressing
- Warm character = comfortable, organic feeling
- "Break" implies rhythmic intensity, forward movement
- Overall mood: purposeful, groovy, vintage soul

STEP 4: Best Use Case
- Classic breakbeat → perfect for drum foundation
- 93 BPM suits boom-bap, lo-fi, neo-soul production
- Warm character won't clash with melodic layers
- Use as: Verse drums, loop foundation, rhythmic bed

STEP 5: Compatibility
- Seek: 90-96 BPM samples
- Seek: D minor or F major (relative major) melodic elements
- Seek: Warm bass samples (sub-bass, 40-80 Hz)
- Seek: Jazz/soul/funk samples from same era
- Avoid: Bright, digital, modern samples (era mismatch)
- Avoid: Fast tempo samples (BPM mismatch)
```

**Output:**
```json
{
  "mood": ["purposeful", "groovy", "vintage"],
  "era": "1970s",
  "genre": "soul/funk",
  "energy_level": "medium",
  "descriptors": ["warm", "organic", "breakbeat", "dusty", "live-drums"],
  "compatibility_tags": ["boom-bap", "neo-soul", "jazzy", "vintage", "analog"],
  "best_use": "drum foundation"
}
```

## Using This Protocol

1. **Read the protocol before each analysis**
2. **Work through each step sequentially**
3. **Write out your reasoning** (don't skip to answers)
4. **Connect technical data to musical meaning**
5. **Think like a producer** (how would this be used?)
6. **Structure your final output** as specified JSON

This thinking process ensures consistent, high-quality vibe analysis that helps producers find and combine compatible samples for their SP-404MK2 workflow.
