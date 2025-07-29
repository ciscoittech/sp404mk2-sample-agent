"""
Smart specialist assignment for sample-related tasks.
Analyzes task requirements and assigns appropriate specialists.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Specialist:
    """Represents a specialist with their expertise."""
    id: str
    name: str
    triggers: List[str]
    description: str


# Define available specialists
SPECIALISTS = {
    "groove-analyst": Specialist(
        id="groove-analyst",
        name="Groove Analyst",
        triggers=["drum", "rhythm", "swing", "timing", "groove", "beat", "bpm"],
        description="Rhythm, timing, and swing analysis"
    ),
    "era-expert": Specialist(
        id="era-expert",
        name="Era Expert",
        triggers=["vintage", "70s", "80s", "90s", "era", "old school", "classic", "retro"],
        description="Musical history and production techniques"
    ),
    "vibe-analyst": Specialist(
        id="vibe-analyst",
        name="Vibe Analyst",
        triggers=["mood", "vibe", "feeling", "texture", "atmosphere", "emotional", "energy"],
        description="Mood, texture, and emotional qualities"
    ),
    "sample-compatibility": Specialist(
        id="sample-compatibility",
        name="Sample Compatibility",
        triggers=["match", "compatible", "work together", "kit", "cohesion", "complement"],
        description="Musical matching and compatibility scoring"
    ),
    "batch-processor": Specialist(
        id="batch-processor",
        name="Batch Processor",
        triggers=["collection", "folder", "batch", "multiple", "many", "hundreds", "thousands"],
        description="Large-scale processing and rate limiting"
    ),
    "kit-builder": Specialist(
        id="kit-builder",
        name="Kit Builder",
        triggers=["kit", "bank", "sp-404", "sp404", "pads", "layout", "performance"],
        description="SP-404 bank assembly and organization"
    ),
    "download-manager": Specialist(
        id="download-manager",
        name="Download Manager",
        triggers=["youtube", "download", "source", "timestamp", "extract", "video"],
        description="Source acquisition and extraction"
    ),
    "musical-search": Specialist(
        id="musical-search",
        name="Musical Search",
        triggers=["find", "search", "discover", "looking for", "need", "want"],
        description="Query optimization and source discovery"
    )
}


# Task type to specialist mapping
TASK_TYPE_SPECIALISTS = {
    "collection": ["musical-search", "download-manager"],
    "analysis": ["vibe-analyst", "groove-analyst"],
    "organization": ["kit-builder", "sample-compatibility"],
    "processing": ["batch-processor", "vibe-analyst"],
    "technical": ["batch-processor"],
    "download": ["download-manager", "musical-search"]
}


class SpecialistAssigner:
    """Assigns specialists based on task analysis."""
    
    def __init__(self):
        self.specialists = SPECIALISTS
        self.task_mappings = TASK_TYPE_SPECIALISTS
    
    def analyze_task_type(self, title: str, description: str) -> str:
        """Determine primary task type from title and description."""
        text = f"{title} {description}".lower()
        
        # Check for task type indicators
        if any(word in text for word in ["download", "youtube", "find", "search"]):
            return "collection"
        elif any(word in text for word in ["analyze", "vibe", "mood", "bpm"]):
            return "analysis"
        elif any(word in text for word in ["organize", "kit", "bank", "arrange"]):
            return "organization"
        elif any(word in text for word in ["process", "batch", "collection", "folder"]):
            return "processing"
        elif any(word in text for word in ["fix", "bug", "error", "slow"]):
            return "technical"
        else:
            return "general"
    
    def find_keyword_specialists(self, text: str) -> List[str]:
        """Find specialists based on keyword matches."""
        text_lower = text.lower()
        matched = []
        
        for spec_id, specialist in self.specialists.items():
            # Check if any trigger words match
            for trigger in specialist.triggers:
                if trigger in text_lower and spec_id not in matched:
                    matched.append(spec_id)
                    break
        
        return matched
    
    def assign_specialists(
        self, 
        title: str, 
        description: str = "", 
        max_specialists: int = 4
    ) -> List[Dict[str, str]]:
        """
        Assign specialists to a task based on analysis.
        
        Returns list of specialist assignments with roles.
        """
        # Determine task type
        task_type = self.analyze_task_type(title, description)
        
        # Get primary specialists for task type
        primary_specialists = self.task_mappings.get(task_type, [])
        
        # Find additional specialists from keywords
        text = f"{title} {description}"
        keyword_specialists = self.find_keyword_specialists(text)
        
        # Combine and deduplicate
        all_specialists = []
        specialist_ids = []
        
        # Add primary specialists first
        for spec_id in primary_specialists:
            if spec_id in self.specialists and spec_id not in specialist_ids:
                specialist_ids.append(spec_id)
                spec = self.specialists[spec_id]
                all_specialists.append({
                    "id": spec_id,
                    "name": spec.name,
                    "role": f"Primary - {spec.description}"
                })
        
        # Add keyword specialists
        for spec_id in keyword_specialists:
            if spec_id not in specialist_ids and len(all_specialists) < max_specialists:
                specialist_ids.append(spec_id)
                spec = self.specialists[spec_id]
                all_specialists.append({
                    "id": spec_id,
                    "name": spec.name,
                    "role": f"Support - {spec.description}"
                })
        
        # Limit to max specialists
        return all_specialists[:max_specialists]
    
    def estimate_complexity(self, title: str, description: str, specialists: List[Dict]) -> int:
        """Estimate task complexity (1-10 scale)."""
        text = f"{title} {description}".lower()
        complexity = 5  # Base complexity
        
        # Factors that increase complexity
        if "batch" in text or "collection" in text:
            complexity += 2
        if any(word in text for word in ["hundreds", "thousands", "many"]):
            complexity += 2
        if len(specialists) >= 3:
            complexity += 1
        if "complex" in text or "difficult" in text:
            complexity += 1
        
        # Factors that decrease complexity  
        if "simple" in text or "basic" in text:
            complexity -= 2
        if "single" in text or "one" in text:
            complexity -= 1
        
        # Clamp to 1-10 range
        return max(1, min(10, complexity))
    
    def suggest_labels(
        self, 
        task_type: str, 
        specialists: List[Dict],
        complexity: int
    ) -> List[str]:
        """Suggest GitHub labels for the issue."""
        labels = []
        
        # Task type label
        type_labels = {
            "collection": "collection",
            "analysis": "analysis",
            "organization": "organization", 
            "processing": "processing",
            "technical": "bug",
            "general": "enhancement"
        }
        labels.append(type_labels.get(task_type, "task"))
        
        # Specialist-based labels
        specialist_labels = {
            "vibe-analyst": "vibe",
            "groove-analyst": "groove",
            "batch-processor": "batch",
            "kit-builder": "kit",
            "download-manager": "youtube",
            "era-expert": "vintage"
        }
        
        for spec in specialists[:2]:  # Max 2 specialist labels
            if spec["id"] in specialist_labels:
                labels.append(specialist_labels[spec["id"]])
        
        # Size label based on complexity
        if complexity <= 3:
            labels.append("small")
        elif complexity <= 6:
            labels.append("medium")
        else:
            labels.append("large")
        
        # Priority (simplified)
        if complexity >= 8 or task_type == "technical":
            labels.append("high-priority")
        
        return labels


# Convenience function
def assign_specialists_for_task(
    title: str, 
    description: str = ""
) -> Dict[str, any]:
    """
    Main function to assign specialists and analyze a task.
    
    Returns:
        Dictionary with task analysis including specialists, complexity, labels
    """
    assigner = SpecialistAssigner()
    
    # Analyze task
    task_type = assigner.analyze_task_type(title, description)
    specialists = assigner.assign_specialists(title, description)
    complexity = assigner.estimate_complexity(title, description, specialists)
    labels = assigner.suggest_labels(task_type, specialists, complexity)
    
    return {
        "task_type": task_type,
        "specialists": specialists,
        "complexity": complexity,
        "labels": labels,
        "time_estimate": estimate_time(complexity),
    }


def estimate_time(complexity: int) -> str:
    """Estimate time based on complexity."""
    if complexity <= 2:
        return "30 minutes"
    elif complexity <= 4:
        return "1-2 hours"
    elif complexity <= 6:
        return "2-4 hours"
    elif complexity <= 8:
        return "1-2 days"
    else:
        return "2-5 days"


# Example usage
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("Process Wanns Wavs collection for vibe analysis", 
         "Need to analyze 500+ samples for mood and compatibility"),
        
        ("Find boom bap drums from YouTube", 
         "Looking for 90s hip-hop drum breaks"),
        
        ("Build jazz kit from existing samples", 
         "Organize my jazz samples into SP-404 bank"),
        
        ("Fix slow batch processing", 
         "Processing taking too long for large collections")
    ]
    
    for title, desc in test_cases:
        print(f"\nTask: {title}")
        result = assign_specialists_for_task(title, desc)
        print(f"Type: {result['task_type']}")
        print(f"Complexity: {result['complexity']}/10")
        print(f"Time: {result['time_estimate']}")
        print(f"Labels: {', '.join(result['labels'])}")
        print("Specialists:")
        for spec in result['specialists']:
            print(f"  - {spec['name']}: {spec['role']}")