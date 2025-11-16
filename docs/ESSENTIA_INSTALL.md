# Essentia Installation Guide

**Essentia** is a high-performance C++ library for audio analysis with Python bindings. It provides superior accuracy for BPM detection, key estimation, and genre classification compared to librosa alone.

---

## Table of Contents

- [Why Essentia?](#why-essentia)
- [Installation Methods](#installation-methods)
  - [macOS (Recommended)](#macos-recommended)
  - [Linux / Ubuntu](#linux--ubuntu)
  - [Docker](#docker)
  - [Windows (via WSL)](#windows-via-wsl)
- [Verification](#verification)
- [System Dependencies](#system-dependencies)
- [Troubleshooting](#troubleshooting)
- [Known Issues](#known-issues)
- [Fallback Behavior](#fallback-behavior)

---

## Why Essentia?

Essentia provides research-grade audio analysis with significant advantages:

- **BPM Detection**: More accurate than librosa's beat tracking
- **Multi-Feature Analysis**: Combines multiple algorithms for better results
- **Genre Classification**: Built-in classifiers trained on large datasets
- **Key Detection**: Harmonic analysis for musical key estimation
- **Performance**: Optimized C++ core with Python bindings

**Note**: Essentia is **optional**. The application will fall back to librosa if Essentia is not available.

---

## Installation Methods

### macOS (Recommended)

Essentia installs cleanly via pip on macOS:

```bash
# Using the project's virtual environment
source venv/bin/activate
pip install essentia

# Verify installation
python -c "from essentia.standard import MonoLoader, RhythmExtractor2013; print('Essentia installed successfully')"
```

**Requirements**:
- Python 3.9-3.13
- macOS 10.15+ (Catalina or later)
- Xcode Command Line Tools (for compilation)

**Install Xcode tools if needed**:
```bash
xcode-select --install
```

---

### Linux / Ubuntu

On Linux, Essentia requires system dependencies before installation:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libyaml-dev \
    libfftw3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libsamplerate0-dev \
    libtag1-dev \
    python3-dev \
    python3-numpy

# Install Essentia via pip
source venv/bin/activate
pip install essentia

# Verify installation
python -c "from essentia.standard import MonoLoader, RhythmExtractor2013; print('Essentia installed successfully')"
```

**Tested on**:
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Debian 11+

---

### Docker

**Current Status**: ⚠️ Essentia installation in Docker has compatibility issues with Python 3.11 build process.

The Dockerfile is configured to **gracefully fall back** to librosa if Essentia fails to install:

```bash
# Build the Docker image (will use librosa fallback)
docker-compose build

# Check if Essentia is available in the container
docker-compose run backend python -c "from backend.app.utils.essentia_check import get_availability_status; import json; print(json.dumps(get_availability_status(), indent=2))"
```

**System dependencies** (included in Dockerfile for when Essentia works):
- `build-essential`
- `libyaml-dev`
- `libfftw3-dev`
- `libavcodec-dev`, `libavformat-dev`, `libavutil-dev`
- `libsamplerate0-dev`
- `libtag1-dev`

**Workaround for Docker users**:
1. Use the Docker image with librosa fallback (recommended)
2. Use Docker with volume mount to local virtual environment
3. Run the application natively on macOS/Linux where Essentia works

**Note**: The application will automatically use librosa for audio analysis if Essentia is not available. Performance difference is minimal (< 1 second per sample).

---

### Windows (via WSL)

Essentia is not officially supported on native Windows. Use **WSL2** (Windows Subsystem for Linux):

1. **Install WSL2** with Ubuntu:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

2. **Inside WSL**, follow the [Linux installation steps](#linux--ubuntu) above

3. **Verify**:
   ```bash
   python -c "from essentia.standard import MonoLoader; print('Essentia available')"
   ```

---

## Verification

After installation, verify Essentia is working:

```bash
# Quick check
python -c "from backend.app.utils.essentia_check import check_essentia_availability; print('Available:', check_essentia_availability())"

# Detailed status
python -c "from backend.app.utils.essentia_check import get_availability_status; import json; print(json.dumps(get_availability_status(), indent=2))"
```

**Expected output**:
```json
{
  "available": true,
  "version": "2.1-beta6-dev",
  "features": [
    "MonoLoader",
    "RhythmExtractor2013",
    "KeyExtractor",
    "TonalExtractor"
  ]
}
```

---

## System Dependencies

Essentia depends on several C/C++ libraries:

| Library | Purpose | Required For |
|---------|---------|--------------|
| `libfftw3` | Fast Fourier Transform | Spectral analysis |
| `libavcodec`, `libavformat`, `libavutil` | FFmpeg libraries | Audio decoding |
| `libsamplerate` | Sample rate conversion | Audio resampling |
| `libtag` | Metadata reading | ID3 tags |
| `libyaml` | YAML parsing | Configuration |
| `build-essential` | Compilation tools | Building from source |

**Install on Ubuntu/Debian**:
```bash
sudo apt-get install build-essential libyaml-dev libfftw3-dev \
    libavcodec-dev libavformat-dev libavutil-dev \
    libsamplerate0-dev libtag1-dev
```

**Install on macOS** (via Homebrew):
```bash
brew install fftw ffmpeg libsamplerate libyaml taglib
```

---

## Troubleshooting

### Issue: Import Error on macOS

**Symptom**:
```
ImportError: dlopen(...): Library not loaded: @rpath/libessentia.dylib
```

**Solution**:
```bash
# Reinstall with dependencies
pip uninstall essentia
brew install fftw ffmpeg
pip install --no-cache-dir essentia
```

---

### Issue: Build Fails on Linux

**Symptom**:
```
error: command 'gcc' failed with exit status 1
```

**Solution**:
```bash
# Install missing build dependencies
sudo apt-get install build-essential python3-dev
pip install --upgrade pip setuptools wheel
pip install essentia
```

---

### Issue: FFmpeg Libraries Not Found

**Symptom**:
```
error: libavcodec not found
```

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install libavcodec-dev libavformat-dev libavutil-dev

# macOS
brew install ffmpeg
```

---

### Issue: Docker Build Fails

**Symptom**:
```
ERROR: Could not build wheels for essentia
```

**Solution**:
Ensure all system dependencies are in the Dockerfile **before** `pip install`:

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    libyaml-dev \
    libfftw3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libsamplerate0-dev \
    libtag1-dev
```

---

### Issue: Version Mismatch

**Symptom**:
```
AttributeError: module 'essentia' has no attribute 'standard'
```

**Solution**:
```bash
# Uninstall and reinstall specific version
pip uninstall essentia
pip install essentia>=2.1b6.dev1110
```

---

## Known Issues

### 1. Python 3.13 Compatibility
- **Status**: ✅ Working (tested with 2.1-beta6-dev)
- **Note**: Requires `essentia>=2.1b6.dev1110`

### 2. ARM64 (Apple Silicon) Support
- **Status**: ✅ Working on macOS
- **Note**: Prebuilt wheels available for M1/M2/M3 Macs

### 3. Docker Build Failures
- **Status**: ⚠️ Known issue with Python 3.11
- **Reason**: Essentia's waf build system has compatibility issues
- **Solution**: Dockerfile automatically falls back to librosa
- **Alternative**: Run application natively where Essentia works

### 4. Alpine Linux (Docker)
- **Status**: ⚠️ Not recommended
- **Reason**: Essentia requires glibc (Alpine uses musl)
- **Solution**: Use `python:3.11-slim` (Debian-based) instead

### 5. Windows Native Support
- **Status**: ❌ Not supported
- **Workaround**: Use WSL2 with Ubuntu

---

## Fallback Behavior

The application is designed to work **with or without** Essentia:

1. **With Essentia**: Uses `RhythmExtractor2013` for high-accuracy BPM detection
2. **Without Essentia**: Falls back to `librosa.beat.beat_track()` for BPM estimation

**Example fallback code**:
```python
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from essentia.standard import MonoLoader, RhythmExtractor2013
    # Use Essentia for analysis
else:
    import librosa
    # Use librosa fallback
```

**Performance comparison**:
| Feature | Essentia | Librosa (Fallback) |
|---------|----------|-------------------|
| BPM Accuracy | 95%+ | 85-90% |
| Processing Time | 2-4s | 3-5s |
| Key Detection | Built-in | Requires `librosa-hpss` |
| Genre Classification | Built-in | Not available |

---

## Configuration

Set environment variables to control Essentia usage:

```bash
# Enable/disable Essentia (auto-detected by default)
USE_ESSENTIA=true

# BPM extraction method (when Essentia is available)
ESSENTIA_BPM_METHOD=multifeature  # Options: multifeature, percival, degara
```

Add to `.env`:
```bash
# Audio Analysis Settings
USE_ESSENTIA=true
ESSENTIA_BPM_METHOD=multifeature
```

---

## Additional Resources

- **Official Documentation**: https://essentia.upf.edu/documentation/
- **Installation Guide**: https://essentia.upf.edu/installing.html
- **GitHub Repository**: https://github.com/MTG/essentia
- **Python Tutorial**: https://essentia.upf.edu/python_tutorial.html

---

## Support

If you encounter issues not covered here:

1. Check the [Essentia GitHub Issues](https://github.com/MTG/essentia/issues)
2. Verify system dependencies are installed
3. Test with a fresh virtual environment
4. Use the application's fallback mode (librosa only)

**Remember**: Essentia is **optional** for this project. The application works perfectly fine with librosa alone.
