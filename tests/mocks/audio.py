"""
Mock audio data and utilities for testing.
"""

import numpy as np
from typing import Dict, Any, Tuple


class MockAudioData:
    """Generate mock audio data for testing."""
    
    @staticmethod
    def create_test_audio(duration: float = 1.0, sample_rate: int = 44100) -> np.ndarray:
        """Create mock audio data."""
        samples = int(duration * sample_rate)
        # Simple sine wave
        t = np.linspace(0, duration, samples)
        frequency = 440.0  # A4 note
        audio = np.sin(2 * np.pi * frequency * t)
        return audio
    
    @staticmethod
    def create_drum_pattern(bpm: float = 120.0, duration: float = 4.0) -> Dict[str, Any]:
        """Create mock drum pattern data."""
        beat_duration = 60.0 / bpm
        beats_per_bar = 4
        num_bars = int(duration / (beat_duration * beats_per_bar))
        
        # Mock onset times for drums
        kick_times = []
        snare_times = []
        hihat_times = []
        
        for bar in range(num_bars):
            bar_start = bar * beats_per_bar * beat_duration
            # Kick on 1 and 3
            kick_times.extend([bar_start, bar_start + 2 * beat_duration])
            # Snare on 2 and 4
            snare_times.extend([bar_start + beat_duration, bar_start + 3 * beat_duration])
            # Hi-hat on 8th notes
            for i in range(8):
                hihat_times.append(bar_start + i * beat_duration / 2)
        
        return {
            "kick_onsets": kick_times,
            "snare_onsets": snare_times,
            "hihat_onsets": hihat_times,
            "all_onsets": sorted(kick_times + snare_times + hihat_times)
        }
    
    @staticmethod
    def create_swing_pattern(
        base_bpm: float = 90.0,
        swing_percentage: float = 66.7,
        duration: float = 4.0
    ) -> Dict[str, Any]:
        """Create mock swing pattern data."""
        # Convert swing percentage to ratio
        # 50% = straight, 66.7% = triplet swing
        swing_ratio = swing_percentage / 100.0
        
        beat_duration = 60.0 / base_bpm
        eighth_straight = beat_duration / 2
        
        # Calculate swung eighth notes
        first_eighth = eighth_straight * 2 * swing_ratio
        second_eighth = eighth_straight * 2 * (1 - swing_ratio)
        
        onsets = []
        time = 0.0
        
        while time < duration:
            onsets.append(time)  # Downbeat
            onsets.append(time + first_eighth)  # Swung eighth
            time += first_eighth + second_eighth
        
        return {
            "onsets": onsets,
            "swing_ratio": swing_ratio,
            "actual_swing_percentage": swing_percentage,
            "timing_deviations": [0.0] * len(onsets)  # Mock perfect timing
        }


class MockFrequencyData:
    """Generate mock frequency analysis data."""
    
    @staticmethod
    def get_instrument_frequency_profile(instrument_type: str) -> Dict[str, float]:
        """Get typical frequency characteristics for instruments."""
        profiles = {
            "kick": {
                "spectral_centroid": 150.0,
                "spectral_bandwidth": 200.0,
                "spectral_rolloff": 500.0,
                "fundamental_freq": 60.0
            },
            "snare": {
                "spectral_centroid": 2500.0,
                "spectral_bandwidth": 3000.0,
                "spectral_rolloff": 8000.0,
                "fundamental_freq": 200.0
            },
            "bass": {
                "spectral_centroid": 250.0,
                "spectral_bandwidth": 300.0,
                "spectral_rolloff": 1000.0,
                "fundamental_freq": 80.0
            },
            "hihat": {
                "spectral_centroid": 6000.0,
                "spectral_bandwidth": 4000.0,
                "spectral_rolloff": 12000.0,
                "fundamental_freq": 0.0  # No clear fundamental
            },
            "pad": {
                "spectral_centroid": 1500.0,
                "spectral_bandwidth": 2000.0,
                "spectral_rolloff": 5000.0,
                "fundamental_freq": 440.0
            }
        }
        
        return profiles.get(instrument_type, {
            "spectral_centroid": 2000.0,
            "spectral_bandwidth": 1500.0,
            "spectral_rolloff": 4000.0,
            "fundamental_freq": 440.0
        })
    
    @staticmethod
    def get_era_frequency_characteristics(era: str) -> Dict[str, Any]:
        """Get typical frequency characteristics by era."""
        era_profiles = {
            "1950s-1960s": {
                "frequency_range": (50, 8000),  # Limited high frequencies
                "typical_rolloff": 6000.0,
                "noise_floor": -40,  # Higher noise floor
                "characteristics": ["warm", "limited_highs", "mono"]
            },
            "1970s": {
                "frequency_range": (40, 15000),
                "typical_rolloff": 12000.0,
                "noise_floor": -50,
                "characteristics": ["analog_warmth", "full_spectrum", "stereo"]
            },
            "1980s": {
                "frequency_range": (30, 18000),
                "typical_rolloff": 16000.0,
                "noise_floor": -60,
                "characteristics": ["bright", "digital_sheen", "wide_stereo"]
            },
            "1990s": {
                "frequency_range": (35, 16000),
                "typical_rolloff": 14000.0,
                "noise_floor": -55,
                "characteristics": ["filtered", "sampled", "compressed"]
            },
            "2000s-2010s": {
                "frequency_range": (20, 20000),
                "typical_rolloff": 18000.0,
                "noise_floor": -70,
                "characteristics": ["hyped", "loud", "digital_perfect"]
            }
        }
        
        return era_profiles.get(era, {
            "frequency_range": (20, 20000),
            "typical_rolloff": 15000.0,
            "noise_floor": -60,
            "characteristics": ["modern"]
        })


class MockKeyData:
    """Mock key detection data."""
    
    # Circle of fifths for key relationships
    KEYS = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]
    
    @staticmethod
    def get_key_from_index(index: int, mode: str = "major") -> str:
        """Get key name from circle of fifths index."""
        key = MockKeyData.KEYS[index % 12]
        return f"{key} {mode}"
    
    @staticmethod
    def get_related_keys(root_key: str) -> Dict[str, str]:
        """Get harmonically related keys."""
        # Simplified - just extract root note
        root = root_key.split()[0]
        try:
            index = MockKeyData.KEYS.index(root)
        except ValueError:
            index = 0
        
        return {
            "parallel": f"{root} {'minor' if 'major' in root_key else 'major'}",
            "relative": MockKeyData.get_key_from_index(index + 3, "minor" if "major" in root_key else "major"),
            "dominant": MockKeyData.get_key_from_index(index + 1, "major"),
            "subdominant": MockKeyData.get_key_from_index(index - 1, "major")
        }