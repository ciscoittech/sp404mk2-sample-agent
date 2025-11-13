"""
API Usage tracking model for OpenRouter API costs
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ApiUsage(Base):
    """Track OpenRouter API usage and costs per request"""
    __tablename__ = "api_usage"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User tracking
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Request identification
    request_id = Column(String, unique=True, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    operation = Column(String, nullable=False, index=True)  # "chat", "collector_search", "collector_discover", "vibe_analysis"

    # Token usage
    input_tokens = Column(Integer, default=0, nullable=False)
    output_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)

    # Cost tracking (USD)
    input_cost = Column(Float, default=0.0, nullable=False)
    output_cost = Column(Float, default=0.0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)

    # Context references
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=True)
    batch_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Additional metadata
    extra_metadata = Column(JSON, default={})

    # Relationships
    user = relationship("User", back_populates="api_usage")
    sample = relationship("Sample", back_populates="api_usage")

    def __repr__(self):
        return f"<ApiUsage(id={self.id}, model={self.model}, operation={self.operation}, cost=${self.total_cost:.4f})>"
