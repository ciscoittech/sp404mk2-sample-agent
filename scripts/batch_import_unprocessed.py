#!/usr/bin/env python
"""
Batch import unprocessed audio files into the database.
Creates sample records for all files not yet in the database.
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import json


def batch_import_unprocessed():
    """Import all unprocessed audio files into the database."""

    # Get all audio files on disk
    audio_extensions = {'.wav', '.mp3', '.aiff', '.flac', '.ogg', '.m4a'}
    audio_files = {}

    print("🔍 Scanning samples directory...")
    for root, dirs, files in os.walk('samples'):
        for f in files:
            if Path(f).suffix.lower() in audio_extensions:
                rel_path = os.path.join(root, f)
                abs_path = os.path.abspath(rel_path)
                normalized = os.path.normpath(abs_path)
                audio_files[f] = normalized

    print(f"✓ Found {len(audio_files)} audio files on disk")

    # Get all files in database - use direct sqlite file path
    db_file = 'backend/sp404_samples.db'
    if not os.path.exists(db_file):
        print(f"❌ Database file not found at {db_file}")
        return []

    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    cursor.execute('SELECT file_path, id FROM samples')
    db_samples_data = cursor.fetchall()
    db.close()
    db_samples = {os.path.normpath(os.path.abspath(p)): sid for p, sid in db_samples_data}

    # SQLite direct case
    db_filenames = {os.path.basename(p) for p in db_samples.keys()}

    disk_filenames = set(audio_files.keys())
    unprocessed_filenames = disk_filenames - db_filenames

    print(f"✓ Found {len(db_filenames)} samples in database")
    print(f"✓ Found {len(unprocessed_filenames)} unprocessed files")

    if len(unprocessed_filenames) == 0:
        print("\n✓ All files are already in the database!")
        return

    # Create unprocessed list for batch processing
    unprocessed_files = []
    for filename in sorted(unprocessed_filenames):
        unprocessed_files.append({
            'filename': filename,
            'abs_path': audio_files[filename],
            'rel_path': os.path.relpath(audio_files[filename], os.getcwd())
        })

    # Save to file for batch processing
    output_file = 'scripts/batch_automation/unprocessed_files.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump({
            'total_count': len(unprocessed_files),
            'discovered_at': datetime.now().isoformat(),
            'files': unprocessed_files
        }, f, indent=2)

    print(f"\n✓ Saved {len(unprocessed_files)} unprocessed files to {output_file}")
    print(f"\nNext steps:")
    print(f"1. Review the unprocessed files list")
    print(f"2. Run batch import:")
    print(f"   ./venv/bin/python scripts/batch_import_samples.py --input scripts/batch_automation/unprocessed_files.json")
    print(f"3. Generate audio analysis:")
    print(f"   ./venv/bin/python backend/scripts/analyze_samples.py --all")
    print(f"4. Generate embeddings:")
    print(f"   ./venv/bin/python backend/scripts/generate_embeddings.py --all")

    return unprocessed_files


if __name__ == '__main__':
    batch_import_unprocessed()
