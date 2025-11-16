#!/usr/bin/env python3
"""
Test script for hardware intent detection and routing.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sp404_chat import SP404ChatAgent


def test_hardware_detection():
    """Test hardware intent detection with various queries."""
    agent = SP404ChatAgent()

    test_cases = [
        # Hardware questions (should detect)
        ("How do I resample a pad on the SP-404?", True),
        ("What effects can I use for lo-fi hip-hop?", True),
        ("How can I record a sample?", True),
        ("How to save my project?", True),
        ("What's the button combination for the looper?", True),
        ("How do I create a pattern on the SP404?", True),

        # Non-hardware questions (should not detect)
        ("Find me some 70s soul samples", False),
        ("I need dusty jazz drums", False),
        ("Tell me about boom bap production", False),
        ("What's the weather like?", False),
    ]

    print("Testing Hardware Intent Detection\n" + "=" * 50)

    correct = 0
    total = len(test_cases)

    for query, expected in test_cases:
        detected = agent.detect_hardware_intent(query)
        status = "✓" if detected == expected else "✗"
        result = "PASS" if detected == expected else "FAIL"

        print(f"{status} [{result}] '{query}'")
        print(f"   Expected: {expected}, Got: {detected}")

        if detected == expected:
            correct += 1

            # If hardware detected, show routing
            if detected:
                sections = agent._route_to_manual_sections(query)
                section_names = [s.split('/')[-1] for s in sections]
                print(f"   Routed to: {', '.join(section_names)}")

        print()

    print("=" * 50)
    print(f"Results: {correct}/{total} tests passed ({correct/total*100:.1f}%)")
    print()

    return correct == total


def test_section_routing():
    """Test that routing maps queries to correct manual sections."""
    agent = SP404ChatAgent()

    test_cases = [
        ("How do I resample?", ["sp404-sampling.md"]),
        ("What effects are available?", ["sp404-effects.md"]),
        ("How to create a pattern?", ["sp404-sequencer.md"]),
        ("How do I save my project?", ["sp404-file-mgmt.md"]),
        ("What are the playback modes?", ["sp404-performance.md"]),
    ]

    print("\nTesting Section Routing\n" + "=" * 50)

    correct = 0
    total = len(test_cases)

    for query, expected_files in test_cases:
        sections = agent._route_to_manual_sections(query)
        section_names = [s.split('/')[-1] for s in sections]

        # Check if expected files are in the result
        found_all = all(exp in section_names for exp in expected_files)

        status = "✓" if found_all else "✗"
        result = "PASS" if found_all else "FAIL"

        print(f"{status} [{result}] '{query}'")
        print(f"   Expected: {expected_files}")
        print(f"   Got:      {section_names}")

        if found_all:
            correct += 1

        print()

    print("=" * 50)
    print(f"Results: {correct}/{total} tests passed ({correct/total*100:.1f}%)")
    print()

    return correct == total


if __name__ == "__main__":
    detection_passed = test_hardware_detection()
    routing_passed = test_section_routing()

    if detection_passed and routing_passed:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
