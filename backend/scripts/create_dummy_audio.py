#!/usr/bin/env python3
"""Create dummy audio files for demo samples"""
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
    ("8ca78d8e-1275-42d3-88be-09d23987d022.wav", 220),  # Vintage Jazz Drums - A3
    ("f884a720-6851-47b6-9506-70dc158e635c.wav", 330),  # Trap Hi-Hats - E4
    ("7edef989-083b-44bf-a1ac-06bcc36d6066.wav", 262),  # Soul Piano Chord - C4
    ("30709a1c-e550-4e55-901f-98e77a89f0e1.wav", 110),  # Boom Bap Kick - A2
    ("4432225d-f69c-4e94-9a0c-39c947c966db.wav", 294),  # Ambient Pad - D4
]

# Create dummy audio files
upload_dir = "/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/backend/uploads/2"

for filename, freq in samples:
    filepath = os.path.join(upload_dir, filename)
    print(f"Creating {filename} with frequency {freq}Hz...")
    create_sine_wave(filepath, frequency=freq)

print("\nDummy audio files created successfully!")