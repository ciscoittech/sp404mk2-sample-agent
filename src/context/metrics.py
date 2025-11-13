"""
Context metrics tracking and monitoring.

Tracks token usage, tier loading, pruning events, and performance metrics.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class ContextSnapshot:
    """Single snapshot of context state."""
    timestamp: datetime
    total_tokens: int
    tier_tokens: Dict[str, int]
    tier_items: Dict[str, int]
    task_type: Optional[str]
    pruning_occurred: bool
    load_time_ms: float


@dataclass
class ContextMetrics:
    """Tracks context management metrics."""

    # Configuration
    track_snapshots: bool = True
    max_snapshots: int = 100

    # Current state
    current_tokens: int = 0
    current_tier_tokens: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    current_tier_items: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Historical data
    snapshots: List[ContextSnapshot] = field(default_factory=list)
    total_requests: int = 0
    total_pruning_events: int = 0

    # Performance tracking
    load_times: List[float] = field(default_factory=list)
    tier_load_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Budget tracking
    budget_warnings: int = 0
    budget_exceeded: int = 0

    def record_load(
        self,
        tier: str,
        tokens: int,
        items: int,
        load_time_ms: float
    ):
        """Record a tier load event."""
        self.current_tier_tokens[tier] = tokens
        self.current_tier_items[tier] = items
        self.tier_load_counts[tier] += 1
        self.load_times.append(load_time_ms)

        # Update total
        self.current_tokens = sum(self.current_tier_tokens.values())

    def record_prune(self, tier: str, tokens_removed: int):
        """Record a pruning event."""
        self.total_pruning_events += 1
        self.current_tier_tokens[tier] = max(0, self.current_tier_tokens[tier] - tokens_removed)
        self.current_tokens = sum(self.current_tier_tokens.values())

    def record_request(
        self,
        task_type: Optional[str],
        pruning_occurred: bool,
        total_load_time_ms: float
    ):
        """Record a complete request processing."""
        self.total_requests += 1

        if self.track_snapshots:
            snapshot = ContextSnapshot(
                timestamp=datetime.now(),
                total_tokens=self.current_tokens,
                tier_tokens=dict(self.current_tier_tokens),
                tier_items=dict(self.current_tier_items),
                task_type=task_type,
                pruning_occurred=pruning_occurred,
                load_time_ms=total_load_time_ms
            )
            self.snapshots.append(snapshot)

            # Keep only recent snapshots
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots = self.snapshots[-self.max_snapshots:]

    def record_budget_warning(self):
        """Record a budget warning event."""
        self.budget_warnings += 1

    def record_budget_exceeded(self):
        """Record a budget exceeded event."""
        self.budget_exceeded += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of metrics."""
        avg_load_time = sum(self.load_times) / len(self.load_times) if self.load_times else 0

        return {
            "current_state": {
                "total_tokens": self.current_tokens,
                "tier_tokens": dict(self.current_tier_tokens),
                "tier_items": dict(self.current_tier_items)
            },
            "performance": {
                "total_requests": self.total_requests,
                "avg_load_time_ms": round(avg_load_time, 2),
                "total_load_events": sum(self.tier_load_counts.values()),
                "tier_load_counts": dict(self.tier_load_counts)
            },
            "budget_management": {
                "total_pruning_events": self.total_pruning_events,
                "budget_warnings": self.budget_warnings,
                "budget_exceeded": self.budget_exceeded,
                "pruning_rate": round(
                    self.total_pruning_events / self.total_requests * 100, 1
                ) if self.total_requests > 0 else 0
            },
            "recent_snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "tokens": s.total_tokens,
                    "task_type": s.task_type,
                    "pruning": s.pruning_occurred
                }
                for s in self.snapshots[-5:]
            ]
        }

    def get_tier_efficiency(self) -> Dict[str, float]:
        """Calculate efficiency metrics for each tier."""
        efficiency = {}

        for tier, load_count in self.tier_load_counts.items():
            if load_count > 0:
                avg_tokens = self.current_tier_tokens[tier]
                avg_items = self.current_tier_items[tier]

                # Tokens per item (lower is better - more efficient)
                if avg_items > 0:
                    efficiency[tier] = avg_tokens / avg_items
                else:
                    efficiency[tier] = 0

        return efficiency

    def reset(self):
        """Reset all metrics."""
        self.current_tokens = 0
        self.current_tier_tokens.clear()
        self.current_tier_items.clear()
        self.snapshots.clear()
        self.total_requests = 0
        self.total_pruning_events = 0
        self.load_times.clear()
        self.tier_load_counts.clear()
        self.budget_warnings = 0
        self.budget_exceeded = 0

    def export_json(self, filepath: str):
        """Export metrics to JSON file."""
        data = {
            "summary": self.get_summary(),
            "tier_efficiency": self.get_tier_efficiency(),
            "all_snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "total_tokens": s.total_tokens,
                    "tier_tokens": s.tier_tokens,
                    "tier_items": s.tier_items,
                    "task_type": s.task_type,
                    "pruning_occurred": s.pruning_occurred,
                    "load_time_ms": s.load_time_ms
                }
                for s in self.snapshots
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def __repr__(self) -> str:
        return (
            f"ContextMetrics(tokens={self.current_tokens}, "
            f"requests={self.total_requests}, "
            f"pruning_events={self.total_pruning_events})"
        )
