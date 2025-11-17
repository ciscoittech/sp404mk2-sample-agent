"""
SP-404MK2 Project Builder Service

Orchestrates complete project generation from kits:
1. Fetches kit and samples from database
2. Exports audio samples (format conversion to 48kHz/16-bit)
3. Builds PADCONF.BIN using PadconfService
4. Creates PROJECT_INFO.txt metadata file
5. Packages everything into ZIP archive
6. Tracks export in database

Output structure:
    project_name.zip
        ├── PADCONF.BIN (52,000 bytes)
        ├── PROJECT_INFO.txt (metadata)
        └── samples/
            ├── sample_001.wav
            ├── sample_002.wav
            └── ...
"""

import logging
import time
import uuid
import statistics
import zipfile
import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kit import Kit, KitSample
from app.models.sample import Sample
from app.models.sp404_export import SP404Export, SP404ExportSample
from app.schemas.sp404_project import ProjectBuildRequest, ProjectBuildResult
from app.services.padconf_service import PadconfService, PadConfig, ProjectConfig
from app.services.sp404_export_service import SP404ExportService

logger = logging.getLogger(__name__)


class SP404ProjectBuilderError(Exception):
    """Base exception for project builder errors"""
    pass


class SP404ProjectBuilderService:
    """
    Service for building complete SP-404MK2 projects from kits.

    Handles:
    - Kit validation and sample retrieval
    - BPM auto-detection (median or fallback)
    - Audio conversion to SP-404 format
    - PADCONF.BIN generation
    - ZIP packaging
    - Database export tracking
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize project builder service.

        Args:
            db_session: SQLAlchemy async database session
        """
        self.db = db_session
        self.padconf_service = PadconfService()
        self.export_service = SP404ExportService(db_session)

    async def build_project(
        self,
        kit_id: int,
        request: ProjectBuildRequest,
        output_base_path: Optional[Path] = None
    ) -> ProjectBuildResult:
        """
        Build complete SP-404MK2 project from kit.

        Process:
        1. Validate kit exists and has samples
        2. Auto-detect or use custom BPM
        3. Create temporary working directory
        4. Export audio samples to samples/ directory
        5. Build PADCONF.BIN from kit layout
        6. Create PROJECT_INFO.txt
        7. Package into ZIP archive
        8. Save export record to database
        9. Return result with download URL

        Args:
            kit_id: Database ID of kit to export
            request: Project build configuration
            output_base_path: Optional custom export directory (defaults to /tmp/sp404_projects)

        Returns:
            ProjectBuildResult with success status and download information

        Raises:
            SP404ProjectBuilderError: On critical failures
        """
        start_time = time.time()

        try:
            # 1. Fetch kit from database
            kit = await self._get_kit(kit_id)
            if not kit:
                return ProjectBuildResult(
                    success=False,
                    error_message=f"Kit {kit_id} not found"
                )

            # 2. Fetch kit samples
            samples = await self._get_kit_samples(kit_id)
            if not samples:
                return ProjectBuildResult(
                    success=False,
                    error_message=f"Kit {kit_id} has no samples",
                    sample_count=0
                )

            # 3. Detect or use custom BPM
            project_bpm = request.project_bpm or self._detect_project_bpm(samples)

            # 4. Create temporary working directory
            if output_base_path is None:
                output_base_path = Path("/tmp/sp404_projects")

            output_base_path.mkdir(parents=True, exist_ok=True)

            # Create unique project directory
            project_id = uuid.uuid4().hex[:8]
            project_dir = output_base_path / f"{request.project_name}_{project_id}"
            project_dir.mkdir(parents=True, exist_ok=True)

            samples_dir = project_dir / "samples"
            samples_dir.mkdir(exist_ok=True)

            # 5. Export audio samples with format conversion
            logger.info(f"Exporting {len(samples)} samples to {samples_dir}")
            exported_paths = await self._export_audio_samples(
                samples=samples,
                format=request.audio_format,
                output_dir=samples_dir
            )

            # 6. Build PadConfig objects for PADCONF.BIN
            pad_configs = await self._build_pad_configs(
                kit_id=kit_id,
                samples=samples,
                project_bpm=project_bpm
            )

            # 7. Generate PADCONF.BIN
            project_config = ProjectConfig(
                project_name=request.project_name,
                project_bpm=project_bpm,
                tempo_mode="project"
            )

            padconf_data = self.padconf_service.create_padconf(
                project_config=project_config,
                pad_configs=pad_configs
            )

            # Write PADCONF.BIN to project directory
            padconf_path = project_dir / "PADCONF.BIN"
            padconf_path.write_bytes(padconf_data)

            logger.info(f"Generated PADCONF.BIN: {len(padconf_data)} bytes")

            # 8. Create PROJECT_INFO.txt
            info_path = project_dir / "PROJECT_INFO.txt"
            await self._create_project_info(
                info_path=info_path,
                kit=kit,
                request=request,
                project_bpm=project_bpm,
                sample_count=len(samples)
            )

            # 9. Create ZIP archive
            zip_path = await self._create_project_zip(
                project_dir=project_dir,
                project_name=request.project_name,
                output_base_path=output_base_path
            )

            # Calculate file size
            file_size = zip_path.stat().st_size

            # Calculate duration
            duration = time.time() - start_time

            # 10. Save export record to database
            export_id = await self._create_export_record(
                kit_id=kit_id,
                project_name=request.project_name,
                sample_count=len(samples),
                output_path=str(zip_path),
                format=request.audio_format,
                file_size=file_size,
                duration=duration,
                samples=samples
            )

            # 11. Generate download URL
            download_url = f"/api/v1/projects/download/{export_id}"

            logger.info(
                f"Project build successful: {request.project_name} "
                f"({len(samples)} samples, {file_size} bytes, {duration:.2f}s)"
            )

            return ProjectBuildResult(
                success=True,
                export_id=str(export_id),
                project_name=request.project_name,
                sample_count=len(samples),
                file_size_bytes=file_size,
                download_url=download_url
            )

        except Exception as e:
            logger.error(f"Project build failed for kit {kit_id}: {e}", exc_info=True)
            return ProjectBuildResult(
                success=False,
                error_message=str(e)
            )

    def _detect_project_bpm(self, samples: List[Sample]) -> float:
        """
        Detect project BPM from sample BPMs.

        Strategy:
        - Use median BPM if samples have BPM data
        - Fallback to 120.0 BPM if no BPM data available

        Args:
            samples: List of samples to analyze

        Returns:
            Detected BPM (median or fallback)
        """
        # Collect valid BPMs
        bpms = [float(s.bpm) for s in samples if s.bpm is not None]

        if not bpms:
            logger.info("No BPM data available, using fallback BPM 120.0")
            return 120.0

        # Use median to avoid outliers
        median_bpm = float(statistics.median(bpms))

        logger.info(f"Detected project BPM: {median_bpm} (median of {len(bpms)} samples)")

        return median_bpm

    async def _export_audio_samples(
        self,
        samples: List[Sample],
        format: str,
        output_dir: Path
    ) -> List[Path]:
        """
        Export and convert audio samples to SP-404 format.

        Converts all samples to 48kHz/16-bit WAV or AIFF.

        Args:
            samples: List of samples to export
            format: Output format (wav or aiff)
            output_dir: Directory to write converted samples

        Returns:
            List of paths to converted audio files

        Raises:
            SP404ProjectBuilderError: If conversion fails
        """
        exported_paths = []

        for i, sample in enumerate(samples):
            input_path = Path(sample.file_path)

            # Generate output filename (sanitized, numbered)
            # Use sample title if available, otherwise use original filename
            base_name = str(sample.title or input_path.stem)
            sanitized_name = self.export_service.sanitize_filename(base_name)

            # Number samples sequentially (001, 002, etc.)
            output_filename = f"{sanitized_name}_{i+1:03d}.{format}"
            output_path = output_dir / output_filename

            # Convert using SP404ExportService
            conversion_result = await self.export_service.convert_to_sp404_format(
                input_path=input_path,
                output_path=output_path,
                format=format
            )

            if not conversion_result.success:
                raise SP404ProjectBuilderError(
                    f"Failed to convert sample {sample.id}: {conversion_result.error_message}"
                )

            exported_paths.append(output_path)

        logger.info(f"Exported {len(exported_paths)} audio files to {output_dir}")

        return exported_paths

    async def _build_pad_configs(
        self,
        kit_id: int,
        samples: List[Sample],
        project_bpm: float
    ) -> List[PadConfig]:
        """
        Build PadConfig objects for each sample in kit.

        Maps samples to their assigned pads (bank + pad number).
        Sets BPM, volume, and other pad parameters.

        Args:
            kit_id: Kit database ID
            samples: List of samples in kit
            project_bpm: Project BPM for BPM sync

        Returns:
            List of PadConfig objects for PADCONF.BIN generation
        """
        pad_configs = []

        # Fetch kit sample assignments
        stmt = select(KitSample).where(KitSample.kit_id == kit_id)
        result = await self.db.execute(stmt)
        kit_samples = result.scalars().all()

        # Create mapping of sample_id -> KitSample
        kit_sample_map = {ks.sample_id: ks for ks in kit_samples}

        for i, sample in enumerate(samples):
            kit_sample = kit_sample_map.get(sample.id)

            if not kit_sample:
                logger.warning(f"Sample {sample.id} not found in kit assignments, skipping")
                continue

            # Calculate global pad index (1-160)
            # Bank A=1-16, B=17-32, C=33-48, etc.
            bank_letter = str(kit_sample.pad_bank)
            bank_offset = (ord(bank_letter) - ord('A')) * 16
            pad_index = int(bank_offset + kit_sample.pad_number)

            # Get sample filename
            filename = Path(sample.file_path).name

            # Sanitize filename (SP-404 requirement)
            filename = self.export_service.sanitize_filename(filename)

            # Create PadConfig
            sample_bpm = float(sample.bpm) if sample.bpm is not None else project_bpm

            pad_config = PadConfig(
                pad_index=pad_index,
                filename=filename,
                sample_start=0,
                sample_end=0,
                bpm=sample_bpm,
                volume=100,  # Default volume
                pitch=0,
                fine_tune=0,
                speed=10000,
                bpm_sync=False,  # User can enable in hardware
                loop=False,
                gate=False,
                vinyl_effect=False,
                loop_point=0,
                loop_mode=0,
                pan=64,
                mute_group=0,
                pad_link=0,
                bus_route=0,
                attack=0,
                hold=0,
                release=0,
                one_shot_mode=0
            )

            pad_configs.append(pad_config)

        logger.info(f"Built {len(pad_configs)} PadConfig objects")

        return pad_configs

    async def _create_project_zip(
        self,
        project_dir: Path,
        project_name: str,
        output_base_path: Path
    ) -> Path:
        """
        Package project into ZIP archive.

        Structure:
            project_name.zip
                ├── PADCONF.BIN
                ├── PROJECT_INFO.txt
                └── samples/
                    ├── sample_001.wav
                    └── ...

        Args:
            project_dir: Directory containing project files
            project_name: Name for ZIP file
            output_base_path: Directory to save ZIP

        Returns:
            Path to created ZIP file
        """
        # Sanitize project name for filename
        safe_project_name = self.export_service.sanitize_filename(project_name).replace('.', '')

        zip_path = output_base_path / f"{safe_project_name}.zip"

        # Create ZIP archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add PADCONF.BIN
            padconf_path = project_dir / "PADCONF.BIN"
            if padconf_path.exists():
                zf.write(padconf_path, "PADCONF.BIN")

            # Add PROJECT_INFO.txt
            info_path = project_dir / "PROJECT_INFO.txt"
            if info_path.exists():
                zf.write(info_path, "PROJECT_INFO.txt")

            # Add all samples
            samples_dir = project_dir / "samples"
            if samples_dir.exists():
                for sample_file in samples_dir.iterdir():
                    if sample_file.is_file():
                        # Add with samples/ prefix
                        zf.write(sample_file, f"samples/{sample_file.name}")

        logger.info(f"Created ZIP archive: {zip_path} ({zip_path.stat().st_size} bytes)")

        return zip_path

    async def _create_project_info(
        self,
        info_path: Path,
        kit: Kit,
        request: ProjectBuildRequest,
        project_bpm: float,
        sample_count: int
    ) -> None:
        """
        Create PROJECT_INFO.txt metadata file.

        Contains useful information about the project for reference.

        Args:
            info_path: Path where info file will be written
            kit: Kit object
            request: Project build request
            project_bpm: Detected or custom BPM
            sample_count: Number of samples in project
        """
        info_lines = [
            "# SP-404MK2 Project Information",
            "",
            f"Project Name: {request.project_name}",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Source Kit",
            f"Kit Name: {kit.name}",
            f"Kit Description: {kit.description or 'N/A'}",
            "",
            "## Project Settings",
            f"Project BPM: {project_bpm}",
            f"Audio Format: {request.audio_format.upper()}",
            f"Sample Count: {sample_count}",
            "",
            "## Hardware Import Instructions",
            "1. Copy this ZIP file to SD card",
            "2. Extract on SP-404MK2 (or extract on computer and copy folder)",
            "3. Load PADCONF.BIN using [PROJECT] button",
            "4. Samples should auto-load from samples/ directory",
            "",
            "## Notes",
            "- All samples converted to 48kHz/16-bit for SP-404MK2 compatibility",
            "- PADCONF.BIN contains pad assignments and settings",
            "- Adjust BPM sync, loop points, and effects on hardware",
            "",
            f"Generated by SP-404MK2 Sample Agent v1.0"
        ]

        info_path.write_text('\n'.join(info_lines))

        logger.debug(f"Created PROJECT_INFO.txt: {info_path}")

    async def _get_kit(self, kit_id: int) -> Optional[Kit]:
        """Fetch kit from database"""
        stmt = select(Kit).where(Kit.id == kit_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_kit_samples(self, kit_id: int) -> List[Sample]:
        """Fetch all samples for a kit"""
        stmt = (
            select(Sample)
            .join(KitSample)
            .where(KitSample.kit_id == kit_id)
            .order_by(KitSample.pad_bank, KitSample.pad_number)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _create_export_record(
        self,
        kit_id: int,
        project_name: str,
        sample_count: int,
        output_path: str,
        format: str,
        file_size: int,
        duration: float,
        samples: List[Sample]
    ) -> int:
        """
        Create database record for this export.

        Args:
            kit_id: Source kit ID
            project_name: Project name
            sample_count: Number of samples exported
            output_path: Path to ZIP file
            format: Audio format used
            file_size: Total ZIP file size
            duration: Export duration in seconds
            samples: List of exported samples

        Returns:
            Export record ID
        """
        export_record = SP404Export(
            user_id=None,  # TODO: Add user tracking when auth is implemented
            export_type="project",
            sample_count=sample_count,
            output_path=output_path,
            organized_by="kit",
            format=format,
            total_size_bytes=file_size,
            export_duration_seconds=duration
        )

        self.db.add(export_record)
        await self.db.flush()

        # Create records for each exported sample
        for sample in samples:
            export_sample = SP404ExportSample(
                export_id=export_record.id,
                sample_id=sample.id,
                output_filename=f"{sample.title or 'sample'}.{format}",
                conversion_successful=True,
                file_size_bytes=0,  # Individual size not tracked for projects
                conversion_time_seconds=0
            )
            self.db.add(export_sample)

        await self.db.commit()
        await self.db.refresh(export_record)

        logger.info(f"Created export record {export_record.id} for project '{project_name}'")

        return int(export_record.id)
