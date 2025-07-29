"""
Kit model for SP-404 sample collections
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Kit(Base):
    """Kit model for organizing samples into SP-404 banks."""
    __tablename__ = "kits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(String)
    is_public = Column(Boolean, default=False)
    
    # SP-404 specific configuration
    pad_layout = Column(JSON, default=dict)  # Maps pad positions to samples
    bank_config = Column(JSON, default=dict)  # Bank A, B, C, D configurations
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="kits")
    samples = relationship("KitSample", back_populates="kit", cascade="all, delete-orphan")


class KitSample(Base):
    """Association table for kit-sample relationships with additional properties."""
    __tablename__ = "kit_samples"
    
    kit_id = Column(Integer, ForeignKey("kits.id"), primary_key=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), primary_key=True)
    
    # Pad assignment
    pad_bank = Column(String, nullable=False)  # A, B, C, or D
    pad_number = Column(Integer, nullable=False)  # 1-16
    
    # Performance settings
    volume = Column(Float, default=1.0)  # 0.0 to 1.0
    pitch_shift = Column(Integer, default=0)  # semitones
    
    # Relationships
    kit = relationship("Kit", back_populates="samples")
    sample = relationship("Sample", back_populates="kit_associations")