"""Base agent class for all specialized agents."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

from ..config import settings


class AgentStatus(str, Enum):
    """Agent execution status."""
    
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class AgentResult(BaseModel):
    """Result from agent execution."""
    
    agent_name: str
    task_id: str
    status: AgentStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


T = TypeVar("T", bound="Agent")


class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        """Initialize agent with a unique name."""
        self.name = name
        self.id = str(uuid4())
        self.status = AgentStatus.IDLE
        self.current_task_id: Optional[str] = None
        self.retry_count = 0
        self.max_retries = settings.agent_max_retries
        self.timeout = settings.agent_timeout_seconds
        
    @abstractmethod
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Execute the agent's main task.
        
        Args:
            task_id: Unique identifier for this task
            **kwargs: Task-specific parameters
            
        Returns:
            AgentResult with execution details
        """
        pass
    
    async def run(self, task_id: str, **kwargs) -> AgentResult:
        """
        Run the agent with retry logic and error handling.
        
        Args:
            task_id: Unique identifier for this task
            **kwargs: Task-specific parameters
            
        Returns:
            AgentResult with execution details
        """
        self.current_task_id = task_id
        self.status = AgentStatus.RUNNING
        started_at = datetime.utcnow()
        
        for attempt in range(self.max_retries + 1):
            try:
                # Run with timeout
                result = await asyncio.wait_for(
                    self.execute(task_id, **kwargs),
                    timeout=self.timeout
                )
                
                # Success
                self.status = AgentStatus.SUCCESS
                result.completed_at = datetime.utcnow()
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"Agent {self.name} timed out after {self.timeout} seconds"
                self.status = AgentStatus.FAILED
                
                if attempt < self.max_retries:
                    self.status = AgentStatus.RETRYING
                    self.retry_count += 1
                    await self._handle_retry(attempt, error_msg)
                    continue
                    
                return AgentResult(
                    agent_name=self.name,
                    task_id=task_id,
                    status=AgentStatus.FAILED,
                    error=error_msg,
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                    metadata={"retry_count": self.retry_count}
                )
                
            except Exception as e:
                error_msg = f"Agent {self.name} failed: {str(e)}"
                self.status = AgentStatus.FAILED
                
                if attempt < self.max_retries and self._is_retryable(e):
                    self.status = AgentStatus.RETRYING
                    self.retry_count += 1
                    await self._handle_retry(attempt, str(e))
                    continue
                    
                return AgentResult(
                    agent_name=self.name,
                    task_id=task_id,
                    status=AgentStatus.FAILED,
                    error=error_msg,
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                    metadata={"retry_count": self.retry_count}
                )
        
        # Should not reach here
        return AgentResult(
            agent_name=self.name,
            task_id=task_id,
            status=AgentStatus.FAILED,
            error="Max retries exceeded",
            started_at=started_at,
            completed_at=datetime.utcnow(),
            metadata={"retry_count": self.retry_count}
        )
    
    async def _handle_retry(self, attempt: int, error: str) -> None:
        """
        Handle retry logic with exponential backoff.
        
        Args:
            attempt: Current attempt number
            error: Error message from previous attempt
        """
        wait_time = min(2 ** attempt, 60)  # Max 60 seconds
        await asyncio.sleep(wait_time)
    
    def _is_retryable(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if the error is retryable
        """
        # Add specific error types that should be retried
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            # Add more as needed
        )
        return isinstance(error, retryable_errors)
    
    def reset(self) -> None:
        """Reset agent state."""
        self.status = AgentStatus.IDLE
        self.current_task_id = None
        self.retry_count = 0
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.__class__.__name__}(name='{self.name}', status={self.status})"