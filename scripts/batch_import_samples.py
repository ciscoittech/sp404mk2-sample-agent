#!/usr/bin/env python
"""
Batch import unprocessed files into the database as Sample records.
"""
import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def batch_import_samples(input_file=None):
    """Import samples from unprocessed files list into database."""

    if input_file is None:
        input_file = 'scripts/batch_automation/unprocessed_files.json'

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return 0

    # Load unprocessed files
    with open(input_file, 'r') as f:
        data = json.load(f)

    unprocessed_files = data.get('files', [])
    print(f"📂 Loading {len(unprocessed_files)} unprocessed files from {input_file}")

    # Connect to database
    db_file = 'backend/sp404_samples.db'
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    # Get default user (or create if needed)
    cursor.execute('SELECT id FROM users WHERE id = 1')
    user = cursor.fetchone()
    if not user:
        # Create default user
        cursor.execute(
            "INSERT INTO users (id, email, username, hashed_password, is_active) VALUES (1, 'system@local', 'system', '', 1)"
        )
        db.commit()
    user_id = 1

    # Import samples
    imported = 0
    failed = 0
    duplicates = 0

    print(f"📥 Importing samples...")

    for idx, file_info in enumerate(unprocessed_files, 1):
        try:
            filename = file_info.get('filename')
            file_path = file_info.get('abs_path')

            if not os.path.exists(file_path):
                print(f"  ⚠ Skipped (missing): {filename}")
                failed += 1
                continue

            # Get file size
            file_size = os.path.getsize(file_path)

            # Check if already exists
            cursor.execute(
                "SELECT id FROM samples WHERE file_path = ?",
                (file_path,)
            )
            if cursor.fetchone():
                duplicates += 1
                continue

            # Get file extension for title formatting
            title = os.path.splitext(filename)[0]

            # Insert sample
            cursor.execute("""
                INSERT INTO samples (
                    user_id, title, file_path, file_size, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                title,
                file_path,
                file_size,
                datetime.now().isoformat()
            ))

            imported += 1

            # Show progress every 500 samples
            if imported % 500 == 0:
                print(f"  ✓ Imported {imported} samples ({idx}/{len(unprocessed_files)})")

        except Exception as e:
            print(f"  ❌ Error importing {filename}: {str(e)}")
            failed += 1
            continue

    # Commit all changes
    db.commit()
    db.close()

    print(f"\n✅ Import complete:")
    print(f"  Imported: {imported}")
    print(f"  Duplicates: {duplicates}")
    print(f"  Failed: {failed}")
    print(f"  Total processed: {len(unprocessed_files)}")

    # Verify count
    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM samples")
    total_samples = cursor.fetchone()[0]
    db.close()

    print(f"\n📊 Database now contains {total_samples} total samples")

    return imported


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Batch import samples')
    parser.add_argument('--input', help='Input JSON file with unprocessed files')
    args = parser.parse_args()

    batch_import_samples(args.input)
