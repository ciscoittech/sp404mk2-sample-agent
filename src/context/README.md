# Intelligent Context Management

**Status:** ✅ Complete (Priority 4)
**Location:** `src/context/`

## Overview

Intelligent tier-based context management system for SP404MK2 agents. Automatically loads relevant context based on task type while managing token budgets and providing performance metrics.

## Features

### 4-Tier Context Hierarchy

1. **Tier 1 - Immediate** (always loaded, ~500-1200 tokens)
   - Current user request
   - Last 2-3 conversation exchanges
   - Current task status

2. **Tier 2 - Working** (loaded for active tasks, ~800-2000 tokens)
   - Current musical intent and parameters
   - Active search results
   - Discovered samples
   - Relevant tool documentation

3. **Tier 3 - Reference** (loaded on demand, ~500-1500 tokens)
   - Task-specific heuristics
   - Tool registry
   - Quick reference guides

4. **Tier 4 - Background** (loaded selectively, ~300-1000 tokens)
   - Thinking protocols
   - Example patterns
   - Specialist knowledge excerpts

### Smart Features

- **Task Detection**: Automatically detects task type from user input
- **Budget Management**: Soft limit (4000) and hard limit (5000) with automatic pruning
- **Context Prioritization**: Preserves critical context when over budget
- **Performance Metrics**: Tracks token usage, load times, pruning events
- **Backwards Compatible**: Drop-in replacement for old ConversationContext

## Usage

### Basic Usage

```python
from src.context import IntelligentContextManager

# Initialize
manager = IntelligentContextManager()

# Build context for LLM
context = manager.build_context("I need some 90s boom bap samples")

# Add conversation history
manager.add_exchange(user_input, agent_response)

# Get metrics
metrics = manager.get_metrics_summary()
```

### Integration with Chat Agent

```python
class SP404ChatAgent:
    def __init__(self):
        self.context = IntelligentContextManager()

    async def process_request(self, user_input: str) -> str:
        # Build intelligent context automatically
        intelligent_context = self.context.build_context(user_input)

        # Use in LLM messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": intelligent_context},
            {"role": "user", "content": user_input}
        ]
```

### State Management

```python
# Update musical intent
manager.update_musical_intent({
    "genres": ["soul", "funk"],
    "bpm_range": (85, 95),
    "era": "70s"
})

# Add discovered samples
manager.add_discovered_sample({
    "title": "Sample Title",
    "platform": "youtube",
    "quality_score": 0.85
})

# Register active tools
manager.register_active_tool("youtube_search")

# Update search results
manager.update_search_results(results_list)
```

### Metrics and Monitoring

```python
# Get metrics summary
metrics = manager.get_metrics_summary()

print(f"Total Tokens: {metrics['current_state']['total_tokens']}")
print(f"Requests: {metrics['performance']['total_requests']}")
print(f"Avg Load Time: {metrics['performance']['avg_load_time_ms']:.2f}ms")
print(f"Pruning Rate: {metrics['budget_management']['pruning_rate']:.1f}%")

# Export metrics to file
manager.export_metrics("context_metrics.json")
```

## Configuration

Context behavior is configured in `.claude/context/tier_config.json`:

```json
{
  "tier_budgets": {
    "tier1_immediate": {
      "min_tokens": 500,
      "max_tokens": 1200,
      "priority": 1,
      "always_loaded": true
    }
  },
  "total_budget": {
    "soft_limit": 4000,
    "hard_limit": 5000
  },
  "task_type_detection": {
    "sample_search": {
      "keywords": ["find", "search", "looking for"],
      "required_tiers": [1, 2, 3],
      "load_heuristics": ["search_intent_detection", "query_generation"]
    }
  }
}
```

### Task Types

The system automatically detects these task types:

- **sample_search** - User wants to find samples
  - Loads: Tiers 1-3 + search heuristics + query protocol
  - Triggers: "find", "search", "looking for", "need samples"

- **vibe_analysis** - User wants vibe/mood analysis
  - Loads: Tiers 1, 2, 4 + quality heuristics + vibe protocol
  - Triggers: "analyze", "vibe", "mood"

- **youtube_analysis** - User provides YouTube URL
  - Loads: Tiers 1-2 + timestamp extractor docs
  - Triggers: "youtube.com", "youtu.be"

- **general_conversation** - Default fallback
  - Loads: Tier 1 only (minimal context)

## Architecture

### Core Modules

- **`intelligent_manager.py`** - Main context orchestrator (491 lines)
  - Task detection
  - Tier loading
  - Budget management
  - Pruning strategy

- **`context_tiers.py`** - Tier loaders (520 lines)
  - Tier 1-4 loading logic
  - Content formatting
  - Token estimation

- **`metrics.py`** - Metrics tracking (183 lines)
  - Performance metrics
  - Budget tracking
  - Snapshot history

### Key Classes

```
IntelligentContextManager
├── TierLoader
│   ├── load_tier1_immediate()
│   ├── load_tier2_working()
│   ├── load_tier3_reference()
│   └── load_tier4_background()
└── ContextMetrics
    ├── record_load()
    ├── record_prune()
    └── get_summary()
```

## Token Budget Management

### Budget Strategy

- **Soft Limit (4000 tokens)**: Normal operation ceiling
- **Hard Limit (5000 tokens)**: Absolute maximum
- **Warning Threshold (3500 tokens)**: Alert before pruning

### Pruning Strategy

When context exceeds soft limit:

1. **Priority-based pruning**: Remove lower-priority tiers first
2. **Prune order**: Tier 4 → Tier 3 → Tier 2
3. **Tier 1 protection**: Always preserved (current request + recent history)
4. **Oldest-first**: Within a tier, remove oldest items first

### Example

```
Initial: 4500 tokens (over budget)
  Tier 1: 800 tokens (preserved)
  Tier 2: 1500 tokens
  Tier 3: 1200 tokens
  Tier 4: 1000 tokens

After pruning:
  Tier 1: 800 tokens (preserved)
  Tier 2: 1500 tokens
  Tier 3: 1200 tokens
  Tier 4: 0 tokens (pruned)
Total: 3500 tokens ✓
```

## Performance

### Test Results

From `test_context_manager.py`:

- **Load Time**: < 0.01ms average per tier
- **Context Size**:
  - General conversation: ~200 chars (50 tokens)
  - Sample search: ~9000 chars (2250 tokens)
  - YouTube analysis: ~9800 chars (2450 tokens)
- **Memory**: Negligible overhead
- **Pruning**: Fast (<1ms)

### Optimization Tips

1. **Adjust tier budgets** in config for your use case
2. **Reduce max_examples** in heuristics for faster loading
3. **Disable optional tiers** for simple conversations
4. **Use task_type_override** to skip detection

## Testing

Run the test suite:

```bash
python test_context_manager.py
```

Tests cover:
- ✓ Basic context loading
- ✓ Sample search context
- ✓ YouTube analysis context
- ✓ Metrics collection
- ✓ Backwards compatibility API

## Migration from ConversationContext

The `IntelligentContextManager` is a drop-in replacement:

**Old Code:**
```python
from sp404_chat import ConversationContext

context = ConversationContext()
context.add_exchange(user_input, response)
context_string = context.get_context_string()
```

**New Code:**
```python
from src.context import IntelligentContextManager

context = IntelligentContextManager()
context.add_exchange(user_input, response)
context_string = context.build_context(user_input)  # Much smarter!
```

The new manager provides:
- ✓ Same API (backwards compatible)
- ✓ Intelligent tier loading
- ✓ Token budget management
- ✓ Performance metrics
- ✓ Task-aware context

## Examples

### Example 1: Sample Search

```python
manager = IntelligentContextManager()

# User: "I need some Dilla-style drums"
context = manager.build_context("I need some Dilla-style drums")

# Automatically loads:
# - Tier 1: Current request
# - Tier 2: Empty (no samples yet)
# - Tier 3: search_intent_detection + query_generation heuristics
# - Tier 4: search_query_generation_protocol + good_examples

# Context contains ~9000 chars of relevant information
# ready for the LLM to generate great search queries
```

### Example 2: Conversation with History

```python
manager = IntelligentContextManager()

# First exchange
manager.add_exchange("What's boom bap?", "Boom bap is...")

# Second exchange - context includes history
context = manager.build_context("Find me some boom bap samples")

# Tier 1 includes:
# - Current request: "Find me some boom bap samples"
# - Previous exchange about boom bap
# - Task status

# Tiers 2-4 load search-specific content
```

### Example 3: YouTube Analysis

```python
manager = IntelligentContextManager()

# Detects YouTube URL automatically
url = "https://youtube.com/watch?v=abc123"
context = manager.build_context(url)

# Loads:
# - Tier 1: URL request
# - Tier 2: timestamp_extractor tool docs
# - Tier 3: Optional (not needed)
# - Tier 4: Optional (not needed)

# Compact, focused context for YouTube analysis
```

## New CLI Command

Added `/metrics` command to sp404_chat.py:

```
You: /metrics

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric            ┃ Value  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total Tokens      │ 2150   │
│   tier1           │ 850    │
│   tier2           │ 1300   │
│                   │        │
│ Total Requests    │ 5      │
│ Avg Load Time     │ 0.02ms │
│                   │        │
│ Pruning Events    │ 0      │
│ Pruning Rate      │ 0.0%   │
└───────────────────┴────────┘
```

## Future Enhancements

Potential improvements (not implemented):

1. **Semantic Similarity**: Use embeddings to find most relevant examples
2. **Dynamic Token Budgets**: Adjust based on LLM model
3. **Context Caching**: Cache loaded tiers for repeated tasks
4. **Smart Prefetching**: Load likely-needed tiers in advance
5. **A/B Testing**: Compare context strategies

## Credits

Implemented as **Priority 4** of the LLM Agent Development Philosophy integration.

**Related Components:**
- Priority 1: Thinking Protocols (`.claude/thinking_protocols/`)
- Priority 2: Tool Documentation (`.claude/tools/`)
- Priority 3: Heuristics Library (`.claude/heuristics/`)
- Priority 6: Example Libraries (`.claude/examples/`)

---

**Status:** Production Ready ✅
**Date:** 2025-01-29
**Total Lines:** ~1,200 (core modules + tests)
