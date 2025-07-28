"""Command-line interface for SP404MK2 Sample Agent."""

import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import settings
from .logging_config import setup_logging
from .agents.collector import CollectorAgent
from .agents.downloader import DownloaderAgent
from .agents.analyzer import AnalyzerAgent
from .agents.reporter import ReporterAgent

# Create CLI app
app = typer.Typer(
    name="sp404agent",
    help="AI-powered sample collection agent for SP404MK2",
    add_completion=False,
)

console = Console()


@app.command()
def collect(
    genre: str = typer.Argument(..., help="Musical genre (e.g., jazz, hip-hop)"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="Specific style within genre"),
    bpm_min: Optional[int] = typer.Option(None, "--bpm-min", help="Minimum BPM"),
    bpm_max: Optional[int] = typer.Option(None, "--bpm-max", help="Maximum BPM"),
    count: int = typer.Option(10, "--count", "-c", help="Number of samples to collect"),
    download: bool = typer.Option(False, "--download", "-d", help="Download immediately"),
) -> None:
    """
    Collect samples based on criteria.
    
    Examples:
        sp404agent collect jazz --style bebop --bpm-min 120 --bpm-max 140
        sp404agent collect hip-hop --count 20 --download
    """
    async def run_collection():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Discover samples
            task = progress.add_task("[cyan]Discovering samples...", total=None)
            
            collector = CollectorAgent()
            result = await collector.execute(
                task_id=f"cli_collect_{genre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                genre=genre,
                style=style,
                bpm_range=(bpm_min, bpm_max) if bpm_min and bpm_max else None,
                max_results=count
            )
            
            progress.update(task, completed=True)
            
            if result.status.value == "success":
                sources = result.result.get("sources", [])
                console.print(f"\n[green]✓ Found {len(sources)} samples[/green]")
                
                # Display results
                if sources:
                    table = Table(title="Discovered Samples")
                    table.add_column("#", style="dim", width=4)
                    table.add_column("Title", style="cyan")
                    table.add_column("Platform", style="magenta")
                    table.add_column("Duration", style="yellow")
                    
                    for i, source in enumerate(sources[:10], 1):  # Show first 10
                        table.add_row(
                            str(i),
                            source.get("title", "Unknown")[:50],
                            source.get("platform", "unknown"),
                            f"{source.get('duration', 0)}s"
                        )
                    
                    if len(sources) > 10:
                        table.add_row("...", f"({len(sources)-10} more)", "...", "...")
                    
                    console.print(table)
                
                # Download if requested
                if download and sources:
                    console.print()
                    task = progress.add_task("[cyan]Downloading samples...", total=len(sources))
                    
                    downloader = DownloaderAgent()
                    dl_result = await downloader.execute(
                        task_id=f"cli_download_{genre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        source_urls=[s["url"] for s in sources],
                        output_dir=str(settings.download_path),
                        max_count=count
                    )
                    
                    progress.update(task, completed=True)
                    
                    if dl_result.status.value == "success":
                        count = dl_result.result.get("downloaded_count", 0)
                        console.print(f"\n[green]✓ Downloaded {count} files to {settings.download_path}[/green]")
                    else:
                        console.print(f"\n[red]✗ Download failed: {dl_result.error}[/red]")
            else:
                console.print(f"\n[red]✗ Collection failed: {result.error}[/red]")
    
    asyncio.run(run_collection())


@app.command()
def analyze(
    input_dir: str = typer.Argument(..., help="Directory containing audio files"),
    organize: bool = typer.Option(False, "--organize", "-o", help="Organize files by BPM"),
    detect_key: bool = typer.Option(False, "--key", "-k", help="Detect musical key"),
    report: bool = typer.Option(False, "--report", "-r", help="Generate analysis report"),
) -> None:
    """
    Analyze audio files for BPM, key, and other characteristics.
    
    Examples:
        sp404agent analyze ./downloads
        sp404agent analyze ./samples --organize --key --report
    """
    async def run_analysis():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Analyzing audio files...", total=None)
            
            analyzer = AnalyzerAgent()
            result = await analyzer.execute(
                task_id=f"cli_analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                input_dir=input_dir,
                organize_by_bpm=organize,
                detect_key=detect_key,
                create_report=report,
                report_path=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json" if report else None
            )
            
            progress.update(task, completed=True)
            
            if result.status.value == "success":
                count = result.result.get("analyzed_count", 0)
                console.print(f"\n[green]✓ Analyzed {count} files[/green]")
                
                # Show summary
                if count > 0:
                    files = result.result.get("files", [])
                    
                    # BPM summary
                    bpms = [f.get("bpm", 0) for f in files if f.get("bpm")]
                    if bpms:
                        avg_bpm = sum(bpms) / len(bpms)
                        console.print(f"\n[bold]Analysis Summary:[/bold]")
                        console.print(f"  Average BPM: {avg_bpm:.1f}")
                        console.print(f"  BPM Range: {min(bpms):.0f} - {max(bpms):.0f}")
                    
                    # Key distribution
                    if detect_key:
                        key_groups = result.result.get("key_groups", {})
                        if key_groups:
                            console.print(f"\n  Key Distribution:")
                            for key, files in key_groups.items():
                                console.print(f"    {key}: {len(files)} files")
                    
                    console.print(f"\n  Files organized by BPM: {'Yes' if organize else 'No'}")
                    
                    if report:
                        console.print(f"  Report saved: {result.result.get('report_path')}")
            else:
                console.print(f"\n[red]✗ Analysis failed: {result.error}[/red]")
    
    asyncio.run(run_analysis())


@app.command()
def review(
    action: str = typer.Argument("list", help="Action: list, create"),
    batch_id: Optional[int] = typer.Option(None, "--batch", "-b", help="Batch ID"),
) -> None:
    """
    Manage review queues for sample approval.
    
    Examples:
        sp404agent review list
        sp404agent review create --batch 1
    """
    async def run_review():
        reporter = ReporterAgent()
        
        if action == "create":
            # Mock getting samples - in production, get from database
            samples = [
                {
                    "filename": f"sample_{i}.wav",
                    "bpm": 90 + i,
                    "key": ["C major", "F minor", "G major"][i % 3],
                    "source_url": f"https://example.com/{i}"
                }
                for i in range(5)
            ]
            
            result = await reporter.execute(
                task_id=f"cli_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action="create_review_queue",
                batch_data={
                    "batch_name": f"Review Batch {batch_id or datetime.now().strftime('%Y%m%d')}",
                    "samples": samples
                },
                output_dir=str(settings.review_queue_path)
            )
            
            if result.status.value == "success":
                console.print(f"\n[green]✓ Review queue created: {result.result['review_file']}[/green]")
                console.print(f"  Samples: {result.result['samples_count']}")
            else:
                console.print(f"\n[red]✗ Failed to create review queue[/red]")
                
        elif action == "list":
            # List review files
            import glob
            pattern = f"{settings.review_queue_path}/*.md"
            files = glob.glob(pattern)
            
            if files:
                console.print("\n[bold]Review Queues:[/bold]")
                
                table = Table()
                table.add_column("File", style="cyan")
                table.add_column("Created", style="yellow")
                table.add_column("Size", style="green")
                
                for f in sorted(files)[-10:]:  # Show last 10
                    path = Path(f)
                    created = datetime.fromtimestamp(path.stat().st_mtime)
                    size = path.stat().st_size / 1024  # KB
                    
                    table.add_row(
                        path.name,
                        created.strftime("%Y-%m-%d %H:%M"),
                        f"{size:.1f} KB"
                    )
                
                console.print(table)
            else:
                console.print("\n[yellow]No review queues found[/yellow]")
                console.print(f"  Looked in: {settings.review_queue_path}")
    
    asyncio.run(run_review())


@app.command()
def status(
    tasks: bool = typer.Option(False, "--tasks", "-t", help="Show task statistics"),
) -> None:
    """
    Check system status and configuration.
    
    Example:
        sp404agent status
        sp404agent status --tasks
    """
    console.print("[bold green]SP404MK2 Sample Agent Status[/bold green]\n")
    
    # Configuration status
    console.print("[bold]Configuration:[/bold]")
    console.print(f"  Version: 0.1.0")
    console.print(f"  Log Level: {settings.agent_log_level}")
    
    # Check critical components
    console.print("\n[bold]Components:[/bold]")
    
    # Database
    if settings.turso_url and settings.turso_token:
        console.print("  ✅ Database: Configured")
    else:
        console.print("  ❌ Database: Not configured")
    
    # API Keys
    if settings.openrouter_api_key:
        console.print("  ✅ OpenRouter API: Configured")
    else:
        console.print("  ❌ OpenRouter API: Not configured")
    
    # Directories
    console.print("\n[bold]Directories:[/bold]")
    for name, path in [
        ("Downloads", settings.download_path),
        ("Samples", settings.sample_path),
        ("Review Queue", settings.review_queue_path)
    ]:
        if Path(path).exists():
            console.print(f"  ✅ {name}: {path}")
        else:
            console.print(f"  ⚠️  {name}: {path} (not created)")
    
    if tasks:
        console.print("\n[bold]Task Statistics:[/bold]")
        # In production, query database for stats
        console.print("  [dim]Database statistics not available in demo mode[/dim]")


@app.command()
def workflow(
    genre: str = typer.Argument(..., help="Musical genre"),
    count: int = typer.Option(5, "--count", "-c", help="Number of samples"),
    skip_download: bool = typer.Option(False, "--skip-download", help="Skip download phase"),
) -> None:
    """
    Run complete workflow: collect → download → analyze → review.
    
    Example:
        sp404agent workflow jazz --count 10
        sp404agent workflow "lo-fi hip hop" --skip-download
    """
    async def run_workflow():
        console.print(f"\n[bold cyan]🎵 Starting complete workflow for '{genre}'[/bold cyan]\n")
        
        # Track timing
        start_time = datetime.now()
        
        # 1. Collect
        console.print("[bold]1️⃣  Collecting samples...[/bold]")
        collector = CollectorAgent()
        collect_result = await collector.execute(
            task_id=f"workflow_{genre.replace(' ', '_')}_collect",
            genre=genre,
            max_results=count
        )
        
        if collect_result.status.value != "success":
            console.print("[red]✗ Collection failed[/red]")
            return
        
        sources = collect_result.result.get("sources", [])
        console.print(f"[green]✓ Found {len(sources)} samples[/green]")
        
        # 2. Download (optional)
        if not skip_download and sources:
            console.print("\n[bold]2️⃣  Downloading samples...[/bold]")
            downloader = DownloaderAgent()
            download_result = await downloader.execute(
                task_id=f"workflow_{genre.replace(' ', '_')}_download",
                source_urls=[s["url"] for s in sources],
                output_dir=str(settings.download_path)
            )
            
            if download_result.status.value != "success":
                console.print("[red]✗ Download failed[/red]")
                return
            
            console.print(f"[green]✓ Downloaded {download_result.result['downloaded_count']} files[/green]")
        else:
            console.print("\n[bold]2️⃣  Skipping download phase[/bold]")
        
        # 3. Analyze
        console.print("\n[bold]3️⃣  Analyzing samples...[/bold]")
        analyzer = AnalyzerAgent()
        analyze_result = await analyzer.execute(
            task_id=f"workflow_{genre.replace(' ', '_')}_analyze",
            input_dir=str(settings.download_path),
            organize_by_bpm=True,
            detect_key=True
        )
        
        if analyze_result.status.value != "success":
            console.print("[red]✗ Analysis failed[/red]")
            return
        
        console.print(f"[green]✓ Analyzed {analyze_result.result['analyzed_count']} files[/green]")
        
        # 4. Create review queue
        console.print("\n[bold]4️⃣  Creating review queue...[/bold]")
        reporter = ReporterAgent()
        review_result = await reporter.execute(
            task_id=f"workflow_{genre.replace(' ', '_')}_review",
            action="create_review_queue",
            batch_data={
                "batch_name": f"{genre.title()} Collection - {datetime.now().strftime('%Y%m%d')}",
                "samples": analyze_result.result["files"]
            },
            output_dir=str(settings.review_queue_path)
        )
        
        if review_result.status.value == "success":
            console.print(f"[green]✓ Review queue created: {review_result.result['review_file']}[/green]")
            
            # Summary
            elapsed = datetime.now() - start_time
            console.print(f"\n[bold green]✨ Workflow complete![/bold green]")
            console.print(f"  Total time: {elapsed.seconds}s")
            console.print(f"  Samples ready for review: {len(analyze_result.result['files'])}")
            console.print(f"  Review file: {review_result.result['review_file']}")
        else:
            console.print("[red]✗ Review queue creation failed[/red]")
    
    asyncio.run(run_workflow())


@app.command()
def config(
    show: bool = typer.Option(True, "--show/--no-show", help="Show current configuration"),
    validate: bool = typer.Option(False, "--validate", "-v", help="Validate configuration"),
) -> None:
    """
    Display and validate configuration.
    
    Examples:
        sp404agent config
        sp404agent config --validate
    """
    if show:
        table = Table(title="SP404MK2 Agent Configuration")
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        table.add_column("Status", style="green")
        
        # Check each setting
        configs = [
            ("Download Path", str(settings.download_path), "✅" if Path(settings.download_path).exists() else "⚠️"),
            ("Sample Path", str(settings.sample_path), "✅" if Path(settings.sample_path).exists() else "⚠️"),
            ("Review Queue Path", str(settings.review_queue_path), "✅" if Path(settings.review_queue_path).exists() else "⚠️"),
            ("Sample Rate", f"{settings.default_sample_rate} Hz", "✅"),
            ("Bit Depth", f"{settings.default_bit_depth} bit", "✅"),
            ("Max Download Size", f"{settings.max_download_size_mb} MB", "✅"),
            ("Daily Token Limit", f"{settings.daily_token_limit:,}", "✅"),
            ("Cost Alert Threshold", f"${settings.cost_alert_threshold_usd}", "✅"),
        ]
        
        for setting, value, status in configs:
            table.add_row(setting, value, status)
        
        console.print(table)
    
    if validate:
        console.print("\n[bold]Validating configuration...[/bold]\n")
        
        errors = []
        warnings = []
        
        # Check required settings
        if not settings.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY not set - AI features will not work")
        
        if not settings.turso_url or not settings.turso_token:
            warnings.append("Turso database not configured - using local mode")
        
        # Check directories
        for name, path in [
            ("Download", settings.download_path),
            ("Sample", settings.sample_path),
            ("Review Queue", settings.review_queue_path)
        ]:
            if not Path(path).exists():
                warnings.append(f"{name} directory does not exist: {path}")
        
        # Display results
        if errors:
            console.print("[red]❌ Errors found:[/red]")
            for error in errors:
                console.print(f"   {error}")
        
        if warnings:
            console.print("\n[yellow]⚠️  Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"   {warning}")
        
        if not errors:
            console.print("\n[green]✅ Configuration is valid![/green]")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error output"),
) -> None:
    """SP404MK2 Sample Agent - AI-powered sample collection for producers."""
    if quiet:
        setup_logging("ERROR", rich_console=False)
    elif verbose:
        setup_logging("DEBUG")
    else:
        setup_logging()


if __name__ == "__main__":
    app()