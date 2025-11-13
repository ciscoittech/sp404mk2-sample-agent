#!/usr/bin/env python3
"""
Simple test of pattern selection core logic without full dependencies.

Tests the pattern selector decision tree and metrics without requiring full agent imports.
"""

import json
from pathlib import Path


def test_pattern_config():
    """Test that pattern config exists and is valid."""
    print("=== Test 1: Pattern Config ===")

    config_path = Path(".claude/patterns/pattern_config.json")

    assert config_path.exists(), f"Config not found at {config_path}"
    print(f"✓ Config file exists: {config_path}")

    with open(config_path) as f:
        config = json.load(f)

    # Check required sections
    assert "patterns" in config, "Missing 'patterns' section"
    assert "decision_tree" in config, "Missing 'decision_tree' section"
    assert "task_pattern_mapping" in config, "Missing 'task_pattern_mapping' section"
    print(f"✓ Config has all required sections")

    # Check patterns
    patterns = config["patterns"]
    required_patterns = ["single_call", "routing", "prompt_chain", "parallel"]

    for pattern in required_patterns:
        assert pattern in patterns, f"Missing pattern: {pattern}"
        print(f"✓ Pattern defined: {pattern}")

    # Check task mappings
    mappings = config["task_pattern_mapping"]
    expected_mappings = ["youtube_url_analysis", "sample_search", "vibe_analysis"]

    for mapping in expected_mappings:
        assert mapping in mappings, f"Missing mapping: {mapping}"
        print(f"✓ Task mapping defined: {mapping}")

    print("\n✓ Pattern config test passed!\n")


def test_pattern_modules_exist():
    """Test that all pattern modules exist."""
    print("=== Test 2: Pattern Modules ===")

    pattern_dir = Path("src/agents/patterns")
    assert pattern_dir.exists(), f"Pattern directory not found: {pattern_dir}"
    print(f"✓ Pattern directory exists: {pattern_dir}")

    required_modules = [
        "pattern_selector.py",
        "routing_pattern.py",
        "prompt_chain_pattern.py",
        "parallel_pattern.py",
        "pattern_metrics.py"
    ]

    for module in required_modules:
        module_path = pattern_dir / module
        assert module_path.exists(), f"Module not found: {module_path}"
        print(f"✓ Module exists: {module}")

    print("\n✓ Pattern modules test passed!\n")


def test_pattern_logic():
    """Test basic pattern selection logic without imports."""
    print("=== Test 3: Pattern Selection Logic ===")

    # Load config
    config_path = Path(".claude/patterns/pattern_config.json")
    with open(config_path) as f:
        config = json.load(f)

    # Test 1: YouTube URL should map to routing
    task_mapping = config["task_pattern_mapping"]["youtube_url_analysis"]
    assert task_mapping["pattern"] == "routing", "YouTube URL should route"
    assert task_mapping["route_to"] == "timestamp_extractor", "Should route to timestamp_extractor"
    print("✓ YouTube URL → routing → timestamp_extractor")

    # Test 2: Sample search should map to routing
    task_mapping = config["task_pattern_mapping"]["sample_search"]
    assert task_mapping["pattern"] == "routing", "Sample search should route"
    assert task_mapping["route_to"] == "youtube_search", "Should route to youtube_search"
    print("✓ Sample search → routing → youtube_search")

    # Test 3: Vibe analysis should be single call
    task_mapping = config["task_pattern_mapping"]["vibe_analysis"]
    assert task_mapping["pattern"] == "single_call", "Vibe analysis should be single call"
    print("✓ Vibe analysis → single_call")

    # Test 4: Check decision tree exists
    decision_tree = config["decision_tree"]
    assert "step1_check_tools" in decision_tree, "Missing decision tree step 1"
    assert "step2_check_complexity" in decision_tree, "Missing decision tree step 2"
    print("✓ Decision tree has required steps")

    print("\n✓ Pattern selection logic test passed!\n")


def test_file_structure():
    """Test that all required files exist."""
    print("=== Test 4: File Structure ===")

    required_files = [
        ".claude/patterns/pattern_config.json",
        "src/agents/patterns/__init__.py",
        "src/agents/patterns/pattern_selector.py",
        "src/agents/patterns/routing_pattern.py",
        "src/agents/patterns/prompt_chain_pattern.py",
        "src/agents/patterns/parallel_pattern.py",
        "src/agents/patterns/pattern_metrics.py"
    ]

    for filepath in required_files:
        path = Path(filepath)
        assert path.exists(), f"File not found: {filepath}"
        print(f"✓ File exists: {filepath}")

    print("\n✓ File structure test passed!\n")


def test_code_quality():
    """Test basic code quality of pattern modules."""
    print("=== Test 5: Code Quality ===")

    pattern_files = [
        "src/agents/patterns/pattern_selector.py",
        "src/agents/patterns/routing_pattern.py",
        "src/agents/patterns/prompt_chain_pattern.py",
        "src/agents/patterns/parallel_pattern.py",
        "src/agents/patterns/pattern_metrics.py"
    ]

    for filepath in pattern_files:
        with open(filepath) as f:
            content = f.read()

        # Check for docstrings
        assert '"""' in content, f"{filepath} missing docstrings"

        # Check for type hints
        assert " -> " in content, f"{filepath} missing return type hints"

        # Check for async support (except selector and metrics)
        if "pattern" in filepath and "selector" not in filepath and "metrics" not in filepath:
            assert "async def" in content, f"{filepath} should have async methods"

        print(f"✓ {Path(filepath).name}: docstrings ✓, type hints ✓")

    print("\n✓ Code quality test passed!\n")


def run_all_tests():
    """Run all simple tests."""
    print("\n" + "="*60)
    print("PATTERN SELECTION SIMPLE TEST SUITE")
    print("="*60 + "\n")

    try:
        test_pattern_config()
        test_pattern_modules_exist()
        test_pattern_logic()
        test_file_structure()
        test_code_quality()

        print("="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")

        print("Note: Full integration tests require dependencies.")
        print("Run 'python test_pattern_selection.py' after installing dependencies.\n")

        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
