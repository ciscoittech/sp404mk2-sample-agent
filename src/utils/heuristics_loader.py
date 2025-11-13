"""Heuristics Loader Utility

Loads and formats heuristics from XML files for injection into LLM prompts.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import lru_cache


class HeuristicsLoader:
    """Load and parse heuristics XML files for agent use."""

    def __init__(self, heuristics_dir: Optional[Path] = None):
        """Initialize loader with heuristics directory.

        Args:
            heuristics_dir: Path to .claude/heuristics/ directory.
                          If None, uses default location.
        """
        if heuristics_dir is None:
            # Default to .claude/heuristics/ relative to project root
            project_root = Path(__file__).parent.parent.parent
            heuristics_dir = project_root / ".claude" / "heuristics"

        self.heuristics_dir = Path(heuristics_dir)

        if not self.heuristics_dir.exists():
            raise FileNotFoundError(
                f"Heuristics directory not found: {self.heuristics_dir}"
            )

    @lru_cache(maxsize=32)
    def load_heuristic(self, domain: str, heuristic_id: Optional[str] = None) -> Dict[str, Any]:
        """Load specific heuristic from XML file.

        Args:
            domain: Domain name (matches XML filename without .xml)
            heuristic_id: Specific heuristic ID to load. If None, loads all.

        Returns:
            Dictionary containing heuristic data

        Example:
            >>> loader = HeuristicsLoader()
            >>> h = loader.load_heuristic("search_intent_detection", "detect_sample_search")
            >>> print(h['name'])
            'Detect Sample Search Intent'
        """
        xml_file = self.heuristics_dir / f"{domain}.xml"

        if not xml_file.exists():
            raise FileNotFoundError(f"Heuristic file not found: {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        if heuristic_id:
            # Find specific heuristic by ID
            heuristic_elem = root.find(f".//heuristic[@id='{heuristic_id}']")
            if heuristic_elem is None:
                raise ValueError(
                    f"Heuristic '{heuristic_id}' not found in {domain}"
                )
            return self._parse_heuristic_element(heuristic_elem)
        else:
            # Load all heuristics in domain
            heuristics = []
            for h_elem in root.findall(".//heuristic"):
                heuristics.append(self._parse_heuristic_element(h_elem))
            return {
                "domain": domain,
                "heuristics": heuristics,
                "metadata": self._parse_metadata(root)
            }

    def _parse_heuristic_element(self, elem: ET.Element) -> Dict[str, Any]:
        """Parse a single heuristic XML element into dictionary."""
        heuristic = {
            "id": elem.get("id"),
            "name": self._get_text(elem, "name"),
            "when": self._get_text(elem, "when"),
            "generally": self._get_text(elem, "generally"),
            "unless": self._get_text(elem, "unless"),
        }

        # Parse consider factors
        consider_elem = elem.find("consider")
        if consider_elem is not None:
            heuristic["consider"] = [
                factor.text.strip()
                for factor in consider_elem.findall("factor")
                if factor.text
            ]

        # Parse examples
        examples_elem = elem.find("examples")
        if examples_elem is not None:
            heuristic["examples"] = self._parse_examples(examples_elem)

        return heuristic

    def _parse_examples(self, examples_elem: ET.Element) -> List[Dict]:
        """Parse examples from XML."""
        examples = []
        for ex in examples_elem.findall("example"):
            example = {
                "outcome": ex.get("outcome"),
                "input": self._get_text(ex, "input"),
                "reasoning": self._get_text(ex, "reasoning"),
                "confidence": float(self._get_text(ex, "confidence", "0.0"))
            }
            examples.append(example)
        return examples

    def _parse_metadata(self, root: ET.Element) -> Dict:
        """Parse metadata section."""
        metadata_elem = root.find("metadata")
        if metadata_elem is None:
            return {}

        return {
            "version": self._get_text(metadata_elem, "version"),
            "description": self._get_text(metadata_elem, "description"),
            "last_updated": self._get_text(metadata_elem, "last_updated")
        }

    def _get_text(self, elem: ET.Element, tag: str, default: str = "") -> str:
        """Safely get text from XML element."""
        child = elem.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    def format_for_prompt(
        self,
        domain: str,
        heuristic_id: Optional[str] = None,
        include_examples: bool = True,
        max_examples: int = 3
    ) -> str:
        """Format heuristic for injection into LLM prompt.

        Args:
            domain: Domain name
            heuristic_id: Specific heuristic ID (None for all)
            include_examples: Whether to include examples
            max_examples: Maximum number of examples to include

        Returns:
            Formatted string ready for prompt injection

        Example:
            >>> loader = HeuristicsLoader()
            >>> prompt_text = loader.format_for_prompt("search_intent_detection")
            >>> # Use in agent prompt:
            >>> agent_prompt = f"{prompt_text}\\n\\nNow analyze: {user_input}"
        """
        data = self.load_heuristic(domain, heuristic_id)

        if heuristic_id:
            # Single heuristic
            return self._format_single_heuristic(data, include_examples, max_examples)
        else:
            # Multiple heuristics
            formatted = f"# {data['domain'].replace('_', ' ').title()} Heuristics\n\n"

            if "metadata" in data and data["metadata"].get("description"):
                formatted += f"{data['metadata']['description']}\n\n"

            for h in data["heuristics"]:
                formatted += self._format_single_heuristic(h, include_examples, max_examples)
                formatted += "\n---\n\n"

            return formatted

    def _format_single_heuristic(
        self,
        heuristic: Dict,
        include_examples: bool,
        max_examples: int
    ) -> str:
        """Format a single heuristic for prompt."""
        formatted = f"## {heuristic['name']}\n\n"

        # WHEN section
        if heuristic.get("when"):
            formatted += f"**When to use:** {heuristic['when']}\n\n"

        # CONSIDER section
        if heuristic.get("consider"):
            formatted += "**Consider these factors:**\n"
            for factor in heuristic["consider"]:
                formatted += f"- {factor}\n"
            formatted += "\n"

        # GENERALLY section
        if heuristic.get("generally"):
            formatted += f"**General guideline:**\n{heuristic['generally']}\n\n"

        # UNLESS section
        if heuristic.get("unless"):
            formatted += f"**Exceptions:**\n{heuristic['unless']}\n\n"

        # EXAMPLES section
        if include_examples and heuristic.get("examples"):
            formatted += "**Examples:**\n\n"
            examples = heuristic["examples"][:max_examples]
            for i, ex in enumerate(examples, 1):
                formatted += f"{i}. **{ex.get('outcome', 'Example')}**\n"
                if ex.get("input"):
                    formatted += f"   Input: \"{ex['input']}\"\n"
                if ex.get("reasoning"):
                    formatted += f"   Reasoning: {ex['reasoning']}\n"
                if ex.get("confidence"):
                    formatted += f"   Confidence: {ex['confidence']:.2f}\n"
                formatted += "\n"

        return formatted

    def get_quick_reference(self, domain: str, heuristic_id: str) -> str:
        """Get condensed quick-reference version of heuristic.

        Useful for including in prompts where space is limited.
        Omits examples and detailed explanations.

        Args:
            domain: Domain name
            heuristic_id: Specific heuristic ID

        Returns:
            Condensed heuristic text
        """
        h = self.load_heuristic(domain, heuristic_id)

        quick_ref = f"{h['name']}: "

        if h.get("generally"):
            # Take first sentence only
            generally = h["generally"].split(".")[0] + "."
            quick_ref += generally

        if h.get("unless"):
            unless = h["unless"].split(".")[0] + "."
            quick_ref += f" Unless: {unless}"

        return quick_ref

    def list_available_heuristics(self) -> Dict[str, List[str]]:
        """List all available heuristics by domain.

        Returns:
            Dictionary mapping domain names to lists of heuristic IDs
        """
        heuristics_by_domain = {}

        for xml_file in self.heuristics_dir.glob("*.xml"):
            domain = xml_file.stem
            tree = ET.parse(xml_file)
            root = tree.getroot()

            heuristic_ids = [
                elem.get("id")
                for elem in root.findall(".//heuristic")
                if elem.get("id")
            ]

            heuristics_by_domain[domain] = heuristic_ids

        return heuristics_by_domain


# Convenience functions for common use cases

def get_search_intent_heuristic() -> str:
    """Get formatted search intent detection heuristic for prompts."""
    loader = HeuristicsLoader()
    return loader.format_for_prompt(
        "search_intent_detection",
        "detect_sample_search",
        include_examples=True,
        max_examples=3
    )


def get_query_generation_heuristics() -> str:
    """Get formatted query generation heuristics for prompts."""
    loader = HeuristicsLoader()
    return loader.format_for_prompt(
        "query_generation",
        include_examples=True,
        max_examples=2
    )


def get_quality_assessment_heuristic(heuristic_id: str = "youtube_source_quality") -> str:
    """Get formatted quality assessment heuristic for prompts.

    Args:
        heuristic_id: Which quality heuristic to use. Options:
            - "youtube_source_quality" (default)
            - "audio_sample_quality"
            - "musical_quality"
            - "usability_assessment"
    """
    loader = HeuristicsLoader()
    return loader.format_for_prompt(
        "sample_quality_assessment",
        heuristic_id,
        include_examples=True,
        max_examples=2
    )


# Example usage
if __name__ == "__main__":
    # Demo the loader
    loader = HeuristicsLoader()

    print("=== Available Heuristics ===")
    for domain, ids in loader.list_available_heuristics().items():
        print(f"\n{domain}:")
        for hid in ids:
            print(f"  - {hid}")

    print("\n\n=== Search Intent Heuristic (Formatted for Prompt) ===")
    print(get_search_intent_heuristic())

    print("\n\n=== Quick Reference Example ===")
    quick = loader.get_quick_reference(
        "query_generation",
        "sample_indicator_inclusion"
    )
    print(quick)
