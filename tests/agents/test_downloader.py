"""Tests for Downloader Agent."""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.agents.downloader import DownloaderAgent
from src.agents.base import AgentStatus


class TestDownloaderAgent:
    """Test suite for Downloader Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a Downloader Agent instance."""
        return DownloaderAgent()
    
    @pytest.fixture
    def sample_task_params(self, tmp_path):
        """Sample parameters for download tasks."""
        return {
            "source_url": "https://youtube.com/watch?v=test123",
            "output_dir": str(tmp_path / "downloads"),
            "sample_type": "drum_break",
            "max_count": 5,
            "audio_format": "wav",
            "sample_rate": 44100,
            "bit_depth": 16
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.name == "downloader"
        assert agent.status == AgentStatus.IDLE
        assert agent.max_retries == 3
    
    @pytest.mark.asyncio
    async def test_download_youtube_success(self, agent, sample_task_params):
        """Test successful YouTube download."""
        task_id = "test_task_001"
        
        with patch('src.agents.downloader.download_youtube') as mock_download, \
             patch('src.agents.downloader.database.create_sample') as mock_db, \
             patch('src.agents.downloader.database.add_agent_log') as mock_log:
            
            # Mock successful download
            mock_download.return_value = {
                "success": True,
                "output_path": "/downloads/sample.wav",
                "metadata": {
                    "title": "Test Sample",
                    "duration": 180
                }
            }
            mock_db.return_value = {"id": 1}
            mock_log.return_value = {"id": 100}
            
            result = await agent.execute(task_id, **sample_task_params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.agent_name == "downloader"
            assert result.task_id == task_id
            assert result.result["downloaded_count"] == 1
            assert len(result.result["files"]) == 1
            
            # Verify tools were called
            mock_download.assert_called_once()
            mock_db.assert_called_once()
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_download_direct_url_success(self, agent):
        """Test successful direct URL download."""
        task_id = "test_task_002"
        params = {
            "source_url": "https://example.com/sample.wav",
            "output_dir": "/downloads",
            "sample_type": "bass"
        }
        
        with patch('src.agents.downloader.download_direct') as mock_download, \
             patch('src.agents.downloader.database.create_sample') as mock_db:
            
            mock_download.return_value = {
                "success": True,
                "output_path": "/downloads/sample.wav",
                "size_bytes": 1024000
            }
            mock_db.return_value = {"id": 2}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["downloaded_count"] == 1
            mock_download.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_download_batch_urls(self, agent, sample_task_params):
        """Test downloading multiple URLs."""
        task_id = "test_task_003"
        params = {
            **sample_task_params,
            "source_urls": [
                "https://youtube.com/watch?v=test1",
                "https://youtube.com/watch?v=test2",
                "https://example.com/direct.wav"
            ]
        }
        
        with patch('src.agents.downloader.download_batch') as mock_batch, \
             patch('src.agents.downloader.database.create_sample') as mock_db:
            
            mock_batch.return_value = [
                {"success": True, "output_path": "/downloads/sample1.wav"},
                {"success": True, "output_path": "/downloads/sample2.wav"},
                {"success": True, "output_path": "/downloads/sample3.wav"}
            ]
            mock_db.return_value = {"id": 1}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["downloaded_count"] == 3
            assert mock_db.call_count == 3
    
    @pytest.mark.asyncio
    async def test_download_with_metadata_extraction(self, agent, sample_task_params):
        """Test download with metadata extraction for database."""
        task_id = "test_task_004"
        
        with patch('src.agents.downloader.download_youtube') as mock_download, \
             patch('src.agents.downloader.get_youtube_metadata') as mock_metadata, \
             patch('src.agents.downloader.database.create_sample') as mock_db:
            
            mock_metadata.return_value = {
                "title": "Funky Drummer Break",
                "duration": 240,
                "uploader": "Sample Channel"
            }
            
            mock_download.return_value = {
                "success": True,
                "output_path": "/downloads/funky_drummer.wav"
            }
            
            mock_db.return_value = {"id": 1}
            
            result = await agent.execute(task_id, **sample_task_params)
            
            assert result.status == AgentStatus.SUCCESS
            
            # Check that metadata was used in database call
            db_call_args = mock_db.call_args[0][0]
            assert "filename" in db_call_args
            assert "duration_seconds" in db_call_args
    
    @pytest.mark.asyncio
    async def test_download_failure_handling(self, agent, sample_task_params):
        """Test handling of download failures."""
        task_id = "test_task_005"
        
        with patch('src.agents.downloader.download_youtube') as mock_download, \
             patch('src.agents.downloader.database.add_agent_log') as mock_log:
            
            mock_download.side_effect = Exception("Network error")
            mock_log.return_value = {"id": 100}
            
            result = await agent.execute(task_id, **sample_task_params)
            
            assert result.status == AgentStatus.FAILED
            assert "Network error" in result.error
            
            # Verify error was logged
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert any("error" in call.get("log_level", "") for call in log_calls)
    
    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, agent):
        """Test handling of missing required parameters."""
        task_id = "test_task_006"
        params = {
            # Missing source_url
            "output_dir": "/downloads"
        }
        
        result = await agent.execute(task_id, **params)
        
        assert result.status == AgentStatus.FAILED
        assert "source_url" in result.error
    
    @pytest.mark.asyncio
    async def test_download_with_progress_tracking(self, agent, sample_task_params):
        """Test download with progress tracking."""
        task_id = "test_task_007"
        progress_updates = []
        
        def progress_callback(downloaded, total):
            progress_updates.append((downloaded, total))
        
        params = {
            **sample_task_params,
            "progress_callback": progress_callback
        }
        
        with patch('src.agents.downloader.download_youtube') as mock_download, \
             patch('src.agents.downloader.database.create_sample') as mock_db, \
             patch('src.agents.downloader.database.update_task_status') as mock_status:
            
            mock_download.return_value = {
                "success": True,
                "output_path": "/downloads/sample.wav"
            }
            mock_db.return_value = {"id": 1}
            mock_status.return_value = {"rows_affected": 1}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            
            # Verify task status was updated
            status_calls = [call[0][1] for call in mock_status.call_args_list]
            assert "in_progress" in status_calls
            assert "completed" in status_calls
    
    @pytest.mark.asyncio
    async def test_download_with_format_conversion(self, agent):
        """Test download with audio format conversion."""
        task_id = "test_task_008"
        params = {
            "source_url": "https://youtube.com/watch?v=test123",
            "output_dir": "/downloads",
            "audio_format": "wav",
            "sample_rate": 44100,
            "bit_depth": 16,
            "convert_to_mono": True
        }
        
        with patch('src.agents.downloader.download_youtube') as mock_download, \
             patch('src.agents.downloader.convert_format') as mock_convert, \
             patch('src.agents.downloader.database.create_sample') as mock_db:
            
            mock_download.return_value = {
                "success": True,
                "output_path": "/downloads/sample.mp3"
            }
            
            mock_convert.return_value = {
                "success": True,
                "output_path": "/downloads/sample.wav"
            }
            
            mock_db.return_value = {"id": 1}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            
            # Verify conversion was called
            mock_convert.assert_called_once()
            convert_args = mock_convert.call_args[1]
            assert convert_args["format"] == "wav"
            assert convert_args["sample_rate"] == 44100
    
    @pytest.mark.asyncio
    async def test_download_respects_max_count(self, agent):
        """Test that agent respects max_count parameter."""
        task_id = "test_task_009"
        params = {
            "source_urls": [f"https://youtube.com/watch?v=test{i}" for i in range(10)],
            "output_dir": "/downloads",
            "max_count": 3
        }
        
        with patch('src.agents.downloader.download_batch') as mock_batch, \
             patch('src.agents.downloader.database.create_sample') as mock_db:
            
            # Mock that we would download all 10, but agent should limit to 3
            mock_batch.return_value = [
                {"success": True, "output_path": f"/downloads/sample{i}.wav"}
                for i in range(3)
            ]
            mock_db.return_value = {"id": 1}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["downloaded_count"] == 3
            
            # Verify only 3 URLs were passed to download_batch
            batch_urls = mock_batch.call_args[0][0]
            assert len(batch_urls) == 3
    
    @pytest.mark.asyncio
    async def test_download_creates_output_directory(self, agent, tmp_path):
        """Test that agent creates output directory if it doesn't exist."""
        task_id = "test_task_010"
        output_dir = tmp_path / "new_downloads_dir"
        
        params = {
            "source_url": "https://youtube.com/watch?v=test123",
            "output_dir": str(output_dir),
            "sample_type": "drum_break"
        }
        
        with patch('src.agents.downloader.download_youtube') as mock_download, \
             patch('src.agents.downloader.database.create_sample') as mock_db:
            
            mock_download.return_value = {
                "success": True,
                "output_path": str(output_dir / "sample.wav")
            }
            mock_db.return_value = {"id": 1}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert output_dir.exists()  # Directory should be created