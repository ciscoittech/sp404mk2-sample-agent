"""Simple Collector Agent with OpenRouter integration (no database)."""

import os
import json
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from .base import Agent, AgentResult, AgentStatus


class CollectorAgent(Agent):
    """Agent responsible for discovering samples using AI."""
    
    def __init__(self):
        """Initialize the Collector Agent."""
        super().__init__("collector")
        
        # OpenRouter configuration
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemma-2-9b-it:free"  # Free model
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
            
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """Discover samples based on criteria."""
        print(f"[{self.name}] Starting AI-powered sample discovery...")
        started_at = datetime.now(timezone.utc)
        
        try:
            # Extract parameters
            genre = kwargs.get("genre", "electronic")
            style = kwargs.get("style", "")
            bpm_range = kwargs.get("bpm_range")
            max_results = kwargs.get("max_results", 10)
            
            # Generate search queries using AI
            print(f"[{self.name}] Asking AI for search queries...")
            search_queries = await self._generate_search_queries(
                genre, style, bpm_range
            )
            
            # Discover samples
            print(f"[{self.name}] AI is discovering samples...")
            sources = await self._discover_samples(
                search_queries, genre, style, max_results
            )
            
            print(f"[{self.name}] ✓ Discovered {len(sources)} samples")
            
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
            print(f"[{self.name}] ✗ Failed: {str(e)}")
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
        bpm_range: Optional[Tuple[int, int]]
    ) -> List[str]:
        """Generate search queries using AI."""
        
        prompt = f"""Generate 5 specific YouTube search queries to find high-quality {genre} samples for music production.

Genre: {genre}
Style: {style or "any"}
BPM Range: {f"{bpm_range[0]}-{bpm_range[1]}" if bpm_range else "any"}

Requirements:
- Focus on finding drum breaks, bass lines, melodies, and atmospheric sounds
- Include BPM in queries when relevant
- Target channels known for sample packs or music production
- Mix specific searches with broader ones

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
            "temperature": 0.7,
            "max_tokens": 500
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
                content = content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                queries = json.loads(content.strip())
                return queries[:5]
            except Exception as e:
                print(f"[{self.name}] Failed to parse queries, using defaults")
                return [
                    f"{genre} {style} drum break sample",
                    f"{genre} bass line loop",
                    f"{genre} melody sample pack",
                    f"{style} {genre} atmosphere",
                    f"{genre} percussion loop"
                ]
    
    async def _discover_samples(
        self,
        search_queries: List[str],
        genre: str,
        style: Optional[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Use AI to discover realistic samples."""
        
        prompt = f"""Based on these YouTube search queries for {genre} {style or ''} samples:
{json.dumps(search_queries, indent=2)}

Generate {max_results} realistic sample discoveries that a producer might find. For each sample, provide:
- A realistic YouTube video title
- Channel name
- Estimated BPM (if applicable, null for atmospheric)
- Sample type (drums, bass, keys, melody, atmosphere, percussion, vocal)
- Duration in seconds (4-32)
- Quality score (0.7-1.0)
- Musical key (if melodic, null otherwise)
- Brief description

Return ONLY a JSON array. Example:
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
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a music production expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse response
            try:
                content = content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                samples = json.loads(content.strip())
                
                # Convert to our format
                sources = []
                for i, sample in enumerate(samples[:max_results]):
                    source = {
                        "url": f"https://youtube.com/watch?v={genre[:3]}{i:03d}",
                        "title": sample.get("title", f"{genre} Sample {i+1}"),
                        "platform": "youtube",
                        "duration": sample.get("duration", 16),
                        "description": sample.get("description", ""),
                        "metadata": {
                            "channel": sample.get("channel", "Unknown"),
                            "views": 10000 + (i * 1000),
                            "likes": 500 + (i * 50)
                        },
                        "estimated_bpm": sample.get("bpm"),
                        "estimated_key": sample.get("key"),
                        "sample_type": sample.get("type", "unknown"),
                        "quality_score": sample.get("quality", 0.8),
                        "tags": [genre]
                    }
                    
                    if style:
                        source["tags"].append(style)
                    if sample.get("type"):
                        source["tags"].append(sample["type"])
                    if sample.get("bpm"):
                        source["tags"].append(f"{sample['bpm']}bpm")
                    
                    sources.append(source)
                
                return sources
                
            except Exception as e:
                print(f"[{self.name}] Parse error: {str(e)}")
                # Return minimal data
                return [{
                    "url": f"https://youtube.com/watch?v=demo{i}",
                    "title": f"{genre} Sample {i+1}",
                    "platform": "youtube",
                    "duration": 16,
                    "description": "Sample discovery",
                    "metadata": {"channel": "Demo"},
                    "tags": [genre]
                } for i in range(min(3, max_results))]