#!/usr/bin/env python3
"""
Clean duplicate tags from all samples.

This script:
1. Iterates through all samples in the database
2. Removes duplicate tags while preserving order
3. Updates all samples in PostgreSQL

Example issue fixed:
  Before: ["snare", "drum", "the-crate-vol5", "the-crate-vol5", "the-crate-vol5", ...]
  After:  ["snare", "drum", "the-crate-vol5"]

Run with: python scripts/clean_duplicate_tags.py
"""

import asyncio
import sys
import os
import logging
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models.sample import Sample
from app.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TagCleaner:
    """Clean duplicate tags from samples."""

    def __init__(self):
        self.engine = None
        self.async_session = None
        self.stats = {
            "total_processed": 0,
            "samples_with_duplicates": 0,
            "tags_removed": 0,
            "samples_updated": 0,
        }

    async def initialize(self):
        """Initialize database connection."""
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info(f"Connected to PostgreSQL: {settings.DATABASE_URL}")

    def clean_tags(self, tags: Optional[List[str]]) -> tuple:
        """
        Remove duplicate tags while preserving order.

        Returns:
            (cleaned_tags, num_removed)
        """
        if not tags:
            return tags, 0

        seen = set()
        cleaned = []
        removed = 0

        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                cleaned.append(tag)
            else:
                removed += 1

        return cleaned, removed

    async def process_sample(self, sample: Sample, session: AsyncSession) -> bool:
        """
        Process a single sample.

        Returns:
            True if sample was updated
        """
        self.stats["total_processed"] += 1

        if not sample.tags:
            return False

        original_count = len(sample.tags)
        cleaned_tags, removed_count = self.clean_tags(sample.tags)

        # Check if there were duplicates
        if removed_count > 0:
            self.stats["samples_with_duplicates"] += 1
            self.stats["tags_removed"] += removed_count

            # Update sample
            sample.tags = cleaned_tags

            try:
                await session.commit()
                logger.info(
                    f"[{self.stats['total_processed']}] {sample.title}: "
                    f"removed {removed_count} duplicate tags "
                    f"({original_count} → {len(cleaned_tags)} tags)"
                )
                self.stats["samples_updated"] += 1
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"  ✗ Failed to commit: {e}")
                return False
        else:
            logger.debug(f"[{self.stats['total_processed']}] {sample.title}: no duplicates")
            return False

    async def clean_all(self):
        """Process all samples."""
        logger.info("Starting tag cleanup...")
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
                if i % 500 == 0:
                    logger.info(f"Progress: {i}/{total} samples processed...")

        # Print summary
        logger.info("=" * 80)
        logger.info("Tag Cleanup Complete!")
        logger.info("=" * 80)
        logger.info(f"Total processed:       {self.stats['total_processed']}")
        logger.info(f"Samples with duplicates: {self.stats['samples_with_duplicates']}")
        logger.info(f"Total tags removed:    {self.stats['tags_removed']}")
        logger.info(f"Samples updated:       {self.stats['samples_updated']}")
        logger.info("=" * 80)

    async def cleanup(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()


async def main():
    """Main entry point."""
    cleaner = TagCleaner()

    try:
        await cleaner.initialize()
        await cleaner.clean_all()
    finally:
        await cleaner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
