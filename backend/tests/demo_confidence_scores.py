#!/usr/bin/env python3
"""
Demonstration of confidence scoring functionality.

This script analyzes a sample audio file and displays:
- BPM with confidence score
- Genre with confidence score (if available)
- Analysis metadata (analyzer used, method, etc.)
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.audio_features_service import AudioFeaturesService


async def demo_confidence_scores():
    """Demonstrate confidence scoring with a real audio file."""

    # Initialize service
    service = AudioFeaturesService()

    print("\n" + "="*70)
    print("CONFIDENCE SCORING DEMONSTRATION")
    print("="*70)
    print(f"\nAnalyzer: {service.analyzer_type.upper()}")

    # Find a test audio file
    test_files = [
        Path(__file__).parent / "fixtures" / "test_audio.wav",
        Path(__file__).parent.parent.parent / "uploads" / "1" / "4ac7a597-16be-40f6-8196-a3127e9aa17b.wav",
    ]

    test_file = None
    for f in test_files:
        if f.exists():
            test_file = f
            break

    if not test_file:
        print("\n❌ No test audio file found")
        return

    print(f"Sample: {test_file.name}")
    print(f"Path: {test_file}")

    # Analyze file
    print("\n📊 Analyzing...")
    try:
        features = await service.analyze_file(test_file)

        print("\n" + "-"*70)
        print("ANALYSIS RESULTS")
        print("-"*70)

        # BPM with confidence
        if features.bpm is not None:
            confidence = features.bpm_confidence or 0
            confidence_label = get_confidence_label(confidence)
            print(f"\n🎵 BPM: {features.bpm:.1f}")
            print(f"   Confidence: {confidence}/100 {confidence_label}")
        else:
            print("\n🎵 BPM: Not detected")

        # Genre with confidence
        if features.genre is not None:
            confidence = features.genre_confidence or 0
            confidence_label = get_confidence_label(confidence)
            print(f"\n🎸 Genre: {features.genre}")
            print(f"   Confidence: {confidence}/100 {confidence_label}")
        else:
            print("\n🎸 Genre: Not detected")

        # Key with confidence
        if features.key is not None:
            confidence = features.key_confidence or 0
            confidence_label = get_confidence_label(confidence)
            key_str = f"{features.key} {features.scale or ''}".strip()
            print(f"\n🎹 Key: {key_str}")
            print(f"   Confidence: {confidence}/100 {confidence_label}")
        else:
            print("\n🎹 Key: Not detected")

        # Metadata
        if features.metadata:
            print("\n" + "-"*70)
            print("ANALYSIS METADATA")
            print("-"*70)
            for key, value in features.metadata.items():
                print(f"  {key}: {value}")

        print("\n" + "="*70)
        print("✅ Analysis complete!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def get_confidence_label(confidence: int) -> str:
    """Get a visual label for confidence level."""
    if confidence >= 80:
        return "✅ HIGH"
    elif confidence >= 50:
        return "⚠️  MEDIUM"
    else:
        return "❌ LOW"


if __name__ == "__main__":
    asyncio.run(demo_confidence_scores())
