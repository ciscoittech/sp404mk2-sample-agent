#!/usr/bin/env python3
"""
Populate download metadata from existing sample files.

Scans /samples/mediafire/ directory and creates download records
for each file found on disk.
"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime

db_path = "backend/sp404_samples.db"
samples_dir = Path("samples/mediafire")

def populate_downloads():
    """Scan disk and create download metadata records."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if downloads table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='downloads'
    """)

    if not cursor.fetchone():
        print("⚠️  downloads table does not exist yet")
        # Create it
        cursor.execute("""
            CREATE TABLE downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path VARCHAR NOT NULL UNIQUE,
                platform VARCHAR DEFAULT 'mediafire',
                status VARCHAR DEFAULT 'pending_review',
                rating INTEGER,
                notes TEXT,
                reviewed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created downloads table")

    # Scan mediafire directory
    if not samples_dir.exists():
        print(f"❌ Directory not found: {samples_dir}")
        return

    sample_files = list(samples_dir.glob("**/*"))
    audio_files = [f for f in sample_files if f.is_file() and f.suffix.lower() in ['.wav', '.mp3', '.aiff', '.flac']]

    print(f"Found {len(audio_files)} audio files in {samples_dir}")

    # Insert downloads
    inserted = 0
    skipped = 0

    for audio_file in audio_files:
        relative_path = str(audio_file.relative_to(samples_dir.parent))

        try:
            cursor.execute("""
                INSERT INTO downloads (file_path, platform, status)
                VALUES (?, 'mediafire', 'pending_review')
            """, (relative_path,))
            inserted += 1
        except sqlite3.IntegrityError:
            # File already exists
            skipped += 1

    conn.commit()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM downloads")
    total = cursor.fetchone()[0]

    print(f"\n✅ Download Metadata Populated")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped (duplicate): {skipped}")
    print(f"   Total in database: {total}")

    conn.close()
    return total

if __name__ == "__main__":
    populate_downloads()
