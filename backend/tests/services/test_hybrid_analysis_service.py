"""
TDD RED Phase Tests for HybridAnalysisService

These tests define the expected behavior of the Hybrid Analysis Service before implementation.
Following Test-Driven Development (TDD) RED-GREEN-REFACTOR methodology.

Test Strategy:
- 13 MVP-level tests (10 service unit tests + 3 integration tests)
- REAL integration: Uses actual AudioFeaturesService, OpenRouterService, PreferencesService
- Real database session for full integration testing
- Real audio files from test fixtures
- No mocks - tests complete workflow orchestration

The HybridAnalysisService orchestrates:
1. PreferencesService - User settings for analysis behavior
2. AudioFeaturesService - Librosa-based audio feature extraction
3. OpenRouterService - AI vibe analysis with cost tracking
4. Sample database - Persistent storage of analysis results

Expected Failures:
- ImportError: HybridAnalysisService module doesn't exist yet
- AttributeError: Methods and models not implemented
- All tests should fail until implementation is complete
"""
import pytest
import pytest_asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import time


# =============================================================================
# SERVICE UNIT TESTS (10 tests)
# =============================================================================


@pytest.mark.asyncio
async def test_analyze_sample_full_workflow(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 1: Analyze sample with both features enabled (full workflow).

    Validates:
    - Service orchestrates all 3 services correctly
    - Both audio features and vibe analysis are performed
    - Results include data from both analyses
    - Cost is calculated and tracked
    - No steps are skipped
    - Timing information is captured

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models (will fail until implemented)
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Set preferences to enable both features
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=True,
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create sample in database with real audio file
    sample = Sample(
        id=1,
        user_id=test_user.id,
        title="Test Full Workflow Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze with hybrid service
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample.id)

    # Assert: Verify both services ran successfully
    assert result.sample_id == sample.id, "Sample ID must match"
    assert result.features_extracted is True, "Audio features should be extracted"
    assert result.vibe_analyzed is True, "Vibe analysis should be performed"

    # Verify audio features were extracted
    assert result.audio_features is not None, "Audio features must be present"
    assert result.audio_features.duration_seconds is not None, "Duration must be extracted"
    assert result.audio_features.sample_rate is not None, "Sample rate must be extracted"

    # Verify vibe analysis was performed
    assert result.vibe_analysis is not None, "Vibe analysis content must be present"
    assert len(result.vibe_analysis) > 0, "Vibe analysis should not be empty"
    assert result.model_used == "qwen/qwen3-7b-it", "Model used should match preference"

    # Verify cost tracking
    assert result.cost > 0, "Cost should be greater than zero for AI call"

    # Verify timing
    assert result.analysis_time_seconds > 0, "Analysis time must be positive"

    # Verify no steps were skipped
    assert len(result.skipped_reasons) == 0, "No steps should be skipped in full workflow"


@pytest.mark.asyncio
async def test_analyze_sample_audio_only(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 2: Analyze sample with only audio features enabled.

    Validates:
    - Audio features are extracted
    - Vibe analysis is skipped
    - Cost is zero (no AI calls)
    - Skipped reasons include vibe analysis disabled
    - Graceful partial execution

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Enable only audio features
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=False,  # Disable vibe analysis
        auto_audio_features=True,   # Enable audio features
    ))

    # Create sample
    sample = Sample(
        id=2,
        user_id=test_user.id,
        title="Test Audio Only Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample.id)

    # Assert: Audio features extracted, vibe analysis skipped
    assert result.features_extracted is True, "Audio features should be extracted"
    assert result.vibe_analyzed is False, "Vibe analysis should be skipped"

    assert result.audio_features is not None, "Audio features must be present"
    assert result.vibe_analysis is None, "Vibe analysis should be None"
    assert result.model_used is None, "No model should be used"

    # Verify no cost (no AI calls)
    assert result.cost == 0.0, "Cost should be zero when no AI calls made"

    # Verify skip reason is documented
    assert len(result.skipped_reasons) > 0, "Should have skip reasons"
    assert any("vibe" in reason.lower() for reason in result.skipped_reasons), \
        "Skip reasons should mention vibe analysis"


@pytest.mark.asyncio
async def test_analyze_sample_vibe_only(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 3: Analyze sample with only vibe analysis enabled.

    Validates:
    - Audio features are skipped
    - Vibe analysis is performed (without audio features in prompt)
    - Cost is tracked
    - Skipped reasons include audio features disabled
    - AI can still provide basic vibe analysis

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Enable only vibe analysis
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,    # Enable vibe analysis
        auto_audio_features=False,  # Disable audio features
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create sample
    sample = Sample(
        id=3,
        user_id=test_user.id,
        title="Test Vibe Only Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample.id)

    # Assert: Vibe analysis performed, audio features skipped
    assert result.features_extracted is False, "Audio features should be skipped"
    assert result.vibe_analyzed is True, "Vibe analysis should be performed"

    assert result.audio_features is None, "Audio features should be None"
    assert result.vibe_analysis is not None, "Vibe analysis must be present"
    assert result.model_used == "qwen/qwen3-7b-it", "Model should match preference"

    # Verify cost is tracked
    assert result.cost > 0, "Cost should be greater than zero for AI call"

    # Verify skip reason for audio features
    assert len(result.skipped_reasons) > 0, "Should have skip reasons"
    assert any("audio" in reason.lower() or "feature" in reason.lower()
               for reason in result.skipped_reasons), \
        "Skip reasons should mention audio features"


@pytest.mark.asyncio
async def test_analyze_sample_both_disabled(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 4: Analyze sample with both features disabled.

    Validates:
    - Both audio features and vibe analysis are skipped
    - Service still returns valid result with metadata
    - Cost is zero
    - Both skip reasons are documented
    - Quick execution (no processing)

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Disable both features
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=False,   # Disable vibe
        auto_audio_features=False,  # Disable audio
    ))

    # Create sample
    sample = Sample(
        id=4,
        user_id=test_user.id,
        title="Test Both Disabled Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample.id)

    # Assert: Both features skipped
    assert result.features_extracted is False, "Audio features should be skipped"
    assert result.vibe_analyzed is False, "Vibe analysis should be skipped"

    assert result.audio_features is None, "Audio features should be None"
    assert result.vibe_analysis is None, "Vibe analysis should be None"
    assert result.model_used is None, "No model should be used"

    # Verify no cost
    assert result.cost == 0.0, "Cost should be zero with no processing"

    # Verify skip reasons for both
    assert len(result.skipped_reasons) >= 2, "Should have skip reasons for both features"

    # Verify quick execution
    assert result.analysis_time_seconds < 1.0, "Should execute quickly with no processing"


@pytest.mark.asyncio
async def test_analyze_sample_force_override(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 5: Analyze sample with force_analyze=True override.

    Validates:
    - Preferences are overridden when force_analyze=True
    - Both features run despite being disabled in preferences
    - Override behavior is clearly indicated
    - All analysis is performed successfully
    - Cost is tracked despite preferences

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Disable BOTH features in preferences
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=False,   # Disabled
        auto_audio_features=False,  # Disabled
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create sample
    sample = Sample(
        id=5,
        user_id=test_user.id,
        title="Test Force Override Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze with force_analyze=True
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample.id, force_analyze=True)

    # Assert: Both services ran DESPITE preferences being disabled
    assert result.features_extracted is True, "Audio features should be forced"
    assert result.vibe_analyzed is True, "Vibe analysis should be forced"

    assert result.audio_features is not None, "Audio features must be present"
    assert result.vibe_analysis is not None, "Vibe analysis must be present"

    # Verify cost is tracked
    assert result.cost > 0, "Cost should be tracked for forced analysis"

    # Skip reasons should be empty or indicate forced analysis
    # (Implementation detail: may have "Forced analysis" or be empty)
    if len(result.skipped_reasons) > 0:
        assert any("force" in reason.lower() for reason in result.skipped_reasons), \
            "If skip reasons present, should mention forced analysis"


@pytest.mark.asyncio
async def test_analyze_sample_override_model(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 6: Analyze sample with override_model parameter.

    Validates:
    - Model override works regardless of preferences
    - Specified model is used instead of preference model
    - Cost calculation uses correct model pricing
    - Override is reflected in result.model_used

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Set default model to 7B
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=False,  # Skip to focus on model override
        vibe_analysis_model="qwen/qwen3-7b-it"  # Default
    ))

    # Create sample
    sample = Sample(
        id=6,
        user_id=test_user.id,
        title="Test Model Override Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze with override_model to 235B
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(
        sample_id=sample.id,
        override_model="qwen/qwen3-235b-a22b-2507"  # Override to larger model
    )

    # Assert: Override model was used
    assert result.vibe_analyzed is True, "Vibe analysis should be performed"
    assert result.model_used == "qwen/qwen3-235b-a22b-2507", \
        "Override model should be used instead of preference"

    # Verify cost reflects the more expensive 235B model
    assert result.cost > 0, "Cost should be calculated"
    # Note: Cost should be higher than 7B model, but we can't test exact values
    # since they depend on token counts


@pytest.mark.asyncio
async def test_analyze_sample_missing_sample(db_session: AsyncSession):
    """
    Test 7: Analyze sample with non-existent sample ID.

    Validates:
    - Service handles missing samples gracefully
    - Appropriate error is raised
    - Error message is descriptive
    - Database consistency is maintained

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService

    # Act & Assert: Attempt to analyze non-existent sample
    service = HybridAnalysisService(db_session)

    with pytest.raises(Exception) as exc_info:
        await service.analyze_sample(sample_id=999999)

    # Verify error is descriptive
    error_message = str(exc_info.value).lower()
    assert "not found" in error_message or "does not exist" in error_message, \
        "Error should indicate sample not found"


@pytest.mark.asyncio
async def test_analyze_sample_missing_audio_file(
    db_session: AsyncSession,
    test_user
):
    """
    Test 8: Analyze sample where audio file doesn't exist on disk.

    Validates:
    - Audio features extraction fails gracefully
    - Vibe analysis can still proceed (if enabled)
    - Partial results are returned (metadata only or vibe only)
    - Error is logged but doesn't crash service
    - features_extracted=False indicates failure

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Enable both features
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=True,
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create sample with non-existent file path
    sample = Sample(
        id=7,
        user_id=test_user.id,
        title="Test Missing File Sample",
        file_path="/fake/path/that/does/not/exist.wav",
        file_size=12345,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Act: Analyze (should handle missing file gracefully)
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample.id)

    # Assert: Audio features failed, but service didn't crash
    assert result.features_extracted is False, \
        "Audio features should fail when file missing"
    assert result.audio_features is None, \
        "Audio features should be None"

    # Vibe analysis may or may not proceed depending on implementation
    # But the service should return a valid result either way
    assert result.sample_id == sample.id, "Sample ID should be correct"
    assert result.analysis_time_seconds >= 0, "Analysis time should be recorded"

    # Should have skip/error reason for audio features
    assert len(result.skipped_reasons) > 0, "Should document audio feature failure"


@pytest.mark.asyncio
async def test_analyze_batch_sequential_processing(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 9: Analyze batch with 3 samples (sequential processing).

    Validates:
    - Batch processing handles multiple samples
    - Sequential execution (one after another)
    - Aggregated statistics are correct
    - Individual results are included
    - Total cost and time are calculated
    - All samples processed successfully

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Enable both features
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=True,
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create 3 samples
    sample_ids = []
    for i in range(1, 4):
        sample = Sample(
            user_id=test_user.id,
            title=f"Batch Sample {i}",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size,
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    # Act: Analyze batch
    service = HybridAnalysisService(db_session)
    start_time = time.time()
    result = await service.analyze_batch(sample_ids=sample_ids)
    elapsed = time.time() - start_time

    # Assert: Batch results
    assert result.total_samples == 3, "Should process 3 samples"
    assert result.successful == 3, "All samples should succeed"
    assert result.failed == 0, "No samples should fail"

    # Verify individual results
    assert len(result.results) == 3, "Should have 3 individual results"
    for individual_result in result.results:
        assert individual_result.features_extracted is True, "Features should be extracted"
        assert individual_result.vibe_analyzed is True, "Vibe should be analyzed"

    # Verify aggregated statistics
    assert result.total_cost > 0, "Total cost should be calculated"
    assert result.total_time_seconds > 0, "Total time should be positive"
    assert result.total_time_seconds <= elapsed + 1.0, \
        "Reported time should be close to actual elapsed time"

    # Verify average calculation
    expected_avg = result.total_time_seconds / 3
    assert abs(result.average_time_per_sample - expected_avg) < 0.1, \
        "Average time should be total time / sample count"

    # Verify no batch-level skip
    assert result.skipped_reason is None, "Batch should not be skipped"


@pytest.mark.asyncio
async def test_analyze_batch_respects_preferences(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Test 10: Analyze batch respects batch processing preferences.

    Validates:
    - Batch uses batch_processing_model preference
    - Batch uses batch_auto_analyze preference
    - Batch behavior differs from single sample preferences
    - Model override applies to all samples in batch

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Arrange: Set different models for single vs batch
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        vibe_analysis_model="qwen/qwen3-7b-it",           # Single sample uses 7B
        batch_processing_model="qwen/qwen3-235b-a22b-2507",  # Batch uses 235B
        auto_vibe_analysis=True,
        auto_audio_features=True,
        batch_auto_analyze=True  # Enable batch auto-analysis
    ))

    # Create 2 samples
    sample_ids = []
    for i in range(1, 3):
        sample = Sample(
            user_id=test_user.id,
            title=f"Batch Prefs Sample {i}",
            file_path=str(test_wav_fixture),
            file_size=test_wav_fixture.stat().st_size,
        )
        db_session.add(sample)
        await db_session.flush()
        sample_ids.append(sample.id)

    await db_session.commit()

    # Act: Analyze batch
    service = HybridAnalysisService(db_session)
    result = await service.analyze_batch(sample_ids=sample_ids)

    # Assert: Batch used batch_processing_model
    assert result.successful == 2, "Both samples should succeed"

    for individual_result in result.results:
        assert individual_result.vibe_analyzed is True, "Vibe should be analyzed"
        assert individual_result.model_used == "qwen/qwen3-235b-a22b-2507", \
            "Batch should use batch_processing_model preference (235B not 7B)"


# =============================================================================
# INTEGRATION TESTS (3 tests)
# =============================================================================


@pytest.mark.asyncio
async def test_integration_complete_workflow(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Integration Test 1: Complete workflow from upload to analysis result in DB.

    Validates:
    - End-to-end sample creation and analysis
    - Database persistence of all results
    - Sample.extra_metadata stores audio features
    - VibeAnalysis record is created with AI results
    - Relationships between models work correctly
    - Query back from database returns complete data

    This is a REAL integration test using actual database and services.

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample
    from app.models.vibe_analysis import VibeAnalysis

    # Arrange: Enable full analysis
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=True,
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create sample (simulating upload)
    sample = Sample(
        user_id=test_user.id,
        title="Integration Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    sample_id = sample.id

    # Act: Trigger analysis
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample_id)

    # Commit and clear session to ensure data is persisted
    await db_session.commit()
    await db_session.close()

    # Query sample back from database
    stmt = select(Sample).where(Sample.id == sample_id)
    query_result = await db_session.execute(stmt)
    retrieved_sample = query_result.scalar_one()

    # Assert: Sample has audio features in extra_metadata
    assert retrieved_sample is not None, "Sample should be in database"
    assert "audio_features" in retrieved_sample.extra_metadata, \
        "Sample.extra_metadata should contain audio_features"

    features_dict = retrieved_sample.extra_metadata["audio_features"]
    assert features_dict["duration_seconds"] is not None, \
        "Audio features should include duration"
    assert features_dict["sample_rate"] is not None, \
        "Audio features should include sample rate"

    # Query vibe analysis from database
    vibe_stmt = select(VibeAnalysis).where(VibeAnalysis.sample_id == sample_id)
    vibe_result = await db_session.execute(vibe_stmt)
    vibe_record = vibe_result.scalar_one_or_none()

    # Assert: VibeAnalysis record exists
    assert vibe_record is not None, "VibeAnalysis record should be created"
    assert vibe_record.sample_id == sample_id, "VibeAnalysis should link to sample"
    assert vibe_record.mood_primary is not None, "Vibe analysis should have primary mood"
    assert vibe_record.model_version == "qwen/qwen3-7b-it", \
        "Model version should be recorded"


@pytest.mark.asyncio
async def test_integration_cost_tracking(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Integration Test 2: Cost tracking integration with UsageTrackingService.

    Validates:
    - OpenRouter costs are tracked in ApiUsage table
    - Cost matches HybridAnalysisResult.cost
    - Usage record includes sample_id reference
    - Token counts are recorded
    - Operation type is correct

    This tests integration between HybridAnalysisService and UsageTrackingService.

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample
    from app.models.api_usage import ApiUsage

    # Arrange: Enable vibe analysis (skip audio to focus on cost tracking)
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=False,
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    # Create sample
    sample = Sample(
        user_id=test_user.id,
        title="Cost Tracking Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    sample_id = sample.id

    # Act: Analyze (triggers OpenRouter API call with cost tracking)
    service = HybridAnalysisService(db_session)
    result = await service.analyze_sample(sample_id=sample_id)

    # Assert: Cost is tracked in result
    assert result.cost > 0, "Cost should be calculated"

    # Query ApiUsage table for this sample
    usage_stmt = select(ApiUsage).where(ApiUsage.sample_id == sample_id)
    usage_result = await db_session.execute(usage_stmt)
    usage_records = usage_result.scalars().all()

    # Assert: ApiUsage record exists
    assert len(usage_records) > 0, "At least one ApiUsage record should exist"

    # Find the vibe analysis usage record
    vibe_usage = None
    for record in usage_records:
        if "vibe" in record.operation.lower() or record.operation == "chat_completion":
            vibe_usage = record
            break

    assert vibe_usage is not None, "ApiUsage record for vibe analysis should exist"
    assert vibe_usage.sample_id == sample_id, "Usage should reference correct sample"
    assert vibe_usage.model == "qwen/qwen3-7b-it", "Model should match"
    assert vibe_usage.total_tokens > 0, "Token count should be recorded"
    assert vibe_usage.total_cost > 0, "Cost should be recorded"

    # Cost should match between result and database (within floating point tolerance)
    assert abs(vibe_usage.total_cost - result.cost) < 0.0001, \
        "Database cost should match result cost"


@pytest.mark.asyncio
async def test_integration_preferences_change_behavior(
    db_session: AsyncSession,
    test_user,
    test_wav_fixture
):
    """
    Integration Test 3: Changing preferences changes analysis behavior.

    Validates:
    - PreferencesService integration works correctly
    - Changing preferences affects subsequent analyses
    - Same sample analyzed twice with different settings produces different results
    - Service respects real-time preference changes

    This tests dynamic behavior based on preference state.

    Expected to fail until HybridAnalysisService is implemented.
    """
    # Import models
    from app.services.hybrid_analysis_service import HybridAnalysisService
    from app.services.preferences_service import PreferencesService
    from app.schemas.preferences import UserPreferenceUpdate
    from app.models.sample import Sample

    # Create sample once (reuse for both analyses)
    sample = Sample(
        user_id=test_user.id,
        title="Preferences Change Test Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    sample_id = sample.id

    # Test 1: Analyze with both features ENABLED
    prefs_service = PreferencesService(db_session)
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=True,
        vibe_analysis_model="qwen/qwen3-7b-it"
    ))

    service = HybridAnalysisService(db_session)
    result1 = await service.analyze_sample(sample_id=sample_id)

    # Assert: Both features ran
    assert result1.features_extracted is True, "First analysis should extract features"
    assert result1.vibe_analyzed is True, "First analysis should analyze vibe"
    assert result1.cost > 0, "First analysis should have cost"

    # Test 2: Change preferences to DISABLE both features
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=False,   # Disable
        auto_audio_features=False,  # Disable
    ))

    # Analyze same sample again with new preferences
    result2 = await service.analyze_sample(sample_id=sample_id)

    # Assert: Both features skipped this time
    assert result2.features_extracted is False, "Second analysis should skip features"
    assert result2.vibe_analyzed is False, "Second analysis should skip vibe"
    assert result2.cost == 0.0, "Second analysis should have no cost"
    assert len(result2.skipped_reasons) > 0, "Second analysis should document skips"

    # Test 3: Change preferences again to enable only vibe with different model
    await prefs_service.update_preferences(UserPreferenceUpdate(
        auto_vibe_analysis=True,
        auto_audio_features=False,
        vibe_analysis_model="qwen/qwen3-235b-a22b-2507"  # Different model
    ))

    # Analyze third time
    result3 = await service.analyze_sample(sample_id=sample_id)

    # Assert: Only vibe ran, with new model
    assert result3.features_extracted is False, "Third analysis should skip features"
    assert result3.vibe_analyzed is True, "Third analysis should analyze vibe"
    assert result3.model_used == "qwen/qwen3-235b-a22b-2507", \
        "Third analysis should use updated model"
    assert result3.cost > 0, "Third analysis should have cost"


# =============================================================================
# META-TEST: Verify imports will fail (RED phase)
# =============================================================================


def test_imports_will_fail():
    """
    Meta-test to document that imports should fail in RED phase.

    This test documents the expected ImportError that will occur when
    running these tests before implementation.
    """
    with pytest.raises(ImportError):
        from app.services.hybrid_analysis_service import HybridAnalysisService

    with pytest.raises(ImportError):
        from app.schemas.hybrid_analysis import HybridAnalysisResult

    with pytest.raises(ImportError):
        from app.schemas.hybrid_analysis import BatchAnalysisResult

    with pytest.raises(ImportError):
        from app.schemas.hybrid_analysis import AnalysisConfig
