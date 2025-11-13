"""
Parallel pattern implementation.

Executes independent tasks concurrently for improved latency.
Used when multiple operations have no dependencies.
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Status of a parallel task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ParallelTask:
    """A single task in parallel execution."""
    name: str
    handler: Callable
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class ParallelResult:
    """Result of parallel execution."""
    success: bool
    tasks_completed: int
    tasks_total: int
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    total_latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ParallelPattern:
    """
    Concurrent execution of independent tasks.

    Features:
    - Parallel task execution
    - Configurable concurrency limit
    - Aggregate results
    - Individual task error handling
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Initialize parallel pattern.

        Args:
            max_concurrent: Maximum concurrent tasks (default: 5)
        """
        self.max_concurrent = max_concurrent
        self.tasks: List[ParallelTask] = []

    def add_task(
        self,
        name: str,
        handler: Callable,
        description: str = ""
    ) -> "ParallelPattern":
        """
        Add a task to execute in parallel.

        Args:
            name: Task name
            handler: Async function to execute
            description: Task description

        Returns:
            Self for chaining
        """
        task = ParallelTask(
            name=name,
            handler=handler,
            description=description
        )
        self.tasks.append(task)
        return self

    async def execute(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ParallelResult:
        """
        Execute all tasks in parallel.

        Args:
            user_input: User's input
            context: Optional context dict

        Returns:
            ParallelResult with aggregated results
        """
        import time

        context = context or {}
        results = {}
        errors = {}
        tasks_completed = 0

        start_time = time.time()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def execute_task(task: ParallelTask):
            """Execute a single task with semaphore."""
            async with semaphore:
                task.status = TaskStatus.RUNNING
                task_start = time.time()

                try:
                    result = await task.handler(user_input, context)

                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.latency_ms = (time.time() - task_start) * 1000

                    return task.name, result, None

                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.latency_ms = (time.time() - task_start) * 1000

                    return task.name, None, str(e)

        # Execute all tasks concurrently
        task_results = await asyncio.gather(
            *[execute_task(task) for task in self.tasks],
            return_exceptions=True
        )

        # Process results
        for task_result in task_results:
            if isinstance(task_result, Exception):
                # Handle unexpected exceptions
                errors["unknown"] = str(task_result)
            else:
                task_name, result, error = task_result

                if error:
                    errors[task_name] = error
                else:
                    results[task_name] = result
                    tasks_completed += 1

        total_latency_ms = (time.time() - start_time) * 1000

        # Check overall success
        success = tasks_completed > 0  # At least one task succeeded

        return ParallelResult(
            success=success,
            tasks_completed=tasks_completed,
            tasks_total=len(self.tasks),
            results=results,
            errors=errors,
            total_latency_ms=total_latency_ms,
            metadata={
                "max_concurrent": self.max_concurrent,
                "success_rate": tasks_completed / len(self.tasks) if self.tasks else 0.0
            }
        )

    def get_task_status(self) -> List[Dict[str, Any]]:
        """Get status of all tasks."""
        return [
            {
                "name": task.name,
                "description": task.description,
                "status": task.status.value,
                "latency_ms": task.latency_ms,
                "error": task.error
            }
            for task in self.tasks
        ]

    def reset(self):
        """Reset all tasks to pending."""
        for task in self.tasks:
            task.status = TaskStatus.PENDING
            task.result = None
            task.error = None
            task.latency_ms = 0.0

    def __repr__(self) -> str:
        return f"ParallelPattern(tasks={len(self.tasks)}, max_concurrent={self.max_concurrent})"
