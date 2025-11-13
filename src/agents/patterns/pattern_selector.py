"""
Pattern selector for intelligent agent execution.

Chooses the appropriate execution pattern based on task characteristics:
- Single Call: Simple, well-defined tasks
- Routing: Direct tool mapping
- Prompt Chain: Sequential dependent steps
- Parallel: Independent concurrent operations
- Orchestrator-Workers: Complex coordinated workflows
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class PatternType(Enum):
    """Available execution patterns."""
    SINGLE_CALL = "single_call"
    ROUTING = "routing"
    PROMPT_CHAIN = "prompt_chain"
    PARALLEL = "parallel"
    ORCHESTRATOR_WORKERS = "orchestrator_workers"


@dataclass
class PatternDecision:
    """Decision about which pattern to use."""
    pattern: PatternType
    reasoning: str
    route_to: Optional[str] = None  # For routing pattern
    steps: Optional[List[Dict[str, Any]]] = None  # For prompt chain
    subtasks: Optional[List[str]] = None  # For parallel
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PatternSelector:
    """
    Selects the appropriate execution pattern for a given task.

    Uses a decision tree to determine:
    1. Can a single tool handle this? → Routing
    2. Is it simple with examples? → Single Call
    3. Do steps have dependencies? → Prompt Chain
    4. Are there multiple independent tasks? → Parallel
    5. Is complex coordination needed? → Orchestrator-Workers
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize pattern selector.

        Args:
            config_path: Path to pattern_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / ".claude" / "patterns" / "pattern_config.json"

        with open(config_path) as f:
            self.config = json.load(f)

        self.patterns = self.config["patterns"]
        self.decision_tree = self.config["decision_tree"]
        self.task_mapping = self.config["task_pattern_mapping"]

    def select_pattern(
        self,
        user_input: str,
        task_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PatternDecision:
        """
        Select the appropriate pattern for this task.

        Args:
            user_input: The user's request
            task_type: Optional explicit task type
            context: Optional context information

        Returns:
            PatternDecision with chosen pattern and reasoning
        """
        context = context or {}

        # Check for explicit task type mapping
        if task_type and task_type in self.task_mapping:
            return self._get_mapped_pattern(task_type, user_input, context)

        # Otherwise, use decision tree
        return self._apply_decision_tree(user_input, context)

    def _get_mapped_pattern(
        self,
        task_type: str,
        user_input: str,
        context: Dict[str, Any]
    ) -> PatternDecision:
        """Get pattern from explicit task mapping."""
        mapping = self.task_mapping[task_type]
        pattern_name = mapping["pattern"]

        # Build pattern decision
        pattern = PatternType(pattern_name)

        reasoning = f"Task type '{task_type}' maps to {pattern_name} pattern"

        kwargs = {
            "pattern": pattern,
            "reasoning": reasoning
        }

        # Add pattern-specific data
        if "route_to" in mapping:
            kwargs["route_to"] = mapping["route_to"]
            reasoning += f", routing to {mapping['route_to']}"

        if "steps" in mapping:
            kwargs["steps"] = mapping["steps"]

        if "use_protocol" in mapping:
            kwargs["metadata"] = {"protocol": mapping["use_protocol"]}

        if "use_examples" in mapping:
            kwargs["metadata"] = kwargs.get("metadata", {})
            kwargs["metadata"]["use_examples"] = True

        kwargs["reasoning"] = reasoning

        return PatternDecision(**kwargs)

    def _apply_decision_tree(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> PatternDecision:
        """Apply decision tree to select pattern."""

        # Step 1: Check for tool routing
        tool_route = self._check_tool_routing(user_input)
        if tool_route:
            return PatternDecision(
                pattern=PatternType.ROUTING,
                reasoning=f"Request matches tool trigger: {tool_route}",
                route_to=tool_route,
                confidence=0.95
            )

        # Step 2: Check if simple task
        if self._is_simple_task(user_input, context):
            return PatternDecision(
                pattern=PatternType.SINGLE_CALL,
                reasoning="Simple, well-defined task with available examples",
                confidence=0.9
            )

        # Step 3: Check for dependencies
        has_dependencies = self._check_dependencies(user_input, context)
        if has_dependencies:
            return PatternDecision(
                pattern=PatternType.PROMPT_CHAIN,
                reasoning="Task has sequential dependencies requiring ordered execution",
                confidence=0.85
            )

        # Step 4: Check for parallel opportunities
        subtasks = self._extract_subtasks(user_input, context)
        if len(subtasks) >= 3:
            return PatternDecision(
                pattern=PatternType.PARALLEL,
                reasoning=f"Task has {len(subtasks)} independent subtasks that can run concurrently",
                subtasks=subtasks,
                confidence=0.8
            )

        # Step 5: Default to prompt chain (safer fallback)
        return PatternDecision(
            pattern=PatternType.PROMPT_CHAIN,
            reasoning="Complex task requiring structured execution (fallback pattern)",
            confidence=0.6
        )

    def _check_tool_routing(self, user_input: str) -> Optional[str]:
        """Check if request maps to a specific tool."""
        input_lower = user_input.lower()

        # Check all mapped task types for routing patterns
        for task_type, mapping in self.task_mapping.items():
            if mapping["pattern"] == "routing" and "triggers" in mapping:
                triggers = mapping["triggers"]

                if any(trigger in input_lower for trigger in triggers):
                    return mapping.get("route_to")

        return None

    def _is_simple_task(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if this is a simple task suitable for single call."""
        # Heuristics for simple tasks
        input_lower = user_input.lower()

        simple_indicators = [
            len(user_input.split()) < 20,  # Short request
            any(word in input_lower for word in ["what", "explain", "describe", "classify"]),
            "?" in user_input  # Question
        ]

        complex_indicators = [
            any(word in input_lower for word in ["and then", "after", "once", "before"]),
            any(word in input_lower for word in ["multiple", "several", "all"]),
            user_input.count(",") >= 3  # Multiple clauses
        ]

        return sum(simple_indicators) >= 2 and sum(complex_indicators) == 0

    def _check_dependencies(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if task has sequential dependencies."""
        input_lower = user_input.lower()

        dependency_keywords = [
            "then", "after", "once", "before", "first", "next",
            "→", "->", "followed by", "and then", "subsequently"
        ]

        return any(keyword in input_lower for keyword in dependency_keywords)

    def _extract_subtasks(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Extract independent subtasks from request."""
        # Simple heuristic: split on "and", "also", comma
        parts = []

        # Split on "and"
        and_parts = user_input.split(" and ")
        for part in and_parts:
            # Further split on commas
            comma_parts = part.split(",")
            parts.extend([p.strip() for p in comma_parts if p.strip()])

        # Filter out very short parts (likely not independent tasks)
        subtasks = [p for p in parts if len(p.split()) >= 3]

        return subtasks

    def should_use_pattern(
        self,
        pattern: PatternType,
        task_characteristics: Dict[str, Any]
    ) -> bool:
        """
        Check if a specific pattern is appropriate.

        Args:
            pattern: Pattern to check
            task_characteristics: Dict with task properties

        Returns:
            True if pattern is appropriate
        """
        pattern_def = self.patterns.get(pattern.value, {})
        when_to_use = pattern_def.get("when_to_use", [])

        # Count how many criteria match
        matches = 0
        for criterion in when_to_use:
            criterion_lower = criterion.lower()

            # Check against task characteristics
            for key, value in task_characteristics.items():
                if isinstance(value, bool) and value:
                    if key.lower() in criterion_lower:
                        matches += 1
                        break
                elif isinstance(value, str) and value.lower() in criterion_lower:
                    matches += 1
                    break

        # Pattern is appropriate if >50% criteria match
        return matches / len(when_to_use) > 0.5 if when_to_use else False

    def get_pattern_info(self, pattern: PatternType) -> Dict[str, Any]:
        """Get information about a specific pattern."""
        return self.patterns.get(pattern.value, {})

    def list_patterns(self) -> List[str]:
        """List all available patterns."""
        return list(self.patterns.keys())

    def __repr__(self) -> str:
        return f"PatternSelector(patterns={len(self.patterns)})"
