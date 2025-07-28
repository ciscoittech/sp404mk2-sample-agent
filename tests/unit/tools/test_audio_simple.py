"""
Simple unit tests for Audio Tools that match actual implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import os

from src.tools.audio import (
    detect_bpm,
    detect_key,
    analyze_frequency_content,
    get_duration
)


class TestAudioFunctions:
    """Test suite for Audio Functions."""
    
    @patch('os.path.exists', return_value=True)
    @patch('librosa.load')
    @patch('librosa.beat.beat_track')
    def test_detect_bpm(self, mock_beat_track, mock_load, mock_exists):
        """Test BPM detection."""
        # Mock librosa functions
        mock_load.return_value = (np.random.rand(44100), 44100)
        mock_beat_track.return_value = (90.0, np.array([0, 0.5, 1.0, 1.5]))
        
        result = detect_bpm("test.wav")
        
        assert result["bpm"] == 90.0
        assert result["confidence"] > 0
        assert "beat_positions" in result
    
    @patch('os.path.exists', return_value=True)
    @patch('librosa.load')
    def test_get_duration(self, mock_load, mock_exists):
        """Test duration calculation."""
        # Mock 2 seconds of audio at 44100 Hz
        mock_load.return_value = (np.random.rand(88200), 44100)
        
        duration = get_duration("test.wav")
        
        assert duration == pytest.approx(2.0, 0.01)
    
    @patch('os.path.exists', return_value=True)
    @patch('librosa.load')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_rolloff') 
    @patch('librosa.feature.spectral_bandwidth')
    @patch('librosa.feature.rms')
    def test_analyze_frequency_content(self, mock_rms, mock_bandwidth, 
                                     mock_rolloff, mock_centroid, mock_load, mock_exists):
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
    
    @patch('os.path.exists', return_value=True)
    @patch('librosa.load')
    @patch('librosa.feature.chroma_stft')
    def test_detect_key(self, mock_chroma, mock_load, mock_exists):
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
        assert 0 <= result["confidence"] <= 1
    
    def test_error_handling(self):
        """Test error handling for non-existent files."""
        # These should raise FileNotFoundError since os.path.exists isn't mocked
        with pytest.raises(FileNotFoundError):
            detect_bpm("non_existent_file.wav")
        
        with pytest.raises(FileNotFoundError):
            get_duration("non_existent_file.wav")
        
        with pytest.raises(FileNotFoundError):
            analyze_frequency_content("non_existent_file.wav")