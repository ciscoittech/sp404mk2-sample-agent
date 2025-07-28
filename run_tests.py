#!/usr/bin/env python3
"""
Test runner for SP404MK2 Sample Agent.
Run all tests with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with coverage."""
    
    print("🧪 SP404MK2 Sample Agent - Test Suite")
    print("=" * 60)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"])
        print()
    
    # Run tests with coverage
    print("🔍 Running tests with coverage...\n")
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "-p", "no:warnings",  # Suppress warnings for cleaner output
        "tests/"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated:")
        print("   - Terminal: See above")
        print("   - HTML: htmlcov/index.html")
        print("   - XML: coverage.xml")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    
    return result.returncode


def run_specific_test(test_path):
    """Run a specific test file or directory."""
    
    print(f"🔍 Running tests in: {test_path}\n")
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        test_path
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def run_unit_tests():
    """Run only unit tests."""
    print("🔍 Running unit tests...\n")
    return run_specific_test("tests/unit/")


def run_integration_tests():
    """Run only integration tests."""
    print("🔍 Running integration tests...\n")
    return run_specific_test("tests/integration/")


def run_with_markers(marker):
    """Run tests with specific marker."""
    
    print(f"🔍 Running tests marked with: {marker}\n")
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "-m",
        marker,
        "tests/"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def print_usage():
    """Print usage information."""
    print("""
Usage: python run_tests.py [option]

Options:
    (no option)     Run all tests with coverage
    unit            Run only unit tests
    integration     Run only integration tests
    specific PATH   Run specific test file/directory
    fast            Run only fast tests (exclude slow)
    slow            Run only slow tests
    
Examples:
    python run_tests.py
    python run_tests.py unit
    python run_tests.py specific tests/unit/agents/test_groove_analyst.py
    python run_tests.py fast
""")


def main():
    """Main test runner."""
    
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        
        if option == "unit":
            return run_unit_tests()
        elif option == "integration":
            return run_integration_tests()
        elif option == "specific" and len(sys.argv) > 2:
            return run_specific_test(sys.argv[2])
        elif option == "fast":
            return run_with_markers("not slow")
        elif option == "slow":
            return run_with_markers("slow")
        elif option in ["-h", "--help", "help"]:
            print_usage()
            return 0
        else:
            print(f"❌ Unknown option: {option}")
            print_usage()
            return 1
    else:
        # Run all tests
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())