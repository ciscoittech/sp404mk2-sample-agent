# SP404MK2 Sample Agent Troubleshooting Guide

This guide helps you resolve common issues with the SP404MK2 Sample Agent system.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Agent-Specific Issues](#agent-specific-issues)
4. [Performance Problems](#performance-problems)
5. [Database Issues](#database-issues)
6. [API and Network Issues](#api-and-network-issues)

---

## Installation Issues

### Problem: ModuleNotFoundError when importing agents
```
ModuleNotFoundError: No module named 'src.agents'
```

**Solution:**
```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/sp404mk2-sample-agent"
```

### Problem: Missing dependencies
```
ImportError: No module named 'pydantic_ai'
```

**Solution:**
```bash
# Install all requirements
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### Problem: FFmpeg not found
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

---

## Runtime Errors

### Problem: "No OPENROUTER_API_KEY found"
```
ValueError: OPENROUTER_API_KEY environment variable not set
```

**Solution:**
```bash
# Set environment variable
export OPENROUTER_API_KEY="your-api-key-here"

# Or create .env file
echo "OPENROUTER_API_KEY=your-api-key-here" > .env
```

### Problem: "TURSO_URL is not configured"
```
WARNING: TURSO_URL is not configured. Database features will be disabled.
```

**Solution:**
This is just a warning - the system works without a database. To enable database features:
```bash
export TURSO_URL="your-turso-url"
export TURSO_TOKEN="your-turso-token"
```

### Problem: Audio file not found
```
FileNotFoundError: [Errno 2] No such file or directory: 'sample.wav'
```

**Solution:**
- Use absolute paths instead of relative paths
- Verify file exists before processing
- Check file permissions

```python
import os
if os.path.exists(file_path):
    result = await analyze_groove([file_path])
```

---

## Agent-Specific Issues

### Conversational CLI Issues

**Problem: "Connection error" in chat interface**

Solution:
- Check internet connection
- Verify OpenRouter API key is valid
- Check OpenRouter service status

**Problem: Chat doesn't understand musical terms**

Solution:
- Be more specific with genre/era/artist references
- Use examples: "like DJ Premier" instead of "boom bap"
- Include BPM ranges when known

### Groove Analyst Issues

**Problem: Incorrect BPM detection**

Solution:
```python
# Use deep analysis for complex rhythms
result = await analyze_groove(
    file_paths=["complex_rhythm.wav"],
    analysis_depth="deep"
)

# For half/double time issues, check the groove_type
# It will indicate if BPM might be half or double
```

**Problem: Swing percentage seems wrong**

Solution:
- Ensure sample has clear rhythmic elements
- Samples shorter than 2 seconds may not analyze well
- Ambient or non-rhythmic samples will show 50% (straight)

### Era Expert Issues

**Problem: Wrong era detected**

Solution:
- Modern recreations of vintage sounds may confuse detection
- Check confidence score - low confidence means uncertain
- Provide genre context for better accuracy

```python
result = await analyze_era(
    file_paths=["sample.wav"],
    genre="soul"  # Helps narrow down era characteristics
)
```

### Sample Relationship Issues

**Problem: All compatibility scores are low**

Solution:
- Check if samples are in compatible formats
- Very short samples (<0.5s) may not analyze well
- Percussion-only samples won't have harmonic scores

**Problem: Harmonic analysis missing**

Solution:
- Drums and percussion don't have detectable keys
- Ensure samples have tonal content
- Check key detection confidence

### Organization Issues

**Problem: Files not being copied**

Solution:
```python
# Ensure copy_files=True (default)
result = await organize_samples(
    sample_paths,
    strategy="musical",
    copy_files=True  # Must be True to actually copy files
)
```

**Problem: SP-404 banks have empty slots**

Solution:
- Need enough samples to fill the template
- Check overflow folder for extra samples
- Some samples may not match any category

---

## Performance Problems

### Problem: Analysis taking too long

**Solutions:**

1. **Process in smaller batches**
```python
# Instead of analyzing 100 files at once
for i in range(0, len(all_files), 20):
    batch = all_files[i:i+20]
    await analyze_groove(batch)
```

2. **Use quick analysis mode**
```python
result = await analyze_groove(
    file_paths=samples,
    analysis_depth="quick"  # Faster but less detailed
)
```

3. **Disable compatibility analysis for large sets**
```python
result = await organize_samples(
    samples,
    analyze_relationships=False  # Skip compatibility checking
)
```

### Problem: High memory usage

**Solutions:**
- Process files sequentially instead of in parallel
- Clear cache between batches
- Use smaller audio files (downsample if needed)

---

## Database Issues

### Problem: Database connection errors

**Solution:**
The system works without a database. To completely disable database features:
```python
# Agents will automatically skip database operations
# No action needed - warnings can be ignored
```

### Problem: Database queries slow

**Solution:**
- Ensure Turso database is in a nearby region
- Use batch operations when possible
- Consider caching frequently accessed data

---

## API and Network Issues

### Problem: YouTube download fails

**Common causes and solutions:**

1. **Video is private/deleted**
   - Check if URL is accessible in browser
   - Try alternative videos

2. **yt-dlp outdated**
   ```bash
   pip install --upgrade yt-dlp
   ```

3. **Rate limiting**
   - Add delays between downloads
   - Use different search queries

### Problem: OpenRouter API errors

**Error: "Rate limit exceeded"**
```python
# Add delays between API calls
import asyncio
await asyncio.sleep(1)  # 1 second delay
```

**Error: "Invalid API key"**
- Check key is correctly set
- Verify key has sufficient credits
- Ensure no extra spaces in key

### Problem: Search returns no results

**Solutions:**
- Make search terms less specific
- Remove special characters from queries
- Try alternative spellings/terms

```python
# Instead of specific terms
"UK garage 2-step rhythm 138.5 BPM"

# Try broader search
"UK garage drums 130-140 BPM"
```

---

## Common Error Messages

### "Mock analysis - audio libraries not available"
This appears in test environments. Install audio libraries:
```bash
pip install librosa soundfile
```

### "No compatible samples found"
- Samples may be too different musically
- Try lowering compatibility threshold
- Check if samples have analyzable content

### "Unsupported audio format"
Supported formats: WAV, MP3, FLAC, M4A
```bash
# Convert using ffmpeg
ffmpeg -i input.ogg -c:a pcm_s16le output.wav
```

---

## Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific agent
from src.logging_config import AgentLogger
logger = AgentLogger("groove_analyst")
logger.setLevel(logging.DEBUG)
```

---

## Getting Help

1. **Check logs** in `data/logs/` directory
2. **Run test scripts** to verify individual components
3. **Create minimal reproducible example**
4. **Check GitHub issues** for similar problems
5. **Submit new issue** with:
   - Error message
   - Steps to reproduce
   - System information
   - Sample files (if applicable)

---

## Quick Fixes Checklist

- [ ] Environment variables set correctly
- [ ] All dependencies installed
- [ ] FFmpeg available in PATH
- [ ] Audio files exist and are readable
- [ ] Internet connection active
- [ ] API key has credits
- [ ] Using absolute file paths
- [ ] File formats are supported
- [ ] Sufficient disk space for output

---

*If you encounter an issue not covered here, please create a GitHub issue with details.*