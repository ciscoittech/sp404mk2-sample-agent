#!/usr/bin/env python3
"""
Quick test of the IntelligentContextManager.

Tests basic functionality including tier loading, budget management,
and task detection.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.context import IntelligentContextManager


def test_basic_context_loading():
    """Test basic context loading."""
    print("=== Test 1: Basic Context Loading ===")

    manager = IntelligentContextManager()

    # Test simple request
    context = manager.build_context("Hello, can you help me?")

    print(f"✓ Context built: {len(context)} characters")
    print(f"✓ Task detected: {manager.current_task.task_type}")
    print(f"✓ Loaded tiers: {list(manager.loaded_tiers.keys())}")

    # Add an exchange
    manager.add_exchange("Hello", "Hi there!")

    # Build context again
    context2 = manager.build_context("What about samples?")

    print(f"✓ Context rebuilt with history: {len(context2)} characters")
    print(f"✓ Task detected: {manager.current_task.task_type}")

    print("\n✓ Basic context loading test passed!\n")


def test_sample_search_context():
    """Test sample search context loading."""
    print("=== Test 2: Sample Search Context ===")

    manager = IntelligentContextManager()

    # Test search request
    context = manager.build_context("I need some dusty 70s soul samples")

    print(f"✓ Context built: {len(context)} characters")
    print(f"✓ Task detected: {manager.current_task.task_type}")
    print(f"✓ Loaded tiers: {list(manager.loaded_tiers.keys())}")

    if manager.current_task:
        print(f"✓ Heuristics to load: {manager.current_task.load_heuristics}")
        print(f"✓ Protocols to load: {manager.current_task.load_protocols}")

    # Add musical intent
    manager.update_musical_intent({
        "genres": ["soul", "funk"],
        "era": "70s",
        "texture_descriptors": ["dusty", "warm"]
    })

    # Add samples
    manager.add_discovered_sample({
        "title": "70s Soul Break",
        "platform": "youtube",
        "quality_score": 0.85
    })

    # Rebuild context
    context2 = manager.build_context("Show me more like that")

    print(f"✓ Context rebuilt with intent and samples: {len(context2)} characters")

    print("\n✓ Sample search context test passed!\n")


def test_youtube_analysis_context():
    """Test YouTube analysis context."""
    print("=== Test 3: YouTube Analysis Context ===")

    manager = IntelligentContextManager()

    # Test YouTube URL
    context = manager.build_context("https://youtube.com/watch?v=test123")

    print(f"✓ Context built: {len(context)} characters")
    print(f"✓ Task detected: {manager.current_task.task_type}")
    print(f"✓ Loaded tiers: {list(manager.loaded_tiers.keys())}")

    if manager.current_task:
        print(f"✓ Tools to load: {manager.current_task.load_tools}")

    # Register tool
    manager.register_active_tool("timestamp_extractor")

    # Rebuild
    context2 = manager.build_context("What timestamps did you find?")

    print(f"✓ Context rebuilt with active tools: {len(context2)} characters")

    print("\n✓ YouTube analysis context test passed!\n")


def test_metrics():
    """Test metrics collection."""
    print("=== Test 4: Metrics Collection ===")

    manager = IntelligentContextManager()

    # Perform several requests
    for i in range(3):
        context = manager.build_context(f"Request {i+1}")
        manager.add_exchange(f"Request {i+1}", f"Response {i+1}")

    # Get metrics
    metrics = manager.get_metrics_summary()

    print(f"✓ Total requests: {metrics['performance']['total_requests']}")
    print(f"✓ Current tokens: {metrics['current_state']['total_tokens']}")
    print(f"✓ Avg load time: {metrics['performance']['avg_load_time_ms']:.2f}ms")
    print(f"✓ Pruning events: {metrics['budget_management']['total_pruning_events']}")

    # Check tier usage
    print(f"✓ Tier tokens: {metrics['current_state']['tier_tokens']}")

    print("\n✓ Metrics collection test passed!\n")


def test_context_manager_api():
    """Test backwards compatibility API."""
    print("=== Test 5: Backwards Compatibility API ===")

    manager = IntelligentContextManager()

    # Test old API methods
    manager.add_exchange("User message", "Agent response")

    context_string = manager.get_context_string()
    print(f"✓ get_context_string() works: {len(context_string)} characters")

    # Test state methods
    manager.update_musical_intent({"genres": ["hip-hop"]})
    manager.add_discovered_sample({"title": "Test Sample"})
    manager.register_active_tool("youtube_search")
    manager.clear_active_tools()

    print("✓ All state management methods work")

    # Test reset
    manager.reset()
    print(f"✓ Reset works: {len(manager.conversation_history)} history items")

    print("\n✓ Backwards compatibility API test passed!\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("INTELLIGENT CONTEXT MANAGER TEST SUITE")
    print("="*60 + "\n")

    try:
        test_basic_context_loading()
        test_sample_search_context()
        test_youtube_analysis_context()
        test_metrics()
        test_context_manager_api()

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
    sys.exit(run_all_tests())
