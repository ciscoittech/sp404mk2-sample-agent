# Essentia Quick Start Guide

**TL;DR**: Essentia is optional, works great on macOS, falls back to librosa in Docker.

---

## Quick Install

### macOS (Recommended)
```bash
source venv/bin/activate
pip install essentia
```

### Linux
```bash
sudo apt-get install build-essential libyaml-dev libfftw3-dev \
    libavcodec-dev libavformat-dev libavutil-dev \
    libsamplerate0-dev libtag1-dev
pip install essentia
```

### Docker
```bash
docker-compose build  # Automatically falls back to librosa
```

---

## Quick Check

```bash
# Check if Essentia is available
python -c "from backend.app.utils.essentia_check import check_essentia_availability; print(check_essentia_availability())"

# Get detailed status
python -c "from backend.app.utils.essentia_check import get_availability_status; import json; print(json.dumps(get_availability_status(), indent=2))"
```

---

## Quick Usage

```python
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from essentia.standard import MonoLoader, RhythmExtractor2013
    # Use high-accuracy Essentia analysis
else:
    import librosa
    # Fall back to librosa
```

---

## Platform Status

| Platform | Status | Install Method | Notes |
|----------|--------|---------------|-------|
| macOS | ✅ Working | `pip install essentia` | Recommended |
| Linux | ✅ Working | System deps + pip | See above |
| Docker | ⚠️ Fallback | Auto (librosa) | Performance similar |
| Windows | ❌ Not supported | Use WSL2 | - |

---

## Troubleshooting

**Import Error on macOS:**
```bash
pip uninstall essentia
brew install fftw ffmpeg
pip install --no-cache-dir essentia
```

**Build fails on Linux:**
```bash
sudo apt-get install build-essential python3-dev
pip install essentia
```

**Docker issues:**
- Don't worry! The Dockerfile automatically falls back to librosa
- Performance difference is minimal (< 1 second per sample)

---

## Configuration

Add to your `.env`:
```bash
USE_ESSENTIA=true
ESSENTIA_BPM_METHOD=multifeature
```

---

## When to Use Essentia

**Use Essentia when:**
- Running on macOS or Linux natively
- Need highest BPM accuracy (+5-10%)
- Processing large batches for analysis
- Want built-in genre classification

**Use librosa fallback when:**
- Running in Docker
- On Windows without WSL
- Essentia installation fails
- Quick testing/development

---

## Performance Comparison

| Feature | Essentia | Librosa |
|---------|----------|---------|
| BPM Accuracy | 95%+ | 85-90% |
| Processing Time | 2-4s | 3-5s |
| Key Detection | Built-in | Requires extra |
| Genre Classification | Built-in | Not available |

---

## Full Documentation

See `docs/ESSENTIA_INSTALL.md` for complete installation guide, troubleshooting, and advanced configuration.
