"""
Sample model for audio file metadata
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Sample(Base):
    """Sample model for audio files."""
    __tablename__ = "samples"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    title = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # bytes
    duration = Column(Float)  # seconds
    
    # Musical properties
    bpm = Column(Float, index=True)
    musical_key = Column(String)
    genre = Column(String, index=True)
    
    # JSON fields for flexible data
    tags = Column(JSON, default=list)
    extra_metadata = Column(JSON, default=dict)  # For additional properties
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True))
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="samples")
    vibe_analysis = relationship(
        "VibeAnalysis",
        back_populates="sample",
        uselist=False,
        cascade="all, delete-orphan"
    )
    kit_associations = relationship(
        "KitSample",
        back_populates="sample",
        cascade="all, delete-orphan"
    )