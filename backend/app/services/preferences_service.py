"""
PreferencesService for managing user preferences.

Handles CRUD operations for system-wide user preferences using a single-row
design (id=1). Provides helper methods for accessing specific preference values.
"""
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preferences import UserPreference
from app.schemas.preferences import (
    UserPreferenceResponse,
    UserPreferenceUpdate,
    AvailableModelsResponse,
    ModelMetadata
)

logger = logging.getLogger(__name__)


class PreferencesService:
    """
    Service for managing user preferences.

    Uses single-row design (id=1) for system-wide settings.
    Automatically creates default preferences on first access.
    """

    # Available models with pricing and metadata
    AVAILABLE_MODELS = {
        "qwen/qwen3-7b-it": {
            "name": "Qwen 7B (Fast)",
            "input_cost": 0.10 / 1_000_000,
            "output_cost": 0.10 / 1_000_000,
            "description": "Fast and cost-effective model for quick vibe analysis. Great for batch processing and real-time feedback."
        },
        "qwen/qwen3-235b-a22b-2507": {
            "name": "Qwen 235B (Deep)",
            "input_cost": 0.80 / 1_000_000,
            "output_cost": 0.80 / 1_000_000,
            "description": "Powerful model for deep analysis with rich musical understanding. Best for detailed vibe analysis and complex audio interpretation."
        }
    }

    def __init__(self, db_session: AsyncSession):
        """
        Initialize preferences service.

        Args:
            db_session: SQLAlchemy async database session
        """
        self.db = db_session

    async def get_preferences(self) -> UserPreferenceResponse:
        """
        Get user preferences (creates defaults if none exist).

        Uses single-row design with id=1. If preferences don't exist,
        creates them with default values automatically.

        Returns:
            UserPreferenceResponse with current preferences

        Raises:
            Exception: If database operation fails
        """
        try:
            # Query for preferences (id=1)
            stmt = select(UserPreference).where(UserPreference.id == 1)
            result = await self.db.execute(stmt)
            prefs = result.scalar_one_or_none()

            # Create defaults if none exist
            if prefs is None:
                logger.info("No preferences found, creating defaults")
                prefs = await self._create_defaults()

            return UserPreferenceResponse.model_validate(prefs)

        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            raise

    async def update_preferences(self, update: UserPreferenceUpdate) -> UserPreferenceResponse:
        """
        Update preferences with partial data.

        Only updates fields that are provided (not None). Uses the
        exclude_unset option to handle partial updates correctly.

        Args:
            update: UserPreferenceUpdate with fields to change

        Returns:
            UserPreferenceResponse with updated preferences

        Raises:
            Exception: If database operation fails
        """
        try:
            # Get existing preferences (creates if needed)
            stmt = select(UserPreference).where(UserPreference.id == 1)
            result = await self.db.execute(stmt)
            prefs = result.scalar_one_or_none()

            if prefs is None:
                logger.info("Creating preferences for update")
                prefs = await self._create_defaults()

            # Update only provided fields
            update_data = update.model_dump(exclude_unset=True)
            if update_data:
                logger.info(f"Updating preferences: {list(update_data.keys())}")
                for field, value in update_data.items():
                    setattr(prefs, field, value)

                # Explicitly update the updated_at timestamp
                # SQLite doesn't handle onupdate properly, PostgreSQL does, but manual update works for both
                from datetime import datetime, timezone
                prefs.updated_at = datetime.now(timezone.utc)

                await self.db.commit()
                await self.db.refresh(prefs)
                logger.info("Preferences updated successfully")
            else:
                logger.info("No fields to update")

            return UserPreferenceResponse.model_validate(prefs)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating preferences: {e}")
            raise

    async def get_vibe_model(self) -> str:
        """
        Get the preferred vibe analysis model.

        Returns:
            Model identifier string (e.g., 'qwen/qwen3-7b-it')

        Raises:
            Exception: If database operation fails
        """
        prefs = await self.get_preferences()
        return prefs.vibe_analysis_model

    async def get_batch_model(self) -> str:
        """
        Get the preferred batch processing model.

        Returns:
            Model identifier string (e.g., 'qwen/qwen3-7b-it')

        Raises:
            Exception: If database operation fails
        """
        prefs = await self.get_preferences()
        return prefs.batch_processing_model

    async def should_auto_analyze(self, is_batch: bool = False) -> bool:
        """
        Check if auto-analysis should be performed.

        Args:
            is_batch: True for batch operations, False for single samples

        Returns:
            True if auto-analysis is enabled for the operation type

        Raises:
            Exception: If database operation fails
        """
        prefs = await self.get_preferences()
        if is_batch:
            return prefs.batch_auto_analyze
        return prefs.auto_vibe_analysis

    async def should_extract_features(self) -> bool:
        """
        Check if audio features should be automatically extracted.

        Returns:
            True if auto feature extraction is enabled

        Raises:
            Exception: If database operation fails
        """
        prefs = await self.get_preferences()
        return prefs.auto_audio_features

    async def get_cost_limit(self) -> Optional[float]:
        """
        Get the maximum cost per request limit.

        Returns:
            Maximum cost in USD, or None if no limit is set

        Raises:
            Exception: If database operation fails
        """
        prefs = await self.get_preferences()
        return prefs.max_cost_per_request

    @staticmethod
    async def get_available_models() -> AvailableModelsResponse:
        """
        Get list of available models with pricing metadata.

        This is a static method that doesn't require database access.
        Returns hardcoded model information for the UI to display.

        Returns:
            AvailableModelsResponse with model list and pricing

        Note:
            Static method - no database connection required
        """
        models = []
        for model_id, metadata in PreferencesService.AVAILABLE_MODELS.items():
            models.append(ModelMetadata(
                model_id=model_id,
                name=metadata["name"],
                input_cost=metadata["input_cost"],
                output_cost=metadata["output_cost"],
                description=metadata["description"]
            ))

        return AvailableModelsResponse(models=models)

    async def _create_defaults(self) -> UserPreference:
        """
        Create default preferences (internal helper).

        Creates a new UserPreference row with id=1 and default values.
        Commits to database and returns the created object.

        Returns:
            UserPreference with default values

        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info("Creating default preferences with id=1")
            prefs = UserPreference(
                id=1,
                vibe_analysis_model="qwen/qwen3-7b-it",
                auto_vibe_analysis=True,
                auto_audio_features=True,
                batch_processing_model="qwen/qwen3-7b-it",
                batch_auto_analyze=False,
                max_cost_per_request=None
            )
            self.db.add(prefs)
            await self.db.commit()
            await self.db.refresh(prefs)
            logger.info("Default preferences created successfully")
            return prefs

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating default preferences: {e}")
            raise
