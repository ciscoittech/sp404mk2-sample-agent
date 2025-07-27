"""Logging configuration for the application."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from .config import settings


class AgentLogFormatter(logging.Formatter):
    """Custom formatter for agent logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with agent-specific information."""
        # Add agent name if available
        if hasattr(record, "agent_name"):
            record.agent_info = f"[{record.agent_name}]"
        else:
            record.agent_info = ""
            
        # Add task ID if available
        if hasattr(record, "task_id"):
            record.task_info = f"[Task: {record.task_id}]"
        else:
            record.task_info = ""
            
        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    rich_console: bool = True
) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (defaults to settings)
        log_file: Optional log file path
        rich_console: Whether to use rich console handler
    """
    # Use provided level or get from settings
    level = getattr(logging, log_level or settings.agent_log_level)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with rich formatting
    if rich_console:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    else:
        # Basic console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_formatter = AgentLogFormatter(
            "%(asctime)s - %(name)s - %(levelname)s %(agent_info)s%(task_info)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_formatter = AgentLogFormatter(
            "%(asctime)s - %(name)s - %(levelname)s %(agent_info)s%(task_info)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log initial setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {level} level")


class AgentLogger:
    """Logger wrapper for agents with context information."""
    
    def __init__(self, agent_name: str, task_id: Optional[str] = None):
        """
        Initialize agent logger.
        
        Args:
            agent_name: Name of the agent
            task_id: Optional task ID for context
        """
        self.agent_name = agent_name
        self.task_id = task_id
        self.logger = logging.getLogger(f"agent.{agent_name}")
        
    def _add_context(self, kwargs: dict) -> dict:
        """Add agent context to log kwargs."""
        extra = kwargs.get("extra", {})
        extra["agent_name"] = self.agent_name
        if self.task_id:
            extra["task_id"] = self.task_id
        kwargs["extra"] = extra
        return kwargs
        
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(msg, **self._add_context(kwargs))
        
    def info(self, msg: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(msg, **self._add_context(kwargs))
        
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(msg, **self._add_context(kwargs))
        
    def error(self, msg: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(msg, **self._add_context(kwargs))
        
    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(msg, **self._add_context(kwargs))
        
    def exception(self, msg: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(msg, **self._add_context(kwargs))
        
    def set_task_id(self, task_id: str) -> None:
        """Update task ID for context."""
        self.task_id = task_id


# Initialize logging on module import
setup_logging()