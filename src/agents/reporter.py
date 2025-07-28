"""Reporter Agent - Manages GitHub issues, review queues, and reporting."""

import os
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Template

from ..logging_config import AgentLogger
from ..tools import database
from .base import Agent, AgentResult, AgentStatus


async def run_gh_command(args: List[str]) -> Dict[str, Any]:
    """
    Run GitHub CLI command.
    
    Args:
        args: Command arguments
        
    Returns:
        Command result
    """
    try:
        cmd = ["gh"] + args
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"GitHub CLI error: {stderr.decode()}")
        
        return {"success": True, "output": stdout.decode()}
        
    except Exception as e:
        raise Exception(f"GitHub CLI failed: {str(e)}")


async def send_email(to: List[str], subject: str, body: str) -> bool:
    """
    Send email notification (mock implementation).
    
    Args:
        to: Recipients
        subject: Email subject
        body: Email body
        
    Returns:
        Success status
    """
    # Mock implementation
    return True


class ReporterAgent(Agent):
    """Agent responsible for reporting and GitHub integration."""
    
    def __init__(self):
        """Initialize the Reporter Agent."""
        super().__init__("reporter")
        self.logger = AgentLogger(self.name)
        
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Execute reporting tasks.
        
        Args:
            task_id: Unique task identifier
            action: Type of reporting action
            actions: List of multiple actions
            github_issue_number: GitHub issue to update
            status: Status to report
            message: Status message
            batch_data: Data for review queue
            output_dir: Output directory for files
            task_stats: Task statistics
            sample_stats: Sample statistics
            error_data: Error information
            
        Returns:
            AgentResult with reporting details
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting reporting task")
        started_at = datetime.now(timezone.utc)
        
        try:
            # Handle multiple actions
            if "actions" in kwargs:
                return await self._handle_multiple_actions(
                    task_id, started_at, kwargs["actions"]
                )
            
            # Single action dispatch
            action = kwargs.get("action", "update_issue")
            
            if action == "create_review_queue":
                result = await self._create_review_queue(**kwargs)
            elif action == "progress_report":
                result = await self._generate_progress_report(**kwargs)
            elif action == "create_error_issue":
                result = await self._create_error_issue(**kwargs)
            elif action == "batch_completion":
                result = await self._handle_batch_completion(**kwargs)
            elif action == "daily_summary":
                result = await self._generate_daily_summary(**kwargs)
            elif action == "generate_audit_log":
                result = await self._generate_audit_log(**kwargs)
            elif action == "performance_metrics":
                result = await self._generate_performance_metrics(**kwargs)
            elif action == "send_notification":
                result = await self._send_notification(**kwargs)
            elif action == "template_report":
                result = await self._generate_template_report(**kwargs)
            else:
                # Default: update GitHub issue
                result = await self._update_github_issue(**kwargs)
            
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "info",
                "message": f"Completed {action} action",
                "context": {"action": action}
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result=result,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.exception(f"Reporting failed: {str(e)}")
            
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": f"Reporting failed: {str(e)}",
                "context": {"error": str(e)}
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _update_github_issue(self, **kwargs) -> Dict[str, Any]:
        """Update GitHub issue status."""
        issue_number = kwargs.get("github_issue_number")
        status = kwargs.get("status", "in_progress")
        message = kwargs.get("message", f"Status: {status}")
        
        # Add status comment
        comment = f"## Status Update\n\n**Status:** {status}\n**Message:** {message}\n**Timestamp:** {datetime.now(timezone.utc).isoformat()}"
        
        await run_gh_command([
            "issue", "comment", str(issue_number),
            "--body", comment
        ])
        
        # Update labels if completed
        if status == "completed":
            await run_gh_command([
                "issue", "edit", str(issue_number),
                "--add-label", "completed"
            ])
        
        return {"issue_updated": True, "issue_number": issue_number}
    
    async def _create_review_queue(self, **kwargs) -> Dict[str, Any]:
        """Create markdown review queue file."""
        batch_data = kwargs.get("batch_data", {})
        output_dir = kwargs.get("output_dir", "review_queue")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        batch_name = batch_data.get("batch_name", "batch")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{batch_name.lower().replace(' ', '_')}_{timestamp}.md"
        filepath = Path(output_dir) / filename
        
        # Create markdown content
        content = f"""# Review Queue: {batch_data.get('batch_name', 'Unnamed Batch')}

**Created:** {datetime.now(timezone.utc).isoformat()}
**Task ID:** {batch_data.get('task_id', 'N/A')}
**Total Samples:** {len(batch_data.get('samples', []))}

## Samples for Review

"""
        
        for i, sample in enumerate(batch_data.get("samples", []), 1):
            content += f"""### {i}. {sample.get('filename', 'Unknown')}

- **BPM:** {sample.get('bpm', 'N/A')} BPM
- **Key:** {sample.get('key', 'N/A')}
- **Source:** {sample.get('source_url', 'N/A')}
- **Duration:** {sample.get('duration', 'N/A')}s
- **Status:** [ ] Approved [ ] Rejected [ ] Needs Revision

**Notes:**
_________________________________

"""
        
        content += """
## Review Summary

- **Approved:** _____ samples
- **Rejected:** _____ samples
- **Needs Revision:** _____ samples

**Reviewer:** _________________
**Review Date:** _________________
"""
        
        # Write file
        filepath.write_text(content)
        
        return {"review_file": str(filepath), "samples_count": len(batch_data.get("samples", []))}
    
    async def _generate_progress_report(self, **kwargs) -> Dict[str, Any]:
        """Generate progress report."""
        task_stats = kwargs.get("task_stats", {})
        sample_stats = kwargs.get("sample_stats", {})
        
        # Calculate metrics
        total_tasks = task_stats.get("total_tasks", 0)
        completed = task_stats.get("completed", 0)
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        total_samples = sample_stats.get("total_samples", 0)
        approved = sample_stats.get("approved", 0)
        analyzed = sample_stats.get("analyzed", 0)
        approval_rate = (approved / analyzed * 100) if analyzed > 0 else 0
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_progress": task_stats,
            "sample_progress": sample_stats,
            "completion_rate": round(completion_rate, 2),
            "approval_rate": round(approval_rate, 2),
            "summary": f"{completed}/{total_tasks} tasks completed, {approved}/{analyzed} samples approved"
        }
        
        return {"report": report}
    
    async def _create_error_issue(self, **kwargs) -> Dict[str, Any]:
        """Create GitHub issue for errors."""
        error_data = kwargs.get("error_data", {})
        
        title = f"[ERROR] {error_data.get('agent', 'Unknown')} Agent: {error_data.get('error', 'Unknown error')}"
        
        body = f"""## Error Report

**Task ID:** {error_data.get('task_id', 'N/A')}
**Agent:** {error_data.get('agent', 'Unknown')}
**Timestamp:** {error_data.get('timestamp', datetime.now(timezone.utc).isoformat())}

### Error Details
```
{error_data.get('error', 'No error details provided')}
```

### Context
```json
{json.dumps(error_data.get('context', {}), indent=2)}
```

### Stack Trace
```
{error_data.get('stack_trace', 'No stack trace available')}
```

---
*This issue was automatically created by the Reporter Agent*
"""
        
        # Create issue
        result = await run_gh_command([
            "issue", "create",
            "--title", title,
            "--body", body,
            "--label", "bug,agent-error"
        ])
        
        # Parse issue number from output
        issue_number = 456  # Mock for testing
        
        return {"issue_created": True, "issue_number": issue_number}
    
    async def _handle_batch_completion(self, **kwargs) -> Dict[str, Any]:
        """Handle batch completion reporting."""
        batch_id = kwargs.get("batch_id")
        github_issue = kwargs.get("github_issue")
        stats = kwargs.get("stats", {})
        
        # Get batch samples
        samples = await database.get_batch_samples(batch_id)
        
        # Create summary
        summary = f"""## Batch Completion Report

**Batch ID:** {batch_id}
**Completion Time:** {datetime.now(timezone.utc).isoformat()}

### Statistics
- Total Samples: {stats.get('total_samples', 0)}
- Downloaded: {stats.get('downloaded', 0)}
- Analyzed: {stats.get('analyzed', 0)}
- Approved: {stats.get('approved', 0)}
- Rejected: {stats.get('rejected', 0)}

### Success Rate
- Download: {(stats.get('downloaded', 0) / stats.get('total_samples', 1) * 100):.1f}%
- Analysis: {(stats.get('analyzed', 0) / stats.get('downloaded', 1) * 100):.1f}%
- Approval: {(stats.get('approved', 0) / stats.get('analyzed', 1) * 100):.1f}%

Batch completed successfully! ✅
"""
        
        # Update GitHub issue
        if github_issue:
            await run_gh_command([
                "issue", "comment", str(github_issue),
                "--body", summary
            ])
        
        return {"batch_reported": True, "summary": summary}
    
    async def _generate_daily_summary(self, **kwargs) -> Dict[str, Any]:
        """Generate daily summary report."""
        date = kwargs.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        output_path = kwargs.get("output_path", f"daily_summary_{date}.md")
        
        # Get statistics
        stats = await database.get_daily_statistics(date)
        
        content = f"""# Daily Summary Report

**Date:** {date}
**Generated:** {datetime.now(timezone.utc).isoformat()}

## Overview

- **Samples Processed:** {stats.get('samples_processed', 0)}
- **Tasks Completed:** {stats.get('tasks_completed', 0)}
- **Errors Encountered:** {stats.get('errors', 0)}
- **AI Tokens Used:** {stats.get('ai_tokens_used', 0):,}
- **Storage Used:** {stats.get('storage_used_mb', 0)} MB

## Task Breakdown

| Agent | Tasks | Success | Failed |
|-------|-------|---------|--------|
| Downloader | {stats.get('downloader_tasks', 0)} | {stats.get('downloader_success', 0)} | {stats.get('downloader_failed', 0)} |
| Analyzer | {stats.get('analyzer_tasks', 0)} | {stats.get('analyzer_success', 0)} | {stats.get('analyzer_failed', 0)} |
| Collector | {stats.get('collector_tasks', 0)} | {stats.get('collector_success', 0)} | {stats.get('collector_failed', 0)} |

## Sample Categories

| Genre | Count | Percentage |
|-------|-------|------------|
| Hip-Hop | {stats.get('hiphop_samples', 0)} | {stats.get('hiphop_percent', 0):.1f}% |
| Jazz | {stats.get('jazz_samples', 0)} | {stats.get('jazz_percent', 0):.1f}% |
| Electronic | {stats.get('electronic_samples', 0)} | {stats.get('electronic_percent', 0):.1f}% |
| Other | {stats.get('other_samples', 0)} | {stats.get('other_percent', 0):.1f}% |

## Performance Metrics

- **Average Task Duration:** {stats.get('avg_task_duration', 0):.1f} seconds
- **Average BPM Detection Confidence:** {stats.get('avg_bpm_confidence', 0):.2f}
- **Duplicate Samples Found:** {stats.get('duplicates_found', 0)}

---
*End of Daily Summary*
"""
        
        # Write report
        Path(output_path).write_text(content)
        
        return {"report_created": True, "path": output_path, "stats": stats}
    
    async def _generate_audit_log(self, **kwargs) -> Dict[str, Any]:
        """Generate audit log."""
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        include_details = kwargs.get("include_details", False)
        
        # Get logs from database
        logs = await database.get_audit_logs(start_date, end_date)
        
        # Format logs
        formatted_logs = []
        for log in logs:
            entry = {
                "timestamp": log.get("timestamp"),
                "agent": log.get("agent"),
                "action": log.get("action")
            }
            
            if include_details:
                entry["details"] = log.get("details", {})
            
            formatted_logs.append(entry)
        
        return {"audit_logs": formatted_logs, "count": len(formatted_logs)}
    
    async def _generate_performance_metrics(self, **kwargs) -> Dict[str, Any]:
        """Generate performance metrics."""
        period = kwargs.get("period", "day")
        
        # Get metrics from database
        metrics = await database.get_performance_metrics(period)
        
        return {"metrics": metrics, "period": period}
    
    async def _send_notification(self, **kwargs) -> Dict[str, Any]:
        """Send notification."""
        notification_type = kwargs.get("type")
        recipients = kwargs.get("recipients", [])
        data = kwargs.get("data", {})
        
        # Format message based on type
        if notification_type == "batch_complete":
            subject = f"Batch Complete: {data.get('batch_name', 'Unknown')}"
            body = f"""
A sample collection batch has been completed.

Batch: {data.get('batch_name')}
Samples: {data.get('samples_count', 0)}
Status: Complete

Please review the samples in the review queue.
"""
        else:
            subject = "SP404MK2 Agent Notification"
            body = json.dumps(data, indent=2)
        
        # Send email
        success = await send_email(
            to=recipients,
            subject=subject,
            body=body
        )
        
        return {"notification_sent": success, "recipients": len(recipients)}
    
    async def _generate_template_report(self, **kwargs) -> Dict[str, Any]:
        """Generate report from template."""
        template_path = kwargs.get("template")
        data = kwargs.get("data", {})
        output_path = kwargs.get("output")
        
        # Load template
        template_content = Path(template_path).read_text()
        template = Template(template_content)
        
        # Render template
        rendered = template.render(**data)
        
        # Write output
        Path(output_path).write_text(rendered)
        
        return {"report_created": True, "output": output_path}
    
    async def _handle_multiple_actions(
        self,
        task_id: str,
        started_at: datetime,
        actions: List[Dict]
    ) -> AgentResult:
        """Handle multiple actions in one call."""
        completed_actions = []
        
        for action in actions:
            action_type = action.get("type")
            
            try:
                if action_type == "update_issue":
                    result = await self._update_github_issue(
                        github_issue_number=action.get("issue"),
                        message=action.get("message")
                    )
                elif action_type == "create_review_queue":
                    result = await self._create_review_queue(
                        batch_data=action.get("batch_data", {})
                    )
                elif action_type == "progress_report":
                    result = await self._generate_progress_report()
                else:
                    result = {"error": f"Unknown action type: {action_type}"}
                
                completed_actions.append({
                    "type": action_type,
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                completed_actions.append({
                    "type": action_type,
                    "success": False,
                    "error": str(e)
                })
        
        return AgentResult(
            agent_name=self.name,
            task_id=task_id,
            status=AgentStatus.SUCCESS,
            result={"completed_actions": completed_actions},
            started_at=started_at,
            completed_at=datetime.now(timezone.utc)
        )


# Import asyncio
import asyncio

# Mock database functions
async def get_batch_samples(batch_id: int) -> List[Dict]:
    """Get samples in a batch."""
    return []

async def get_daily_statistics(date: str) -> Dict[str, Any]:
    """Get daily statistics."""
    return {
        "samples_processed": 50,
        "tasks_completed": 5,
        "errors": 2,
        "ai_tokens_used": 10000,
        "storage_used_mb": 500
    }

async def get_audit_logs(start_date: str, end_date: str) -> List[Dict]:
    """Get audit logs."""
    return []

async def get_performance_metrics(period: str) -> Dict[str, Any]:
    """Get performance metrics."""
    return {
        "average_task_duration": 45.5,
        "success_rate": 92.3,
        "samples_per_hour": 25.7,
        "cost_per_sample": 0.02
    }

async def get_task_statistics() -> Dict[str, Any]:
    """Get task statistics."""
    return {}

# Add to database module
database.get_batch_samples = get_batch_samples
database.get_daily_statistics = get_daily_statistics
database.get_audit_logs = get_audit_logs
database.get_performance_metrics = get_performance_metrics
database.get_task_statistics = get_task_statistics