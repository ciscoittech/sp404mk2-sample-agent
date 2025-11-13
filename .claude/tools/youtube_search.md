# YouTube Search Tool

## Purpose
Search YouTube for sample packs, loops, and breakbeats with intelligent quality filtering and relevance scoring. This is the primary discovery tool for finding sample content on YouTube.

## When to Use

**Use this tool when:**
- ✅ User explicitly asks to "find", "search", or "discover" samples
- ✅ User mentions genres/styles/eras they want samples for
- ✅ User references producer/artist styles (e.g., "Madlib sound")
- ✅ User wants sample recommendations based on vibe/mood
- ✅ Building a sample collection for a project

**DO NOT use this tool when:**
- ❌ User provides a specific YouTube URL (use `timestamp_extractor` instead)
- ❌ User asks general questions about music ("What is boom bap?")
- ❌ User wants to analyze existing samples (use `audio_analyzer`)
- ❌ User wants to organize downloaded samples (use `download_manager`)

## Tool Signature

```python
async def search(
    query: str,
    max_results: int = 10,
    filter_samples: bool = True
) -> List[Dict[str, Any]]
```

## Parameters

### `query` (required)
**Type:** `string`
**Description:** The YouTube search query to execute

**Good Examples:**
```python
# Specific genre + era + element
query = "90s boom bap drum samples"

# Artist reference + type
query = "Madlib style sample pack"

# Texture + genre + format
query = "dusty jazz loops vinyl"

# Technical + genre + quality
query = "85-95 BPM hip hop samples WAV"
```

**Bad Examples:**
```python
# Too vague (returns anything)
query = "samples"  ❌

# Too narrow (no results)
query = "1994 NYC underground MPC60 boom bap breaks" ❌

# Using negation (doesn't work on YouTube)
query = "samples -trap -edm" ❌

# Missing sample indicators
query = "jazz 70s"  ❌ (should be "jazz samples 70s")
```

**Common Mistakes:**
- Not including "samples", "pack", "loops", or "breaks" in query
- Overloading query with too many adjectives
- Using too-generic terms ("beats" instead of "drum samples")
- Not specifying use case ("jazz" vs "jazz samples for hip hop")

**Heuristics for Query Construction:**
```
WHEN: User request is vague or conversational
CONSIDER: What genre, era, texture, BPM, or artist they're implying
GENERALLY: Include 2-4 core terms (genre + descriptor + "samples")
UNLESS: Direct artist reference, then use "[Artist] style sample pack"

Example:
User: "I need that Dilla bounce"
→ Query: "J Dilla style sample pack" OR "neo soul samples 90 BPM"
NOT: "Dilla bounce" (too literal)
```

---

### `max_results` (optional)
**Type:** `integer`
**Default:** `10`
**Range:** `1-50` (recommended: 5-20)

**Description:** Maximum number of results to return

**Guidelines:**
```
Initial exploration: 10-15 results
Comprehensive collection: 20-30 results
Quick check: 5 results
Avoid: >30 results (diminishing returns, slower)
```

**Common Mistakes:**
- Requesting 50+ results (slow, low-quality results at end)
- Requesting 1-2 results (not enough variety)

**Heuristics:**
```
WHEN: Building initial collection
CONSIDER: User's intent (exploring vs specific need)
GENERALLY: Default to 10 results
UNLESS: User explicitly wants "a lot" (use 20-25)
```

---

### `filter_samples` (optional)
**Type:** `boolean`
**Default:** `true`

**Description:** Filter results to prioritize actual sample content over beats/songs

**When to use `true` (default):**
- Looking for samples to make beats with ✅
- Sample discovery workflow ✅
- Building sample library ✅

**When to use `false`:**
- User wants inspiration from finished tracks
- Analyzing production techniques in songs
- Finding song references (rare)

**Heuristics:**
```
WHEN: Searching for content
CONSIDER: Is user looking for samples (to use) or songs (to listen)?
GENERALLY: Always use filter_samples=true
UNLESS: User explicitly asks for "songs" or "beats" (not samples)
```

## Return Value

**Type:** `List[Dict[str, Any]]`

**Structure:**
```python
{
    "url": str,                    # Full YouTube URL
    "title": str,                  # Video title
    "channel": str,                # Channel name
    "duration": int,               # Duration in seconds
    "view_count": int,             # Number of views
    "published_at": str,           # ISO 8601 date
    "description": str,            # Video description (truncated)
    "quality_score": float,        # 0.0-1.0 relevance score
    "platform": "youtube"          # Platform identifier
}
```

**Quality Score Interpretation:**
```
0.9-1.0: Excellent match (sample pack, clear title, good metadata)
0.7-0.89: Good match (likely samples, decent quality indicators)
0.5-0.69: Fair match (might be samples, needs verification)
<0.5: Weak match (probably not samples, filtered out if filter_samples=true)
```

**Example Return:**
```python
[
    {
        "url": "https://youtube.com/watch?v=abc123",
        "title": "90s Boom Bap Drum Kit - FREE Download",
        "channel": "SampleSupply",
        "duration": 180,
        "view_count": 45000,
        "published_at": "2023-05-15T10:30:00Z",
        "description": "Classic 90s hip hop drums...",
        "quality_score": 0.95,
        "platform": "youtube"
    },
    # ... more results
]
```

## Error Cases

### Common Errors and Handling

**1. No Results Found**
```python
# Returns empty list
results = []

# How to handle:
if not results:
    # Try broader query or alternative terms
    alternative_query = broaden_search(original_query)
```

**2. API Rate Limit**
```python
# Raises: Exception with rate limit message
# How to handle: Exponential backoff, cache results
```

**3. Invalid Query**
```python
# Empty query or too short
# Raises: ValueError
# How to handle: Validate query length (>3 chars)
```

**4. Network Error**
```python
# Connection issues
# Raises: aiohttp.ClientError
# How to handle: Retry with exponential backoff
```

## Usage Examples

### Example 1: User Wants Boom Bap Drums

**Context:**
```
User: "I need some boom bap drums around 90 BPM"
```

**Thinking Process:**
```
1. Intent: Sample discovery (use youtube_search)
2. Genre: Boom bap (90s hip-hop style)
3. Element: Drums
4. BPM: ~90
5. Query strategy: Include all key terms
```

**Tool Usage:**
```python
from src.tools.youtube_search import YouTubeSearcher

searcher = YouTubeSearcher()

# Construct query with specificity
query = "boom bap drum samples 90 BPM"

results = await searcher.search(
    query=query,
    max_results=10,
    filter_samples=True  # We want samples, not beats
)

# Process results
for result in results:
    if result['quality_score'] > 0.7:  # Good matches only
        print(f"Found: {result['title']}")
        print(f"  Quality: {result['quality_score']}")
        print(f"  URL: {result['url']}")
```

**Why This Works:**
- Specific BPM mentioned
- "Samples" keyword included
- Genre clearly stated
- Reasonable max_results for exploration

---

### Example 2: Artist Style Reference

**Context:**
```
User: "Find me some Madlib-style loops"
```

**Thinking Process:**
```
1. Intent: Sample discovery with artist reference
2. Artist: Madlib (sample-heavy, jazzy, dusty aesthetic)
3. Element: Loops
4. Strategy: Direct reference + genre descriptors
```

**Tool Usage:**
```python
# Primary query: Direct artist reference
primary_query = "Madlib style sample pack"
primary_results = await searcher.search(
    query=primary_query,
    max_results=10,
    filter_samples=True
)

# Alternative queries for variety
alt_queries = [
    "dusty jazz samples vinyl",
    "obscure soul samples rare groove",
    "psychedelic funk samples"
]

all_results = primary_results
for alt_query in alt_queries[:1]:  # Use 1-2 alternatives
    alt_results = await searcher.search(
        query=alt_query,
        max_results=5,
        filter_samples=True
    )
    all_results.extend(alt_results)

# Deduplicate by URL
unique_results = {r['url']: r for r in all_results}.values()
```

**Why This Works:**
- Primary query uses direct artist reference (YouTube knows this)
- Alternative queries target Madlib's musical characteristics
- Combining multiple angles gets variety
- Deduplication prevents showing same video twice

---

### Example 3: Vibe-Based Search

**Context:**
```
User: "I want that lo-fi bedroom producer sound"
```

**Thinking Process:**
```
1. Intent: Vibe-based discovery (abstract request)
2. Aesthetic: Lo-fi, bedroom, imperfect
3. Translation needed: Vibe → concrete search terms
4. Strategy: Multiple queries covering different aspects
```

**Tool Usage:**
```python
# Translate vibe to concrete terms
queries = [
    "lo-fi hip hop sample pack",           # Direct genre
    "vinyl crackle ambient textures",      # Texture elements
    "dusty piano samples emotional",       # Melodic elements
    "jazz samples for lo-fi beats"         # Source material
]

all_results = []
for query in queries:
    results = await searcher.search(
        query=query,
        max_results=8,  # Slightly fewer per query
        filter_samples=True
    )
    all_results.extend(results)

# Sort by quality score
all_results.sort(key=lambda x: x['quality_score'], reverse=True)

# Return top 15 unique results
seen_urls = set()
unique_results = []
for result in all_results:
    if result['url'] not in seen_urls and len(unique_results) < 15:
        seen_urls.add(result['url'])
        unique_results.append(result)
```

**Why This Works:**
- Vibe translated to multiple concrete queries
- Each query targets different aspect of the aesthetic
- Combined results give comprehensive coverage
- Quality sorting ensures best matches first

---

### Example 4: Error Handling

**Robust Implementation:**
```python
async def safe_youtube_search(query: str, max_results: int = 10):
    """Search with proper error handling."""

    # Validate input
    if not query or len(query) < 3:
        raise ValueError("Query must be at least 3 characters")

    # Ensure sample indicators present
    if not any(term in query.lower() for term in ['sample', 'pack', 'loop', 'break', 'kit']):
        query += " samples"  # Add if missing

    searcher = YouTubeSearcher()

    try:
        results = await searcher.search(
            query=query,
            max_results=max_results,
            filter_samples=True
        )

        # Handle empty results
        if not results:
            # Try broader query
            broader_query = simplify_query(query)
            results = await searcher.search(
                query=broader_query,
                max_results=max_results,
                filter_samples=True
            )

        return results

    except aiohttp.ClientError as e:
        # Network error: retry once
        await asyncio.sleep(2)
        return await searcher.search(query, max_results, filter_samples=True)

    except Exception as e:
        # Log error and return empty list
        logger.error(f"YouTube search failed: {e}")
        return []

def simplify_query(query: str) -> str:
    """Remove overly specific terms to broaden search."""
    # Remove BPM numbers
    query = re.sub(r'\d+-?\d*\s*bpm', '', query, flags=re.IGNORECASE)
    # Remove year ranges
    query = re.sub(r'\d{4}s?', '', query)
    return query.strip()
```

## Best Practices

### 1. Query Construction
```python
# Good: Specific but not overloaded
"90s boom bap drum samples"

# Bad: Too many descriptors
"vintage old school classic 90s east coast underground boom bap drums"

# Good: Uses cultural references
"J Dilla style sample pack"

# Bad: Too abstract
"samples with that vibe you know"
```

### 2. Result Processing
```python
# Always check quality score
good_results = [r for r in results if r['quality_score'] > 0.7]

# Verify sample indicators in title
has_sample_terms = any(
    term in result['title'].lower()
    for term in ['sample', 'pack', 'loop', 'break', 'kit']
)

# Check duration (sample packs usually 2-10 minutes)
reasonable_duration = 120 <= result['duration'] <= 600
```

### 3. Multi-Query Strategies
```python
# For comprehensive coverage, use 3-5 related queries
primary = "boom bap drum samples"
secondary = "90s hip hop drums"
tertiary = "MPC drum kit"

# Combine and deduplicate
all_results = combine_and_dedupe([
    await search(primary, 10),
    await search(secondary, 8),
    await search(tertiary, 5)
])
```

### 4. Caching Results
```python
# YouTube search is expensive (API calls)
# Cache results for repeated queries
cache_key = f"yt_search:{query}:{max_results}"
if cache_key in cache:
    return cache[cache_key]

results = await searcher.search(query, max_results)
cache[cache_key] = results
cache.expire(cache_key, 3600)  # 1 hour TTL
```

## Integration with Other Tools

### Flow 1: Discovery → Analysis → Download
```python
# 1. Search for samples
results = await youtube_search("lo-fi piano samples", 10)

# 2. Get video metadata for top result
from src.tools.timestamp_extractor import TimestampExtractor
extractor = TimestampExtractor()
timestamps = extractor.extract_from_url(results[0]['url'])

# 3. Download specific segments
from src.tools.download import download_youtube_segment
for ts in timestamps:
    await download_youtube_segment(
        url=results[0]['url'],
        start_time=ts['seconds'],
        duration=ts.get('duration', 30)
    )
```

### Flow 2: Search → Metadata → Database
```python
# 1. Search
results = await youtube_search("trap drums", 15)

# 2. Store metadata
from src.tools.database import add_sample_source
for result in results:
    await add_sample_source({
        'url': result['url'],
        'title': result['title'],
        'platform': 'youtube',
        'quality_score': result['quality_score'],
        'discovered_at': datetime.now()
    })
```

## Performance Considerations

**Rate Limits:**
- YouTube Data API: 10,000 quota units/day
- Each search: ~100 units
- Max searches per day: ~100
- **Recommendation**: Cache aggressively, batch user requests

**Response Time:**
- Average: 1-3 seconds per search
- Slow queries: 5-10 seconds (complex searches)
- **Recommendation**: Show loading indicator, use async

**Result Quality:**
- First 5-10 results: Usually high quality
- Results 11-20: Declining quality
- Results 20+: Often irrelevant
- **Recommendation**: Default to 10, max 20

## Troubleshooting

### Problem: No Results
**Causes:**
- Query too specific
- Rare genre/artist
- Misspelled terms

**Solutions:**
```python
# Broaden query
if not results:
    # Remove BPM/year constraints
    broader = remove_constraints(query)
    results = await search(broader)

# Try alternative terms
alternatives = generate_alternatives(query)
for alt in alternatives:
    results = await search(alt)
    if results:
        break
```

### Problem: Low-Quality Results
**Causes:**
- Generic query
- filter_samples=False
- Low quality_score threshold

**Solutions:**
```python
# Add specificity
query = f"{query} sample pack WAV"

# Filter strictly
good_results = [r for r in results if r['quality_score'] > 0.8]

# Verify sample indicators
has_download = 'free' in r['title'].lower() or 'download' in r['title'].lower()
```

### Problem: Repeated Results Across Queries
**Causes:**
- Similar queries hit same videos
- Popular videos dominate

**Solutions:**
```python
# Deduplicate across queries
seen_urls = set()
unique = []
for result in all_results:
    if result['url'] not in seen_urls:
        seen_urls.add(result['url'])
        unique.append(result)

# Diversify by channel
by_channel = defaultdict(list)
for r in results:
    by_channel[r['channel']].append(r)

# Take max 2 per channel
diverse = []
for channel, vids in by_channel.items():
    diverse.extend(vids[:2])
```

## Summary

**Key Takeaways:**
1. ✅ Always include "samples", "pack", "loops", or "kit" in queries
2. ✅ Use 2-4 core terms (not 10+ adjectives)
3. ✅ Direct artist references work better than describing their sound
4. ✅ Default to max_results=10, rarely exceed 20
5. ✅ Always use filter_samples=true for sample discovery
6. ✅ Check quality_score > 0.7 for reliable matches
7. ✅ Cache results to respect API limits
8. ✅ Handle errors gracefully with fallback queries

**This tool is your primary sample discovery mechanism. Use it well.**
