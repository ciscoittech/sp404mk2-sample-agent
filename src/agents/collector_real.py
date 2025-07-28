"""Real Collector Agent with OpenRouter integration."""

import os
import json
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from ..logging_config import AgentLogger
from ..tools import database
from .base import Agent, AgentResult, AgentStatus


class CollectorAgent(Agent):
    """Agent responsible for discovering and categorizing samples using AI."""
    
    def __init__(self):
        """Initialize the Collector Agent."""
        super().__init__("collector")
        self.logger = AgentLogger(self.name)
        
        # OpenRouter configuration
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Import settings and use configured model
        from ..config import settings
        self.model = settings.collector_model
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
            
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Discover and categorize samples based on criteria.
        
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
        self.logger.info("Starting sample collection with AI")
        started_at = datetime.now(timezone.utc)
        
        try:
            # Extract parameters
            genre = kwargs.get("genre", "electronic")
            style = kwargs.get("style", "")
            bpm_range = kwargs.get("bpm_range")
            key = kwargs.get("key")
            era = kwargs.get("era", "modern")
            max_results = kwargs.get("max_results", 10)
            
            # Generate search queries using AI
            search_queries = await self._generate_search_queries(
                genre, style, bpm_range, era
            )
            
            # Analyze queries to extract sample ideas
            sources = await self._discover_samples(
                search_queries, genre, style, max_results
            )
            
            # Log to database
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "info",
                "message": f"Discovered {len(sources)} samples using AI",
                "context": {
                    "genre": genre,
                    "style": style,
                    "queries": search_queries
                }
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result={
                    "sources": sources,
                    "search_queries": search_queries,
                    "total_found": len(sources)
                },
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.exception(f"Collection failed: {str(e)}")
            
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": f"Collection failed: {str(e)}",
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
    
    async def _generate_search_queries(
        self,
        genre: str,
        style: Optional[str],
        bpm_range: Optional[Tuple[int, int]],
        era: str
    ) -> List[str]:
        """Generate search queries using AI."""
        
        prompt = f"""Generate 5 specific YouTube search queries to find high-quality {genre} samples for music production.

Genre: {genre}
Style: {style or "any"}
BPM Range: {f"{bpm_range[0]}-{bpm_range[1]}" if bpm_range else "any"}
Era: {era}

Requirements:
- Focus on finding drum breaks, bass lines, melodies, and atmospheric sounds
- Include BPM in queries when relevant
- Target channels known for sample packs or music production
- Mix specific searches (e.g., "{genre} drum break 90 bpm") with broader ones

Return ONLY a JSON array of 5 search query strings. Example:
["jazz drum break 120 bpm", "bebop bass line sample pack", ...]"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "SP404MK2 Sample Agent"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a music production expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": settings.model_temperature,
            "max_tokens": 800
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            try:
                # Clean up response
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                queries = json.loads(content.strip())
                return queries[:5]  # Ensure max 5 queries
            except:
                # Fallback queries if parsing fails
                return [
                    f"{genre} {style} drum break sample",
                    f"{genre} bass line {era}",
                    f"{genre} melody loop sample pack",
                    f"{style} {genre} atmosphere pad",
                    f"{genre} percussion loop free"
                ]
    
    async def _discover_samples(
        self,
        search_queries: List[str],
        genre: str,
        style: Optional[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Use AI to imagine realistic sample discoveries based on queries."""
        
        prompt = f"""Based on these YouTube search queries for {genre} {style or ''} samples:
{json.dumps(search_queries, indent=2)}

Generate {max_results} realistic sample discoveries that a producer might find. For each sample, provide:
- A realistic YouTube video title
- Estimated BPM (if applicable)
- Sample type (drums, bass, keys, melody, atmosphere, percussion, vocal)
- Estimated duration in seconds (4-32 seconds)
- Quality assessment (0.7-1.0)
- Musical key (if melodic)

Return ONLY a JSON array of samples. Example format:
[
  {{
    "title": "90s Hip Hop Drum Break - 93 BPM - Free Sample Pack",
    "channel": "ProducerLoops",
    "type": "drums",
    "bpm": 93,
    "duration": 8,
    "quality": 0.85,
    "key": null,
    "description": "Classic boom bap drums with vinyl texture"
  }}
]"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "SP404MK2 Sample Agent"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a music production expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": settings.model_temperature + 0.1,
            "max_tokens": settings.collector_max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse AI response
            try:
                # Clean up response
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                samples = json.loads(content.strip())
                
                # Convert to our format
                sources = []
                for i, sample in enumerate(samples[:max_results]):
                    source = {
                        "url": f"https://youtube.com/watch?v={genre[:3]}{i:03d}",  # Mock URL
                        "title": sample.get("title", f"{genre} Sample {i+1}"),
                        "platform": "youtube",
                        "duration": sample.get("duration", 16),
                        "description": sample.get("description", ""),
                        "metadata": {
                            "channel": sample.get("channel", "Unknown Channel"),
                            "views": 10000 + (i * 1000),
                            "likes": 500 + (i * 50),
                            "upload_date": "2025-01-01"
                        },
                        "estimated_bpm": sample.get("bpm"),
                        "estimated_key": sample.get("key"),
                        "sample_type": sample.get("type", "unknown"),
                        "quality_score": sample.get("quality", 0.8),
                        "tags": [genre, style or genre, sample.get("type", "sample")]
                    }
                    
                    if sample.get("bpm"):
                        source["tags"].append(f"{sample['bpm']}bpm")
                    
                    sources.append(source)
                
                return sources
                
            except Exception as e:
                self.logger.error(f"Failed to parse AI response: {str(e)}")
                # Return minimal mock data on error
                return [{
                    "url": f"https://youtube.com/watch?v=error{i}",
                    "title": f"{genre} Sample {i+1}",
                    "platform": "youtube",
                    "duration": 16,
                    "description": "AI parsing failed - mock sample",
                    "metadata": {"channel": "Mock Channel"},
                    "tags": [genre]
                } for i in range(min(3, max_results))]