"""
YouTube channel, playlist, and video models for sample discovery.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class YouTubeChannel(Base):
    """YouTube channel model for monitoring sample sources."""
    __tablename__ = "youtube_channels"

    id = Column(Integer, primary_key=True, index=True)

    # YouTube identifiers
    channel_id = Column(String, unique=True, nullable=False, index=True)
    channel_name = Column(String, nullable=False, index=True)
    channel_url = Column(String, nullable=False)
    custom_url = Column(String)  # @username

    # Channel metadata
    description = Column(Text)
    subscriber_count = Column(Integer)
    video_count = Column(Integer)
    view_count = Column(Integer)
    country = Column(String)
    published_at = Column(DateTime(timezone=True))

    # Monitoring configuration
    priority = Column(Integer, default=0, index=True)  # Higher = more important
    crawl_frequency_days = Column(Integer, default=7)
    last_crawled_at = Column(DateTime(timezone=True))
    enabled = Column(Boolean, default=True)

    # Categorization
    genres = Column(JSON, default=list)  # ["soul", "funk", "jazz"]
    tags = Column(JSON, default=list)  # Custom tags
    notes = Column(Text)  # User notes about this channel

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    playlists = relationship(
        "YouTubePlaylist",
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    videos = relationship(
        "YouTubeVideo",
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    crawl_history = relationship(
        "ChannelCrawlHistory",
        back_populates="channel",
        cascade="all, delete-orphan"
    )


class YouTubePlaylist(Base):
    """YouTube playlist model for organized content collections."""
    __tablename__ = "youtube_playlists"

    id = Column(Integer, primary_key=True, index=True)

    # YouTube identifiers
    playlist_id = Column(String, unique=True, nullable=False, index=True)
    channel_id = Column(String, ForeignKey("youtube_channels.channel_id"), nullable=False)

    # Playlist metadata
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    video_count = Column(Integer, default=0)
    privacy_status = Column(String)  # public, unlisted, private
    published_at = Column(DateTime(timezone=True))

    # Monitoring
    priority = Column(Integer, default=0)
    last_crawled_at = Column(DateTime(timezone=True))
    enabled = Column(Boolean, default=True)

    # Categorization
    tags = Column(JSON, default=list)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    channel = relationship("YouTubeChannel", back_populates="playlists")
    videos = relationship(
        "YouTubeVideo",
        back_populates="playlist",
        cascade="all, delete-orphan"
    )


class YouTubeVideo(Base):
    """YouTube video model for sample candidates."""
    __tablename__ = "youtube_videos"

    id = Column(Integer, primary_key=True, index=True)

    # YouTube identifiers
    video_id = Column(String, unique=True, nullable=False, index=True)
    channel_id = Column(String, ForeignKey("youtube_channels.channel_id"), nullable=False)
    playlist_id = Column(String, ForeignKey("youtube_playlists.playlist_id"))

    # Video metadata
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    duration_seconds = Column(Integer, index=True)
    upload_date = Column(DateTime(timezone=True), index=True)

    # Engagement metrics
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)

    # Content classification
    category_id = Column(String)
    tags = Column(JSON, default=list)
    is_sample_pack = Column(Boolean, default=False, index=True)
    is_free = Column(Boolean, index=True)

    # Extracted metadata (AI-enhanced)
    estimated_bpm = Column(Integer)
    estimated_key = Column(String)
    genre_tags = Column(JSON, default=list)  # ["soul", "funk", "70s"]
    quality_score = Column(Float, index=True)  # 0.0-1.0, AI-generated

    # Timestamp data
    has_timestamps = Column(Boolean, default=False, index=True)
    timestamps = Column(JSON, default=list)  # [{"time": 0, "title": "Loop 1"}]
    chapters = Column(JSON, default=list)  # yt-dlp extracted chapters

    # Download tracking
    download_status = Column(
        String,
        default="pending",
        index=True
    )  # pending, queued, downloading, downloaded, failed, skipped
    download_id = Column(String)  # TODO: Add ForeignKey("download_metadata.download_id") when download_metadata table is created
    download_priority = Column(Integer, default=0)
    downloaded_at = Column(DateTime(timezone=True))
    download_error = Column(Text)

    # File information (after download)
    file_path = Column(String)
    file_size_bytes = Column(Integer)
    audio_format = Column(String)
    sample_rate = Column(Integer)

    # Filtering metadata
    filter_score = Column(Float)  # Combined filtering score
    filter_reasons = Column(JSON, default=list)  # Why it passed/failed filters

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True))  # When AI analyzed it

    # Relationships
    channel = relationship("YouTubeChannel", back_populates="videos")
    playlist = relationship("YouTubePlaylist", back_populates="videos")


class ChannelCrawlHistory(Base):
    """Track channel crawling operations for monitoring and debugging."""
    __tablename__ = "channel_crawl_history"

    id = Column(Integer, primary_key=True, index=True)

    # Channel reference
    channel_id = Column(String, ForeignKey("youtube_channels.channel_id"), nullable=False)

    # Crawl timing
    crawl_started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    crawl_completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)

    # Crawl results
    status = Column(String, default="running", index=True)  # running, completed, failed
    videos_discovered = Column(Integer, default=0)
    videos_new = Column(Integer, default=0)
    videos_updated = Column(Integer, default=0)
    playlists_discovered = Column(Integer, default=0)

    # API usage
    api_quota_used = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)

    # Error tracking
    error_message = Column(Text)
    error_type = Column(String)

    # Additional metadata
    crawl_type = Column(String)  # full, incremental, priority
    crawl_metadata = Column(JSON, default=dict)  # Extra crawl info (renamed from 'metadata' to avoid SQLAlchemy reserved name)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    channel = relationship("YouTubeChannel", back_populates="crawl_history")


class YouTubeQuotaUsage(Base):
    """Track YouTube API quota usage for rate limiting."""
    __tablename__ = "youtube_quota_usage"

    id = Column(Integer, primary_key=True, index=True)

    # Date tracking (one row per day)
    date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)

    # Quota usage
    quota_used = Column(Integer, default=0)
    quota_limit = Column(Integer, default=10000)
    api_calls = Column(Integer, default=0)

    # Breakdown by operation
    quota_by_operation = Column(JSON, default=dict)  # {"channels.list": 10, "videos.list": 50}

    # Alerts
    alert_sent = Column(Boolean, default=False)
    alert_threshold_reached = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
