"""
Hybrid Analysis Service.

Orchestrates audio feature extraction and AI vibe analysis based on user preferences.
Combines AudioFeaturesService, OpenRouterService, and PreferencesService to provide
comprehensive sample analysis with automatic cost tracking.
"""
import asyncio
import time
import logging
from pathlib import Path
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.models.sample import Sample
from app.models.vibe_analysis import VibeAnalysis
from app.services.audio_features_service import AudioFeaturesService
from app.services.openrouter_service import (
    OpenRouterService,
    OpenRouterRequest,
    OpenRouterError
)
from app.services.usage_tracking_service import UsageTrackingService
from app.services.preferences_service import PreferencesService
from app.schemas.hybrid_analysis import (
    HybridAnalysisResult,
    BatchAnalysisResult,
    AnalysisConfig,
    BatchAnalysisConfig
)
from app.models.audio_features import AudioFeatures, AudioError

logger = logging.getLogger(__name__)


class HybridAnalysisService:
    """
    Orchestrates hybrid analysis combining audio features and AI vibe interpretation.

    Workflow:
    1. Check user preferences (or apply force_analyze override)
    2. Get sample from database
    3. Extract audio features (if enabled)
    4. Generate AI vibe analysis (if enabled)
    5. Save results to database
    6. Return aggregated results

    Implements graceful degradation - returns partial results on errors.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize hybrid analysis service.

        Args:
            db: SQLAlchemy async database session
        """
        self.db = db
        self.audio_service = AudioFeaturesService()
        self.usage_service = UsageTrackingService(db)
        self.openrouter_service = OpenRouterService(self.usage_service)
        self.prefs_service = PreferencesService(db)

    async def analyze_sample(
        self,
        sample_id: int,
        force_analyze: bool = False,
        override_model: Optional[str] = None,
        config: Optional[AnalysisConfig] = None
    ) -> HybridAnalysisResult:
        """
        Perform hybrid analysis on a single sample.

        Workflow:
        1. Check preferences (or use force_analyze override)
        2. Get sample from database
        3. Extract audio features (if enabled)
        4. Generate AI vibe analysis (if enabled)
        5. Return aggregated results

        Implements graceful degradation - returns partial results on errors.

        Args:
            sample_id: Database ID of the sample to analyze
            force_analyze: Force both analyses regardless of preferences
            override_model: Override the AI model to use
            config: Optional analysis configuration

        Returns:
            HybridAnalysisResult with analysis data, costs, and timing

        Raises:
            ValueError: If sample not found in database
        """
        start_time = time.time()
        skipped_reasons = []
        total_cost = 0.0

        # Step 1: Check preferences
        preferences = await self.prefs_service.get_preferences()

        # Determine what to analyze
        if config:
            extract_features = (
                config.extract_audio_features
                if config.extract_audio_features is not None
                else preferences.auto_audio_features
            )
            perform_vibe = (
                config.perform_vibe_analysis
                if config.perform_vibe_analysis is not None
                else preferences.auto_vibe_analysis
            )
        elif force_analyze:
            extract_features = True
            perform_vibe = True
        else:
            extract_features = preferences.auto_audio_features
            perform_vibe = preferences.auto_vibe_analysis

        # Step 2: Get sample
        result = await self.db.execute(select(Sample).where(Sample.id == sample_id))
        sample = result.scalar_one_or_none()

        if not sample:
            raise ValueError(f"Sample with id {sample_id} not found")

        # Verify file exists
        file_path = Path(sample.file_path)
        if not file_path.exists():
            skipped_reasons.append(f"Audio file not found: {file_path}")
            extract_features = False
            perform_vibe = False  # Can't do vibe without file for context

        # Step 3: Extract audio features
        audio_features = None
        features_extracted = False

        if extract_features and file_path.exists():
            try:
                # Use analyze_file method (which runs in thread pool)
                audio_features = await self.audio_service.analyze_file(file_path)
                features_extracted = True

                # Update sample with extracted features
                if audio_features.bpm:
                    sample.bpm = audio_features.bpm
                    sample.bpm_confidence = audio_features.bpm_confidence
                if audio_features.key:
                    sample.musical_key = f"{audio_features.key} {audio_features.scale or ''}".strip()
                    sample.key_confidence = audio_features.key_confidence
                if audio_features.genre:
                    sample.genre = audio_features.genre
                    sample.genre_confidence = audio_features.genre_confidence

                # Save duration from audio features
                if audio_features.duration_seconds:
                    sample.duration = audio_features.duration_seconds

                # Save analysis metadata
                if audio_features.metadata:
                    sample.analysis_metadata = audio_features.metadata

                # Save to extra_metadata
                if not sample.extra_metadata:
                    sample.extra_metadata = {}
                sample.extra_metadata['audio_features'] = audio_features.to_dict()

                await self.db.commit()
                await self.db.refresh(sample)

            except AudioError as e:
                logger.warning(f"Audio feature extraction failed for sample {sample_id}: {e}")
                skipped_reasons.append(f"Audio feature extraction failed: {str(e.message)}")
            except Exception as e:
                logger.error(f"Unexpected error during audio feature extraction: {e}")
                skipped_reasons.append(f"Audio feature extraction failed: {str(e)}")
        elif not extract_features:
            skipped_reasons.append("Audio feature extraction disabled in preferences")

        # Step 4: AI Vibe Analysis
        vibe_analysis = None
        vibe_analyzed = False
        model_used = None

        if perform_vibe:
            try:
                # Build prompt
                prompt = self._build_vibe_prompt(sample, audio_features)

                # Determine model
                model = override_model or preferences.vibe_analysis_model
                model_used = model

                # Call OpenRouter
                openrouter_response = await self.openrouter_service.chat_completion(
                    OpenRouterRequest(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a music producer analyzing samples for vibe and emotional characteristics. Provide detailed, insightful analysis."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                )

                vibe_analysis = openrouter_response.content
                vibe_analyzed = True
                total_cost += openrouter_response.cost

                # Track usage with sample_id (OpenRouter already tracks, but without sample_id)
                # So we track again with sample_id for proper association
                await self.usage_service.track_api_call(
                    model=model,
                    operation="vibe_analysis",
                    input_tokens=openrouter_response.usage.prompt_tokens,
                    output_tokens=openrouter_response.usage.completion_tokens,
                    sample_id=sample.id,
                    extra_metadata={"request_id": openrouter_response.request_id} if openrouter_response.request_id else {}
                )

                # Save to database
                await self._save_vibe_analysis(
                    sample_id=sample.id,
                    vibe_content=vibe_analysis,
                    model=model,
                    cost=openrouter_response.cost,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )

            except OpenRouterError as e:
                logger.warning(f"Vibe analysis failed for sample {sample_id}: {e}")
                skipped_reasons.append(f"Vibe analysis failed: {str(e.message)}")
            except Exception as e:
                logger.error(f"Unexpected error during vibe analysis: {e}")
                skipped_reasons.append(f"Vibe analysis failed: {str(e)}")
        elif not perform_vibe:
            skipped_reasons.append("Vibe analysis disabled in preferences")

        # Step 5: Return results
        analysis_time = time.time() - start_time

        return HybridAnalysisResult(
            sample_id=sample_id,
            audio_features=audio_features,
            features_extracted=features_extracted,
            vibe_analysis=vibe_analysis,
            vibe_analyzed=vibe_analyzed,
            model_used=model_used,
            cost=total_cost,
            analysis_time_seconds=analysis_time,
            skipped_reasons=skipped_reasons
        )

    async def analyze_batch(
        self,
        sample_ids: List[int],
        config: Optional[BatchAnalysisConfig] = None
    ) -> BatchAnalysisResult:
        """
        Analyze multiple samples sequentially.

        Uses batch_processing_model from preferences unless overridden.

        Args:
            sample_ids: List of sample IDs to analyze
            config: Optional batch configuration

        Returns:
            BatchAnalysisResult with aggregated statistics
        """
        start_time = time.time()
        results = []
        successful = 0
        failed = 0
        total_cost = 0.0

        # Get preferences for batch model
        preferences = await self.prefs_service.get_preferences()
        batch_model = preferences.batch_processing_model

        # Process each sample
        for sample_id in sample_ids:
            try:
                # Use batch model unless overridden
                override_model = config.override_model if config else None
                model = override_model or batch_model

                # Create AnalysisConfig from BatchAnalysisConfig
                analysis_config = None
                if config:
                    analysis_config = AnalysisConfig(
                        force_analyze=config.force_analyze,
                        override_model=model,
                        extract_audio_features=config.extract_audio_features,
                        perform_vibe_analysis=config.perform_vibe_analysis,
                        max_cost_override=config.max_cost_override
                    )

                result = await self.analyze_sample(
                    sample_id=sample_id,
                    override_model=model,
                    config=analysis_config
                )

                results.append(result)
                successful += 1
                total_cost += result.cost

            except Exception as e:
                logger.error(f"Failed to analyze sample {sample_id}: {e}")
                failed += 1
                # Add failed result
                results.append(HybridAnalysisResult(
                    sample_id=sample_id,
                    audio_features=None,
                    features_extracted=False,
                    vibe_analysis=None,
                    vibe_analyzed=False,
                    model_used=None,
                    cost=0.0,
                    analysis_time_seconds=0.0,
                    skipped_reasons=[f"Error: {str(e)}"]
                ))

        total_time = time.time() - start_time

        return BatchAnalysisResult(
            total_samples=len(sample_ids),
            successful=successful,
            failed=failed,
            total_cost=total_cost,
            total_time_seconds=total_time,
            average_time_per_sample=total_time / len(sample_ids) if sample_ids else 0,
            results=results,
            skipped_reason=None
        )

    def _build_vibe_prompt(
        self,
        sample: Sample,
        audio_features: Optional[AudioFeatures]
    ) -> str:
        """
        Build a prompt for vibe analysis including available metadata.

        Args:
            sample: Sample database model
            audio_features: Optional audio features from extraction

        Returns:
            Formatted prompt string for AI analysis
        """
        prompt_parts = [
            f"Analyze the vibe and characteristics of this audio sample:",
            f"Title: {sample.title}",
        ]

        if audio_features:
            prompt_parts.append(f"BPM: {audio_features.bpm}")
            prompt_parts.append(f"Key: {audio_features.key} {audio_features.scale or ''}")
            prompt_parts.append(f"Duration: {audio_features.duration_seconds:.2f}s")

        if sample.genre:
            prompt_parts.append(f"Genre: {sample.genre}")

        prompt_parts.append(
            "\nDescribe the emotional quality, texture, and best use cases for this sample."
        )

        return "\n".join(prompt_parts)

    async def _save_vibe_analysis(
        self,
        sample_id: int,
        vibe_content: str,
        model: str,
        cost: float,
        processing_time_ms: int
    ) -> None:
        """
        Save vibe analysis to database.

        Creates or updates VibeAnalysis record with parsed AI response.
        Uses simple text parsing to extract structured data.

        Args:
            sample_id: Sample database ID
            vibe_content: AI-generated vibe analysis text
            model: Model used for generation
            cost: Cost of the analysis
            processing_time_ms: Processing time in milliseconds
        """
        try:
            # Check if analysis already exists
            stmt = select(VibeAnalysis).where(VibeAnalysis.sample_id == sample_id)
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            # Parse vibe content for structured data (simple heuristics)
            mood_primary = self._extract_primary_mood(vibe_content)
            energy_level = self._extract_energy_level(vibe_content)

            if existing:
                # Update existing record
                existing.mood_primary = mood_primary
                existing.energy_level = energy_level
                existing.model_version = model
                existing.confidence_score = 0.8  # Default confidence
                existing.processing_time_ms = processing_time_ms
            else:
                # Create new record
                vibe_analysis = VibeAnalysis(
                    sample_id=sample_id,
                    mood_primary=mood_primary,
                    mood_secondary=None,
                    energy_level=energy_level,
                    danceability=None,
                    acousticness=None,
                    instrumentalness=None,
                    texture_tags=[],
                    characteristics={"raw_analysis": vibe_content},
                    model_version=model,
                    confidence_score=0.8,
                    processing_time_ms=processing_time_ms
                )
                self.db.add(vibe_analysis)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to save vibe analysis: {e}")
            await self.db.rollback()
            # Don't raise - this is a non-critical failure

    def _extract_primary_mood(self, vibe_content: str) -> str:
        """
        Extract primary mood from vibe analysis content.

        Uses simple keyword matching. Defaults to 'neutral' if no mood found.

        Args:
            vibe_content: AI-generated vibe analysis text

        Returns:
            Primary mood string
        """
        content_lower = vibe_content.lower()

        moods = [
            "energetic", "melancholic", "aggressive", "chill", "mysterious",
            "uplifting", "dark", "bright", "calm", "intense", "playful",
            "serious", "nostalgic", "futuristic"
        ]

        for mood in moods:
            if mood in content_lower:
                return mood

        return "neutral"

    def _extract_energy_level(self, vibe_content: str) -> float:
        """
        Extract energy level from vibe analysis content.

        Uses keyword matching to estimate energy on 0-1 scale.

        Args:
            vibe_content: AI-generated vibe analysis text

        Returns:
            Energy level float between 0.0 and 1.0
        """
        content_lower = vibe_content.lower()

        # High energy keywords
        if any(word in content_lower for word in ["high energy", "intense", "aggressive", "powerful"]):
            return 0.8

        # Medium-high energy
        if any(word in content_lower for word in ["energetic", "upbeat", "lively"]):
            return 0.7

        # Medium energy
        if any(word in content_lower for word in ["moderate", "balanced"]):
            return 0.5

        # Low energy
        if any(word in content_lower for word in ["calm", "chill", "relaxed", "mellow"]):
            return 0.3

        # Very low energy
        if any(word in content_lower for word in ["ambient", "peaceful", "gentle"]):
            return 0.2

        # Default to medium
        return 0.5
