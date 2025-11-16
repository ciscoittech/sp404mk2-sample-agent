"""
SP404ExportService for converting and exporting samples to SP-404MK2 format.

Provides comprehensive export functionality including format conversion,
validation, filename sanitization, and organization strategies.
"""
import asyncio
import logging
import os
import re
import time
import unicodedata
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

try:
    import librosa
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sample import Sample
from app.models.kit import Kit, KitSample
from app.models.sp404_export import SP404Export, SP404ExportSample
from app.schemas.sp404_export import (
    ExportConfig,
    ConversionResult,
    ValidationResult,
    ExportResult,
    BatchExportResult,
)

logger = logging.getLogger(__name__)


class SP404ExportError(Exception):
    """Base exception for SP-404 export errors."""
    pass


class SP404ExportService:
    """
    Service for exporting samples in SP-404MK2 compatible format.

    Handles:
    - Audio conversion to 48kHz/16-bit WAV/AIFF
    - Sample validation (duration, format, readability)
    - Filename sanitization (ASCII-safe, hardware-compatible)
    - Organization strategies (flat, genre, BPM, kit)
    - Export tracking and history
    """

    # SP-404MK2 Hardware Requirements
    TARGET_SAMPLE_RATE = 48000
    TARGET_BIT_DEPTH = 16
    MIN_DURATION_MS = 100
    MAX_FILENAME_LENGTH = 255

    # Supported formats for input and output
    SUPPORTED_INPUT_FORMATS = {'.wav', '.aiff', '.aif', '.mp3', '.flac', '.m4a'}
    SUPPORTED_OUTPUT_FORMATS = {'wav', 'aiff'}

    # BPM ranges for organization
    BPM_RANGES = [
        (0, 70, "slow"),
        (70, 90, "70-90"),
        (90, 110, "90-110"),
        (110, 130, "110-130"),
        (130, 150, "130-150"),
        (150, 300, "fast")
    ]

    def __init__(self, db_session: Optional[AsyncSession]):
        """
        Initialize SP404ExportService.

        Args:
            db_session: SQLAlchemy async database session (can be None for conversion-only use)

        Raises:
            SP404ExportError: If required audio libraries not available
        """
        if not AUDIO_LIBS_AVAILABLE:
            raise SP404ExportError(
                "Required audio libraries not available. "
                "Install with: pip install librosa soundfile"
            )

        self.db = db_session

    async def convert_to_sp404_format(
        self,
        input_path: Path,
        output_path: Path,
        format: str = "wav"
    ) -> ConversionResult:
        """
        Convert audio file to SP-404MK2 compatible format (48kHz/16-bit).

        Uses librosa for sample rate conversion and soundfile for writing.
        Runs CPU-intensive work in thread pool to avoid blocking event loop.

        Args:
            input_path: Path to input audio file
            output_path: Path where converted file will be saved
            format: Output format - "wav" or "aiff"

        Returns:
            ConversionResult with details about the conversion

        Raises:
            SP404ExportError: If format unsupported
        """
        # Validate format
        if format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise SP404ExportError(
                f"Unsupported output format: {format}. "
                f"Supported: {', '.join(self.SUPPORTED_OUTPUT_FORMATS)}"
            )

        # Check if file exists
        if not input_path.exists():
            return ConversionResult(
                success=False,
                output_path=None,
                original_format=input_path.suffix.lower(),
                original_sample_rate=0,
                original_duration=0.0,
                error_message=f"Input file not found: {input_path}"
            )

        try:
            # Run conversion in thread pool (CPU-intensive)
            result = await asyncio.to_thread(
                self._convert_sync,
                input_path,
                output_path,
                format
            )

            logger.info(
                f"Converted {input_path.name}: "
                f"{result.original_sample_rate}Hz → {result.converted_sample_rate}Hz"
            )

            return result

        except Exception as e:
            logger.error(f"Conversion failed for {input_path}: {e}")
            return ConversionResult(
                success=False,
                output_path=None,
                original_format=input_path.suffix.lower(),
                original_sample_rate=0,
                original_duration=0.0,
                error_message=str(e)
            )

    def _convert_sync(
        self,
        input_path: Path,
        output_path: Path,
        format: str
    ) -> ConversionResult:
        """
        Synchronous audio conversion (runs in thread pool).

        Args:
            input_path: Input audio file
            output_path: Output file path
            format: Output format (wav/aiff)

        Returns:
            ConversionResult with conversion details
        """
        # Load audio file with librosa
        y, sr = librosa.load(str(input_path), sr=None, mono=False)

        # Store original properties
        original_format = input_path.suffix.lower()
        original_sr = sr

        # Calculate original duration
        if y.ndim > 1:
            # Stereo - use first channel for duration
            original_duration = len(y[0]) / sr
        else:
            original_duration = len(y) / sr

        # Resample if needed
        if sr != self.TARGET_SAMPLE_RATE:
            if y.ndim > 1:
                # Resample each channel separately for stereo
                y_resampled = np.array([
                    librosa.resample(
                        y[ch],
                        orig_sr=sr,
                        target_sr=self.TARGET_SAMPLE_RATE
                    )
                    for ch in range(y.shape[0])
                ])
            else:
                # Mono resampling
                y_resampled = librosa.resample(
                    y,
                    orig_sr=sr,
                    target_sr=self.TARGET_SAMPLE_RATE
                )
            y = y_resampled
            sr = self.TARGET_SAMPLE_RATE

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Transpose for soundfile (expects time x channels for stereo)
        if y.ndim > 1:
            y_transposed = y.T
        else:
            y_transposed = y

        # Write with soundfile (automatically handles 16-bit conversion)
        sf.write(
            str(output_path),
            y_transposed,
            sr,
            subtype='PCM_16',  # 16-bit PCM
            format=format.upper()
        )

        return ConversionResult(
            success=True,
            output_path=output_path,
            original_format=original_format,
            original_sample_rate=original_sr,
            original_duration=original_duration,
            converted_sample_rate=self.TARGET_SAMPLE_RATE,
        )

    def validate_sample(self, file_path: Path) -> ValidationResult:
        """
        Validate sample meets SP-404MK2 requirements.

        Checks:
        - File exists and is readable
        - Duration >= 100ms
        - File format is supported

        Args:
            file_path: Path to audio file to validate

        Returns:
            ValidationResult with validation details
        """
        errors = []

        # Check file exists
        if not file_path.exists():
            errors.append(f"File not found: {file_path}")
            return ValidationResult(
                valid=False,
                duration_ms=0,
                meets_duration_requirement=False,
                format_supported=False,
                file_readable=False,
                errors=errors
            )

        # Check file is readable
        try:
            file_readable = file_path.is_file() and os.access(file_path, os.R_OK)
        except Exception as e:
            file_readable = False
            errors.append(f"File not readable: {e}")

        # Check format
        file_ext = file_path.suffix.lower()
        format_supported = file_ext in self.SUPPORTED_INPUT_FORMATS
        if not format_supported:
            errors.append(
                f"Unsupported format: {file_ext}. "
                f"Supported: {', '.join(self.SUPPORTED_INPUT_FORMATS)}"
            )

        # Check duration (requires audio loading)
        duration_ms = 0
        meets_duration = False

        if file_readable and format_supported:
            try:
                # Quick duration check
                duration_seconds = librosa.get_duration(path=str(file_path))
                duration_ms = duration_seconds * 1000
                meets_duration = duration_ms >= self.MIN_DURATION_MS

                if not meets_duration:
                    errors.append(
                        f"Duration too short: {duration_ms:.1f}ms "
                        f"(minimum: {self.MIN_DURATION_MS}ms)"
                    )
            except Exception as e:
                errors.append(f"Could not determine duration: {e}")

        valid = len(errors) == 0

        return ValidationResult(
            valid=valid,
            duration_ms=duration_ms,
            meets_duration_requirement=meets_duration,
            format_supported=format_supported,
            file_readable=file_readable,
            errors=errors
        )

    def sanitize_filename(self, filename: str, max_length: int = 255) -> str:
        """
        Make filename SP-404MK2 compatible.

        SP-404MK2 requirements:
        - ASCII-safe characters only (double-byte chars may not display)
        - No special characters that cause filesystem issues
        - Reasonable length (max 255 chars)

        Rules applied:
        1. Normalize unicode to ASCII equivalents
        2. Replace spaces with underscores
        3. Remove non-ASCII and special characters
        4. Limit length to max_length
        5. Ensure filename doesn't start with dot or dash

        Args:
            filename: Original filename (with or without extension)
            max_length: Maximum filename length (default 255)

        Returns:
            Sanitized ASCII-safe filename
        """
        # Split extension
        path = Path(filename)
        name = path.stem
        ext = path.suffix

        # 1. Normalize unicode to ASCII (é → e, etc.)
        name = unicodedata.normalize('NFKD', name)
        name = name.encode('ASCII', 'ignore').decode('ASCII')

        # 2. Replace spaces with underscores
        name = name.replace(' ', '_')

        # 3. Remove special characters (keep alphanumeric, underscore, hyphen)
        name = re.sub(r'[^a-zA-Z0-9_\-]', '', name)

        # 4. Remove consecutive underscores/hyphens
        name = re.sub(r'[_\-]+', '_', name)

        # 5. Strip leading/trailing special chars
        name = name.strip('.-_')

        # 6. Ensure we have something left
        if not name:
            name = "sample"

        # 7. Limit length (accounting for extension)
        max_name_length = max_length - len(ext)
        if len(name) > max_name_length:
            name = name[:max_name_length]

        # Reconstruct filename
        sanitized = f"{name}{ext}"

        logger.debug(f"Sanitized filename: '{filename}' → '{sanitized}'")

        return sanitized

    async def export_single_sample(
        self,
        sample_id: int,
        config: ExportConfig,
        db: Optional[AsyncSession] = None,
        track_export: bool = True
    ) -> ExportResult:
        """
        Export single sample to SP-404MK2 format.

        Process:
        1. Retrieve sample from database
        2. Validate sample meets requirements
        3. Sanitize filename
        4. Determine output path based on organization
        5. Convert to target format
        6. Track export in database
        7. Return result

        Args:
            sample_id: Database ID of sample to export
            config: Export configuration (format, organization, etc.)
            db: Database session (uses self.db if not provided)

        Returns:
            ExportResult with export details

        Raises:
            SP404ExportError: If sample not found or export fails
        """
        if db is None:
            db = self.db

        start_time = time.time()

        # 1. Get sample
        stmt = select(Sample).where(Sample.id == sample_id)
        result = await db.execute(stmt)
        sample = result.scalar_one_or_none()

        if not sample:
            raise SP404ExportError(f"Sample {sample_id} not found")

        # 2. Validate
        input_path = Path(sample.file_path)
        validation = self.validate_sample(input_path)

        if not validation.valid:
            return ExportResult(
                success=False,
                sample_id=sample_id,
                output_path="",
                output_filename="",
                format=config.format,
                file_size_bytes=0,
                conversion_time_seconds=0,
                error=f"Validation failed: {', '.join(validation.errors)}"
            )

        # 3. Sanitize filename - use sample title if available
        if sample.title:
            base_name = sample.title
        else:
            base_name = input_path.stem

        if config.sanitize_filenames:
            sanitized_stem = self.sanitize_filename(base_name + input_path.suffix)
            sanitized_stem = Path(sanitized_stem).stem
        else:
            sanitized_stem = base_name

        # Append format extension
        output_filename = f"{sanitized_stem}.{config.format}"

        # 4. Determine output path
        output_base = Path(config.output_base_path or "/tmp/sp404_exports")
        output_path = self._organize_export_path(
            output_base,
            sample,
            config.organize_by
        )

        full_output_path = output_path / output_filename

        # 5. Convert
        conversion = await self.convert_to_sp404_format(
            input_path,
            full_output_path,
            config.format
        )

        if not conversion.success:
            return ExportResult(
                success=False,
                sample_id=sample_id,
                output_path=str(output_path),
                output_filename=output_filename,
                format=config.format,
                file_size_bytes=0,
                conversion_time_seconds=0,
                error=conversion.error_message
            )

        # 6. Get file size
        file_size = full_output_path.stat().st_size

        # Calculate duration
        duration_seconds = time.time() - start_time

        # 7. Optionally create metadata file
        metadata_created = False
        if config.include_metadata:
            metadata_path = output_path / f"{sanitized_stem}_metadata.txt"
            await self._write_metadata_file(
                metadata_path,
                sample,
                conversion
            )
            metadata_created = True

        # 8. Track export in database (only if requested)
        if track_export:
            await self._create_export_record(
                export_type="single",
                sample_count=1,
                output_path=str(output_path),
                organized_by=config.organize_by,
                format=config.format,
                total_size_bytes=file_size,
                export_duration_seconds=duration_seconds,
                results=[ExportResult(
                    success=True,
                    sample_id=sample_id,
                    output_path=str(output_path),
                    output_filename=output_filename,
                    format=config.format,
                    file_size_bytes=file_size,
                    conversion_time_seconds=duration_seconds
                )],
                db=db
            )

        return ExportResult(
            success=True,
            sample_id=sample_id,
            output_path=str(output_path),
            output_filename=output_filename,
            format=config.format,
            file_size_bytes=file_size,
            conversion_time_seconds=duration_seconds,
            metadata_file_created=metadata_created
        )

    async def export_batch(
        self,
        sample_ids: List[int],
        config: ExportConfig,
        db: Optional[AsyncSession] = None
    ) -> BatchExportResult:
        """
        Export multiple samples with organization.

        Processes all samples and aggregates results. Continues on error
        to export as many samples as possible.

        Args:
            sample_ids: List of sample IDs to export
            config: Export configuration
            db: Database session (uses self.db if not provided)

        Returns:
            BatchExportResult with aggregated statistics
        """
        if db is None:
            db = self.db

        start_time = time.time()

        results = []
        errors = []
        successful = 0
        failed = 0
        total_size = 0

        output_base = Path(config.output_base_path or "/tmp/sp404_exports")

        for sample_id in sample_ids:
            try:
                # Don't track individual exports - we'll track the batch
                result = await self.export_single_sample(sample_id, config, db, track_export=False)
                results.append(result)

                if result.success:
                    successful += 1
                    total_size += result.file_size_bytes
                else:
                    failed += 1
                    if result.error:
                        errors.append(f"Sample {sample_id}: {result.error}")

            except Exception as e:
                failed += 1
                error_msg = f"Sample {sample_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Failed to export sample {sample_id}: {e}")

        # Calculate total time
        total_time = time.time() - start_time

        # Calculate averages
        avg_time = total_time / len(sample_ids) if sample_ids else 0

        # Track batch export in database
        if successful > 0:  # Only track if we exported at least one sample
            await self._create_export_record(
                export_type="batch",
                sample_count=len(sample_ids),
                output_path=str(output_base),
                organized_by=config.organize_by,
                format=config.format,
                total_size_bytes=total_size,
                export_duration_seconds=total_time,
                results=results,
                db=db
            )

        return BatchExportResult(
            total_requested=len(sample_ids),
            successful=successful,
            failed=failed,
            total_size_bytes=total_size,
            total_time_seconds=total_time,
            average_time_per_sample=avg_time,
            total_samples=len(sample_ids),
            output_base_path=str(output_base),
            organized_by=config.organize_by,
            results=results,
            errors=errors
        )

    async def export_kit(
        self,
        kit_id: int,
        config: ExportConfig,
        db: Optional[AsyncSession] = None
    ) -> "KitExportResult":
        """
        Export entire kit with structure preservation.

        Maintains:
        - Kit organization
        - Bank structure (A, B, C, D)
        - Sample order (pad 1-16)

        Creates folder structure:
        output_path/
          kit_name/
            bank_A/
              pad_01_sample.wav
              pad_02_sample.wav
              ...

        Args:
            kit_id: Database ID of kit to export
            config: Export configuration
            db: Database session (uses self.db if not provided)

        Returns:
            KitExportResult with kit export details

        Raises:
            SP404ExportError: If kit not found
        """
        if db is None:
            db = self.db

        start_time = time.time()

        # Get kit
        stmt = select(Kit).where(Kit.id == kit_id)
        result = await db.execute(stmt)
        kit = result.scalar_one_or_none()

        if not kit:
            raise SP404ExportError(f"Kit {kit_id} not found")

        # Get kit samples
        stmt = select(Sample).join(KitSample).where(KitSample.kit_id == kit_id)
        result = await db.execute(stmt)
        samples = result.scalars().all()

        if not samples:
            raise SP404ExportError(f"Kit {kit_id} has no samples")

        # Create kit folder
        output_base = Path(config.output_base_path or "/tmp/sp404_exports")
        sanitized_kit_name = self.sanitize_filename(kit.name).replace('.', '')
        kit_folder = output_base / sanitized_kit_name
        kit_folder.mkdir(parents=True, exist_ok=True)

        # Export samples
        successful = 0
        failed = 0
        total_size = 0
        error_list = []

        for sample in samples:
            try:
                # Get kit sample info for pad/bank
                stmt = select(KitSample).where(
                    KitSample.kit_id == kit_id,
                    KitSample.sample_id == sample.id
                )
                result = await db.execute(stmt)
                kit_sample = result.scalar_one_or_none()

                if not kit_sample:
                    failed += 1
                    continue

                # Determine output based on organization
                if config.organize_by == "bank" or getattr(config, 'include_bank_layout', False):
                    # Bank organization
                    bank_folder = kit_folder / f"bank_{kit_sample.pad_bank}"
                    bank_folder.mkdir(exist_ok=True)
                    output_dir = bank_folder

                    # Create pad-numbered filename
                    input_path = Path(sample.file_path)
                    sanitized_name = self.sanitize_filename(input_path.stem)
                    output_filename = f"pad_{kit_sample.pad_number:02d}_{sanitized_name}.{config.format}"
                else:
                    # Kit organization (flat within kit folder)
                    output_dir = kit_folder
                    input_path = Path(sample.file_path)
                    sanitized_name = self.sanitize_filename(input_path.stem)
                    output_filename = f"{sanitized_name}.{config.format}"

                output_path = output_dir / output_filename

                # Validate
                validation = self.validate_sample(Path(sample.file_path))
                if not validation.valid:
                    failed += 1
                    error_list.append(f"Sample {sample.id} validation failed")
                    continue

                # Convert
                conversion = await self.convert_to_sp404_format(
                    Path(sample.file_path),
                    output_path,
                    config.format
                )

                if conversion.success:
                    successful += 1
                    total_size += output_path.stat().st_size
                else:
                    failed += 1
                    error_list.append(f"Sample {sample.id} conversion failed")

            except Exception as e:
                failed += 1
                error_list.append(f"Sample {sample.id}: {str(e)}")
                logger.error(f"Failed to export kit sample {sample.id}: {e}")

        # Calculate duration
        duration_seconds = time.time() - start_time

        # Import here to avoid circular dependency
        from app.schemas.sp404_export import KitExportResult

        return KitExportResult(
            success=successful > 0,
            kit_id=kit_id,
            kit_name=kit.name,
            sample_count=len(samples),
            successful=successful,
            failed=failed,
            output_path=str(kit_folder),
            format=config.format,
            total_size_bytes=total_size,
            export_time_seconds=duration_seconds,
            errors=error_list
        )

    def _get_bpm_folder_name(self, bpm: Optional[float]) -> str:
        """
        Map BPM value to folder name.

        Args:
            bpm: BPM value (can be None)

        Returns:
            Folder name for BPM range
        """
        if bpm is None:
            return "unknown_bpm"

        for min_bpm, max_bpm, folder_name in self.BPM_RANGES:
            if min_bpm <= bpm < max_bpm:
                return folder_name

        return "unknown_bpm"

    def _organize_export_path(
        self,
        base_path: Path,
        sample: Sample,
        organize_by: str
    ) -> Path:
        """
        Determine output path based on organization strategy.

        Strategies:
        - "flat": All samples in base_path
        - "genre": base_path/genre/
        - "bpm": base_path/bpm_range/
        - "kit": Not used for single samples (kit export has own logic)

        Args:
            base_path: Base export directory
            sample: Sample being exported
            organize_by: Organization strategy

        Returns:
            Path where sample should be exported
        """
        if organize_by == "flat":
            return base_path

        elif organize_by == "genre":
            genre = sample.genre or "unknown_genre"
            # Use genre as-is for folder name (don't over-sanitize)
            # Just ensure safe filesystem characters
            genre_folder = re.sub(r'[^a-zA-Z0-9_\-]', '_', genre)
            return base_path / genre_folder

        elif organize_by == "bpm":
            bpm_folder = self._get_bpm_folder_name(sample.bpm)
            return base_path / bpm_folder

        else:
            # Default to flat if unknown strategy
            logger.warning(f"Unknown organization strategy: {organize_by}, using flat")
            return base_path

    async def _write_metadata_file(
        self,
        metadata_path: Path,
        sample: Sample,
        conversion: ConversionResult
    ) -> None:
        """
        Write metadata text file alongside exported sample.

        Contains useful information for organizing and tracking samples.

        Args:
            metadata_path: Path where metadata file will be written
            sample: Sample being exported
            conversion: Conversion result with technical details
        """
        metadata_lines = [
            "# SP-404MK2 Sample Metadata",
            "",
            f"Title: {sample.title}",
            f"Genre: {sample.genre or 'Unknown'}",
            f"BPM: {sample.bpm or 'Unknown'}",
            f"Key: {sample.musical_key or 'Unknown'}",
            "",
            "## Technical Details",
            f"Original Format: {conversion.original_format}",
            f"Original Sample Rate: {conversion.original_sample_rate} Hz",
            f"Original Duration: {conversion.original_duration:.2f} seconds",
            f"Converted Sample Rate: {conversion.converted_sample_rate} Hz",
            f"Converted Bit Depth: {self.TARGET_BIT_DEPTH} bit",
            "",
            "## Database Info",
            f"Sample ID: {sample.id}",
            f"Created: {sample.created_at}",
        ]

        metadata_path.write_text('\n'.join(metadata_lines))
        logger.debug(f"Wrote metadata file: {metadata_path}")

    async def _create_export_record(
        self,
        export_type: str,
        sample_count: int,
        output_path: str,
        organized_by: str,
        format: str,
        total_size_bytes: int,
        export_duration_seconds: float,
        results: List[ExportResult],
        db: AsyncSession,
        user_id: Optional[int] = None
    ) -> SP404Export:
        """
        Create database record tracking this export.

        Args:
            export_type: "single", "batch", or "kit"
            sample_count: Number of samples exported
            output_path: Base path where files were exported
            organized_by: Organization strategy used
            format: Output format (wav/aiff)
            total_size_bytes: Total size of all exported files
            export_duration_seconds: Time taken for export
            results: List of individual export results
            db: Database session
            user_id: Optional user ID (for future auth)

        Returns:
            Created SP404Export record
        """
        export_record = SP404Export(
            user_id=user_id,
            export_type=export_type,
            sample_count=sample_count,
            output_path=output_path,
            organized_by=organized_by,
            format=format,
            total_size_bytes=total_size_bytes,
            export_duration_seconds=export_duration_seconds
        )

        db.add(export_record)
        await db.flush()  # Get ID without committing

        # Create records for each exported sample
        for result in results:
            if result.success:
                export_sample = SP404ExportSample(
                    export_id=export_record.id,
                    sample_id=result.sample_id,
                    output_filename=result.output_filename,
                    conversion_successful=True,
                    conversion_error=None,
                    file_size_bytes=result.file_size_bytes,
                    conversion_time_seconds=result.conversion_time_seconds
                )
            else:
                export_sample = SP404ExportSample(
                    export_id=export_record.id,
                    sample_id=result.sample_id,
                    output_filename=result.output_filename or "",
                    conversion_successful=False,
                    conversion_error=result.error,
                    file_size_bytes=0,
                    conversion_time_seconds=0
                )

            db.add(export_sample)

        await db.commit()
        await db.refresh(export_record)

        logger.info(
            f"Created export record {export_record.id}: "
            f"{sample_count} samples, {total_size_bytes} bytes"
        )

        return export_record
