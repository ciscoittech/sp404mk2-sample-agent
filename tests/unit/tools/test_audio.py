"""
Unit tests for Audio Tools.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path
import os

from src.tools.audio import (
    detect_bpm,
    detect_key,
    analyze_frequency_content,
    get_duration,
    convert_format,
    normalize_audio,
    create_fingerprint,
    trim_silence
)


class TestAudioFunctions:
    """Test suite for Audio Functions."""
    
    @pytest.fixture
    def mock_audio_file(self, temp_output_dir):
        """Create a mock audio file path."""
        return str(temp_output_dir / "test_audio.wav")
    
    @patch('librosa.load')
    @patch('librosa.beat.beat_track')
    def test_detect_bpm(self, mock_beat_track, mock_load):
        """Test BPM detection."""
        # Mock librosa functions
        mock_load.return_value = (np.random.rand(44100), 44100)  # 1 second of audio
        mock_beat_track.return_value = (90.0, np.array([0, 0.5, 1.0, 1.5]))
        
        result = detect_bpm("test.wav")
        
        assert result["bpm"] == 90.0
        assert result["confidence"] > 0
        assert "beat_positions" in result
        mock_load.assert_called_once()
        mock_beat_track.assert_called_once()
    
    @patch('librosa.load')
    def test_get_duration(self, mock_load):
        """Test duration calculation."""
        # Mock 2 seconds of audio at 44100 Hz
        mock_load.return_value = (np.random.rand(88200), 44100)
        
        duration = get_duration("test.wav")
        
        assert duration == pytest.approx(2.0, 0.01)
        mock_load.assert_called_once()
    
    @patch('librosa.load')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_rolloff')
    @patch('librosa.feature.spectral_bandwidth')
    @patch('librosa.feature.rms')
    def test_analyze_frequency_content(self, mock_rms, mock_bandwidth, 
                                     mock_rolloff, mock_centroid, mock_load):
        """Test frequency content analysis."""
        # Mock audio and features
        mock_load.return_value = (np.random.rand(44100), 44100)
        mock_centroid.return_value = np.array([[1500.0]])
        mock_rolloff.return_value = np.array([[4000.0]])
        mock_bandwidth.return_value = np.array([[2000.0]])
        mock_rms.return_value = np.array([[0.5]])
        
        result = analyze_frequency_content("test.wav")
        
        assert "spectral_centroid" in result
        assert "spectral_rolloff" in result
        assert "spectral_bandwidth" in result
        assert "rms_energy" in result
        assert result["spectral_centroid"] == 1500.0
        mock_load.assert_called_once()
    
    @patch('librosa.load')
    @patch('librosa.feature.chroma_stft')
    def test_detect_key(self, mock_chroma, mock_load):
        """Test key detection."""
        # Mock audio and chroma features
        mock_load.return_value = (np.random.rand(44100), 44100)
        
        # Create chroma features with C major profile
        chroma = np.zeros((12, 100))
        chroma[0, :] = 1.0  # Strong C
        chroma[4, :] = 0.8  # Strong E
        chroma[7, :] = 0.8  # Strong G
        mock_chroma.return_value = chroma
        
        result = detect_key("test.wav")
        
        assert "key" in result
        assert "confidence" in result
        assert "scale" in result
        assert isinstance(result["key"], str)
        assert result["confidence"] >= 0 and result["confidence"] <= 1
        mock_load.assert_called_once()
    
    @patch('librosa.load')
    @patch('soundfile.write')
    def test_normalize_audio(self, mock_write, mock_load):
        """Test audio normalization."""
        # Mock audio with low amplitude
        audio = np.random.rand(44100) * 0.1
        mock_load.return_value = (audio, 44100)
        
        output_path = normalize_audio("input.wav", "output.wav", target_db=-3.0)
        
        assert output_path == "output.wav"
        mock_load.assert_called_once()
        mock_write.assert_called_once()
        
        # Check that audio was normalized
        written_audio = mock_write.call_args[0][1]
        assert np.max(np.abs(written_audio)) > np.max(np.abs(audio))
    
    @patch('librosa.load')
    def test_create_fingerprint(self, mock_load):
        """Test audio fingerprint creation."""
        # Mock consistent audio data
        np.random.seed(42)
        mock_load.return_value = (np.random.rand(44100), 44100)
        
        fingerprint = create_fingerprint("test.wav")
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA-256 hex digest length
        mock_load.assert_called_once()
        
        # Same file should produce same fingerprint
        fingerprint2 = create_fingerprint("test.wav")
        assert fingerprint == fingerprint2
    
    @patch('librosa.load')
    @patch('soundfile.write')
    @patch('librosa.effects.trim')
    def test_trim_silence(self, mock_trim, mock_write, mock_load):
        """Test silence trimming."""
        # Mock audio with silence
        audio = np.concatenate([
            np.zeros(1000),  # Leading silence
            np.random.rand(44100),  # Audio content
            np.zeros(1000)   # Trailing silence
        ])
        mock_load.return_value = (audio, 44100)
        mock_trim.return_value = (audio[1000:-1000], [1000, 45100])
        
        output_path = trim_silence("input.wav", "output.wav", top_db=20)
        
        assert output_path == "output.wav"
        mock_load.assert_called_once()
        mock_trim.assert_called_once()
        mock_write.assert_called_once()
    
    @patch('subprocess.run')
    def test_convert_format_success(self, mock_run):
        """Test successful format conversion."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        output_path = convert_format("input.wav", "output.mp3", "mp3")
        
        assert output_path == "output.mp3"
        mock_run.assert_called_once()
        assert "ffmpeg" in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_convert_format_failure(self, mock_run):
        """Test format conversion failure."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error")
        
        with pytest.raises(RuntimeError):
            convert_format("input.wav", "output.mp3", "mp3")
    
    def test_error_handling(self):
        """Test error handling for non-existent files."""
        with pytest.raises(Exception):
            detect_bpm("non_existent_file.wav")
        
        with pytest.raises(Exception):
            get_duration("non_existent_file.wav")
        
        with pytest.raises(Exception):
            analyze_frequency_content("non_existent_file.wav")


class TestAudioIntegration:
    """Integration tests for audio tools."""
    
    @pytest.fixture
    def sample_audio(self):
        """Create a simple sine wave for testing."""
        sr = 44100
        duration = 1.0
        frequency = 440.0  # A4
        t = np.linspace(0, duration, int(sr * duration))
        audio = np.sin(2 * np.pi * frequency * t)
        return audio, sr
    
    @patch('librosa.load')
    @patch('soundfile.write')
    def test_audio_processing_pipeline(self, mock_write, mock_load, sample_audio):
        """Test complete audio processing pipeline."""
        audio, sr = sample_audio
        mock_load.return_value = (audio, sr)
        
        # Test duration
        duration = get_duration("test.wav")
        assert duration == pytest.approx(1.0, 0.01)
        
        # Test frequency analysis
        with patch('librosa.feature.spectral_centroid') as mock_centroid:
            mock_centroid.return_value = np.array([[440.0]])
            result = analyze_frequency_content("test.wav")
            assert result["spectral_centroid"] == pytest.approx(440.0, rel=0.1)
        
        # Test normalization
        normalize_audio("test.wav", "normalized.wav")
        assert mock_write.called