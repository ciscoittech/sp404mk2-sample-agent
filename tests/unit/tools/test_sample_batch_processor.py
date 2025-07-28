"""
Unit tests for Sample Batch Processor - TDD approach.
Tests for processing large sample collections with rate limiting.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
from pathlib import Path
import json

# Import will fail until implemented
from src.tools.sample_batch_processor import (
    SampleBatchProcessor,
    ProcessingStatus,
    BatchResult,
    SampleCollection
)


class TestSampleBatchProcessor:
    """Test suite for Sample Batch Processor."""
    
    @pytest.fixture
    def processor(self, temp_output_dir):
        """Create a batch processor instance."""
        return SampleBatchProcessor(
            collection_path="/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/Wanns Wavs 1",
            cache_dir=str(temp_output_dir / "cache")
        )
    
    def test_processor_initialization(self, processor):
        """Test processor initializes correctly."""
        assert processor.collection_path == Path("/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/Wanns Wavs 1")
        assert processor.cache_dir.exists()
        assert processor.batch_size == 5
        assert processor.rate_limit_seconds == 12  # 5 requests per minute
        assert hasattr(processor, 'vibe_agent')
        assert hasattr(processor, 'audio_analyzer')
    
    def test_sample_collection_model(self):
        """Test SampleCollection data model."""
        collection = SampleCollection(
            name="Test Collection",
            path="/path/to/samples",
            total_samples=100,
            processed_samples=50,
            status=ProcessingStatus.IN_PROGRESS,
            metadata={"genre": "jazz", "era": "1970s"}
        )
        
        assert collection.name == "Test Collection"
        assert collection.total_samples == 100
        assert collection.processed_samples == 50
        assert collection.progress_percentage == 50.0
        assert collection.status == ProcessingStatus.IN_PROGRESS
    
    def test_batch_result_model(self):
        """Test BatchResult data model."""
        result = BatchResult(
            batch_number=1,
            samples_processed=5,
            success_count=4,
            error_count=1,
            processing_time=2.5,
            errors=["Failed to process sample_5.wav"]
        )
        
        assert result.batch_number == 1
        assert result.samples_processed == 5
        assert result.success_count == 4
        assert result.error_count == 1
        assert result.success_rate == 0.8
    
    def test_discover_samples(self, processor, temp_output_dir):
        """Test discovering audio samples in directory."""
        # Create a temporary directory with test files
        test_dir = temp_output_dir / "test_samples"
        test_dir.mkdir()
        
        # Create test files
        (test_dir / "sample1.wav").write_text("")
        (test_dir / "sample2.WAV").write_text("")
        (test_dir / "sample3.mp3").write_text("")
        (test_dir / "not_audio.txt").write_text("")
        (test_dir / "sample4.aiff").write_text("")
        
        # Update processor collection path
        processor.collection_path = test_dir
        
        samples = processor.discover_samples()
        
        assert len(samples) == 4  # Only audio files
        assert all(s.suffix.lower() in ['.wav', '.mp3', '.aiff'] for s in samples)
        assert "not_audio.txt" not in [s.name for s in samples]
    
    @patch('src.tools.audio.detect_bpm')
    @patch('src.tools.audio.detect_key')
    @patch('src.tools.audio.analyze_frequency_content')
    def test_extract_local_features(self, mock_freq, mock_key, mock_bpm, processor):
        """Test local audio feature extraction."""
        # Mock audio analysis functions
        mock_bpm.return_value = {"bpm": 90, "confidence": 0.9}
        mock_key.return_value = {"key": "Am", "confidence": 0.8}
        mock_freq.return_value = {
            "spectral_centroid": 1500.0,
            "spectral_rolloff": 4000.0
        }
        
        features = processor.extract_local_features(Path("test.wav"))
        
        assert features["bpm"] == 90
        assert features["key"] == "Am"
        assert features["spectral_centroid"] == 1500.0
        assert "filename" in features
    
    def test_cache_operations(self, processor):
        """Test cache save and load operations."""
        test_data = {
            "filename": "test.wav",
            "vibe": {
                "mood": ["dark", "atmospheric"],
                "genre": "ambient"
            }
        }
        
        # Save to cache
        processor.save_to_cache("test.wav", test_data)
        
        # Load from cache
        cached = processor.load_from_cache("test.wav")
        
        assert cached is not None
        assert cached["filename"] == "test.wav"
        assert cached["vibe"]["mood"] == ["dark", "atmospheric"]
    
    @pytest.mark.asyncio
    async def test_process_batch_with_rate_limiting(self, processor):
        """Test batch processing with rate limiting."""
        samples = [Path(f"sample_{i}.wav") for i in range(5)]
        
        # Mock the vibe agent
        from src.agents.vibe_analysis import SampleVibe, VibeDescriptor
        mock_vibe_results = [
            SampleVibe(
                filename=f"sample_{i}.wav",
                bpm=120,
                key="C",
                vibe=VibeDescriptor(
                    mood=["test"],
                    era="modern",
                    genre="test",
                    energy_level="medium",
                    descriptors=["test"]
                ),
                compatibility_tags=["test"],
                best_use="test"
            )
            for i in range(5)
        ]
        processor.vibe_agent.analyze_batch = AsyncMock(return_value=mock_vibe_results)
        
        # Mock local feature extraction
        with patch.object(processor, 'extract_local_features') as mock_extract:
            def side_effect(sample_path):
                return {"filename": sample_path.name, "bpm": 120, "key": "C"}
            mock_extract.side_effect = side_effect
            
            # Track time to ensure rate limiting
            start_time = asyncio.get_event_loop().time()
            
            result = await processor.process_batch(samples, batch_number=1)
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            assert isinstance(result, BatchResult)
            assert result.batch_number == 1
            assert result.samples_processed == 5
            assert result.success_count == 5
            
            # Should not process faster than rate limit allows
            # (but first batch might be immediate)
            assert elapsed < 2  # Should be fast for first batch
    
    @pytest.mark.asyncio
    async def test_process_collection(self, processor):
        """Test processing entire collection."""
        # Mock sample discovery
        with patch.object(processor, 'get_unprocessed_samples') as mock_unprocessed:
            mock_unprocessed.return_value = [Path(f"sample_{i}.wav") for i in range(12)]
            
            # Mock cached files
            with patch.object(processor, 'get_cached_files') as mock_cached:
                mock_cached.return_value = []
                
                # Mock batch processing
                with patch.object(processor, 'process_batch') as mock_batch:
                    # Create AsyncMock for async method
                    async def mock_process_batch(*args, **kwargs):
                        return BatchResult(
                            batch_number=kwargs.get('batch_number', 1),
                            samples_processed=5,
                            success_count=5,
                            error_count=0,
                            processing_time=1.0
                        )
                    mock_batch.side_effect = mock_process_batch
                    
                    # Mock progress callback
                    progress_updates = []
                    def progress_callback(status):
                        progress_updates.append(status)
                    
                    collection = await processor.process_collection(
                        progress_callback=progress_callback
                    )
                    
                    assert collection.total_samples == 12
                    assert collection.status == ProcessingStatus.COMPLETED
                    # Should have processed in 3 batches (12 samples / 5 per batch)
                    assert mock_batch.call_count == 3
                    assert len(progress_updates) > 0
    
    def test_generate_processing_report(self, processor):
        """Test generating processing report."""
        # Create mock results
        processor.processing_results = [
            BatchResult(
                batch_number=1, 
                samples_processed=5, 
                success_count=5, 
                error_count=0, 
                processing_time=1.2
            ),
            BatchResult(
                batch_number=2, 
                samples_processed=5, 
                success_count=4, 
                error_count=1, 
                processing_time=1.5, 
                errors=["Error in sample_8.wav"]
            ),
            BatchResult(
                batch_number=3, 
                samples_processed=2, 
                success_count=2, 
                error_count=0, 
                processing_time=0.8
            )
        ]
        
        report = processor.generate_report()
        
        assert "Total Samples Processed: 12" in report
        assert "Success Rate: 91.67%" in report
        assert "Total Processing Time:" in report
        assert "Errors:" in report
        assert "sample_8.wav" in report
    
    @pytest.mark.asyncio
    async def test_resume_processing(self, processor):
        """Test resuming interrupted processing."""
        # Mock some cached results
        cached_files = ["sample_1.wav", "sample_2.wav"]
        with patch.object(processor, 'get_cached_files') as mock_cached:
            mock_cached.return_value = cached_files
            
            with patch.object(processor, 'discover_samples') as mock_discover:
                all_samples = [Path(f"sample_{i}.wav") for i in range(5)]
                mock_discover.return_value = all_samples
                
                unprocessed = processor.get_unprocessed_samples()
                
                assert len(unprocessed) == 3  # 5 total - 2 cached
                assert Path("sample_1.wav") not in unprocessed
                assert Path("sample_2.wav") not in unprocessed
    
    def test_error_handling(self, processor):
        """Test error handling in batch processing."""
        # Test with non-existent file
        with patch('src.tools.audio.detect_bpm') as mock_bpm:
            mock_bpm.side_effect = FileNotFoundError("File not found")
            
            features = processor.extract_local_features(Path("missing.wav"))
            
            assert features["error"] is True
            assert "File not found" in features.get("error_message", "")
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, processor):
        """Test that rate limiting is properly enforced."""
        # Set last request time to now
        processor._last_request_time = asyncio.get_event_loop().time()
        
        # Try to process immediately
        start = asyncio.get_event_loop().time()
        await processor._apply_rate_limit()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should wait approximately 12 seconds
        assert elapsed >= 11  # Allow small margin
        assert elapsed < 13
    
    def test_export_results(self, processor):
        """Test exporting results to JSON."""
        # Add some mock cached results
        processor.save_to_cache("test1.wav", {
            "filename": "test1.wav",
            "vibe": {"mood": ["happy"], "genre": "pop"}
        })
        processor.save_to_cache("test2.wav", {
            "filename": "test2.wav", 
            "vibe": {"mood": ["dark"], "genre": "ambient"}
        })
        
        export_path = processor.export_results()
        
        assert export_path.exists()
        assert export_path.suffix == ".json"
        
        # Load and verify exported data
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        assert len(data["samples"]) == 2
        assert data["metadata"]["total_samples"] == 2
        assert "export_date" in data["metadata"]