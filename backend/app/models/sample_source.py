"""
Sample source model for tracking sample origins and attribution
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime

from app.db.base import Base


class SourceType(str, Enum):
    """Source type enumeration for sample origins."""
    YOUTUBE = "youtube"
    UPLOAD = "upload"
    SAMPLE_PACK = "sample_pack"
    BATCH_IMPORT = "batch_import"


class LicenseType(str, Enum):
    """License type enumeration for sample usage rights."""
    ROYALTY_FREE = "royalty_free"
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"


class SampleSource(Base):
    """Sample source model for tracking origins and attribution."""
    __tablename__ = "sample_sources"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to sample (one-to-one relationship)
    sample_id = Column(
        Integer,
        ForeignKey("samples.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Enforce one-to-one relationship
        index=True
    )

    # Source tracking
    source_type = Column(String, nullable=False, index=True)
    source_url = Column(String(2048), nullable=True)

    # Attribution fields
    artist = Column(String(255), nullable=True)
    album = Column(String(255), nullable=True)
    release_date = Column(DateTime(timezone=True), nullable=True)

    # Licensing
    license_type = Column(String, nullable=False, default=LicenseType.UNKNOWN.value)

    # File metadata
    original_filename = Column(String(255), nullable=True)

    # Batch reference (for BATCH_IMPORT type)
    import_batch_id = Column(String, ForeignKey("batches.id"), nullable=True)

    # Flexible metadata storage
    metadata_json = Column(JSON, default=dict, server_default="{}")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sample = relationship(
        "Sample",
        back_populates="source",
        uselist=False
    )
    batch = relationship("Batch", foreign_keys=[import_batch_id])

    @property
    def attribution_text(self) -> str:
        """Generate attribution text from metadata.

        Returns:
            Human-readable attribution string like "J Dilla - 'Donuts' (2006)"
        """
        parts: list[str] = []
        if self.artist:
            parts.append(str(self.artist))
        if self.album:
            parts.append(f"'{self.album}'")
        if self.release_date:
            parts.append(f"({self.release_date.year})")
        return " - ".join(parts) if parts else "Unknown Source"
