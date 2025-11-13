# Timestamp Extractor Tool

## Purpose
Extract sample timestamps from YouTube video descriptions and comments. Identifies individual samples within longer videos (sample packs, mix tapes, beat compilations) so producers can download specific segments rather than entire videos.

## When to Use

**Use this tool when:**
- ✅ User provides a specific YouTube URL
- ✅ Video appears to be a sample pack or compilation
- ✅ Need to identify individual samples within a long video
- ✅ Video description likely contains timestamps
- ✅ User wants to analyze a specific video for samples

**DO NOT use this tool when:**
- ❌ User asks to "find" or "search" for samples (use `youtube_search` instead)
- ❌ No YouTube URL provided (need URL to extract from)
- ❌ Video is a single sample/loop (no timestamps needed)
- ❌ User wants general sample discovery (not specific video analysis)

## Tool Signature

```python
class TimestampExtractor:
    def extract_from_url(self, url: str) -> Dict[str, Any]
    def extract_timestamps_from_text(self, text: str) -> List[Dict[str, Any]]
```

## Methods

### `extract_from_url(url: str)`

**Parameters:**
- `url` (required): YouTube video URL (full or short form)

**Returns:** `Dict[str, Any]`
```python
{
    "url": str,                          # Original URL
    "video_id": str,                     # YouTube video ID
    "title": str,                        # Video title
    "description_timestamps": List[Dict], # Timestamps from description
    "comment_timestamps": List[Dict],    # Timestamps from comments (if fetched)
    "total_timestamps": int              # Total count
}
```

**Example:**
```python
extractor = TimestampExtractor()
result = extractor.extract_from_url("https://youtube.com/watch?v=abc123")

print(result['total_timestamps'])  # 15
for ts in result['description_timestamps']:
    print(f"{ts['timestamp']} - {ts['description']}")
```

---

### `extract_timestamps_from_text(text: str)`

**Parameters:**
- `text` (required): Text to extract timestamps from (description or comment)

**Returns:** `List[Dict[str, Any]]`
```python
[
    {
        "timestamp": str,         # "0:00", "1:23", "12:34"
        "seconds": int,          # Total seconds (for seeking)
        "description": str,      # Text after timestamp
        "is_sample": bool       # Likely a sample vs section marker
    },
    # ... more timestamps
]
```

**Timestamp Format Detection:**
```python
# Supported formats:
"0:00 - Intro"          # MM:SS
"1:23 Sample 1"         # MM:SS
"12:34:56 Long video"   # HH:MM:SS
"0:00:00 Start"         # HH:MM:SS
"[0:00] Timestamped"    # Brackets
"(1:23) Sample"         # Parentheses
```

## Return Value Details

### Timestamp Object Structure

```python
{
    "timestamp": "1:23",               # Original timestamp string
    "seconds": 83,                     # Converted to seconds
    "description": "Dusty Jazz Loop",  # Description text
    "is_sample": True,                 # Heuristic: likely a sample?
    "confidence": 0.85                 # 0.0-1.0 confidence score
}
```

### Sample Detection Heuristics

**High Confidence (>0.8):**
- Contains: "sample", "loop", "break", "drum", "bass", "melody"
- Pattern: "#1", "Sample 01", "Track 1"
- Numbered sequence: "1.", "2.", "3."

**Medium Confidence (0.5-0.8):**
- Contains genre names: "jazz", "soul", "funk"
- Contains descriptors: "dusty", "vintage", "classic"
- Contains instruments: "piano", "guitar", "saxophone"

**Low Confidence (<0.5):**
- Generic: "intro", "outro", "end"
- No sample indicators
- Too vague: "next", "more"

**Example Classification:**
```python
"0:00 Dusty Jazz Piano Sample"     → is_sample=True, confidence=0.95
"1:23 Sample #1"                   → is_sample=True, confidence=0.9
"5:00 Vintage Drum Break"          → is_sample=True, confidence=0.85
"10:00 Interlude"                  → is_sample=False, confidence=0.3
"15:00 Thanks for watching"        → is_sample=False, confidence=0.1
```

## Usage Examples

### Example 1: Analyzing a Sample Pack Video

**Context:**
```
User: "https://youtube.com/watch?v=xyz789"
(Video title: "FREE 90s Soul Sample Pack - 10 Samples")
```

**Thinking Process:**
```
1. User provided URL → Use timestamp_extractor
2. Video appears to be sample pack → Extract timestamps
3. Description likely has sample list → Parse timestamps
4. Present results to user
```

**Tool Usage:**
```python
from src.tools.timestamp_extractor import TimestampExtractor

extractor = TimestampExtractor()

# Extract timestamps from video
result = extractor.extract_from_url(
    "https://youtube.com/watch?v=xyz789"
)

print(f"Found {result['total_timestamps']} timestamps")
print(f"Video: {result['title']}")

# Filter for likely samples
samples = [
    ts for ts in result['description_timestamps']
    if ts['is_sample'] and ts['confidence'] > 0.7
]

print(f"\nSamples detected: {len(samples)}")
for i, sample in enumerate(samples, 1):
    print(f"{i}. {sample['timestamp']} - {sample['description']}")
    print(f"   Confidence: {sample['confidence']:.2f}")
```

**Expected Output:**
```
Found 10 timestamps
Video: FREE 90s Soul Sample Pack - 10 Samples

Samples detected: 10
1. 0:00 - Dusty Jazz Piano Loop
   Confidence: 0.92
2. 0:45 - Vintage Drum Break
   Confidence: 0.88
3. 1:30 - Soul Bassline
   Confidence: 0.85
...
```

---

### Example 2: Distinguishing Samples from Section Markers

**Context:**
```
Video description:
"0:00 Intro
 0:15 Sample 1 - Jazz Loop
 1:00 Sample 2 - Drum Break
 2:30 Outro
 3:00 Download Link"
```

**Tool Usage:**
```python
description = """
0:00 Intro
0:15 Sample 1 - Jazz Loop
1:00 Sample 2 - Drum Break
2:30 Outro
3:00 Download Link
"""

timestamps = extractor.extract_timestamps_from_text(description)

# Separate samples from markers
samples = []
markers = []

for ts in timestamps:
    if ts['is_sample']:
        samples.append(ts)
    else:
        markers.append(ts)

print(f"Actual samples: {len(samples)}")
for s in samples:
    print(f"  {s['timestamp']} - {s['description']}")

print(f"\nSection markers: {len(markers)}")
for m in markers:
    print(f"  {m['timestamp']} - {m['description']}")
```

**Expected Output:**
```
Actual samples: 2
  0:15 - Sample 1 - Jazz Loop
  1:00 - Sample 2 - Drum Break

Section markers: 3
  0:00 - Intro
  2:30 - Outro
  3:00 - Download Link
```

---

### Example 3: Integration with Download Workflow

**Context:**
```
User: "Download samples 1-3 from https://youtube.com/watch?v=abc123"
```

**Full Workflow:**
```python
from src.tools.timestamp_extractor import TimestampExtractor
from src.tools.download import download_youtube_segment

# 1. Extract timestamps
extractor = TimestampExtractor()
result = extractor.extract_from_url("https://youtube.com/watch?v=abc123")

# 2. Get samples only (filter out markers)
samples = [
    ts for ts in result['description_timestamps']
    if ts['is_sample'] and ts['confidence'] > 0.7
]

# 3. Download requested range (samples 1-3)
requested_samples = samples[0:3]  # Indices 0, 1, 2

for i, sample in enumerate(requested_samples, 1):
    print(f"Downloading sample {i}: {sample['description']}")

    # Calculate duration (until next timestamp or 30s default)
    next_sample = samples[i] if i < len(samples) else None
    duration = (
        next_sample['seconds'] - sample['seconds']
        if next_sample else 30
    )

    # Download segment
    filename = await download_youtube_segment(
        url=result['url'],
        start_time=sample['seconds'],
        duration=duration,
        output_name=f"sample_{i:02d}_{sanitize(sample['description'])}.wav"
    )

    print(f"  Saved: {filename}")
```

---

### Example 4: Handling No Timestamps Found

**Context:**
```
Video with no timestamps in description
```

**Robust Implementation:**
```python
def analyze_video(url: str) -> Dict:
    """Analyze video with fallback strategies."""

    extractor = TimestampExtractor()
    result = extractor.extract_from_url(url)

    # No timestamps found
    if result['total_timestamps'] == 0:
        print("No timestamps found in description.")
        print("Possible strategies:")
        print("1. Check comments for timestamps (community-added)")
        print("2. Download full video for manual chopping")
        print("3. Use audio analysis to detect sample boundaries")

        return {
            'status': 'no_timestamps',
            'suggestions': [
                'download_full_video',
                'check_comments',
                'use_audio_analysis'
            ]
        }

    # Few timestamps (might be section markers, not samples)
    elif result['total_timestamps'] < 3:
        samples = [
            ts for ts in result['description_timestamps']
            if ts['is_sample']
        ]

        if not samples:
            return {
                'status': 'no_samples_detected',
                'markers_found': result['total_timestamps'],
                'suggestion': 'Video may be single sample, not pack'
            }

    # Good number of timestamps
    return {
        'status': 'success',
        'timestamps': result['description_timestamps'],
        'sample_count': len([
            ts for ts in result['description_timestamps']
            if ts['is_sample']
        ])
    }
```

## Error Cases

### Common Errors and Handling

**1. Invalid URL**
```python
# Error: URL doesn't match YouTube patterns
# Raises: ValueError("Invalid YouTube URL")

# How to handle:
try:
    result = extractor.extract_from_url(user_url)
except ValueError as e:
    print(f"Invalid URL: {e}")
    print("YouTube URL should look like:")
    print("  - https://youtube.com/watch?v=VIDEO_ID")
    print("  - https://youtu.be/VIDEO_ID")
```

**2. Video Not Found**
```python
# Error: Video doesn't exist or is private
# Returns: result with empty timestamps

# How to handle:
if result['total_timestamps'] == 0:
    if not result.get('title'):
        print("Video not found or is private/deleted")
```

**3. No Description**
```python
# Video has no description text
# Returns: Empty description_timestamps list

# How to handle:
if not result['description_timestamps']:
    print("Video has no description.")
    print("Suggestions:")
    print("  - Check comments for timestamps")
    print("  - Download full video")
    print("  - Contact uploader")
```

**4. Ambiguous Timestamps**
```python
# Timestamps present but not clearly samples
Example: "0:00 Part 1", "1:00 Part 2"

# How to handle:
uncertain_samples = [
    ts for ts in timestamps
    if ts['confidence'] < 0.6
]

if uncertain_samples:
    print("Found timestamps but unclear if they're samples:")
    for ts in uncertain_samples:
        print(f"  {ts['timestamp']} - {ts['description']}")
    print("\nRecommend manual verification.")
```

## Heuristics

### When to Extract Timestamps

```xml
<heuristic id="timestamp_extraction_decision">
  <when>User provides YouTube URL</when>

  <consider>
    - Does video title contain "sample pack", "kit", "collection"?
    - Is video duration >2 minutes? (likely multiple samples)
    - Does description appear to have list format?
    - Is channel known for sample content?
  </consider>

  <generally>
    Extract timestamps if:
    - Title mentions "pack", "kit", "collection"
    - Duration >2 minutes
    - Description >100 characters (likely has details)
  </generally>

  <unless>
    - Video is <60 seconds (single sample)
    - Title is vague (no sample indicators)
    - URL is not from YouTube
  </unless>
</heuristic>
```

### Sample vs. Marker Classification

```xml
<heuristic id="sample_classification">
  <when>Timestamp extracted from text</when>

  <consider>
    - Does description contain sample indicators?
      (sample, loop, break, drum, bass, melody, sound)
    - Is it numbered? (#1, Sample 01, Track 1)
    - Does it describe musical content?
      (jazz piano, vintage drums, soul bassline)
  </consider>

  <generally>
    Mark as is_sample=True if:
    - Contains "sample", "loop", "break"
    - Numbered sequence pattern
    - Musical descriptors present
  </generally>

  <unless>
    - Generic markers: "intro", "outro", "thanks"
    - Non-musical: "download", "link", "subscribe"
    - Too vague: "next", "more", "part"
  </unless>
</heuristic>
```

## Integration Patterns

### Pattern 1: URL Analysis Flow
```
User provides URL
    ↓
timestamp_extractor.extract_from_url()
    ↓
Check total_timestamps
    ├─ 0 timestamps → Suggest full download
    ├─ 1-5 timestamps → Verify if samples or markers
    └─ 6+ timestamps → Likely sample pack, proceed
        ↓
    Filter is_sample=True with confidence >0.7
        ↓
    Present to user with options:
        - Download all
        - Download specific range
        - Download individual samples
```

### Pattern 2: Multi-Tool Workflow
```
youtube_search("lo-fi sample pack")
    ↓
Get top 3 results
    ↓
For each result:
    timestamp_extractor.extract_from_url(result['url'])
        ↓
    Count samples in each video
        ↓
Sort by sample count (most samples first)
    ↓
Present best video to user
```

### Pattern 3: Download Automation
```
timestamp_extractor.extract_from_url(url)
    ↓
Filter samples (is_sample=True, confidence>0.7)
    ↓
For each sample:
    Calculate segment bounds (start → next timestamp)
        ↓
    download_youtube_segment(url, start, duration)
        ↓
    Save with descriptive filename
        ↓
    Add metadata to database
```

## Best Practices

### 1. Always Validate Timestamps
```python
# Check if timestamps are sequential
timestamps_sorted = sorted(timestamps, key=lambda x: x['seconds'])
if timestamps != timestamps_sorted:
    print("Warning: Timestamps not in order")

# Check for reasonable spacing (>5 seconds between samples)
for i in range(len(timestamps) - 1):
    gap = timestamps[i+1]['seconds'] - timestamps[i]['seconds']
    if gap < 5:
        print(f"Warning: Short gap between samples ({gap}s)")
```

### 2. Provide User Feedback
```python
# Show progress during extraction
print("Analyzing video...")
result = extractor.extract_from_url(url)

print(f"✓ Video: {result['title']}")
print(f"✓ Found {result['total_timestamps']} timestamps")

samples = [ts for ts in result['description_timestamps'] if ts['is_sample']]
print(f"✓ Detected {len(samples)} samples")
```

### 3. Handle Edge Cases
```python
# Video might have timestamps in comments, not description
if result['total_timestamps'] == 0:
    print("No timestamps in description. Checking comments...")
    # Check comments (if API available)

# Timestamps might be in unusual format
# Example: "Sample 1 (0:00)", "Sample 2 (1:30)"
# Extractor should handle multiple formats

# Some videos use chapters (YouTube feature)
# These appear differently than description timestamps
```

### 4. Cache Results
```python
# Extracting timestamps requires fetching metadata
# Cache results to avoid repeated API calls
cache_key = f"ts_extract:{video_id}"
if cache_key in cache:
    return cache[cache_key]

result = extractor.extract_from_url(url)
cache[cache_key] = result
cache.expire(cache_key, 86400)  # 24 hour TTL
```

## Performance Considerations

**Speed:**
- Typical extraction: <1 second (cached metadata)
- With metadata fetch: 1-3 seconds
- With comment parsing: 3-10 seconds

**Accuracy:**
- Description timestamps: ~95% accuracy
- Sample detection: ~85% accuracy (heuristic-based)
- Edge cases: Manual verification recommended

**Limitations:**
- Cannot detect samples not listed in description
- Relies on uploader providing timestamps
- Heuristics may misclassify edge cases

## Troubleshooting

### Problem: No Timestamps Detected
**Possible Causes:**
- Video description has no timestamps
- Timestamps in unusual format
- Timestamps in comments only

**Solutions:**
1. Check comments (if API available)
2. Try audio analysis to detect sample boundaries
3. Download full video for manual chopping

### Problem: Wrong Sample Classification
**Causes:**
- Generic descriptions ("Sample 1", "Track 2")
- Unusual naming conventions
- Markers confused with samples

**Solutions:**
```python
# Lower confidence threshold for ambiguous cases
all_timestamps = [
    ts for ts in result['description_timestamps']
    if ts['confidence'] > 0.5  # Lower from 0.7
]

# Manual review prompt
print("Some timestamps have low confidence:")
for ts in all_timestamps:
    if ts['confidence'] < 0.7:
        print(f"{ts['timestamp']} - {ts['description']}")
        print(f"  Confidence: {ts['confidence']}")
        print(f"  Is this a sample? (y/n)")
```

### Problem: Timestamp Gaps
**Causes:**
- Missing timestamps in sequence
- Uploader didn't list all samples

**Solutions:**
```python
# Detect gaps
timestamps_sorted = sorted(timestamps, key=lambda x: x['seconds'])
for i in range(len(timestamps_sorted) - 1):
    gap = timestamps_sorted[i+1]['seconds'] - timestamps_sorted[i]['seconds']
    if gap > 60:  # >1 minute gap
        print(f"Large gap detected: {gap}s between samples")
        print(f"  {timestamps_sorted[i]['timestamp']} → {timestamps_sorted[i+1]['timestamp']}")
        print("  Possible unlisted samples in between")
```

## Summary

**Key Takeaways:**
1. ✅ Use when user provides YouTube URL (not for general search)
2. ✅ Check `total_timestamps` before proceeding
3. ✅ Filter by `is_sample=True` and `confidence>0.7`
4. ✅ Handle case where no timestamps found gracefully
5. ✅ Validate timestamp sequence and spacing
6. ✅ Cache results to avoid repeated metadata fetches
7. ✅ Integrate with download tools for segment extraction

**This tool transforms long sample pack videos into organized, downloadable segments.**
