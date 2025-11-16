"""Generate BPM correction statistics report.

This script analyzes the test dataset and generates a comprehensive report
on BPM detection accuracy, correction effectiveness, and prior usage.

Usage:
    python scripts/bpm_correction_report.py

Output:
    Prints detailed statistics report to console
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.audio_features_service import AudioFeaturesService


def load_test_dataset() -> List[Dict]:
    """Load ground truth dataset from test_dataset.json."""
    dataset_path = Path(__file__).parent.parent / "tests" / "fixtures" / "test_dataset.json"
    with open(dataset_path) as f:
        data = json.load(f)
    return data["samples"]


def is_within_tolerance(detected: float, ground_truth: float, tolerance: float = 2.0) -> bool:
    """Check if detected BPM is within tolerance of ground truth."""
    return abs(detected - ground_truth) <= tolerance


async def generate_report():
    """Generate comprehensive BPM correction statistics report."""
    print("\n" + "="*80)
    print("BPM CORRECTION STATISTICS REPORT")
    print("="*80)
    print()

    # Initialize service
    service = AudioFeaturesService()
    print(f"Analyzer: {service.analyzer_type.upper()}")
    print()

    # Load test dataset
    dataset = load_test_dataset()
    print(f"Loading {len(dataset)} test samples...")
    print()

    # Analyze all samples
    results = []
    for sample in dataset:
        fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")

        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping")
            continue

        ground_truth = sample["ground_truth_bpm"]

        # Analyze
        features = await service.analyze_file(file_path)
        detected_bpm = features.bpm

        results.append({
            "file": sample["file"],
            "ground_truth": ground_truth,
            "detected": detected_bpm,
            "error": abs(detected_bpm - ground_truth),
            "accurate": is_within_tolerance(detected_bpm, ground_truth)
        })

    # Get correction statistics
    stats = service.get_bpm_correction_stats()

    # Print statistics
    print("-"*80)
    print("DETECTION STATISTICS")
    print("-"*80)
    print(f"Total samples analyzed:      {stats['total_analyzed']}")
    print(f"Corrections applied:         {stats['corrections_applied']}")
    print(f"Correction rate:             {stats['correction_rate']:.1%}")
    print(f"Prior usage count:           {stats['prior_used_count']}")
    print(f"Prior usage rate:            {stats['prior_usage_rate']:.1%}")
    print()

    # Print correction types breakdown
    if stats['correction_types']:
        print("-"*80)
        print("CORRECTION TYPES BREAKDOWN")
        print("-"*80)
        for correction, count in sorted(stats['correction_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {correction:15s}: {count:2d} occurrences")
        print()

    # Print accuracy results
    accurate = sum(1 for r in results if r["accurate"])
    total = len(results)
    accuracy = (accurate / total * 100) if total > 0 else 0

    print("-"*80)
    print("ACCURACY RESULTS")
    print("-"*80)
    print(f"Samples within ±2 BPM:       {accurate}/{total} ({accuracy:.1f}%)")
    avg_error = sum(r["error"] for r in results) / total if total > 0 else 0
    print(f"Average error:               {avg_error:.2f} BPM")
    print()

    # Print per-sample results
    print("-"*80)
    print("PER-SAMPLE RESULTS")
    print("-"*80)
    for r in results:
        status = "✓" if r["accurate"] else "✗"
        print(f"{status} {Path(r['file']).name:30s} | "
              f"GT: {r['ground_truth']:6.1f} | "
              f"Det: {r['detected']:6.1f} | "
              f"Err: {r['error']:5.2f}")
    print()

    # Print recommendations
    print("-"*80)
    print("RECOMMENDATIONS")
    print("-"*80)

    if stats['correction_rate'] > 0.5:
        print("⚠ High correction rate (>50%) detected!")
        print("  Consider adjusting custom prior distribution or detection algorithm.")
    else:
        print("✓ Correction rate is reasonable.")

    if accuracy < 75.0 and service.analyzer_type == "librosa":
        print("⚠ Accuracy below target (75% for librosa).")
        print("  Recommendations:")
        print("  - Review correction logic in bpm_validation.py")
        print("  - Adjust custom prior peaks in _get_tempo_prior()")
        print("  - Consider enabling Essentia analyzer for higher accuracy")
    elif accuracy < 90.0 and service.analyzer_type == "essentia":
        print("⚠ Accuracy below target (90% for Essentia).")
        print("  Recommendations:")
        print("  - Review Essentia BPM method configuration")
        print("  - Check sample quality and duration")
    else:
        print("✓ Accuracy meets or exceeds target.")

    if stats['prior_usage_rate'] < 0.8:
        print("⚠ Low prior usage rate (<80%).")
        print("  Most samples are one-shots or falling back to default prior.")

    print()
    print("="*80)
    print()


if __name__ == "__main__":
    asyncio.run(generate_report())
