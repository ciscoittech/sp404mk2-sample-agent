#!/usr/bin/env python3
"""Fix sample_embeddings table to store vectors as JSON"""
import sqlite3
import json

db_path = "backend/sp404_samples.db"

try:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # Disable FK checks for migration
    cursor = conn.cursor()

    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS sample_embeddings")

    # Create sample_embeddings table with TEXT column for JSON vectors
    cursor.execute("""
        CREATE TABLE sample_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER NOT NULL UNIQUE,
            vibe_vector TEXT NOT NULL,
            embedding_source VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sample_id) REFERENCES samples(id)
        )
    """)

    conn.commit()
    print("✅ sample_embeddings table recreated with TEXT column for JSON vectors")

    # Verify
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sample_embeddings'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(sample_embeddings)")
        columns = cursor.fetchall()
        print("✅ Table columns:")
        for col in columns:
            print(f"   - {col[1]}: {col[2]}")

    conn.execute("PRAGMA foreign_keys = ON")  # Re-enable FK checks
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
