# 🎛️ SP404MK2 Sample Agent - Command Reference

## 🚀 Quick Start
```bash
# Always activate environment first!
source venv/bin/activate
```

## 📀 Main Commands

### 1. Complete Pipeline (All Steps)
```bash
# Run full pipeline with default genres
python run_complete_pipeline.py

# Output: pipeline_output/
```

### 2. Genre-Specific Collections
```bash
# Soul samples collection
python run_soul_collection.py

# Quick soul collection (smaller files)
python run_soul_quick.py

# Test run (minimal samples)
python test_pipeline_quick.py
```

### 3. Individual Steps

#### Discovery Only (No Downloads)
```bash
# Discover samples with AI
python run_ai_discovery.py
```

#### Download Specific Samples
```bash
# Search and download from YouTube
python youtube_search_download.py

# Download single sample from URL
python download_single_sample.py
```

#### Analysis Tools
```bash
# Analyze downloaded samples
python analyze_downloaded_sample.py

# Convert and analyze specific file
python convert_and_analyze.py

# Analyze all existing downloads
python analyze_soul_downloads.py
```

## 📁 Output Locations

- **Downloads**: `[output_dir]/downloads/`
- **Organized by BPM**: `[output_dir]/organized/by_bpm/`
- **Organized by Key**: `[output_dir]/organized/by_key/`
- **Review Queues**: `[output_dir]/review_queue/`

## 🎨 Customize Genres

Edit any pipeline script to change genres:
```python
genres = [
    {"genre": "jazz", "style": "bebop", "count": 3, "bpm_range": (120, 180)},
    {"genre": "hip-hop", "style": "boom-bap", "count": 3, "bpm_range": (85, 95)},
    {"genre": "soul", "style": "funk", "count": 3, "bpm_range": (95, 115)},
    {"genre": "electronic", "style": "house", "count": 3, "bpm_range": (120, 128)}
]
```

## 🛠️ Troubleshooting

### Check Dependencies
```bash
# Python packages
pip list | grep -E "yt-dlp|librosa|openai"

# System tools
which ffmpeg  # Should show: /opt/homebrew/bin/ffmpeg
which yt-dlp  # Should show: .../venv/bin/yt-dlp
```

### View Logs
```bash
# Check recent downloads
ls -la downloads/

# View pipeline metadata
cat pipeline_output/pipeline_metadata_*.json | jq .
```

### Manual Operations
```bash
# Convert audio format
ffmpeg -i input.webm -acodec pcm_s16le -ar 44100 output.wav

# Download from YouTube URL
yt-dlp -x --audio-format wav "https://youtube.com/watch?v=VIDEO_ID"
```

## 💡 Pro Tips

1. **Limit API calls** to avoid rate limits:
   ```python
   max_downloads=5  # In pipeline.run()
   ```

2. **Filter by duration** to get shorter samples:
   ```python
   'match_filter': lambda info: info.get('duration', 0) < 300  # Under 5 min
   ```

3. **Check discovered samples** before downloading:
   ```bash
   python run_ai_discovery.py  # Review output first
   ```

4. **Organize existing files**:
   ```bash
   python analyze_soul_downloads.py  # Analyzes all downloaded files
   ```

## 🎵 Sample Types

The agent can discover:
- `drums` - Drum breaks and loops
- `bass` - Basslines
- `keys` - Piano, Rhodes, organs
- `melody` - Melodic loops
- `vocal` - Vocal samples
- `atmosphere` - Pads and textures
- `horns` - Brass sections

## 📊 Review Your Collection

After running any pipeline:
```bash
# Open the latest review queue
ls -t soul_analysis_output/review_queue/*.md | head -1 | xargs open

# Or manually browse
open soul_analysis_output/organized/by_bpm/
```

---

**Remember**: Always activate the virtual environment first!
```bash
source venv/bin/activate
```