# Groove Analyst Agent

The Groove Analyst Agent provides deep rhythm and timing analysis for audio samples, helping producers understand and match grooves with precision.

## Features

### 🎵 Rhythm Analysis
- **Swing Quantification**: Measures swing percentage (50% straight to 75% hard swing)
- **Microtiming Detection**: Analyzes millisecond-level timing variations
- **Pocket Analysis**: Scores how well elements "lock" together rhythmically
- **Push/Pull Detection**: Identifies if playing ahead, behind, or on the beat

### 🥁 Groove Characteristics
- **Humanization Level**: mechanical → tight → loose → human → drunk
- **Ghost Note Density**: Detects subtle rhythmic elements
- **Timing Consistency**: Measures natural variations vs precision
- **Era Classification**: Identifies production era by groove characteristics

### 🔍 Reference Matching
- **Artist Similarity**: Matches grooves to famous drummers/producers
- **Style Detection**: J Dilla, Questlove, Bernard Purdie, etc.
- **Compatibility Scoring**: Rates how well grooves work together

## Analysis Output

### Complete Analysis Structure
```yaml
groove_analysis:
  bpm: 92.5
  bpm_confidence: 0.85
  
  groove:
    swing_percentage: 64.3
    timing_feel: "behind"
    pocket_score: 8.5/10
    humanization_level: "loose"
    ghost_note_density: "medium"
  
  timing:
    average_deviation_ms: 18.5
    swing_ratio: "64:36"
    push_pull_ms: -12.0  # Negative = behind
    consistency: 0.78
    
  musical_description: |
    Medium swing creating a bouncy, head-nodding groove.
    Playing behind the beat creates a laid-back, relaxed feel.
    Sits deep in the pocket with incredible groove.
    
  similar_to: ["Dilla", "Questlove (similar feel)"]
  era_classification: "1990s"
  
  recommendations:
    - "Perfect for hip-hop production and head-nodding beats"
    - "Layer with straight drums for rhythmic contrast"
    - "Preserve the natural timing when chopping"
```

## Usage Examples

### Basic Groove Analysis
```python
from src.agents.groove_analyst import analyze_groove

# Analyze single file
result = await analyze_groove(
    file_paths=["samples/drum_break.wav"],
    analysis_depth="detailed"
)

# Check groove characteristics
groove = result["analyses"][0]["groove"]
print(f"Swing: {groove['swing_percentage']}%")
print(f"Pocket Score: {groove['pocket_score']}/10")
print(f"Feel: {groove['timing_feel']}")
```

### Comparing Multiple Grooves
```python
# Compare grooves for compatibility
result = await analyze_groove(
    file_paths=[
        "samples/main_drums.wav",
        "samples/percussion_loop.wav",
        "samples/hi_hat_pattern.wav"
    ],
    compare=True
)

# Get compatibility scores
comparison = result["comparison"]
best_pair = comparison["best_pair"]
print(f"Best match: {best_pair['file1']} + {best_pair['file2']}")
print(f"Compatibility: {best_pair['compatibility_score']}/10")
```

### Integration with Pipeline
```python
# In your pipeline
from src.agents.groove_analyst import GrooveAnalystAgent

agent = GrooveAnalystAgent()

# Analyze downloaded samples
for sample in downloaded_samples:
    result = await agent.execute(
        task_id=f"groove_{sample['id']}",
        file_paths=[sample['path']]
    )
    
    if result.status == AgentStatus.SUCCESS:
        groove_data = result.result["analyses"][0]
        # Use groove data for organization
        sample['groove_metadata'] = groove_data
```

## Groove References

### Famous Groove Signatures

#### J Dilla
- **Swing**: 62-68%
- **Timing**: Intentionally "drunk" timing
- **Characteristics**: Off-kilter, wonky, humanized
- **Recognition**: MPC3000 swing, Detroit hip-hop

#### Questlove
- **Swing**: 58-62%
- **Timing**: Consistently 15-20ms behind grid
- **Characteristics**: Deep pocket, laid-back
- **Recognition**: The Roots, neo-soul

#### Bernard Purdie
- **Swing**: 55-60%
- **Timing**: On the beat with ghost notes
- **Characteristics**: The "Purdie Shuffle"
- **Recognition**: Steely Dan, session work

#### Programmed/Quantized
- **Swing**: 50-52%
- **Timing**: Machine-perfect
- **Characteristics**: No deviation, rigid
- **Recognition**: Modern trap, EDM

## Era Classification

### Groove Characteristics by Decade

| Era | Swing Range | Humanization | Characteristics |
|-----|-------------|--------------|-----------------|
| 1960s | 55-65% | Human | Live recording, slight rushing |
| 1970s | 56-62% | Tight | Funk pocket, tape compression |
| 1980s | 50-55% | Mechanical | Drum machines, gated reverb |
| 1990s | 58-68% | Loose | MPC swing, golden era hip-hop |
| 2000s+ | 50-65% | Mixed | Hybrid human/quantized |

## Compatibility Scoring

### How Grooves Are Matched

1. **Swing Difference**: Within 5% = highly compatible
2. **Timing Feel**: Same feel (behind/on/ahead) = better match
3. **Humanization**: Similar levels work better together
4. **Pocket Score**: High pocket scores blend well

### Compatibility Recommendations
- **8-10/10**: Excellent match - lock together perfectly
- **6-8/10**: Good compatibility - minor adjustments help
- **4-6/10**: Moderate - use creatively for contrast
- **0-4/10**: Low - best in different song sections

## Technical Details

### Swing Calculation
```
Swing % = (Second 8th note position - 0.5) / 0.5 * 100
Where:
- 0.5 = straight (50%)
- 0.67 = triplet feel (67%)
- 0.75 = maximum swing (75%)
```

### Pocket Score Algorithm
```python
pocket_score = 10.0
# Optimal at 15ms behind beat
pocket_score -= abs(timing.push_pull_ms + 15) / 10
# Consistency matters
pocket_score -= (1 - timing.consistency) * 5
# Cap at 0-10 range
pocket_score = max(0, min(10, pocket_score))
```

### Timing Analysis
- **Onset Detection**: Find exact hit points
- **Grid Deviation**: Measure from perfect quantization
- **Consistency**: Standard deviation of timing
- **Push/Pull**: Average ahead/behind measurement

## Best Practices

### For Sample Selection
1. **Match BPM First**: Stay within ±5 BPM
2. **Check Swing Compatibility**: ±5% works well
3. **Consider Pocket Scores**: 7+ for main grooves
4. **Preserve Natural Timing**: Don't over-quantize

### For Production
1. **Layer Different Swings**: Creates rhythmic interest
2. **Use Behind-Beat for Space**: Laid-back grooves leave room
3. **Match Era Characteristics**: Consistency in production
4. **Trust High Pocket Scores**: They carry tracks

## Advanced Features

### Multi-Layer Analysis
Analyze complete drum stems:
- Kick pattern timing
- Snare placement
- Hi-hat swing
- Overall cohesion

### Groove Fingerprinting
Create unique signatures for:
- Sample matching
- Duplicate detection
- Style clustering

### Adaptive Recommendations
Based on your production style:
- Suggested pairings
- Complementary grooves
- Contrast options

## Troubleshooting

### Inaccurate BPM Detection
- Check file quality
- Ensure clear transients
- Try manual BPM setting

### Low Pocket Scores
- Natural for experimental grooves
- Check if intentionally loose
- May need timing correction

### No Similar Artists Found
- Unique groove pattern
- Try broader search
- Check swing percentage