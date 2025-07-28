# Timestamp-Based Extraction

The timestamp extraction system intelligently extracts specific segments from YouTube videos based on timestamps found in descriptions and comments. This allows users to download only the relevant samples instead of entire videos.

## Features

### 🕐 Timestamp Detection
- **Multiple Formats**: Recognizes various timestamp formats
  - Standard: `0:00`, `00:00`, `0:00:00`
  - With descriptions: `0:00 - Sample Name`
  - Bracketed: `[0:00] Sample Name`
  - Parenthetical: `(0:00) Sample Name`

- **Smart Recognition**: Identifies sample-related timestamps
  - Keywords: sample, loop, break, beat, drum, bass, melody
  - Filters out non-sample content (talking, intros, etc.)

### 🔥 Quality Indicators
- **Fire Emoji Detection**: Community-validated quality
  - 🔥 = Good sample
  - 🔥🔥 = Great sample
  - 🔥🔥🔥 = Excellent sample
  - 🔥🔥🔥🔥 = Must-have sample

- **Community Signals**: Recognizes quality indicators
  - "fire", "heat", "hot" keywords
  - Multiple fire emojis
  - Excitement indicators

### 🎯 Extraction Modes

#### 1. Auto-Detection Mode
```python
# Automatically finds and extracts all timestamps
results = await extract_youtube_timestamps(
    url="https://youtube.com/watch?v=abc123",
    output_dir="samples/",
    auto_detect=True
)
```

#### 2. Fire Samples Only
```python
# Extract only highly-rated samples (🔥🔥+)
results = await extract_fire_samples(
    url="https://youtube.com/watch?v=abc123",
    output_dir="samples/fire/",
    min_fire_count=2
)
```

#### 3. Manual Timestamps
```python
# Provide specific timestamps
timestamps = [
    {"time": 30, "timestamp": "0:30", "description": "Drum break"},
    {"time": 90, "timestamp": "1:30", "description": "Bass loop"}
]
results = await extract_youtube_timestamps(
    url="https://youtube.com/watch?v=abc123",
    output_dir="samples/",
    timestamps=timestamps,
    auto_detect=False
)
```

## Segment Generation

### Intelligent Segmentation
- Uses next timestamp as natural end point
- Default 30-second segments when no next timestamp
- Minimum 5-second segment length
- Respects video duration limits

### Audio Processing
- Automatic fade in/out (100ms default)
- Preserves original quality
- Multiple format support (WAV, MP3, FLAC)
- Comprehensive analysis of each segment

## Usage Examples

### Basic Usage
```python
from src.tools.timestamp_extractor import TimestampExtractor

extractor = TimestampExtractor()

# Extract from YouTube video
results = await extractor.extract_segments(
    url="https://youtube.com/watch?v=abc123",
    output_dir="samples/",
    auto_detect=True,
    segment_length=30,
    format="wav"
)

# Check results
for segment in results['segments']:
    print(f"Extracted: {segment['description']}")
    print(f"  File: {segment['file']}")
    print(f"  Duration: {segment['duration']}s")
    print(f"  BPM: {segment['analysis']['bpm']}")
```

### Fire Sample Extraction
```python
# Extract only the best samples
fire_results = await extractor.extract_fire_samples(
    url="https://youtube.com/watch?v=abc123",
    output_dir="samples/fire/",
    min_fire_count=3  # Only 🔥🔥🔥+ samples
)

print(f"Found {len(fire_results['segments'])} fire samples!")
```

### Custom Timestamp Processing
```python
# Parse timestamps from custom text
description = """
Sample pack contents:
0:00 - Intro (skip)
0:15 - Dusty drum break 🔥🔥
1:00 - Jazz piano loop 🔥🔥🔥
2:30 - Vintage soul chop 🔥🔥
"""

timestamps = extractor.extract_timestamps_from_text(description)
fire_samples = [ts for ts in timestamps if ts['quality_indicator'] >= 2]
```

## Output Structure

### Extraction Results
```json
{
  "video_url": "https://youtube.com/watch?v=abc123",
  "segments": [
    {
      "index": 1,
      "file": "samples/segment_01_Jazz_break_loop.wav",
      "start": 45,
      "end": 83,
      "duration": 38,
      "description": "Jazz break loop 🔥🔥",
      "is_sample": true,
      "quality_indicator": 2,
      "analysis": {
        "bpm": 92.5,
        "bpm_confidence": 0.85,
        "key": "F minor",
        "duration": 38,
        "frequency": {
          "spectral_centroid": 2500.0,
          "spectral_rolloff": 5000.0
        }
      }
    }
  ],
  "errors": []
}
```

### Segment Naming
- Format: `segment_{index:02d}_{safe_description}.{format}`
- Example: `segment_03_Vintage_soul_sample.wav`
- Removes special characters from descriptions
- Limits description length to 50 characters

## Integration with Pipeline

The timestamp extractor integrates seamlessly with the existing pipeline:

```python
# In your pipeline
from src.tools.timestamp_extractor import extract_youtube_timestamps

# After discovering a video with timestamps
if has_timestamps_in_description:
    # Extract segments instead of full video
    segments = await extract_youtube_timestamps(
        video_url,
        output_dir="samples/segments/"
    )
    
    # Process each segment
    for segment in segments['segments']:
        # Organize by BPM, key, etc.
        await organize_sample(segment)
```

## Performance Optimization

### Parallel Processing
- Downloads full video once
- Extracts all segments concurrently
- Analyzes segments in parallel
- Efficient memory usage

### Smart Caching
- Reuses downloaded video for multiple segments
- Caches analysis results
- Avoids redundant processing

## Error Handling

### Common Issues
1. **No timestamps found**: Falls back to automatic segmentation
2. **Invalid timestamps**: Skips and continues with valid ones
3. **Download failures**: Reports specific segment errors
4. **Analysis failures**: Provides partial results

### Error Response
```json
{
  "errors": [
    "Failed to extract segment 3: Invalid time range",
    "Analysis failed for segment 5: BPM detection error"
  ]
}
```

## Future Enhancements

1. **Comment Mining**: Extract timestamps from top comments
2. **Waveform Visualization**: Show visual segments
3. **Smart Boundaries**: Use silence detection for better cuts
4. **Batch Processing**: Handle playlists and channels
5. **Real-time Preview**: Stream segments before download

## Best Practices

1. **Check Description First**: Many producers list timestamps
2. **Trust Fire Emojis**: Community validation is valuable
3. **Verify Segments**: Quick preview before organizing
4. **Respect Copyright**: Only extract for personal use
5. **Credit Sources**: Keep track of original videos

## Troubleshooting

### No Segments Extracted
- Check if video has timestamps in description
- Try lowering fire count threshold
- Use automatic segmentation as fallback

### Poor Segment Quality
- Adjust fade in/out duration
- Increase segment length
- Check original video quality

### Analysis Errors
- Ensure audio libraries installed
- Check file permissions
- Verify segment duration (>1 second)