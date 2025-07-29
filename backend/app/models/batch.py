"""
Batch processing database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

from app.db.base import Base


class BatchStatus(str, Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Batch(Base):
    """Batch processing job"""
    __tablename__ = "batches"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    name = Column(String, nullable=False)
    collection_path = Column(String, nullable=False)
    status = Column(SQLEnum(BatchStatus), default=BatchStatus.PENDING, nullable=False)
    
    # Processing stats
    total_samples = Column(Integer, default=0)
    processed_samples = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Processing options
    options = Column(JSON, default={})
    batch_size = Column(Integer, default=5)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Results
    cache_dir = Column(String)
    export_path = Column(String)
    error_log = Column(JSON, default=[])
    
    # Relationships
    user = relationship("User", back_populates="batches")
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_samples == 0:
            return 0.0
        return (self.processed_samples / self.total_samples) * 100
    
    @property
    def processing_time(self) -> float:
        """Calculate processing time in seconds"""
        if not self.started_at:
            return 0.0
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.processed_samples == 0:
            return 0.0
        return (self.success_count / self.processed_samples) * 100