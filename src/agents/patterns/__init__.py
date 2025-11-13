"""
Agent pattern selection and execution.

Implements intelligent pattern selection based on task complexity:
- Single Call: Simple tasks with examples
- Routing: Direct tool mapping
- Prompt Chain: Sequential execution with gates
- Parallel: Concurrent independent tasks
- Orchestrator-Workers: Complex coordinated workflows
"""

from .pattern_selector import PatternSelector, PatternDecision
from .routing_pattern import RoutingPattern
from .prompt_chain_pattern import PromptChainPattern
from .parallel_pattern import ParallelPattern
from .pattern_metrics import PatternMetrics

__all__ = [
    "PatternSelector",
    "PatternDecision",
    "RoutingPattern",
    "PromptChainPattern",
    "ParallelPattern",
    "PatternMetrics"
]
