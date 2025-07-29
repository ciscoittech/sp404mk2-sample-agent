"""
Vibe Analysis model for AI-generated sample analysis
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class VibeAnalysis(Base):
    """Vibe analysis results from AI processing."""
    __tablename__ = "vibe_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), unique=True, nullable=False)
    
    # Core vibe properties
    mood_primary = Column(String, nullable=False)
    mood_secondary = Column(String)
    energy_level = Column(Float)  # 0.0 to 1.0
    
    # Musical analysis
    danceability = Column(Float)  # 0.0 to 1.0
    acousticness = Column(Float)  # 0.0 to 1.0
    instrumentalness = Column(Float)  # 0.0 to 1.0
    
    # Texture and characteristics (stored as JSON)
    texture_tags = Column(JSON, default=list)
    characteristics = Column(JSON, default=dict)
    
    # Analysis metadata
    model_version = Column(String)
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sample = relationship("Sample", back_populates="vibe_analysis")