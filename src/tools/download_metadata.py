"""
Download metadata management for enhanced review capabilities.
Stores detailed information about downloads for later analysis and review.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..config import settings


class DownloadMetadata(BaseModel):
    """Metadata for a downloaded file."""
    
    download_id: str = Field(description="Unique download identifier")
    source_url: str = Field(description="Original source URL")
    source_platform: str = Field(description="Platform (youtube, soundcloud, etc)")
    
    # File information
    original_filename: str = Field(description="Original filename")
    local_filepath: str = Field(description="Local file path")
    file_size_bytes: int = Field(description="File size in bytes")
    duration_seconds: Optional[float] = Field(description="Audio duration")
    
    # Source metadata
    title: str = Field(description="Video/track title")
    channel: str = Field(description="Channel/artist name")
    description: Optional[str] = Field(default=None, description="Source description")
    upload_date: Optional[str] = Field(default=None, description="Original upload date")
    
    # Musical analysis
    estimated_bpm: Optional[float] = Field(default=None, description="Estimated BPM")
    estimated_key: Optional[str] = Field(default=None, description="Estimated musical key")
    genres: List[str] = Field(default_factory=list, description="Identified genres")
    tags: List[str] = Field(default_factory=list, description="User/system tags")
    
    # Download context
    download_timestamp: datetime = Field(description="When downloaded")
    download_reason: str = Field(description="Why downloaded (search, analysis, etc)")
    user_session: Optional[str] = Field(default=None, description="User session identifier")
    
    # Review status
    review_status: str = Field(default="pending", description="Review status")
    review_notes: Optional[str] = Field(default=None, description="Review notes")
    quality_rating: Optional[int] = Field(default=None, description="Quality rating 1-10")
    
    # Usage tracking
    times_accessed: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(default=None, description="Last access time")
    used_in_projects: List[str] = Field(default_factory=list, description="Projects using this sample")


class DownloadMetadataManager:
    """Manages download metadata storage and retrieval."""
    
    def __init__(self):
        self.metadata_dir = settings.download_metadata_path
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index file for quick lookups
        self.index_file = self.metadata_dir / "download_index.json"
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Ensure the index file exists."""
        if not self.index_file.exists():
            with open(self.index_file, 'w') as f:
                json.dump({"downloads": [], "last_updated": datetime.now(timezone.utc).isoformat()}, f)
    
    def create_download_record(
        self,
        source_url: str,
        local_filepath: str,
        title: str,
        channel: str,
        download_reason: str = "user_request",
        **kwargs
    ) -> DownloadMetadata:
        """Create a new download metadata record."""
        
        download_id = str(uuid.uuid4())
        
        # Get file info
        filepath = Path(local_filepath)
        file_size = filepath.stat().st_size if filepath.exists() else 0
        
        # Determine platform from URL
        platform = "unknown"
        if "youtube.com" in source_url or "youtu.be" in source_url:
            platform = "youtube"
        elif "soundcloud.com" in source_url:
            platform = "soundcloud"
        
        # Create metadata record
        metadata = DownloadMetadata(
            download_id=download_id,
            source_url=source_url,
            source_platform=platform,
            original_filename=filepath.name,
            local_filepath=str(filepath.absolute()),
            file_size_bytes=file_size,
            title=title,
            channel=channel,
            download_timestamp=datetime.now(timezone.utc),
            download_reason=download_reason,
            **kwargs
        )
        
        # Save to file
        self._save_metadata(metadata)
        
        # Update index
        self._update_index(metadata)
        
        return metadata
    
    def _save_metadata(self, metadata: DownloadMetadata):
        """Save metadata to individual file."""
        metadata_file = self.metadata_dir / f"{metadata.download_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)
    
    def _update_index(self, metadata: DownloadMetadata):
        """Update the download index."""
        try:
            with open(self.index_file, 'r') as f:
                index = json.load(f)
        except:
            index = {"downloads": [], "last_updated": ""}
        
        # Add or update entry
        entry = {
            "download_id": metadata.download_id,
            "title": metadata.title,
            "channel": metadata.channel,
            "platform": metadata.source_platform,
            "download_timestamp": metadata.download_timestamp.isoformat(),
            "review_status": metadata.review_status,
            "file_size_bytes": metadata.file_size_bytes
        }
        
        # Remove existing entry if updating
        index["downloads"] = [d for d in index["downloads"] if d["download_id"] != metadata.download_id]
        index["downloads"].append(entry)
        
        # Sort by download time (newest first)
        index["downloads"].sort(key=lambda x: x["download_timestamp"], reverse=True)
        index["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_download(self, download_id: str) -> Optional[DownloadMetadata]:
        """Retrieve download metadata by ID."""
        metadata_file = self.metadata_dir / f"{download_id}.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            return DownloadMetadata(**data)
        except Exception as e:
            print(f"Error loading metadata {download_id}: {e}")
            return None
    
    def update_download(self, download_id: str, **updates) -> bool:
        """Update download metadata."""
        metadata = self.get_download(download_id)
        if not metadata:
            return False
        
        # Update fields
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        # Save updated metadata
        self._save_metadata(metadata)
        self._update_index(metadata)
        
        return True
    
    def list_downloads(
        self,
        limit: int = 50,
        platform: Optional[str] = None,
        review_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List downloads with optional filtering."""
        try:
            with open(self.index_file, 'r') as f:
                index = json.load(f)
        except:
            return []
        
        downloads = index.get("downloads", [])
        
        # Apply filters
        if platform:
            downloads = [d for d in downloads if d.get("platform") == platform]
        
        if review_status:
            downloads = [d for d in downloads if d.get("review_status") == review_status]
        
        return downloads[:limit]
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get download statistics."""
        try:
            with open(self.index_file, 'r') as f:
                index = json.load(f)
        except:
            return {"total_downloads": 0}
        
        downloads = index.get("downloads", [])
        
        # Calculate stats
        stats = {
            "total_downloads": len(downloads),
            "platforms": {},
            "review_status": {},
            "total_size_mb": 0,
            "recent_downloads": len([d for d in downloads if self._is_recent(d.get("download_timestamp"))]),
        }
        
        for download in downloads:
            # Platform stats
            platform = download.get("platform", "unknown")
            stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1
            
            # Review status stats
            status = download.get("review_status", "pending")
            stats["review_status"][status] = stats["review_status"].get(status, 0) + 1
            
            # Size stats
            size_bytes = download.get("file_size_bytes", 0)
            stats["total_size_mb"] += size_bytes / (1024 * 1024)
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        return stats
    
    def _is_recent(self, timestamp_str: Optional[str]) -> bool:
        """Check if timestamp is within last 24 hours."""
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            return (now - timestamp).total_seconds() < 86400  # 24 hours
        except:
            return False
    
    def mark_for_review(self, download_id: str, notes: Optional[str] = None) -> bool:
        """Mark a download for review."""
        return self.update_download(
            download_id,
            review_status="needs_review",
            review_notes=notes
        )
    
    def complete_review(self, download_id: str, rating: int, notes: Optional[str] = None) -> bool:
        """Complete review of a download."""
        return self.update_download(
            download_id,
            review_status="reviewed",
            quality_rating=rating,
            review_notes=notes
        )


# Global instance
download_metadata = DownloadMetadataManager()


# Convenience functions
def create_download_record(source_url: str, local_filepath: str, title: str, channel: str, **kwargs) -> DownloadMetadata:
    """Create a download metadata record."""
    return download_metadata.create_download_record(source_url, local_filepath, title, channel, **kwargs)


def get_download_stats() -> Dict[str, Any]:
    """Get download statistics."""
    return download_metadata.get_download_stats()


def list_recent_downloads(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent downloads."""
    return download_metadata.list_downloads(limit=limit)