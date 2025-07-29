"""
Example unit test demonstrating TDD pattern for backend services.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# This test is written BEFORE the implementation
# Following TDD: Red -> Green -> Refactor


class TestSampleService:
    """Test cases for SampleService following TDD approach."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_sample_with_file(self, db_session, sample_factory):
        """Test creating a sample with file upload."""
        # Arrange
        from app.services.sample_service import SampleService
        from app.schemas.sample import SampleCreate
        
        service = SampleService(db_session)
        mock_storage = AsyncMock()
        mock_storage.save_file.return_value = "samples/test-123.wav"
        
        sample_data = SampleCreate(
            title="Test Beat",
            tags=["hip-hop", "drums"],
            genre="hip-hop"
        )
        
        mock_file = Mock()
        mock_file.filename = "test.wav"
        mock_file.content_type = "audio/wav"
        mock_file.read = AsyncMock(return_value=b"fake-audio-data")
        
        # Act
        result = await service.create_sample(
            data=sample_data,
            file=mock_file,
            user_id=1,
            storage=mock_storage
        )
        
        # Assert
        assert result.title == "Test Beat"
        assert result.file_path == "samples/test-123.wav"
        assert result.user_id == 1
        assert "hip-hop" in result.tags
        mock_storage.save_file.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_sample_queues_task(self, db_session):
        """Test that analyzing a sample queues a background task."""
        # Arrange
        from app.services.sample_service import SampleService
        
        service = SampleService(db_session)
        mock_queue = AsyncMock()
        
        # Act
        await service.analyze_sample(
            sample_id=123,
            queue=mock_queue
        )
        
        # Assert
        mock_queue.enqueue.assert_called_once_with(
            "analyze_sample",
            sample_id=123,
            priority="normal"
        )
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_samples_with_filters(self, db_session, sample_factory):
        """Test searching samples with multiple filters."""
        # Arrange
        from app.services.sample_service import SampleService
        
        service = SampleService(db_session)
        
        # Create test data
        samples = [
            sample_factory(title="Jazz Drums", genre="jazz", bpm=93),
            sample_factory(title="Hip Hop Beat", genre="hip-hop", bpm=120),
            sample_factory(title="Jazz Bass", genre="jazz", bpm=95),
        ]
        
        # Act
        results = await service.search_samples(
            search="jazz",
            genre="jazz",
            bpm_min=90,
            bpm_max=100
        )
        
        # Assert
        assert len(results) == 2
        assert all("jazz" in r.title.lower() for r in results)
        assert all(90 <= r.bpm <= 100 for r in results)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_sample_with_vibe_analysis(self, db_session):
        """Test retrieving a sample includes vibe analysis if available."""
        # Arrange
        from app.services.sample_service import SampleService
        
        service = SampleService(db_session)
        
        # Mock sample with vibe analysis
        mock_sample = Mock()
        mock_sample.id = 1
        mock_sample.vibe_analysis = Mock(
            mood_primary="energetic",
            energy_level=0.8
        )
        
        # Act
        result = await service.get_sample_with_analysis(1)
        
        # Assert
        assert result is not None
        assert result.vibe_analysis.mood_primary == "energetic"
        assert result.vibe_analysis.energy_level == 0.8
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_batch_process_samples(self, db_session):
        """Test batch processing multiple samples."""
        # Arrange
        from app.services.sample_service import SampleService
        
        service = SampleService(db_session)
        sample_ids = [1, 2, 3, 4, 5]
        
        # Act
        batch_id = await service.create_batch_process(
            sample_ids=sample_ids,
            process_type="vibe_analysis",
            user_id=1
        )
        
        # Assert
        assert batch_id is not None
        # Verify batch created in database
        batch = await service.get_batch(batch_id)
        assert batch.total_samples == 5
        assert batch.status == "pending"