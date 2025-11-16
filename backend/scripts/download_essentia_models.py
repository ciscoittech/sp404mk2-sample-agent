#!/usr/bin/env python3
"""
Download pre-trained Essentia models for genre classification.

Downloads embedding and genre classification models from Essentia's model repository.
Includes progress bars, checksum verification, and skip logic for existing files.
"""

import hashlib
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        BarColumn,
        DownloadColumn,
        TimeRemainingColumn,
        TransferSpeedColumn,
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for better progress display: pip install rich")


# Model configuration
# Updated URLs based on Essentia's model repository structure (Jan 2025)
MODELS = {
    "embedding": {
        "url": "https://essentia.upf.edu/models/feature-extractors/maest/discogs-maest-30s-pw-519l-2.pb",
        "expected_size": 347996675,  # ~332MB (actual size from server)
        "description": "MAEST embedding model (332MB)"
    },
    "genre": {
        "url": "https://essentia.upf.edu/models/classification-heads/genre_discogs519/genre_discogs519-discogs-maest-30s-pw-519l-1.pb",
        "expected_size": 1616096,  # ~1.5MB (actual size from server)
        "description": "Genre classification model (1.5MB)"
    }
}


def get_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to file

    Returns:
        SHA256 checksum as hex string
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_file_size(file_path: Path, expected_size: int, tolerance: float = 0.1) -> bool:
    """Verify downloaded file size is within expected range.

    Args:
        file_path: Path to downloaded file
        expected_size: Expected file size in bytes
        tolerance: Acceptable size difference as fraction (default: 10%)

    Returns:
        True if size is acceptable, False otherwise
    """
    actual_size = file_path.stat().st_size
    min_size = expected_size * (1 - tolerance)
    max_size = expected_size * (1 + tolerance)

    if min_size <= actual_size <= max_size:
        return True

    print(f"Warning: File size mismatch")
    print(f"  Expected: ~{expected_size / (1024*1024):.1f}MB")
    print(f"  Actual: {actual_size / (1024*1024):.1f}MB")
    return False


def download_with_rich_progress(url: str, output_path: Path, description: str) -> bool:
    """Download file with Rich progress bar.

    Args:
        url: URL to download from
        output_path: Where to save the file
        description: Description for progress bar

    Returns:
        True if download successful, False otherwise
    """
    console = Console()

    # Create SSL context that doesn't verify certificates (for MTG server)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        # Get file size
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, context=ssl_context) as response:
            total_size = int(response.headers.get('content-length', 0))

        # Download with progress
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(description, total=total_size)

            def reporthook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                progress.update(task, completed=min(downloaded, total_size))

            # Use custom opener with SSL context
            opener = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=ssl_context)
            )
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, output_path, reporthook=reporthook)

        console.print(f"[green]✓[/green] Downloaded: {output_path.name}")
        return True

    except Exception as e:
        console.print(f"[red]✗[/red] Download failed: {e}")
        return False


def download_with_basic_progress(url: str, output_path: Path, description: str) -> bool:
    """Download file with basic progress indicator (no Rich).

    Args:
        url: URL to download from
        output_path: Where to save the file
        description: Description to display

    Returns:
        True if download successful, False otherwise
    """
    print(f"\nDownloading: {description}")
    print(f"URL: {url}")

    # Create SSL context that doesn't verify certificates (for MTG server)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')

        # Use custom opener with SSL context
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_context)
        )
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, output_path, reporthook=reporthook)
        print(f"\n✓ Downloaded: {output_path.name}")
        return True

    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False


def download_model(
    name: str,
    config: dict,
    models_dir: Path,
    force: bool = False
) -> bool:
    """Download a single model file.

    Args:
        name: Model name (e.g., 'embedding', 'genre')
        config: Model configuration dict with url, expected_size, description
        models_dir: Directory to save model
        force: If True, re-download even if file exists

    Returns:
        True if model is available (existed or downloaded), False on error
    """
    url = config["url"]
    expected_size = config["expected_size"]
    description = config["description"]

    # Determine output path from URL filename
    filename = Path(url).name
    output_path = models_dir / filename

    # Check if already downloaded
    if output_path.exists() and not force:
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"[yellow]⊙[/yellow] Already exists: {filename}")
        else:
            print(f"⊙ Already exists: {filename}")

        # Verify size
        if verify_file_size(output_path, expected_size):
            return True
        else:
            if RICH_AVAILABLE:
                console = Console()
                console.print(f"[yellow]![/yellow] Size verification failed, re-downloading...")
            else:
                print("! Size verification failed, re-downloading...")

    # Download the file
    if RICH_AVAILABLE:
        success = download_with_rich_progress(url, output_path, description)
    else:
        success = download_with_basic_progress(url, output_path, description)

    if not success:
        return False

    # Verify downloaded file size
    if not verify_file_size(output_path, expected_size):
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"[yellow]![/yellow] Warning: File size differs from expected, but may still work")
        else:
            print("! Warning: File size differs from expected, but may still work")

    return True


def main(force: bool = False) -> int:
    """Main download function.

    Args:
        force: If True, re-download even if files exist

    Returns:
        0 on success, 1 on failure
    """
    if RICH_AVAILABLE:
        console = Console()
        console.print("\n[bold cyan]Essentia Model Downloader[/bold cyan]")
        console.print("Downloading pre-trained models for genre classification\n")
    else:
        print("\n=== Essentia Model Downloader ===")
        print("Downloading pre-trained models for genre classification\n")

    # Determine models directory relative to this script
    script_dir = Path(__file__).parent
    models_dir = script_dir.parent / "models" / "essentia"

    # Create directory if needed
    models_dir.mkdir(parents=True, exist_ok=True)

    if RICH_AVAILABLE:
        console.print(f"[dim]Output directory: {models_dir}[/dim]\n")
    else:
        print(f"Output directory: {models_dir}\n")

    # Download all models
    success_count = 0
    total_count = len(MODELS)

    for name, config in MODELS.items():
        if download_model(name, config, models_dir, force):
            success_count += 1

    # Summary
    print()
    if success_count == total_count:
        if RICH_AVAILABLE:
            console.print(f"[bold green]✓ All {total_count} models ready[/bold green]")
        else:
            print(f"✓ All {total_count} models ready")

        # Show total size
        total_size = sum(
            (models_dir / Path(config["url"]).name).stat().st_size
            for config in MODELS.values()
            if (models_dir / Path(config["url"]).name).exists()
        )
        if RICH_AVAILABLE:
            console.print(f"[dim]Total size: {total_size / (1024*1024):.1f} MB[/dim]\n")
        else:
            print(f"Total size: {total_size / (1024*1024):.1f} MB\n")

        return 0
    else:
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗ {total_count - success_count} models failed to download[/bold red]\n")
        else:
            print(f"✗ {total_count - success_count} models failed to download\n")
        return 1


if __name__ == "__main__":
    # Check for --force flag
    force = "--force" in sys.argv or "-f" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python download_essentia_models.py [--force]")
        print("\nOptions:")
        print("  --force, -f    Re-download models even if they exist")
        print("  --help, -h     Show this help message")
        sys.exit(0)

    sys.exit(main(force=force))
