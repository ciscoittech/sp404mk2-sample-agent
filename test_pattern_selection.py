#!/usr/bin/env python3
"""
Test suite for pattern selection system.

Tests pattern selector, routing, prompt chain, and parallel patterns.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.patterns.pattern_selector import PatternSelector, PatternType
from src.agents.patterns.routing_pattern import RoutingPattern
from src.agents.patterns.prompt_chain_pattern import PromptChainPattern
from src.agents.patterns.parallel_pattern import ParallelPattern
from src.agents.patterns.pattern_metrics import PatternMetrics


# Test handlers
async def mock_youtube_search(user_input: str, context: dict):
    """Mock YouTube search handler."""
    return {"results": ["video1", "video2"], "query": user_input}


async def mock_timestamp_extractor(user_input: str, context: dict):
    """Mock timestamp extractor handler."""
    return {"timestamps": ["0:00", "1:30"], "url": user_input}


async def mock_vibe_analysis(user_input: str, context: dict):
    """Mock vibe analysis handler."""
    return {"mood": ["chill", "groovy"], "sample": user_input}


# Prompt chain handlers
async def step1_generate_queries(user_input: str, context: dict, results: dict):
    """Generate search queries."""
    return ["boom bap drums", "90 BPM samples"]


async def step2_search(user_input: str, context: dict, results: dict):
    """Execute search."""
    queries = results.get("generate_queries", [])
    return {"results": [f"result_for_{q}" for q in queries]}


async def step3_filter(user_input: str, context: dict, results: dict):
    """Filter results."""
    search_results = results.get("search", {}).get("results", [])
    return [r for r in search_results if "90" in r or "boom" in r]


# Parallel task handlers
async def task1_search_youtube(user_input: str, context: dict):
    """Search YouTube."""
    await asyncio.sleep(0.01)  # Simulate work
    return {"platform": "youtube", "count": 5}


async def task2_search_soundcloud(user_input: str, context: dict):
    """Search SoundCloud."""
    await asyncio.sleep(0.01)  # Simulate work
    return {"platform": "soundcloud", "count": 3}


async def task3_search_bandcamp(user_input: str, context: dict):
    """Search Bandcamp."""
    await asyncio.sleep(0.01)  # Simulate work
    return {"platform": "bandcamp", "count": 4}


def test_pattern_selector():
    """Test pattern selector decision making."""
    print("=== Test 1: Pattern Selector ===")

    selector = PatternSelector()

    # Test 1: YouTube URL routing
    decision = selector.select_pattern("https://youtube.com/watch?v=abc123")
    assert decision.pattern == PatternType.ROUTING, f"Expected ROUTING, got {decision.pattern}"
    assert decision.route_to == "timestamp_extractor", f"Expected timestamp_extractor, got {decision.route_to}"
    print(f"✓ YouTube URL → {decision.pattern.value} (routes to {decision.route_to})")

    # Test 2: Sample search routing
    decision = selector.select_pattern("Find me some boom bap samples")
    assert decision.pattern == PatternType.ROUTING, f"Expected ROUTING, got {decision.pattern}"
    assert decision.route_to == "youtube_search", f"Expected youtube_search, got {decision.route_to}"
    print(f"✓ Sample search → {decision.pattern.value} (routes to {decision.route_to})")

    # Test 3: Simple question
    decision = selector.select_pattern("What is boom bap?")
    assert decision.pattern == PatternType.SINGLE_CALL, f"Expected SINGLE_CALL, got {decision.pattern}"
    print(f"✓ Simple question → {decision.pattern.value}")

    # Test 4: Sequential workflow
    decision = selector.select_pattern("Find samples and then download the best ones")
    assert decision.pattern in [PatternType.PROMPT_CHAIN, PatternType.ROUTING], f"Expected PROMPT_CHAIN or ROUTING, got {decision.pattern}"
    print(f"✓ Sequential workflow → {decision.pattern.value}")

    # Test 5: Explicit task type mapping
    decision = selector.select_pattern(
        "Analyze this sample",
        task_type="vibe_analysis"
    )
    assert decision.pattern == PatternType.SINGLE_CALL, f"Expected SINGLE_CALL, got {decision.pattern}"
    print(f"✓ Vibe analysis (mapped) → {decision.pattern.value}")

    print("\n✓ Pattern selector test passed!\n")


async def test_routing_pattern():
    """Test routing pattern execution."""
    print("=== Test 2: Routing Pattern ===")

    router = RoutingPattern()

    # Register routes
    router.register_route("youtube_search", mock_youtube_search)
    router.register_route("timestamp_extractor", mock_timestamp_extractor)

    # Test 1: Route to YouTube search
    result = await router.execute("youtube_search", "boom bap samples")
    assert result.success, f"Routing failed: {result.error}"
    assert "results" in result.result, "Missing results in output"
    print(f"✓ Routed to youtube_search: {len(result.result['results'])} results")

    # Test 2: Route to timestamp extractor
    result = await router.execute("timestamp_extractor", "https://youtube.com/watch?v=abc")
    assert result.success, f"Routing failed: {result.error}"
    assert "timestamps" in result.result, "Missing timestamps in output"
    print(f"✓ Routed to timestamp_extractor: {len(result.result['timestamps'])} timestamps")

    # Test 3: Invalid route
    result = await router.execute("invalid_route", "test")
    assert not result.success, "Should have failed for invalid route"
    assert "not found" in result.error.lower(), "Wrong error message"
    print(f"✓ Invalid route handled: {result.error[:50]}...")

    print("\n✓ Routing pattern test passed!\n")


async def test_prompt_chain_pattern():
    """Test prompt chain pattern execution."""
    print("=== Test 3: Prompt Chain Pattern ===")

    chain = PromptChainPattern()

    # Build chain
    chain.add_step("generate_queries", step1_generate_queries, "Generate search queries")
    chain.add_step("search", step2_search, "Execute search")
    chain.add_step("filter", step3_filter, "Filter results")

    # Execute chain
    result = await chain.execute("I need boom bap samples")

    assert result.success, f"Chain failed with errors: {result.errors}"
    assert result.steps_completed == 3, f"Expected 3 steps, completed {result.steps_completed}"
    print(f"✓ Chain executed: {result.steps_completed}/{result.steps_total} steps")

    # Check results
    assert "generate_queries" in result.results, "Missing step 1 results"
    assert "search" in result.results, "Missing step 2 results"
    assert "filter" in result.results, "Missing step 3 results"

    print(f"✓ Step 1 (queries): {result.results['generate_queries']}")
    print(f"✓ Step 2 (search): {len(result.results['search']['results'])} results")
    print(f"✓ Step 3 (filter): {len(result.results['filter'])} filtered")

    print("\n✓ Prompt chain pattern test passed!\n")


async def test_parallel_pattern():
    """Test parallel pattern execution."""
    print("=== Test 4: Parallel Pattern ===")

    parallel = ParallelPattern(max_concurrent=3)

    # Add tasks
    parallel.add_task("youtube", task1_search_youtube, "Search YouTube")
    parallel.add_task("soundcloud", task2_search_soundcloud, "Search SoundCloud")
    parallel.add_task("bandcamp", task3_search_bandcamp, "Search Bandcamp")

    # Execute in parallel
    result = await parallel.execute("boom bap samples")

    assert result.success, f"Parallel execution failed with errors: {result.errors}"
    assert result.tasks_completed == 3, f"Expected 3 tasks, completed {result.tasks_completed}"
    print(f"✓ Parallel execution: {result.tasks_completed}/{result.tasks_total} tasks")
    print(f"✓ Total latency: {result.total_latency_ms:.2f}ms")

    # Check results
    assert "youtube" in result.results, "Missing YouTube results"
    assert "soundcloud" in result.results, "Missing SoundCloud results"
    assert "bandcamp" in result.results, "Missing Bandcamp results"

    total_samples = sum(r["count"] for r in result.results.values())
    print(f"✓ Total samples found: {total_samples}")

    # Verify parallelization benefit
    # If sequential, would be ~30ms (3 * 10ms), parallel should be ~10-15ms
    assert result.total_latency_ms < 25, f"Parallel execution too slow: {result.total_latency_ms}ms"
    print(f"✓ Parallelization benefit confirmed")

    print("\n✓ Parallel pattern test passed!\n")


def test_pattern_metrics():
    """Test pattern metrics tracking."""
    print("=== Test 5: Pattern Metrics ===")

    metrics = PatternMetrics()

    # Record some pattern selections
    metrics.record_pattern_selection("routing", "youtube_url_analysis")
    metrics.record_pattern_selection("routing", "sample_search")
    metrics.record_pattern_selection("single_call", "vibe_analysis")

    # Record executions
    metrics.record_execution("routing", "youtube_url_analysis", 10.5, True)
    metrics.record_execution("routing", "sample_search", 15.2, True)
    metrics.record_execution("single_call", "vibe_analysis", 5.3, True)
    metrics.record_execution("prompt_chain", "workflow", 50.0, False, "Validation failed")

    # Get stats
    summary = metrics.get_summary()

    assert summary["total_executions"] == 4, f"Expected 4 executions, got {summary['total_executions']}"
    print(f"✓ Total executions: {summary['total_executions']}")

    # Check routing stats
    routing_stats = metrics.get_pattern_stats("routing")
    assert routing_stats["success_rate"] == 100.0, f"Expected 100% success, got {routing_stats['success_rate']}%"
    print(f"✓ Routing pattern: {routing_stats['usage_count']} uses, {routing_stats['success_rate']}% success")

    # Check most used
    most_used = metrics.get_most_used_pattern()
    assert most_used == "routing", f"Expected 'routing', got '{most_used}'"
    print(f"✓ Most used pattern: {most_used}")

    # Check fastest
    fastest = metrics.get_fastest_pattern()
    assert fastest == "single_call", f"Expected 'single_call', got '{fastest}'"
    print(f"✓ Fastest pattern: {fastest}")

    print("\n✓ Pattern metrics test passed!\n")


async def test_integration():
    """Test integration between components."""
    print("=== Test 6: Integration Test ===")

    selector = PatternSelector()
    router = RoutingPattern()
    metrics = PatternMetrics()

    # Register routes
    router.register_route("youtube_search", mock_youtube_search)

    # Workflow: Select pattern → Execute → Track metrics
    user_input = "Find boom bap samples"

    # 1. Select pattern
    decision = selector.select_pattern(user_input)
    metrics.record_pattern_selection(decision.pattern.value, "sample_search")
    print(f"✓ Pattern selected: {decision.pattern.value}")

    # 2. Execute
    import time
    start = time.time()

    if decision.pattern == PatternType.ROUTING:
        result = await router.execute(decision.route_to, user_input)
        success = result.success
    else:
        success = True  # Mock other patterns

    latency_ms = (time.time() - start) * 1000

    # 3. Track metrics
    metrics.record_execution(decision.pattern.value, "sample_search", latency_ms, success)
    print(f"✓ Execution tracked: {latency_ms:.2f}ms, success={success}")

    # 4. Get stats
    stats = metrics.get_pattern_stats(decision.pattern.value)
    print(f"✓ Pattern stats: {stats}")

    print("\n✓ Integration test passed!\n")


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("PATTERN SELECTION TEST SUITE")
    print("="*60 + "\n")

    try:
        # Sync tests
        test_pattern_selector()
        test_pattern_metrics()

        # Async tests
        await test_routing_pattern()
        await test_prompt_chain_pattern()
        await test_parallel_pattern()
        await test_integration()

        print("="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")

        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
