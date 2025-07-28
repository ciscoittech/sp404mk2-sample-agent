"""Downloader Agent - Downloads samples from various sources."""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path

from ..logging_config import AgentLogger
from ..tools.download import (
    download_youtube, download_direct, download_batch,
    validate_youtube_url, get_youtube_metadata
)
from ..tools.audio import convert_format
from ..tools import database
from .base import Agent, AgentResult, AgentStatus


class DownloaderAgent(Agent):
    """Agent responsible for downloading samples from YouTube and direct sources."""
    
    def __init__(self):
        """Initialize the Downloader Agent."""
        super().__init__("downloader")
        self.logger = AgentLogger(self.name)
        
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Download samples from specified sources.
        
        Args:
            task_id: Unique task identifier
            source_url: Single URL to download from
            source_urls: List of URLs to download from
            output_dir: Directory to save downloads
            sample_type: Type of samples to download
            max_count: Maximum number of samples to download
            audio_format: Target audio format (default: wav)
            sample_rate: Target sample rate (default: 44100)
            bit_depth: Target bit depth (default: 16)
            convert_to_mono: Convert to mono (default: False)
            progress_callback: Optional progress callback
            
        Returns:
            AgentResult with download details
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting download task")
        started_at = datetime.now(timezone.utc)
        
        # Extract parameters
        source_url = kwargs.get("source_url")
        source_urls = kwargs.get("source_urls", [])
        output_dir = kwargs.get("output_dir", "./downloads")
        sample_type = kwargs.get("sample_type", "all")
        max_count = kwargs.get("max_count", 10)
        audio_format = kwargs.get("audio_format", "wav")
        sample_rate = kwargs.get("sample_rate", 44100)
        bit_depth = kwargs.get("bit_depth", 16)
        convert_to_mono = kwargs.get("convert_to_mono", False)
        progress_callback = kwargs.get("progress_callback")
        
        # Validate inputs
        if not source_url and not source_urls:
            error_msg = "No source_url or source_urls provided"
            self.logger.error(error_msg)
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": error_msg
            })
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=error_msg,
                started_at=started_at,
            )
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            # Update task status
            await database.update_task_status(task_id, "in_progress")
            
            # Prepare URLs list
            urls = source_urls[:max_count] if source_urls else [source_url]
            urls = urls[:max_count]  # Respect max_count
            
            downloaded_files = []
            
            # Download files
            if len(urls) > 1:
                # Batch download
                self.logger.info(f"Downloading {len(urls)} files")
                results = await download_batch(urls, output_dir)
                
                for i, result in enumerate(results):
                    if result.get("success"):
                        await self._process_downloaded_file(
                            result, task_id, sample_type, 
                            audio_format, sample_rate, bit_depth,
                            convert_to_mono
                        )
                        downloaded_files.append(result)
                    else:
                        self.logger.warning(f"Failed to download: {urls[i]}")
            else:
                # Single download
                url = urls[0]
                self.logger.info(f"Downloading from {url}")
                
                # Get metadata first if YouTube
                metadata = {}
                if validate_youtube_url(url):
                    try:
                        metadata = await get_youtube_metadata(url)
                    except Exception as e:
                        self.logger.warning(f"Failed to get metadata: {e}")
                
                # Download
                if validate_youtube_url(url):
                    result = await download_youtube(
                        url, output_dir, audio_format, 
                        sample_rate, bit_depth, progress_callback
                    )
                else:
                    filename = os.path.basename(url) or "sample.wav"
                    output_path = os.path.join(output_dir, filename)
                    result = await download_direct(
                        url, output_path, progress_callback
                    )
                
                if result.get("success"):
                    result["metadata"] = {**metadata, **result.get("metadata", {})}
                    await self._process_downloaded_file(
                        result, task_id, sample_type,
                        audio_format, sample_rate, bit_depth,
                        convert_to_mono
                    )
                    downloaded_files.append(result)
                else:
                    raise Exception(f"Download failed: {result.get('error')}")
            
            # Update task status
            await database.update_task_status(task_id, "completed")
            
            # Log success
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "info",
                "message": f"Successfully downloaded {len(downloaded_files)} files",
                "context": {"downloaded_count": len(downloaded_files)}
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result={
                    "downloaded_count": len(downloaded_files),
                    "files": downloaded_files,
                    "source": source_url or "multiple",
                },
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                metadata={
                    "sample_type": sample_type,
                    "max_count": max_count,
                    "audio_format": audio_format
                }
            )
            
        except Exception as e:
            self.logger.exception(f"Download failed: {str(e)}")
            
            # Log error
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": f"Download failed: {str(e)}",
                "context": {"error": str(e)}
            })
            
            # Update task status
            await database.update_task_status(task_id, "failed")
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _process_downloaded_file(
        self, 
        download_result: Dict[str, Any],
        task_id: str,
        sample_type: str,
        audio_format: str,
        sample_rate: int,
        bit_depth: int,
        convert_to_mono: bool
    ) -> None:
        """
        Process a downloaded file: convert format and save to database.
        
        Args:
            download_result: Result from download operation
            task_id: Task ID
            sample_type: Type of sample
            audio_format: Target format
            sample_rate: Target sample rate
            bit_depth: Target bit depth
            convert_to_mono: Whether to convert to mono
        """
        output_path = download_result.get("output_path")
        
        # Convert format if needed
        if output_path and not output_path.endswith(f".{audio_format}"):
            try:
                new_path = output_path.rsplit(".", 1)[0] + f".{audio_format}"
                channels = 1 if convert_to_mono else 2
                
                convert_result = await convert_format(
                    output_path, new_path,
                    format=audio_format,
                    sample_rate=sample_rate,
                    bit_depth=bit_depth,
                    channels=channels
                )
                
                if convert_result.get("success"):
                    # Remove original file
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    output_path = new_path
                    download_result["output_path"] = new_path
            except Exception as e:
                self.logger.warning(f"Format conversion failed: {e}")
        
        # Save to database
        metadata = download_result.get("metadata", {})
        sample_data = {
            "filename": os.path.basename(output_path),
            "file_path": output_path,
            "source_url": download_result.get("url", ""),
            "source_type": "youtube" if validate_youtube_url(download_result.get("url", "")) else "direct",
            "style": sample_type,
            "genre": metadata.get("genre", ""),
            "duration_seconds": metadata.get("duration"),
            "file_size_bytes": download_result.get("size_bytes"),
            "sample_rate": sample_rate,
            "bit_depth": bit_depth,
            "status": "pending"
        }
        
        await database.create_sample(sample_data)