#!/usr/bin/env env python3
"""Test script for the improved Vibe Analysis Agent with thinking protocol."""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.vibe_analysis import VibeAnalysisAgent


async def test_vibe_analysis():
    """Test vibe analysis on sample data."""
    console = Console()

    console.print("\n[bold cyan]🎵 SP404MK2 Vibe Analysis Agent - Phase 1 Testing[/bold cyan]\n")
    console.print("[yellow]Testing improved agent with 5-step thinking protocol[/yellow]\n")

    # Create agent
    agent = VibeAnalysisAgent()

    # Test samples with realistic musical data
    test_samples = [
        {
            "filename": "02 - Le Collecteur.wav",
            "bpm": 90,
            "key": "D minor",
            "spectral_centroid": 1200
        },
        {
            "filename": "02. Lalo Schifrin - The Cop.wav",
            "bpm": 120,
            "key": "C major",
            "spectral_centroid": 2400
        },
        {
            "filename": "09 - Moby Grape - Sitting by The Window 1967.wav",
            "bpm": 110,
            "key": "G major",
            "spectral_centroid": 1800
        }
    ]

    console.print(Panel.fit(
        "[bold]Test Samples:[/bold]\n\n" +
        "\n".join([f"• {s['filename']} ({s['bpm']} BPM, {s['key']})" for s in test_samples]),
        title="📂 Samples",
        border_style="blue"
    ))

    # Analyze each sample
    results = []
    for i, sample in enumerate(test_samples, 1):
        console.print(f"\n[bold cyan]Analyzing sample {i}/3...[/bold cyan]")

        try:
            result = await agent.analyze_vibe(sample)
            results.append(result)

            # Display result
            table = Table(title=f"🎼 {result.filename}", show_header=False, border_style="green")
            table.add_column("Property", style="cyan", width=20)
            table.add_column("Value", style="white")

            table.add_row("BPM", str(result.bpm))
            table.add_row("Key", result.key)
            table.add_row("Era", result.vibe.era)
            table.add_row("Genre", result.vibe.genre)
            table.add_row("Energy Level", result.vibe.energy_level)
            table.add_row("Mood", ", ".join(result.vibe.mood))
            table.add_row("Descriptors", ", ".join(result.vibe.descriptors))
            table.add_row("Best Use", result.best_use)
            table.add_row("Compatibility", ", ".join(result.compatibility_tags[:5]))

            console.print(table)
            console.print(f"[dim]✓ Analysis complete with {result.confidence*100:.0f}% confidence[/dim]")

        except Exception as e:
            console.print(f"[red]✗ Error analyzing {sample['filename']}: {str(e)}[/red]")

    # Summary
    if results:
        console.print("\n" + "="*70)
        console.print("[bold green]✓ Phase 1 Test Complete[/bold green]\n")

        console.print("[bold]Key Improvements:[/bold]")
        console.print("  • Agent uses 5-step thinking protocol")
        console.print("  • Analyzes musical characteristics → context → mood → use case")
        console.print("  • Specific descriptors instead of generic terms")
        console.print("  • Reasoning-based compatibility matching")

        console.print(f"\n[bold]Results:[/bold] {len(results)}/{len(test_samples)} samples analyzed successfully")

        # Show genre/era distribution
        eras = [r.vibe.era for r in results]
        genres = [r.vibe.genre for r in results]
        console.print(f"\n[dim]Eras detected: {', '.join(set(eras))}[/dim]")
        console.print(f"[dim]Genres detected: {', '.join(set(genres))}[/dim]")


async def test_batch_analysis():
    """Test batch analysis."""
    console = Console()

    console.print("\n[bold cyan]🎵 Testing Batch Analysis[/bold cyan]\n")

    agent = VibeAnalysisAgent()

    # Batch test samples
    batch_samples = [
        {"filename": "02 - Le Collecteur.wav", "bpm": 93, "key": "D minor", "spectral_centroid": 1150},
        {"filename": "10 - The Mirage - See The Rain 1966.wav", "bpm": 115, "key": "A major", "spectral_centroid": 2200},
        {"filename": "05 - Under the shade of an old oak.wav", "bpm": 88, "key": "E minor", "spectral_centroid": 900}
    ]

    console.print(f"[yellow]Analyzing {len(batch_samples)} samples in batch mode...[/yellow]\n")

    try:
        results = await agent.analyze_batch(batch_samples)

        # Create summary table
        table = Table(title="📊 Batch Analysis Results", border_style="cyan")
        table.add_column("Sample", style="white", width=30)
        table.add_column("Era", style="yellow")
        table.add_column("Genre", style="green")
        table.add_column("Energy", style="magenta")
        table.add_column("Best Use", style="cyan")

        for result in results:
            table.add_row(
                result.filename[:30],
                result.vibe.era,
                result.vibe.genre,
                result.vibe.energy_level,
                result.best_use
            )

        console.print(table)
        console.print(f"\n[green]✓ Batch analysis complete: {len(results)} samples processed[/green]")

    except Exception as e:
        console.print(f"[red]✗ Batch analysis error: {str(e)}[/red]")


if __name__ == "__main__":
    console = Console()

    try:
        # Run single sample test
        asyncio.run(test_vibe_analysis())

        # Ask to run batch test
        console.print("\n" + "="*70)
        console.print("\n[bold]Run batch analysis test? (y/n)[/bold] ", end="")
        response = input().strip().lower()

        if response == 'y':
            asyncio.run(test_batch_analysis())

        console.print("\n[bold green]All tests complete! ✓[/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error running tests: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())
