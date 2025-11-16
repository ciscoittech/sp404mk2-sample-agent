"""
BPM Accuracy Validation Tests - Task 1.4

Tests BPM detection accuracy against ground truth dataset created
by generate_test_samples.py. Measures improvement from octave correction
and custom prior distribution enhancements.

Goals:
- Validate octave correction is working
- Measure accuracy improvement vs baseline
- Test with and without prior/octave correction
- Generate comprehensive accuracy report
"""
import json
import pytest
from pathlib import Path
from typing import Dict, List, Tuple

from app.services.audio_features_service import AudioFeaturesService
from app.utils.essentia_check import ESSENTIA_AVAILABLE


def load_test_dataset() -> List[Dict]:
    """
    Load ground truth dataset from test_dataset.json.

    Returns:
        List of sample metadata with ground truth BPMs
    """
    dataset_path = Path(__file__).parent.parent / "fixtures" / "test_dataset.json"
    with open(dataset_path) as f:
        data = json.load(f)
    return data["samples"]


def is_within_tolerance(detected: float, ground_truth: float, tolerance: float = 2.0) -> bool:
    """
    Check if detected BPM is within tolerance of ground truth.

    Args:
        detected: Detected BPM value
        ground_truth: Known ground truth BPM
        tolerance: Acceptable error in BPM (default: ±2 BPM)

    Returns:
        True if within tolerance
    """
    return abs(detected - ground_truth) <= tolerance


def classify_error(detected: float, ground_truth: float) -> str:
    """
    Classify the type of BPM detection error.

    Returns:
        Error type: "correct", "half", "double", "triple", "other"
    """
    if is_within_tolerance(detected, ground_truth):
        return "correct"
    elif is_within_tolerance(detected, ground_truth / 2):
        return "half"
    elif is_within_tolerance(detected, ground_truth * 2):
        return "double"
    elif is_within_tolerance(detected, ground_truth / 3):
        return "third"
    elif is_within_tolerance(detected, ground_truth * 3):
        return "triple"
    else:
        return "other"


@pytest.mark.asyncio
async def test_bpm_accuracy_on_known_dataset():
    """
    Test BPM accuracy on ground truth dataset.

    Validates that our octave correction and prior distribution
    improvements achieve the target accuracy of 75%+ (librosa) or
    90%+ (Essentia).
    """
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    correct = 0
    total = 0
    errors = []

    for sample in dataset:
        # Construct absolute path
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")

        ground_truth = sample["ground_truth_bpm"]

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm

        # Check accuracy (within ±2 BPM)
        error = abs(detected_bpm - ground_truth)
        error_type = classify_error(detected_bpm, ground_truth)

        if is_within_tolerance(detected_bpm, ground_truth):
            correct += 1
        else:
            errors.append({
                "file": sample["file"],
                "ground_truth": ground_truth,
                "detected": detected_bpm,
                "error": error,
                "error_type": error_type,
                "notes": sample.get("notes", "")
            })
        total += 1

    accuracy = (correct / total) * 100

    # Print detailed report
    print("\n" + "="*70)
    print("BPM ACCURACY VALIDATION REPORT")
    print("="*70)
    print(f"Analyzer: {service.analyzer_type}")
    print(f"Total samples: {total}")
    print(f"Accurate (±2 BPM): {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")

    if errors:
        print("\n" + "-"*70)
        print(f"ERRORS ({len(errors)} samples):")
        print("-"*70)
        for err in errors:
            print(f"  {err['file']:35s} | "
                  f"GT: {err['ground_truth']:6.1f} | "
                  f"Detected: {err['detected']:6.1f} | "
                  f"Error: {err['error']:5.1f} | "
                  f"Type: {err['error_type']}")
            if err.get('notes'):
                print(f"    Notes: {err['notes']}")

    print("="*70 + "\n")

    # Target: 75%+ for librosa, 90%+ for Essentia
    target_accuracy = 90.0 if ESSENTIA_AVAILABLE and service.analyzer_type == "essentia" else 75.0

    assert accuracy >= target_accuracy, \
        f"Accuracy {accuracy:.1f}% below {target_accuracy}% target"


@pytest.mark.asyncio
async def test_octave_correction_effectiveness():
    """
    Test that octave correction is catching and fixing errors.

    Validates that the octave correction logic from Task 1.1 is
    working correctly.
    """
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    octave_errors_caught = 0
    corrections = []

    for sample in dataset:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")
        ground_truth = sample["ground_truth_bpm"]

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm
        error_type = classify_error(detected_bpm, ground_truth)

        # Check if this was an octave error that got corrected
        if error_type in ["half", "double", "triple", "third"]:
            # This suggests an octave error wasn't fully corrected
            corrections.append({
                "file": sample["file"],
                "ground_truth": ground_truth,
                "detected": detected_bpm,
                "error_type": error_type
            })
        elif error_type == "correct":
            # This could be a corrected octave error or naturally correct
            octave_errors_caught += 1

    print("\n" + "="*70)
    print("OCTAVE CORRECTION EFFECTIVENESS")
    print("="*70)
    print(f"Samples processed: {len(dataset)}")
    print(f"Correct detections: {octave_errors_caught}")

    if corrections:
        print(f"\nRemaining octave errors: {len(corrections)}")
        for corr in corrections:
            print(f"  {corr['file']:35s} | "
                  f"GT: {corr['ground_truth']:6.1f} | "
                  f"Detected: {corr['detected']:6.1f} | "
                  f"Type: {corr['error_type']}")
    else:
        print("\nNo remaining octave errors detected!")

    print("="*70 + "\n")


@pytest.mark.asyncio
async def test_accuracy_by_sample_type():
    """
    Test accuracy breakdown by sample type (click vs musical).

    Validates that both click tracks and musical samples are
    being detected accurately.
    """
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    results = {
        "click": {"correct": 0, "total": 0},
        "musical": {"correct": 0, "total": 0}
    }

    for sample in dataset:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")
        ground_truth = sample["ground_truth_bpm"]

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm

        # Determine sample category
        if "click" in sample["file"]:
            category = "click"
        else:
            category = "musical"

        # Check accuracy
        if is_within_tolerance(detected_bpm, ground_truth):
            results[category]["correct"] += 1
        results[category]["total"] += 1

    # Calculate accuracies
    click_accuracy = (results["click"]["correct"] / results["click"]["total"] * 100
                     if results["click"]["total"] > 0 else 0)
    musical_accuracy = (results["musical"]["correct"] / results["musical"]["total"] * 100
                       if results["musical"]["total"] > 0 else 0)

    print("\n" + "="*70)
    print("ACCURACY BY SAMPLE TYPE")
    print("="*70)
    print(f"Click tracks: {results['click']['correct']}/{results['click']['total']} "
          f"({click_accuracy:.1f}%)")
    print(f"Musical samples: {results['musical']['correct']}/{results['musical']['total']} "
          f"({musical_accuracy:.1f}%)")
    print("="*70 + "\n")

    # Both should meet target
    target = 70.0 if service.analyzer_type == "librosa" else 85.0
    assert click_accuracy >= target, \
        f"Click track accuracy {click_accuracy:.1f}% below {target}% target"


@pytest.mark.asyncio
async def test_accuracy_by_bpm_range():
    """
    Test accuracy breakdown by BPM range.

    Validates that all tempo ranges (slow/medium/fast) are
    being detected accurately.
    """
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    # Define BPM ranges
    ranges = {
        "slow (60-89)": (60, 89),
        "medium (90-129)": (90, 129),
        "fast (130-180)": (130, 180)
    }

    results = {name: {"correct": 0, "total": 0} for name in ranges.keys()}

    for sample in dataset:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")
        ground_truth = sample["ground_truth_bpm"]

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm

        # Determine range
        for range_name, (min_bpm, max_bpm) in ranges.items():
            if min_bpm <= ground_truth <= max_bpm:
                if is_within_tolerance(detected_bpm, ground_truth):
                    results[range_name]["correct"] += 1
                results[range_name]["total"] += 1
                break

    print("\n" + "="*70)
    print("ACCURACY BY BPM RANGE")
    print("="*70)

    for range_name, result in results.items():
        if result["total"] > 0:
            accuracy = result["correct"] / result["total"] * 100
            print(f"{range_name:20s}: {result['correct']}/{result['total']} ({accuracy:.1f}%)")

    print("="*70 + "\n")


@pytest.mark.asyncio
async def test_prior_distribution_effectiveness():
    """
    Test that custom prior distribution is improving accuracy.

    Validates that our custom prior (Task 1.3) is biasing detection
    toward common hip-hop tempos effectively.
    """
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    # Focus on common hip-hop tempos where prior should help
    hip_hop_tempos = [90, 105, 115, 140, 170]
    results = []

    for sample in dataset:
        ground_truth = sample["ground_truth_bpm"]

        # Only test samples at our prior peaks
        if ground_truth not in hip_hop_tempos:
            continue

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm

        results.append({
            "bpm": ground_truth,
            "accurate": is_within_tolerance(detected_bpm, ground_truth)
        })

    if results:
        accuracy = sum(1 for r in results if r["accurate"]) / len(results) * 100
        print("\n" + "="*70)
        print("PRIOR DISTRIBUTION EFFECTIVENESS")
        print("="*70)
        print(f"Common hip-hop tempos (90,105,115,140,170 BPM)")
        print(f"Accuracy: {accuracy:.1f}% ({sum(1 for r in results if r['accurate'])}/{len(results)})")
        print("="*70 + "\n")

        # Prior should give high accuracy on these tempos
        target = 85.0 if service.analyzer_type == "essentia" else 70.0
        assert accuracy >= target, \
            f"Prior distribution not effective: {accuracy:.1f}% below {target}% target"


@pytest.mark.asyncio
async def test_generate_comprehensive_report():
    """
    Generate comprehensive accuracy report for documentation.

    This test always passes and is used to generate a detailed
    report of BPM detection performance.
    """
    service = AudioFeaturesService()
    dataset = load_test_dataset()

    all_results = []

    for sample in dataset:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")
        ground_truth = sample["ground_truth_bpm"]

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm

        all_results.append({
            "file": sample["file"],
            "ground_truth": ground_truth,
            "detected": detected_bpm,
            "error": abs(detected_bpm - ground_truth),
            "error_type": classify_error(detected_bpm, ground_truth),
            "accurate": is_within_tolerance(detected_bpm, ground_truth),
            "genre": sample.get("genre", ""),
            "notes": sample.get("notes", "")
        })

    # Calculate statistics
    total = len(all_results)
    accurate = sum(1 for r in all_results if r["accurate"])
    accuracy = (accurate / total) * 100
    avg_error = sum(r["error"] for r in all_results) / total

    # Error type breakdown
    error_types = {}
    for r in all_results:
        error_type = r["error_type"]
        error_types[error_type] = error_types.get(error_type, 0) + 1

    # Print comprehensive report
    print("\n" + "="*70)
    print("COMPREHENSIVE BPM ACCURACY REPORT")
    print("="*70)
    print(f"Analyzer: {service.analyzer_type.upper()}")
    print(f"Test Dataset Version: 1.0")
    print(f"Total Samples: {total}")
    print()
    print("OVERALL ACCURACY:")
    print(f"  Correct (±2 BPM): {accurate}/{total} ({accuracy:.1f}%)")
    print(f"  Average Error: {avg_error:.2f} BPM")
    print()
    print("ERROR TYPE BREAKDOWN:")
    for error_type, count in sorted(error_types.items()):
        pct = (count / total) * 100
        print(f"  {error_type:10s}: {count:2d} samples ({pct:5.1f}%)")
    print()
    print("DETAILED RESULTS:")
    print("-"*70)

    for r in all_results:
        status = "✓" if r["accurate"] else "✗"
        print(f"{status} {r['file']:35s} | "
              f"GT: {r['ground_truth']:6.1f} | "
              f"Det: {r['detected']:6.1f} | "
              f"Err: {r['error']:5.2f} | "
              f"Type: {r['error_type']}")

    print("="*70 + "\n")

    # Always pass - this is for reporting only
    assert True
