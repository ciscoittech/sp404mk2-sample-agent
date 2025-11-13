"""
Pattern usage metrics tracking.

Tracks which patterns are used, success rates, latency, and costs
to optimize pattern selection over time.
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path


@dataclass
class PatternExecution:
    """Record of a single pattern execution."""
    pattern_name: str
    task_type: str
    timestamp: datetime
    latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternMetrics:
    """
    Tracks pattern usage and performance metrics.

    Features:
    - Pattern usage counting
    - Success rate tracking
    - Latency monitoring
    - Cost estimation
    - Pattern selection logging
    """

    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging

        # Usage tracking
        self.pattern_usage: Dict[str, int] = defaultdict(int)
        self.task_type_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Performance tracking
        self.pattern_latencies: Dict[str, List[float]] = defaultdict(list)
        self.pattern_successes: Dict[str, int] = defaultdict(int)
        self.pattern_failures: Dict[str, int] = defaultdict(int)

        # Execution history
        self.executions: List[PatternExecution] = []
        self.max_history = 1000

        # Total counts
        self.total_executions = 0

    def record_pattern_selection(
        self,
        pattern_name: str,
        task_type: str,
        reasoning: Optional[str] = None
    ):
        """Record that a pattern was selected."""
        self.pattern_usage[pattern_name] += 1
        self.task_type_patterns[task_type][pattern_name] += 1

    def record_execution(
        self,
        pattern_name: str,
        task_type: str,
        latency_ms: float,
        success: bool,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a pattern execution."""
        self.total_executions += 1

        # Track latency
        self.pattern_latencies[pattern_name].append(latency_ms)

        # Track success/failure
        if success:
            self.pattern_successes[pattern_name] += 1
        else:
            self.pattern_failures[pattern_name] += 1

        # Store execution record
        execution = PatternExecution(
            pattern_name=pattern_name,
            task_type=task_type,
            timestamp=datetime.now(),
            latency_ms=latency_ms,
            success=success,
            error=error,
            metadata=metadata or {}
        )

        self.executions.append(execution)

        # Keep history manageable
        if len(self.executions) > self.max_history:
            self.executions = self.executions[-self.max_history:]

    def get_pattern_stats(self, pattern_name: str) -> Dict[str, Any]:
        """Get statistics for a specific pattern."""
        usage_count = self.pattern_usage.get(pattern_name, 0)

        if usage_count == 0:
            return {
                "usage_count": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0
            }

        successes = self.pattern_successes.get(pattern_name, 0)
        failures = self.pattern_failures.get(pattern_name, 0)
        total = successes + failures

        success_rate = (successes / total * 100) if total > 0 else 0.0

        latencies = self.pattern_latencies.get(pattern_name, [])
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        return {
            "usage_count": usage_count,
            "executions": total,
            "success_rate": round(success_rate, 1),
            "successes": successes,
            "failures": failures,
            "avg_latency_ms": round(avg_latency, 2),
            "min_latency_ms": round(min(latencies), 2) if latencies else 0.0,
            "max_latency_ms": round(max(latencies), 2) if latencies else 0.0
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get overall metrics summary."""
        pattern_stats = {}

        for pattern_name in self.pattern_usage.keys():
            pattern_stats[pattern_name] = self.get_pattern_stats(pattern_name)

        # Task type distribution
        task_type_dist = {}
        for task_type, patterns in self.task_type_patterns.items():
            task_type_dist[task_type] = dict(patterns)

        # Recent executions
        recent_executions = [
            {
                "pattern": ex.pattern_name,
                "task": ex.task_type,
                "timestamp": ex.timestamp.isoformat(),
                "latency_ms": ex.latency_ms,
                "success": ex.success
            }
            for ex in self.executions[-10:]
        ]

        return {
            "total_executions": self.total_executions,
            "pattern_stats": pattern_stats,
            "task_type_distribution": task_type_dist,
            "recent_executions": recent_executions
        }

    def get_most_used_pattern(self) -> Optional[str]:
        """Get the most frequently used pattern."""
        if not self.pattern_usage:
            return None

        return max(self.pattern_usage.items(), key=lambda x: x[1])[0]

    def get_fastest_pattern(self) -> Optional[str]:
        """Get the pattern with lowest average latency."""
        if not self.pattern_latencies:
            return None

        avg_latencies = {
            pattern: sum(latencies) / len(latencies)
            for pattern, latencies in self.pattern_latencies.items()
            if latencies
        }

        if not avg_latencies:
            return None

        return min(avg_latencies.items(), key=lambda x: x[1])[0]

    def get_most_reliable_pattern(self) -> Optional[str]:
        """Get the pattern with highest success rate."""
        if not self.pattern_usage:
            return None

        success_rates = {}

        for pattern in self.pattern_usage.keys():
            successes = self.pattern_successes.get(pattern, 0)
            failures = self.pattern_failures.get(pattern, 0)
            total = successes + failures

            if total > 0:
                success_rates[pattern] = successes / total

        if not success_rates:
            return None

        return max(success_rates.items(), key=lambda x: x[1])[0]

    def export_json(self, filepath: str):
        """Export metrics to JSON file."""
        data = {
            "summary": self.get_summary(),
            "all_executions": [
                {
                    "pattern": ex.pattern_name,
                    "task_type": ex.task_type,
                    "timestamp": ex.timestamp.isoformat(),
                    "latency_ms": ex.latency_ms,
                    "success": ex.success,
                    "error": ex.error,
                    "metadata": ex.metadata
                }
                for ex in self.executions
            ]
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def reset(self):
        """Reset all metrics."""
        self.pattern_usage.clear()
        self.task_type_patterns.clear()
        self.pattern_latencies.clear()
        self.pattern_successes.clear()
        self.pattern_failures.clear()
        self.executions.clear()
        self.total_executions = 0

    def __repr__(self) -> str:
        return (
            f"PatternMetrics("
            f"total_executions={self.total_executions}, "
            f"patterns_used={len(self.pattern_usage)})"
        )
