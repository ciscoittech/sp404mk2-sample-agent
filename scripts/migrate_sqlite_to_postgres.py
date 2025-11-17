#!/usr/bin/env python
"""
Migrate samples and embeddings from SQLite to PostgreSQL.
"""
import sqlite3
import sys
import asyncio
from datetime import datetime

# Add backend to path
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


async def migrate_samples():
    """Migrate samples from SQLite to PostgreSQL."""

    # Connect to SQLite
    sqlite_db = sqlite3.connect('backend/sp404_samples.db')
    sqlite_cursor = sqlite_db.cursor()

    # Get PostgreSQL connection info
    postgres_url = "postgresql+asyncpg://sp404_user:changeme123@localhost:5433/sp404_samples"

    print("🔄 Starting migration from SQLite to PostgreSQL...")
    print(f"  Source: SQLite (backend/sp404_samples.db)")
    print(f"  Target: PostgreSQL (localhost:5433/sp404_samples)")

    # Create async engine for PostgreSQL
    engine = create_async_engine(postgres_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # Get sample count
        sqlite_cursor.execute("SELECT COUNT(*) FROM samples")
        sample_count = sqlite_cursor.fetchone()[0]
        sqlite_cursor.execute("SELECT COUNT(*) FROM sample_embeddings")
        embedding_count = sqlite_cursor.fetchone()[0]

        print(f"\n📊 Data to migrate:")
        print(f"  Samples: {sample_count}")
        print(f"  Embeddings: {embedding_count}")

        # Fetch all samples from SQLite
        sqlite_cursor.execute("""
            SELECT id, user_id, title, file_path, file_size, duration, bpm, musical_key,
                   genre, tags, extra_metadata, created_at, analyzed_at, last_accessed_at,
                   bpm_confidence, genre_confidence, key_confidence, analysis_metadata
            FROM samples
        """)

        samples = sqlite_cursor.fetchall()

        print(f"\n📥 Migrating {len(samples)} samples...")

        async with async_session() as session:
            # Batch insert samples
            inserted = 0
            for idx, sample in enumerate(samples, 1):
                try:
                    id_, user_id, title, file_path, file_size, duration, bpm, musical_key, \
                    genre, tags, extra_metadata, created_at, analyzed_at, last_accessed_at, \
                    bpm_confidence, genre_confidence, key_confidence, analysis_metadata = sample

                    # Build INSERT statement
                    insert_sql = """
                        INSERT INTO samples (
                            id, user_id, title, file_path, file_size, duration, bpm, musical_key,
                            genre, tags, extra_metadata, created_at, analyzed_at, last_accessed_at,
                            bpm_confidence, genre_confidence, key_confidence, analysis_metadata
                        ) VALUES (
                            :id, :user_id, :title, :file_path, :file_size, :duration, :bpm, :musical_key,
                            :genre, :tags, :extra_metadata, :created_at, :analyzed_at, :last_accessed_at,
                            :bpm_confidence, :genre_confidence, :key_confidence, :analysis_metadata
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            file_path = EXCLUDED.file_path,
                            file_size = EXCLUDED.file_size,
                            duration = EXCLUDED.duration,
                            bpm = EXCLUDED.bpm,
                            musical_key = EXCLUDED.musical_key,
                            genre = EXCLUDED.genre,
                            tags = EXCLUDED.tags,
                            extra_metadata = EXCLUDED.extra_metadata,
                            analyzed_at = EXCLUDED.analyzed_at,
                            last_accessed_at = EXCLUDED.last_accessed_at,
                            bpm_confidence = EXCLUDED.bpm_confidence,
                            genre_confidence = EXCLUDED.genre_confidence,
                            key_confidence = EXCLUDED.key_confidence,
                            analysis_metadata = EXCLUDED.analysis_metadata
                    """

                    await session.execute(text(insert_sql), {
                        'id': id_,
                        'user_id': user_id,
                        'title': title,
                        'file_path': file_path,
                        'file_size': file_size,
                        'duration': duration,
                        'bpm': bpm,
                        'musical_key': musical_key,
                        'genre': genre,
                        'tags': tags,
                        'extra_metadata': extra_metadata,
                        'created_at': created_at,
                        'analyzed_at': analyzed_at,
                        'last_accessed_at': last_accessed_at,
                        'bpm_confidence': bpm_confidence,
                        'genre_confidence': genre_confidence,
                        'key_confidence': key_confidence,
                        'analysis_metadata': analysis_metadata
                    })

                    inserted += 1

                    if inserted % 500 == 0:
                        await session.commit()
                        print(f"  ✓ Migrated {inserted}/{len(samples)} samples")

                except Exception as e:
                    print(f"  ⚠ Error on sample {id_}: {str(e)}")
                    continue

            # Final commit
            await session.commit()
            print(f"  ✓ Migrated all {inserted} samples")

        # Migrate embeddings
        sqlite_cursor.execute("""
            SELECT sample_id, embedding FROM sample_embeddings
        """)

        embeddings = sqlite_cursor.fetchall()
        print(f"\n📥 Migrating {len(embeddings)} embeddings...")

        async with async_session() as session:
            inserted = 0
            for idx, (sample_id, embedding) in enumerate(embeddings, 1):
                try:
                    insert_sql = """
                        INSERT INTO sample_embeddings (sample_id, embedding)
                        VALUES (:sample_id, :embedding)
                        ON CONFLICT (sample_id) DO UPDATE SET
                            embedding = EXCLUDED.embedding
                    """

                    await session.execute(text(insert_sql), {
                        'sample_id': sample_id,
                        'embedding': embedding
                    })

                    inserted += 1

                    if inserted % 500 == 0:
                        await session.commit()
                        print(f"  ✓ Migrated {inserted}/{len(embeddings)} embeddings")

                except Exception as e:
                    print(f"  ⚠ Error on embedding for sample {sample_id}: {str(e)}")
                    continue

            # Final commit
            await session.commit()
            print(f"  ✓ Migrated all {inserted} embeddings")

        sqlite_db.close()

        # Verify migration
        async with async_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM samples"))
            pg_sample_count = result.scalar()
            result = await session.execute(text("SELECT COUNT(*) FROM sample_embeddings"))
            pg_embedding_count = result.scalar()

        print(f"\n✅ Migration complete!")
        print(f"  PostgreSQL now has:")
        print(f"    - {pg_sample_count} samples")
        print(f"    - {pg_embedding_count} embeddings")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(migrate_samples())
    sys.exit(0 if success else 1)
