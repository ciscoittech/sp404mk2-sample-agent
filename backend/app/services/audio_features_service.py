"""
Audio Features Service for analyzing audio files using librosa and Essentia.

Provides comprehensive audio analysis including BPM detection, key detection,
spectral features, and temporal characteristics. Automatically selects the best
available analyzer (Essentia or librosa) with graceful fallback.
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

try:
    import librosa
    import numpy as np
    import scipy.stats as stats
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

from app.core.config import settings
from app.models.audio_features import AudioFeatures, AudioError
from app.utils.essentia_check import ESSENTIA_AVAILABLE

# Import Essentia analyzer if available
if ESSENTIA_AVAILABLE:
    try:
        from app.services.essentia_analyzer import EssentiaAnalyzer
    except ImportError:
        ESSENTIA_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioFeaturesService:
    """
    Service for extracting audio features from audio files.

    Intelligently selects between Essentia (high accuracy) and librosa (fallback)
    based on availability and configuration. Provides graceful degradation when
    Essentia is unavailable or fails.

    Features:
    - Automatic analyzer selection (Essentia → librosa fallback)
    - BPM detection (90-95% accuracy with Essentia, 70-80% with librosa)
    - Key detection
    - Spectral features (centroid, rolloff, bandwidth)
    - Temporal features (zero crossing rate, RMS energy)
    - Genre classification (Essentia only, if enabled)

    Configuration:
    - USE_ESSENTIA: Enable/disable Essentia (default: True)
    - ENABLE_GENRE_CLASSIFICATION: Enable genre analysis (default: False)
    - ESSENTIA_BPM_METHOD: BPM algorithm (multifeature/degara/percival)
    - AUDIO_ANALYSIS_TIMEOUT: Analysis timeout in seconds (default: 30)
    """

    def __init__(self):
        """Initialize the audio features service.

        Selects the best available analyzer based on:
        1. USE_ESSENTIA setting (can be disabled via config)
        2. ESSENTIA_AVAILABLE flag (import check)
        3. Successful EssentiaAnalyzer initialization

        Falls back to librosa if Essentia is unavailable or fails to initialize.
        """
        self.analyzer_type = "librosa"  # Default fallback
        self.essentia_analyzer: Optional[EssentiaAnalyzer] = None

        # Initialize BPM correction statistics
        self._bpm_stats = {
            'total': 0,
            'corrected': 0,
            'correction_types': {},
            'prior_used': 0
        }

        # Check librosa availability
        if not LIBROSA_AVAILABLE:
            logger.warning(
                "librosa not available. Audio analysis features will be limited. "
                "Install with: pip install librosa soundfile"
            )

        # Try to initialize Essentia analyzer
        if self._should_use_essentia():
            try:
                self.essentia_analyzer = EssentiaAnalyzer()
                self.analyzer_type = "essentia"
                logger.info(
                    f"AudioFeaturesService initialized with Essentia analyzer "
                    f"(BPM method: {settings.ESSENTIA_BPM_METHOD}, "
                    f"genre classification: {settings.ENABLE_GENRE_CLASSIFICATION})"
                )
            except Exception as e:
                logger.warning(
                    f"Essentia initialization failed: {e}. "
                    f"Falling back to librosa analyzer."
                )
                self.essentia_analyzer = None
                self.analyzer_type = "librosa"
        else:
            logger.info(
                f"AudioFeaturesService initialized with librosa analyzer "
                f"(Essentia disabled: USE_ESSENTIA={settings.USE_ESSENTIA}, "
                f"available={ESSENTIA_AVAILABLE})"
            )

    def _should_use_essentia(self) -> bool:
        """Check if Essentia should be used for analysis.

        Essentia is used if:
        1. USE_ESSENTIA setting is True (can be disabled via .env)
        2. ESSENTIA_AVAILABLE is True (library imported successfully)

        Returns:
            True if Essentia should be attempted, False to use librosa
        """
        return settings.USE_ESSENTIA and ESSENTIA_AVAILABLE

    async def analyze_file(self, file_path: Path) -> AudioFeatures:
        """
        Analyze an audio file and extract comprehensive features.

        Intelligently selects between Essentia and librosa analyzers with
        automatic fallback. Tries Essentia first (if enabled and available),
        then falls back to librosa on failure.

        CPU-intensive work is executed in a thread pool to avoid blocking
        the event loop.

        Args:
            file_path: Path to the audio file to analyze

        Returns:
            AudioFeatures object with extracted features and metadata about
            which analyzer was used

        Raises:
            AudioError: If the file doesn't exist, is corrupted, or both
                       analyzers fail
        """
        # Validate file exists
        if not file_path.exists():
            raise AudioError(
                message=f"Audio file not found: {file_path}",
                file_path=file_path
            )

        # Validate file is not empty
        if file_path.stat().st_size == 0:
            raise AudioError(
                message=f"Audio file is empty: {file_path}",
                file_path=file_path
            )

        # Try Essentia first if available
        if self.analyzer_type == "essentia" and self.essentia_analyzer:
            try:
                logger.debug(f"Attempting Essentia analysis for {file_path.name}")
                features = await self._analyze_with_essentia(file_path)
                logger.info(f"Successfully analyzed {file_path.name} with Essentia")
                return features

            except Exception as e:
                logger.error(
                    f"Essentia analysis failed for {file_path.name}: {e}. "
                    f"Falling back to librosa."
                )
                # Fall through to librosa fallback

        # Use librosa (either as primary or fallback)
        return await self._analyze_with_librosa(file_path)

    async def _analyze_with_essentia(self, file_path: Path) -> AudioFeatures:
        """
        Analyze audio file using Essentia.

        Provides high-accuracy BPM detection and optional genre classification.
        Converts Essentia results to AudioFeatures format for consistency.

        Args:
            file_path: Path to audio file

        Returns:
            AudioFeatures with Essentia-derived features

        Raises:
            Exception: If Essentia analysis fails (caller will fallback to librosa)
        """
        if not self.essentia_analyzer:
            raise RuntimeError("Essentia analyzer not initialized")

        # Detect sample type early
        from app.utils.audio_utils import detect_sample_type
        sample_type = detect_sample_type(file_path)
        logger.info(f"Sample type detected: {sample_type} for {file_path.name}")

        # Determine BPM method (config override or auto-select)
        method = settings.ESSENTIA_BPM_METHOD

        # Get basic file info first (for method selection)
        try:
            y, sr = librosa.load(str(file_path), sr=None, mono=True, duration=0.1)
            duration = librosa.get_duration(path=str(file_path))
        except Exception as e:
            raise RuntimeError(f"Failed to get audio duration: {e}")

        # Auto-select method based on duration if not explicitly set
        if method == "auto":
            method = self.essentia_analyzer.get_recommended_method(duration)

        # Run BPM analysis
        bpm_result = await self.essentia_analyzer.analyze_bpm(
            file_path,
            method=method
        )

        # Run genre classification if enabled
        genre_result = None
        if settings.ENABLE_GENRE_CLASSIFICATION:
            try:
                genre_result = await self.essentia_analyzer.analyze_genre(file_path)
            except Exception as e:
                logger.warning(
                    f"Genre classification failed for {file_path.name}: {e}. "
                    f"Continuing with BPM-only analysis."
                )

        # Load full audio for remaining features
        y, sr = librosa.load(str(file_path), sr=None, mono=False)

        # Handle stereo vs mono
        if y.ndim > 1:
            num_channels = y.shape[0]
            y_mono = librosa.to_mono(y)
        else:
            num_channels = 1
            y_mono = y

        duration = librosa.get_duration(y=y_mono, sr=sr)
        num_samples = len(y_mono)

        # Extract remaining features with librosa (Essentia doesn't provide these)
        key, scale = self._extract_key(y_mono, sr)
        spectral_centroid = self._extract_spectral_centroid(y_mono, sr)
        spectral_bandwidth = self._extract_spectral_bandwidth(y_mono, sr)
        spectral_rolloff = self._extract_spectral_rolloff(y_mono, sr)
        spectral_flatness = self._extract_spectral_flatness(y_mono, sr)
        zero_crossing_rate = self._extract_zero_crossing_rate(y_mono)
        rms_energy = self._extract_rms_energy(y_mono)
        harmonic_ratio = self._extract_harmonic_ratio(y_mono, sr)
        mfcc_mean, mfcc_std = self._extract_mfcc(y_mono, sr)
        chroma_mean, chroma_std = self._extract_chroma(y_mono, sr)

        # Convert confidence scores from 0.0-1.0 to 0-100 integer scale
        # Cap at 100 in case Essentia returns values > 1.0
        bpm_confidence_score = min(100, int(bpm_result.confidence * 100)) if bpm_result else None
        genre_confidence_score = min(100, int(genre_result.confidence * 100)) if genre_result else None

        # Create AudioFeatures with Essentia BPM
        return AudioFeatures(
            file_path=file_path,
            duration_seconds=float(duration),
            sample_rate=int(sr),
            num_channels=num_channels,
            num_samples=int(num_samples),
            bpm=bpm_result.bpm if bpm_result else None,
            bpm_confidence=bpm_confidence_score,
            key=key,
            scale=scale,
            sample_type=sample_type,
            genre=genre_result.primary_genre if genre_result else None,
            genre_confidence=genre_confidence_score,
            spectral_centroid=spectral_centroid,
            spectral_bandwidth=spectral_bandwidth,
            spectral_rolloff=spectral_rolloff,
            spectral_flatness=spectral_flatness,
            zero_crossing_rate=zero_crossing_rate,
            rms_energy=rms_energy,
            harmonic_ratio=harmonic_ratio,
            mfcc_mean=mfcc_mean,
            mfcc_std=mfcc_std,
            chroma_mean=chroma_mean,
            chroma_std=chroma_std,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            # Add metadata about analysis
            metadata={
                "analyzer": "essentia",
                "bpm_method": method,
                "bpm_raw": bpm_result.bpm if bpm_result else None,
                "bpm_confidence_raw": bpm_result.confidence if bpm_result else None,
                "genre": genre_result.primary_genre if genre_result else None,
                "genre_confidence_raw": genre_result.confidence if genre_result else None,
                "sp404_category": genre_result.sp404_category if genre_result else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    async def _analyze_with_librosa(self, file_path: Path) -> AudioFeatures:
        """
        Analyze audio file using librosa (fallback or primary).

        This is the original librosa-based implementation, used either as:
        1. Primary analyzer (when Essentia disabled)
        2. Fallback analyzer (when Essentia fails)

        Args:
            file_path: Path to audio file

        Returns:
            AudioFeatures with librosa-derived features

        Raises:
            AudioError: If librosa analysis fails
        """
        # Check librosa availability
        if not LIBROSA_AVAILABLE:
            raise AudioError(
                message="librosa library not available. Install with: pip install librosa soundfile",
                file_path=file_path
            )

        try:
            # Log which mode we're in
            if self.analyzer_type == "essentia":
                logger.info(f"Using librosa fallback for {file_path.name}")
            else:
                logger.debug(f"Using librosa for {file_path.name}")

            # Run CPU-intensive analysis in thread pool
            features = await asyncio.to_thread(self._analyze_sync, file_path)
            return features

        except AudioError:
            # Re-raise AudioError as-is
            raise

        except Exception as e:
            # Wrap any other exceptions in AudioError
            raise AudioError(
                message=f"Failed to analyze audio file: {str(e)}",
                file_path=file_path,
                original_error=e
            )

    def _analyze_sync(self, file_path: Path) -> AudioFeatures:
        """
        Synchronous audio analysis implementation.

        This method performs CPU-intensive work and should be called
        via asyncio.to_thread() to avoid blocking the event loop.

        Args:
            file_path: Path to the audio file

        Returns:
            AudioFeatures with extracted features
        """
        try:
            # Detect sample type early (before heavy processing)
            from app.utils.audio_utils import detect_sample_type
            sample_type = detect_sample_type(file_path)
            logger.info(f"Sample type detected: {sample_type} for {file_path.name}")

            # Load audio file
            y, sr = librosa.load(str(file_path), sr=None, mono=False)

            # Handle stereo vs mono
            if y.ndim > 1:
                num_channels = y.shape[0]
                # Convert to mono for analysis
                y_mono = librosa.to_mono(y)
            else:
                num_channels = 1
                y_mono = y

            # Extract basic properties
            duration = librosa.get_duration(y=y_mono, sr=sr)
            num_samples = len(y_mono)

            # Extract features with graceful error handling
            bpm = self._extract_bpm(y_mono, sr, sample_type)
            key, scale = self._extract_key(y_mono, sr)

            spectral_centroid = self._extract_spectral_centroid(y_mono, sr)
            spectral_bandwidth = self._extract_spectral_bandwidth(y_mono, sr)
            spectral_rolloff = self._extract_spectral_rolloff(y_mono, sr)
            spectral_flatness = self._extract_spectral_flatness(y_mono, sr)

            zero_crossing_rate = self._extract_zero_crossing_rate(y_mono)
            rms_energy = self._extract_rms_energy(y_mono)

            harmonic_ratio = self._extract_harmonic_ratio(y_mono, sr)

            mfcc_mean, mfcc_std = self._extract_mfcc(y_mono, sr)
            chroma_mean, chroma_std = self._extract_chroma(y_mono, sr)

            # Default moderate confidence for librosa (65%) since it lacks built-in confidence scores
            bpm_confidence_score = 65 if bpm is not None else None

            # Create AudioFeatures object
            return AudioFeatures(
                file_path=file_path,
                duration_seconds=float(duration),
                sample_rate=int(sr),
                num_channels=num_channels,
                num_samples=int(num_samples),
                bpm=bpm,
                bpm_confidence=bpm_confidence_score,
                key=key,
                scale=scale,
                sample_type=sample_type,
                spectral_centroid=spectral_centroid,
                spectral_bandwidth=spectral_bandwidth,
                spectral_rolloff=spectral_rolloff,
                spectral_flatness=spectral_flatness,
                zero_crossing_rate=zero_crossing_rate,
                rms_energy=rms_energy,
                harmonic_ratio=harmonic_ratio,
                mfcc_mean=mfcc_mean,
                mfcc_std=mfcc_std,
                chroma_mean=chroma_mean,
                chroma_std=chroma_std,
                extraction_timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "analyzer": "librosa",
                    "bpm_method": "beat_track",
                    "sample_type": sample_type,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        except Exception as e:
            # This will be caught by analyze_file and wrapped in AudioError
            raise

    def _get_tempo_prior(self, sample_type: str = "loop") -> Optional[object]:
        """Create custom prior distribution for tempo estimation.

        Biases detection toward common hip-hop tempos to reduce octave errors:
        - 90 BPM (boom bap, lo-fi)
        - 105 BPM (classic hip-hop)
        - 115 BPM (mid-tempo)
        - 140 BPM (trap)
        - 170 BPM (double-time)

        Args:
            sample_type: "loop" or "one-shot"

        Returns:
            Prior distribution object for librosa.beat.beat_track, or None

        Note:
            Custom prior is currently disabled due to librosa API changes.
            Relying on octave correction in validate_bpm() instead.
        """
        # TODO: Implement scipy.stats distribution object for librosa 0.10+
        # For now, rely on octave correction logic in validate_bpm()
        return None

    def _extract_bpm(self, y: np.ndarray, sr: int, sample_type: str = "loop") -> Optional[float]:
        """Extract BPM (tempo) from audio with custom prior and octave error correction.

        Args:
            y: Audio time series
            sr: Sample rate
            sample_type: "one-shot" or "loop" for appropriate validation

        Returns:
            Corrected BPM or None if extraction fails
        """
        try:
            from app.utils.bpm_validation import validate_bpm

            # Log input parameters at DEBUG level
            duration = len(y) / sr
            logger.debug(f"BPM extraction: sample_type={sample_type}, duration={duration:.2f}s")

            # Get custom prior for sample type
            prior = self._get_tempo_prior(sample_type)

            # Log prior usage at DEBUG level
            if prior is not None:
                logger.debug(f"Using custom prior for {sample_type}")
            else:
                logger.debug(f"Using default librosa prior (custom prior disabled)")

            # Run beat tracking with prior
            if prior is not None:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr, prior=prior)
            else:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # Extract scalar BPM
            if isinstance(tempo, np.ndarray):
                raw_bpm = float(tempo[0]) if len(tempo) > 0 else None
            else:
                raw_bpm = float(tempo)

            if raw_bpm is None or raw_bpm == 0.0:
                logger.debug("BPM detection returned None or 0.0")
                return None

            # Log raw BPM detected at DEBUG level
            logger.debug(f"Raw BPM detected: {raw_bpm:.1f}")

            # Apply octave correction and validation
            corrected_bpm, was_corrected = validate_bpm(raw_bpm, sample_type)

            # Log validation results at DEBUG level
            logger.debug(f"Validation result: corrected_bpm={corrected_bpm:.1f}, was_corrected={was_corrected}")

            # Check if corrected BPM is valid (Pydantic validator requires 20-300)
            if corrected_bpm < 20 or corrected_bpm > 300:
                logger.warning(f"BPM {corrected_bpm} outside valid range (20-300), returning None")
                return None

            # Log octave corrections at INFO level
            if was_corrected:
                # Determine correction type
                if corrected_bpm > raw_bpm:
                    multiplier = corrected_bpm / raw_bpm
                    correction_type = f"multiplied by {multiplier:.1f}x"
                else:
                    divisor = raw_bpm / corrected_bpm
                    correction_type = f"divided by {divisor:.1f}x"

                logger.info(
                    f"BPM corrected ({correction_type}): "
                    f"{raw_bpm:.1f} → {corrected_bpm:.1f}"
                )
            else:
                logger.debug(f"BPM validated (no correction): {corrected_bpm:.1f}")

            # Track statistics
            self._bpm_stats['total'] += 1
            if was_corrected:
                self._bpm_stats['corrected'] += 1
                # Track specific correction type
                correction_key = f"{raw_bpm:.0f}→{corrected_bpm:.0f}"
                self._bpm_stats['correction_types'][correction_key] = \
                    self._bpm_stats['correction_types'].get(correction_key, 0) + 1
            if prior is not None:
                self._bpm_stats['prior_used'] += 1

            return corrected_bpm

        except Exception as e:
            logger.error(f"BPM extraction failed: {e}", exc_info=True)
            return None

    def get_bpm_correction_stats(self) -> dict:
        """Get statistics on BPM corrections.

        Returns:
            Dictionary with correction statistics:
            - total_analyzed: Total samples processed
            - corrections_applied: Number of corrections made
            - correction_rate: Percentage of samples corrected (0.0-1.0)
            - correction_types: Breakdown of correction types (e.g., "26→104": 3)
            - prior_usage_rate: Percentage of samples using custom prior (0.0-1.0)
            - prior_used_count: Number of samples using custom prior

        Example:
            >>> service = AudioFeaturesService()
            >>> # ... analyze some files ...
            >>> stats = service.get_bpm_correction_stats()
            >>> print(f"Analyzed {stats['total_analyzed']} samples")
            >>> print(f"Correction rate: {stats['correction_rate']:.1%}")
        """
        total = self._bpm_stats.get('total', 0)
        corrected = self._bpm_stats.get('corrected', 0)
        prior_used = self._bpm_stats.get('prior_used', 0)

        return {
            'total_analyzed': total,
            'corrections_applied': corrected,
            'correction_rate': corrected / total if total > 0 else 0.0,
            'correction_types': self._bpm_stats.get('correction_types', {}),
            'prior_usage_rate': prior_used / total if total > 0 else 0.0,
            'prior_used_count': prior_used
        }

    def _extract_key(self, y: np.ndarray, sr: int) -> tuple[Optional[str], Optional[str]]:
        """
        Extract musical key and scale from audio.

        Uses chroma features to estimate the key.

        Returns:
            Tuple of (key, scale) where both can be None if detection fails
        """
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Average chroma across time
            chroma_mean = np.mean(chroma, axis=1)

            # Find the most prominent pitch class
            key_index = np.argmax(chroma_mean)

            # Map to note names
            keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            key = keys[key_index]

            # Simple major/minor detection based on chroma profile
            # This is a simplified heuristic
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])

            # Rotate profiles to match detected key
            rotated_major = np.roll(major_profile, key_index)
            rotated_minor = np.roll(minor_profile, key_index)

            # Correlate with chroma
            major_correlation = np.corrcoef(chroma_mean, rotated_major)[0, 1]
            minor_correlation = np.corrcoef(chroma_mean, rotated_minor)[0, 1]

            scale = "major" if major_correlation > minor_correlation else "minor"

            return key, scale

        except Exception as e:
            logger.warning(f"Key extraction failed: {e}")
            return None, None

    def _extract_spectral_centroid(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Extract average spectral centroid."""
        try:
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            return float(np.mean(centroid))
        except Exception as e:
            logger.warning(f"Spectral centroid extraction failed: {e}")
            return None

    def _extract_spectral_bandwidth(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Extract average spectral bandwidth."""
        try:
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            return float(np.mean(bandwidth))
        except Exception as e:
            logger.warning(f"Spectral bandwidth extraction failed: {e}")
            return None

    def _extract_spectral_rolloff(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Extract average spectral rolloff."""
        try:
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            return float(np.mean(rolloff))
        except Exception as e:
            logger.warning(f"Spectral rolloff extraction failed: {e}")
            return None

    def _extract_spectral_flatness(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Extract average spectral flatness."""
        try:
            flatness = librosa.feature.spectral_flatness(y=y)
            return float(np.mean(flatness))
        except Exception as e:
            logger.warning(f"Spectral flatness extraction failed: {e}")
            return None

    def _extract_zero_crossing_rate(self, y: np.ndarray) -> Optional[float]:
        """Extract average zero crossing rate."""
        try:
            zcr = librosa.feature.zero_crossing_rate(y)
            return float(np.mean(zcr))
        except Exception as e:
            logger.warning(f"Zero crossing rate extraction failed: {e}")
            return None

    def _extract_rms_energy(self, y: np.ndarray) -> Optional[float]:
        """Extract average RMS energy."""
        try:
            rms = librosa.feature.rms(y=y)
            return float(np.mean(rms))
        except Exception as e:
            logger.warning(f"RMS energy extraction failed: {e}")
            return None

    def _extract_harmonic_ratio(self, y: np.ndarray, sr: int) -> Optional[float]:
        """
        Extract ratio of harmonic to percussive content.

        Returns value between 0 and 1 where:
        - Values close to 1 indicate more harmonic content
        - Values close to 0 indicate more percussive content
        """
        try:
            # Separate harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Calculate energy in each component
            harmonic_energy = np.sum(y_harmonic ** 2)
            percussive_energy = np.sum(y_percussive ** 2)

            # Calculate ratio
            total_energy = harmonic_energy + percussive_energy
            if total_energy > 0:
                return float(harmonic_energy / total_energy)
            return None

        except Exception as e:
            logger.warning(f"Harmonic ratio extraction failed: {e}")
            return None

    def _extract_mfcc(self, y: np.ndarray, sr: int) -> tuple[Optional[list], Optional[list]]:
        """
        Extract MFCC (Mel-frequency cepstral coefficients) features.

        Returns:
            Tuple of (mean, std) where each is a list of 13 coefficients
        """
        try:
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1).tolist()
            mfcc_std = np.std(mfcc, axis=1).tolist()
            return mfcc_mean, mfcc_std
        except Exception as e:
            logger.warning(f"MFCC extraction failed: {e}")
            return None, None

    def _extract_chroma(self, y: np.ndarray, sr: int) -> tuple[Optional[list], Optional[list]]:
        """
        Extract chroma features.

        Returns:
            Tuple of (mean, std) where each is a list of 12 pitch classes
        """
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1).tolist()
            chroma_std = np.std(chroma, axis=1).tolist()
            return chroma_mean, chroma_std
        except Exception as e:
            logger.warning(f"Chroma extraction failed: {e}")
            return None, None
