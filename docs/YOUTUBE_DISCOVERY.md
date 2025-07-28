# Enhanced YouTube Discovery

The enhanced YouTube discovery system provides intelligent search capabilities with musical understanding, quality scoring, and specialized search modes.

## Features

### 🎯 Intelligent Search
- **Quality Scoring**: Automatically scores videos based on relevance and quality indicators
- **Sample Filtering**: Filters out tutorials, reactions, and non-sample content
- **Producer Channels**: Recognizes trusted producer and label channels
- **Engagement Metrics**: Considers views, likes, and ratios for quality assessment

### 🎵 Musical Search Modes

#### 1. Standard Search
```python
results = await searcher.search("jazz drum samples", max_results=20)
```
- Optimized for finding sample packs and loops
- Filters by music category
- Prioritizes medium-length videos (4-20 minutes)

#### 2. Era-Specific Search
```python
results = await searcher.search_by_era("70s", "soul", max_results=20)
```
- Maps era descriptions to multiple search terms
- Combines era-specific terminology (e.g., "seventies", "1970s", "funk soul")
- Understands production characteristics by decade

#### 3. Producer-Style Search
```python
results = await searcher.search_by_producer("dilla", max_results=20)
```
- Searches for specific producer styles and techniques
- Includes related terms (e.g., "MPC3000", "Detroit hip hop")
- Finds type beats and similar production styles

#### 4. Vibe-Based Search
```python
results = await search_youtube_by_vibe("dusty", "hip-hop", max_results=20)
```
- Translates vibe descriptions to technical terms
- Expands queries with related concepts
- Maintains musical context

## Quality Scoring System

### Scoring Factors

1. **Title Indicators** (+0.1 each)
   - Quality terms: "HQ", "HD", "WAV", "FLAC", "24bit", "lossless"
   - Format mentions: "high quality", "studio quality", "vinyl rip"

2. **Sample Pack Indicators** (+0.15 each)
   - "sample pack", "drum kit", "loop kit"
   - "free download", "royalty free", "no copyright"

3. **Channel Reputation** (+0.2)
   - Recognized producer channels (Splice, Mass Appeal, etc.)
   - Genre-specific trusted sources

4. **Engagement Metrics**
   - Views > 10,000: +0.1
   - Views > 100,000: +0.1
   - Like ratio > 4%: +0.1

5. **Duration Scoring** (+0.1)
   - Optimal range: 3-20 minutes
   - Filters out short clips and long streams

### Filtering System

Videos are filtered out if they:
- Are too short (<60s) or too long (>1 hour)
- Contain non-sample keywords: "reaction", "review", "tutorial", "explained"
- Have very low engagement or quality scores

Videos are boosted if they contain:
- Sample-related terms: "sample", "loop", "break", "drum", "kit"
- Format indicators: "wav", "free", "download"

## Integration with Collector Agent

The enhanced YouTube search is fully integrated with the collector agent:

```python
# In collector.py
async def search_youtube(query: str, max_results: int = 10) -> List[Dict]:
    """Search YouTube for samples using enhanced search."""
    results = await youtube_searcher.search(query, max_results, filter_samples=True)
    # Results include quality scores and metadata
```

### Query Generation

The collector agent now generates optimized queries:
- Base queries with genre and style
- BPM-specific variations
- Era-specific terminology
- Quality indicators ("free download", "WAV samples")

## API Configuration

### With YouTube Data API v3
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```
- Full search capabilities
- Detailed video metadata
- Higher rate limits

### Without API Key
- Falls back to mock data for testing
- Limited functionality in production
- Consider web scraping alternatives

## Usage Examples

### Basic Search
```python
from src.tools.youtube_search import YouTubeSearcher

searcher = YouTubeSearcher()
results = await searcher.search("boom bap drums", max_results=10)

for result in results:
    print(f"{result['title']} - Score: {result['quality_score']:.2f}")
```

### Advanced Search with Filters
```python
# Search for high-quality 90s samples
results = await searcher.search_by_era("90s", "hip-hop", max_results=20)

# Filter by quality score
high_quality = [r for r in results if r['quality_score'] > 0.8]

# Sort by engagement
by_views = sorted(results, key=lambda x: x['view_count'], reverse=True)
```

### Multi-Platform Search
```python
# Get platform-optimized results
results = await searcher.search_multi_platform("jazz samples", max_results=30)

# Access different result categories
samples = results['youtube']      # Direct sample results
tutorials = results['tutorials']  # Production tutorials
performances = results['performances']  # Live performances
```

## Performance Optimizations

1. **Batch Processing**: Multiple queries executed concurrently
2. **Result Caching**: Duplicate detection across searches
3. **Smart Filtering**: Early filtering reduces processing
4. **Quality Prioritization**: Best results returned first

## Future Enhancements

1. **Machine Learning**: Train quality classifier on labeled data
2. **Timestamp Extraction**: Identify specific sample moments
3. **Audio Preview**: Quick preview without full download
4. **Playlist Support**: Process entire YouTube playlists
5. **Channel Monitoring**: Track favorite producer channels

## Troubleshooting

### No Results Found
- Check internet connection
- Verify API key if using YouTube Data API
- Try broader search terms
- Check for rate limiting

### Low Quality Results
- Adjust quality threshold
- Add more specific search terms
- Use producer or era-specific searches
- Filter by trusted channels

### API Rate Limits
- Implement caching
- Batch searches efficiently
- Use quota-aware request management
- Consider fallback strategies