# SP404MK2 Sample Agent API Reference

This document provides a complete API reference for all agents, tools, and utilities in the SP404MK2 Sample Agent system.

## Table of Contents
1. [Conversational Interface](#conversational-interface)
2. [Agent APIs](#agent-apis)
3. [Tool APIs](#tool-apis)
4. [Utility Functions](#utility-functions)
5. [Data Models](#data-models)

---

## Conversational Interface

### SP404Chat
Main conversational interface class.

```python
from sp404_chat import SP404Chat

chat = SP404Chat()
await chat.start()
```

#### Methods

**`process_message(user_input: str) -> str`**
- Processes natural language input
- Returns streaming response
- Executes searches if intent detected

**`detect_search_intent(user_input: str, response: str) -> bool`**
- Analyzes if user wants to search for samples
- Returns True if search intent detected

---

## Agent APIs

### Groove Analyst Agent

```python
from src.agents.groove_analyst import GrooveAnalystAgent, analyze_groove

# Using the agent directly
agent = GrooveAnalystAgent()
result = await agent.execute(
    task_id="unique_id",
    file_paths=["sample1.wav", "sample2.wav"],
    analysis_depth="deep"  # "quick", "standard", or "deep"
)

# Using convenience function
result = await analyze_groove(
    file_paths=["sample.wav"],
    analysis_depth="standard",
    reference_artists=["dilla", "questlove"]
)
```

#### Response Structure
```python
{
    "analyses": [{
        "file_path": str,
        "file_name": str,
        "bpm": float,
        "swing_percentage": float,
        "groove_type": str,  # "straight", "swing", "shuffle", etc.
        "timing_feel": str,  # "ahead", "behind", "on"
        "micro_timing": Dict[str, float],
        "closest_references": List[Dict[str, Any]],
        "production_tips": List[str]
    }],
    "summary": {
        "files_analyzed": int,
        "average_swing": float,
        "dominant_groove": str
    }
}
```

### Era Expert Agent

```python
from src.agents.era_expert import EraExpertAgent, analyze_era, get_era_search_queries

# Era detection from audio
result = await analyze_era(
    file_paths=["vintage.wav"],
    enhance_search=True
)

# Get era information
result = await analyze_era(
    target_era="1970s",
    genre="soul",
    enhance_search=True
)

# Generate search queries
queries = await get_era_search_queries(
    era="1990s",
    genre="hip-hop",
    base_query="drum breaks"
)
```

#### Response Structure
```python
{
    "analyses": [{
        "detected_era": str,  # "1970s", "1990s", etc.
        "confidence": float,
        "equipment": List[Dict[str, Any]],
        "techniques": Dict[str, List[str]],
        "characteristics": Dict[str, str],
        "genre_context": Dict[str, Any],
        "enhanced_searches": List[str],
        "modern_recreation": Dict[str, List[str]]
    }],
    "summary": {
        "predominant_era": str,
        "recommended_searches": List[str]
    }
}
```

### Sample Relationship Agent

```python
from src.agents.sample_relationship import analyze_sample_compatibility, check_harmonic_compatibility

# Full compatibility analysis
result = await analyze_sample_compatibility(
    sample_pairs=[("kick.wav", "bass.wav"), ("snare.wav", "hihat.wav")],
    genre="hip-hop",
    analysis_depth="standard",
    check_type="all"  # "harmonic", "rhythmic", "frequency", or "all"
)

# Quick harmonic check
result = await check_harmonic_compatibility("sample1.wav", "sample2.wav")
```

#### Response Structure
```python
{
    "analyses": [{
        "sample1_path": str,
        "sample2_path": str,
        "overall_score": float,  # 0-10
        "harmonic": {
            "key_relationship": str,
            "interval_semitones": int,
            "compatibility_score": float,
            "suggestion": Optional[str]
        },
        "rhythmic": {
            "bpm_compatibility": float,  # 0-100%
            "tempo_relationship": str,
            "groove_match": float,  # 0-10
            "timing_alignment": str
        },
        "frequency": {
            "overlap_areas": List[str],
            "masking_risk": str,  # "low", "medium", "high"
            "complementary_score": float,
            "eq_suggestions": List[str]
        },
        "recommendations": List[str],
        "best_arrangement": str,
        "relationship_type": str
    }],
    "kit_suggestions": Dict[str, Any]  # If multiple pairs analyzed
}
```

---

## Tool APIs

### YouTube Search Tool

```python
from src.tools.youtube_search import YouTubeSearcher

searcher = YouTubeSearcher()
results = await searcher.search(
    query="boom bap drums 90 bpm",
    max_results=20,
    quality_threshold=0.5  # 0-1, filters by quality score
)
```

#### Quality Scoring Factors
- View count (logarithmic scale)
- Duration (optimal: 30s-5min)
- Channel reputation
- Title relevance
- Upload recency

### Timestamp Extractor

```python
from src.tools.timestamp_extractor import TimestampExtractor

extractor = TimestampExtractor()

# Extract timestamps from video
timestamps = await extractor.extract_timestamps(url="youtube.com/watch?v=...")

# Extract segments
await extractor.extract_segments(
    url="youtube.com/watch?v=...",
    output_dir="samples/",
    timestamps=timestamps,  # Optional, auto-detects if not provided
    quality_threshold=2  # Minimum fire emoji count
)
```

### Intelligent Organizer

```python
from src.tools.intelligent_organizer import IntelligentOrganizer, organize_samples, create_sp404_banks

# General organization
result = await organize_samples(
    sample_paths=["sample1.wav", "sample2.wav"],
    strategy="musical",  # See strategies below
    output_dir="organized/",
    analyze_relationships=True,
    copy_files=True  # False for dry run
)

# SP-404 specific
result = await create_sp404_banks(
    sample_paths=samples,
    template="hip_hop_kit",  # "live_performance", "finger_drumming"
    output_dir="sp404_banks/"
)
```

#### Organization Strategies
- `"musical"` - By BPM, key, and type
- `"genre"` - By detected era and genre
- `"groove"` - By rhythmic characteristics
- `"compatibility"` - Groups that work well together
- `"sp404"` - SP-404 bank structure
- `"project"` - Project-specific layouts

### Audio Analysis Tools

```python
from src.tools.audio import detect_bpm, detect_key, analyze_frequency_content, get_duration

# BPM detection
bpm_info = detect_bpm("sample.wav")
# Returns: {"bpm": float, "confidence": float}

# Key detection
key_info = detect_key("sample.wav")
# Returns: {"key": str, "confidence": float}

# Frequency analysis
freq_info = analyze_frequency_content("sample.wav")
# Returns: {
#     "spectral_centroid": float,
#     "spectral_bandwidth": float,
#     "spectral_rolloff": float
# }

# Duration
duration = get_duration("sample.wav")  # Returns float (seconds)
```

---

## Utility Functions

### Musical Understanding

```python
from src.chat.musical_understanding import MusicalUnderstanding

mu = MusicalUnderstanding()

# Parse natural language request
request = mu.parse_request("I need jazzy drums from the 90s with that Dilla swing")
# Returns: MusicalRequest object with structured data

# Extract search queries
queries = mu.extract_search_queries(request)
# Returns: List[str] of search queries
```

---

## Data Models

### Base Agent Models

```python
from src.agents.base import AgentResult, AgentStatus

class AgentResult:
    agent_name: str
    task_id: str
    status: AgentStatus  # SUCCESS, FAILED, PENDING
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: datetime
    completed_at: datetime
```

### Musical Request Model

```python
from src.chat.musical_understanding import MusicalRequest

class MusicalRequest(BaseModel):
    genres: List[str]
    bpm_range: Optional[Tuple[int, int]]
    eras: List[str]
    mood_descriptors: List[str]
    texture_descriptors: List[str]
    reference_artists: List[str]
    specific_elements: List[str]
```

### Groove Analysis Models

```python
class GrooveAnalysis(BaseModel):
    bpm: float
    swing_percentage: float
    groove_type: str
    timing_feel: str
    micro_timing: Dict[str, float]
    humanization_score: float
    complexity_rating: str
```

### Era Analysis Models

```python
class EraAnalysisResult(BaseModel):
    detected_era: Optional[str]
    confidence: float
    key_equipment: List[EraEquipment]
    techniques: EraTechniques
    sonic_characteristics: EraCharacteristics
    genre_context: Dict[str, str]
    search_queries: List[str]
```

### Compatibility Models

```python
class CompatibilityResult(BaseModel):
    sample1_path: str
    sample2_path: str
    overall_score: float
    harmonic: HarmonicAnalysis
    rhythmic: RhythmicAnalysis
    frequency: FrequencyAnalysis
    energy_compatibility: float
    recommendations: List[str]
    best_arrangement: str
    relationship_type: str
```

---

## Error Handling

All agents follow consistent error handling:

```python
try:
    result = await agent.execute(...)
    if result.status == AgentStatus.SUCCESS:
        # Process result.result
    else:
        # Handle error in result.error
except Exception as e:
    # Handle unexpected errors
```

---

## Rate Limiting and Performance

### Recommendations
- Process samples in batches of 20-50
- Use `analysis_depth="quick"` for initial scans
- Enable caching for repeated analyses
- Disable relationship analysis for large batches

### Async Best Practices
```python
# Process multiple files concurrently
import asyncio

async def batch_analyze(files):
    tasks = [analyze_groove([f]) for f in files]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Environment Variables

```bash
# Required
OPENROUTER_API_KEY="your-api-key"

# Optional
TURSO_URL="your-turso-url"
TURSO_TOKEN="your-turso-token"

# Performance tuning
MAX_CONCURRENT_DOWNLOADS=5
ANALYSIS_BATCH_SIZE=20
CACHE_DIR="~/.sp404_cache"
```

---

## Examples

### Complete Discovery Pipeline
```python
async def discover_and_organize():
    # 1. Search for samples
    searcher = YouTubeSearcher()
    videos = await searcher.search("boom bap drums 90 bpm")
    
    # 2. Extract samples
    extractor = TimestampExtractor()
    for video in videos[:5]:
        await extractor.extract_segments(
            url=video["url"],
            output_dir="raw_samples/"
        )
    
    # 3. Analyze samples
    samples = glob.glob("raw_samples/*.wav")
    groove_analysis = await analyze_groove(samples)
    era_analysis = await analyze_era(samples)
    
    # 4. Check compatibility
    pairs = [(samples[i], samples[i+1]) for i in range(0, len(samples)-1, 2)]
    compatibility = await analyze_sample_compatibility(pairs)
    
    # 5. Organize
    await organize_samples(
        samples,
        strategy="compatibility",
        output_dir="organized/"
    )
```

### SP-404 Kit Building
```python
async def build_sp404_kit(theme="jazz"):
    # 1. Search with era context
    queries = await get_era_search_queries("1970s", theme, "drum breaks")
    
    # 2. Collect samples
    samples = []
    for query in queries[:3]:
        results = await searcher.search(query)
        # ... download best results
    
    # 3. Create SP-404 banks
    await create_sp404_banks(
        samples,
        template="hip_hop_kit",
        output_dir=f"sp404_{theme}_kit/"
    )
```