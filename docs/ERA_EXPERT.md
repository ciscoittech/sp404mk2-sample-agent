# Era Expert Agent

The Era Expert Agent is a musical archaeologist and production historian that provides deep insights into recording techniques, equipment, and sonic characteristics across all eras of recorded music.

## Features

### 🎙️ Era Detection
- **Automatic Analysis**: Detects production era from audio characteristics
- **Frequency Profiling**: Analyzes spectral content to identify era
- **Artifact Recognition**: Identifies tape hiss, vinyl noise, digital artifacts
- **Confidence Scoring**: Rates detection certainty

### 📚 Historical Knowledge
- **Equipment Database**: Comprehensive listing of era-specific gear
- **Production Techniques**: Recording and mixing methods by decade
- **Sonic Signatures**: Characteristic sounds of each era
- **Genre Context**: Studio and producer information

### 🔍 Search Enhancement
- **Era-Specific Queries**: Generates period-appropriate search terms
- **Equipment References**: Includes iconic gear in searches
- **Producer Styles**: References key producers and studios
- **Modern Recreation**: Tips for achieving vintage sounds today

## Era Database

### 1950s-1960s: The Birth of Modern Recording
- **Equipment**: Ampex tape machines, Neumann U47, EMT plates
- **Techniques**: Live to 2-track, minimal overdubs
- **Sound**: Warm midrange, natural dynamics, mono/narrow stereo
- **Search Terms**: "vintage warmth", "tube saturation", "live room"

### 1970s: The Golden Age of Analog
- **Equipment**: Neve 8078, SSL 4000, Minimoog, Rhodes
- **Techniques**: 16/24 track, heavy compression, isolated recording
- **Sound**: Punchy drums, analog warmth, wide stereo
- **Genres**: Funk, Disco, Soul, Rock
- **Search Terms**: "analog warmth", "vintage compression", "70s funk"

### 1980s: Digital Revolution
- **Equipment**: Fairlight CMI, DX7, LinnDrum, Lexicon reverbs
- **Techniques**: MIDI sequencing, gated reverb, digital sampling
- **Sound**: Bright highs, huge reverbs, synthetic textures
- **Search Terms**: "80s reverb", "gated drums", "DX7 bass"

### 1990s: The Sampling Era
- **Equipment**: MPC2000/3000, SP-1200, Technics 1200s
- **Techniques**: Vinyl sampling, bit reduction, chopping
- **Sound**: Filtered highs, boom bap punch, vinyl artifacts
- **Genres**: Hip-Hop, R&B, Trip-Hop
- **Search Terms**: "boom bap", "golden era", "dusty samples"

### 2000s-2010s: The DAW Era
- **Equipment**: Software DAWs, plugin emulations, controllers
- **Techniques**: In-the-box production, loudness war mastering
- **Sound**: Hyped lows/highs, perfect timing, maximum loudness
- **Search Terms**: "modern production", "trap drums", "sidechain"

## Usage Examples

### Era Detection from Audio
```python
from src.agents.era_expert import analyze_era

# Detect era from audio files
result = await analyze_era(
    file_paths=["samples/vintage_break.wav"],
    enhance_search=True
)

# Check detection
analysis = result["analyses"][0]
print(f"Detected Era: {analysis['detected_era']}")
print(f"Confidence: {analysis['confidence']:.1%}")
print(f"Production Notes: {analysis['production_notes']}")
```

### Getting Era Information
```python
# Get detailed information about an era
result = await analyze_era(
    target_era="1970s",
    genre="soul",
    enhance_search=True
)

era_info = result["analyses"][0]
# Access equipment, techniques, characteristics
equipment = era_info["equipment"]
techniques = era_info["techniques"]
```

### Search Query Enhancement
```python
from src.agents.era_expert import get_era_search_queries

# Generate era-specific search queries
queries = await get_era_search_queries(
    era="1990s",
    genre="hip-hop",
    base_query="drum breaks"
)

# Results might include:
# - "drum breaks 1990s"
# - "drum breaks boom bap"
# - "drum breaks MPC2000/3000"
# - "drum breaks golden era samples"
# - "hip-hop boom bap MPC"
```

### Modern Recreation Tips
```python
# Get tips for recreating vintage sounds
agent = EraExpertAgent()
tips = agent._get_modern_recreation_tips("1970s")

# Access plugins, techniques, and tips
print("Plugins:", tips["plugins"])
print("Techniques:", tips["techniques"])
print("Pro Tips:", tips["tips"])
```

## Genre-Specific Knowledge

### Motown (1960s)
- **Studio**: Hitsville U.S.A., Studio A
- **Producers**: Berry Gordy, Smokey Robinson
- **Signature**: Direct-input bass, tambourine on 2&4
- **Secret**: Custom EQ curve on mix bus

### Philadelphia Soul (1970s)
- **Studio**: Sigma Sound Studios
- **Producers**: Gamble & Huff
- **Signature**: Lush strings, MFSB rhythm section
- **Sound**: The "Philadelphia Sound" - orchestral soul

### Golden Era Hip-Hop (1990s)
- **Studios**: D&D, Battery, Unique Recording
- **Producers**: DJ Premier, Pete Rock, Large Professor
- **Signature**: Filtered jazz loops, hard drums
- **Equipment**: SP-1200 for crunch, MPC for swing

## Modern Recreation Guide

### Achieving Vintage Sounds Today

#### 1950s-1960s Sound
- **Plugins**: UAD Studer A800, Waves J37, Softube Tube-Tech
- **Techniques**: Record in mono, use room mics, gentle saturation
- **Tips**: Less is more, commit to sounds, preserve dynamics

#### 1970s Analog Warmth
- **Plugins**: UAD Neve 1073, Waves SSL, Arturia analogs
- **Techniques**: Parallel compression, analog-style EQ, tape delay
- **Tips**: Push the preamps, use bus compression, wide stereo

#### 1980s Digital Brightness
- **Plugins**: Arturia DX7 V, D16 LuSH-101, Valhalla VintageVerb
- **Techniques**: Gated reverb, chorus on everything, digital delays
- **Tips**: Embrace brightness, big reverbs, layer synths

#### 1990s Sampling Era
- **Plugins**: XLN RC-20, Decimort 2, Vinyl simulators
- **Techniques**: Bit reduction, vinyl simulation, MPC swing
- **Tips**: Sample in mono, filter highs, add vinyl crackle

## Era Authentication

### Verifying Authenticity
1. **Frequency Content**: Check for era-appropriate rolloff
2. **Dynamic Range**: Compare to typical era compression
3. **Noise Floor**: Look for tape hiss, vinyl noise
4. **Stereo Image**: Mono (60s) vs wide (80s)

### Common Era Indicators
- **1960s**: Limited highs, mono, room ambience
- **1970s**: Warm mids, analog compression artifacts
- **1980s**: Bright digital sheen, gated reverb tails
- **1990s**: Filtered samples, 12-bit aliasing, vinyl noise
- **2000s+**: Loudness war compression, perfect pitch

## Search Enhancement Examples

### Base Query: "soul bass"
#### 1970s Enhancement:
- "soul bass Fender Precision"
- "soul bass James Jamerson"
- "Philadelphia soul bass direct"
- "70s funk bass Bootsy Collins"

### Base Query: "hip hop drums"
#### 1990s Enhancement:
- "hip hop drums MPC2000"
- "SP-1200 drum breaks 90 BPM"
- "Pete Rock drums dusty"
- "DJ Premier drums chopped"

## Best Practices

### For Sample Discovery
1. **Include Era Terms**: Add decade or year range
2. **Reference Equipment**: Include iconic gear names
3. **Use Genre Context**: Add studio or producer names
4. **Layer Searches**: Combine era + genre + technique

### For Production
1. **Study the Limitations**: Era constraints created signatures
2. **Embrace Imperfections**: Noise and artifacts add character
3. **Use Period Techniques**: Match recording methods to era
4. **Reference Original Tracks**: Compare to era exemplars

## Integration with Pipeline

```python
# In your discovery pipeline
from src.agents.era_expert import EraExpertAgent

agent = EraExpertAgent()

# Enhance searches based on desired era
if user_wants_70s_sound:
    result = await agent.execute(
        task_id="era_search",
        target_era="1970s",
        genre="funk",
        base_query="drum breaks",
        enhance_search=True
    )
    
    # Use enhanced queries for discovery
    enhanced_queries = result.result["analyses"][0]["enhanced_searches"]
```

## Troubleshooting

### Incorrect Era Detection
- Check file quality and encoding
- Ensure authentic source material
- Consider modern recreations may confuse detection

### Missing Genre Context
- Not all genre/era combinations have data
- Try broader genre categories
- Check alternative era ranges