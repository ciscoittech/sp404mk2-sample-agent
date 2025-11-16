#!/usr/bin/env python
"""
Demo script to showcase Essentia feature flag system.

Demonstrates:
1. Analyzer selection based on settings
2. Fallback behavior
3. Metadata tracking
4. Logging output
"""
import asyncio
import logging
from pathlib import Path
from unittest.mock import patch

from app.services.audio_features_service import AudioFeaturesService
from app.utils.essentia_check import ESSENTIA_AVAILABLE

# Configure logging to see analyzer selection
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_essentia_enabled():
    """Demo with Essentia enabled (default)."""
    print("\n" + "="*60)
    print("DEMO 1: Essentia Enabled (USE_ESSENTIA=True)")
    print("="*60)

    with patch('app.services.audio_features_service.settings') as mock_settings:
        mock_settings.USE_ESSENTIA = True
        mock_settings.ENABLE_GENRE_CLASSIFICATION = False
        mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
        mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

        service = AudioFeaturesService()
        print(f"\n✓ Service initialized with: {service.analyzer_type}")
        print(f"  - Essentia available: {ESSENTIA_AVAILABLE}")
        print(f"  - Genre classification: False")

        # Try to analyze a sample
        test_file = Path("tests/fixtures/test_sample.wav")
        if test_file.exists():
            print(f"\n✓ Analyzing: {test_file.name}")
            features = await service.analyze_file(test_file)
            print(f"  - Analyzer used: {features.metadata.get('analyzer')}")
            print(f"  - BPM: {features.bpm}")
            if features.metadata.get('bpm_confidence'):
                print(f"  - BPM confidence: {features.metadata.get('bpm_confidence'):.2f}")
        else:
            print(f"\n✗ Test file not found: {test_file}")


async def demo_essentia_disabled():
    """Demo with Essentia disabled."""
    print("\n" + "="*60)
    print("DEMO 2: Essentia Disabled (USE_ESSENTIA=False)")
    print("="*60)

    with patch('app.services.audio_features_service.settings') as mock_settings:
        mock_settings.USE_ESSENTIA = False
        mock_settings.ENABLE_GENRE_CLASSIFICATION = False
        mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
        mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

        service = AudioFeaturesService()
        print(f"\n✓ Service initialized with: {service.analyzer_type}")
        print(f"  - Essentia available: {ESSENTIA_AVAILABLE}")
        print(f"  - Forced to use: librosa")

        # Try to analyze a sample
        test_file = Path("tests/fixtures/test_sample.wav")
        if test_file.exists():
            print(f"\n✓ Analyzing: {test_file.name}")
            features = await service.analyze_file(test_file)
            print(f"  - Analyzer used: {features.metadata.get('analyzer')}")
            print(f"  - BPM: {features.bpm}")
        else:
            print(f"\n✗ Test file not found: {test_file}")


async def demo_genre_classification():
    """Demo with genre classification enabled."""
    print("\n" + "="*60)
    print("DEMO 3: Genre Classification (ENABLE_GENRE_CLASSIFICATION=True)")
    print("="*60)

    if not ESSENTIA_AVAILABLE:
        print("\n✗ Skipping: Essentia not available")
        return

    with patch('app.services.audio_features_service.settings') as mock_settings:
        mock_settings.USE_ESSENTIA = True
        mock_settings.ENABLE_GENRE_CLASSIFICATION = True
        mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
        mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

        service = AudioFeaturesService()
        print(f"\n✓ Service initialized with: {service.analyzer_type}")
        print(f"  - Genre classification: Enabled")
        print(f"  - Note: Requires models to be downloaded")

        # Try to analyze a sample
        test_file = Path("tests/fixtures/test_sample.wav")
        if test_file.exists():
            print(f"\n✓ Analyzing: {test_file.name}")
            try:
                features = await service.analyze_file(test_file)
                print(f"  - Analyzer used: {features.metadata.get('analyzer')}")
                print(f"  - BPM: {features.bpm}")
                if features.metadata.get('genre'):
                    print(f"  - Genre: {features.metadata.get('genre')}")
                    print(f"  - SP404 category: {features.metadata.get('sp404_category')}")
                else:
                    print(f"  - Genre: Not available (models not downloaded)")
            except Exception as e:
                print(f"\n✗ Analysis failed: {e}")
                print("  - This is expected if genre models are not downloaded")
        else:
            print(f"\n✗ Test file not found: {test_file}")


async def demo_fallback_behavior():
    """Demo fallback from Essentia to librosa."""
    print("\n" + "="*60)
    print("DEMO 4: Automatic Fallback (Essentia → librosa)")
    print("="*60)

    if not ESSENTIA_AVAILABLE:
        print("\n✗ Skipping: Essentia not available")
        return

    with patch('app.services.audio_features_service.settings') as mock_settings:
        mock_settings.USE_ESSENTIA = True
        mock_settings.ENABLE_GENRE_CLASSIFICATION = False
        mock_settings.ESSENTIA_BPM_METHOD = "multifeature"
        mock_settings.AUDIO_ANALYSIS_TIMEOUT = 30

        service = AudioFeaturesService()
        print(f"\n✓ Service initialized with: {service.analyzer_type}")

        # Force Essentia to fail
        if service.analyzer_type == "essentia":
            original_method = service._analyze_with_essentia

            async def mock_fail(*args, **kwargs):
                raise RuntimeError("Simulated Essentia failure for demo")

            service._analyze_with_essentia = mock_fail

            test_file = Path("tests/fixtures/test_sample.wav")
            if test_file.exists():
                print(f"\n✓ Analyzing with forced Essentia failure: {test_file.name}")
                features = await service.analyze_file(test_file)
                print(f"  - Fallback analyzer used: {features.metadata.get('analyzer')}")
                print(f"  - BPM: {features.bpm}")
                print(f"  - ✓ Fallback successful!")
            else:
                print(f"\n✗ Test file not found: {test_file}")


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("ESSENTIA FEATURE FLAG SYSTEM - DEMONSTRATION")
    print("="*60)
    print(f"\nSystem Status:")
    print(f"  - Essentia installed: {ESSENTIA_AVAILABLE}")
    print(f"  - Python version: 3.13")

    await demo_essentia_enabled()
    await demo_essentia_disabled()
    await demo_genre_classification()
    await demo_fallback_behavior()

    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("  1. USE_ESSENTIA flag controls which analyzer is used")
    print("  2. Automatic fallback to librosa on Essentia failures")
    print("  3. ENABLE_GENRE_CLASSIFICATION controls genre analysis")
    print("  4. All metadata tracked in features.metadata dict")
    print("  5. Comprehensive logging for debugging")
    print()


if __name__ == "__main__":
    asyncio.run(main())
