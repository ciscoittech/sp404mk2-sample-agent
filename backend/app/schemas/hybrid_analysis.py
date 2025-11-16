"""
Schemas for hybrid analysis results.

Defines response models for the HybridAnalysisService that orchestrates
AudioFeaturesService, OpenRouterService, and PreferencesService.
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.audio_features import AudioFeatures


class HybridAnalysisResult(BaseModel):
    """
    Result from analyzing a single sample with hybrid analysis.

    Combines audio features extraction and AI vibe analysis based on
    user preferences. Includes graceful degradation and skipped step tracking.
    """

    # Sample identification
    sample_id: int = Field(..., description="Database ID of analyzed sample")

    # Audio features (if extracted)
    audio_features: Optional[AudioFeatures] = Field(
        None,
        description="Extracted audio features (None if skipped or failed)"
    )
    features_extracted: bool = Field(
        ...,
        description="Whether audio features were successfully extracted"
    )

    # Vibe analysis (if performed)
    vibe_analysis: Optional[str] = Field(
        None,
        description="AI-generated vibe analysis content (None if skipped or failed)"
    )
    vibe_analyzed: bool = Field(
        ...,
        description="Whether vibe analysis was successfully performed"
    )
    model_used: Optional[str] = Field(
        None,
        description="AI model used for vibe analysis (None if skipped)"
    )

    # Cost and performance
    cost: float = Field(
        default=0.0,
        description="Total cost of analysis in USD (0.0 if no AI calls)"
    )
    analysis_time_seconds: float = Field(
        ...,
        description="Total time taken for analysis"
    )

    # Execution tracking
    skipped_reasons: List[str] = Field(
        default_factory=list,
        description="List of reasons why steps were skipped (e.g., 'Audio features disabled in preferences')"
    )

    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True  # Allow AudioFeatures with Path


class BatchAnalysisConfig(BaseModel):
    """
    Configuration for batch analysis operations.

    Allows overriding default preferences for batch processing.
    """

    force_analyze: bool = Field(
        default=False,
        description="Force analysis even if preferences disable it"
    )
    override_model: Optional[str] = Field(
        None,
        description="Override model to use instead of preference setting"
    )
    extract_audio_features: Optional[bool] = Field(
        None,
        description="Override audio features extraction setting (None = use preferences)"
    )
    perform_vibe_analysis: Optional[bool] = Field(
        None,
        description="Override vibe analysis setting (None = use preferences)"
    )
    max_cost_override: Optional[float] = Field(
        None,
        description="Override max cost per request (None = use preferences)"
    )


class BatchAnalysisResult(BaseModel):
    """
    Result from analyzing multiple samples in a batch.

    Aggregates statistics and results from processing multiple samples
    sequentially with the hybrid analysis workflow.
    """

    # Summary statistics
    total_samples: int = Field(..., description="Total number of samples in batch")
    successful: int = Field(..., description="Number of samples successfully analyzed")
    failed: int = Field(..., description="Number of samples that failed analysis")

    # Cost and performance aggregates
    total_cost: float = Field(..., description="Total cost of all analyses in USD")
    total_time_seconds: float = Field(..., description="Total time for batch processing")
    average_time_per_sample: float = Field(..., description="Average time per sample in seconds")

    # Individual results
    results: List[HybridAnalysisResult] = Field(
        ...,
        description="Individual analysis results for each sample"
    )

    # Batch-level tracking
    skipped_reason: Optional[str] = Field(
        None,
        description="Reason entire batch was skipped (None if processed)"
    )


class AnalysisConfig(BaseModel):
    """
    Configuration for single sample analysis.

    Allows fine-grained control over the analysis workflow.
    """

    force_analyze: bool = Field(
        default=False,
        description="Force analysis regardless of preferences"
    )
    override_model: Optional[str] = Field(
        None,
        description="Override AI model to use"
    )
    extract_audio_features: Optional[bool] = Field(
        None,
        description="Override audio features setting"
    )
    perform_vibe_analysis: Optional[bool] = Field(
        None,
        description="Override vibe analysis setting"
    )
    max_cost_override: Optional[float] = Field(
        None,
        description="Override max cost limit"
    )
    save_to_database: bool = Field(
        default=True,
        description="Whether to save results to database"
    )
