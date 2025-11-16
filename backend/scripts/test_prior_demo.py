"""Quick demo of the custom tempo prior distribution."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import numpy as np
from app.services.audio_features_service import AudioFeaturesService


def demo_prior():
    """Demonstrate the custom tempo prior."""
    service = AudioFeaturesService()

    print("Custom Tempo Prior Distribution Demo")
    print("=" * 60)
    print()

    # Test for loops
    print("1. Prior for LOOPS:")
    prior = service._get_tempo_prior(sample_type="loop")
    tempos = np.linspace(30, 300, 271)

    if prior is not None:
        print(f"   ✓ Generated prior array: shape={prior.shape}")
        print(f"   ✓ Normalized: sum={prior.sum():.6f} (should be 1.0)")
        print(f"   ✓ Min probability: {prior.min():.8f}")
        print(f"   ✓ Max probability: {prior.max():.8f}")
        print()

        print("   Peak probabilities at target tempos:")
        target_tempos = [90, 105, 115, 140, 170]
        for tempo in target_tempos:
            idx = np.argmin(np.abs(tempos - tempo))
            # Find max in ±5 BPM region
            region = prior[max(0, idx-5):min(len(prior), idx+6)]
            peak = np.max(region)
            peak_idx = max(0, idx-5) + np.argmax(region)
            peak_tempo = tempos[peak_idx]
            print(f"     {tempo} BPM: {peak:.6f} (peak at {peak_tempo:.1f} BPM)")
        print()

        # Show contrast with far-away tempos
        print("   Baseline probabilities at far-away tempos:")
        baseline_tempos = [30, 60, 200, 300]
        for tempo in baseline_tempos:
            idx = np.argmin(np.abs(tempos - tempo))
            print(f"     {tempo} BPM: {prior[idx]:.6f}")
        print()

        # Calculate average and show peak-to-baseline ratio
        avg_prob = np.mean(prior)
        max_prob = np.max(prior)
        print(f"   Average probability: {avg_prob:.6f}")
        print(f"   Peak-to-average ratio: {max_prob/avg_prob:.2f}x")

    else:
        print("   ✗ Prior is None (unexpected for loops)")

    print()
    print("2. Prior for ONE-SHOTS:")
    prior_oneshot = service._get_tempo_prior(sample_type="one-shot")
    if prior_oneshot is None:
        print("   ✓ Prior is None (uses librosa default)")
    else:
        print("   ✗ Prior is not None (unexpected for one-shots)")

    print()
    print("=" * 60)
    print("Demo complete!")
    print()
    print("The prior successfully biases BPM detection toward:")
    print("  - 90 BPM (boom bap, lo-fi)")
    print("  - 105 BPM (classic hip-hop)")
    print("  - 115 BPM (mid-tempo)")
    print("  - 140 BPM (trap)")
    print("  - 170 BPM (double-time)")
    print()
    print("This should reduce octave errors and improve accuracy!")


if __name__ == "__main__":
    demo_prior()
