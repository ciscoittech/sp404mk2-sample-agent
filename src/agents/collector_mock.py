"""Mock Collector Agent for demos without API calls."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from ..logging_config import AgentLogger
from ..tools import database
from .base import Agent, AgentResult, AgentStatus


class CollectorAgent(Agent):
    """Mock agent responsible for discovering and categorizing samples."""
    
    def __init__(self):
        """Initialize the Collector Agent."""
        super().__init__("collector")
        self.logger = AgentLogger(self.name)
        
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Mock sample discovery based on criteria.
        
        Args:
            task_id: Unique task identifier
            genre: Musical genre to search for
            style: Specific style within genre
            bpm_range: Tuple of (min_bpm, max_bpm)
            key: Musical key preference
            era: Time period for samples
            max_results: Maximum number of results
            
        Returns:
            AgentResult with discovered sample sources
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting mock sample collection")
        started_at = datetime.now(timezone.utc)
        
        try:
            # Extract parameters
            genre = kwargs.get("genre", "electronic")
            style = kwargs.get("style", "")
            bpm_range = kwargs.get("bpm_range")
            max_results = kwargs.get("max_results", 10)
            
            # Generate mock samples based on genre
            sources = self._generate_mock_samples(genre, style, bpm_range, max_results)
            
            # Log success
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "info",
                "message": f"Mock discovered {len(sources)} samples",
                "context": {"genre": genre, "count": len(sources)}
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result={
                    "sources": sources,
                    "search_queries": [f"{genre} {style} samples"],
                    "total_found": len(sources)
                },
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.exception(f"Mock collection failed: {str(e)}")
            
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": f"Mock collection failed: {str(e)}",
                "context": {"error": str(e)}
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    def _generate_mock_samples(
        self, 
        genre: str, 
        style: str,
        bpm_range: Optional[Tuple[int, int]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Generate mock sample data based on genre."""
        
        # Mock sample templates by genre
        templates = {
            "jazz": [
                {"title": "Bebop Drum Break", "bpm": 140, "key": None, "duration": 8},
                {"title": "Walking Bass Line", "bpm": 120, "key": "F", "duration": 16},
                {"title": "Piano Comping Pattern", "bpm": 130, "key": "Bb", "duration": 12},
                {"title": "Brush Drums Groove", "bpm": 90, "key": None, "duration": 10},
                {"title": "Upright Bass Solo", "bpm": 110, "key": "C", "duration": 20}
            ],
            "hip-hop": [
                {"title": "Boom Bap Drums", "bpm": 93, "key": None, "duration": 8},
                {"title": "Soul Chop Sample", "bpm": 87, "key": "Am", "duration": 4},
                {"title": "Vinyl Crackle Loop", "bpm": 90, "key": None, "duration": 16},
                {"title": "Bass Heavy Beat", "bpm": 85, "key": "Dm", "duration": 8},
                {"title": "Old School Break", "bpm": 95, "key": None, "duration": 12}
            ],
            "electronic": [
                {"title": "Techno Kick Pattern", "bpm": 128, "key": None, "duration": 16},
                {"title": "Acid Bass Loop", "bpm": 130, "key": "A", "duration": 8},
                {"title": "Ambient Pad", "bpm": 120, "key": "Em", "duration": 32},
                {"title": "Glitch Percussion", "bpm": 140, "key": None, "duration": 4},
                {"title": "Synth Arpeggio", "bpm": 125, "key": "G", "duration": 16}
            ]
        }
        
        # Get templates for genre or use default
        genre_templates = templates.get(genre.lower(), templates["electronic"])
        
        # Add style prefix if provided
        if style:
            for template in genre_templates:
                template["title"] = f"{style.title()} {template['title']}"
        
        # Filter by BPM range if provided
        if bpm_range:
            min_bpm, max_bpm = bpm_range
            genre_templates = [
                t for t in genre_templates 
                if min_bpm <= t["bpm"] <= max_bpm
            ]
        
        # Create mock sources
        sources = []
        for i, template in enumerate(genre_templates[:max_results]):
            source = {
                "url": f"https://youtube.com/watch?v=mock_{genre}_{i}",
                "title": f"{template['title']} - {template['bpm']} BPM",
                "platform": "youtube",
                "duration": template["duration"],
                "description": f"High quality {genre} sample, perfect for SP404MK2",
                "metadata": {
                    "channel": f"{genre.title()} Samples Channel",
                    "views": 10000 + (i * 1000),
                    "likes": 500 + (i * 50),
                    "upload_date": "2025-01-15"
                },
                "estimated_bpm": template["bpm"],
                "estimated_key": template["key"],
                "tags": [genre, style, f"{template['bpm']}bpm", "sample", "sp404"]
            }
            sources.append(source)
        
        return sources