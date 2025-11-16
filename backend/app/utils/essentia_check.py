"""
Essentia availability checker.

Provides safe import handling for optional Essentia dependency
and helper functions to check if Essentia is available at runtime.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import Essentia components
try:
    from essentia.standard import (
        MonoLoader,
        RhythmExtractor2013,
        KeyExtractor,
        TonalExtractor,
    )

    ESSENTIA_AVAILABLE = True
    logger.info("Essentia successfully loaded and available")
except ImportError as e:
    ESSENTIA_AVAILABLE = False
    logger.warning(f"Essentia not available: {e}")
    logger.info("Audio analysis will fall back to librosa")


def check_essentia_availability() -> bool:
    """
    Check if Essentia is available for use.

    Returns:
        bool: True if Essentia is available, False otherwise
    """
    return ESSENTIA_AVAILABLE


def get_essentia_version() -> Optional[str]:
    """
    Get the installed Essentia version.

    Returns:
        Optional[str]: Version string if available, None otherwise
    """
    if not ESSENTIA_AVAILABLE:
        return None

    try:
        import essentia

        return getattr(essentia, "__version__", "unknown")
    except Exception as e:
        logger.warning(f"Could not determine Essentia version: {e}")
        return None


def get_availability_status() -> dict:
    """
    Get detailed status of Essentia availability.

    Returns:
        dict: Status information including availability, version, and features
    """
    status = {
        "available": ESSENTIA_AVAILABLE,
        "version": get_essentia_version() if ESSENTIA_AVAILABLE else None,
        "features": [],
    }

    if ESSENTIA_AVAILABLE:
        try:
            from essentia.standard import (
                MonoLoader,
                RhythmExtractor2013,
                KeyExtractor,
                TonalExtractor,
            )

            status["features"] = [
                "MonoLoader",
                "RhythmExtractor2013",
                "KeyExtractor",
                "TonalExtractor",
            ]
        except ImportError as e:
            logger.warning(f"Some Essentia features unavailable: {e}")
            status["error"] = str(e)

    return status


# Log status on import
if __name__ != "__main__":
    status = get_availability_status()
    if status["available"]:
        logger.info(
            f"Essentia {status['version']} loaded with features: {', '.join(status['features'])}"
        )
    else:
        logger.info("Essentia not available - using fallback audio analysis")
