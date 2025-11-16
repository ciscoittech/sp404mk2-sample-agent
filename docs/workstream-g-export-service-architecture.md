# SP-404MK2 Export Service - Architectural Design

**Workstream:** G - SP-404MK2 Export Service
**Status:** Design Complete
**Date:** 2025-11-14
**Version:** 1.0

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Service Design](#service-design)
4. [Data Model Design](#data-model-design)
5. [API Design](#api-design)
6. [Audio Processing Pipeline](#audio-processing-pipeline)
7. [Organization Logic](#organization-logic)
8. [Error Handling Strategy](#error-handling-strategy)
9. [Performance Considerations](#performance-considerations)
10. [Integration Points](#integration-points)
11. [Testing Strategy](#testing-strategy)
12. [Implementation Checklist](#implementation-checklist)

---

## Executive Summary

The SP-404MK2 Export Service provides a comprehensive solution for converting audio samples to hardware-compatible format with proper validation, organization, and tracking. The service addresses the critical pain point of preparing samples for the SP-404MK2 hardware sampler, which requires specific audio specifications and has unique constraints.

### Key Features

- **Format Conversion**: Automatic conversion to 48kHz/16-bit WAV or AIFF
- **Validation**: Ensures samples meet SP-404MK2 requirements (duration ≥100ms)
- **Filename Sanitization**: ASCII-safe filenames for hardware compatibility
- **Organization Options**: Flat, by-genre, by-BPM, or kit-based structure
- **Export Tracking**: Complete history with analytics and re-export capability
- **Background Processing**: Async handling for large batches
- **User Preferences**: Configurable defaults for export settings

### Hardware Requirements Addressed

| Requirement | Implementation |
|------------|----------------|
| 48kHz/16-bit format | `librosa.resample()` + `soundfile.write()` |
| WAV/AIFF support | Configurable output format |
| 100ms minimum duration | Pre-conversion validation |
| ASCII-safe filenames | Unicode normalization and sanitization |
| Organized structure | Multiple organization strategies |

---

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Public API      │      │  Protected API   │            │
│  │  Endpoints       │      │  (Future)        │            │
│  └────────┬─────────┘      └────────┬─────────┘            │
│           │                         │                       │
│           └────────┬────────────────┘                       │
│                    │                                        │
│         ┌──────────▼──────────┐                            │
│         │ SP404ExportService  │                            │
│         │                     │                            │
│         │ - convert_to_sp404  │                            │
│         │ - validate_sample   │                            │
│         │ - sanitize_filename │                            │
│         │ - export_single     │                            │
│         │ - export_batch      │                            │
│         │ - export_kit        │                            │
│         └──────────┬──────────┘                            │
│                    │                                        │
│         ┌──────────┼──────────┐                            │
│         │          │          │                            │
│    ┌────▼────┐ ┌──▼──┐  ┌───▼────┐                        │
│    │ librosa │ │ sf  │  │ pathlib│                        │
│    │         │ │     │  │        │                        │
│    └─────────┘ └─────┘  └────────┘                        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                     Database Layer                           │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ SP404Export │  │ SP404Export  │  │ UserPreference  │   │
│  │             │◄─┤ Sample       │  │                 │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│         │                  │                                │
│         └──────────────────┴──────────────┐                │
│                                            │                │
│                                     ┌──────▼──────┐         │
│                                     │   Sample    │         │
│                                     │   Kit       │         │
│                                     └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Service Responsibilities

**SP404ExportService**: Core business logic for export operations
- Audio format conversion using librosa/soundfile
- Sample validation against SP-404MK2 requirements
- Filename sanitization for hardware compatibility
- Organization strategy implementation
- Export tracking and history management

**PreferencesService**: User preference management (integration point)
- Default export format preferences
- Default organization strategy
- Export base path configuration

**SampleService**: Sample metadata and file management (integration point)
- Sample retrieval for export
- File path resolution
- Metadata access

---

## Service Design

### File: `backend/app/services/sp404_export_service.py`

```python
"""
SP404ExportService for converting and exporting samples to SP-404MK2 format.

Provides comprehensive export functionality including format conversion,
validation, filename sanitization, and organization strategies.
"""
import asyncio
import logging
import re
import unicodedata
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime, timezone
import zipfile
import shutil

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
    BatchExportResult
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
    SUPPORTED_INPUT_FORMATS = {'.wav', '.aiff', '.aif', '.mp3', '.flac', '.m4a', '.ogg'}
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

    def __init__(self, db_session: AsyncSession):
        """
        Initialize SP404ExportService.

        Args:
            db_session: SQLAlchemy async database session

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
            SP404ExportError: If conversion fails or format unsupported
        """
        # Validate format
        if format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise SP404ExportError(
                f"Unsupported output format: {format}. "
                f"Supported: {', '.join(self.SUPPORTED_OUTPUT_FORMATS)}"
            )

        # Validate input exists
        if not input_path.exists():
            raise SP404ExportError(f"Input file not found: {input_path}")

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

        # Handle stereo/mono
        if y.ndim > 1:
            # Keep stereo if original is stereo
            pass
        else:
            # Mono stays mono
            y = y.reshape(1, -1) if y.ndim == 1 else y

        # Calculate original duration
        original_duration = librosa.get_duration(y=y, sr=sr)

        # Resample if needed
        if sr != self.TARGET_SAMPLE_RATE:
            if y.ndim > 1:
                # Resample each channel
                y_resampled = np.array([
                    librosa.resample(
                        y[ch],
                        orig_sr=sr,
                        target_sr=self.TARGET_SAMPLE_RATE
                    )
                    for ch in range(y.shape[0])
                ])
            else:
                y_resampled = librosa.resample(
                    y[0] if y.ndim > 1 else y,
                    orig_sr=sr,
                    target_sr=self.TARGET_SAMPLE_RATE
                )
                y_resampled = y_resampled.reshape(1, -1)

            y = y_resampled
            sr = self.TARGET_SAMPLE_RATE

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write with soundfile (automatically handles 16-bit conversion)
        # Transpose for soundfile (expects time x channels)
        y_transposed = y.T if y.ndim > 1 else y

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
            converted_bit_depth=self.TARGET_BIT_DEPTH
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
                # Quick duration check without full load
                y, sr = librosa.load(str(file_path), sr=None, duration=1.0)
                duration_ms = len(y) / sr * 1000
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

    def sanitize_filename(self, filename: str) -> str:
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
        4. Limit length to MAX_FILENAME_LENGTH
        5. Ensure filename doesn't start with dot or dash

        Args:
            filename: Original filename (with or without extension)

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

        # 2. Replace spaces and underscores
        name = name.replace(' ', '_')

        # 3. Remove special characters (keep alphanumeric, underscore, hyphen)
        name = re.sub(r'[^a-zA-Z0-9_\-]', '', name)

        # 4. Remove consecutive underscores/hyphens
        name = re.sub(r'[_\-]+', '_', name)

        # 5. Ensure doesn't start with dot or dash
        name = name.lstrip('.-_')

        # 6. Ensure we have something left
        if not name:
            name = "sample"

        # 7. Limit length (accounting for extension)
        max_name_length = self.MAX_FILENAME_LENGTH - len(ext)
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
        db: AsyncSession
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
            db: Database session

        Returns:
            ExportResult with export details

        Raises:
            SP404ExportError: If sample not found or export fails
        """
        start_time = datetime.now(timezone.utc)

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

        # 3. Sanitize filename
        original_filename = input_path.name
        if config.sanitize_filenames:
            sanitized_name = self.sanitize_filename(original_filename)
            sanitized_stem = Path(sanitized_name).stem
        else:
            sanitized_stem = input_path.stem

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
        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()

        # 7. Optionally create metadata file
        if config.include_metadata:
            await self._write_metadata_file(
                full_output_path.parent / f"{sanitized_stem}_metadata.txt",
                sample,
                conversion
            )

        return ExportResult(
            success=True,
            sample_id=sample_id,
            output_path=str(output_path),
            output_filename=output_filename,
            format=config.format,
            file_size_bytes=file_size,
            conversion_time_seconds=duration_seconds
        )

    async def export_batch(
        self,
        sample_ids: List[int],
        config: ExportConfig,
        db: AsyncSession
    ) -> BatchExportResult:
        """
        Export multiple samples with organization.

        Processes all samples and aggregates results. Continues on error
        to export as many samples as possible.

        Args:
            sample_ids: List of sample IDs to export
            config: Export configuration
            db: Database session

        Returns:
            BatchExportResult with aggregated statistics
        """
        start_time = datetime.now(timezone.utc)

        results = []
        errors = []
        successful = 0
        failed = 0
        total_size = 0

        output_base = Path(config.output_base_path or "/tmp/sp404_exports")

        for sample_id in sample_ids:
            try:
                result = await self.export_single_sample(sample_id, config, db)
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
        end_time = datetime.now(timezone.utc)
        total_time = (end_time - start_time).total_seconds()

        # Create export tracking record
        export_record = await self._create_export_record(
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
            output_base_path=str(output_base),
            organized_by=config.organize_by,
            results=results,
            errors=errors
        )

    async def export_kit(
        self,
        kit_id: int,
        config: ExportConfig,
        db: AsyncSession
    ) -> ExportResult:
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
            bank_B/
              ...

        Args:
            kit_id: Database ID of kit to export
            config: Export configuration
            db: Database session

        Returns:
            ExportResult with kit export details

        Raises:
            SP404ExportError: If kit not found
        """
        start_time = datetime.now(timezone.utc)

        # Get kit with samples
        stmt = select(Kit).where(Kit.id == kit_id)
        result = await db.execute(stmt)
        kit = result.scalar_one_or_none()

        if not kit:
            raise SP404ExportError(f"Kit {kit_id} not found")

        # Get kit samples
        stmt = select(KitSample).where(KitSample.kit_id == kit_id)
        result = await db.execute(stmt)
        kit_samples = result.scalars().all()

        if not kit_samples:
            raise SP404ExportError(f"Kit {kit_id} has no samples")

        # Create kit folder
        output_base = Path(config.output_base_path or "/tmp/sp404_exports")
        sanitized_kit_name = self.sanitize_filename(kit.name)
        kit_folder = output_base / sanitized_kit_name
        kit_folder.mkdir(parents=True, exist_ok=True)

        # Export each sample to appropriate bank folder
        successful = 0
        failed = 0
        total_size = 0

        for kit_sample in kit_samples:
            try:
                # Get sample details
                stmt = select(Sample).where(Sample.id == kit_sample.sample_id)
                result = await db.execute(stmt)
                sample = result.scalar_one_or_none()

                if not sample:
                    failed += 1
                    continue

                # Create bank folder
                bank_folder = kit_folder / f"bank_{kit_sample.pad_bank}"
                bank_folder.mkdir(exist_ok=True)

                # Create pad-numbered filename
                input_path = Path(sample.file_path)
                sanitized_name = self.sanitize_filename(input_path.stem)
                output_filename = f"pad_{kit_sample.pad_number:02d}_{sanitized_name}.{config.format}"
                output_path = bank_folder / output_filename

                # Convert
                conversion = await self.convert_to_sp404_format(
                    input_path,
                    output_path,
                    config.format
                )

                if conversion.success:
                    successful += 1
                    total_size += output_path.stat().st_size
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                logger.error(f"Failed to export kit sample {kit_sample.sample_id}: {e}")

        # Calculate duration
        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()

        return ExportResult(
            success=successful > 0,
            sample_id=kit_id,  # Using kit_id here
            output_path=str(kit_folder),
            output_filename=sanitized_kit_name,
            format=config.format,
            file_size_bytes=total_size,
            conversion_time_seconds=duration_seconds,
            error=f"{failed} samples failed" if failed > 0 else None
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
            # Sanitize genre for folder name
            genre = self.sanitize_filename(genre)
            return base_path / genre

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
            f"Tags: {', '.join(sample.tags) if sample.tags else 'None'}",
            "",
            "## Technical Details",
            f"Original Format: {conversion.original_format}",
            f"Original Sample Rate: {conversion.original_sample_rate} Hz",
            f"Original Duration: {conversion.original_duration:.2f} seconds",
            f"Converted Sample Rate: {conversion.converted_sample_rate} Hz",
            f"Converted Bit Depth: {conversion.converted_bit_depth} bit",
            "",
            "## Database Info",
            f"Sample ID: {sample.id}",
            f"Created: {sample.created_at}",
            f"Analyzed: {sample.analyzed_at or 'Not analyzed'}",
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
                    output_subfolder=result.output_path,
                    conversion_successful=True,
                    error_message=None
                )
            else:
                export_sample = SP404ExportSample(
                    export_id=export_record.id,
                    sample_id=result.sample_id,
                    output_filename=result.output_filename,
                    output_subfolder=result.output_path,
                    conversion_successful=False,
                    error_message=result.error
                )

            db.add(export_sample)

        await db.commit()
        await db.refresh(export_record)

        logger.info(
            f"Created export record {export_record.id}: "
            f"{sample_count} samples, {total_size_bytes} bytes"
        )

        return export_record

    async def create_export_zip(
        self,
        export_id: int,
        db: AsyncSession
    ) -> Path:
        """
        Create ZIP archive of exported samples for download.

        Args:
            export_id: Database ID of export
            db: Database session

        Returns:
            Path to created ZIP file

        Raises:
            SP404ExportError: If export not found or ZIP creation fails
        """
        # Get export record
        stmt = select(SP404Export).where(SP404Export.id == export_id)
        result = await db.execute(stmt)
        export_record = result.scalar_one_or_none()

        if not export_record:
            raise SP404ExportError(f"Export {export_id} not found")

        # Create ZIP file
        output_path = Path(export_record.output_path)
        zip_path = output_path.parent / f"export_{export_id}.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from export directory
                for file_path in output_path.rglob('*'):
                    if file_path.is_file():
                        # Add with relative path
                        arcname = file_path.relative_to(output_path)
                        zipf.write(file_path, arcname)

            logger.info(f"Created ZIP archive: {zip_path}")
            return zip_path

        except Exception as e:
            raise SP404ExportError(f"Failed to create ZIP: {e}")
```

---

## Data Model Design

### File: `backend/app/models/sp404_export.py`

```python
"""
Models for SP-404MK2 export tracking.

Tracks export history for analytics, re-export capability, and audit trail.
"""
from sqlalchemy import Column, Integer, String, BigInteger, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SP404Export(Base):
    """
    Track export operations for analytics and history.

    Stores metadata about each export operation, including:
    - What was exported (type, sample count)
    - Where it was exported (path, organization)
    - How it was exported (format, settings)
    - Performance metrics (size, duration)
    """
    __tablename__ = "sp404_exports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Export details
    export_type = Column(String, nullable=False, index=True)  # "single", "batch", "kit"
    sample_count = Column(Integer, nullable=False)
    output_path = Column(String, nullable=False)
    organized_by = Column(String, nullable=False)  # "flat", "genre", "bpm", "kit"
    format = Column(String, nullable=False)  # "wav", "aiff"

    # Metrics
    total_size_bytes = Column(BigInteger, nullable=False, default=0)
    export_duration_seconds = Column(Float, nullable=False, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    exported_samples = relationship(
        "SP404ExportSample",
        back_populates="export",
        cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="sp404_exports")

    # Indexes for common queries
    __table_args__ = (
        Index('ix_sp404_exports_user_created', 'user_id', 'created_at'),
        Index('ix_sp404_exports_type_created', 'export_type', 'created_at'),
    )


class SP404ExportSample(Base):
    """
    Track individual samples within an export operation.

    Provides detailed tracking of each sample in an export:
    - Export success/failure status
    - Output location and filename
    - Error messages for debugging
    """
    __tablename__ = "sp404_export_samples"

    id = Column(Integer, primary_key=True)
    export_id = Column(Integer, ForeignKey("sp404_exports.id"), nullable=False, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False, index=True)

    # Export details for this sample
    output_filename = Column(String, nullable=False)
    output_subfolder = Column(String, nullable=True)  # Relative to export output_path
    conversion_successful = Column(Boolean, nullable=False, default=True)
    error_message = Column(String, nullable=True)

    # Relationships
    export = relationship("SP404Export", back_populates="exported_samples")
    sample = relationship("Sample", back_populates="sp404_export_samples")

    # Composite index for looking up exports by sample
    __table_args__ = (
        Index('ix_sp404_export_samples_sample_export', 'sample_id', 'export_id'),
    )
```

### Updates to Existing Models

**File: `backend/app/models/user.py`**

Add relationship to User model:

```python
# Add to User model relationships
sp404_exports = relationship("SP404Export", back_populates="user", cascade="all, delete-orphan")
```

**File: `backend/app/models/sample.py`**

Add relationship to Sample model:

```python
# Add to Sample model relationships
sp404_export_samples = relationship(
    "SP404ExportSample",
    back_populates="sample",
    cascade="all, delete-orphan"
)
```

**File: `backend/app/models/user_preferences.py`**

Add SP-404 export preferences:

```python
# Add to UserPreference model (after existing preferences)

# SP-404MK2 export preferences
sp404_export_format = Column(String, nullable=False, default="wav")  # "wav" or "aiff"
sp404_default_organization = Column(String, nullable=False, default="flat")  # "flat", "genre", "bpm"
sp404_sanitize_filenames = Column(Boolean, nullable=False, default=True)
sp404_include_metadata = Column(Boolean, nullable=False, default=True)
sp404_export_base_path = Column(String, nullable=True)  # Custom export location
```

---

## Pydantic Schemas Design

### File: `backend/app/schemas/sp404_export.py`

```python
"""
Pydantic schemas for SP-404MK2 export operations.

Defines request/response models for export API endpoints.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from pathlib import Path
from datetime import datetime


class ExportConfig(BaseModel):
    """
    Configuration for SP-404MK2 export operation.

    Controls all aspects of the export process including format,
    organization, and optional features.
    """
    organize_by: str = Field(
        default="flat",
        description="Organization strategy: 'flat', 'genre', 'bpm', 'kit'"
    )
    format: str = Field(
        default="wav",
        description="Output format: 'wav' or 'aiff'"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include .txt metadata files alongside samples"
    )
    sanitize_filenames: bool = Field(
        default=True,
        description="Sanitize filenames to ASCII-safe characters"
    )
    output_base_path: Optional[str] = Field(
        default=None,
        description="Custom export location (defaults to temp directory)"
    )

    @validator('organize_by')
    def validate_organize_by(cls, v):
        """Validate organization strategy."""
        allowed = ['flat', 'genre', 'bpm', 'kit']
        if v not in allowed:
            raise ValueError(f"organize_by must be one of: {', '.join(allowed)}")
        return v

    @validator('format')
    def validate_format(cls, v):
        """Validate output format."""
        allowed = ['wav', 'aiff']
        if v not in allowed:
            raise ValueError(f"format must be one of: {', '.join(allowed)}")
        return v.lower()


class ConversionResult(BaseModel):
    """
    Result of audio format conversion operation.

    Contains technical details about the conversion process and outcome.
    """
    success: bool = Field(..., description="Whether conversion succeeded")
    output_path: Optional[Path] = Field(None, description="Path to converted file")

    # Original file properties
    original_format: str = Field(..., description="Original file extension")
    original_sample_rate: int = Field(..., description="Original sample rate in Hz")
    original_duration: float = Field(..., description="Original duration in seconds")

    # Converted file properties
    converted_sample_rate: int = Field(default=48000, description="Converted sample rate (48kHz)")
    converted_bit_depth: int = Field(default=16, description="Converted bit depth (16-bit)")

    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if conversion failed")

    class Config:
        # Allow Path objects
        arbitrary_types_allowed = True


class ValidationResult(BaseModel):
    """
    Result of sample validation against SP-404MK2 requirements.

    Checks all hardware requirements before export.
    """
    valid: bool = Field(..., description="Whether sample meets all requirements")

    # Specific validation checks
    duration_ms: float = Field(..., description="Sample duration in milliseconds")
    meets_duration_requirement: bool = Field(..., description="Duration >= 100ms")
    format_supported: bool = Field(..., description="File format is supported")
    file_readable: bool = Field(..., description="File exists and is readable")

    # Detailed error messages
    errors: List[str] = Field(default_factory=list, description="List of validation errors")


class ExportResult(BaseModel):
    """
    Result of exporting a single sample.

    Contains details about the export operation for one sample.
    """
    success: bool = Field(..., description="Whether export succeeded")
    sample_id: int = Field(..., description="Database ID of exported sample")

    # Output details
    output_path: str = Field(..., description="Directory where file was exported")
    output_filename: str = Field(..., description="Name of exported file")
    format: str = Field(..., description="Output format (wav/aiff)")

    # Metrics
    file_size_bytes: int = Field(..., description="Size of exported file in bytes")
    conversion_time_seconds: float = Field(..., description="Time taken to export")

    # Error handling
    error: Optional[str] = Field(None, description="Error message if export failed")


class BatchExportResult(BaseModel):
    """
    Result of exporting multiple samples in batch.

    Aggregates results from all samples in the batch operation.
    """
    # Summary statistics
    total_requested: int = Field(..., description="Number of samples requested for export")
    successful: int = Field(..., description="Number of successfully exported samples")
    failed: int = Field(..., description="Number of failed exports")

    # Metrics
    total_size_bytes: int = Field(..., description="Total size of all exported files")
    total_time_seconds: float = Field(..., description="Total time for batch operation")

    # Output details
    output_base_path: str = Field(..., description="Base directory for exports")
    organized_by: str = Field(..., description="Organization strategy used")

    # Detailed results
    results: List[ExportResult] = Field(..., description="Individual export results")
    errors: List[str] = Field(default_factory=list, description="List of error messages")


class SP404ExportResponse(BaseModel):
    """
    Database export record response.

    Used for retrieving export history and analytics.
    """
    id: int
    user_id: Optional[int]

    # Export details
    export_type: str
    sample_count: int
    output_path: str
    organized_by: str
    format: str

    # Metrics
    total_size_bytes: int
    export_duration_seconds: float

    # Timestamp
    created_at: datetime

    class Config:
        from_attributes = True


class SP404ExportSampleResponse(BaseModel):
    """
    Individual sample within export record.
    """
    id: int
    export_id: int
    sample_id: int

    output_filename: str
    output_subfolder: Optional[str]
    conversion_successful: bool
    error_message: Optional[str]

    class Config:
        from_attributes = True


class ExportHistoryResponse(BaseModel):
    """
    Paginated export history response.
    """
    items: List[SP404ExportResponse]
    total: int
    page: int
    pages: int
    limit: int
```

---

## API Design

### File: `backend/app/api/v1/endpoints/sp404_export.py` (new file)

```python
"""
API endpoints for SP-404MK2 export operations.

Provides RESTful interface for exporting samples to hardware-compatible format.
"""
import logging
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.sp404_export_service import SP404ExportService, SP404ExportError
from app.schemas.sp404_export import (
    ExportConfig,
    ExportResult,
    BatchExportResult,
    SP404ExportResponse,
    ExportHistoryResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/samples/{sample_id}/export", response_model=ExportResult)
async def export_single_sample(
    sample_id: int,
    config: ExportConfig,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Export single sample to SP-404MK2 compatible format.

    Converts audio file to 48kHz/16-bit WAV or AIFF format with proper
    validation and filename sanitization.

    For small files, processes synchronously and returns result immediately.
    For large files (>10MB), processes in background and returns job ID.

    Args:
        sample_id: Database ID of sample to export
        config: Export configuration (format, organization, etc.)
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        ExportResult with export details and download location

    Raises:
        404: Sample not found
        422: Validation failed or unsupported format
        500: Export operation failed
    """
    try:
        service = SP404ExportService(db)

        # For MVP, process synchronously
        # TODO: Add background processing for large files
        result = await service.export_single_sample(sample_id, config, db)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error
            )

        return result

    except SP404ExportError as e:
        logger.error(f"Export error for sample {sample_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error exporting sample {sample_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export operation failed"
        )


@router.post("/samples/export-batch", response_model=BatchExportResult)
async def export_batch_samples(
    sample_ids: List[int],
    config: ExportConfig,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Export multiple samples in batch with organization.

    Processes all samples and organizes according to strategy:
    - flat: All samples in one folder
    - genre: Samples organized by genre
    - bpm: Samples organized by BPM range

    Always processes in background for batches > 5 samples.

    Args:
        sample_ids: List of sample IDs to export
        config: Export configuration
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        BatchExportResult with aggregated statistics

    Raises:
        422: Invalid sample IDs or configuration
        500: Batch export failed
    """
    if not sample_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No samples provided for export"
        )

    if len(sample_ids) > 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Maximum 1000 samples per batch"
        )

    try:
        service = SP404ExportService(db)

        # For MVP, process synchronously
        # TODO: Add background processing for large batches
        result = await service.export_batch(sample_ids, config, db)

        return result

    except SP404ExportError as e:
        logger.error(f"Batch export error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in batch export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch export operation failed"
        )


@router.post("/kits/{kit_id}/export", response_model=ExportResult)
async def export_kit(
    kit_id: int,
    config: ExportConfig,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Export entire kit with bank/pad structure.

    Creates organized folder structure:
    - kit_name/bank_A/pad_01_sample.wav
    - kit_name/bank_B/pad_01_sample.wav
    - etc.

    Maintains SP-404MK2 pad layout for easy hardware loading.

    Args:
        kit_id: Database ID of kit to export
        config: Export configuration
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        ExportResult with kit export details

    Raises:
        404: Kit not found
        422: Kit has no samples or export failed
        500: Export operation failed
    """
    try:
        service = SP404ExportService(db)

        result = await service.export_kit(kit_id, config, db)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error
            )

        return result

    except SP404ExportError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error exporting kit {kit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kit export operation failed"
        )


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Download completed export as ZIP file.

    Creates ZIP archive of all exported samples and metadata files
    for easy download and transfer to SP-404MK2.

    Args:
        export_id: Database ID of export
        db: Database session

    Returns:
        FileResponse with ZIP file

    Raises:
        404: Export not found
        500: ZIP creation failed
    """
    try:
        service = SP404ExportService(db)

        # Create ZIP file
        zip_path = await service.create_export_zip(export_id, db)

        return FileResponse(
            path=str(zip_path),
            media_type='application/zip',
            filename=f'sp404_export_{export_id}.zip',
            headers={
                "Content-Disposition": f"attachment; filename=sp404_export_{export_id}.zip"
            }
        )

    except SP404ExportError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating download for export {export_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create download"
        )


@router.get("/exports", response_model=ExportHistoryResponse)
async def list_exports(
    page: int = 1,
    limit: int = 20,
    export_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List export history with pagination.

    Provides access to past exports for re-download and analytics.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        export_type: Filter by type ("single", "batch", "kit")
        db: Database session

    Returns:
        ExportHistoryResponse with paginated export list
    """
    # TODO: Implement export history listing
    # This is a placeholder for future implementation
    return ExportHistoryResponse(
        items=[],
        total=0,
        page=page,
        pages=0,
        limit=limit
    )
```

### Update Main Router

**File: `backend/app/api/v1/api.py`**

```python
# Add import
from app.api.v1.endpoints import sp404_export

# Add router
api_router.include_router(
    sp404_export.router,
    prefix="/sp404",
    tags=["sp404-export"]
)
```

---

## Audio Processing Pipeline

### Conversion Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Audio Conversion Pipeline                  │
└─────────────────────────────────────────────────────────────┘

1. Validation Phase
   ├── Check file exists
   ├── Validate format (WAV, AIFF, MP3, FLAC, M4A)
   ├── Load audio metadata
   └── Verify duration >= 100ms
       ↓
2. Load Phase (librosa)
   ├── Load audio: y, sr = librosa.load(path, sr=None, mono=False)
   ├── Detect channels (mono/stereo)
   ├── Store original properties (sr, duration, format)
       ↓
3. Conversion Phase
   ├── Check sample rate
   │   ├── If sr != 48000Hz
   │   │   ├── Stereo: Resample each channel separately
   │   │   └── Mono: Resample single channel
   │   └── Use librosa.resample(y, orig_sr=sr, target_sr=48000)
   │
   ├── Prepare for output
   │   ├── Ensure proper shape for soundfile (time x channels)
   │   └── Transpose if needed: y.T
       ↓
4. Write Phase (soundfile)
   ├── Create output directory if needed
   ├── Write with soundfile.write():
   │   ├── Sample rate: 48000 Hz
   │   ├── Bit depth: PCM_16 (16-bit)
   │   └── Format: WAV or AIFF
   └── Return ConversionResult
       ↓
5. Post-Processing
   ├── Get file size
   ├── Optionally create metadata .txt file
   └── Track in database (SP404Export tables)
```

### Library Usage Details

**librosa** - Audio loading and resampling
```python
# Load audio preserving original sample rate
y, sr = librosa.load(str(input_path), sr=None, mono=False)

# Resample to 48kHz
y_resampled = librosa.resample(
    y,
    orig_sr=sr,
    target_sr=48000
)

# Get duration
duration = librosa.get_duration(y=y, sr=sr)
```

**soundfile** - Audio writing
```python
# Write with specific format and bit depth
sf.write(
    str(output_path),
    y_transposed,  # time x channels
    48000,  # sample rate
    subtype='PCM_16',  # 16-bit PCM
    format='WAV'  # or 'AIFF'
)
```

### Quality Preservation Strategy

1. **Sample Rate Conversion**: Uses librosa's high-quality resampling
   - Default resampling algorithm: sinc interpolation
   - Preserves frequency content up to Nyquist frequency
   - Minimal aliasing and artifacts

2. **Bit Depth Conversion**: soundfile handles conversion
   - Automatic scaling to 16-bit range
   - Proper dithering applied
   - No clipping (unless input already clipped)

3. **Channel Handling**:
   - Preserves stereo if original is stereo
   - Keeps mono if original is mono
   - No unnecessary channel conversion

4. **Format Support**:
   - Input: WAV, AIFF, MP3, FLAC, M4A (ALAC, AAC), OGG
   - Output: WAV (PCM_16), AIFF (PCM_16)
   - Lossless conversion from lossless sources
   - High-quality decode from lossy sources (MP3, M4A/AAC)

---

## Organization Logic

### Organization Strategies

**1. Flat Organization**
```
output_path/
  sample_001.wav
  sample_002.wav
  sample_003.wav
  ...
```

**2. Genre Organization**
```
output_path/
  hiphop/
    sample_001.wav
    sample_002.wav
  jazz/
    sample_003.wav
  electronic/
    sample_004.wav
  unknown_genre/
    sample_005.wav
```

**3. BPM Organization**
```
output_path/
  slow/           # 0-70 BPM
    sample_001.wav
  70-90/
    sample_002.wav
  90-110/
    sample_003.wav
  110-130/
    sample_004.wav
  130-150/
    sample_005.wav
  fast/           # 150+ BPM
    sample_006.wav
  unknown_bpm/
    sample_007.wav
```

**4. Kit Organization**
```
output_path/
  my_kit_name/
    bank_A/
      pad_01_kick.wav
      pad_02_snare.wav
      ...
      pad_16_cymbal.wav
    bank_B/
      pad_01_bass.wav
      ...
    bank_C/
      ...
    bank_D/
      ...
```

### Folder Structure Logic

**Genre Folders**:
- Use genre from sample.genre field
- Sanitize genre name (ASCII-safe)
- Default to "unknown_genre" if not set

**BPM Folders**:
- Map BPM to predefined ranges
- Ranges: 0-70 (slow), 70-90, 90-110, 110-130, 130-150, 150+ (fast)
- Default to "unknown_bpm" if not set

**Kit Folders**:
- Top level: Kit name (sanitized)
- Second level: Bank folders (bank_A, bank_B, bank_C, bank_D)
- Files: Numbered by pad position (pad_01 to pad_16)

### Naming Conventions

**File Naming**:
- Base name from original sample title or filename
- Sanitized to ASCII-safe characters
- Format: `{sanitized_name}.{format}`
- Kit mode: `pad_{number:02d}_{sanitized_name}.{format}`

**Folder Naming**:
- All folder names sanitized to ASCII
- Lowercase for consistency
- Underscores instead of spaces
- Special characters removed

### Metadata File Format

Optional `.txt` file alongside each sample:

```
# SP-404MK2 Sample Metadata

Title: Vintage Drum Loop
Genre: Hip-Hop
BPM: 95
Key: A minor
Tags: drums, vintage, vinyl

## Technical Details
Original Format: .mp3
Original Sample Rate: 44100 Hz
Original Duration: 4.52 seconds
Converted Sample Rate: 48000 Hz
Converted Bit Depth: 16 bit

## Database Info
Sample ID: 123
Created: 2025-11-14 10:30:00
Analyzed: 2025-11-14 10:31:00
```

---

## Error Handling Strategy

### Error Categories

**1. Validation Errors** (422 Unprocessable Entity)
- Sample not found
- File not found
- Duration too short (<100ms)
- Unsupported format
- Invalid configuration

**2. Conversion Errors** (422 Unprocessable Entity)
- Audio loading failed
- Resampling failed
- File write failed
- Corrupted audio file

**3. File System Errors** (500 Internal Server Error)
- Permission denied
- Disk full
- Path too long
- Invalid characters in path

**4. Resource Errors** (500 Internal Server Error)
- Out of memory
- CPU timeout
- Database connection failed

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "error_type": "validation_error",
  "sample_id": 123,
  "context": {
    "file_path": "/path/to/file.wav",
    "validation_errors": ["Duration too short: 50ms (minimum: 100ms)"]
  }
}
```

### Error Recovery Strategies

**Validation Failures**:
- Return detailed ValidationResult
- Continue batch processing (don't fail entire batch)
- Log specific issues for debugging

**Conversion Failures**:
- Retry once with different parameters
- Fall back to mono if stereo fails
- Skip problematic samples in batch

**File System Failures**:
- Create missing directories automatically
- Sanitize paths more aggressively
- Provide clear error messages

**Batch Processing**:
- Continue on error (don't fail entire batch)
- Collect all errors for reporting
- Return partial success with error list

### Logging Strategy

**Info Level**:
- Export started (type, sample count)
- Conversion completed (file, duration)
- Export completed (total size, duration)

**Warning Level**:
- Validation warnings (non-fatal)
- Fallback to defaults
- Skipped samples

**Error Level**:
- Conversion failures
- File system errors
- Database errors

**Example Log Output**:
```
INFO: Starting batch export: 10 samples, genre organization, WAV format
INFO: Converted sample_001.mp3: 44100Hz → 48000Hz (3.2s)
WARN: Sample 5 duration below minimum: 85ms, skipping
ERROR: Failed to export sample 7: Permission denied writing to /exports/
INFO: Export completed: 8/10 successful, 2 failed, 32.5 MB, 12.3s
```

---

## Performance Considerations

### Background Processing Strategy

**When to Use Background Tasks**:
- Batch exports > 5 samples
- Individual samples > 10MB
- Kit exports with > 20 samples

**Implementation** (Future Enhancement):
```python
# Using FastAPI BackgroundTasks for simple cases
background_tasks.add_task(
    service.export_batch,
    sample_ids,
    config,
    db
)

# Using Celery for production (future)
from app.tasks import export_batch_task
task = export_batch_task.delay(sample_ids, config)
return {"task_id": task.id}
```

### Progress Tracking

**For MVP** (Synchronous):
- Return immediate results
- No progress tracking needed

**For Future** (Async):
```python
# Redis-based progress tracking
{
  "task_id": "export_123",
  "status": "in_progress",
  "total": 100,
  "completed": 45,
  "failed": 2,
  "current_sample": "sample_046.wav"
}
```

### Resource Management

**Memory Management**:
- Process files one at a time (no batch loading)
- Use asyncio.to_thread() for CPU work
- Release memory after each conversion
- Limit concurrent conversions

**CPU Management**:
- Run conversions in thread pool
- Limit thread pool size (e.g., 4 workers)
- Use process pool for very large files
- Implement timeout (e.g., 60s per file)

**Disk Management**:
- Check available space before export
- Clean up temp files on error
- Use streaming for ZIP creation
- Implement quota limits (future)

**Database Management**:
- Use connection pooling
- Commit after each sample (batch mode)
- Batch insert export records
- Use indexes for queries

### Performance Benchmarks

**Target Performance** (local hardware):
- Small sample (<5MB): <2 seconds
- Medium sample (5-20MB): 2-10 seconds
- Large sample (>20MB): 10-30 seconds
- Batch (100 samples): <5 minutes

**Optimization Opportunities**:
- Cache resampling filters
- Parallel processing for batches
- Skip conversion if already 48kHz/16-bit
- Use faster resampling for non-critical work

---

## Integration Points

### Existing Services

**PreferencesService** (`app/services/preferences_service.py`):
```python
# Get export preferences
prefs = await preferences_service.get_preferences()
default_format = prefs.sp404_export_format
default_org = prefs.sp404_default_organization
```

**SampleService** (`app/services/sample_service.py`):
```python
# Retrieve sample for export
sample = await sample_service.get_sample_by_id(sample_id)
file_path = Path(sample.file_path)
```

**AudioFeaturesService** (`app/services/audio_features_service.py`):
```python
# Get audio features for validation
features = await audio_features_service.analyze_file(file_path)
if features.duration_seconds < 0.1:  # 100ms
    raise ValidationError("Duration too short")
```

### Database Integration

**Sample Relationships**:
```python
# Track which samples have been exported
sample.sp404_export_samples  # List of SP404ExportSample

# Find all exports containing a sample
exports = await db.execute(
    select(SP404Export)
    .join(SP404ExportSample)
    .where(SP404ExportSample.sample_id == sample_id)
)
```

**Kit Integration**:
```python
# Export kit with all samples
kit = await db.execute(select(Kit).where(Kit.id == kit_id))
kit_samples = await db.execute(
    select(KitSample).where(KitSample.kit_id == kit_id)
)
```

### Frontend Integration

**Upload → Export Workflow**:
```javascript
// After sample upload
POST /api/v1/public/samples (upload file)
→ Sample created with ID 123

// Export sample
POST /api/v1/sp404/samples/123/export
{
  "organize_by": "flat",
  "format": "wav",
  "include_metadata": true
}
→ ExportResult returned

// Download export
GET /api/v1/sp404/exports/456/download
→ ZIP file downloaded
```

**Batch Export UI Flow**:
```javascript
// User selects multiple samples in grid
selectedSamples = [123, 124, 125, ...]

// Batch export
POST /api/v1/sp404/samples/export-batch
{
  "sample_ids": [123, 124, 125, ...],
  "config": {
    "organize_by": "genre",
    "format": "wav"
  }
}
→ BatchExportResult with download link
```

---

## Testing Strategy

### Unit Tests

**Service Tests** (`backend/tests/services/test_sp404_export_service.py`):
- Test audio conversion (48kHz/16-bit)
- Test validation (duration, format, readability)
- Test filename sanitization (unicode, special chars)
- Test organization logic (flat, genre, BPM)
- Test error handling (missing files, corrupt audio)

**Model Tests** (`backend/tests/models/test_sp404_export.py`):
- Test export record creation
- Test relationships (export → samples)
- Test cascading deletes

**Schema Tests** (`backend/tests/schemas/test_sp404_export.py`):
- Test validation (format, organization)
- Test serialization/deserialization

### Integration Tests

**API Tests** (`backend/tests/api/test_sp404_export.py`):
- Test single sample export endpoint
- Test batch export endpoint
- Test kit export endpoint
- Test download endpoint
- Test error responses

**Database Tests**:
- Test export tracking
- Test query performance
- Test concurrent exports

### E2E Tests

**Browser Tests** (`frontend/tests/e2e/test_export.spec.js`):
- Test export button click
- Test format selection
- Test organization selection
- Test download initiation
- Test error display

### Test Fixtures

**Audio Files** (`backend/tests/fixtures/audio/`):
- `test_sample_48k.wav` - Already correct format
- `test_sample_44k.mp3` - Needs conversion
- `test_sample_stereo.wav` - Stereo file
- `test_sample_short.wav` - <100ms (should fail)
- `test_sample_unicode_名前.wav` - Unicode filename

**Database Fixtures**:
```python
@pytest.fixture
async def sample_for_export(db_session):
    """Create sample with valid audio file."""
    sample = Sample(
        title="Test Sample",
        file_path="/path/to/test_sample.wav",
        genre="hip-hop",
        bpm=95.0,
        user_id=1
    )
    db_session.add(sample)
    await db_session.commit()
    return sample
```

### Test Coverage Goals

- **Service Layer**: >90% coverage
- **API Endpoints**: >85% coverage
- **Models**: >95% coverage
- **Critical Paths**: 100% coverage (conversion, validation)

---

## Implementation Checklist

### Phase 1: Core Service (Week 1)

- [ ] Create `backend/app/models/sp404_export.py`
  - [ ] SP404Export model
  - [ ] SP404ExportSample model
  - [ ] Relationships to User and Sample

- [ ] Update existing models
  - [ ] Add sp404_exports to User model
  - [ ] Add sp404_export_samples to Sample model
  - [ ] Add SP-404 preferences to UserPreference model

- [ ] Create `backend/app/schemas/sp404_export.py`
  - [ ] ExportConfig schema
  - [ ] ConversionResult schema
  - [ ] ValidationResult schema
  - [ ] ExportResult schema
  - [ ] BatchExportResult schema
  - [ ] Response schemas

- [ ] Create `backend/app/services/sp404_export_service.py`
  - [ ] SP404ExportService class
  - [ ] convert_to_sp404_format() method
  - [ ] validate_sample() method
  - [ ] sanitize_filename() method
  - [ ] export_single_sample() method
  - [ ] Organization helper methods

### Phase 2: API Endpoints (Week 1-2)

- [ ] Create `backend/app/api/v1/endpoints/sp404_export.py`
  - [ ] POST /sp404/samples/{id}/export
  - [ ] POST /sp404/samples/export-batch
  - [ ] POST /sp404/kits/{id}/export
  - [ ] GET /sp404/exports/{id}/download
  - [ ] GET /sp404/exports (history)

- [ ] Update API router
  - [ ] Include sp404_export router
  - [ ] Add to OpenAPI docs

### Phase 3: Batch & Kit Support (Week 2)

- [ ] Implement batch export
  - [ ] export_batch() method
  - [ ] Batch error handling
  - [ ] Export tracking

- [ ] Implement kit export
  - [ ] export_kit() method
  - [ ] Bank/pad organization
  - [ ] Kit folder structure

- [ ] Implement ZIP download
  - [ ] create_export_zip() method
  - [ ] FileResponse handling

### Phase 4: Database Migration (Week 2)

- [ ] Create Alembic migration
  - [ ] Add sp404_exports table
  - [ ] Add sp404_export_samples table
  - [ ] Add user preferences columns
  - [ ] Add indexes

- [ ] Test migration
  - [ ] Upgrade
  - [ ] Downgrade
  - [ ] Data integrity

### Phase 5: Testing (Week 3)

- [ ] Unit tests
  - [ ] Service tests (conversion, validation, organization)
  - [ ] Model tests
  - [ ] Schema tests

- [ ] Integration tests
  - [ ] API endpoint tests
  - [ ] Database tests

- [ ] E2E tests (coordinated with Frontend)
  - [ ] Export workflow
  - [ ] Download workflow

- [ ] Test fixtures
  - [ ] Audio files
  - [ ] Database fixtures

### Phase 6: Documentation (Week 3)

- [ ] API documentation
  - [ ] Endpoint descriptions
  - [ ] Request/response examples
  - [ ] Error codes

- [ ] User documentation
  - [ ] Export guide
  - [ ] Organization strategies
  - [ ] Hardware compatibility

- [ ] Developer documentation
  - [ ] Service architecture
  - [ ] Extension points
  - [ ] Performance tuning

### Phase 7: Frontend Integration (Week 4)

- [ ] Export button UI
- [ ] Configuration modal
- [ ] Download handling
- [ ] Progress indication
- [ ] Error display

---

## Appendices

### A. SP-404MK2 Hardware Specifications

**Audio Format Requirements**:
- Sample Rate: 48 kHz (mandatory on import)
- Bit Depth: 16-bit PCM
- Formats: WAV, AIFF (input); MP3, FLAC, M4A supported but converted
- Duration: Minimum 100ms (shorter samples rejected)

**File System Limitations**:
- Filename Length: Max 255 characters
- Character Set: ASCII recommended (double-byte may not display)
- Special Characters: Avoid in filenames

**Organization**:
- Banks: A, B, C, D (16 pads each, 64 total)
- Projects: Can save bank configurations
- SD Card: FAT32 format recommended

### B. Audio Processing Libraries

**librosa** (0.10.0+):
- Audio loading: librosa.load()
- Resampling: librosa.resample()
- Duration: librosa.get_duration()
- Feature extraction: tempo, key, spectral features

**soundfile** (0.12.0+):
- Audio writing: sf.write()
- Format support: WAV, AIFF, FLAC, OGG
- Subtype support: PCM_16, PCM_24, PCM_32, FLOAT

**numpy** (1.24.0+):
- Array operations
- Signal processing
- Matrix operations

### C. Performance Optimization Notes

**Caching Opportunities**:
- Resampling filters (librosa)
- Validation results
- Filename sanitization mapping

**Parallelization**:
- Process multiple samples in parallel (batch mode)
- Use multiprocessing for CPU-bound work
- Limit concurrent operations to avoid resource exhaustion

**Memory Optimization**:
- Stream large files
- Process in chunks
- Release memory immediately after conversion

**Database Optimization**:
- Use indexes for common queries
- Batch insert export records
- Connection pooling
- Async operations throughout

---

**END OF ARCHITECTURAL DESIGN DOCUMENT**

This design is ready for:
1. **Test Writer Agent**: Create comprehensive test suite
2. **Coder Agent**: Implement service, models, schemas, and API
3. **Frontend Team**: Design UI integration points
4. **DevOps**: Plan deployment and monitoring

All integration points with existing services are documented and ready for implementation.
