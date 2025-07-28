# Intelligent Organization System

The Intelligent Organization System automatically organizes your sample library using advanced musical analysis, creating logical folder structures that match your workflow and the SP-404MK2's bank system.

## Features

### 🎯 Organization Strategies

1. **Musical Properties**
   - Organizes by BPM ranges, musical key, and sample type
   - Creates intuitive folder hierarchy: `type/bpm_range/key`
   - Perfect for general library management

2. **Genre & Era**
   - Groups samples by detected era and inferred genre
   - Leverages Era Expert Agent for historical accuracy
   - Structure: `genre/era` (e.g., `hip_hop/1990s`)

3. **Groove Style**
   - Categorizes by rhythmic feel and swing percentage
   - Uses Groove Analyst Agent for deep rhythm analysis
   - Structure: `groove_type/feel` (e.g., `boom_bap/heavy_swing`)

4. **Compatibility Groups**
   - Groups samples that work well together musically
   - Uses Sample Relationship Agent for compatibility scoring
   - Creates ready-to-use sample kits

5. **SP-404 Banks**
   - Organizes directly into SP-404MK2 bank structure
   - Multiple templates for different performance styles
   - Automatic pad assignment optimization

6. **Project-Specific**
   - Tailored organization for specific workflows
   - Templates for beat making, live looping, and more
   - Focuses on practical production needs

### 📊 Intelligent Analysis

- **Multi-Agent Analysis**: Leverages all specialized agents
- **Metadata Preservation**: Saves analysis data with samples
- **Descriptive Renaming**: Adds BPM, key, and style to filenames
- **Compatibility Scoring**: Identifies samples that work together
- **Batch Processing**: Handles large libraries efficiently

## Usage Examples

### Basic Musical Organization
```python
from src.tools.intelligent_organizer import organize_samples

# Organize by musical properties
result = await organize_samples(
    sample_paths=["sample1.wav", "sample2.wav", ...],
    strategy="musical",
    output_dir="my_organized_library"
)

# Check the report
print(result["report"])
```

### Create SP-404 Banks
```python
from src.tools.intelligent_organizer import create_sp404_banks

# Organize into SP-404 bank structure
result = await create_sp404_banks(
    sample_paths=drum_samples,
    template="hip_hop_kit",  # or "live_performance", "finger_drumming"
    output_dir="sp404_banks"
)

# Result structure:
# SP404_Bank_A/
#   A01_kick_90bpm_Cmaj.wav
#   A02_snare_90bpm_Cmaj.wav
#   A03_hihat_closed_90bpm.wav
#   A04_hihat_open_90bpm.wav
# SP404_Bank_B/
#   B01_perc1_...
#   etc.
```

### Group Compatible Samples
```python
# Find and group compatible samples
result = await organize_samples(
    sample_paths=all_samples,
    strategy="compatibility",
    threshold=7.0,  # Minimum compatibility score (0-10)
    analyze_relationships=True
)

# Results in:
# compatible_group_1/
#   kick_90bpm_C.wav
#   bass_90bpm_C.wav
#   melody_90bpm_G.wav
# compatible_group_2/
#   ...
```

### Genre-Based Organization
```python
# Organize by detected genre and era
result = await organize_samples(
    sample_paths=vintage_samples,
    strategy="genre",
    output_dir="genre_collection"
)

# Results in:
# hip_hop/1990s/
#   boom_bap_break_93bpm.wav
#   dusty_sample_90bpm.wav
# soul/1970s/
#   funk_bass_85bpm.wav
#   rhythm_guitar_95bpm.wav
```

## Organization Strategies Detail

### Musical Properties Strategy
Creates a three-level hierarchy:
```
organized_samples/
├── drums/
│   ├── slow_60-70/
│   │   ├── Cmaj/
│   │   └── Amin/
│   ├── medium_70-90/
│   └── uptempo_90-120/
├── bass/
│   └── [similar structure]
└── melody/
    └── [similar structure]
```

### SP-404 Bank Templates

#### Hip-Hop Kit Template
- **Bank A**: Core drums (kick, snare, hats)
- **Bank B**: Percussion and cymbals
- **Bank C**: Bass elements (bass, sub, 808)
- **Bank D**: Melodic elements and FX

#### Live Performance Template
- **Bank A**: Song sections (intro, verses)
- **Bank B**: Choruses and transitions
- **Bank C**: Drum variations
- **Bank D**: Effects and atmospheres

#### Finger Drumming Template
- **Bank A**: Primary drums (2 kicks, 2 snares)
- **Bank B**: Hi-hats and cymbals
- **Bank C**: Toms and claps
- **Bank D**: Percussion elements

### Compatibility Grouping
The system analyzes:
1. **Harmonic compatibility** (key relationships)
2. **Rhythmic compatibility** (BPM and groove)
3. **Frequency compatibility** (spectral overlap)
4. **Energy compatibility** (dynamic levels)

Groups are formed with samples scoring 7.0+ compatibility.

### Project-Specific Templates

#### Beat Making
```
beat_making/
├── drums/        # Rhythmic elements
├── bass/         # Low-end elements
├── melodies/     # Melodic loops and samples
├── textures/     # Atmospheric elements
└── oneshots/     # Short hits and stabs
```

#### Live Looping
```
live_looping/
├── loops_4bar/   # Standard 4-bar loops
├── loops_8bar/   # Extended 8-bar loops
├── transitions/  # FX and risers
└── oneshots/     # Triggers and hits
```

## Advanced Options

### Analysis Depth
```python
result = await organize_samples(
    sample_paths=samples,
    strategy="musical",
    analyze_relationships=True,  # Deep compatibility analysis
    copy_files=False            # Plan only, don't copy files
)
```

### Custom Renaming
The system automatically generates descriptive names:
- Original: `break_001.wav`
- Renamed: `break_001_93bpm_Amin_boombap.wav`

### Metadata Preservation
Each organized sample gets a companion `.json` file:
```json
{
  "original_path": "/original/break_001.wav",
  "bpm": {"bpm": 93.2, "confidence": 0.95},
  "key": {"key": "A minor", "confidence": 0.87},
  "groove": {
    "groove_type": "boom_bap",
    "swing_percentage": 67.5
  },
  "era": {
    "detected_era": "1990s",
    "confidence": 0.82
  }
}
```

## Organization Report

After organization, you get a detailed report:
```
# Sample Organization Report

Date: 2024-01-20 15:30:00
Total Samples: 150
Folders Created: 25
Files Organized: 150

## Organization Structure

### drums/uptempo_90-120/Cmaj (15 files)
- kick_punchy_90bpm_Cmaj_boombap.wav
  - BPM: 90.0
  - Key: C major
  - Groove: boom_bap
...

## High Compatibility Pairs
- kick_90bpm_C.wav + bass_90bpm_C.wav: 9.5/10
- melody_120bpm_C.wav + pad_120bpm_Am.wav: 8.8/10
```

## Best Practices

### For Large Libraries
1. **Start with Musical Organization**: Get a general structure
2. **Create SP-404 Banks**: From your favorites
3. **Build Compatibility Groups**: For quick kit creation
4. **Use Project Templates**: For specific productions

### Workflow Integration
1. **After Discovery**: Organize newly discovered samples
2. **Before Production**: Create project-specific folders
3. **Regular Maintenance**: Re-organize as library grows
4. **Backup Originals**: Always keep source files

### Performance Tips
- Process in batches of 50-100 samples
- Disable compatibility analysis for speed
- Use `copy_files=False` to preview organization
- Run overnight for very large libraries

## Troubleshooting

### Slow Processing
- Reduce batch size
- Disable relationship analysis
- Use faster strategy (musical vs compatibility)

### Incorrect Categorization
- Check sample quality and format
- Verify samples are properly trimmed
- Some ambient/experimental samples may not categorize well

### SP-404 Template Mismatch
- Ensure you have enough samples for the template
- Some samples may not fit template categories
- Check the overflow folder for uncategorized samples