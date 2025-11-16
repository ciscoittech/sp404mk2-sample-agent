"""
Embedding Status Checker & Wait/Retry Logic

Validates embedding availability before vibe search tests and provides
intelligent wait/retry logic for embedding generation.

No mock data - checks real database state.
"""

import asyncio
import logging
import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Adjust import path as needed for your project
try:
    from backend.app.models import Sample, SampleEmbedding
except ImportError:
    from app.models import Sample, SampleEmbedding

logger = logging.getLogger(__name__)


class EmbeddingValidator:
    """Validates embedding availability and readiness for vibe search."""

    # Minimum samples needed for meaningful vibe search testing
    MINIMUM_EMBEDDINGS_FOR_TESTING = 30
    # Production-quality coverage threshold
    PRODUCTION_COVERAGE_THRESHOLD = 80
    # Wait timeout for embedding generation (5 minutes)
    DEFAULT_TIMEOUT_SECONDS = 300
    # Check interval (5 seconds)
    CHECK_INTERVAL_SECONDS = 5

    @staticmethod
    async def get_embedding_status(db: AsyncSession) -> dict:
        """
        Get current embedding coverage statistics.

        Returns:
            {
                'total_samples': int,
                'embedded_samples': int,
                'coverage_pct': float,
                'ready': bool (coverage >= MINIMUM_EMBEDDINGS_FOR_TESTING),
                'production_ready': bool (coverage >= PRODUCTION_COVERAGE_THRESHOLD),
                'samples_needed': int (for minimum)
            }
        """
        try:
            # Count total samples (active only)
            total_query = select(func.count(Sample.id)).where(
                Sample.deleted_at.is_(None)
            )
            total_result = await db.execute(total_query)
            total_samples = total_result.scalar() or 0

            # Count embedded samples
            embedded_query = select(func.count(SampleEmbedding.sample_id))
            embedded_result = await db.execute(embedded_query)
            embedded_samples = embedded_result.scalar() or 0

            # Calculate coverage
            coverage_pct = (
                (embedded_samples / total_samples * 100)
                if total_samples > 0
                else 0
            )

            # Calculate what's needed
            samples_needed = max(
                0,
                EmbeddingValidator.MINIMUM_EMBEDDINGS_FOR_TESTING - embedded_samples
            )

            return {
                'total_samples': total_samples,
                'embedded_samples': embedded_samples,
                'coverage_pct': round(coverage_pct, 1),
                'ready': embedded_samples >= EmbeddingValidator.MINIMUM_EMBEDDINGS_FOR_TESTING,
                'production_ready': coverage_pct >= EmbeddingValidator.PRODUCTION_COVERAGE_THRESHOLD,
                'samples_needed': samples_needed,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error checking embedding status: {e}")
            return {
                'error': str(e),
                'total_samples': 0,
                'embedded_samples': 0,
                'coverage_pct': 0.0,
                'ready': False,
                'production_ready': False,
                'samples_needed': EmbeddingValidator.MINIMUM_EMBEDDINGS_FOR_TESTING
            }

    @staticmethod
    async def wait_for_embeddings(
        db: AsyncSession,
        min_samples: Optional[int] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        check_interval: int = CHECK_INTERVAL_SECONDS,
        verbose: bool = True
    ) -> dict:
        """
        Wait for embeddings to be generated with retry logic.

        This function polls the database at regular intervals and waits
        for the minimum number of embeddings to be available. Useful in
        test setup to handle cases where embedding generation is still
        in progress.

        Args:
            db: AsyncSession database connection
            min_samples: Minimum embeddings needed (default: MINIMUM_EMBEDDINGS_FOR_TESTING)
            timeout_seconds: Maximum time to wait (default: 300 seconds)
            check_interval: Polling interval in seconds (default: 5)
            verbose: Log progress messages (default: True)

        Returns:
            {
                'success': bool,
                'embedded_count': int,
                'wait_time_seconds': int,
                'message': str,
                'final_status': dict (from get_embedding_status)
            }
        """
        if min_samples is None:
            min_samples = EmbeddingValidator.MINIMUM_EMBEDDINGS_FOR_TESTING

        start_time = time.time()
        last_count = 0
        last_log_time = start_time

        while time.time() - start_time < timeout_seconds:
            try:
                # Get current count
                query = select(func.count(SampleEmbedding.sample_id))
                result = await db.execute(query)
                current_count = result.scalar() or 0

                # Log progress at intervals
                if verbose and time.time() - last_log_time >= 10:
                    progress_pct = (current_count / min_samples * 100) if min_samples > 0 else 0
                    elapsed = int(time.time() - start_time)
                    logger.info(
                        f"Embedding progress: {current_count}/{min_samples} ({progress_pct:.0f}%) "
                        f"- elapsed: {elapsed}s"
                    )
                    last_log_time = time.time()

                # Check if we've reached minimum
                if current_count >= min_samples:
                    elapsed = int(time.time() - start_time)
                    final_status = await EmbeddingValidator.get_embedding_status(db)

                    if verbose:
                        logger.info(
                            f"Embeddings ready: {current_count} samples "
                            f"({final_status['coverage_pct']}% coverage) "
                            f"in {elapsed}s"
                        )

                    return {
                        'success': True,
                        'embedded_count': current_count,
                        'wait_time_seconds': elapsed,
                        'message': f'Ready: {current_count} embeddings in {elapsed}s',
                        'final_status': final_status
                    }

                # Sleep before next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error during embedding wait: {e}")
                # Continue retrying on error

        # Timeout reached
        elapsed = int(time.time() - start_time)
        final_status = await EmbeddingValidator.get_embedding_status(db)

        message = (
            f"Timeout after {elapsed}s: Only {current_count}/{min_samples} embeddings "
            f"({final_status['coverage_pct']}% coverage)"
        )

        if verbose:
            logger.warning(message)

        return {
            'success': False,
            'embedded_count': current_count,
            'wait_time_seconds': elapsed,
            'message': message,
            'final_status': final_status
        }

    @staticmethod
    async def alert_user_if_needed(db: AsyncSession) -> Optional[str]:
        """
        Check embedding status and return user alert if needed.

        Returns None if everything is fine, or an alert message if action needed.
        """
        status = await EmbeddingValidator.get_embedding_status(db)

        if not status.get('ready', False):
            samples_needed = status.get('samples_needed', 0)
            return (
                f"⚠️  VIBE SEARCH REQUIRES EMBEDDINGS\n\n"
                f"Current: {status['embedded_samples']}/{status['total_samples']} "
                f"({status['coverage_pct']}%)\n"
                f"Need: {samples_needed} more embeddings\n\n"
                f"Generate embeddings:\n"
                f"  ./venv/bin/python backend/scripts/generate_embeddings.py --resume\n"
                f"Estimated time: ~{max(2, samples_needed // 50)} hours"
            )

        if not status.get('production_ready', False):
            return (
                f"⏳ PARTIAL EMBEDDING COVERAGE\n\n"
                f"Current: {status['coverage_pct']}% "
                f"({status['embedded_samples']}/{status['total_samples']})\n"
                f"Production threshold: 80%\n\n"
                f"Vibe search available but with limited results.\n"
                f"Continue generating embeddings for complete coverage."
            )

        return None


class EmbeddingTestHelper:
    """Helper for test setup and embedding validation."""

    @staticmethod
    async def ensure_embeddings_ready(
        db: AsyncSession,
        skip_if_insufficient: bool = True,
        verbose: bool = True
    ) -> bool:
        """
        Ensure embeddings are ready for testing.

        Args:
            db: Database session
            skip_if_insufficient: If True and embeddings not ready, skip test
            verbose: Log messages

        Returns:
            True if ready, False if not (and skip_if_insufficient=False)

        Raises:
            pytest.skip() if skip_if_insufficient and not ready
        """
        status = await EmbeddingValidator.get_embedding_status(db)

        if not status.get('ready', False):
            message = (
                f"Insufficient embeddings: {status['embedded_samples']}/30 "
                f"({status['coverage_pct']}%)"
            )

            if skip_if_insufficient:
                # Will be caught by pytest
                import pytest
                pytest.skip(message)

            if verbose:
                logger.warning(message)

            return False

        if verbose:
            logger.info(
                f"Embeddings ready: {status['embedded_samples']} samples "
                f"({status['coverage_pct']}% coverage)"
            )

        return True

    @staticmethod
    async def wait_for_embeddings_or_skip(
        db: AsyncSession,
        timeout_seconds: int = 300,
        verbose: bool = True
    ) -> None:
        """
        Wait for embeddings with pytest skip fallback.

        If embeddings are not ready within timeout, skip the test.
        """
        result = await EmbeddingValidator.wait_for_embeddings(
            db=db,
            timeout_seconds=timeout_seconds,
            verbose=verbose
        )

        if not result['success']:
            import pytest
            pytest.skip(result['message'])

    @staticmethod
    def sync_wrapper_check_embeddings(db_session) -> dict:
        """
        Synchronous wrapper for checking embeddings (for pytest fixtures).

        Use this in pytest fixtures that can't be async.
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            EmbeddingValidator.get_embedding_status(db_session)
        )
