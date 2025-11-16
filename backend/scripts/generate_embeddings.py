#!/usr/bin/env python3
"""
Generate and populate vector embeddings for existing samples.

This script:
1. Reads samples from PostgreSQL with vibe analysis
2. Creates embedding source text from vibe descriptions
3. Generates embeddings using EmbeddingService (OpenRouter API)
4. Stores embeddings in PostgreSQL sample_embeddings table
5. Tracks progress with resumability and cost estimation

Cost Estimation:
- OpenRouter text-embedding-3-small: ~$0.02 per 1M tokens
- Average ~200 tokens per sample
- 2,328 samples × 200 tokens = 465,600 tokens ≈ $0.009 total

Usage:
    python backend/scripts/generate_embeddings.py --all
    python backend/scripts/generate_embeddings.py --resume
    python backend/scripts/generate_embeddings.py --dry-run
    python backend/scripts/generate_embeddings.py --sample-ids 1,2,3,100-200
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.sample import Sample
from app.models.vibe_analysis import VibeAnalysis
from app.models.sample_embedding import SampleEmbedding

from app.services.embedding_service import EmbeddingService
from app.services.usage_tracking_service import UsageTrackingService

console = Console()

PROGRESS_FILE = Path(__file__).parent / "embeddings_progress.json"
BATCH_SIZE = 100  # Process 100 samples at a time


class ProgressTracker:
    """Track embedding generation progress for resumability."""

    def __init__(self, progress_file: Path = PROGRESS_FILE):
        self.progress_file = progress_file
        self.data = self._load()

    def _load(self) -> Dict:
        """Load progress from file or initialize new."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "last_processed_id": 0,
            "total_processed": 0,
            "total_cost_usd": 0.0,
            "total_tokens": 0,
            "failures": [],
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def save(self):
        """Save progress to file."""
        self.data["updated_at"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def update(self, sample_id: int, cost: float = 0.0, tokens: int = 0, failed: bool = False):
        """Update progress counters."""
        self.data["last_processed_id"] = sample_id
        self.data["total_processed"] += 1
        self.data["total_cost_usd"] += cost
        self.data["total_tokens"] += tokens
        if failed:
            self.data.setdefault("failures", []).append({
                "sample_id": sample_id,
                "timestamp": datetime.now().isoformat()
            })
        self.save()

    def reset(self):
        """Reset progress (for fresh run)."""
        self.data = {
            "last_processed_id": 0,
            "total_processed": 0,
            "total_cost_usd": 0.0,
            "total_tokens": 0,
            "failures": [],
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.save()


def create_embedding_source_text(sample: Sample, vibe: Optional[VibeAnalysis]) -> str:
    """
    Create embedding source text from sample and vibe data.

    Format:
        Title: {title}
        Genre: {genre}
        BPM: {bpm}
        Key: {musical_key}
        Mood: {mood_primary}, {mood_secondary}
        Energy: {energy_level}
        Tags: {vibe_tags}
        Description: {raw_analysis}

    Args:
        sample: Sample model with basic properties
        vibe: VibeAnalysis model (optional, may be None)

    Returns:
        Formatted text for embedding generation
    """
    parts = [f"Title: {sample.title}"]

    # Add musical properties
    if sample.genre:
        parts.append(f"Genre: {sample.genre}")
    if sample.bpm:
        parts.append(f"BPM: {sample.bpm:.0f}")
    if sample.musical_key:
        parts.append(f"Key: {sample.musical_key}")

    # Add vibe analysis if available
    if vibe:
        mood_parts = [vibe.mood_primary]
        if vibe.mood_secondary:
            mood_parts.append(vibe.mood_secondary)
        parts.append(f"Mood: {', '.join(mood_parts)}")

        if vibe.energy_level is not None:
            parts.append(f"Energy: {vibe.energy_level:.2f}")

        # Add texture tags
        if vibe.texture_tags:
            tags = ', '.join(vibe.texture_tags)
            parts.append(f"Tags: {tags}")

        # Add raw analysis/characteristics
        if vibe.characteristics and 'raw_analysis' in vibe.characteristics:
            raw = vibe.characteristics['raw_analysis']
            parts.append(f"Description: {raw}")

    # Add sample tags as fallback
    if sample.tags:
        parts.append(f"Sample Tags: {', '.join(sample.tags)}")

    return '\n'.join(parts)




def validate_embedding(embedding: List[float], expected_dim: int = 1536) -> bool:
    """
    Validate embedding dimensions and values.

    Args:
        embedding: Vector to validate
        expected_dim: Expected number of dimensions

    Returns:
        True if valid, False otherwise
    """
    if len(embedding) != expected_dim:
        console.print(f"[red]Invalid dimensions: {len(embedding)} (expected {expected_dim})[/red]")
        return False

    # Check for NaN or infinite values
    if any(not isinstance(x, (int, float)) or x != x or abs(x) == float('inf') for x in embedding):
        console.print(f"[red]Invalid values detected (NaN or infinite)[/red]")
        return False

    return True


async def fetch_samples_batch(
    session: AsyncSession,
    last_id: int = 0,
    limit: int = BATCH_SIZE,
    sample_ids: Optional[List[int]] = None
) -> List[Tuple[Sample, Optional[VibeAnalysis]]]:
    """
    Fetch batch of samples with vibe analysis from PostgreSQL.

    Args:
        session: Database session
        last_id: Last processed sample ID (for pagination)
        limit: Number of samples to fetch
        sample_ids: Optional specific sample IDs to fetch

    Returns:
        List of (Sample, VibeAnalysis) tuples
    """
    query = (
        select(Sample, VibeAnalysis)
        .outerjoin(VibeAnalysis, Sample.id == VibeAnalysis.sample_id)
        .order_by(Sample.id)
    )

    if sample_ids:
        query = query.where(Sample.id.in_(sample_ids))
    else:
        query = query.where(Sample.id > last_id).limit(limit)

    result = await session.execute(query)
    return result.all()


async def store_embedding_in_postgres(
    session: AsyncSession,
    sample_id: int,
    embedding: List[float],
    source_text: str
) -> bool:
    """
    Store embedding in PostgreSQL database.

    Args:
        session: AsyncSession for database operations
        sample_id: Sample ID
        embedding: Vector embedding (1536 dimensions)
        source_text: Original text used for embedding

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if embedding exists
        query = select(SampleEmbedding).where(SampleEmbedding.sample_id == sample_id)
        result = await session.execute(query)
        existing = result.scalar_one_or_none()

        # Convert embedding list to JSON string for SQLite compatibility
        embedding_json = json.dumps(embedding) if isinstance(embedding, list) else embedding

        if existing:
            # Update existing embedding
            existing.vibe_vector = embedding_json
            existing.embedding_source = source_text
        else:
            # Insert new embedding
            new_embedding = SampleEmbedding(
                sample_id=sample_id,
                vibe_vector=embedding_json,
                embedding_source=source_text
            )
            session.add(new_embedding)

        await session.commit()
        return True

    except Exception as e:
        await session.rollback()
        console.print(f"[red]Failed to store embedding for sample {sample_id}: {e}[/red]")
        return False


async def generate_embeddings_batch(
    samples: List[Tuple[Sample, Optional[VibeAnalysis]]],
    session: AsyncSession,
    embedding_service: EmbeddingService,
    progress: ProgressTracker,
    dry_run: bool = False,
    max_retries: int = 3
) -> Tuple[int, int, float]:
    """
    Generate embeddings for a batch of samples.

    Args:
        samples: List of (Sample, VibeAnalysis) tuples
        embedding_service: EmbeddingService instance
        progress: Progress tracker
        dry_run: If True, only estimate cost without making API calls
        max_retries: Maximum number of retries for failed embeddings

    Returns:
        Tuple of (successful, failed, total_cost)
    """
    successful = 0
    failed = 0
    total_cost = 0.0

    for sample, vibe in samples:
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Create embedding source text
                source_text = create_embedding_source_text(sample, vibe)

                if dry_run:
                    # Estimate tokens (rough: 4 chars per token)
                    estimated_tokens = len(source_text) // 4
                    # OpenRouter text-embedding-3-small: $0.02 per 1M tokens
                    estimated_cost = (estimated_tokens / 1_000_000) * 0.02
                    total_cost += estimated_cost
                    successful += 1
                    if retry_count == 0:  # Only print on first attempt
                        console.print(f"[dim]Sample {sample.id}: ~{estimated_tokens} tokens, ~${estimated_cost:.6f}[/dim]")
                    break  # Success, exit retry loop
                else:
                    # Generate embedding via API
                    embedding = await embedding_service.generate_embedding(source_text)

                    # Validate embedding
                    if not validate_embedding(embedding):
                        raise ValueError("Invalid embedding generated")

                    # Store in PostgreSQL
                    success = await store_embedding_in_postgres(session, sample.id, embedding, source_text)
                    if not success:
                        raise Exception("Failed to store embedding in PostgreSQL")

                    # Estimate cost (approximate based on text length)
                    estimated_tokens = len(source_text) // 4
                    cost = (estimated_tokens / 1_000_000) * 0.02

                    # Track progress
                    progress.update(sample.id, cost=cost, tokens=estimated_tokens)
                    total_cost += cost
                    successful += 1
                    break  # Success, exit retry loop

            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    console.print(f"[red]Failed to process sample {sample.id} after {max_retries} retries: {e}[/red]")
                    progress.update(sample.id, failed=True)
                    failed += 1
                    break
                else:
                    # Exponential backoff
                    wait_time = min(2 ** retry_count, 10)
                    console.print(f"[yellow]Retry {retry_count}/{max_retries} for sample {sample.id} after {wait_time}s: {e}[/yellow]")
                    await asyncio.sleep(wait_time)

    return successful, failed, total_cost


async def process_all_samples(
    resume: bool = False,
    dry_run: bool = False,
    sample_ids: Optional[List[int]] = None,
    reset: bool = False
):
    """
    Main processing function for generating embeddings.

    Args:
        resume: Continue from last checkpoint
        dry_run: Only estimate cost, don't make API calls
        sample_ids: Optional list of specific sample IDs to process
        reset: Reset progress and start fresh
    """
    # Initialize progress tracker
    progress = ProgressTracker()
    if reset:
        progress.reset()

    # Initialize database connection
    # Use SQLite database (located in backend/ directory)
    backend_dir = Path(__file__).parent.parent
    db_path = backend_dir / "sp404_samples.db"

    # Override DATABASE_URL to use local SQLite
    db_url = f"sqlite+aiosqlite:///{db_path}"

    console.print(f"[dim]Using database: {db_path}[/dim]")

    engine = create_async_engine(db_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize services
    # Create a session for services
    embedding_service = None
    if not dry_run:
        async with AsyncSessionLocal() as session:
            usage_tracking_service = UsageTrackingService(session)
            embedding_service = EmbeddingService(usage_tracking_service)

    # Get total sample count
    async with AsyncSessionLocal() as session:
        if sample_ids:
            total_samples = len(sample_ids)
        else:
            result = await session.execute(select(Sample.id).order_by(Sample.id.desc()).limit(1))
            max_id = result.scalar()
            total_samples = max_id or 0

    console.print(Panel(
        f"[bold cyan]Embedding Generation {'(DRY RUN)' if dry_run else ''}[/bold cyan]\n\n"
        f"Total samples: {total_samples:,}\n"
        f"Last processed: {progress.data['last_processed_id']}\n"
        f"Resume from: {progress.data['last_processed_id'] + 1}\n"
        f"Batch size: {BATCH_SIZE}\n"
        f"Previous cost: ${progress.data['total_cost_usd']:.4f}",
        title="Configuration",
        border_style="cyan"
    ))

    # Statistics
    total_successful = 0
    total_failed = 0
    total_cost = progress.data['total_cost_usd']

    # Progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress_bar:

        task = progress_bar.add_task(
            f"[cyan]{'Estimating' if dry_run else 'Processing'} samples...",
            total=total_samples
        )

        # Process in batches
        last_id = progress.data['last_processed_id'] if resume else 0
        remaining = total_samples - last_id

        while remaining > 0:
            async with AsyncSessionLocal() as session:
                # Fetch batch
                samples = await fetch_samples_batch(
                    session,
                    last_id=last_id,
                    limit=BATCH_SIZE,
                    sample_ids=sample_ids
                )

                if not samples:
                    break

                # Process batch
                successful, failed, batch_cost = await generate_embeddings_batch(
                    samples, session, embedding_service, progress, dry_run
                )

                total_successful += successful
                total_failed += failed
                total_cost += batch_cost

                # Update progress
                last_id = samples[-1][0].id  # Last sample ID in batch
                progress_bar.update(task, advance=len(samples))
                remaining -= len(samples)

                # Update progress bar description
                progress_bar.update(
                    task,
                    description=f"[cyan]Processed {total_successful + total_failed}/{total_samples} "
                                f"(${total_cost:.4f})"
                )

    # Final statistics
    display_final_stats(
        total_samples=total_successful + total_failed,
        successful=total_successful,
        failed=total_failed,
        total_cost=total_cost,
        failures=progress.data.get('failures', []),
        dry_run=dry_run
    )


def display_final_stats(
    total_samples: int,
    successful: int,
    failed: int,
    total_cost: float,
    failures: List[Dict],
    dry_run: bool
):
    """Display final processing statistics."""
    table = Table(title=f"{'Cost Estimation' if dry_run else 'Embedding Generation'} Summary", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Samples", f"{total_samples:,}")
    table.add_row("Successful", f"{successful:,}")
    table.add_row("Failed", f"{failed:,}")
    table.add_row("Success Rate", f"{(successful / total_samples * 100) if total_samples > 0 else 0:.1f}%")
    table.add_row("Total Cost", f"${total_cost:.4f}")
    if successful > 0:
        table.add_row("Avg Cost/Sample", f"${total_cost / successful:.6f}")

    console.print(table)

    if failures:
        console.print(f"\n[yellow]Failed samples: {len(failures)}[/yellow]")
        console.print(f"Sample IDs: {', '.join(str(f['sample_id']) for f in failures[:10])}")
        if len(failures) > 10:
            console.print(f"... and {len(failures) - 10} more")


def parse_sample_ids(ids_str: str) -> List[int]:
    """
    Parse sample ID string into list of integers.

    Supports:
    - Individual IDs: "1,2,3"
    - Ranges: "100-200"
    - Mixed: "1,5,10-20,100"

    Args:
        ids_str: Comma-separated IDs and ranges

    Returns:
        List of sample IDs
    """
    ids = []
    for part in ids_str.split(','):
        part = part.strip()
        if '-' in part:
            # Range
            start, end = map(int, part.split('-'))
            ids.extend(range(start, end + 1))
        else:
            # Single ID
            ids.append(int(part))
    return sorted(set(ids))  # Remove duplicates and sort


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate vector embeddings for sample library"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all',
        action='store_true',
        help='Process all samples from beginning'
    )
    group.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint'
    )
    group.add_argument(
        '--sample-ids',
        type=str,
        help='Process specific sample IDs (e.g., "1,2,3,100-200")'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Estimate cost only, do not make API calls'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset progress and start fresh (use with --all)'
    )

    args = parser.parse_args()

    # Parse sample IDs if provided
    sample_ids = None
    if args.sample_ids:
        sample_ids = parse_sample_ids(args.sample_ids)
        console.print(f"[cyan]Processing {len(sample_ids)} specific samples[/cyan]")

    # Run async main
    asyncio.run(process_all_samples(
        resume=args.resume,
        dry_run=args.dry_run,
        sample_ids=sample_ids,
        reset=args.reset
    ))


if __name__ == "__main__":
    main()
