"""
Vibe Analysis Agent - Analyzes musical mood, character, and compatibility of samples.
Uses AI to understand the vibe of audio samples and create complementary kits.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from .base import Agent, AgentStatus
from ..config import settings
from ..logging_config import AgentLogger


class VibeDescriptor(BaseModel):
    """Describes the vibe characteristics of a sample."""
    mood: List[str] = Field(description="3 mood descriptors (e.g., dark, uplifting, tense)")
    era: str = Field(description="Time period or era (e.g., 1970s, modern)")
    genre: str = Field(description="Musical genre or style")
    energy_level: str = Field(description="Energy level: low, medium, high")
    descriptors: List[str] = Field(description="Additional descriptive terms")


class SampleVibe(BaseModel):
    """Complete vibe analysis for a sample."""
    filename: str = Field(description="Sample filename")
    bpm: float = Field(description="Beats per minute")
    key: str = Field(description="Musical key")
    vibe: VibeDescriptor = Field(description="Vibe characteristics")
    compatibility_tags: List[str] = Field(description="Tags for finding compatible samples")
    best_use: str = Field(description="Suggested use: drums, bass, melody, pad, etc.")
    confidence: float = Field(default=0.8, description="Analysis confidence 0-1")


class VibeAnalysisAgent(Agent):
    """Agent that analyzes the vibe and mood of audio samples."""
    
    def __init__(self):
        """Initialize the Vibe Analysis Agent."""
        super().__init__(name="VibeAnalyst")
        self.description = "I analyze the vibe, mood, and character of audio samples"
        
        self.logger = AgentLogger("vibe_analyst")
        self.batch_size = 5  # Process 5 samples per API call
        self.rate_limit = 5  # 5 requests per minute
        self.last_request_time = None
        self.request_count = 0
        self._cache = {}  # Simple in-memory cache
        
        # API configuration
        self.api_key = settings.openrouter_api_key
        self.model = settings.collector_model  # Using the free model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def analyze_vibe(self, sample_data: Dict[str, Any]) -> SampleVibe:
        """Analyze the vibe of a single sample.
        
        Args:
            sample_data: Dictionary with filename, bpm, key, and spectral data
            
        Returns:
            SampleVibe object with complete analysis
        """
        # Check cache first
        cache_key = f"{sample_data['filename']}_{sample_data.get('bpm', 0)}_{sample_data.get('key', '')}"
        if cache_key in self._cache:
            self.logger.info(f"Using cached analysis for {sample_data['filename']}")
            return self._cache[cache_key]
        
        # Apply rate limiting
        await self._apply_rate_limit()
        
        prompt = self.create_single_prompt(sample_data)
        
        try:
            self.status = AgentStatus.RUNNING
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a musical vibe analyst. Analyze samples and return JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    vibe = self.parse_vibe_response(
                        content, 
                        sample_data['filename'],
                        sample_data.get('bpm', 0),
                        sample_data.get('key', '')
                    )
                    
                    # Cache the result
                    self._cache[cache_key] = vibe
                    
                    self.status = AgentStatus.IDLE
                    return vibe
                else:
                    raise Exception(f"API error: {response.status_code}")
                    
        except Exception as e:
            self.logger.error(f"Error analyzing vibe: {str(e)}")
            self.status = AgentStatus.FAILED
            raise
    
    async def analyze_batch(self, samples: List[Dict[str, Any]]) -> List[SampleVibe]:
        """Analyze multiple samples in a batch.
        
        Args:
            samples: List of sample data dictionaries
            
        Returns:
            List of SampleVibe objects
        """
        results = []
        
        # Process in batches of batch_size
        for i in range(0, len(samples), self.batch_size):
            batch = samples[i:i + self.batch_size]
            
            # Check cache for each sample
            uncached = []
            for sample in batch:
                cache_key = f"{sample['filename']}_{sample.get('bpm', 0)}_{sample.get('key', '')}"
                if cache_key in self._cache:
                    results.append(self._cache[cache_key])
                else:
                    uncached.append(sample)
            
            if uncached:
                # Apply rate limiting
                await self._apply_rate_limit()
                
                prompt = self.create_batch_prompt(uncached)
                
                try:
                    self.status = AgentStatus.RUNNING
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            self.api_url,
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": self.model,
                                "messages": [
                                    {"role": "system", "content": "You are a musical vibe analyst. Analyze samples and return JSON array only."},
                                    {"role": "user", "content": prompt}
                                ],
                                "temperature": 0.5,
                                "max_tokens": 2000
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            content = result['choices'][0]['message']['content']
                            batch_vibes = self.parse_batch_response(content, uncached)
                            
                            # Cache results
                            for vibe in batch_vibes:
                                cache_key = f"{vibe.filename}_{vibe.bpm}_{vibe.key}"
                                self._cache[cache_key] = vibe
                            
                            results.extend(batch_vibes)
                            self.status = AgentStatus.IDLE
                        else:
                            raise Exception(f"API error: {response.status_code}")
                            
                except Exception as e:
                    self.logger.error(f"Error in batch analysis: {str(e)}")
                    self.status = AgentStatus.FAILED
                    raise
        
        return results
    
    def create_single_prompt(self, sample_data: Dict[str, Any]) -> str:
        """Create prompt for single sample analysis with thinking protocol."""
        return f"""
        Analyze this audio sample for vibe and mood using the 5-step thinking protocol.

        SAMPLE DATA:
        Filename: {sample_data['filename']}
        BPM: {sample_data.get('bpm', 'unknown')}
        Key: {sample_data.get('key', 'unknown')}
        Spectral Centroid: {sample_data.get('spectral_centroid', 'unknown')}

        THINKING PROTOCOL - Work through each step:

        STEP 1: Analyze Musical Characteristics
        - What does the BPM suggest about energy level and use case?
        - What does the key signature tell us about emotional quality?
        - What does the spectral centroid indicate about tonal character?
        - What instrumentation can be inferred?

        STEP 2: Consider Era and Production Context
        - What era does this BPM/spectrum combination suggest?
        - What production techniques were common in that period?
        - What genre movements align with these characteristics?

        STEP 3: Identify Mood and Emotional Qualities
        - Energy level (low/medium/high) based on BPM and character
        - Emotional valence (dark/neutral/bright) from key and texture
        - Overall mood synthesis from all factors

        STEP 4: Determine Best Use Case
        - How should a producer use this sample?
        - Foundation/drums, bass, melody, harmony, texture, or transition?

        STEP 5: Identify Compatibility
        - What BPM range works with this?
        - What keys are compatible?
        - What other samples complement this?

        EXAMPLE REASONING:
        "The BPM of 90 suggests mid-tempo, typical of boom bap (85-100 BPM range).
        The warm spectral centroid (1200 Hz) indicates analog character.
        Combined with D minor key, this creates a reflective, grounded mood.
        Best used as drum foundation for boom bap/lo-fi production."

        After working through all steps, return ONLY a JSON object:
        {{
          "mood": ["descriptor1", "descriptor2", "descriptor3"],
          "era": "time_period",
          "genre": "primary_genre",
          "energy_level": "low|medium|high",
          "descriptors": ["adj1", "adj2", "adj3", "adj4", "adj5"],
          "compatibility_tags": ["tag1", "tag2", "tag3"],
          "best_use": "use_case"
        }}
        """
    
    def create_batch_prompt(self, samples: List[Dict[str, Any]]) -> str:
        """Create prompt for batch analysis with thinking protocol."""
        prompt = """Analyze these audio samples using the thinking protocol:

1. Analyze musical characteristics (BPM → energy, key → mood, spectrum → tone)
2. Consider era and production context
3. Identify mood and emotional qualities
4. Determine best use case
5. Identify compatibility factors

SAMPLES:\n\n"""

        for i, sample in enumerate(samples):
            prompt += f"""Sample {i+1}:
- Filename: {sample['filename']}
- BPM: {sample.get('bpm', 'unknown')}
- Key: {sample.get('key', 'unknown')}
- Spectral Centroid: {sample.get('spectral_centroid', 'unknown')}

"""

        prompt += """
For each sample, think through the analysis, then return JSON array with:
- filename: the filename
- mood: array of 3 specific mood descriptors (not generic like "good")
- era: time period (e.g., "1970s", "modern")
- genre: musical genre
- energy_level: "low", "medium", or "high"
- descriptors: array of 3-5 specific terms (texture, style, character)
- compatibility_tags: array of tags for finding compatible samples
- best_use: suggested use (drum foundation, bass foundation, melodic layer, texture, etc.)

Return as JSON array ONLY (no markdown, no explanations).
"""

        return prompt
    
    def parse_vibe_response(self, response: str, filename: str, bpm: float, key: str) -> SampleVibe:
        """Parse AI response into SampleVibe object."""
        try:
            # Clean response (remove markdown if present)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            data = json.loads(response)
            
            # Validate required fields
            required = ["mood", "era", "genre"]
            for field in required:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            vibe = VibeDescriptor(
                mood=data.get("mood", []),
                era=data.get("era", "unknown"),
                genre=data.get("genre", "unknown"),
                energy_level=data.get("energy_level", "medium"),
                descriptors=data.get("descriptors", [])
            )
            
            return SampleVibe(
                filename=filename,
                bpm=bpm,
                key=key,
                vibe=vibe,
                compatibility_tags=data.get("compatibility_tags", []),
                best_use=data.get("best_use", "unknown"),
                confidence=0.8
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing vibe response: {str(e)}")
            raise
    
    def parse_batch_response(self, response: str, samples: List[Dict[str, Any]]) -> List[SampleVibe]:
        """Parse batch AI response into list of SampleVibe objects."""
        try:
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            data = json.loads(response)
            
            if not isinstance(data, list):
                data = [data]  # Convert single object to list
            
            results = []
            for i, item in enumerate(data):
                if i < len(samples):
                    sample = samples[i]
                    vibe = VibeDescriptor(
                        mood=item.get("mood", []),
                        era=item.get("era", "unknown"),
                        genre=item.get("genre", "unknown"),
                        energy_level=item.get("energy_level", "medium"),
                        descriptors=item.get("descriptors", [])
                    )
                    
                    results.append(SampleVibe(
                        filename=item.get("filename", sample['filename']),
                        bpm=sample.get('bpm', 0),
                        key=sample.get('key', ''),
                        vibe=vibe,
                        compatibility_tags=item.get("compatibility_tags", []),
                        best_use=item.get("best_use", "unknown"),
                        confidence=0.8
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error parsing batch response: {str(e)}")
            raise
    
    def calculate_compatibility(self, vibe1: VibeDescriptor, vibe2: VibeDescriptor) -> float:
        """Calculate compatibility score between two vibes (0-1)."""
        score = 0.0
        
        # Era match (20%)
        if vibe1.era == vibe2.era:
            score += 0.2
        
        # Genre similarity (20%)
        if vibe1.genre == vibe2.genre:
            score += 0.2
        elif any(g in vibe2.genre for g in vibe1.genre.split('-')):
            score += 0.1
        
        # Energy level match (20%)
        if vibe1.energy_level == vibe2.energy_level:
            score += 0.2
        elif abs(['low', 'medium', 'high'].index(vibe1.energy_level) - 
                ['low', 'medium', 'high'].index(vibe2.energy_level)) == 1:
            score += 0.1
        
        # Mood overlap (30%)
        mood_overlap = len(set(vibe1.mood) & set(vibe2.mood))
        score += (mood_overlap / max(len(vibe1.mood), 1)) * 0.3
        
        # Descriptor overlap (10%)
        desc_overlap = len(set(vibe1.descriptors) & set(vibe2.descriptors))
        score += (desc_overlap / max(len(vibe1.descriptors), 1)) * 0.1
        
        return min(score, 1.0)
    
    async def find_complementary(self, target: SampleVibe, samples: List[SampleVibe]) -> List[SampleVibe]:
        """Find samples that complement the target sample."""
        complementary = []
        
        for sample in samples:
            if sample.filename != target.filename:
                # Calculate compatibility
                score = self.calculate_compatibility(target.vibe, sample.vibe)
                
                # Check for complementary characteristics
                # Same BPM or harmonically related
                bpm_compatible = abs(sample.bpm - target.bpm) < 5 or \
                                sample.bpm == target.bpm * 2 or \
                                sample.bpm == target.bpm / 2
                
                # Key compatibility (simplified)
                key_compatible = sample.key == target.key or \
                               sample.key in self._get_compatible_keys(target.key)
                
                # Different but complementary uses
                use_compatible = sample.best_use != target.best_use
                
                # High compatibility score and at least one other match
                if score >= 0.4 and (bpm_compatible or key_compatible) and use_compatible:
                    complementary.append(sample)
        
        return complementary
    
    def _get_compatible_keys(self, key: str) -> List[str]:
        """Get harmonically compatible keys (simplified)."""
        # Very simplified key compatibility
        compatible = {
            "C": ["Am", "F", "G"],
            "Am": ["C", "Dm", "Em", "F"],
            "G": ["C", "D", "Em"],
            "D": ["G", "A", "Bm"],
            # Add more as needed
        }
        return compatible.get(key, [key])  # Return same key as compatible if not in dict
    
    async def _apply_rate_limit(self):
        """Apply rate limiting to respect API limits."""
        now = datetime.now()
        
        if self.last_request_time:
            # Calculate time since last request
            time_diff = (now - self.last_request_time).total_seconds()
            
            # If less than 12 seconds (5 requests per 60 seconds), wait
            if time_diff < 12:
                wait_time = 12 - time_diff
                self.logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.now()
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a vibe analysis task.
        
        Args:
            task: Dictionary with 'action' and 'data' keys
            
        Returns:
            Dictionary with results
        """
        action = task.get('action', 'analyze')
        
        if action == 'analyze':
            sample_data = task.get('data', {})
            result = await self.analyze_vibe(sample_data)
            return {"status": "success", "result": result.model_dump()}
        
        elif action == 'analyze_batch':
            samples = task.get('data', [])
            results = await self.analyze_batch(samples)
            return {
                "status": "success", 
                "results": [r.model_dump() for r in results]
            }
        
        elif action == 'find_complementary':
            target = task.get('target')
            samples = task.get('samples', [])
            if isinstance(target, dict):
                target = SampleVibe(**target)
            if samples and isinstance(samples[0], dict):
                samples = [SampleVibe(**s) for s in samples]
            
            results = await self.find_complementary(target, samples)
            return {
                "status": "success",
                "complementary": [r.model_dump() for r in results]
            }
        
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}