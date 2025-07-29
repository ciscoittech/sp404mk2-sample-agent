#!/usr/bin/env python3
"""Create test audio files for batch processing"""
import os
import sys
import wave
import struct
import math
import random

def create_drum_pattern(filename, bpm=120, duration=4, sample_rate=44100):
    """Create a simple drum pattern"""
    num_samples = int(sample_rate * duration)
    samples = []
    
    beat_duration = 60.0 / bpm  # Duration of one beat in seconds
    samples_per_beat = int(sample_rate * beat_duration)
    
    for i in range(num_samples):
        value = 0
        
        # Kick on 1 and 3
        if i % (samples_per_beat * 2) < 1000:
            value += int(20000 * math.sin(2 * math.pi * 60 * i / sample_rate))
        
        # Hi-hat on every 16th note
        if i % (samples_per_beat // 4) < 500:
            value += int(5000 * random.random())
        
        # Clamp value
        value = max(-32767, min(32767, value))
        samples.append(struct.pack('<h', value))
    
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(samples))

def create_bass_line(filename, key_freq=110, bpm=120, duration=4, sample_rate=44100):
    """Create a simple bass line"""
    num_samples = int(sample_rate * duration)
    samples = []
    
    notes = [1, 1.25, 0.75, 1.5]  # Relative frequencies
    beat_duration = 60.0 / bpm
    samples_per_beat = int(sample_rate * beat_duration)
    
    for i in range(num_samples):
        beat_index = (i // samples_per_beat) % len(notes)
        freq = key_freq * notes[beat_index]
        
        # Add harmonics for richer sound
        value = int(15000 * math.sin(2 * math.pi * freq * i / sample_rate))
        value += int(5000 * math.sin(4 * math.pi * freq * i / sample_rate))
        
        # Apply envelope
        envelope = min(1.0, (i % samples_per_beat) / 1000.0)
        value = int(value * envelope)
        
        samples.append(struct.pack('<h', value))
    
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(samples))

def create_synth_pad(filename, base_freq=220, duration=4, sample_rate=44100):
    """Create an ambient synth pad"""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # Multiple oscillators with slight detuning
        value = 0
        for detune in [0.99, 1.0, 1.01]:
            value += math.sin(2 * math.pi * base_freq * detune * t)
            value += 0.3 * math.sin(2 * math.pi * base_freq * 2 * detune * t)
        
        # LFO modulation
        lfo = math.sin(2 * math.pi * 0.5 * t)
        value *= (0.8 + 0.2 * lfo)
        
        # Normalize and convert
        value = int(8000 * value)
        samples.append(struct.pack('<h', value))
    
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(samples))

# Create test batch collection
output_dir = "/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/test_batch_collection"

test_files = [
    ("funky_drums_120bpm.wav", lambda f: create_drum_pattern(f, bpm=120)),
    ("trap_drums_140bpm.wav", lambda f: create_drum_pattern(f, bpm=140)),
    ("slow_drums_90bpm.wav", lambda f: create_drum_pattern(f, bpm=90)),
    ("deep_bass_Bb.wav", lambda f: create_bass_line(f, key_freq=116.54)),
    ("groovy_bass_C.wav", lambda f: create_bass_line(f, key_freq=130.81)),
    ("ambient_pad_D.wav", lambda f: create_synth_pad(f, base_freq=293.66)),
    ("warm_pad_F.wav", lambda f: create_synth_pad(f, base_freq=349.23)),
    ("ethereal_pad_A.wav", lambda f: create_synth_pad(f, base_freq=440)),
]

print("Creating test batch collection...")
for filename, create_func in test_files:
    filepath = os.path.join(output_dir, filename)
    print(f"  Creating {filename}...")
    create_func(filepath)

print(f"\nCreated {len(test_files)} test audio files in:")
print(f"  {output_dir}")
print("\nYou can now use this directory for batch processing!")