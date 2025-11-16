#!/usr/bin/env python3
"""
Reprocess samples with suspicious BPM values (octave errors).

Finds samples with BPM < 60 or > 180 and re-analyzes them using the
improved audio analysis system with octave correction.
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from app.core.config import settings
from app.core.database import engine
from app.models.sample import Sample
from app.services.audio_features_service import AudioFeaturesService

console = Console()


async def find_suspicious_samples(session) -> List[Sample]:
    """Find samples with BPM values likely to be octave errors."""
    query = select(Sample).where(
        or_(
            Sample.bpm < 60,
            Sample.bpm > 180
        )
    ).order_by(Sample.bpm)

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

        # Re-analyze
        features = await audio_service.analyze_file(file_path)

        # Update sample
        sample.bpm = features.bpm
        sample.musical_key = features.key
        sample.genre = features.genre
        sample.bpm_confidence = features.bpm_confidence
        sample.genre_confidence = features.genre_confidence
        sample.key_confidence = features.key_confidence

        # Store analysis metadata
        sample.analysis_metadata = features.metadata if features.metadata else {}

        await session.commit()

        return {
            "id": sample.id,
            "title": sample.title,
            "status": "success",
            "old_bpm": old_bpm,
            "new_bpm": sample.bpm,
            "bpm_confidence": sample.bpm_confidence,
            "corrected": abs(old_bpm - sample.bpm) > 1.0
        }

    except Exception as e:
        return {
            "id": sample.id,
            "title": sample.title,
            "status": "error",
            "error": str(e),
            "old_bpm": sample.bpm
        }


async def main(yes: bool = False):
    """Main execution."""
    console.print(Panel.fit(
        "[bold cyan]Selective BPM Reprocessing[/bold cyan]\n"
        "Finding samples with suspicious BPM values (< 60 or > 180)",
        border_style="cyan"
    ))

    # Create database session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # Find suspicious samples
        console.print("\n[yellow]🔍 Searching for suspicious BPM values...[/yellow]")
        samples = await find_suspicious_samples(session)

        if not samples:
            console.print("[green]✓ No suspicious BPM values found![/green]")
            return

        # Show what we found
        table = Table(title=f"Found {len(samples)} Suspicious Samples")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Current BPM", style="yellow")
        table.add_column("Issue", style="red")

        for sample in samples:
            issue = "Too Low" if sample.bpm < 60 else "Too High"
            table.add_row(
                str(sample.id),
                sample.title[:50],
                f"{sample.bpm:.1f}",
                issue
            )

        console.print(table)

        # Confirm (unless --yes flag provided)
        if not yes:
            console.print(f"\n[yellow]About to reprocess {len(samples)} samples[/yellow]")
            response = console.input("[bold]Continue? [y/N]: [/bold]")

            if response.lower() != 'y':
                console.print("[red]Cancelled[/red]")
                return
        else:
            console.print(f"\n[green]Auto-confirmed: Reprocessing {len(samples)} samples...[/green]")

        # Initialize audio service
        audio_service = AudioFeaturesService()

        # Process samples
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Reprocessing samples...", total=len(samples))

            for sample in samples:
                progress.update(task, description=f"[cyan]Processing {sample.title[:40]}...")
                result = await reprocess_sample(sample, audio_service, session)
                results.append(result)
                progress.advance(task)

        # Show results
        console.print("\n[bold green]✓ Reprocessing Complete[/bold green]\n")

        # Summary table
        summary = Table(title="Reprocessing Results")
        summary.add_column("Title", style="white")
        summary.add_column("Old BPM", style="red")
        summary.add_column("New BPM", style="green")
        summary.add_column("Confidence", style="cyan")
        summary.add_column("Status", style="yellow")

        success_count = 0
        corrected_count = 0
        error_count = 0

        for result in results:
            if result["status"] == "success":
                success_count += 1
                if result.get("corrected"):
                    corrected_count += 1

                confidence = result.get("bpm_confidence", 0)
                confidence_str = f"{confidence}%" if confidence else "N/A"

                summary.add_row(
                    result["title"][:40],
                    f"{result['old_bpm']:.1f}",
                    f"{result['new_bpm']:.1f}",
                    confidence_str,
                    "✓ Corrected" if result.get("corrected") else "✓ Same"
                )
            else:
                error_count += 1
                summary.add_row(
                    result["title"][:40],
                    f"{result['old_bpm']:.1f}",
                    "—",
                    "—",
                    f"✗ {result.get('error', 'Unknown error')}"
                )

        console.print(summary)

        # Final stats
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total processed: {len(results)}")
        console.print(f"  [green]Successful: {success_count}[/green]")
        console.print(f"  [yellow]BPM corrected: {corrected_count}[/yellow]")
        console.print(f"  [red]Errors: {error_count}[/red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reprocess samples with suspicious BPM values (< 60 or > 180)"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Auto-confirm without prompting (useful for cron jobs)"
    )
    args = parser.parse_args()

    asyncio.run(main(yes=args.yes))
