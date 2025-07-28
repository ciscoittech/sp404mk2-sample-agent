"""
Sample Batch Processor - Processes large collections of audio samples with rate limiting.
Designed for the Wanns Wavs collection and similar large sample libraries.
"""

import asyncio
import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from pydantic import BaseModel, Field

from ..agents.vibe_analysis import VibeAnalysisAgent
from ..logging_config import AgentLogger
from . import audio


class ProcessingStatus(str, Enum):
    """Status of collection processing."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class BatchResult(BaseModel):
    """Result from processing a batch of samples."""
    batch_number: int
    samples_processed: int
    success_count: int
    error_count: int
    processing_time: float
    errors: List[str] = Field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.samples_processed == 0:
            return 0.0
        return self.success_count / self.samples_processed


class SampleCollection(BaseModel):
    """Represents a collection of samples being processed."""
    name: str
    path: str
    total_samples: int
    processed_samples: int = 0
    status: ProcessingStatus = ProcessingStatus.PENDING
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_samples == 0:
            return 0.0
        return (self.processed_samples / self.total_samples) * 100


class SampleBatchProcessor:
    """Processes collections of audio samples with rate limiting and caching."""
    
    def __init__(self, collection_path: str, cache_dir: str = "sample_cache"):
        """Initialize the batch processor.
        
        Args:
            collection_path: Path to the sample collection
            cache_dir: Directory for caching results
        """
        self.logger = AgentLogger("batch_processor")
        self.collection_path = Path(collection_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Processing configuration
        self.batch_size = 5  # Process 5 samples per batch
        self.rate_limit_seconds = 12  # 5 requests per minute = 12 seconds between
        
        # Initialize components
        self.vibe_agent = VibeAnalysisAgent()
        self.audio_analyzer = audio  # Reference to audio tools module
        
        # Processing state
        self._last_request_time: Optional[float] = None
        self.processing_results: List[BatchResult] = []
    
    def discover_samples(self) -> List[Path]:
        """Discover all audio samples in the collection directory.
        
        Returns:
            List of paths to audio files
        """
        audio_extensions = {'.wav', '.mp3', '.aiff', '.flac', '.m4a', '.ogg'}
        samples = []
        
        if not self.collection_path.exists():
            self.logger.error(f"Collection path does not exist: {self.collection_path}")
            return samples
        
        # Get all files in directory
        for file_path in self.collection_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                samples.append(file_path)
        
        self.logger.info(f"Discovered {len(samples)} audio samples")
        return sorted(samples)  # Sort for consistent ordering
    
    def extract_local_features(self, sample_path: Path) -> Dict[str, Any]:
        """Extract audio features locally without API calls.
        
        Args:
            sample_path: Path to audio file
            
        Returns:
            Dictionary of audio features
        """
        features = {
            "filename": sample_path.name,
            "path": str(sample_path)
        }
        
        try:
            # Extract BPM
            bpm_data = self.audio_analyzer.detect_bpm(str(sample_path))
            features["bpm"] = bpm_data.get("bpm", 0)
            features["bpm_confidence"] = bpm_data.get("confidence", 0)
            
            # Extract key
            key_data = self.audio_analyzer.detect_key(str(sample_path))
            features["key"] = key_data.get("key", "")
            features["key_confidence"] = key_data.get("confidence", 0)
            
            # Extract frequency features
            freq_data = self.audio_analyzer.analyze_frequency_content(str(sample_path))
            features.update(freq_data)
            
            # Get duration
            features["duration"] = self.audio_analyzer.get_duration(str(sample_path))
            
        except Exception as e:
            self.logger.error(f"Error extracting features from {sample_path}: {str(e)}")
            features["error"] = True
            features["error_message"] = str(e)
        
        return features
    
    def save_to_cache(self, filename: str, data: Dict[str, Any]):
        """Save processed data to cache.
        
        Args:
            filename: Sample filename
            data: Data to cache
        """
        cache_file = self.cache_dir / f"{filename}.json"
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_cache(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load cached data for a sample.
        
        Args:
            filename: Sample filename
            
        Returns:
            Cached data or None if not found
        """
        cache_file = self.cache_dir / f"{filename}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_cached_files(self) -> List[str]:
        """Get list of files that have been cached.
        
        Returns:
            List of cached filenames
        """
        cached = []
        for cache_file in self.cache_dir.glob("*.json"):
            cached.append(cache_file.stem)
        return cached
    
    def get_unprocessed_samples(self) -> List[Path]:
        """Get samples that haven't been processed yet.
        
        Returns:
            List of unprocessed sample paths
        """
        all_samples = self.discover_samples()
        cached_files = set(self.get_cached_files())
        
        unprocessed = []
        for sample in all_samples:
            if sample.name not in cached_files:
                unprocessed.append(sample)
        
        return unprocessed
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between API calls."""
        if self._last_request_time is not None:
            elapsed = asyncio.get_event_loop().time() - self._last_request_time
            if elapsed < self.rate_limit_seconds:
                wait_time = self.rate_limit_seconds - elapsed
                self.logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def process_batch(self, samples: List[Path], batch_number: int) -> BatchResult:
        """Process a batch of samples.
        
        Args:
            samples: List of sample paths to process
            batch_number: Batch sequence number
            
        Returns:
            BatchResult with processing statistics
        """
        start_time = asyncio.get_event_loop().time()
        success_count = 0
        errors = []
        
        # Extract local features for all samples
        sample_data = []
        for sample in samples:
            # Check cache first
            cached = self.load_from_cache(sample.name)
            if cached:
                self.logger.info(f"Using cached data for {sample.name}")
                success_count += 1
                continue
            
            # Extract features
            features = self.extract_local_features(sample)
            if not features.get("error"):
                sample_data.append(features)
            else:
                errors.append(f"{sample.name}: {features.get('error_message', 'Unknown error')}")
        
        # Process uncached samples with vibe analysis
        if sample_data:
            # Apply rate limiting
            await self._apply_rate_limit()
            
            try:
                # Analyze vibes in batch
                vibe_results = await self.vibe_agent.analyze_batch(sample_data)
                
                # Combine results and cache
                for i, vibe in enumerate(vibe_results):
                    if i < len(sample_data):
                        combined = {
                            **sample_data[i],
                            "vibe": vibe.model_dump()
                        }
                        self.save_to_cache(sample_data[i]["filename"], combined)
                        success_count += 1
                        
            except Exception as e:
                self.logger.error(f"Error in vibe analysis: {str(e)}")
                errors.append(f"Vibe analysis failed: {str(e)}")
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return BatchResult(
            batch_number=batch_number,
            samples_processed=len(samples),
            success_count=success_count,
            error_count=len(errors),
            processing_time=processing_time,
            errors=errors
        )
    
    async def process_collection(
        self,
        progress_callback: Optional[Callable[[SampleCollection], None]] = None
    ) -> SampleCollection:
        """Process the entire sample collection.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            SampleCollection with final status
        """
        # Get unprocessed samples
        samples = self.get_unprocessed_samples()
        total_samples = len(samples) + len(self.get_cached_files())
        
        collection = SampleCollection(
            name=self.collection_path.name,
            path=str(self.collection_path),
            total_samples=total_samples,
            processed_samples=len(self.get_cached_files()),
            status=ProcessingStatus.IN_PROGRESS
        )
        
        if progress_callback:
            progress_callback(collection)
        
        # Process in batches
        batch_number = 1
        for i in range(0, len(samples), self.batch_size):
            batch = samples[i:i + self.batch_size]
            
            self.logger.info(f"Processing batch {batch_number} ({len(batch)} samples)")
            
            result = await self.process_batch(batch, batch_number)
            self.processing_results.append(result)
            
            collection.processed_samples += result.success_count
            
            if progress_callback:
                progress_callback(collection)
            
            batch_number += 1
        
        # Update final status
        collection.status = ProcessingStatus.COMPLETED
        collection.metadata = {
            "processing_date": datetime.now().isoformat(),
            "total_batches": len(self.processing_results),
            "cache_dir": str(self.cache_dir)
        }
        
        if progress_callback:
            progress_callback(collection)
        
        return collection
    
    def generate_report(self) -> str:
        """Generate a processing report.
        
        Returns:
            Formatted report string
        """
        if not self.processing_results:
            return "No processing results available."
        
        total_samples = sum(r.samples_processed for r in self.processing_results)
        total_success = sum(r.success_count for r in self.processing_results)
        total_errors = sum(r.error_count for r in self.processing_results)
        total_time = sum(r.processing_time for r in self.processing_results)
        
        report = f"""
Sample Processing Report
========================
Total Samples Processed: {total_samples}
Successful: {total_success}
Failed: {total_errors}
Success Rate: {(total_success / total_samples * 100):.2f}%
Total Processing Time: {total_time:.2f} seconds

Batch Details:
"""
        
        for result in self.processing_results:
            report += f"\nBatch {result.batch_number}:"
            report += f"\n  Samples: {result.samples_processed}"
            report += f"\n  Success: {result.success_count}"
            report += f"\n  Errors: {result.error_count}"
            report += f"\n  Time: {result.processing_time:.2f}s"
            
            if result.errors:
                report += "\n  Errors:"
                for error in result.errors:
                    report += f"\n    - {error}"
        
        return report
    
    def export_results(self, output_path: Optional[Path] = None) -> Path:
        """Export all processed results to JSON.
        
        Args:
            output_path: Optional output path
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.cache_dir / f"export_{timestamp}.json"
        
        # Collect all cached results
        all_results = []
        for cache_file in self.cache_dir.glob("*.json"):
            if not cache_file.name.startswith("export_"):
                with open(cache_file, 'r') as f:
                    all_results.append(json.load(f))
        
        # Create export data
        export_data = {
            "metadata": {
                "collection": str(self.collection_path),
                "total_samples": len(all_results),
                "export_date": datetime.now().isoformat(),
                "processor_version": "1.0.0"
            },
            "samples": all_results
        }
        
        # Write export file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported {len(all_results)} results to {output_path}")
        return output_path