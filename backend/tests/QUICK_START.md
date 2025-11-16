# Audio Features Service - Quick Start Guide

**For Coder Agent:** Fast reference for implementing the service to pass tests.

---

## What to Implement (3 Files)

### 1. Models: `backend/app/models/audio_features.py`

```python
"""Audio features models for librosa analysis."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AudioFeatures:
    """Audio analysis results from librosa."""

    file_path: Path
    duration_seconds: float
    bpm: Optional[float] = None
    key: Optional[str] = None
    spectral_centroid: Optional[float] = None
    spectral_rolloff: Optional[float] = None
    zero_crossing_rate: Optional[float] = None

    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage."""
        return {
            "file_path": str(self.file_path),
            "duration_seconds": self.duration_seconds,
            "bpm": self.bpm,
            "key": self.key,
            "spectral_centroid": self.spectral_centroid,
            "spectral_rolloff": self.spectral_rolloff,
            "zero_crossing_rate": self.zero_crossing_rate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AudioFeatures":
        """Deserialize from dict."""
        return cls(
            file_path=Path(data["file_path"]),
            duration_seconds=data["duration_seconds"],
            bpm=data.get("bpm"),
            key=data.get("key"),
            spectral_centroid=data.get("spectral_centroid"),
            spectral_rolloff=data.get("spectral_rolloff"),
            zero_crossing_rate=data.get("zero_crossing_rate"),
        )


class AudioError(Exception):
    """Exception for audio processing errors."""

    def __init__(
        self, message: str, file_path: Path, original_error: Exception = None
    ):
        self.message = message
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(message)
```

---

### 2. Service: `backend/app/services/audio_features_service.py`

```python
"""Audio features extraction service using librosa."""
import librosa
import numpy as np
from pathlib import Path

from app.models.audio_features import AudioFeatures, AudioError


class AudioFeaturesService:
    """Service for analyzing audio files using librosa."""

    async def analyze_file(self, file_path: Path) -> AudioFeatures:
        """
        Analyze audio file and extract musical features.

        Args:
            file_path: Path to audio file

        Returns:
            AudioFeatures with analysis results

        Raises:
            AudioError: If file cannot be analyzed
        """
        try:
            # Validate file exists
            if not file_path.exists():
                raise AudioError(
                    f"Audio file not found: {file_path}",
                    file_path
                )

            # Load audio
            y, sr = librosa.load(str(file_path), sr=None)

            # Extract duration
            duration = float(librosa.get_duration(y=y, sr=sr))

            # Extract BPM (may fail for some audio)
            bpm = None
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                bpm = float(tempo) if tempo > 0 else None
            except Exception:
                pass  # BPM detection failed, leave as None

            # Extract key (may be inaccurate for some audio)
            key = None
            try:
                chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
                key_index = int(np.argmax(np.sum(chroma, axis=1)))
                keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                key = keys[key_index]
            except Exception:
                pass  # Key detection failed, leave as None

            # Extract spectral features
            spectral_centroid = None
            spectral_rolloff = None
            zero_crossing_rate = None

            try:
                spectral_centroid = float(np.mean(
                    librosa.feature.spectral_centroid(y=y, sr=sr)
                ))
            except Exception:
                pass

            try:
                spectral_rolloff = float(np.mean(
                    librosa.feature.spectral_rolloff(y=y, sr=sr)
                ))
            except Exception:
                pass

            try:
                zero_crossing_rate = float(np.mean(
                    librosa.feature.zero_crossing_rate(y)
                ))
            except Exception:
                pass

            return AudioFeatures(
                file_path=file_path,
                duration_seconds=duration,
                bpm=bpm,
                key=key,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
            )

        except AudioError:
            raise  # Re-raise our custom errors

        except Exception as e:
            raise AudioError(
                f"Failed to analyze audio file: {str(e)}",
                file_path,
                original_error=e,
            )
```

---

### 3. Protocol: `backend/app/services/protocols/audio_features.py`

```python
"""Protocol for audio features service."""
from typing import Protocol
from pathlib import Path

from app.models.audio_features import AudioFeatures


class AudioFeaturesProtocol(Protocol):
    """Protocol for audio feature extraction services."""

    async def analyze_file(self, file_path: Path) -> AudioFeatures:
        """
        Analyze audio file and extract musical features.

        Args:
            file_path: Path to audio file

        Returns:
            AudioFeatures with analysis results
        """
        ...
```

---

## Run Tests

```bash
# From backend directory
cd backend

# Run all audio features tests
../venv/bin/python -m pytest tests/test_audio_features_service.py -v

# Expected output:
# test_analyze_real_wav_file PASSED
# test_invalid_file_raises_audio_error PASSED
# test_save_features_to_database PASSED
```

---

## Key Points

### Error Handling
- Wrap ALL exceptions in `AudioError`
- Re-raise `AudioError` as-is
- Include `original_error` for debugging

### Feature Extraction
- Duration: Must always succeed
- BPM: May be None (detection can fail)
- Key: May be None (detection can fail)
- Spectral: May be None (wrap in try/except)
- **Requirement:** At least 50% of features non-None

### Serialization
- `to_dict()`: Convert Path to string
- `from_dict()`: Convert string to Path
- Handle None values (JSON compatible)

---

## Test Expectations

### Test 1: Real WAV Analysis ✅
```python
features = await audio_service.analyze_file(test_wav_fixture)
assert isinstance(features, AudioFeatures)
assert 1.5 <= features.duration_seconds <= 2.5
# At least 50% features non-None
```

### Test 2: Error Handling ✅
```python
# Non-existent file
with pytest.raises(AudioError):
    await audio_service.analyze_file(non_existent)

# Corrupted file
with pytest.raises(AudioError):
    await audio_service.analyze_file(corrupted)
```

### Test 3: Database Round-Trip ✅
```python
features = await audio_service.analyze_file(test_wav_fixture)
sample = Sample(extra_metadata={"audio_features": features.to_dict()})
# Save, commit, query back
retrieved = AudioFeatures.from_dict(retrieved_sample.extra_metadata["audio_features"])
assert retrieved.bpm == features.bpm
```

---

## Dependencies

Already in `requirements.txt`:
- librosa
- numpy
- soundfile (or scipy)

---

**That's it! Copy these 3 files and tests should pass.** 🎉
