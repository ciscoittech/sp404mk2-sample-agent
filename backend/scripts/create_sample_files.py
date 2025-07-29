#!/usr/bin/env python3
"""Create audio files for samples in the database"""
import asyncio
import os
import sys
import struct
import wave
import math
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal

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

async def create_files_for_samples():
    """Create audio files for all samples in database"""
    async with AsyncSessionLocal() as db:
        # Get all samples
        result = await db.execute(
            text("SELECT id, file_path, genre FROM samples ORDER BY id")
        )
        samples = result.fetchall()
        
        # Define frequencies by genre
        genre_freqs = {
            "Jazz": 220,      # A3
            "Hip-Hop": 147,   # D3
            "Soul": 262,      # C4
            "Electronic": 294,# D4
        }
        
        created_count = 0
        for sample_id, file_path, genre in samples:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            
            # Check if file exists
            if not os.path.exists(file_path):
                # Get frequency based on genre or use default
                freq = genre_freqs.get(genre, 440)
                print(f"Creating {file_path} for {genre} sample (ID: {sample_id})...")
                create_sine_wave(file_path, frequency=freq)
                created_count += 1
        
        if created_count > 0:
            print(f"\n✅ Created {created_count} audio files")
        else:
            print("\n✅ All audio files already exist")

if __name__ == "__main__":
    asyncio.run(create_files_for_samples())