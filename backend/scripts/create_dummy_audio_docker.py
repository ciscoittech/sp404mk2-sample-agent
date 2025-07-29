#!/usr/bin/env python3
"""Create dummy audio files for demo samples in Docker"""
import os
import struct
import wave
import math

def create_sine_wave(filename, frequency=440, duration=2.5, sample_rate=44100):
    """Create a simple sine wave audio file"""
    
    # Generate sine wave data
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        t = float(i) / sample_rate
        value = int(32767 * math.sin(2 * math.pi * frequency * t))
        samples.append(struct.pack('<h', value))  # 16-bit signed PCM
    
    # Write WAV file
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))

# Define samples with unique frequencies
samples = [
    (220, "warm"),     # A3 - Jazz
    (330, "sharp"),    # E4 - Trap
    (262, "soulful"),  # C4 - Soul
    (110, "punchy"),   # A2 - Boom Bap
    (294, "ethereal"), # D4 - Ambient
]

# Create dummy audio files for user 1
upload_dir = "/app/uploads/1"
os.makedirs(upload_dir, exist_ok=True)

# List all .wav files in the directory
existing_files = [f for f in os.listdir(upload_dir) if f.endswith('.wav')]

print(f"Found {len(existing_files)} existing audio files")

# Create dummy files if they don't exist
if len(existing_files) == 0:
    print("Creating dummy audio files...")
    for i, (freq, mood) in enumerate(samples):
        filename = f"sample_{i+1}_{mood}.wav"
        filepath = os.path.join(upload_dir, filename)
        create_sine_wave(filepath, frequency=freq)
        print(f"  Created {filename} ({freq}Hz)")
else:
    # Create files with the existing UUIDs if needed
    for wav_file in existing_files:
        filepath = os.path.join(upload_dir, wav_file)
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            # Determine frequency based on position
            idx = existing_files.index(wav_file)
            freq = samples[idx % len(samples)][0]
            print(f"Creating {wav_file} with frequency {freq}Hz...")
            create_sine_wave(filepath, frequency=freq)

print(f"\nAudio files ready in {upload_dir}")