#!/usr/bin/env python3
"""Initialize sample_embeddings table"""
import sqlite3
import sys

db_path = "backend/sp404_samples.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create sample_embeddings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sample_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER NOT NULL UNIQUE,
            vibe_vector TEXT,
            embedding_source VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sample_id) REFERENCES samples(id)
        )
    """)

    conn.commit()
    print("✅ sample_embeddings table created successfully")

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sample_embeddings'")
    if cursor.fetchone():
        print("✅ Table verified in database")

    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
