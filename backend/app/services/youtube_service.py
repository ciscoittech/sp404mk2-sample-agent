"""
YouTube Data API service for channel monitoring and video discovery.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
import re

from app.models.youtube import (
    YouTubeChannel,
    YouTubePlaylist,
    YouTubeVideo,
    ChannelCrawlHistory,
    YouTubeQuotaUsage
)
from src.config import settings


class QuotaExceededError(Exception):
    """Raised when YouTube API quota is exceeded."""
    pass


class YouTubeService:
    """Service for YouTube Data API operations with quota tracking."""

    # API quota costs (units per operation)
    QUOTA_COSTS = {
        "channels.list": 1,
        "playlists.list": 1,
        "playlistItems.list": 1,
        "videos.list": 1,
        "search.list": 100
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.youtube = None
        if settings.youtube_api_key:
            self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)

    async def _track_quota_usage(self, operation: str, units: int = None):
        """Track YouTube API quota usage."""
        if units is None:
            units = self.QUOTA_COSTS.get(operation, 1)

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Get or create today's quota record
        result = await self.db.execute(
            select(YouTubeQuotaUsage).where(YouTubeQuotaUsage.date == today)
        )
        quota_record = result.scalar_one_or_none()

        if not quota_record:
            quota_record = YouTubeQuotaUsage(
                date=today,
                quota_used=0,
                quota_limit=settings.youtube_daily_quota,
                quota_by_operation={}
            )
            self.db.add(quota_record)

        # Update quota usage
        quota_record.quota_used += units
        quota_record.api_calls += 1

        # Update operation breakdown
        operations = quota_record.quota_by_operation or {}
        operations[operation] = operations.get(operation, 0) + units
        quota_record.quota_by_operation = operations

        # Check for threshold alerts
        usage_percent = quota_record.quota_used / quota_record.quota_limit
        if usage_percent >= settings.youtube_quota_alert_threshold and not quota_record.alert_threshold_reached:
            quota_record.alert_threshold_reached = True
            # TODO: Send alert notification

        await self.db.commit()

        return quota_record

    async def get_remaining_quota(self) -> int:
        """Get remaining YouTube API quota for today."""
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        result = await self.db.execute(
            select(YouTubeQuotaUsage).where(YouTubeQuotaUsage.date == today)
        )
        quota_record = result.scalar_one_or_none()

        if not quota_record:
            return settings.youtube_daily_quota

        return quota_record.quota_limit - quota_record.quota_used

    async def check_quota_available(self, estimated_units: int) -> bool:
        """Check if sufficient quota is available."""
        remaining = await self.get_remaining_quota()
        return remaining >= estimated_units

    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel information from YouTube API.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Channel data dict or None if not found

        Raises:
            QuotaExceededError: If daily quota is exceeded
        """
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        # Check quota
        if not await self.check_quota_available(1):
            raise QuotaExceededError("Daily YouTube API quota exceeded")

        try:
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=channel_id
            )
            response = request.execute()

            await self._track_quota_usage("channels.list")

            if not response.get("items"):
                return None

            item = response["items"][0]
            return {
                "channel_id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "custom_url": item["snippet"].get("customUrl"),
                "country": item["snippet"].get("country"),
                "published_at": datetime.fromisoformat(
                    item["snippet"]["publishedAt"].replace("Z", "+00:00")
                ),
                "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                "video_count": int(item["statistics"].get("videoCount", 0)),
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"]
            }

        except HttpError as e:
            if e.resp.status == 403:
                raise QuotaExceededError("YouTube API quota exceeded")
            raise

    async def get_channel_playlists(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get playlists for a channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum playlists to return

        Returns:
            List of playlist data dicts
        """
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        # Estimate quota: 1 unit per request, may need multiple pages
        estimated_quota = max(1, max_results // 50 + 1)
        if not await self.check_quota_available(estimated_quota):
            raise QuotaExceededError("Insufficient YouTube API quota")

        playlists = []
        next_page_token = None

        try:
            while len(playlists) < max_results:
                request = self.youtube.playlists().list(
                    part="snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=min(50, max_results - len(playlists)),
                    pageToken=next_page_token
                )
                response = request.execute()

                await self._track_quota_usage("playlists.list")

                for item in response.get("items", []):
                    playlists.append({
                        "playlist_id": item["id"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "video_count": int(item["contentDetails"].get("itemCount", 0)),
                        "privacy_status": item["status"]["privacyStatus"] if "status" in item else "public",
                        "published_at": datetime.fromisoformat(
                            item["snippet"]["publishedAt"].replace("Z", "+00:00")
                        )
                    })

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            return playlists

        except HttpError as e:
            if e.resp.status == 403:
                raise QuotaExceededError("YouTube API quota exceeded")
            raise

    async def get_playlist_videos(
        self,
        playlist_id: str,
        max_results: int = 50,
        published_after: Optional[datetime] = None
    ) -> List[str]:
        """
        Get video IDs from a playlist.

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum videos to return
            published_after: Only return videos published after this date

        Returns:
            List of video IDs
        """
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        # Estimate quota
        estimated_quota = max(1, max_results // 50 + 1)
        if not await self.check_quota_available(estimated_quota):
            raise QuotaExceededError("Insufficient YouTube API quota")

        video_ids = []
        next_page_token = None

        try:
            while len(video_ids) < max_results:
                request = self.youtube.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(video_ids)),
                    pageToken=next_page_token
                )
                response = request.execute()

                await self._track_quota_usage("playlistItems.list")

                for item in response.get("items", []):
                    video_id = item["snippet"]["resourceId"]["videoId"]

                    # Filter by publish date if specified
                    if published_after:
                        published = datetime.fromisoformat(
                            item["snippet"]["publishedAt"].replace("Z", "+00:00")
                        )
                        if published < published_after:
                            continue

                    video_ids.append(video_id)

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            return video_ids

        except HttpError as e:
            if e.resp.status == 403:
                raise QuotaExceededError("YouTube API quota exceeded")
            raise

    async def get_videos_info(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for multiple videos.

        Args:
            video_ids: List of YouTube video IDs (max 50)

        Returns:
            List of video data dicts
        """
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        if len(video_ids) > 50:
            raise ValueError("Maximum 50 video IDs per request")

        if not await self.check_quota_available(1):
            raise QuotaExceededError("Insufficient YouTube API quota")

        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids)
            )
            response = request.execute()

            await self._track_quota_usage("videos.list")

            videos = []
            for item in response.get("items", []):
                # Parse ISO 8601 duration (PT1M30S -> 90 seconds)
                duration = isodate.parse_duration(item["contentDetails"]["duration"])
                duration_seconds = int(duration.total_seconds())

                # Extract tags from description or title
                tags = item["snippet"].get("tags", [])

                videos.append({
                    "video_id": item["id"],
                    "channel_id": item["snippet"]["channelId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "duration_seconds": duration_seconds,
                    "upload_date": datetime.fromisoformat(
                        item["snippet"]["publishedAt"].replace("Z", "+00:00")
                    ),
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                    "category_id": item["snippet"]["categoryId"],
                    "tags": tags,
                    "thumbnails": item["snippet"].get("thumbnails", {})
                })

            return videos

        except HttpError as e:
            if e.resp.status == 403:
                raise QuotaExceededError("YouTube API quota exceeded")
            raise

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from YouTube URL."""
        # Try channel ID format: UC...
        if url.startswith("UC") and len(url) == 24:
            return url

        # Try URL patterns
        patterns = [
            r'youtube\.com\/channel\/([UC][0-9A-Za-z_-]{22})',
            r'youtube\.com\/@([^\/\?]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL."""
        # Try playlist ID format
        if url.startswith("PL") or url.startswith("UU"):
            return url

        # Try URL pattern
        match = re.search(r'[?&]list=([0-9A-Za-z_-]+)', url)
        if match:
            return match.group(1)

        return None

    @staticmethod
    def parse_timestamps_from_description(description: str) -> List[Dict[str, Any]]:
        """
        Parse timestamps from video description.

        Looks for patterns like:
        - 0:00 Title
        - 1:30 Title
        - [0:00] Title
        - 00:00 - Title

        Returns:
            List of {"time_seconds": int, "title": str}
        """
        if not description:
            return []

        timestamps = []
        lines = description.split('\n')

        # Common timestamp patterns
        patterns = [
            r'(\d{1,2}):(\d{2})\s*[-–—]?\s*(.+)',  # 0:00 - Title or 0:00 Title
            r'\[(\d{1,2}):(\d{2})\]\s*(.+)',  # [0:00] Title
            r'(\d{1,2}):(\d{2}):(\d{2})\s*[-–—]?\s*(.+)'  # 0:00:00 - Title
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()

                    if len(groups) == 3:  # MM:SS format
                        minutes, seconds, title = groups
                        time_seconds = int(minutes) * 60 + int(seconds)
                    elif len(groups) == 4:  # HH:MM:SS format
                        hours, minutes, seconds, title = groups
                        time_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
                    else:
                        continue

                    timestamps.append({
                        "time_seconds": time_seconds,
                        "title": title.strip()
                    })
                    break

        return timestamps

    @staticmethod
    def detect_is_sample_pack(title: str, description: str = "") -> bool:
        """Detect if video is a sample pack based on title/description."""
        keywords = [
            "sample pack",
            "loop kit",
            "drum kit",
            "sound kit",
            "free samples",
            "free loops"
        ]

        text = (title + " " + (description or "")).lower()
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def detect_is_free(title: str, description: str = "") -> bool:
        """Detect if content is marked as free."""
        keywords = [
            "[free]",
            "(free)",
            "free download",
            "free sample",
            "royalty free"
        ]

        text = (title + " " + (description or "")).lower()
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def extract_bpm_from_text(text: str) -> Optional[int]:
        """Extract BPM from text like '120 BPM' or '90bpm'."""
        match = re.search(r'(\d{2,3})\s*bpm', text, re.IGNORECASE)
        if match:
            bpm = int(match.group(1))
            if 40 <= bpm <= 200:  # Reasonable BPM range
                return bpm
        return None

    @staticmethod
    def extract_genres_from_text(text: str) -> List[str]:
        """Extract genre tags from text."""
        genres = [
            "soul", "funk", "jazz", "hip-hop", "trap", "drill",
            "r&b", "blues", "gospel", "disco", "house", "electronic",
            "rock", "indie", "lo-fi", "boom bap"
        ]

        text_lower = text.lower()
        found_genres = []

        for genre in genres:
            if genre in text_lower:
                found_genres.append(genre)

        return found_genres
