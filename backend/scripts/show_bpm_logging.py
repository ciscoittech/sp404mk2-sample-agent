"""Demonstrate BPM detection logging and statistics tracking."""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.audio_features_service import AudioFeaturesService

# Set up logging to see DEBUG and INFO messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(name)-40s %(message)s'
)


async def main():
    service = AudioFeaturesService()
    sample_path = Path(__file__).parent.parent / "tests" / "fixtures" / "samples" / "click_90bpm.wav"

    print('\n' + '='*80)
    print('EXAMPLE: BPM DETECTION WITH COMPREHENSIVE LOGGING')
    print('='*80)
    print()

    features = await service.analyze_file(sample_path)

    print('\n' + '='*80)
    print(f'RESULT: Detected BPM = {features.bpm:.1f} BPM')
    print('='*80)

    # Show statistics
    stats = service.get_bpm_correction_stats()
    print('\nBPM CORRECTION STATISTICS:')
    print(f'  Total analyzed: {stats["total_analyzed"]}')
    print(f'  Corrections applied: {stats["corrections_applied"]}')
    print(f'  Correction rate: {stats["correction_rate"]:.1%}')
    if stats['correction_types']:
        print('  Correction types:')
        for correction, count in stats['correction_types'].items():
            print(f'    {correction}: {count} occurrences')
    print()


if __name__ == "__main__":
    asyncio.run(main())
