"""
Essentia-based audio analysis service for high-accuracy BPM detection.

Provides commercial-grade audio analysis (90-95% BPM accuracy) using Essentia's
RhythmExtractor2013 algorithm. Falls back gracefully when Essentia is unavailable.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
from pydantic import BaseModel

from app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from essentia.standard import (
        MonoLoader,
        RhythmExtractor2013,
        TensorflowPredictMAEST,
        TensorflowPredict
    )

logger = logging.getLogger(__name__)


class BPMResult(BaseModel):
    """BPM analysis result from Essentia.

    Attributes:
        bpm: Detected tempo in beats per minute
        confidence: Overall confidence score (0.0 to 1.0)
        beats: List of beat timestamps in seconds
        beat_intervals: List of intervals between beats in seconds
        algorithm: Name of the detection algorithm used
    """
    bpm: float
    confidence: float
    beats: List[float]
    beat_intervals: List[float]
    algorithm: str = "essentia_rhythm_extractor_2013"


class GenreResult(BaseModel):
    """Genre classification result from Essentia.

    Attributes:
        primary_genre: Top predicted genre label
        confidence: Confidence score for primary genre (0.0 to 1.0)
        top_3_genres: List of top 3 (genre, confidence) tuples
        sp404_category: Mapped SP-404 production category
        all_predictions: Dict of all predictions above threshold
    """
    primary_genre: str
    confidence: float
    top_3_genres: List[tuple]  # [(genre, confidence), ...]
    sp404_category: str
    all_predictions: Dict[str, float]


class EssentiaAnalyzer:
    """Essentia-based audio analysis service.

    Provides high-accuracy BPM detection using Essentia's RhythmExtractor2013
    algorithm. Designed for SP-404MK2 sample analysis workflow.

    Features:
    - 90-95% BPM detection accuracy
    - Confidence scoring for each analysis
    - Beat position and interval extraction
    - Adaptive method selection based on sample duration

    Raises:
        ImportError: If Essentia is not available at initialization
    """

    def __init__(self):
        """Initialize the Essentia analyzer.

        Raises:
            ImportError: If Essentia library is not available
        """
        if not ESSENTIA_AVAILABLE:
            raise ImportError(
                "Essentia not available. Install with: pip install essentia"
            )

        self.sample_rate = 44100
        self._genre_models: Optional[Dict[str, str]] = None  # Lazy-loaded
        self._genre_mapping: Optional[dict] = None  # Lazy-loaded
        self._genre_labels: Optional[List[str]] = None  # Lazy-loaded
        logger.info("EssentiaAnalyzer initialized with sample_rate=44100")

    def _load_audio(self, audio_path: Path) -> np.ndarray:
        """Load audio file with Essentia MonoLoader.

        Args:
            audio_path: Path to audio file

        Returns:
            Audio samples as numpy array (mono, 44.1kHz)

        Raises:
            RuntimeError: If audio file cannot be loaded
        """
        try:
            loader = MonoLoader(
                filename=str(audio_path),
                sampleRate=self.sample_rate,
                resampleQuality=4  # High quality resampling
            )
            audio = loader()
            logger.debug(f"Loaded audio: {len(audio)} samples at {self.sample_rate}Hz")
            return audio

        except Exception as e:
            logger.error(f"Failed to load audio file {audio_path}: {e}")
            raise RuntimeError(f"Audio loading failed: {e}") from e

    async def analyze_bpm(
        self,
        audio_path: Path,
        method: str = "multifeature"
    ) -> Optional[BPMResult]:
        """Extract BPM using RhythmExtractor2013.

        Performs high-accuracy BPM detection using Essentia's state-of-the-art
        rhythm extraction algorithm. Runs in thread pool to avoid blocking.

        Args:
            audio_path: Path to audio file
            method: Detection method - 'multifeature' (accurate, slow) or
                   'degara' (fast). Default: 'multifeature'

        Returns:
            BPMResult with BPM, confidence, and beat positions, or None on failure

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> result = await analyzer.analyze_bpm(Path("sample.wav"))
            >>> print(f"BPM: {result.bpm:.1f}, Confidence: {result.confidence:.2f}")
        """
        try:
            # Run CPU-intensive analysis in thread pool
            result = await asyncio.to_thread(
                self._analyze_bpm_sync,
                audio_path,
                method
            )
            return result

        except Exception as e:
            logger.error(f"Essentia BPM analysis failed for {audio_path}: {e}")
            return None

    def _analyze_bpm_sync(
        self,
        audio_path: Path,
        method: str
    ) -> BPMResult:
        """Synchronous BPM analysis implementation.

        This method performs CPU-intensive work and should be called
        via asyncio.to_thread() to avoid blocking the event loop.

        Args:
            audio_path: Path to audio file
            method: Detection method ('multifeature' or 'degara')

        Returns:
            BPMResult with extracted rhythm features

        Raises:
            Exception: If rhythm extraction fails
        """
        # Load audio
        audio = self._load_audio(audio_path)

        # Create rhythm extractor with specified method
        extractor = RhythmExtractor2013(method=method)

        # Extract rhythm features
        # Returns: (bpm, beats, beats_confidence, _, beats_intervals)
        bpm, beats, beats_confidence, _, beats_intervals = extractor(audio)

        # Calculate overall confidence as mean of beat confidences
        # beats_confidence can be a scalar or array depending on Essentia version
        if isinstance(beats_confidence, (int, float)):
            confidence = float(beats_confidence)
        elif hasattr(beats_confidence, '__len__') and len(beats_confidence) > 0:
            confidence = float(np.mean(beats_confidence))
        else:
            confidence = 0.0

        logger.info(
            f"Essentia BPM: {bpm:.1f} BPM "
            f"(confidence: {confidence:.2f}, "
            f"method: {method}, "
            f"beats: {len(beats)})"
        )

        return BPMResult(
            bpm=float(bpm),
            confidence=confidence,
            beats=beats.tolist(),
            beat_intervals=beats_intervals.tolist(),
            algorithm=f"essentia_rhythm_extractor_2013_{method}"
        )

    def get_recommended_method(self, duration: float) -> str:
        """Recommend analysis method based on audio duration.

        Chooses between accuracy and speed based on sample length:
        - Short samples (<30s): Use 'multifeature' for maximum accuracy
        - Long samples (>=30s): Use 'degara' for faster processing

        Args:
            duration: Audio duration in seconds

        Returns:
            Recommended method name ('multifeature' or 'degara')

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> method = analyzer.get_recommended_method(10.5)
            >>> print(method)  # 'multifeature'
            >>> method = analyzer.get_recommended_method(45.0)
            >>> print(method)  # 'degara'
        """
        # For SP-404MK2 samples, most will be short (<30s)
        # Use multifeature for accuracy on short samples
        # Use degara for speed on longer samples
        method = "multifeature" if duration < 30 else "degara"
        logger.debug(f"Recommended method for {duration:.1f}s: {method}")
        return method

    def _load_genre_models(self) -> Dict[str, str]:
        """Lazy load genre classification models.

        Loads model file paths on first access. Models are not loaded into memory
        until genre classification is actually performed, keeping memory usage low
        when only BPM analysis is needed.

        Returns:
            Dictionary with 'embedding' and 'genre' model paths

        Raises:
            FileNotFoundError: If model files are not found in expected location

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> models = analyzer._load_genre_models()
            >>> print(models['embedding'])  # Path to embedding model
        """
        # Return cached models if already loaded
        if self._genre_models is not None:
            return self._genre_models

        # Determine models directory (relative to this file)
        backend_dir = Path(__file__).parent.parent.parent
        models_dir = backend_dir / "models" / "essentia"

        # Define expected model files
        embedding_path = models_dir / "discogs-maest-30s-pw-519l-2.pb"
        genre_path = models_dir / "genre_discogs519-discogs-maest-30s-pw-519l-1.pb"

        # Check if models exist
        if not embedding_path.exists() or not genre_path.exists():
            logger.error(f"Genre models not found in {models_dir}")
            raise FileNotFoundError(
                f"Essentia genre models not found.\n"
                f"Expected location: {models_dir}\n"
                f"Missing files:\n"
                f"  - {embedding_path.name}: {'✓' if embedding_path.exists() else '✗'}\n"
                f"  - {genre_path.name}: {'✓' if genre_path.exists() else '✗'}\n\n"
                f"To download models, run:\n"
                f"  python backend/scripts/download_essentia_models.py"
            )

        # Cache and return model paths
        self._genre_models = {
            "embedding": str(embedding_path),
            "genre": str(genre_path)
        }

        logger.info(
            f"Genre models loaded from {models_dir} "
            f"(embedding: {embedding_path.stat().st_size / (1024*1024):.1f}MB, "
            f"genre: {genre_path.stat().st_size / (1024*1024):.1f}MB)"
        )

        return self._genre_models

    def _load_genre_mapping(self) -> dict:
        """Lazy load genre mapping configuration.

        Loads the JSON configuration that maps Essentia's 519 Discogs genres
        to 10 SP-404 production categories.

        Returns:
            Genre mapping configuration dictionary

        Raises:
            FileNotFoundError: If genre_mapping.json is not found

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> mapping = analyzer._load_genre_mapping()
            >>> print(mapping['sp404_categories'].keys())  # SP-404 categories
        """
        # Return cached mapping if already loaded
        if self._genre_mapping is not None:
            return self._genre_mapping

        # Determine config directory (relative to this file)
        backend_dir = Path(__file__).parent.parent.parent
        config_path = backend_dir / "config" / "genre_mapping.json"

        if not config_path.exists():
            logger.error(f"Genre mapping not found at {config_path}")
            raise FileNotFoundError(
                f"Genre mapping configuration not found.\n"
                f"Expected location: {config_path}\n"
                f"This file should be included in the repository."
            )

        # Load and cache configuration
        with open(config_path, 'r') as f:
            self._genre_mapping = json.load(f)

        logger.debug(
            f"Genre mapping loaded: {len(self._genre_mapping['sp404_categories'])} "
            f"SP-404 categories"
        )

        return self._genre_mapping

    def _load_genre_labels(self) -> List[str]:
        """Lazy load genre labels list.

        Loads the 519 Discogs genre labels from JSON configuration.

        Returns:
            List of genre label strings (length 519)

        Raises:
            FileNotFoundError: If genre labels JSON is not found

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> labels = analyzer._load_genre_labels()
            >>> print(len(labels))  # 519
            >>> print(labels[0])  # First genre label
        """
        # Return cached labels if already loaded
        if self._genre_labels is not None:
            return self._genre_labels

        # Determine config directory (relative to this file)
        backend_dir = Path(__file__).parent.parent.parent
        labels_path = backend_dir / "config" / "genre_discogs519_labels.json"

        if not labels_path.exists():
            logger.error(f"Genre labels not found at {labels_path}")
            raise FileNotFoundError(
                f"Genre labels file not found.\n"
                f"Expected location: {labels_path}\n"
                f"This file should be included in the repository."
            )

        # Load and cache labels
        with open(labels_path, 'r') as f:
            data = json.load(f)
            self._genre_labels = data['labels']

        logger.debug(
            f"Genre labels loaded: {len(self._genre_labels)} categories "
            f"(version: {data.get('version', 'unknown')})"
        )

        return self._genre_labels

    def _get_genre_label(self, index: int) -> str:
        """Map genre prediction index to label name.

        Args:
            index: Genre index (0-518)

        Returns:
            Genre label string

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> label = analyzer._get_genre_label(0)
            >>> print(label)  # 'abstract'
        """
        labels = self._load_genre_labels()

        # Handle out of bounds gracefully
        if index < 0 or index >= len(labels):
            logger.warning(f"Genre index {index} out of range [0, {len(labels)-1}]")
            return f"unknown_{index}"

        return labels[index]

    def _map_to_sp404_category(self, genre: str) -> str:
        """Map Essentia genre label to SP-404 production category.

        Matches genre string against category keywords from genre_mapping.json
        to determine the most appropriate SP-404 production category.

        Args:
            genre: Genre label from Essentia classification

        Returns:
            SP-404 category name (e.g., "Hip-Hop/Trap", "Electronic", etc.)

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> category = analyzer._map_to_sp404_category("boom bap")
            >>> print(category)  # "Hip-Hop/Trap"
            >>> category = analyzer._map_to_sp404_category("techno")
            >>> print(category)  # "Electronic"
        """
        mapping = self._load_genre_mapping()

        # Convert genre to lowercase for case-insensitive matching
        genre_lower = genre.lower()

        # Check each SP-404 category's keywords
        for category, keywords in mapping["sp404_categories"].items():
            # Check if any keyword matches the genre
            for keyword in keywords:
                if keyword.lower() in genre_lower or genre_lower in keyword.lower():
                    logger.debug(f"Mapped '{genre}' → '{category}' (keyword: '{keyword}')")
                    return category

        # Default category if no match found
        logger.debug(f"No mapping found for '{genre}', using 'Experimental'")
        return "Experimental"

    def models_available(self) -> bool:
        """Check if genre classification models are available.

        Returns:
            True if models can be loaded, False otherwise

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> if analyzer.models_available():
            ...     print("Genre classification ready")
            ... else:
            ...     print("Download models first")
        """
        try:
            self._load_genre_models()
            return True
        except FileNotFoundError:
            return False

    async def analyze_genre(
        self,
        audio_path: Path
    ) -> Optional[GenreResult]:
        """Classify genre using pre-trained TensorFlow models.

        Performs two-stage genre classification:
        1. Extract embeddings with TensorflowPredictMAEST (16kHz audio)
        2. Classify with TensorflowPredict (519 Discogs genres)

        Note: Model requires 30 seconds of audio minimum. Shorter audio
        will be padded with silence.

        Args:
            audio_path: Path to audio file

        Returns:
            GenreResult with primary genre, confidence, and top predictions,
            or None on failure

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> result = await analyzer.analyze_genre(Path("sample.wav"))
            >>> print(f"Genre: {result.primary_genre}")
            >>> print(f"SP-404 Category: {result.sp404_category}")
            >>> print(f"Top 3: {result.top_3_genres}")
        """
        try:
            # Run CPU-intensive analysis in thread pool
            result = await asyncio.to_thread(
                self._analyze_genre_sync,
                audio_path
            )
            return result

        except Exception as e:
            logger.error(f"Essentia genre classification failed for {audio_path}: {e}")
            return None

    def _analyze_genre_sync(self, audio_path: Path) -> GenreResult:
        """Synchronous genre classification implementation.

        This method performs CPU-intensive TensorFlow inference and should be
        called via asyncio.to_thread() to avoid blocking the event loop.

        Args:
            audio_path: Path to audio file

        Returns:
            GenreResult with classification results

        Raises:
            Exception: If genre classification fails
        """
        # Load models (lazy loading)
        models = self._load_genre_models()
        mapping = self._load_genre_mapping()
        labels = self._load_genre_labels()

        # Load audio at 16kHz (required by MAEST model)
        loader = MonoLoader(
            filename=str(audio_path),
            sampleRate=16000,
            resampleQuality=4
        )
        audio = loader()
        logger.debug(f"Loaded audio: {len(audio)} samples at 16kHz ({len(audio)/16000:.2f}s)")

        # MAEST model requires 30 seconds minimum
        min_samples = 16000 * 30  # 30 seconds at 16kHz
        if len(audio) < min_samples:
            # Pad with silence
            padding = min_samples - len(audio)
            audio = np.pad(audio, (0, padding), mode='constant')
            logger.debug(f"Padded audio to 30s (added {padding} silent samples)")

        # Stage 1: Extract embeddings with MAEST
        embedding_model = TensorflowPredictMAEST(
            graphFilename=models["embedding"],
            output="PartitionedCall/Identity_12"
        )
        embeddings = embedding_model(audio)
        logger.debug(f"Extracted embeddings: shape {embeddings.shape}, type: {type(embeddings)}")

        # Ensure embeddings is the correct type (should be essentia array)
        # The genre model expects embeddings as a pool
        # Convert numpy array to list for TensorflowPredict
        if isinstance(embeddings, np.ndarray):
            embeddings_list = embeddings.tolist()
            logger.debug(f"Converted embeddings to list: {len(embeddings_list)} values")
        else:
            embeddings_list = embeddings

        # Stage 2: Classify genre
        genre_model = TensorflowPredict(
            graphFilename=models["genre"],
            inputs=["embeddings"],
            outputs=["PartitionedCall/model_8/activations/Sigmoid"]
        )
        predictions = genre_model(embeddings)
        logger.debug(f"Genre predictions: {len(predictions)} categories")

        # Get top 3 predictions
        top_3_indices = np.argsort(predictions)[-3:][::-1]
        top_3_genres = [
            (self._get_genre_label(int(idx)), float(predictions[idx]))
            for idx in top_3_indices
        ]

        # Extract primary genre
        primary_genre, primary_confidence = top_3_genres[0]

        # Map to SP-404 category
        sp404_category = self._map_to_sp404_category(primary_genre)

        # Collect all predictions above threshold
        threshold = mapping["confidence_threshold"]
        all_predictions = {
            self._get_genre_label(i): float(predictions[i])
            for i in range(len(predictions))
            if predictions[i] > threshold
        }

        logger.info(
            f"Genre: {primary_genre} → {sp404_category} "
            f"(confidence: {primary_confidence:.3f}, "
            f"top-3: {[g for g, _ in top_3_genres]})"
        )

        return GenreResult(
            primary_genre=primary_genre,
            confidence=primary_confidence,
            top_3_genres=top_3_genres,
            sp404_category=sp404_category,
            all_predictions=all_predictions
        )

    async def analyze_full(self, audio_path: Path) -> dict:
        """Complete audio analysis combining BPM and genre classification.

        Performs both BPM detection and genre classification in parallel,
        returning a unified result dict. Handles partial failures gracefully
        (e.g., BPM succeeds but genre fails).

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with:
                - bpm: BPMResult or None
                - genre: GenreResult or None
                - analyzer: "essentia"
                - success: bool (True if at least one analysis succeeded)

        Examples:
            >>> analyzer = EssentiaAnalyzer()
            >>> result = await analyzer.analyze_full(Path("sample.wav"))
            >>> if result['bpm']:
            ...     print(f"BPM: {result['bpm'].bpm}")
            >>> if result['genre']:
            ...     print(f"Genre: {result['genre'].primary_genre}")
        """
        # Run analyses in parallel
        bpm_task = self.analyze_bpm(audio_path)
        genre_task = self.analyze_genre(audio_path)

        bpm_result, genre_result = await asyncio.gather(
            bpm_task,
            genre_task,
            return_exceptions=True
        )

        # Handle exceptions
        if isinstance(bpm_result, Exception):
            logger.error(f"BPM analysis exception: {bpm_result}")
            bpm_result = None

        if isinstance(genre_result, Exception):
            logger.error(f"Genre analysis exception: {genre_result}")
            genre_result = None

        success = (bpm_result is not None) or (genre_result is not None)

        return {
            "bpm": bpm_result,
            "genre": genre_result,
            "analyzer": "essentia",
            "success": success
        }


# Example usage
async def example_usage():
    """Example usage of EssentiaAnalyzer."""
    if not ESSENTIA_AVAILABLE:
        print("Essentia not available")
        return

    analyzer = EssentiaAnalyzer()
    result = await analyzer.analyze_bpm(Path("sample.wav"))

    if result:
        print(f"BPM: {result.bpm:.1f}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Beats detected: {len(result.beats)}")
        print(f"Algorithm: {result.algorithm}")
