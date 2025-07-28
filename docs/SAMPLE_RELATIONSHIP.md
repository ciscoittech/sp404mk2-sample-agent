# Sample Relationship Agent

The Sample Relationship Agent analyzes musical compatibility between samples, providing detailed insights into how well different audio elements work together harmonically, rhythmically, and spectrally.

## Features

### 🎵 Harmonic Analysis
- **Key Detection**: Identifies the musical key of each sample
- **Interval Relationships**: Calculates semitone distances and musical intervals
- **Compatibility Scoring**: Rates harmonic compatibility from 0-10
- **Transposition Suggestions**: Recommends pitch adjustments when needed

### 🥁 Rhythmic Analysis
- **BPM Matching**: Detects and compares tempos
- **Tempo Relationships**: Identifies half-time, double-time, and polyrhythmic patterns
- **Groove Compatibility**: Analyzes swing and timing characteristics
- **Sync Recommendations**: Suggests tempo adjustments or time-stretching

### 📊 Frequency Analysis
- **Spectral Overlap**: Identifies frequency range conflicts
- **Masking Detection**: Warns about potential frequency masking issues
- **Complementary Scoring**: Rates how well samples fill each other's gaps
- **EQ Suggestions**: Provides specific frequency adjustment recommendations

### ⚡ Energy Compatibility
- **Dynamic Matching**: Compares energy levels between samples
- **Contrast Analysis**: Evaluates whether energy differences create interest or conflict
- **Arrangement Tips**: Suggests how to balance energy levels

## Usage Examples

### Basic Compatibility Check
```python
from src.agents.sample_relationship import analyze_sample_compatibility

# Analyze compatibility between two samples
result = await analyze_sample_compatibility(
    sample_pairs=[("kick.wav", "bass.wav")],
    genre="hip-hop"
)

# Check the results
analysis = result["analyses"][0]
print(f"Overall Score: {analysis['overall_score']}/10")
print(f"Relationship: {analysis['relationship_type']}")
print(f"Best Arrangement: {analysis['best_arrangement']}")
```

### Kit Building Analysis
```python
# Analyze multiple sample combinations for kit building
drum_kit_pairs = [
    ("kick.wav", "snare.wav"),
    ("kick.wav", "hihat.wav"),
    ("snare.wav", "crash.wav"),
    ("kick.wav", "808.wav")
]

result = await analyze_sample_compatibility(
    sample_pairs=drum_kit_pairs,
    genre="trap",
    analysis_depth="deep"
)

# Get kit suggestions
kit = result["kit_suggestions"]
print(f"Best combo: {kit['best_combination']['samples']}")
print(f"Kit recommendation: {kit['kit_recommendation']}")
```

### Specific Check Types
```python
# Check only harmonic compatibility
harmonic_result = await analyze_sample_compatibility(
    sample_pairs=[("melody1.wav", "melody2.wav")],
    check_type="harmonic"
)

# Check only rhythmic compatibility
rhythm_result = await analyze_sample_compatibility(
    sample_pairs=[("drums1.wav", "drums2.wav")],
    check_type="rhythmic"
)

# Check only frequency compatibility
freq_result = await analyze_sample_compatibility(
    sample_pairs=[("bass.wav", "sub.wav")],
    check_type="frequency"
)
```

## Compatibility Scoring System

### Overall Score Interpretation
- **8-10**: Excellent compatibility - use together immediately
- **6-7.9**: Good compatibility - minor adjustments may help
- **4-5.9**: Moderate compatibility - requires careful arrangement
- **0-3.9**: Low compatibility - consider alternatives

### Relationship Types
- **Perfect Match**: Samples work together seamlessly
- **Harmonic Partners**: Strong key relationship
- **Rhythmic Lock**: Tight groove compatibility
- **Frequency Complement**: Fill each other's spectral gaps
- **Compatible Blend**: Work well with some adjustment
- **Creative Tension**: Interesting but challenging
- **Challenging Combination**: Difficult to use together

## Musical Interval Compatibility

The agent uses music theory to score harmonic relationships:

| Interval | Semitones | Score | Use Case |
|----------|-----------|-------|-----------|
| Unison | 0 | 10/10 | Perfect match, layer for thickness |
| Octave | 12 | 10/10 | Natural doubling, adds depth |
| Perfect 5th | 7 | 9/10 | Strong harmonic support |
| Perfect 4th | 5 | 8.5/10 | Stable, slightly tense |
| Major 6th | 9 | 7/10 | Relative minor relationship |
| Minor 3rd | 3 | 7/10 | Dark, emotional pairing |
| Major 3rd | 4 | 6.5/10 | Bright, happy combination |
| Minor 6th | 8 | 6/10 | Melancholic tension |
| Major 2nd | 2 | 5/10 | Suspended feeling |
| Minor 7th | 10 | 4.5/10 | Jazz tension |
| Major 7th | 11 | 4/10 | Complex harmony |
| Tritone | 6 | 3/10 | Maximum tension |
| Minor 2nd | 1 | 2/10 | Dissonant clash |

## Frequency Range Analysis

The agent analyzes these frequency bands:
- **Sub Bass** (20-60 Hz): Only one element should occupy
- **Bass** (60-250 Hz): Careful overlap management
- **Low Mid** (250-500 Hz): Avoid muddiness
- **Mid** (500-2000 Hz): Critical presence range
- **High Mid** (2000-4000 Hz): Clarity vs harshness
- **High** (4000-20000 Hz): Air and brightness

## Genre-Specific Rules

### Hip-Hop
- Kick and 808 must be tuned to the same key
- Samples and drums need matching swing
- Leave 1-3kHz space for vocals

### Jazz
- Walking bass shouldn't clash with comping
- Horns and keys should alternate phrases
- Drums lead the dynamic changes

### Electronic
- Only one sub-bass element at a time
- Multiple synths need distinct filter ranges
- Percussion layers should vary in stereo placement

## Best Practices

### For Producers
1. **Start with Compatibility**: Check samples before heavy processing
2. **Trust the Scores**: High scores usually mean less work needed
3. **Use Recommendations**: Follow EQ and arrangement suggestions
4. **Consider Genre**: Apply genre-specific rules for authentic sound

### For Sample Selection
1. **Build Compatible Kits**: Use the kit analysis for cohesive sets
2. **Mix Relationship Types**: Combine different compatibility types
3. **Balance Energy**: Mix similar and contrasting energy levels
4. **Frequency Planning**: Ensure each sample has its space

## Advanced Features

### Deep Analysis Mode
```python
result = await analyze_sample_compatibility(
    sample_pairs=pairs,
    analysis_depth="deep"  # More thorough analysis
)
```

### Genre Contexts
Supported genres with specific rules:
- `hip-hop`: Focus on groove and sub-bass management
- `jazz`: Emphasis on harmonic complexity and dynamics
- `electronic`: Strict frequency separation and stereo imaging
- `general`: Balanced approach for all genres

## Integration Examples

### With Discovery Pipeline
```python
# After discovering samples, check compatibility
discovered_samples = await discover_samples(query)
pairs = [(samples[0], samples[1]) for samples in discovered_samples]
compatibility = await analyze_sample_compatibility(pairs)
```

### With Organization System
```python
# Organize samples by compatibility
high_compat = [a for a in analyses if a["overall_score"] >= 7]
create_folder("Compatible Pairs", high_compat)
```

## Troubleshooting

### Low Scores Everywhere
- Check file quality and format
- Ensure samples are properly trimmed
- Verify genre selection matches content

### Incorrect Key Detection
- Samples may be atonal or percussion-only
- Very short samples may confuse detection
- Complex harmonies might need manual verification

### Missing Analysis Types
- Some samples may not have detectable properties
- Percussion-only files won't have harmonic analysis
- Ambient sounds may lack clear rhythm