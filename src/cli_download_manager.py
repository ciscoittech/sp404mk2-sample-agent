#!/usr/bin/env python3
"""
Download Manager CLI - Review and manage downloaded content.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

from .tools.download_metadata import download_metadata, DownloadMetadata

app = typer.Typer(help="SP404MK2 Download Manager - Review and manage downloaded content")
console = Console()


@app.command()
def list(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of downloads to show"),
    platform: str = typer.Option(None, "--platform", "-p", help="Filter by platform (youtube, soundcloud)"),
    status: str = typer.Option(None, "--status", "-s", help="Filter by review status"),
):
    """List downloaded content."""
    downloads = download_metadata.list_downloads(limit=limit, platform=platform, review_status=status)
    
    if not downloads:
        console.print("[yellow]No downloads found[/yellow]")
        return
    
    # Create table
    table = Table(title=f"Downloaded Content ({len(downloads)} items)")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Channel", style="green", width=20)
    table.add_column("Platform", style="yellow", width=10)
    table.add_column("Size", style="blue", width=8)
    table.add_column("Status", style="magenta", width=12)
    table.add_column("Downloaded", style="dim", width=12)
    
    for download in downloads:
        # Format size
        size_mb = download.get('file_size_bytes', 0) / (1024 * 1024)
        size_str = f"{size_mb:.1f}MB" if size_mb > 0 else "Unknown"
        
        # Format date
        date_str = download.get('download_timestamp', '')[:10] if download.get('download_timestamp') else 'Unknown'
        
        # Truncate title
        title = download.get('title', 'Unknown')
        if len(title) > 40:
            title = title[:37] + "..."
        
        table.add_row(
            download.get('download_id', '')[:8],
            title,
            download.get('channel', 'Unknown')[:20],
            download.get('platform', 'unknown'),
            size_str,
            download.get('review_status', 'pending'),
            date_str
        )
    
    console.print(table)


@app.command()
def show(download_id: str):
    """Show detailed information about a download."""
    metadata = download_metadata.get_download(download_id)
    
    if not metadata:
        console.print(f"[red]Download {download_id} not found[/red]")
        return
    
    # Create detailed view
    info_text = f"""[bold]Title:[/bold] {metadata.title}
[bold]Channel:[/bold] {metadata.channel}
[bold]Platform:[/bold] {metadata.source_platform}
[bold]URL:[/bold] {metadata.source_url}

[bold]File Information:[/bold]
• Local Path: {metadata.local_filepath}
• File Size: {metadata.file_size_bytes / (1024 * 1024):.2f} MB
• Duration: {metadata.duration_seconds or 'Unknown'} seconds

[bold]Download Details:[/bold]
• Downloaded: {metadata.download_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
• Reason: {metadata.download_reason}
• Review Status: {metadata.review_status}

[bold]Analysis:[/bold]
• Estimated BPM: {metadata.estimated_bpm or 'Not analyzed'}
• Estimated Key: {metadata.estimated_key or 'Not analyzed'}
• Genres: {', '.join(metadata.genres) if metadata.genres else 'None identified'}
• Tags: {', '.join(metadata.tags) if metadata.tags else 'None'}

[bold]Usage:[/bold]
• Times Accessed: {metadata.times_accessed}
• Last Accessed: {metadata.last_accessed.strftime('%Y-%m-%d %H:%M:%S') if metadata.last_accessed else 'Never'}
• Used in Projects: {', '.join(metadata.used_in_projects) if metadata.used_in_projects else 'None'}"""
    
    if metadata.review_notes:
        info_text += f"\n\n[bold]Review Notes:[/bold]\n{metadata.review_notes}"
    
    panel = Panel(info_text, title=f"Download Details: {download_id[:8]}", border_style="cyan")
    console.print(panel)


@app.command() 
def stats():
    """Show download statistics."""
    stats = download_metadata.get_download_stats()
    
    stats_text = f"""[bold]Total Downloads:[/bold] {stats['total_downloads']}
[bold]Total Size:[/bold] {stats['total_size_mb']} MB
[bold]Recent Downloads (24h):[/bold] {stats['recent_downloads']}

[bold]Platforms:[/bold]"""
    
    for platform, count in stats.get('platforms', {}).items():
        stats_text += f"\n• {platform}: {count}"
    
    stats_text += "\n\n[bold]Review Status:[/bold]"
    for status, count in stats.get('review_status', {}).items():
        stats_text += f"\n• {status}: {count}"
    
    panel = Panel(stats_text, title="Download Statistics", border_style="green")
    console.print(panel)


@app.command()
def review(
    download_id: str,
    rating: int = typer.Option(..., "--rating", "-r", help="Quality rating 1-10"),
    notes: str = typer.Option("", "--notes", "-n", help="Review notes")
):
    """Review a download."""
    if rating < 1 or rating > 10:
        console.print("[red]Rating must be between 1 and 10[/red]")
        return
    
    success = download_metadata.complete_review(download_id, rating, notes)
    
    if success:
        console.print(f"[green]✓ Review completed for {download_id[:8]}[/green]")
        console.print(f"  Rating: {rating}/10")
        if notes:
            console.print(f"  Notes: {notes}")
    else:
        console.print(f"[red]✗ Failed to review {download_id}[/red]")


@app.command()
def tag(
    download_id: str,
    tags: str = typer.Option(..., "--tags", "-t", help="Comma-separated tags")
):
    """Add tags to a download."""
    tag_list = [tag.strip() for tag in tags.split(',')]
    
    metadata = download_metadata.get_download(download_id)
    if not metadata:
        console.print(f"[red]Download {download_id} not found[/red]")
        return
    
    # Merge with existing tags
    existing_tags = set(metadata.tags)
    new_tags = existing_tags.union(set(tag_list))
    
    success = download_metadata.update_download(download_id, tags=list(new_tags))
    
    if success:
        console.print(f"[green]✓ Tags updated for {download_id[:8]}[/green]")
        console.print(f"  Tags: {', '.join(sorted(new_tags))}")
    else:
        console.print(f"[red]✗ Failed to update tags for {download_id}[/red]")


@app.command()
def cleanup(
    remove_files: bool = typer.Option(False, "--remove-files", help="Also remove physical files"),
    status: str = typer.Option(None, "--status", help="Only cleanup specific status")
):
    """Clean up download records and optionally files."""
    downloads = download_metadata.list_downloads(limit=1000, review_status=status)
    
    if not downloads:
        console.print("[yellow]No downloads to clean up[/yellow]")
        return
    
    removed_count = 0
    for download in downloads:
        download_id = download.get('download_id', '')
        
        if remove_files:
            # Remove physical file if it exists
            metadata = download_metadata.get_download(download_id)
            if metadata and Path(metadata.local_filepath).exists():
                try:
                    Path(metadata.local_filepath).unlink()
                    console.print(f"[dim]Removed file: {metadata.local_filepath}[/dim]")
                except Exception as e:
                    console.print(f"[red]Failed to remove file: {e}[/red]")
        
        # Remove metadata record
        metadata_file = download_metadata.metadata_dir / f"{download_id}.json"
        if metadata_file.exists():
            try:
                metadata_file.unlink()
                removed_count += 1
            except Exception as e:
                console.print(f"[red]Failed to remove metadata: {e}[/red]")
    
    if removed_count > 0:
        console.print(f"[green]✓ Cleaned up {removed_count} download records[/green]")
        
        # Update index
        download_metadata._ensure_index_exists()
    else:
        console.print("[yellow]No records were cleaned up[/yellow]")


@app.command()
def export(
    output_file: str = typer.Option("downloads_export.json", "--output", "-o", help="Output file"),
    platform: str = typer.Option(None, "--platform", help="Filter by platform")
):
    """Export download metadata to JSON."""
    downloads = download_metadata.list_downloads(limit=1000, platform=platform)
    
    # Get full metadata for each download
    full_exports = []
    for download in downloads:
        download_id = download.get('download_id', '')
        metadata = download_metadata.get_download(download_id)
        if metadata:
            full_exports.append(metadata.model_dump())
    
    # Write to file
    import json
    with open(output_file, 'w') as f:
        json.dump(full_exports, f, indent=2, default=str)
    
    console.print(f"[green]✓ Exported {len(full_exports)} downloads to {output_file}[/green]")


if __name__ == "__main__":
    app()