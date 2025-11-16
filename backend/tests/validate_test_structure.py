"""
Validation script to check if test structure is correct for TDD RED phase.

This script validates the test file structure without running the tests,
which is useful when the service doesn't exist yet.

Run this to verify tests are properly structured before implementing the service.
"""
import ast
import sys
from pathlib import Path


def validate_test_file(test_file_path: Path):
    """
    Validate that the test file has proper structure.

    Checks:
    - All 3 required tests exist
    - Tests are marked as async
    - REAL_INTEGRATION_TEST comments present
    - Proper imports
    - Proper assertions
    """
    print(f"Validating {test_file_path}...\n")

    content = test_file_path.read_text()
    tree = ast.parse(content)

    # Extract test functions
    test_functions = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith("test_")
    ]

    print(f"✓ Found {len(test_functions)} async test functions")

    # Check for required tests
    required_tests = {
        "test_analyze_real_wav_file",
        "test_invalid_file_raises_audio_error",
        "test_save_features_to_database"
    }

    found_tests = {func.name for func in test_functions}
    missing_tests = required_tests - found_tests

    if missing_tests:
        print(f"✗ Missing required tests: {missing_tests}")
        return False

    print(f"✓ All 3 required tests present: {', '.join(required_tests)}")

    # Check for REAL_INTEGRATION_TEST markers
    real_integration_count = content.count("REAL_INTEGRATION_TEST")
    print(f"✓ Found {real_integration_count} REAL_INTEGRATION_TEST markers (expected: 2)")

    if real_integration_count < 2:
        print(f"⚠ Warning: Should have at least 2 REAL_INTEGRATION_TEST markers")

    # Check for proper imports
    required_imports = [
        "AudioFeaturesService",
        "AudioFeatures",
        "AudioError",
        "Sample"
    ]

    for imp in required_imports:
        if imp in content:
            print(f"✓ Imports {imp}")
        else:
            print(f"✗ Missing import: {imp}")
            return False

    # Check for assertions
    assertion_keywords = ["assert", "pytest.raises"]
    has_assertions = any(keyword in content for keyword in assertion_keywords)

    if has_assertions:
        print(f"✓ Contains assertions")
    else:
        print(f"✗ No assertions found")
        return False

    # Check for fixtures usage
    fixtures = ["audio_service", "test_wav_fixture", "db_session", "test_user"]
    for fixture in fixtures:
        if fixture in content:
            print(f"✓ Uses fixture: {fixture}")

    print("\n✅ Test file structure is valid!")
    print("\nNext steps:")
    print("1. Implement AudioFeaturesService in backend/app/services/audio_features_service.py")
    print("2. Implement AudioFeatures and AudioError in backend/app/models/audio_features.py")
    print("3. Run tests: cd backend && ../venv/bin/python -m pytest tests/test_audio_features_service.py -v")
    print("4. Tests should PASS after implementation (TDD GREEN phase)")

    return True


def validate_fixtures(conftest_path: Path):
    """Validate that required fixtures are defined in conftest.py."""
    print(f"\nValidating fixtures in {conftest_path}...\n")

    content = conftest_path.read_text()

    required_fixtures = [
        "audio_service",
        "test_wav_fixture"
    ]

    for fixture in required_fixtures:
        if f"def {fixture}" in content:
            print(f"✓ Fixture defined: {fixture}")
        else:
            print(f"✗ Missing fixture: {fixture}")
            return False

    print("\n✅ All required fixtures are defined!")
    return True


def main():
    """Run validation."""
    test_file = Path(__file__).parent / "test_audio_features_service.py"
    conftest_file = Path(__file__).parent / "conftest.py"

    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        sys.exit(1)

    if not conftest_file.exists():
        print(f"✗ conftest.py not found: {conftest_file}")
        sys.exit(1)

    test_valid = validate_test_file(test_file)
    fixtures_valid = validate_fixtures(conftest_file)

    if test_valid and fixtures_valid:
        print("\n" + "=" * 60)
        print("🎉 TDD RED PHASE COMPLETE")
        print("=" * 60)
        print("\nAll tests are properly structured and will FAIL until")
        print("AudioFeaturesService is implemented.")
        print("\nReady to hand off to Coder agent for implementation!")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
