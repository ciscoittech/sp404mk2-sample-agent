#!/usr/bin/env python3
"""
Reprocess ALL samples with improved audio analysis.

Re-analyzes all samples in the database using the improved audio analysis
system with Essentia, octave correction, and confidence scoring.
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import List
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

from app.core.config import settings
from app.core.database import engine
from app.models.sample import Sample
from app.services.audio_features_service import AudioFeaturesService

console = Console()


async def get_all_samples(session) -> List[Sample]:
    """Get all samples from database."""
    query = select(Sample).order_by(Sample.id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def reprocess_sample(sample: Sample, audio_service: AudioFeaturesService, session) -> dict:
    """Reprocess a single sample and return results."""
    try:
        file_path = Path(sample.file_path)

        if not file_path.exists():
            return {
                "id": sample.id,
                "title": sample.title,
                "status": "error",
                "error": "File not found",
                "old_bpm": sample.bpm
            }

        # Store old values
        old_bpm = sample.bpm
        old_genre = sample.genre
        old_key = sample.musical_key

        # Re-analyze
        features = await audio_service.analyze_file(file_path)

        # Update sample
        sample.bpm = features.bpm
        sample.musical_key = features.key
        sample.genre = features.genre
        sample.bpm_confidence = features.bpm_confidence
        sample.genre_confidence = features.genre_confidence
        sample.key_confidence = features.key_confidence
        sample.analysis_metadata = features.metadata if features.metadata else {}
        sample.analyzed_at = datetime.utcnow()

        await session.commit()

        return {
            "id": sample.id,
            "title": sample.title,
            "status": "success",
            "old_bpm": old_bpm,
            "new_bpm": sample.bpm,
            "bpm_confidence": sample.bpm_confidence,
            "bpm_changed": abs(old_bpm - sample.bpm) > 1.0 if old_bpm else False,
            "genre_changed": old_genre != sample.genre if old_genre else False
        }

    except Exception as e:
        return {
            "id": sample.id,
            "title": sample.title,
            "status": "error",
            "error": str(e),
            "old_bpm": sample.bpm
        }


async def main(yes: bool = False, limit: int = None):
    """Main execution."""
    start_time = datetime.now()

    console.print(Panel.fit(
        "[bold cyan]Full Sample Reprocessing[/bold cyan]\n"
        "Re-analyzing all samples with improved audio analysis",
        border_style="cyan"
    ))

    # Create database session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # Get all samples
        console.print("\n[yellow]📊 Loading samples from database...[/yellow]")
        samples = await get_all_samples(session)

        if not samples:
            console.print("[yellow]⚠ No samples found in database![/yellow]")
            return

        # Apply limit if specified
        if limit:
            samples = samples[:limit]
            console.print(f"[yellow]Limiting to first {limit} samples[/yellow]")

        console.print(f"[green]✓ Found {len(samples)} samples to reprocess[/green]")

        # Confirm (unless --yes flag provided)
        if not yes:
            console.print(f"\n[yellow]About to reprocess {len(samples)} samples[/yellow]")
            console.print(f"[dim]Estimated time: ~{len(samples) * 3 / 60:.1f} minutes[/dim]")
            response = console.input("[bold]Continue? [y/N]: [/bold]")

            if response.lower() != 'y':
                console.print("[red]Cancelled[/red]")
                return
        else:
            console.print(f"\n[green]Auto-confirmed: Reprocessing {len(samples)} samples...[/green]")
            console.print(f"[dim]Estimated time: ~{len(samples) * 3 / 60:.1f} minutes[/dim]")

        # Initialize audio service
        audio_service = AudioFeaturesService()

        # Process samples with progress bar
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Reprocessing samples...", total=len(samples))

            for i, sample in enumerate(samples, 1):
                progress.update(
                    task,
                    description=f"[cyan][{i}/{len(samples)}] {sample.title[:40]}..."
                )
                result = await reprocess_sample(sample, audio_service, session)
                results.append(result)
                progress.advance(task)

        # Calculate stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")
        bpm_changed_count = sum(1 for r in results if r.get("bpm_changed", False))
        genre_changed_count = sum(1 for r in results if r.get("genre_changed", False))

        # Show results
        console.print("\n[bold green]✓ Reprocessing Complete[/bold green]\n")

        # Summary stats
        console.print("[bold]Summary Statistics:[/bold]")
        console.print(f"  Total processed: {len(results)}")
        console.print(f"  [green]Successful: {success_count} ({success_count/len(results)*100:.1f}%)[/green]")
        console.print(f"  [red]Errors: {error_count}[/red]")
        console.print(f"  [yellow]BPM changed: {bpm_changed_count} ({bpm_changed_count/len(results)*100:.1f}%)[/yellow]")
        console.print(f"  [yellow]Genre changed: {genre_changed_count} ({genre_changed_count/len(results)*100:.1f}%)[/yellow]")
        console.print(f"  [cyan]Duration: {duration/60:.1f} minutes[/cyan]")
        console.print(f"  [cyan]Average: {duration/len(results):.1f}s per sample[/cyan]")

        # Show some examples of changed BPMs
        changed_samples = [r for r in results if r.get("bpm_changed", False)]
        if changed_samples:
            console.print("\n[bold]Sample BPM Changes (first 10):[/bold]")
            table = Table()
            table.add_column("Title", style="white")
            table.add_column("Old BPM", style="red")
            table.add_column("New BPM", style="green")
            table.add_column("Confidence", style="cyan")

            for result in changed_samples[:10]:
                confidence = result.get("bpm_confidence", 0)
                confidence_str = f"{confidence}%" if confidence else "N/A"

                table.add_row(
                    result["title"][:40],
                    f"{result['old_bpm']:.1f}",
                    f"{result['new_bpm']:.1f}",
                    confidence_str
                )

            console.print(table)

        # Log errors if any
        error_samples = [r for r in results if r["status"] == "error"]
        if error_samples:
            console.print(f"\n[bold red]Errors ({len(error_samples)}):[/bold red]")
            error_table = Table()
            error_table.add_column("Title", style="white")
            error_table.add_column("Error", style="red")

            for result in error_samples[:10]:
                error_table.add_row(
                    result["title"][:40],
                    result.get("error", "Unknown")[:50]
                )

            console.print(error_table)
            if len(error_samples) > 10:
                console.print(f"[dim]... and {len(error_samples) - 10} more errors[/dim]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reprocess all samples with improved audio analysis"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Auto-confirm without prompting (useful for cron jobs)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Limit number of samples to process (for testing)"
    )
    args = parser.parse_args()

    asyncio.run(main(yes=args.yes, limit=args.limit))
