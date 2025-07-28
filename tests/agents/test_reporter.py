"""Tests for Reporter Agent."""

import pytest
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock, call, mock_open
from datetime import datetime

from src.agents.reporter import ReporterAgent
from src.agents.base import AgentStatus


class TestReporterAgent:
    """Test suite for Reporter Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a Reporter Agent instance."""
        return ReporterAgent()
    
    @pytest.fixture
    def sample_batch_data(self):
        """Sample batch data for reporting."""
        return {
            "task_id": 1,
            "batch_name": "Jazz Samples Batch 001",
            "samples": [
                {
                    "id": 1,
                    "filename": "jazz_drums_90bpm.wav",
                    "bpm": 90,
                    "key": "C major",
                    "source_url": "https://youtube.com/watch?v=test1"
                },
                {
                    "id": 2,
                    "filename": "jazz_bass_95bpm.wav",
                    "bpm": 95,
                    "key": "F minor",
                    "source_url": "https://youtube.com/watch?v=test2"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.name == "reporter"
        assert agent.status == AgentStatus.IDLE
        assert hasattr(agent, 'logger')
    
    @pytest.mark.asyncio
    async def test_update_github_issue_status(self, agent):
        """Test updating GitHub issue status."""
        task_id = "test_task_001"
        params = {
            "github_issue_number": 123,
            "status": "completed",
            "message": "Successfully downloaded 10 samples"
        }
        
        with patch('src.agents.reporter.run_gh_command') as mock_gh:
            mock_gh.return_value = {"success": True}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            
            # Verify GitHub CLI was called
            mock_gh.assert_called()
            call_args = mock_gh.call_args[0][0]
            assert "issue" in call_args
            assert "comment" in call_args
            assert "123" in call_args
    
    @pytest.mark.asyncio
    async def test_create_review_queue_markdown(self, agent, sample_batch_data, tmp_path):
        """Test creating markdown review queue file."""
        task_id = "test_task_002"
        review_dir = tmp_path / "review_queue"
        params = {
            "action": "create_review_queue",
            "batch_data": sample_batch_data,
            "output_dir": str(review_dir)
        }
        
        result = await agent.execute(task_id, **params)
        
        assert result.status == AgentStatus.SUCCESS
        assert "review_file" in result.result
        
        # Check file was created
        review_file = Path(result.result["review_file"])
        assert review_file.exists()
        
        # Check content
        content = review_file.read_text()
        assert "Jazz Samples Batch 001" in content
        assert "jazz_drums_90bpm.wav" in content
        assert "90 BPM" in content
        assert "C major" in content
    
    @pytest.mark.asyncio
    async def test_generate_progress_report(self, agent):
        """Test generating progress report."""
        task_id = "test_task_003"
        params = {
            "action": "progress_report",
            "task_stats": {
                "total_tasks": 10,
                "completed": 7,
                "failed": 1,
                "in_progress": 2
            },
            "sample_stats": {
                "total_samples": 150,
                "analyzed": 120,
                "approved": 100,
                "rejected": 20
            }
        }
        
        with patch('src.agents.reporter.database.get_task_statistics') as mock_stats:
            mock_stats.return_value = params["task_stats"]
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "report" in result.result
            assert result.result["report"]["completion_rate"] == 70.0
            assert result.result["report"]["approval_rate"] == 83.33
    
    @pytest.mark.asyncio
    async def test_create_error_issue(self, agent):
        """Test automatic error issue creation."""
        task_id = "test_task_004"
        params = {
            "action": "create_error_issue",
            "error_data": {
                "task_id": 5,
                "agent": "downloader",
                "error": "Connection timeout",
                "timestamp": datetime.utcnow().isoformat(),
                "context": {"url": "https://example.com/sample.wav"}
            }
        }
        
        with patch('src.agents.reporter.run_gh_command') as mock_gh:
            mock_gh.return_value = {
                "success": True,
                "issue_number": 456
            }
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["issue_created"] is True
            assert result.result["issue_number"] == 456
            
            # Check issue creation command
            call_args = mock_gh.call_args[0][0]
            assert "issue" in call_args
            assert "create" in call_args
            assert "[ERROR]" in call_args
    
    @pytest.mark.asyncio
    async def test_batch_completion_report(self, agent, sample_batch_data):
        """Test creating batch completion report."""
        task_id = "test_task_005"
        params = {
            "action": "batch_completion",
            "batch_id": 1,
            "github_issue": 100,
            "stats": {
                "total_samples": 20,
                "downloaded": 18,
                "analyzed": 18,
                "approved": 15,
                "rejected": 3
            }
        }
        
        with patch('src.agents.reporter.run_gh_command') as mock_gh, \
             patch('src.agents.reporter.database.get_batch_samples') as mock_db:
            
            mock_gh.return_value = {"success": True}
            mock_db.return_value = sample_batch_data["samples"]
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            
            # Verify GitHub issue was updated
            assert mock_gh.call_count >= 1
            issue_update = next(c for c in mock_gh.call_args_list 
                              if "Batch completed" in str(c))
            assert issue_update is not None
    
    @pytest.mark.asyncio
    async def test_daily_summary_report(self, agent, tmp_path):
        """Test generating daily summary report."""
        task_id = "test_task_006"
        params = {
            "action": "daily_summary",
            "date": "2025-01-27",
            "output_path": str(tmp_path / "daily_summary.md")
        }
        
        with patch('src.agents.reporter.database.get_daily_statistics') as mock_stats:
            mock_stats.return_value = {
                "samples_processed": 50,
                "tasks_completed": 5,
                "errors": 2,
                "ai_tokens_used": 10000,
                "storage_used_mb": 500
            }
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert Path(params["output_path"]).exists()
            
            content = Path(params["output_path"]).read_text()
            assert "Daily Summary" in content
            assert "50" in content  # samples processed
    
    @pytest.mark.asyncio
    async def test_audit_log_generation(self, agent):
        """Test generating audit logs."""
        task_id = "test_task_007"
        params = {
            "action": "generate_audit_log",
            "start_date": "2025-01-01",
            "end_date": "2025-01-27",
            "include_details": True
        }
        
        with patch('src.agents.reporter.database.get_audit_logs') as mock_logs:
            mock_logs.return_value = [
                {
                    "timestamp": "2025-01-27T10:00:00",
                    "agent": "downloader",
                    "action": "download_completed",
                    "details": {"file": "sample.wav"}
                },
                {
                    "timestamp": "2025-01-27T10:05:00",
                    "agent": "analyzer",
                    "action": "bpm_detected",
                    "details": {"bpm": 120}
                }
            ]
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "audit_logs" in result.result
            assert len(result.result["audit_logs"]) == 2
    
    @pytest.mark.asyncio
    async def test_performance_metrics_report(self, agent):
        """Test generating performance metrics."""
        task_id = "test_task_008"
        params = {
            "action": "performance_metrics",
            "period": "week"
        }
        
        with patch('src.agents.reporter.database.get_performance_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "average_task_duration": 45.5,
                "success_rate": 92.3,
                "samples_per_hour": 25.7,
                "cost_per_sample": 0.02
            }
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert "metrics" in result.result
            assert result.result["metrics"]["success_rate"] == 92.3
    
    @pytest.mark.asyncio
    async def test_email_notification(self, agent):
        """Test sending email notifications."""
        task_id = "test_task_009"
        params = {
            "action": "send_notification",
            "type": "batch_complete",
            "recipients": ["user@example.com"],
            "data": {
                "batch_name": "Test Batch",
                "samples_count": 10
            }
        }
        
        with patch('src.agents.reporter.send_email') as mock_email:
            mock_email.return_value = True
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert result.result["notification_sent"] is True
            
            # Verify email was sent
            mock_email.assert_called_once()
            email_args = mock_email.call_args[1]
            assert email_args["to"] == ["user@example.com"]
            assert "Test Batch" in email_args["body"]
    
    @pytest.mark.asyncio
    async def test_multiple_actions_in_one_call(self, agent):
        """Test handling multiple reporting actions."""
        task_id = "test_task_010"
        params = {
            "actions": [
                {
                    "type": "update_issue",
                    "issue": 123,
                    "message": "Processing started"
                },
                {
                    "type": "create_review_queue",
                    "batch_data": {"samples": []}
                },
                {
                    "type": "progress_report"
                }
            ]
        }
        
        with patch('src.agents.reporter.run_gh_command') as mock_gh, \
             patch.object(agent, '_create_review_queue') as mock_review, \
             patch.object(agent, '_generate_progress_report') as mock_progress:
            
            mock_gh.return_value = {"success": True}
            mock_review.return_value = {"file": "review.md"}
            mock_progress.return_value = {"completion": 50}
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.SUCCESS
            assert len(result.result["completed_actions"]) == 3
            assert all(a["success"] for a in result.result["completed_actions"])
    
    @pytest.mark.asyncio
    async def test_error_handling_github_failure(self, agent):
        """Test handling GitHub CLI failures."""
        task_id = "test_task_011"
        params = {
            "github_issue_number": 999,
            "status": "completed"
        }
        
        with patch('src.agents.reporter.run_gh_command') as mock_gh:
            mock_gh.side_effect = Exception("GitHub API rate limit exceeded")
            
            result = await agent.execute(task_id, **params)
            
            assert result.status == AgentStatus.FAILED
            assert "GitHub API rate limit" in result.error
    
    @pytest.mark.asyncio
    async def test_template_based_reporting(self, agent, tmp_path):
        """Test using templates for report generation."""
        task_id = "test_task_012"
        template_path = tmp_path / "template.md"
        template_path.write_text("# Report\nSamples: {{ sample_count }}")
        
        params = {
            "action": "template_report",
            "template": str(template_path),
            "data": {"sample_count": 42},
            "output": str(tmp_path / "report.md")
        }
        
        result = await agent.execute(task_id, **params)
        
        assert result.status == AgentStatus.SUCCESS
        
        report = Path(params["output"]).read_text()
        assert "Samples: 42" in report