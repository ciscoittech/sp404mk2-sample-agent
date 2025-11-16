"""
Quick test to check baseline librosa accuracy vs Essentia accuracy.
"""
import json
import asyncio
from pathlib import Path
from app.services.audio_features_service import AudioFeaturesService
from app.core.config import settings


async def test_both_analyzers():
    """Test both analyzers and compare results."""
    # Load dataset
    dataset_path = Path(__file__).parent / "fixtures" / "test_dataset.json"
    with open(dataset_path) as f:
        data = json.load(f)
    samples = data["samples"]

    print("\n" + "="*70)
    print("BASELINE COMPARISON: Librosa vs Essentia")
    print("="*70)

    # Test with librosa (disable Essentia)
    settings.USE_ESSENTIA = False
    service_librosa = AudioFeaturesService()

    print(f"\nLibrosa Analyzer (baseline):")
    print("-"*70)

    librosa_correct = 0
    for sample in samples:
        fixtures_dir = Path(__file__).parent / "fixtures"
        file_path = fixtures_dir / sample["file"].replace("fixtures/", "")
        ground_truth = sample["ground_truth_bpm"]

        features = await service_librosa.analyze_file(file_path)
        detected = features.bpm

        if detected is None:
            print(f"✗ {sample['file']:35s} | GT: {ground_truth:6.1f} | Det: None | Err: N/A (failed)")
            continue

        error = abs(detected - ground_truth)
        is_correct = error <= 2.0

        if is_correct:
            librosa_correct += 1

        status = "✓" if is_correct else "✗"
        print(f"{status} {sample['file']:35s} | GT: {ground_truth:6.1f} | Det: {detected:6.1f} | Err: {error:5.2f}")

    librosa_accuracy = (librosa_correct / len(samples)) * 100
    print(f"\nLibrosa Accuracy: {librosa_accuracy:.1f}% ({librosa_correct}/{len(samples)})")

    # Test with Essentia
    settings.USE_ESSENTIA = True
    service_essentia = AudioFeaturesService()

    if service_essentia.analyzer_type == "essentia":
        print(f"\n\nEssentia Analyzer:")
        print("-"*70)

        essentia_correct = 0
        for sample in samples:
            fixtures_dir = Path(__file__).parent / "fixtures"
            file_path = fixtures_dir / sample["file"].replace("fixtures/", "")
            ground_truth = sample["ground_truth_bpm"]

            features = await service_essentia.analyze_file(file_path)
            detected = features.bpm

            if detected is None:
                print(f"✗ {sample['file']:35s} | GT: {ground_truth:6.1f} | Det: None | Err: N/A (failed)")
                continue

            error = abs(detected - ground_truth)
            is_correct = error <= 2.0

            if is_correct:
                essentia_correct += 1

            status = "✓" if is_correct else "✗"
            print(f"{status} {sample['file']:35s} | GT: {ground_truth:6.1f} | Det: {detected:6.1f} | Err: {error:5.2f}")

        essentia_accuracy = (essentia_correct / len(samples)) * 100
        print(f"\nEssentia Accuracy: {essentia_accuracy:.1f}% ({essentia_correct}/{len(samples)})")

        # Comparison
        print("\n" + "="*70)
        print("COMPARISON:")
        print("="*70)
        print(f"Librosa:  {librosa_accuracy:.1f}% ({librosa_correct}/{len(samples)})")
        print(f"Essentia: {essentia_accuracy:.1f}% ({essentia_correct}/{len(samples)})")
        print(f"Improvement: +{essentia_accuracy - librosa_accuracy:.1f}%")
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_both_analyzers())
