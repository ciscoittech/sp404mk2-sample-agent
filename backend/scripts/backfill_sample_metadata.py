#!/usr/bin/env python3
"""
Backfill missing sample metadata (file_size and duration).

This script:
1. Iterates through all samples in the database
2. Sets file_size from actual file on disk
3. Re-runs audio analysis to populate duration, BPM, key if missing
4. Updates all fields in PostgreSQL

Run with: python scripts/backfill_sample_metadata.py
"""

import asyncio
import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker

from app.models.sample import Sample
from app.services.audio_features_service import AudioFeaturesService
from app.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetadataBackfiller:
    """Backfill missing sample metadata."""

    def __init__(self):
        self.engine = None
        self.async_session = None
        self.audio_service = AudioFeaturesService()
        self.stats = {
            "total_processed": 0,
            "file_size_updated": 0,
            "duration_added": 0,
            "bpm_added": 0,
            "key_added": 0,
            "files_not_found": 0,
            "analysis_failed": 0,
        }

    async def initialize(self):
        """Initialize database connection."""
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info(f"Connected to PostgreSQL: {settings.DATABASE_URL}")

    async def get_all_samples(self) -> list:
        """Get all samples from database."""
        async with self.async_session() as session:
            result = await session.execute(select(Sample))
            return result.scalars().all()

    async def process_sample(self, sample: Sample, session: AsyncSession):
        """Process a single sample."""
        self.stats["total_processed"] += 1
        file_path = Path(sample.file_path)

        # Check if file exists on disk
        if not file_path.exists():
            logger.warning(f"[{self.stats['total_processed']}] File not found: {file_path}")
            self.stats["files_not_found"] += 1
            return

        # 1. Set file_size if missing
        if sample.file_size is None:
            try:
                file_size = file_path.stat().st_size
                sample.file_size = file_size
                self.stats["file_size_updated"] += 1
                logger.debug(f"  ✓ file_size: {file_size} bytes")
            except Exception as e:
                logger.error(f"  ✗ Failed to get file_size: {e}")

        # 2. Run audio analysis if duration is missing
        if sample.duration is None or sample.bpm is None or sample.musical_key is None:
            try:
                logger.debug(f"  → Running audio analysis...")
                features = await self.audio_service.analyze_file(file_path)

                # Update sample with audio features
                if features.duration_seconds is not None:
                    sample.duration = features.duration_seconds
                    self.stats["duration_added"] += 1
                    logger.debug(f"  ✓ duration: {features.duration_seconds:.2f}s")

                if features.bpm is not None:
                    sample.bpm = features.bpm
                    self.stats["bpm_added"] += 1
                    logger.debug(f"  ✓ bpm: {features.bpm:.1f}")

                if features.key is not None:
                    sample.musical_key = features.key
                    self.stats["key_added"] += 1
                    logger.debug(f"  ✓ key: {features.key}")

            except Exception as e:
                self.stats["analysis_failed"] += 1
                logger.warning(f"  ✗ Audio analysis failed: {str(e)[:100]}")

        # 3. Commit changes
        try:
            await session.commit()
            logger.info(
                f"[{self.stats['total_processed']}] Updated: {sample.title} "
                f"(size={sample.file_size}, duration={sample.duration})"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"  ✗ Failed to commit: {e}")

    async def backfill_all(self):
        """Process all samples."""
        logger.info("Starting metadata backfill...")
        logger.info("=" * 80)

        async with self.async_session() as session:
            # Get all samples
            result = await session.execute(select(Sample))
            samples = result.scalars().all()
            total = len(samples)

            logger.info(f"Processing {total} samples...")
            logger.info("=" * 80)

            # Process each sample
            for i, sample in enumerate(samples, 1):
                try:
                    await self.process_sample(sample, session)
                except Exception as e:
                    logger.error(f"[{i}] Unexpected error: {e}")
                    await session.rollback()

                # Progress indicator
                if i % 100 == 0:
                    logger.info(f"Progress: {i}/{total} samples processed...")

        # Print summary
        logger.info("=" * 80)
        logger.info("Backfill Complete!")
        logger.info("=" * 80)
        logger.info(f"Total processed:     {self.stats['total_processed']}")
        logger.info(f"File sizes updated:  {self.stats['file_size_updated']}")
        logger.info(f"Durations added:     {self.stats['duration_added']}")
        logger.info(f"BPMs added:          {self.stats['bpm_added']}")
        logger.info(f"Keys added:          {self.stats['key_added']}")
        logger.info(f"Files not found:     {self.stats['files_not_found']}")
        logger.info(f"Analysis failures:   {self.stats['analysis_failed']}")
        logger.info("=" * 80)

    async def cleanup(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()


async def main():
    """Main entry point."""
    backfiller = MetadataBackfiller()

    try:
        await backfiller.initialize()
        await backfiller.backfill_all()
    finally:
        await backfiller.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
