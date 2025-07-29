"""
Batch processing service
"""
import asyncio
import uuid
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
from pathlib import Path
import sys
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

# Add src to path for importing the batch processor
src_path = os.path.join(os.path.dirname(__file__), '../../../../')
if os.path.exists(src_path):
    sys.path.append(src_path)
else:
    # In Docker, the structure might be different
    src_path = os.path.join(os.path.dirname(__file__), '../../../')
    if os.path.exists(src_path):
        sys.path.append(src_path)

try:
    from src.tools.sample_batch_processor import SampleBatchProcessor, SampleCollection, ProcessingStatus
except ImportError:
    # Fallback: create stub classes for now
    class ProcessingStatus:
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
    
    class SampleCollection:
        def __init__(self, **kwargs):
            self.total_samples = kwargs.get('total_samples', 0)
            self.processed_samples = kwargs.get('processed_samples', 0)
            self.progress_percentage = 0
            self.metadata = {}
    
    class SampleBatchProcessor:
        def __init__(self, collection_path, cache_dir):
            self.collection_path = collection_path
            self.cache_dir = cache_dir
            self.processing_results = []
        
        async def process_collection(self, progress_callback):
            # Stub implementation
            collection = SampleCollection(total_samples=0, processed_samples=0)
            if progress_callback:
                await progress_callback(collection)
            return collection
        
        def export_results(self):
            return Path(self.cache_dir) / "export.json"

from app.models.batch import Batch, BatchStatus
from app.models.user import User
from app.schemas.batch import (
    BatchCreate, BatchResponse, BatchProgress, 
    BatchListResponse, BatchUpdate
)


class BatchService:
    """Service for managing batch processing jobs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_processors: Dict[str, SampleBatchProcessor] = {}
        self._progress_queues: Dict[str, asyncio.Queue] = {}
    
    async def create_batch(
        self, 
        user_id: int, 
        collection_path: str,
        options: Dict[str, Any]
    ) -> Batch:
        """Create a new batch processing job"""
        # Generate unique ID
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        
        # Verify collection path exists
        path = Path(collection_path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Collection path does not exist: {collection_path}")
        
        # Create batch record
        batch = Batch(
            id=batch_id,
            user_id=user_id,
            name=options.get("name", path.name),
            collection_path=collection_path,
            status=BatchStatus.PENDING,
            options=options,
            batch_size=options.get("batch_size", 5),
            cache_dir=f"cache/{batch_id}"
        )
        
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        
        return batch
    
    async def process_batch(self, batch_id: str):
        """Process a batch job (runs in background)"""
        # Get batch from database
        batch = await self.get_batch_by_id(batch_id)
        if not batch:
            return
        
        try:
            # Update status to processing
            batch.status = BatchStatus.PROCESSING
            batch.started_at = datetime.utcnow()
            await self.db.commit()
            
            # Create processor
            processor = SampleBatchProcessor(
                collection_path=batch.collection_path,
                cache_dir=batch.cache_dir
            )
            self._active_processors[batch_id] = processor
            
            # Create progress queue
            progress_queue = asyncio.Queue()
            self._progress_queues[batch_id] = progress_queue
            
            # Process with progress callback
            async def progress_callback(collection: SampleCollection):
                # Update database
                batch.total_samples = collection.total_samples
                batch.processed_samples = collection.processed_samples
                await self.db.commit()
                
                # Send progress update
                progress = BatchProgress(
                    batch_id=batch_id,
                    status=BatchStatus.PROCESSING,
                    total_samples=collection.total_samples,
                    processed_samples=collection.processed_samples,
                    success_count=batch.success_count,
                    error_count=batch.error_count,
                    percentage=collection.progress_percentage,
                    current_sample=collection.metadata.get("current_sample"),
                    eta_minutes=self._calculate_eta(batch, collection)
                )
                await progress_queue.put(progress)
            
            # Run processing
            collection = await processor.process_collection(progress_callback)
            
            # Export results
            export_path = processor.export_results()
            
            # Update batch with results
            batch.status = BatchStatus.COMPLETED
            batch.completed_at = datetime.utcnow()
            batch.export_path = str(export_path)
            batch.success_count = sum(r.success_count for r in processor.processing_results)
            batch.error_count = sum(r.error_count for r in processor.processing_results)
            
            # Collect errors
            errors = []
            for result in processor.processing_results:
                errors.extend(result.errors)
            batch.error_log = errors
            
            await self.db.commit()
            
            # Send completion progress
            final_progress = BatchProgress(
                batch_id=batch_id,
                status=BatchStatus.COMPLETED,
                total_samples=batch.total_samples,
                processed_samples=batch.processed_samples,
                success_count=batch.success_count,
                error_count=batch.error_count,
                percentage=100.0,
                message="Processing completed successfully"
            )
            await progress_queue.put(final_progress)
            
        except Exception as e:
            # Update batch as failed
            batch.status = BatchStatus.FAILED
            batch.completed_at = datetime.utcnow()
            batch.error_log = batch.error_log + [str(e)]
            await self.db.commit()
            
            # Send failure progress
            if batch_id in self._progress_queues:
                error_progress = BatchProgress(
                    batch_id=batch_id,
                    status=BatchStatus.FAILED,
                    total_samples=batch.total_samples,
                    processed_samples=batch.processed_samples,
                    success_count=batch.success_count,
                    error_count=batch.error_count,
                    percentage=batch.progress_percentage,
                    message=f"Processing failed: {str(e)}"
                )
                await self._progress_queues[batch_id].put(error_progress)
        
        finally:
            # Cleanup
            if batch_id in self._active_processors:
                del self._active_processors[batch_id]
            if batch_id in self._progress_queues:
                del self._progress_queues[batch_id]
    
    async def get_batch(self, batch_id: str, user_id: int) -> Optional[Batch]:
        """Get batch by ID for specific user"""
        stmt = select(Batch).where(
            and_(Batch.id == batch_id, Batch.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_batch_by_id(self, batch_id: str) -> Optional[Batch]:
        """Get batch by ID (internal use)"""
        stmt = select(Batch).where(Batch.id == batch_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_batches(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        status: Optional[BatchStatus] = None
    ) -> BatchListResponse:
        """List batches for user with pagination"""
        # Build query
        query = select(Batch).where(Batch.user_id == user_id)
        
        if status:
            query = query.where(Batch.status == status)
        
        # Order by created date desc
        query = query.order_by(Batch.created_at.desc())
        
        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_stmt)
        
        # Paginate
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute
        result = await self.db.execute(query)
        batches = result.scalars().all()
        
        # Convert to response
        items = [BatchResponse.from_orm(batch) for batch in batches]
        pages = (total + limit - 1) // limit
        
        return BatchListResponse(
            items=items,
            total=total,
            page=page,
            pages=pages
        )
    
    async def cancel_batch(self, batch_id: str, user_id: int) -> bool:
        """Cancel a running batch"""
        batch = await self.get_batch(batch_id, user_id)
        if not batch:
            return False
        
        if batch.status not in [BatchStatus.PENDING, BatchStatus.PROCESSING]:
            return False
        
        # Update status
        batch.status = BatchStatus.CANCELLED
        batch.completed_at = datetime.utcnow()
        await self.db.commit()
        
        # TODO: Implement actual cancellation of running process
        # For now, just mark as cancelled in DB
        
        return True
    
    async def watch_progress(self, batch_id: str) -> AsyncGenerator[BatchProgress, None]:
        """Watch progress updates for a batch"""
        if batch_id not in self._progress_queues:
            # Batch might be completed or not started
            batch = await self.get_batch_by_id(batch_id)
            if batch:
                yield BatchProgress(
                    batch_id=batch_id,
                    status=batch.status,
                    total_samples=batch.total_samples,
                    processed_samples=batch.processed_samples,
                    success_count=batch.success_count,
                    error_count=batch.error_count,
                    percentage=batch.progress_percentage,
                    message=f"Batch is {batch.status.value}"
                )
            return
        
        # Stream progress updates
        queue = self._progress_queues[batch_id]
        while True:
            try:
                progress = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield progress
                
                # Stop if completed/failed/cancelled
                if progress.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED]:
                    break
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                batch = await self.get_batch_by_id(batch_id)
                if batch:
                    yield BatchProgress(
                        batch_id=batch_id,
                        status=batch.status,
                        total_samples=batch.total_samples,
                        processed_samples=batch.processed_samples,
                        success_count=batch.success_count,
                        error_count=batch.error_count,
                        percentage=batch.progress_percentage,
                        message="Processing..."
                    )
    
    def _calculate_eta(self, batch: Batch, collection: SampleCollection) -> float:
        """Calculate estimated time remaining in minutes"""
        if batch.processed_samples == 0:
            return 0
        
        elapsed = (datetime.utcnow() - batch.started_at).total_seconds()
        rate = batch.processed_samples / elapsed  # samples per second
        
        if rate > 0:
            remaining = collection.total_samples - collection.processed_samples
            eta_seconds = remaining / rate
            return eta_seconds / 60  # Convert to minutes
        
        return 0