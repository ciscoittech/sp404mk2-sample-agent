# AI-Powered Sample Companion System for Wanns Wavs Collection

## Description
Build an intelligent system to analyze 500+ sample collection (Wanns Wavs) and automatically create complementary sample kits based on vibe/mood for SP-404MK2 workflow using Test-Driven Development (TDD) methodology.

## Technical Analysis
**Complexity**: 7/10
**Estimated Time**: 1-2 weeks
**Risk Level**: Medium (rate limits with free model)
**Development Methodology**: TDD (Test-Driven Development)

## Key Features
1. **Vibe-Based Analysis**: AI understands musical mood and character
2. **Complementary Kits**: Automatically groups 8-16 samples that work together  
3. **Collaborative Planning**: Chat interface for vibe selection before processing
4. **Full Automation**: Batch processes entire collection respecting rate limits

## TDD Implementation Plan

### Phase 1: Core Infrastructure Tests First (2-3 days)
```python
# Write tests BEFORE implementation:
test_vibe_analysis_agent.py
- test_agent_initialization()
- test_batch_processing_5_samples()
- test_rate_limit_handling()
- test_cache_persistence()

test_sample_data_models.py
- test_sample_metadata_structure()
- test_vibe_descriptor_validation()
- test_kit_composition_rules()
```

Then implement:
- [ ] Build `VibeAnalysisAgent` using Pydantic AI
- [ ] Implement batch processing for 5 RPM limit
- [ ] Create caching system for analyses

### Phase 2: Audio Analysis Tests First (2-3 days)
```python
# Write tests BEFORE implementation:
test_audio_analysis.py
- test_bpm_detection_accuracy()
- test_key_signature_detection()
- test_spectral_feature_extraction()
- test_pre_categorization_logic()

test_audio_fixtures.py
- Create test WAV files with known properties
- Mock librosa responses for unit tests
```

Then implement:
- [ ] Local feature extraction with librosa (BPM, key, spectrum)
- [ ] Pre-categorization by obvious features
- [ ] Spectral analysis for timbral matching

### Phase 3: AI Integration Tests First (3-4 days)
```python
# Write tests BEFORE implementation:
test_ai_integration.py
- test_batch_prompt_formation()
- test_vibe_classification_parsing()
- test_complementary_matching_logic()
- test_rate_limit_retry_mechanism()

test_mock_ai_responses.py
- Mock OpenRouter API responses
- Test error handling scenarios
```

Then implement:
- [ ] Batch prompt system (5 samples per request)
- [ ] Vibe/mood classification
- [ ] Complementary matching algorithm
- [ ] Rate limit handling with asyncio

### Phase 4: User Interface Tests First (2-3 days)
```python
# Write tests BEFORE implementation:
test_cli_interface.py
- test_vibe_selection_flow()
- test_progress_display()
- test_kit_preview_formatting()
- test_export_functionality()

test_user_interactions.py
- Test collaborative planning dialogue
- Test error messaging
- Test graceful cancellation
```

Then implement:
- [ ] Collaborative chat for vibe selection
- [ ] Progress tracking for batch processing
- [ ] Kit preview and export system
- [ ] SP-404MK2 format export

## Technical Considerations
- **Model**: FREE qwen/qwen3-235b-a22b-2507:free (5 RPM limit)
- **Processing Time**: ~20 minutes for 500 samples
- **Cost**: $0 (using free tier)
- **Storage**: JSON cache for all analyses
- **Testing**: 90%+ code coverage target

## Test-Driven Acceptance Criteria
- [ ] All unit tests pass before implementation
- [ ] Integration tests verify system behavior
- [ ] Can analyze 500+ samples within rate limits
- [ ] Groups samples into vibe-compatible kits of 8-16
- [ ] Exports kits in SP-404MK2 compatible format
- [ ] Provides collaborative chat interface
- [ ] Never re-analyzes cached samples
- [ ] Handles rate limits gracefully
- [ ] Test coverage > 90%

## TDD Workflow
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green
4. **Document**: Update docs with each feature

## Example Test Case
```python
# test_vibe_analysis.py
def test_sample_vibe_extraction():
    """Test that vibe descriptors are extracted correctly."""
    # Arrange
    sample = SampleData(
        filename="Adrian Younge Presents Venice Dawn.wav",
        bpm=85,
        key="Cm"
    )
    agent = VibeAnalysisAgent()
    
    # Act
    vibe = agent.analyze_vibe(sample)
    
    # Assert
    assert vibe.mood in ["cinematic", "atmospheric", "moody"]
    assert vibe.era == "modern-vintage"
    assert vibe.genre in ["soul", "jazz", "funk"]
    assert len(vibe.descriptors) == 3
```

## Definition of Done
- [ ] All acceptance criteria met
- [ ] All tests written and passing
- [ ] Documentation for vibe descriptors
- [ ] Example kits generated and tested
- [ ] No errors with rate limiting
- [ ] Code review completed
- [ ] Test coverage report > 90%

## MVP Scope
- Basic vibe analysis (mood, era, genre)
- Simple complementary matching
- Manual kit refinement option
- JSON export format
- Comprehensive test suite

## Future Enhancements
- Advanced harmonic analysis
- ML-based similarity matching
- Direct SP-404 file upload
- Web interface for kit browsing
- Performance optimizations

## Labels
`enhancement`, `ai`, `audio-processing`, `tdd`

## Specialist Chain
1. **Testing/Quality**: Set up TDD framework
2. **AI/Pydantic**: Implement agents with tests
3. **Audio Processing**: librosa integration
4. **CLI/UX**: User interface development