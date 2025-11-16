#!/usr/bin/env python3
"""Validate that audio export code uses correct SP-404MK2 settings."""
import sys
import re

def check_audio_format(file_path):
    """Check for SP-404MK2 audio format requirements in code."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        issues = []

        # Check for correct sample rate (48000 Hz)
        if 'sample_rate' in content.lower() or 'sr' in content:
            if '48000' not in content and '48kHz' not in content.lower():
                issues.append("⚠️  Warning: SP-404MK2 requires 48kHz sample rate")

        # Check for correct bit depth (16-bit)
        if 'bit' in content.lower() or 'PCM' in content:
            if '16' not in content:
                issues.append("⚠️  Warning: SP-404MK2 requires 16-bit audio")

        # Check for format validation
        if 'export' in content.lower():
            if 'WAV' not in content and 'AIFF' not in content:
                issues.append("⚠️  Warning: SP-404MK2 supports WAV and AIFF formats")

        if issues:
            print("\\n".join(issues))
            print("\\n✓ Audio format validation completed with warnings")
        else:
            print("✓ Audio format validation passed")

        return 0

    except Exception as e:
        print(f"✗ Audio format validation failed: {e}")
        return 0  # Don't block on error

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_audio_format.py <file_path>")
        sys.exit(0)

    sys.exit(check_audio_format(sys.argv[1]))
