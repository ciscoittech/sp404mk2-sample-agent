"""
User preferences model for system-wide settings.

Uses single-row design with id=1 for system-wide preferences.
This is perfect for MVP where all users share the same settings.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class UserPreference(Base):
    """User preferences model using single-row design (id=1)."""
    __tablename__ = "user_preferences"

    # Single-row design (always id=1)
    id = Column(Integer, primary_key=True, default=1)

    # Vibe analysis preferences
    vibe_analysis_model = Column(String, nullable=False, default="qwen/qwen3-7b-it")
    auto_vibe_analysis = Column(Boolean, nullable=False, default=True)
    auto_audio_features = Column(Boolean, nullable=False, default=True)

    # Batch processing preferences
    batch_processing_model = Column(String, nullable=False, default="qwen/qwen3-7b-it")
    batch_auto_analyze = Column(Boolean, nullable=False, default=False)

    # Cost management
    max_cost_per_request = Column(Float, nullable=True, default=None)

    # SP-404 export preferences
    default_export_format = Column(String, nullable=False, default="wav")
    default_export_organization = Column(String, nullable=False, default="flat")
    auto_sanitize_filenames = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
