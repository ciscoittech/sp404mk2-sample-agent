# Agent Pattern Selection

**Status:** ✅ Complete (Priority 5)
**Location:** `src/agents/patterns/`

## Overview

Intelligent pattern selection system that chooses the optimal execution strategy based on task characteristics. Implements five execution patterns from simple single calls to complex orchestrated workflows.

## The Five Patterns

### 1. Single Call 💬
**Best for:** Simple, well-defined tasks with available examples

**When to use:**
- Request has clear examples to follow
- Task is straightforward (question, classification, generation)
- No tool execution needed
- Context is sufficient for decision

**Examples:**
- "What is boom bap?" → Answer with definition
- "Generate search queries for J Dilla style" → Use examples + protocol
- "Classify this sample genre" → Use examples

**Cost:** Low | **Latency:** Low

### 2. Routing 🎯
**Best for:** Direct tool/agent mapping

**When to use:**
- Request maps directly to a specific tool
- Tool has clear trigger keywords
- Single tool can handle entire request
- No coordination between tools needed

**Examples:**
- YouTube URL → timestamp_extractor
- "Find samples" → youtube_search
- "Analyze vibe" → vibe_analysis_agent

**Cost:** Low | **Latency:** Low

### 3. Prompt Chain ⛓️
**Best for:** Sequential execution with dependencies

**When to use:**
- Task has multiple sequential steps
- Later steps depend on earlier results
- Need validation between steps
- Complex workflow with decision points

**Examples:**
- Search → Filter → Download workflow
- Analyze → Classify → Recommend pipeline
- Extract → Validate → Process sequence

**Cost:** Medium | **Latency:** Medium

### 4. Parallel ⚡
**Best for:** Concurrent independent operations

**When to use:**
- Multiple independent subtasks (3+)
- No dependencies between tasks
- Results can be aggregated after completion
- Time-sensitive operations

**Examples:**
- Search multiple platforms simultaneously
- Analyze multiple samples concurrently
- Generate multiple query variations at once

**Cost:** High | **Latency:** Low (faster than sequential)

### 5. Orchestrator-Workers 🎼
**Best for:** Complex coordinated workflows

**When to use:**
- Very complex multi-step workflow
- Need coordination and replanning
- Multiple specialized agents involved
- Requires dynamic decision making

**Examples:**
- Full sample collection workflow (search, analyze, filter, organize)
- Complex multi-source aggregation
- Adaptive sampling strategy

**Cost:** Very High | **Latency:** High

## Decision Tree

The pattern selector uses a 5-step decision tree:

```
1. Check Tools
   ├─ Maps to single tool? → ROUTING
   └─ No → Continue

2. Check Complexity
   ├─ Simple with examples? → SINGLE CALL
   └─ No → Continue

3. Check Dependencies
   ├─ Sequential dependencies? → PROMPT CHAIN
   └─ No → Continue

4. Check Count
   ├─ 3+ independent tasks? → PARALLEL
   └─ No → Continue

5. Check Orchestration
   ├─ Complex coordination? → ORCHESTRATOR-WORKERS
   └─ No → PROMPT CHAIN (fallback)
```

## Quick Start

### Basic Pattern Selection

```python
from src.agents.patterns import PatternSelector

selector = PatternSelector()

# Automatic selection
decision = selector.select_pattern("Find me boom bap samples")

print(f"Pattern: {decision.pattern.value}")
print(f"Reasoning: {decision.reasoning}")
# Pattern: routing
# Reasoning: Request matches tool trigger: youtube_search
```

### Explicit Task Type

```python
# Use explicit task type for known workflows
decision = selector.select_pattern(
    "Analyze this sample",
    task_type="vibe_analysis"
)

print(f"Pattern: {decision.pattern.value}")
# Pattern: single_call
```

### Routing Pattern

```python
from src.agents.patterns import RoutingPattern

router = RoutingPattern()

# Register routes
router.register_route("youtube_search", search_handler)
router.register_route("timestamp_extractor", extract_handler)

# Execute
result = await router.execute("youtube_search", "boom bap samples")

if result.success:
    print(f"Results: {result.result}")
```

### Prompt Chain Pattern

```python
from src.agents.patterns import PromptChainPattern

chain = PromptChainPattern()

# Build chain
chain.add_step("generate_queries", query_handler, "Generate search queries")
chain.add_step("search", search_handler, "Execute search")
chain.add_step("filter", filter_handler, "Filter results", gate=quality_gate)

# Execute
result = await chain.execute("I need 90 BPM samples")

if result.success:
    print(f"Completed {result.steps_completed}/{result.steps_total} steps")
    print(f"Final result: {result.final_result}")
```

### Parallel Pattern

```python
from src.agents.patterns import ParallelPattern

parallel = ParallelPattern(max_concurrent=3)

# Add tasks
parallel.add_task("youtube", youtube_handler, "Search YouTube")
parallel.add_task("soundcloud", soundcloud_handler, "Search SoundCloud")
parallel.add_task("bandcamp", bandcamp_handler, "Search Bandcamp")

# Execute all concurrently
result = await parallel.execute("boom bap samples")

print(f"Completed: {result.tasks_completed}/{result.tasks_total}")
print(f"Latency: {result.total_latency_ms:.2f}ms")
print(f"Results: {result.results}")
```

### Pattern Metrics

```python
from src.agents.patterns import PatternMetrics

metrics = PatternMetrics()

# Record selections
metrics.record_pattern_selection("routing", "sample_search")

# Record executions
metrics.record_execution("routing", "sample_search", 15.2, True)

# Get stats
summary = metrics.get_summary()
print(f"Total executions: {summary['total_executions']}")

# Get pattern stats
stats = metrics.get_pattern_stats("routing")
print(f"Success rate: {stats['success_rate']}%")
print(f"Avg latency: {stats['avg_latency_ms']}ms")
```

## Configuration

Pattern behavior is configured in `.claude/patterns/pattern_config.json`:

```json
{
  "patterns": {
    "single_call": {
      "description": "Simple single LLM call with examples",
      "when_to_use": ["Clear examples", "Well-defined task"],
      "cost": "low",
      "latency": "low"
    }
  },

  "task_pattern_mapping": {
    "youtube_url_analysis": {
      "pattern": "routing",
      "route_to": "timestamp_extractor"
    },
    "sample_search": {
      "pattern": "routing",
      "route_to": "youtube_search"
    }
  }
}
```

## Architecture

### Core Components

```
PatternSelector
├── Analyzes user input
├── Applies decision tree
├── Returns PatternDecision
└── Uses pattern_config.json

RoutingPattern
├── Registers route handlers
├── Maps input → handler
└── Executes single tool

PromptChainPattern
├── Manages sequential steps
├── Validates between steps
├── Handles failures
└── Returns ChainResult

ParallelPattern
├── Executes tasks concurrently
├── Controls concurrency (semaphore)
├── Aggregates results
└── Returns ParallelResult

PatternMetrics
├── Tracks pattern usage
├── Monitors success rates
├── Measures latency
└── Exports metrics
```

### Key Classes

**PatternSelector**
- `select_pattern(user_input, task_type, context)` → PatternDecision
- `should_use_pattern(pattern, characteristics)` → bool
- `get_pattern_info(pattern)` → Dict

**PatternDecision**
- `pattern`: PatternType enum
- `reasoning`: str (why this pattern)
- `route_to`: Optional[str] (for routing)
- `steps`: Optional[List] (for chains)
- `confidence`: float

**RoutingPattern**
- `register_route(name, handler)` → None
- `execute(route_name, input, context)` → RoutingResult
- `has_route(name)` → bool

**PromptChainPattern**
- `add_step(name, handler, gate, required)` → self
- `execute(input, context)` → ChainResult
- `get_step_status()` → List[Dict]

**ParallelPattern**
- `add_task(name, handler)` → self
- `execute(input, context)` → ParallelResult
- `get_task_status()` → List[Dict]

**PatternMetrics**
- `record_pattern_selection(pattern, task)` → None
- `record_execution(pattern, task, latency, success)` → None
- `get_pattern_stats(pattern)` → Dict
- `get_summary()` → Dict

## Usage Patterns

### Pattern Selection + Execution

```python
selector = PatternSelector()
router = RoutingPattern()
metrics = PatternMetrics()

# Register routes
router.register_route("youtube_search", search_handler)

# Workflow
user_input = "Find boom bap samples"

# 1. Select pattern
decision = selector.select_pattern(user_input)
metrics.record_pattern_selection(decision.pattern.value, "sample_search")

# 2. Execute
if decision.pattern == PatternType.ROUTING:
    result = await router.execute(decision.route_to, user_input)
    success = result.success
elif decision.pattern == PatternType.SINGLE_CALL:
    # Call LLM directly with examples
    pass

# 3. Track metrics
metrics.record_execution(decision.pattern.value, "sample_search", latency_ms, success)
```

### Building Complex Chains

```python
chain = PromptChainPattern()

# Add steps with validation
chain.add_step(
    "generate_queries",
    query_handler,
    description="Generate optimized queries",
    gate=lambda result, ctx: len(result) >= 3,  # Must generate 3+ queries
    required=True
)

chain.add_step(
    "search",
    search_handler,
    description="Execute searches",
    gate=lambda result, ctx: len(result.get("results", [])) > 0,  # Must find results
    required=True
)

chain.add_step(
    "assess_quality",
    quality_handler,
    description="Assess result quality",
    required=False  # Optional step
)

result = await chain.execute(user_input)
```

### Parallel with Aggregation

```python
parallel = ParallelPattern(max_concurrent=5)

# Add multiple search tasks
for platform in ["youtube", "soundcloud", "bandcamp", "freesound"]:
    parallel.add_task(platform, get_search_handler(platform))

result = await parallel.execute("drum samples")

# Aggregate results
all_samples = []
for platform, results in result.results.items():
    all_samples.extend(results)

print(f"Found {len(all_samples)} samples across {len(result.results)} platforms")
print(f"Total time: {result.total_latency_ms:.2f}ms")
```

## Performance

### Pattern Selection Overhead

- **Decision making:** < 1ms
- **Config loading:** One-time at initialization
- **Cache friendly:** No heavy computation

### Execution Performance

**Single Call:**
- Latency: LLM response time (~500-2000ms)
- Cost: 1 LLM call

**Routing:**
- Latency: Tool execution time (varies)
- Cost: Tool-specific

**Prompt Chain (3 steps):**
- Latency: Sum of steps (~1500-5000ms)
- Cost: Multiple calls/tools

**Parallel (3 tasks):**
- Latency: Max of tasks (~500-2000ms, much faster than sequential)
- Cost: Multiple concurrent calls

## Testing

Run tests:

```bash
# Simple tests (no dependencies)
python test_pattern_selection_simple.py

# Full tests (requires dependencies)
python test_pattern_selection.py
```

Test coverage:
- ✓ Pattern selector decision tree
- ✓ Routing pattern execution
- ✓ Prompt chain with validation gates
- ✓ Parallel execution with concurrency control
- ✓ Pattern metrics tracking
- ✓ Integration between components

## Best Practices

### 1. Prefer Simple Patterns

```python
# Good: Use routing for direct tool mapping
if "youtube.com" in user_input:
    decision = PatternDecision(pattern=PatternType.ROUTING, route_to="timestamp_extractor")

# Bad: Use orchestrator for simple task
# Unnecessary complexity and cost
```

### 2. Use Validation Gates

```python
# Good: Validate critical steps
chain.add_step(
    "search",
    handler,
    gate=lambda result, ctx: len(result) > 0  # Ensure results exist
)

# Bad: No validation, failures propagate
chain.add_step("search", handler)  # Might continue with empty results
```

### 3. Limit Parallelization

```python
# Good: Reasonable concurrency limit
parallel = ParallelPattern(max_concurrent=5)

# Bad: Unlimited concurrency
parallel = ParallelPattern(max_concurrent=100)  # Can overwhelm system
```

### 4. Track Metrics

```python
# Good: Track all pattern usage
metrics.record_pattern_selection(pattern, task_type)
metrics.record_execution(pattern, task_type, latency, success)

# Bad: No tracking, can't optimize
# Just execute patterns without metrics
```

### 5. Use Explicit Task Types for Known Workflows

```python
# Good: Explicit task type for known patterns
decision = selector.select_pattern(url, task_type="youtube_url_analysis")

# Ok but slower: Let selector detect
decision = selector.select_pattern(url)  # Works but does more analysis
```

## Examples

See `/test_pattern_selection.py` for complete working examples of:
- Pattern selection for various inputs
- Routing to different tools
- Building and executing prompt chains
- Parallel execution with aggregation
- Metrics tracking and reporting

## Integration

Pattern selection integrates with:
- **Context Manager** (Priority 4): Loads relevant context per pattern
- **Heuristics** (Priority 3): Uses heuristics for decision making
- **Tool Documentation** (Priority 2): Routes to documented tools
- **Thinking Protocols** (Priority 1): Single calls use protocols

## Future Enhancements

Potential improvements (not implemented):

1. **ML-Based Selection**: Learn optimal patterns from historical data
2. **Cost Optimization**: Choose patterns based on budget constraints
3. **Adaptive Chains**: Dynamically adjust chain steps based on intermediate results
4. **Pattern Caching**: Cache common pattern selections
5. **Hybrid Patterns**: Combine patterns (e.g., parallel chains)

## Credits

Implemented as **Priority 5** of the LLM Agent Development Philosophy integration.

**Related Components:**
- Priority 1: Thinking Protocols
- Priority 2: Tool Documentation
- Priority 3: Heuristics Library
- Priority 4: Context Management
- Priority 6: Example Libraries

---

**Status:** Production Ready ✅
**Date:** 2025-01-29
**Total Lines:** ~1,400 (core + tests + docs)
