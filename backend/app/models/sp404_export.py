"""
SP-404MK2 Export database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SP404Export(Base):
    """SP-404 export job record"""
    __tablename__ = "sp404_exports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Export configuration
    export_type = Column(String, nullable=False)  # "single" or "batch"
    sample_count = Column(Integer, default=0)
    output_path = Column(String, nullable=False)
    organized_by = Column(String, default="flat")  # "flat", "genre", "bpm", "key"
    format = Column(String, default="wav")  # "wav" or "aiff"

    # Export statistics
    total_size_bytes = Column(Integer, default=0)
    export_duration_seconds = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="sp404_exports")
    exported_samples = relationship(
        "SP404ExportSample",
        back_populates="export",
        cascade="all, delete-orphan"
    )


class SP404ExportSample(Base):
    """Individual sample in an SP-404 export"""
    __tablename__ = "sp404_export_samples"

    id = Column(Integer, primary_key=True, index=True)
    export_id = Column(Integer, ForeignKey("sp404_exports.id"), nullable=False)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)

    # Conversion details
    output_filename = Column(String, nullable=False)
    conversion_successful = Column(Boolean, default=False)
    conversion_error = Column(String, nullable=True)

    # File details
    file_size_bytes = Column(Integer, default=0)
    conversion_time_seconds = Column(Float, default=0.0)

    # Relationships
    export = relationship("SP404Export", back_populates="exported_samples")
    sample = relationship("Sample")
