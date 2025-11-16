"""
Audio Features model for audio analysis results.

Provides structured storage for audio analysis features extracted by librosa,
including basic properties, spectral characteristics, and rhythm analysis.
"""
from pathlib import Path
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator


class AudioFeatures(BaseModel):
    """
    Audio analysis features extracted from audio files.

    Contains comprehensive audio characteristics including:
    - Basic properties (duration, sample rate, channels)
    - Rhythm features (BPM, key, scale)
    - Spectral features (centroid, rolloff, bandwidth)
    - Temporal features (zero crossing rate, RMS energy)
    """

    # File metadata
    file_path: Path = Field(..., description="Path to the audio file")

    # Basic audio properties
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz")
    num_channels: Optional[int] = Field(None, description="Number of audio channels")
    num_samples: Optional[int] = Field(None, description="Total number of samples")

    # Rhythm and musical features
    bpm: Optional[float] = Field(None, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key (C, C#, D, etc.)")
    scale: Optional[str] = Field(None, description="Scale type (major, minor)")
    sample_type: Optional[str] = Field(None, description="Sample type: 'one-shot' or 'loop'")
    genre: Optional[str] = Field(None, description="Detected genre/style")

    # Confidence scores (0-100 integer scale)
    bpm_confidence: Optional[int] = Field(None, ge=0, le=100, description="BPM detection confidence score (0-100)")
    genre_confidence: Optional[int] = Field(None, ge=0, le=100, description="Genre classification confidence score (0-100)")
    key_confidence: Optional[int] = Field(None, ge=0, le=100, description="Musical key detection confidence score (0-100)")

    # Spectral features
    spectral_centroid: Optional[float] = Field(None, description="Average spectral centroid")
    spectral_bandwidth: Optional[float] = Field(None, description="Average spectral bandwidth")
    spectral_rolloff: Optional[float] = Field(None, description="Average spectral rolloff")
    spectral_flatness: Optional[float] = Field(None, description="Average spectral flatness")

    # Temporal features
    zero_crossing_rate: Optional[float] = Field(None, description="Average zero crossing rate")
    rms_energy: Optional[float] = Field(None, description="Average RMS energy")

    # Harmonic/percussive features
    harmonic_ratio: Optional[float] = Field(None, description="Ratio of harmonic to percussive content")

    # MFCC features (Mel-frequency cepstral coefficients)
    mfcc_mean: Optional[list[float]] = Field(None, description="Mean MFCC values")
    mfcc_std: Optional[list[float]] = Field(None, description="Standard deviation of MFCC values")

    # Chroma features
    chroma_mean: Optional[list[float]] = Field(None, description="Mean chroma values")
    chroma_std: Optional[list[float]] = Field(None, description="Standard deviation of chroma values")

    # Additional metadata
    extraction_timestamp: Optional[str] = Field(None, description="ISO timestamp of feature extraction")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (analyzer used, confidence scores, etc.)")

    @field_validator('bpm')
    @classmethod
    def validate_bpm(cls, v: Optional[float]) -> Optional[float]:
        """Validate BPM is in reasonable range for music."""
        if v is not None and not (20 <= v <= 300):
            raise ValueError(f"BPM {v} outside reasonable range (20-300)")
        return v

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate musical key is a valid note."""
        if v is not None:
            valid_keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            if v not in valid_keys:
                raise ValueError(f"Key {v} not a valid note")
        return v

    @field_validator('scale')
    @classmethod
    def validate_scale(cls, v: Optional[str]) -> Optional[str]:
        """Validate scale is major or minor."""
        if v is not None and v not in ["major", "minor"]:
            raise ValueError(f"Scale {v} must be 'major' or 'minor'")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AudioFeatures to dictionary for JSON serialization.

        Converts Path objects to strings for database storage.

        Returns:
            Dictionary representation of audio features
        """
        data = self.model_dump()
        # Convert Path to string for JSON serialization
        if isinstance(data.get('file_path'), Path):
            data['file_path'] = str(data['file_path'])
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFeatures':
        """
        Create AudioFeatures from dictionary.

        Converts string paths back to Path objects.

        Args:
            data: Dictionary containing audio features

        Returns:
            AudioFeatures instance
        """
        # Convert string path back to Path object
        if 'file_path' in data and isinstance(data['file_path'], str):
            data['file_path'] = Path(data['file_path'])
        return cls(**data)

    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True  # Allow Path type


class AudioError(Exception):
    """
    Exception raised when audio analysis fails.

    Captures detailed information about the failure including the file path
    and the original exception that caused the error.
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[Path] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize AudioError.

        Args:
            message: Human-readable error message
            file_path: Path to the audio file that failed
            original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.file_path = file_path
        self.original_error = original_error

    def __str__(self) -> str:
        """Return formatted error message."""
        error_msg = f"AudioError: {self.message}"
        if self.file_path:
            error_msg += f" (file: {self.file_path})"
        if self.original_error:
            error_msg += f" - Original error: {type(self.original_error).__name__}: {self.original_error}"
        return error_msg
