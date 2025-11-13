"""
Intelligent Context Manager for SP404MK2 agents.

Orchestrates tier-based context loading with token budget management,
task-aware context selection, and automatic pruning.
"""

import time
import json
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from dataclasses import dataclass, field

from .context_tiers import ContextTier, TierLoader, TierContent
from .metrics import ContextMetrics


@dataclass
class TaskContext:
    """Context for the current task."""
    task_type: str
    required_tiers: List[int]
    optional_tiers: List[int]
    load_heuristics: List[str] = field(default_factory=list)
    load_protocols: List[str] = field(default_factory=list)
    load_tools: List[str] = field(default_factory=list)


class IntelligentContextManager:
    """
    Intelligent context management with tier-based loading.

    Features:
    - 4-tier context hierarchy (Immediate, Working, Reference, Background)
    - Token budget management with automatic pruning
    - Task-aware context loading
    - Performance metrics and monitoring
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        project_root: Optional[Path] = None
    ):
        """
        Initialize the context manager.

        Args:
            config_path: Path to tier_config.json (defaults to .claude/context/tier_config.json)
            project_root: Project root directory (defaults to current working directory)
        """
        self.project_root = project_root or Path.cwd()

        # Load configuration
        if config_path is None:
            config_path = self.project_root / ".claude" / "context" / "tier_config.json"

        with open(config_path) as f:
            self.config = json.load(f)

        # Initialize components
        self.tier_loader = TierLoader(self.config, self.project_root)
        self.metrics = ContextMetrics()

        # State management
        self.loaded_tiers: Dict[ContextTier, TierContent] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10

        # Current task state
        self.current_task: Optional[TaskContext] = None
        self.musical_intent: Optional[Dict[str, Any]] = None
        self.discovered_samples: List[Dict[str, Any]] = []
        self.search_results: List[Dict[str, Any]] = []
        self.active_tools: Set[str] = set()

    def detect_task_type(self, user_input: str) -> TaskContext:
        """
        Detect task type from user input.

        Returns TaskContext with required/optional tiers and resources.
        """
        input_lower = user_input.lower()
        task_detection = self.config["task_type_detection"]

        # Check each task type
        for task_type, task_config in task_detection.items():
            keywords = task_config.get("keywords", [])

            # Match keywords
            if any(keyword in input_lower for keyword in keywords):
                return TaskContext(
                    task_type=task_type,
                    required_tiers=task_config.get("required_tiers", [1]),
                    optional_tiers=task_config.get("optional_tiers", []),
                    load_heuristics=task_config.get("load_heuristics", []),
                    load_protocols=task_config.get("load_protocols", []),
                    load_tools=task_config.get("load_tools", [])
                )

        # Default to general conversation
        return TaskContext(
            task_type="general_conversation",
            required_tiers=[1],
            optional_tiers=[2],
            load_heuristics=[],
            load_protocols=[],
            load_tools=[]
        )

    def build_context(
        self,
        user_input: str,
        task_type_override: Optional[str] = None
    ) -> str:
        """
        Build complete context for LLM based on user input.

        Args:
            user_input: Current user input
            task_type_override: Optional manual task type specification

        Returns:
            Formatted context string ready for LLM
        """
        start_time = time.time()

        # Detect task type
        if task_type_override:
            task_detection = self.config["task_type_detection"]
            task_config = task_detection.get(task_type_override, {})
            self.current_task = TaskContext(
                task_type=task_type_override,
                required_tiers=task_config.get("required_tiers", [1]),
                optional_tiers=task_config.get("optional_tiers", []),
                load_heuristics=task_config.get("load_heuristics", []),
                load_protocols=task_config.get("load_protocols", []),
                load_tools=task_config.get("load_tools", [])
            )
        else:
            self.current_task = self.detect_task_type(user_input)

        # Clear previous tiers
        self.loaded_tiers.clear()

        # Load tiers based on task requirements
        self._load_required_tiers(user_input)
        self._load_optional_tiers()

        # Check budget and prune if necessary
        pruning_occurred = self._check_budget_and_prune()

        # Build final context string
        context_string = self._format_context()

        # Record metrics
        total_load_time = (time.time() - start_time) * 1000
        self.metrics.record_request(
            task_type=self.current_task.task_type,
            pruning_occurred=pruning_occurred,
            total_load_time_ms=total_load_time
        )

        return context_string

    def _load_required_tiers(self, user_input: str):
        """Load all required tiers for current task."""
        if not self.current_task:
            return

        for tier_num in self.current_task.required_tiers:
            if tier_num == 1:
                self._load_tier1(user_input)
            elif tier_num == 2:
                self._load_tier2()
            elif tier_num == 3:
                self._load_tier3()
            elif tier_num == 4:
                self._load_tier4()

    def _load_optional_tiers(self):
        """Load optional tiers if budget allows."""
        if not self.current_task:
            return

        current_tokens = sum(
            tier.token_estimate for tier in self.loaded_tiers.values()
        )
        soft_limit = self.config["total_budget"]["soft_limit"]

        for tier_num in self.current_task.optional_tiers:
            # Check if we have room
            if current_tokens >= soft_limit * 0.8:  # Leave 20% buffer
                break

            if tier_num == 1 and ContextTier.TIER1_IMMEDIATE not in self.loaded_tiers:
                self._load_tier1("")
            elif tier_num == 2 and ContextTier.TIER2_WORKING not in self.loaded_tiers:
                self._load_tier2()
            elif tier_num == 3 and ContextTier.TIER3_REFERENCE not in self.loaded_tiers:
                self._load_tier3()
            elif tier_num == 4 and ContextTier.TIER4_BACKGROUND not in self.loaded_tiers:
                self._load_tier4()

            # Recalculate tokens
            current_tokens = sum(
                tier.token_estimate for tier in self.loaded_tiers.values()
            )

    def _load_tier1(self, user_input: str):
        """Load Tier 1: Immediate context."""
        tier_content = self.tier_loader.load_tier1_immediate(
            current_request=user_input,
            conversation_history=self.conversation_history,
            current_task_status={
                "task_type": self.current_task.task_type if self.current_task else "unknown",
                "active_tools": list(self.active_tools)
            }
        )

        self.loaded_tiers[ContextTier.TIER1_IMMEDIATE] = tier_content
        self.metrics.record_load(
            tier="tier1",
            tokens=tier_content.token_estimate,
            items=len(tier_content.items),
            load_time_ms=tier_content.load_time_ms
        )

    def _load_tier2(self):
        """Load Tier 2: Working context."""
        tier_content = self.tier_loader.load_tier2_working(
            musical_intent=self.musical_intent,
            discovered_samples=self.discovered_samples,
            search_results=self.search_results,
            active_tools=list(self.active_tools) if self.active_tools else None
        )

        self.loaded_tiers[ContextTier.TIER2_WORKING] = tier_content
        self.metrics.record_load(
            tier="tier2",
            tokens=tier_content.token_estimate,
            items=len(tier_content.items),
            load_time_ms=tier_content.load_time_ms
        )

    def _load_tier3(self):
        """Load Tier 3: Reference context."""
        heuristics = self.current_task.load_heuristics if self.current_task else []
        load_registry = "search" in self.current_task.task_type if self.current_task else False

        tier_content = self.tier_loader.load_tier3_reference(
            heuristics=heuristics,
            load_tool_registry=load_registry
        )

        if tier_content.content:  # Only add if there's content
            self.loaded_tiers[ContextTier.TIER3_REFERENCE] = tier_content
            self.metrics.record_load(
                tier="tier3",
                tokens=tier_content.token_estimate,
                items=len(tier_content.items),
                load_time_ms=tier_content.load_time_ms
            )

    def _load_tier4(self):
        """Load Tier 4: Background context."""
        protocols = self.current_task.load_protocols if self.current_task else []

        # Determine which examples to load based on task type
        examples = []
        if self.current_task:
            if "search" in self.current_task.task_type:
                examples = ["search_queries/good_examples.md"]
            elif "vibe" in self.current_task.task_type:
                examples = ["vibe_analysis/reasoning_examples.md"]

        tier_content = self.tier_loader.load_tier4_background(
            thinking_protocols=protocols,
            example_libraries=examples,
            specialist_sections=None
        )

        if tier_content.content:  # Only add if there's content
            self.loaded_tiers[ContextTier.TIER4_BACKGROUND] = tier_content
            self.metrics.record_load(
                tier="tier4",
                tokens=tier_content.token_estimate,
                items=len(tier_content.items),
                load_time_ms=tier_content.load_time_ms
            )

    def _check_budget_and_prune(self) -> bool:
        """
        Check if we're over budget and prune if necessary.

        Returns True if pruning occurred.
        """
        current_tokens = sum(
            tier.token_estimate for tier in self.loaded_tiers.values()
        )

        soft_limit = self.config["total_budget"]["soft_limit"]
        hard_limit = self.config["total_budget"]["hard_limit"]

        # Check warning threshold
        warning_threshold = self.config["total_budget"]["warning_threshold"]
        if current_tokens >= warning_threshold:
            self.metrics.record_budget_warning()

        # Prune if over soft limit
        if current_tokens <= soft_limit:
            return False

        # Record budget exceeded
        if current_tokens >= hard_limit:
            self.metrics.record_budget_exceeded()

        # Prune based on strategy
        pruning_strategy = self.config["pruning_strategy"]
        prune_order = pruning_strategy["prune_order"]

        for tier_num in prune_order:
            tier_map = {
                1: ContextTier.TIER1_IMMEDIATE,
                2: ContextTier.TIER2_WORKING,
                3: ContextTier.TIER3_REFERENCE,
                4: ContextTier.TIER4_BACKGROUND
            }

            tier = tier_map.get(tier_num)
            if tier and tier in self.loaded_tiers:
                # Don't prune tier 1 if preserve_tier1 is true
                if tier == ContextTier.TIER1_IMMEDIATE and pruning_strategy["preserve_tier1"]:
                    continue

                # Remove tier
                removed_content = self.loaded_tiers.pop(tier)
                self.metrics.record_prune(f"tier{tier_num}", removed_content.token_estimate)

                # Check if we're under budget now
                current_tokens = sum(
                    t.token_estimate for t in self.loaded_tiers.values()
                )

                if current_tokens <= soft_limit:
                    return True

        return True

    def _format_context(self) -> str:
        """Format loaded tiers into context string."""
        context_parts = ["# CONTEXT INFORMATION\n"]

        # Add tiers in order
        tier_order = [
            ContextTier.TIER1_IMMEDIATE,
            ContextTier.TIER2_WORKING,
            ContextTier.TIER3_REFERENCE,
            ContextTier.TIER4_BACKGROUND
        ]

        for tier in tier_order:
            if tier in self.loaded_tiers:
                tier_content = self.loaded_tiers[tier]
                context_parts.append(f"\n# {tier.value.upper()}\n")
                context_parts.append(tier_content.content)
                context_parts.append("\n")

        return "\n".join(context_parts)

    def add_exchange(self, user_input: str, agent_response: str):
        """Add a conversation exchange to history."""
        self.conversation_history.append({
            "user": user_input,
            "agent": agent_response
        })

        # Keep history manageable
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def update_musical_intent(self, intent: Dict[str, Any]):
        """Update current musical intent."""
        self.musical_intent = intent

    def add_discovered_sample(self, sample: Dict[str, Any]):
        """Add a discovered sample to working context."""
        self.discovered_samples.append(sample)

        # Keep manageable size
        max_samples = self.config["tier2_sources"]["discovered_samples"]["max_samples"]
        if len(self.discovered_samples) > max_samples * 2:
            self.discovered_samples = self.discovered_samples[-max_samples * 2:]

    def update_search_results(self, results: List[Dict[str, Any]]):
        """Update current search results."""
        self.search_results = results

    def register_active_tool(self, tool_name: str):
        """Register a tool as active."""
        self.active_tools.add(tool_name)

    def clear_active_tools(self):
        """Clear all active tools."""
        self.active_tools.clear()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        return self.metrics.get_summary()

    def get_context_string(self) -> str:
        """
        Get formatted conversation history (backwards compatibility).

        This method provides compatibility with the old ConversationContext API.
        """
        if not self.conversation_history:
            return ""

        context = "Previous conversation:\n"
        for exchange in self.conversation_history[-3:]:
            context += f"User: {exchange['user']}\n"
            context += f"Agent: {exchange['agent'][:200]}...\n\n"

        return context

    def reset(self):
        """Reset all context and metrics."""
        self.loaded_tiers.clear()
        self.conversation_history.clear()
        self.current_task = None
        self.musical_intent = None
        self.discovered_samples.clear()
        self.search_results.clear()
        self.active_tools.clear()
        self.metrics.reset()

    def export_metrics(self, filepath: str):
        """Export metrics to file."""
        self.metrics.export_json(filepath)

    def __repr__(self) -> str:
        loaded_tier_names = [t.value for t in self.loaded_tiers.keys()]
        return (
            f"IntelligentContextManager("
            f"loaded_tiers={loaded_tier_names}, "
            f"conversation_length={len(self.conversation_history)}, "
            f"total_tokens={self.metrics.current_tokens})"
        )
