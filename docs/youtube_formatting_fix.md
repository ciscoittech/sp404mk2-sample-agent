# YouTube URL Formatting Fix

## Issue
When users provide YouTube URLs, the CLI output was coming back "out of format" - text was being printed directly to stdout during streaming, bypassing Rich's formatting system.

## Root Cause
1. The streaming response was using `print()` directly instead of Rich's console
2. YouTube URL inputs weren't being detected and handled differently from regular searches
3. Markdown formatting in responses wasn't being properly rendered

## Solution Implemented

### 1. Added YouTube URL Detection
```python
def is_youtube_url(self, text: str) -> bool:
    """Check if text contains a YouTube URL."""
    youtube_patterns = [
        'youtube.com/watch',
        'youtu.be/',
        'youtube.com/v/',
        'youtube.com/embed/'
    ]
    return any(pattern in text.lower() for pattern in youtube_patterns)
```

### 2. Created Dedicated YouTube Analysis Handler
```python
async def analyze_youtube_url(self, url: str) -> Dict[str, Any]:
    """Analyze a YouTube URL for samples."""
    # Extracts timestamps and metadata
    # Returns structured data for proper formatting
```

### 3. Fixed Streaming Output
- Removed direct `print()` calls during streaming
- Response is now collected and formatted through Rich

### 4. Added Proper Markdown Rendering
```python
# Format the response with proper line breaks
formatted_response = response.replace("\\n", "\n")

# If response contains markdown-style formatting, render it properly
if "**" in formatted_response or "##" in formatted_response:
    from rich.markdown import Markdown
    md = Markdown(formatted_response)
    console.print(md)
else:
    console.print(formatted_response)
```

## Result
- YouTube URLs are now properly detected and analyzed
- Output is formatted in clean tables with proper styling
- Timestamps are displayed in an organized table format
- Markdown in responses is properly rendered
- No more raw/unformatted text output

## Testing
Run `python test_youtube_formatting.py` to verify formatting works correctly.