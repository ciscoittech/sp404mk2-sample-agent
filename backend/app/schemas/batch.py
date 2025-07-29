"""
Batch processing schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class BatchStatus(str, Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingOptions(BaseModel):
    """Options for batch processing"""
    vibe_analysis: bool = True
    groove_analysis: bool = False
    era_detection: bool = False
    compatibility_check: bool = False
    auto_categorize: bool = False
    quality_threshold: float = Field(0.7, ge=0, le=1)


class BatchCreate(BaseModel):
    """Create a new batch"""
    collection_path: str
    name: Optional[str] = None
    batch_size: int = Field(5, ge=1, le=10)
    options: Dict[str, Any] = Field(default_factory=dict)


class BatchProgress(BaseModel):
    """Real-time progress update"""
    batch_id: str
    status: BatchStatus
    total_samples: int
    processed_samples: int
    success_count: int
    error_count: int
    percentage: float
    current_sample: Optional[str] = None
    eta_minutes: Optional[float] = None
    message: Optional[str] = None


class BatchResponse(BaseModel):
    """Batch response"""
    id: str
    name: str
    collection_path: str
    status: BatchStatus
    total_samples: int
    processed_samples: int
    success_count: int
    error_count: int
    progress_percentage: float
    options: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: float
    success_rate: float
    cache_dir: Optional[str] = None
    export_path: Optional[str] = None
    error_log: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class BatchListResponse(BaseModel):
    """List of batches with pagination"""
    items: List[BatchResponse]
    total: int
    page: int
    pages: int
    
    
class BatchUpdate(BaseModel):
    """Update batch status"""
    status: Optional[BatchStatus] = None
    processed_samples: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    current_sample: Optional[str] = None
    error_message: Optional[str] = None