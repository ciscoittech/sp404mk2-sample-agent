"""
AI-Powered Kit Assembler Tool.

Uses OpenRouter AI to intelligently build sample kits from natural language prompts.
Analyzes user intent, searches database for matching samples, and assembles cohesive kits.
"""
import logging
from typing import List, Dict, Any, Optional
import json

from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sample import Sample
from app.services.openrouter_service import OpenRouterService, OpenRouterRequest
from app.services.usage_tracking_service import UsageTrackingService

logger = logging.getLogger(__name__)


class KitAssemblerTool:
    """
    AI-powered kit assembler that builds sample kits from natural language prompts.

    Uses OpenRouter AI to:
    - Parse user intent (genre, BPM, vibe, style)
    - Search database for matching samples
    - Assemble cohesive kits based on musical compatibility
    """

    def __init__(self):
        """Initialize kit assembler."""
        pass

    async def build_kit_from_prompt(
        self,
        db: AsyncSession,
        user_id: int,
        prompt: str,
        num_samples: int = 12,
    ) -> Dict[str, Any]:
        """
        Build a complete kit from a natural language prompt.

        Args:
            db: Database session
            user_id: User ID
            prompt: Natural language description (e.g., "lo-fi hip hop at 85 BPM")
            num_samples: Number of samples to include in kit (default 12)

        Returns:
            Dict containing:
                - samples: List of selected samples with pad assignments
                - analysis: AI analysis of the prompt
                - genre: Detected genre
                - bpm: Target BPM (if specified)
        """
        logger.info(f"Building kit from prompt: {prompt}")

        # Step 1: Use AI to analyze the prompt
        analysis = await self._analyze_prompt(prompt, db)

        # Step 2: Search database for matching samples
        samples = await self._find_matching_samples(
            db=db,
            user_id=user_id,
            analysis=analysis,
            limit=num_samples * 3,  # Get 3x more for better selection
        )

        # Step 3: Use AI to select best samples and assign to pads
        selected_samples = await self._select_and_assign_samples(
            db=db,
            samples=samples,
            analysis=analysis,
            num_samples=num_samples,
        )

        return {
            "samples": selected_samples,
            "analysis": analysis,
            "total_found": len(samples),
            "total_selected": len(selected_samples),
        }

    async def _analyze_prompt(self, prompt: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Use AI to analyze user prompt and extract musical intent.

        Returns dict with: genre, bpm, vibe, tags, etc.
        """
        # Create services
        from app.services.usage_tracking_service import UsageTrackingService
        usage_service = UsageTrackingService(db)
        ai_service = OpenRouterService(usage_service)

        system_prompt = """You are a music production AI assistant specializing in sample selection for the Roland SP-404MK2 sampler.

Analyze the user's prompt and extract musical intent. Return a JSON object with:
- genre: Main genre/style (e.g., "lo-fi hip hop", "boom bap", "trap")
- bpm: Target BPM or BPM range (if mentioned)
- vibe: Overall vibe/mood (e.g., "chill", "dark", "uplifting")
- tags: Array of relevant tags for sample searching
- sample_types: Types of samples needed (e.g., ["kick", "snare", "hats", "loops"])

Example:
User: "I want a chill lo-fi hip hop beat around 85 BPM"
Response: {
  "genre": "lo-fi hip hop",
  "bpm": 85,
  "bpm_range": [80, 90],
  "vibe": "chill",
  "tags": ["lo-fi", "chill", "jazz", "vinyl", "dusty"],
  "sample_types": ["kick", "snare", "hat", "loop", "sample"]
}

Only return valid JSON, no other text."""

        request = OpenRouterRequest(
            model="qwen/qwen-2.5-7b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )

        try:
            response = await ai_service.chat_completion(
                request=request,
                sample_id=None,  # No sample for analysis
                operation_type="kit_builder_analysis",
            )

            # Parse JSON response
            analysis = json.loads(response.content)
            logger.info(f"AI analysis: {analysis}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing prompt: {e}")
            # Fallback to simple keyword extraction
            return {
                "genre": "hip hop",
                "tags": prompt.lower().split(),
                "sample_types": ["kick", "snare", "hat"],
            }

    async def _find_matching_samples(
        self,
        db: AsyncSession,
        user_id: int,
        analysis: Dict[str, Any],
        limit: int = 50,
    ) -> List[Sample]:
        """
        Search database for samples matching the AI analysis.
        """
        query = select(Sample).where(Sample.user_id == user_id)

        # Filter by genre if available
        if genre := analysis.get("genre"):
            query = query.where(
                or_(
                    Sample.genre.ilike(f"%{genre}%"),
                    Sample.genre.is_(None),  # Include samples without genre
                )
            )

        # Filter by BPM range if available
        if bpm_range := analysis.get("bpm_range"):
            bpm_min, bpm_max = bpm_range
            query = query.where(
                or_(
                    and_(Sample.bpm >= bpm_min, Sample.bpm <= bpm_max),
                    Sample.bpm.is_(None),  # Include samples without BPM
                )
            )

        # Filter by tags if available (JSON array contains check)
        if tags := analysis.get("tags", []):
            tag_conditions = []
            for tag in tags[:5]:  # Limit to 5 tags
                tag_conditions.append(
                    func.json_extract(Sample.tags, '$').like(f'%"{tag}"%')
                )
            if tag_conditions:
                query = query.where(or_(*tag_conditions))

        # Order by relevance and created date
        query = query.order_by(Sample.created_at.desc()).limit(limit)

        result = await db.execute(query)
        samples = list(result.scalars().all())

        logger.info(f"Found {len(samples)} matching samples")
        return samples

    async def _select_and_assign_samples(
        self,
        db: AsyncSession,
        samples: List[Sample],
        analysis: Dict[str, Any],
        num_samples: int = 12,
    ) -> List[Dict[str, Any]]:
        """
        Use AI to select best samples from candidates and assign to pads.
        """
        # Create services
        from app.services.usage_tracking_service import UsageTrackingService
        usage_service = UsageTrackingService(db)
        ai_service = OpenRouterService(usage_service)

        # Prepare sample data for AI
        sample_data = []
        for i, sample in enumerate(samples[:50]):  # Limit to 50 for token efficiency
            sample_data.append({
                "id": sample.id,
                "title": sample.title,
                "bpm": sample.bpm,
                "genre": sample.genre,
                "duration": sample.duration,
                "tags": sample.tags or [],
            })

        system_prompt = f"""You are a music production AI assistant for the Roland SP-404MK2.

User wants: {analysis.get('genre', 'hip hop')} style, {analysis.get('vibe', 'balanced')} vibe

Select {num_samples} samples from the provided list that work well together musically.
Assign each to a specific pad number (1-16) based on SP-404 conventions:
- Pads 1-4: Loops and melodic samples (longer sounds)
- Pads 5-8: Cymbals and textures
- Pads 9-12: Percussion and accents
- Pads 13: Kick drum
- Pads 14: Snare/clap
- Pads 15: Closed hi-hat
- Pads 16: Open hi-hat

Return JSON array with objects containing:
- sample_id: ID from the list
- pad_number: Pad assignment (1-16)
- reason: Why this sample was selected

Only return valid JSON array, no other text."""

        request = OpenRouterRequest(
            model="qwen/qwen-2.5-7b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Available samples:\n{json.dumps(sample_data, indent=2)}"}
            ],
            temperature=0.5,
            max_tokens=1500,
        )

        try:
            response = await ai_service.chat_completion(
                request=request,
                sample_id=None,
                operation_type="kit_builder_selection",
            )

            # Parse JSON response
            selections = json.loads(response.content)
            logger.info(f"AI selected {len(selections)} samples")
            return selections[:num_samples]  # Ensure we don't exceed limit

        except Exception as e:
            logger.error(f"Error selecting samples: {e}")
            # Fallback to simple selection
            return [
                {
                    "sample_id": sample.id,
                    "pad_number": i + 1,
                    "reason": "Fallback selection"
                }
                for i, sample in enumerate(samples[:num_samples])
            ]
