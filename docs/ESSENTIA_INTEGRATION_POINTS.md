# Essentia Integration Points

**For Task 2.2 and Beyond**

This document outlines how to integrate Essentia into the existing codebase now that Task 2.1 (installation and setup) is complete.

---

## Available Utilities

### Import Pattern
```python
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from essentia.standard import MonoLoader, RhythmExtractor2013
    # Use Essentia
else:
    import librosa
    # Use librosa fallback
```

### Availability Functions
```python
from backend.app.utils.essentia_check import (
    ESSENTIA_AVAILABLE,          # bool: True if Essentia is available
    check_essentia_availability, # function: returns bool
    get_essentia_version,        # function: returns version string
    get_availability_status,     # function: returns detailed dict
)
```

---

## Integration Points

### 1. Audio Features Service
**File:** `backend/app/services/audio_features_service.py`

**Current Implementation:**
- Uses librosa for BPM detection
- Uses librosa for spectral analysis
- Returns AudioFeatures model

**Recommended Changes:**
```python
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from backend.app.services.essentia_service import EssentiaService

class AudioFeaturesService:
    def __init__(self):
        if ESSENTIA_AVAILABLE:
            self.essentia_service = EssentiaService()

    async def extract_bpm(self, audio_path: str) -> float:
        if ESSENTIA_AVAILABLE:
            return await self.essentia_service.extract_bpm(audio_path)
        else:
            # Existing librosa implementation
            return await self._extract_bpm_librosa(audio_path)
```

---

### 2. Create Essentia Service (Task 2.2)
**File:** `backend/app/services/essentia_service.py` (to be created)

**Recommended Structure:**
```python
from essentia.standard import MonoLoader, RhythmExtractor2013, KeyExtractor

class EssentiaService:
    def __init__(self):
        self.rhythm_extractor = RhythmExtractor2013()
        self.key_extractor = KeyExtractor()

    async def extract_bpm(self, audio_path: str) -> float:
        """Extract BPM using Essentia's RhythmExtractor2013."""
        pass

    async def extract_key(self, audio_path: str) -> dict:
        """Extract musical key using Essentia's KeyExtractor."""
        pass

    async def analyze_audio(self, audio_path: str) -> dict:
        """Complete audio analysis using Essentia."""
        pass
```

---

### 3. Configuration
**File:** `backend/app/core/config.py`

**Add Settings:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...

    # Audio Analysis Settings
    USE_ESSENTIA: bool = True  # Auto-detect if not set
    ESSENTIA_BPM_METHOD: str = "multifeature"  # Options: multifeature, percival, degara

    @property
    def essentia_available(self) -> bool:
        from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE
        return ESSENTIA_AVAILABLE and self.USE_ESSENTIA
```

---

### 4. Health Check Endpoint
**File:** `backend/app/api/v1/endpoints/public.py`

**Add Essentia Status:**
```python
from backend.app.utils.essentia_check import get_availability_status

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "essentia": get_availability_status(),
        # ... other health info
    }
```

---

### 5. Logging
**Recommended Pattern:**
```python
import logging
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

logger = logging.getLogger(__name__)

if ESSENTIA_AVAILABLE:
    logger.info("Using Essentia for high-accuracy audio analysis")
else:
    logger.info("Using librosa fallback for audio analysis")
```

---

## Feature Mapping

### BPM Detection
```python
# Essentia (95%+ accuracy)
from essentia.standard import RhythmExtractor2013
extractor = RhythmExtractor2013()
bpm, ticks, confidence, estimates, bpm_intervals = extractor(audio)

# Librosa (85-90% accuracy)
import librosa
tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
```

### Key Detection
```python
# Essentia (built-in)
from essentia.standard import KeyExtractor
key_extractor = KeyExtractor()
key, scale, strength = key_extractor(audio)

# Librosa (requires extra processing)
import librosa
chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)
# ... additional processing needed
```

### Spectral Analysis
```python
# Essentia
from essentia.standard import Spectrum, SpectralCentroid
spectrum = Spectrum()
spectral_centroid = SpectralCentroid()

# Librosa
import librosa
spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
```

---

## Testing Strategy

### Unit Tests
```python
import pytest
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

@pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
def test_essentia_bpm_extraction():
    # Test Essentia-specific functionality
    pass

def test_librosa_bpm_extraction():
    # Test librosa fallback (always runs)
    pass
```

### Integration Tests
```python
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

async def test_audio_analysis_with_essentia():
    if ESSENTIA_AVAILABLE:
        # Verify Essentia is used
        assert service.using_essentia is True
    else:
        # Verify fallback is used
        assert service.using_librosa is True
```

---

## Performance Monitoring

### Add Metrics
```python
import time
from backend.app.utils.essentia_check import ESSENTIA_AVAILABLE

async def analyze_sample(audio_path: str):
    start = time.time()

    if ESSENTIA_AVAILABLE:
        result = await essentia_service.analyze(audio_path)
        method = "essentia"
    else:
        result = await librosa_fallback.analyze(audio_path)
        method = "librosa"

    elapsed = time.time() - start
    logger.info(f"Audio analysis via {method} took {elapsed:.2f}s")

    return result
```

---

## Environment Variables

### Development (.env)
```bash
USE_ESSENTIA=true
ESSENTIA_BPM_METHOD=multifeature
LOG_LEVEL=INFO
```

### Production (.env.production)
```bash
USE_ESSENTIA=true
ESSENTIA_BPM_METHOD=multifeature
LOG_LEVEL=WARNING
```

### Docker (.env.docker)
```bash
# Essentia likely not available in Docker, will auto-fallback
USE_ESSENTIA=false
LOG_LEVEL=INFO
```

---

## Next Steps (Task 2.2)

1. **Create `backend/app/services/essentia_service.py`:**
   - Implement BPM extraction
   - Implement key detection
   - Implement spectral analysis
   - Add comprehensive error handling

2. **Update `backend/app/services/audio_features_service.py`:**
   - Add Essentia integration
   - Implement fallback logic
   - Add logging for which method is used

3. **Add Tests:**
   - Unit tests for Essentia service
   - Integration tests for fallback
   - Performance benchmarks

4. **Update Documentation:**
   - Add usage examples
   - Document performance differences
   - Update CHANGELOG.md

---

## Example Implementation (Task 2.2 Preview)

```python
# backend/app/services/essentia_service.py
from typing import Optional, Dict
from pathlib import Path
import logging

from essentia.standard import MonoLoader, RhythmExtractor2013, KeyExtractor

logger = logging.getLogger(__name__)

class EssentiaService:
    """High-accuracy audio analysis using Essentia."""

    def __init__(self, bpm_method: str = "multifeature"):
        self.bpm_method = bpm_method
        self.rhythm_extractor = RhythmExtractor2013(method=bpm_method)
        self.key_extractor = KeyExtractor()
        logger.info(f"Essentia service initialized with BPM method: {bpm_method}")

    def load_audio(self, audio_path: str) -> tuple:
        """Load audio file using Essentia."""
        loader = MonoLoader(filename=str(audio_path))
        audio = loader()
        return audio, loader.paramValue("sampleRate")

    def extract_bpm(self, audio_path: str) -> float:
        """Extract BPM using RhythmExtractor2013."""
        audio, sr = self.load_audio(audio_path)
        bpm, ticks, confidence, estimates, intervals = self.rhythm_extractor(audio)
        logger.info(f"BPM extracted: {bpm:.2f} (confidence: {confidence:.2f})")
        return float(bpm)

    def extract_key(self, audio_path: str) -> Dict[str, str]:
        """Extract musical key."""
        audio, sr = self.load_audio(audio_path)
        key, scale, strength = self.key_extractor(audio)
        return {
            "key": key,
            "scale": scale,
            "strength": float(strength)
        }

    def analyze(self, audio_path: str) -> Dict:
        """Complete audio analysis."""
        return {
            "bpm": self.extract_bpm(audio_path),
            "key_info": self.extract_key(audio_path),
            "method": "essentia"
        }
```

---

## Questions for Task 2.2

1. Should we cache Essentia extractors or create new instances?
2. Should BPM method be configurable per-request or global?
3. What level of detail should we log?
4. Should we expose Essentia confidence scores in the API?

---

**Ready to proceed with Task 2.2!**
