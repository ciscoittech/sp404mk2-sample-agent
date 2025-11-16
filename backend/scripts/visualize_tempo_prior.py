"""Visualize the custom tempo prior distribution.

This script generates a visualization of the tempo prior distribution
used in BPM detection to bias toward common hip-hop tempos.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import numpy as np
import matplotlib.pyplot as plt

from app.services.audio_features_service import AudioFeaturesService


def visualize_prior():
    """Generate and save visualization of tempo prior."""
    service = AudioFeaturesService()

    # Generate prior for loops
    prior = service._get_tempo_prior(sample_type="loop")
    tempos = np.linspace(30, 300, 271)

    # Target tempos
    target_tempos = [90, 105, 115, 140, 170]
    target_labels = ["90 BPM\n(Boom Bap)", "105 BPM\n(Classic)", "115 BPM\n(Mid-Tempo)",
                     "140 BPM\n(Trap)", "170 BPM\n(Double-Time)"]

    # Create figure
    plt.figure(figsize=(12, 6))

    # Plot prior distribution
    plt.plot(tempos, prior, 'b-', linewidth=2, label='Tempo Prior Distribution')
    plt.fill_between(tempos, prior, alpha=0.3)

    # Mark target tempos
    for tempo, label in zip(target_tempos, target_labels):
        idx = np.argmin(np.abs(tempos - tempo))
        plt.axvline(tempo, color='red', linestyle='--', alpha=0.5, linewidth=1)
        plt.plot(tempo, prior[idx], 'ro', markersize=8)
        plt.text(tempo, prior[idx] + 0.0005, label,
                ha='center', va='bottom', fontsize=9)

    # Formatting
    plt.xlabel('Tempo (BPM)', fontsize=12)
    plt.ylabel('Probability Density', fontsize=12)
    plt.title('Custom Tempo Prior Distribution for Hip-Hop BPM Detection',
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xlim(30, 300)
    plt.ylim(0, None)
    plt.legend(fontsize=10)

    # Save
    output_path = backend_dir / "tempo_prior_visualization.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization to: {output_path}")

    # Print statistics
    print("\nPrior Distribution Statistics:")
    print(f"  Total probability (should be 1.0): {prior.sum():.6f}")
    print(f"  Max probability: {prior.max():.6f}")
    print(f"  Min probability: {prior.min():.6f}")
    print(f"\nPeak probabilities:")
    for tempo in target_tempos:
        idx = np.argmin(np.abs(tempos - tempo))
        print(f"  {tempo} BPM: {prior[idx]:.6f}")


if __name__ == "__main__":
    try:
        visualize_prior()
        print("\n✓ Visualization complete")
    except ImportError as e:
        print(f"✗ Error: matplotlib not installed. Install with: pip install matplotlib")
        print(f"  Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
