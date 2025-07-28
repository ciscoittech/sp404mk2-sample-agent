"""Tests for Analyzer Agent."""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from src.agents.analyzer import AnalyzerAgent
from src.agents.base import AgentStatus


class TestAnalyzerAgent:
    """Test suite for Analyzer Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create an Analyzer Agent instance."""
        return AnalyzerAgent()
    
    @pytest.fixture
    def sample_files(self, tmp_path):
        """Create sample audio files for testing."""
        files = []
        for i in range(3):
            file_path = tmp_path / f"sample_{i}.wav"
            file_path.touch()
            files.append(str(file_path))
        return files
    
    @pytest.fixture
    def analysis_params(self, tmp_path):
        """Sample parameters for analysis tasks."""
        return {
            "input_dir": str(tmp_path),
            "organize_by_bpm": True,
            "detect_key": True,
            "create_fingerprints": True,
            "confidence_threshold": 0.8
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.name == "analyzer"
        assert agent.status == AgentStatus.IDLE
        assert hasattr(agent, 'logger')
    
    @pytest.mark.asyncio
    async def test_analyze_single_file_success(self, agent, sample_files):
        """Test successful analysis of a single audio file."""
        task_id = "test_task_001"
        params = {
            "file_path": sample_files[0],
            "detect_bpm": True,
            "detect_key": True
        }
        
        with patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.audio.detect_key') as mock_key, \
             patch('src.agents.analyzer.audio.get_duration') as mock_duration, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            mock_bpm.return_value = {"bpm": 120.0, "confidence": 0.95}
            mock_key.return_value = {"key": "C major", "confidence": 0.85}
            mock_duration.return_value = 180.0
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["analyzed_count"] == 1
            assert result.result["files"][0]["bpm"] == 120.0
            assert result.result["files"][0]["key"] == "C major"
            
            # Verify tools were called
            mock_bpm.assert_called_once_with(sample_files[0])
            mock_key.assert_called_once_with(sample_files[0])
            mock_duration.assert_called_once_with(sample_files[0])
    
    @pytest.mark.asyncio
    async def test_analyze_directory(self, agent, sample_files, analysis_params):
        """Test analyzing all files in a directory."""
        task_id = "test_task_002"
        
        with patch('src.agents.analyzer.glob.glob') as mock_glob, \
             patch('src.agents.analyzer.audio.batch_analyze') as mock_batch, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            mock_glob.return_value = sample_files
            mock_batch.return_value = [
                {"file_path": f, "bpm": 90 + i*10, "confidence": 0.9, "duration": 120}
                for i, f in enumerate(sample_files)
            ]
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **analysis_params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["analyzed_count"] == 3
            mock_batch.assert_called_once()
            assert mock_db.call_count == 3
    
    @pytest.mark.asyncio
    async def test_organize_by_bpm(self, agent, sample_files, tmp_path):
        """Test organizing files by BPM ranges."""
        task_id = "test_task_003"
        params = {
            "input_dir": str(tmp_path),
            "organize_by_bpm": True,
            "bpm_ranges": [(80, 90), (90, 100), (100, 110)]
        }
        
        with patch('src.agents.analyzer.glob.glob') as mock_glob, \
             patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.shutil.move') as mock_move, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            mock_glob.return_value = sample_files
            mock_bpm.side_effect = [
                {"bpm": 85.0, "confidence": 0.9},
                {"bpm": 95.0, "confidence": 0.85},
                {"bpm": 105.0, "confidence": 0.92}
            ]
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert mock_move.call_count == 3
            
            # Check files were moved to correct folders
            move_calls = mock_move.call_args_list
            assert "80_90_bpm" in str(move_calls[0])
            assert "90_100_bpm" in str(move_calls[1])
            assert "100_110_bpm" in str(move_calls[2])
    
    @pytest.mark.asyncio
    async def test_duplicate_detection(self, agent, sample_files):
        """Test duplicate detection using audio fingerprints."""
        task_id = "test_task_004"
        params = {
            "file_paths": sample_files,
            "detect_duplicates": True
        }
        
        with patch('src.agents.analyzer.audio.create_fingerprint') as mock_fp, \
             patch('src.agents.analyzer.database.get_samples_by_fingerprint') as mock_db_fp, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            # Mock fingerprints - first two are duplicates
            mock_fp.side_effect = ["abc123", "abc123", "xyz789"]
            mock_db_fp.side_effect = [[], [{"id": 1}], []]
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["duplicates_found"] == 1
            assert len(result.result["duplicate_groups"]) == 1
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_filtering(self, agent, sample_files):
        """Test that low confidence detections are flagged."""
        task_id = "test_task_005"
        params = {
            "file_paths": sample_files,
            "confidence_threshold": 0.9
        }
        
        with patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            mock_bpm.side_effect = [
                {"bpm": 120.0, "confidence": 0.95},  # High confidence
                {"bpm": 90.0, "confidence": 0.75},   # Low confidence
                {"bpm": 110.0, "confidence": 0.92}   # High confidence
            ]
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["low_confidence_count"] == 1
            assert result.result["files"][1]["warning"] == "Low confidence BPM detection"
    
    @pytest.mark.asyncio
    async def test_key_detection_and_grouping(self, agent, sample_files):
        """Test key detection and grouping by musical key."""
        task_id = "test_task_006"
        params = {
            "file_paths": sample_files,
            "detect_key": True,
            "group_by_key": True
        }
        
        with patch('src.agents.analyzer.audio.detect_key') as mock_key, \
             patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            mock_key.side_effect = [
                {"key": "C major", "confidence": 0.85},
                {"key": "A minor", "confidence": 0.90},
                {"key": "C major", "confidence": 0.88}
            ]
            mock_bpm.return_value = {"bpm": 100.0, "confidence": 0.9}
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "key_groups" in result.result
            assert len(result.result["key_groups"]["C major"]) == 2
            assert len(result.result["key_groups"]["A minor"]) == 1
    
    @pytest.mark.asyncio
    async def test_spectral_analysis(self, agent, sample_files):
        """Test spectral analysis features."""
        task_id = "test_task_007"
        params = {
            "file_path": sample_files[0],
            "analyze_spectrum": True
        }
        
        with patch('src.agents.analyzer.audio.analyze_frequency_content') as mock_spectrum, \
             patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.database.update_sample') as mock_db:
            
            mock_spectrum.return_value = {
                "spectral_centroid": 2500.0,
                "spectral_rolloff": 5000.0,
                "spectral_bandwidth": 1800.0
            }
            mock_bpm.return_value = {"bpm": 100.0, "confidence": 0.9}
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["files"][0]["spectral_centroid"] == 2500.0
            mock_spectrum.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_for_corrupted_file(self, agent):
        """Test handling of corrupted audio files."""
        task_id = "test_task_008"
        params = {
            "file_path": "/path/to/corrupted.wav"
        }
        
        with patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.database.add_agent_log') as mock_log:
            
            mock_bpm.side_effect = Exception("Invalid audio data")
            mock_log.return_value = {"id": 100}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.FAILED
            assert "Invalid audio data" in result.error
            
            # Verify error was logged
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert any("error" in call.get("log_level", "") for call in log_calls)
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, agent, tmp_path):
        """Test efficient batch processing of multiple files."""
        # Create many files
        files = []
        for i in range(50):
            file_path = tmp_path / f"sample_{i}.wav"
            file_path.touch()
            files.append(str(file_path))
        
        task_id = "test_task_009"
        params = {
            "input_dir": str(tmp_path),
            "batch_size": 10
        }
        
        with patch('src.agents.analyzer.glob.glob') as mock_glob, \
             patch('src.agents.analyzer.audio.batch_analyze') as mock_batch, \
             patch('src.agents.analyzer.database.update_sample_batch') as mock_db:
            
            mock_glob.return_value = files
            mock_batch.return_value = [
                {"file_path": f, "bpm": 100, "confidence": 0.9, "duration": 120}
                for f in files
            ]
            mock_db.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["analyzed_count"] == 50
            
            # Should use batch operations
            assert mock_batch.call_count <= 5  # 50 files / 10 batch size
    
    @pytest.mark.asyncio
    async def test_create_analysis_report(self, agent, sample_files):
        """Test creation of analysis report."""
        task_id = "test_task_010"
        params = {
            "file_paths": sample_files,
            "create_report": True,
            "report_path": "/tmp/analysis_report.json"
        }
        
        with patch('src.agents.analyzer.audio.detect_bpm') as mock_bpm, \
             patch('src.agents.analyzer.audio.detect_key') as mock_key, \
             patch('src.agents.analyzer.database.update_sample') as mock_db, \
             patch('builtins.open', create=True) as mock_open:
            
            mock_bpm.return_value = {"bpm": 100.0, "confidence": 0.9}
            mock_key.return_value = {"key": "C major", "confidence": 0.85}
            mock_db.return_value = {"success": True}
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["report_created"] is True
            assert mock_file.write.called