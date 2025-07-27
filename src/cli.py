"""Command-line interface for SP404MK2 Sample Agent."""

from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from .config import settings
from .logging_config import setup_logging

# Create CLI app
app = typer.Typer(
    name="sp404agent",
    help="AI-powered sample collection agent for SP404MK2",
    add_completion=False,
)

console = Console()


@app.command()
def collect(
    source: str = typer.Argument(..., help="Source URL or channel to collect from"),
    style: str = typer.Option("lo-fi", "--style", "-s", help="Music style to collect"),
    bpm: str = typer.Option("70-110", "--bpm", "-b", help="BPM range (e.g., '80-95')"),
    count: int = typer.Option(10, "--count", "-c", help="Number of samples to collect"),
    create_issue: bool = typer.Option(True, "--issue/--no-issue", help="Create GitHub issue"),
) -> None:
    """
    Start a sample collection task.
    
    Example:
        sp404agent collect "https://youtube.com/playlist?..." --style jazz --bpm 90-100
    """
    console.print(f"[bold green]Starting sample collection task[/bold green]")
    console.print(f"Source: {source}")
    console.print(f"Style: {style}")
    console.print(f"BPM Range: {bpm}")
    console.print(f"Target Count: {count}")
    
    if create_issue:
        console.print("\n[yellow]Creating GitHub issue for tracking...[/yellow]")
        # TODO: Implement GitHub issue creation
        
    # TODO: Implement collection logic
    console.print("\n[red]Collection not yet implemented[/red]")


@app.command()
def review(
    list_pending: bool = typer.Option(False, "--list", "-l", help="List pending reviews"),
    approve: Optional[str] = typer.Option(None, "--approve", "-a", help="Approve samples (comma-separated IDs)"),
    reject: Optional[str] = typer.Option(None, "--reject", "-r", help="Reject samples (comma-separated IDs)"),
) -> None:
    """
    Review pending samples in the queue.
    
    Examples:
        sp404agent review --list
        sp404agent review --approve 1,3,5 --reject 2,4
    """
    if list_pending:
        # TODO: Load and display pending reviews
        console.print("[bold]Pending Sample Reviews[/bold]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Batch", width=20)
        table.add_column("Source", width=30)
        table.add_column("Count", justify="right")
        table.add_column("Date", width=12)
        
        # TODO: Add actual data
        table.add_row("1", "JAZZ-DRUMS-001", "YouTube - Vintage Jazz", "15", "2025-01-27")
        
        console.print(table)
        return
        
    if approve:
        approved_ids = [id.strip() for id in approve.split(",")]
        console.print(f"[green]Approving samples: {approved_ids}[/green]")
        # TODO: Implement approval logic
        
    if reject:
        rejected_ids = [id.strip() for id in reject.split(",")]
        console.print(f"[red]Rejecting samples: {rejected_ids}[/red]")
        # TODO: Implement rejection logic


@app.command()
def status(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Show status for specific agent"),
    tasks: bool = typer.Option(False, "--tasks", "-t", help="Show active tasks"),
) -> None:
    """
    Check agent and system status.
    
    Examples:
        sp404agent status
        sp404agent status --agent downloader
        sp404agent status --tasks
    """
    console.print("[bold]SP404MK2 Sample Agent Status[/bold]\n")
    
    if agent:
        # TODO: Show specific agent status
        console.print(f"Agent: {agent}")
        console.print("Status: [green]Ready[/green]")
    else:
        # Show all agents status
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan", width=20)
        table.add_column("Status", width=12)
        table.add_column("Last Active", width=20)
        table.add_column("Tasks Completed", justify="right")
        
        # TODO: Get actual agent statuses
        agents = [
            ("Architect", "[green]Idle[/green]", "Never", "0"),
            ("Coder", "[green]Idle[/green]", "Never", "0"),
            ("Collector", "[green]Idle[/green]", "Never", "0"),
            ("Downloader", "[green]Idle[/green]", "Never", "0"),
            ("Analyzer", "[green]Idle[/green]", "Never", "0"),
            ("Reporter", "[green]Idle[/green]", "Never", "0"),
        ]
        
        for agent_data in agents:
            table.add_row(*agent_data)
            
        console.print(table)
    
    if tasks:
        console.print("\n[bold]Active Tasks[/bold]")
        # TODO: Show active tasks
        console.print("[dim]No active tasks[/dim]")


@app.command()
def run(
    agent: str = typer.Argument(..., help="Agent name to run"),
    issue: int = typer.Argument(..., help="GitHub issue number"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without executing"),
) -> None:
    """
    Manually run a specific agent on a GitHub issue.
    
    Example:
        sp404agent run downloader 123
    """
    console.print(f"[bold]Running {agent} agent on issue #{issue}[/bold]")
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No actions will be performed[/yellow]")
    
    # TODO: Implement agent execution
    console.print(f"\n[red]Agent execution not yet implemented[/red]")


@app.command()
def logs(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Filter logs by agent"),
    tail: int = typer.Option(20, "--tail", "-n", help="Number of recent logs to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
) -> None:
    """
    View agent logs.
    
    Examples:
        sp404agent logs --tail 50
        sp404agent logs --agent analyzer --follow
    """
    console.print(f"[bold]Agent Logs[/bold]")
    
    if agent:
        console.print(f"Filtering for agent: {agent}")
    
    console.print(f"Showing last {tail} entries")
    
    if follow:
        console.print("[yellow]Following logs... (Ctrl+C to stop)[/yellow]")
    
    # TODO: Implement log viewing
    console.print("\n[red]Log viewing not yet implemented[/red]")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    validate: bool = typer.Option(False, "--validate", "-v", help="Validate configuration"),
) -> None:
    """
    Manage agent configuration.
    
    Examples:
        sp404agent config --show
        sp404agent config --validate
    """
    if show:
        console.print("[bold]Current Configuration[/bold]\n")
        
        # Group settings by category
        categories = {
            "API Keys": ["openrouter_api_key", "turso_url", "github_token"],
            "Agent Settings": ["agent_log_level", "agent_max_retries", "agent_timeout_seconds"],
            "File Paths": ["download_path", "sample_path", "review_queue_path"],
            "Audio Settings": ["default_sample_rate", "default_bit_depth", "max_download_size_mb"],
            "Cost Limits": ["daily_token_limit", "cost_alert_threshold_usd"],
            "Models": ["architect_model", "coder_models", "collector_model"],
        }
        
        for category, fields in categories.items():
            console.print(f"[cyan]{category}:[/cyan]")
            for field in fields:
                value = getattr(settings, field, "Not set")
                # Mask sensitive values
                if "key" in field.lower() or "token" in field.lower():
                    if value and value != "Not set":
                        value = value[:8] + "..." if len(str(value)) > 8 else "***"
                console.print(f"  {field}: {value}")
            console.print()
    
    if validate:
        console.print("[bold]Validating configuration...[/bold]\n")
        
        errors = []
        warnings = []
        
        # Check required fields
        if not settings.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY is not set")
        if not settings.turso_url:
            warnings.append("TURSO_URL is not set (database features disabled)")
        if not settings.turso_token:
            warnings.append("TURSO_TOKEN is not set (database features disabled)")
            
        # Display results
        if errors:
            console.print("[red]Errors:[/red]")
            for error in errors:
                console.print(f"  ❌ {error}")
        
        if warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  ⚠️  {warning}")
                
        if not errors and not warnings:
            console.print("[green]✅ Configuration is valid![/green]")
        elif not errors:
            console.print("\n[green]Configuration is valid with warnings[/green]")
        else:
            console.print("\n[red]Configuration has errors that must be fixed[/red]")


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