"""Tests for AudioFeatures model sample_type field."""

import pytest
from pathlib import Path
from app.models.audio_features import AudioFeatures


class TestAudioFeaturesSampleType:
    """Test AudioFeatures model with sample_type field."""

    def test_create_with_sample_type_one_shot(self):
        """Test creating AudioFeatures with sample_type='one-shot'."""
        features = AudioFeatures(
            file_path=Path("/test/kick.wav"),
            duration_seconds=0.5,
            sample_rate=44100,
            bpm=120.0,
            sample_type="one-shot"
        )

        assert features.sample_type == "one-shot"

    def test_create_with_sample_type_loop(self):
        """Test creating AudioFeatures with sample_type='loop'."""
        features = AudioFeatures(
            file_path=Path("/test/beat_loop.wav"),
            duration_seconds=4.0,
            sample_rate=44100,
            bpm=90.0,
            sample_type="loop"
        )

        assert features.sample_type == "loop"

    def test_create_without_sample_type(self):
        """Test creating AudioFeatures without sample_type (should be None)."""
        features = AudioFeatures(
            file_path=Path("/test/sample.wav"),
            duration_seconds=2.0,
            sample_rate=44100,
            bpm=100.0
        )

        assert features.sample_type is None

    def test_to_dict_includes_sample_type(self):
        """Test that to_dict() includes sample_type field."""
        features = AudioFeatures(
            file_path=Path("/test/sample.wav"),
            duration_seconds=1.0,
            sample_rate=44100,
            sample_type="one-shot"
        )

        data = features.to_dict()
        assert "sample_type" in data
        assert data["sample_type"] == "one-shot"

    def test_from_dict_with_sample_type(self):
        """Test creating AudioFeatures from dict with sample_type."""
        data = {
            "file_path": "/test/sample.wav",
            "duration_seconds": 1.0,
            "sample_rate": 44100,
            "sample_type": "loop"
        }

        features = AudioFeatures.from_dict(data)
        assert features.sample_type == "loop"

    def test_from_dict_without_sample_type(self):
        """Test creating AudioFeatures from dict without sample_type."""
        data = {
            "file_path": "/test/sample.wav",
            "duration_seconds": 1.0,
            "sample_rate": 44100
        }

        features = AudioFeatures.from_dict(data)
        assert features.sample_type is None

    def test_sample_type_serialization_round_trip(self):
        """Test that sample_type survives serialization round trip."""
        original = AudioFeatures(
            file_path=Path("/test/sample.wav"),
            duration_seconds=1.5,
            sample_rate=44100,
            bpm=105.0,
            sample_type="loop"
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = AudioFeatures.from_dict(data)

        assert restored.sample_type == original.sample_type
        assert restored.sample_type == "loop"
