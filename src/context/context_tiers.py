"""
Context tier definitions and loaders.

Implements the 4-tier context hierarchy:
- Tier 1: Immediate (current request, recent history)
- Tier 2: Working (active task state, tools)
- Tier 3: Reference (heuristics, documentation)
- Tier 4: Background (thinking protocols, examples)
"""

import time
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import json


class ContextTier(Enum):
    """Context tier levels."""
    TIER1_IMMEDIATE = "tier1_immediate"
    TIER2_WORKING = "tier2_working"
    TIER3_REFERENCE = "tier3_reference"
    TIER4_BACKGROUND = "tier4_background"


@dataclass
class TierContent:
    """Content for a specific tier."""
    tier: ContextTier
    content: str
    token_estimate: int
    items: List[str]  # Item identifiers
    load_time_ms: float
    metadata: Dict[str, Any]


class TierLoader:
    """Loads content for different context tiers."""

    def __init__(self, config: Dict[str, Any], project_root: Path):
        self.config = config
        self.project_root = project_root
        self.claude_dir = project_root / ".claude"

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 chars)."""
        return len(text) // 4

    def load_tier1_immediate(
        self,
        current_request: str,
        conversation_history: List[Dict[str, str]],
        current_task_status: Optional[Dict[str, Any]] = None
    ) -> TierContent:
        """Load Tier 1: Immediate context."""
        start_time = time.time()
        content_parts = []
        items = []

        # Current request (always included)
        if current_request:
            content_parts.append("## CURRENT REQUEST")
            content_parts.append(current_request)
            items.append("current_request")

        # Recent conversation history
        conv_config = self.config["tier1_sources"]["conversation_history"]
        if conv_config["enabled"] and conversation_history:
            max_exchanges = conv_config["max_exchanges"]
            max_chars = conv_config["max_chars_per_exchange"]

            content_parts.append("\n## RECENT CONVERSATION")
            recent = conversation_history[-max_exchanges:]

            for i, exchange in enumerate(recent, 1):
                user_msg = exchange.get("user", "")[:max_chars]
                agent_msg = exchange.get("agent", "")[:max_chars]

                content_parts.append(f"\nExchange {i}:")
                content_parts.append(f"User: {user_msg}")
                content_parts.append(f"Agent: {agent_msg}")

            items.append(f"conversation_history_{len(recent)}")

        # Current task status
        if current_task_status and self.config["tier1_sources"]["current_task_status"]["enabled"]:
            content_parts.append("\n## CURRENT TASK STATUS")
            content_parts.append(json.dumps(current_task_status, indent=2))
            items.append("task_status")

        content = "\n".join(content_parts)
        load_time = (time.time() - start_time) * 1000

        return TierContent(
            tier=ContextTier.TIER1_IMMEDIATE,
            content=content,
            token_estimate=self.estimate_tokens(content),
            items=items,
            load_time_ms=load_time,
            metadata={"exchange_count": len(conversation_history)}
        )

    def load_tier2_working(
        self,
        musical_intent: Optional[Dict[str, Any]] = None,
        discovered_samples: Optional[List[Dict[str, Any]]] = None,
        search_results: Optional[List[Dict[str, Any]]] = None,
        active_tools: Optional[List[str]] = None
    ) -> TierContent:
        """Load Tier 2: Working context."""
        start_time = time.time()
        content_parts = []
        items = []

        # Musical intent
        intent_config = self.config["tier2_sources"]["musical_intent"]
        if intent_config["enabled"] and musical_intent:
            content_parts.append("## MUSICAL INTENT")
            content_parts.append(json.dumps(musical_intent, indent=2))
            items.append("musical_intent")

        # Discovered samples
        samples_config = self.config["tier2_sources"]["discovered_samples"]
        if samples_config["enabled"] and discovered_samples:
            max_samples = samples_config["max_samples"]
            content_parts.append("\n## DISCOVERED SAMPLES")

            for i, sample in enumerate(discovered_samples[:max_samples], 1):
                content_parts.append(f"\n{i}. {sample.get('title', 'Unknown')}")
                if samples_config["include_metadata"]:
                    content_parts.append(f"   Platform: {sample.get('platform', 'unknown')}")
                    content_parts.append(f"   Quality: {sample.get('quality_score', 0):.2f}")

            items.append(f"samples_{len(discovered_samples[:max_samples])}")

        # Search results
        results_config = self.config["tier2_sources"]["search_results"]
        if results_config["enabled"] and search_results:
            max_results = results_config["max_results"]
            content_parts.append("\n## SEARCH RESULTS")

            for i, result in enumerate(search_results[:max_results], 1):
                content_parts.append(f"{i}. {result.get('title', 'Unknown')}")

            items.append(f"search_results_{len(search_results[:max_results])}")

        # Active tool documentation
        tools_config = self.config["tier2_sources"]["active_tool_docs"]
        if tools_config["enabled"] and active_tools:
            content_parts.append("\n## ACTIVE TOOLS")

            for tool in active_tools:
                tool_doc = self._load_tool_documentation(tool)
                if tool_doc:
                    content_parts.append(f"\n### {tool}")
                    content_parts.append(tool_doc[:500])  # Truncate for working context
                    items.append(f"tool_{tool}")

        content = "\n".join(content_parts)
        load_time = (time.time() - start_time) * 1000

        return TierContent(
            tier=ContextTier.TIER2_WORKING,
            content=content,
            token_estimate=self.estimate_tokens(content),
            items=items,
            load_time_ms=load_time,
            metadata={
                "sample_count": len(discovered_samples) if discovered_samples else 0,
                "tool_count": len(active_tools) if active_tools else 0
            }
        )

    def load_tier3_reference(
        self,
        heuristics: Optional[List[str]] = None,
        load_tool_registry: bool = False
    ) -> TierContent:
        """Load Tier 3: Reference context."""
        start_time = time.time()
        content_parts = []
        items = []

        heur_config = self.config["tier3_sources"]["heuristics"]

        # Load heuristics
        if heur_config["enabled"] and heuristics:
            from src.utils.heuristics_loader import HeuristicsLoader

            loader = HeuristicsLoader(str(self.claude_dir / "heuristics"))
            content_parts.append("## HEURISTICS")

            max_examples = heur_config["max_examples_per_heuristic"]
            include_examples = heur_config["include_examples"]

            for heuristic_spec in heuristics:
                # Parse domain:heuristic_id format
                if ":" in heuristic_spec:
                    domain, heur_id = heuristic_spec.split(":", 1)
                else:
                    # Assume it's a domain with default heuristic
                    domain = heuristic_spec
                    heur_id = None

                try:
                    formatted = loader.format_for_prompt(
                        domain=domain,
                        heuristic_id=heur_id,
                        include_examples=include_examples,
                        max_examples=max_examples
                    )
                    content_parts.append(f"\n### Heuristic: {heuristic_spec}")
                    content_parts.append(formatted)
                    items.append(f"heuristic_{heuristic_spec}")
                except Exception as e:
                    # Silently skip if heuristic not found
                    pass

        # Load tool registry
        registry_config = self.config["tier3_sources"]["tool_registry"]
        if registry_config["enabled"] and load_tool_registry:
            registry_path = self.claude_dir / "tools" / "tool_registry.json"

            if registry_path.exists():
                with open(registry_path) as f:
                    registry = json.load(f)

                content_parts.append("\n## TOOL REGISTRY")
                content_parts.append(json.dumps(registry, indent=2))
                items.append("tool_registry")

        content = "\n".join(content_parts)
        load_time = (time.time() - start_time) * 1000

        return TierContent(
            tier=ContextTier.TIER3_REFERENCE,
            content=content,
            token_estimate=self.estimate_tokens(content),
            items=items,
            load_time_ms=load_time,
            metadata={"heuristic_count": len(heuristics) if heuristics else 0}
        )

    def load_tier4_background(
        self,
        thinking_protocols: Optional[List[str]] = None,
        example_libraries: Optional[List[str]] = None,
        specialist_sections: Optional[List[str]] = None
    ) -> TierContent:
        """Load Tier 4: Background context."""
        start_time = time.time()
        content_parts = []
        items = []

        protocol_config = self.config["tier4_sources"]["thinking_protocols"]

        # Load thinking protocols
        if protocol_config["enabled"] and thinking_protocols:
            content_parts.append("## THINKING PROTOCOLS")

            for protocol in thinking_protocols:
                protocol_path = self.claude_dir / "thinking_protocols" / f"{protocol}.md"

                if protocol_path.exists():
                    with open(protocol_path) as f:
                        content = f.read()

                    # Load condensed version (first 1000 chars + key steps)
                    lines = content.split("\n")
                    condensed = []

                    for line in lines[:50]:  # First 50 lines usually cover structure
                        if line.startswith("#") or "STEP" in line:
                            condensed.append(line)

                    content_parts.append(f"\n### Protocol: {protocol}")
                    content_parts.append("\n".join(condensed))
                    items.append(f"protocol_{protocol}")

        # Load example libraries
        example_config = self.config["tier4_sources"]["example_libraries"]
        if example_config["enabled"] and example_libraries:
            max_examples = example_config["max_examples"]
            content_parts.append("\n## EXAMPLE PATTERNS")

            for lib in example_libraries:
                lib_path = self.claude_dir / "examples" / lib

                if lib_path.exists():
                    with open(lib_path) as f:
                        example_content = f.read()

                    # Extract first N examples (simplified - look for ### markers)
                    examples = []
                    current_example = []
                    example_count = 0

                    for line in example_content.split("\n"):
                        if line.startswith("### "):
                            if current_example and example_count < max_examples:
                                examples.append("\n".join(current_example))
                                example_count += 1
                            current_example = [line]
                        elif current_example:
                            current_example.append(line)

                    if current_example and example_count < max_examples:
                        examples.append("\n".join(current_example))

                    if examples:
                        content_parts.append(f"\n### Examples from {lib}")
                        content_parts.append("\n\n".join(examples))
                        items.append(f"examples_{lib}")

        # Load specialist sections
        specialist_config = self.config["tier4_sources"]["specialist_knowledge"]
        if specialist_config["enabled"] and specialist_sections:
            max_length = specialist_config["max_section_length"]
            content_parts.append("\n## SPECIALIST KNOWLEDGE")

            for section_spec in specialist_sections:
                # Format: filename:section_name
                parts = section_spec.split(":", 1)
                filename = parts[0]
                section = parts[1] if len(parts) > 1 else None

                specialist_path = self.claude_dir / "commands" / filename

                if specialist_path.exists():
                    with open(specialist_path) as f:
                        spec_content = f.read()

                    # Extract section if specified
                    if section:
                        extracted = self._extract_section(spec_content, section, max_length)
                    else:
                        extracted = spec_content[:max_length]

                    content_parts.append(f"\n### {section_spec}")
                    content_parts.append(extracted)
                    items.append(f"specialist_{section_spec}")

        content = "\n".join(content_parts)
        load_time = (time.time() - start_time) * 1000

        return TierContent(
            tier=ContextTier.TIER4_BACKGROUND,
            content=content,
            token_estimate=self.estimate_tokens(content),
            items=items,
            load_time_ms=load_time,
            metadata={
                "protocol_count": len(thinking_protocols) if thinking_protocols else 0,
                "example_count": len(example_libraries) if example_libraries else 0
            }
        )

    def _load_tool_documentation(self, tool_name: str) -> Optional[str]:
        """Load tool documentation file."""
        tool_path = self.claude_dir / "tools" / f"{tool_name}.md"

        if tool_path.exists():
            with open(tool_path) as f:
                content = f.read()
            return content

        return None

    def _extract_section(self, content: str, section_name: str, max_length: int) -> str:
        """Extract a specific section from markdown content."""
        lines = content.split('\n')
        in_section = False
        section_lines = []

        for line in lines:
            if section_name.lower() in line.lower() and line.startswith('#'):
                in_section = True
                section_lines.append(line)
                continue

            if in_section:
                # Stop at next section of same or higher level
                if line.startswith('#') and not line.startswith('##'):
                    break
                section_lines.append(line)

                # Stop if we've collected enough
                if len('\n'.join(section_lines)) >= max_length:
                    break

        result = '\n'.join(section_lines)
        return result[:max_length] if len(result) > max_length else result
