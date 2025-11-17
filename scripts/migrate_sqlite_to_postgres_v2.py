#!/usr/bin/env python
"""
Migrate samples and embeddings from SQLite to PostgreSQL using ORM.
"""
import sqlite3
import sys
import asyncio
from datetime import datetime
import json

# Add backend to path
sys.path.insert(0, 'backend')

from app.models.sample import Sample
from app.models.sample_embedding import SampleEmbedding
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


def parse_datetime(dt_str):
    """Parse datetime string to datetime object."""
    if isinstance(dt_str, datetime):
        return dt_str
    if not dt_str:
        return None
    try:
        # Try ISO format first
        return datetime.fromisoformat(dt_str)
    except:
        # Try SQLite format
        try:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None


async def migrate_samples():
    """Migrate samples from SQLite to PostgreSQL."""

    # Connect to SQLite
    sqlite_db = sqlite3.connect('backend/sp404_samples.db')
    sqlite_db.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_db.cursor()

    # Get PostgreSQL connection info
    postgres_url = "postgresql+asyncpg://sp404_user:changeme123@localhost:5433/sp404_samples"

    print("🔄 Starting migration from SQLite to PostgreSQL (ORM version)...")
    print(f"  Source: SQLite (backend/sp404_samples.db)")
    print(f"  Target: PostgreSQL (localhost:5433/sp404_samples)")

    # Create async engine for PostgreSQL
    engine = create_async_engine(postgres_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # Get sample count
        sqlite_cursor.execute("SELECT COUNT(*) FROM samples")
        sample_count = sqlite_cursor.fetchone()[0]
        sqlite_cursor.execute("SELECT COUNT(*) FROM sample_embeddings WHERE vibe_vector IS NOT NULL")
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
            ORDER BY id
        """)

        samples_data = sqlite_cursor.fetchall()

        print(f"\n📥 Migrating {len(samples_data)} samples...")

        async with async_session() as session:
            # Batch insert samples
            inserted = 0
            for idx, row in enumerate(samples_data, 1):
                try:
                    # Create Sample object from row
                    sample = Sample(
                        id=row['id'],
                        user_id=row['user_id'],
                        title=row['title'],
                        file_path=row['file_path'],
                        file_size=row['file_size'],
                        duration=row['duration'],
                        bpm=row['bpm'],
                        musical_key=row['musical_key'],
                        genre=row['genre'],
                        tags=json.loads(row['tags']) if row['tags'] else None,
                        extra_metadata=json.loads(row['extra_metadata']) if row['extra_metadata'] else None,
                        created_at=parse_datetime(row['created_at']),
                        analyzed_at=parse_datetime(row['analyzed_at']),
                        last_accessed_at=parse_datetime(row['last_accessed_at']),
                        bpm_confidence=row['bpm_confidence'],
                        genre_confidence=row['genre_confidence'],
                        key_confidence=row['key_confidence'],
                        analysis_metadata=json.loads(row['analysis_metadata']) if row['analysis_metadata'] else None
                    )

                    # Check if sample exists and update or insert
                    existing = await session.get(Sample, sample.id)
                    if existing:
                        # Update existing sample
                        for key, value in sample.__dict__.items():
                            if not key.startswith('_'):
                                setattr(existing, key, value)
                    else:
                        # Add new sample
                        session.add(sample)

                    inserted += 1

                    if inserted % 500 == 0:
                        await session.commit()
                        print(f"  ✓ Migrated {inserted}/{len(samples_data)} samples")

                except Exception as e:
                    print(f"  ⚠ Error on sample {row['id']}: {str(e)}")
                    continue

            # Final commit
            await session.commit()
            print(f"  ✓ Migrated all {inserted} samples")

        # Migrate embeddings
        sqlite_cursor.execute("""
            SELECT sample_id, vibe_vector FROM sample_embeddings
            WHERE vibe_vector IS NOT NULL
            ORDER BY sample_id
        """)

        embeddings_data = sqlite_cursor.fetchall()
        print(f"\n📥 Migrating {len(embeddings_data)} embeddings...")

        async with async_session() as session:
            inserted = 0
            for idx, row in enumerate(embeddings_data, 1):
                try:
                    sample_id = row['sample_id']
                    vibe_vector_str = row['vibe_vector']

                    # Parse vibe_vector (could be JSON string or vector)
                    if isinstance(vibe_vector_str, str):
                        try:
                            vibe_vector = json.loads(vibe_vector_str)
                        except:
                            vibe_vector = vibe_vector_str
                    else:
                        vibe_vector = vibe_vector_str

                    # Check if embedding exists
                    existing = await session.get(SampleEmbedding, sample_id)
                    if existing:
                        existing.vibe_vector = vibe_vector
                    else:
                        sample_embedding = SampleEmbedding(
                            sample_id=sample_id,
                            vibe_vector=vibe_vector
                        )
                        session.add(sample_embedding)

                    inserted += 1

                    if inserted % 500 == 0:
                        await session.commit()
                        print(f"  ✓ Migrated {inserted}/{len(embeddings_data)} embeddings")

                except Exception as e:
                    print(f"  ⚠ Error on embedding for sample {row['sample_id']}: {str(e)}")
                    continue

            # Final commit
            await session.commit()
            print(f"  ✓ Migrated all {inserted} embeddings")

        sqlite_db.close()

        # Verify migration
        async with async_session() as session:
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(Sample.id)))
            pg_sample_count = result.scalar()
            result = await session.execute(select(func.count(SampleEmbedding.sample_id)))
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
