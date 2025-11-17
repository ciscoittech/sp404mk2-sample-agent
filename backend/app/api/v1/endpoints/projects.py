"""
SP-404MK2 Project Builder API Endpoints

Provides REST API for building complete SP-404 projects from kits:
- POST /from-kit/{kit_id} - Build project from kit with PADCONF.BIN
- GET /download/{export_id} - Download generated project ZIP

Returns:
- ProjectBuildResult for build operations
- FileResponse for downloads
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.sp404_export import SP404Export
from app.schemas.sp404_project import ProjectBuildRequest, ProjectBuildResult
from app.services.sp404_project_builder_service import SP404ProjectBuilderService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/from-kit/{kit_id}", response_model=ProjectBuildResult)
async def build_project_from_kit(
    kit_id: int,
    request: ProjectBuildRequest,
    output_base_path: Optional[str] = Query(None, description="Custom export directory"),
    db: AsyncSession = Depends(get_db)
) -> ProjectBuildResult:
    """
    Build SP-404MK2 project from kit.

    Creates complete project package with:
    - PADCONF.BIN (52,000 bytes, hardware-compatible pad configuration)
    - samples/ directory (all samples converted to 48kHz/16-bit WAV/AIFF)
    - PROJECT_INFO.txt (metadata for reference)

    Process:
    1. Validates kit exists and has samples
    2. Auto-detects BPM (median) or uses custom BPM
    3. Exports and converts all audio samples
    4. Generates PADCONF.BIN with pad assignments
    5. Packages into ZIP archive
    6. Returns download URL

    Args:
        kit_id: Database ID of kit to export
        request: Project build configuration (name, BPM, format)
        output_base_path: Optional custom export directory
        db: Database session (injected)

    Returns:
        ProjectBuildResult with success status and download information

    Example Request:
        POST /api/v1/projects/from-kit/123
        {
            "project_name": "HipHopBeats",
            "project_bpm": null,  // Auto-detect
            "audio_format": "wav",
            "include_bank_layout": false
        }

    Example Response:
        {
            "success": true,
            "export_id": "42",
            "project_name": "HipHopBeats",
            "sample_count": 12,
            "file_size_bytes": 5242880,
            "download_url": "/api/v1/projects/download/42"
        }

    Errors:
        - 422: Invalid request (bad BPM, format, or project name)
        - 200 with success=false: Kit not found or has no samples
    """
    logger.info(f"Building project from kit {kit_id}: {request.project_name}")

    # Initialize service
    service = SP404ProjectBuilderService(db)

    # Convert output path if provided
    output_path = Path(output_base_path) if output_base_path else None

    # Build project
    result = await service.build_project(
        kit_id=kit_id,
        request=request,
        output_base_path=output_path
    )

    if result.success:
        logger.info(
            f"Project build successful: {result.project_name} "
            f"({result.sample_count} samples, {result.file_size_bytes} bytes)"
        )
    else:
        logger.warning(f"Project build failed for kit {kit_id}: {result.error_message}")

    return result


@router.get("/download/{export_id}")
async def download_project(
    export_id: int,
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Download generated project ZIP file.

    Streams ZIP file containing:
    - PADCONF.BIN (hardware configuration)
    - samples/ directory (converted audio)
    - PROJECT_INFO.txt (metadata)

    Args:
        export_id: Export record ID from build response
        db: Database session (injected)

    Returns:
        FileResponse with ZIP file (application/zip)

    Example:
        GET /api/v1/projects/download/42
        → Returns: project_name.zip (streaming download)

    Errors:
        - 404: Export not found or file doesn't exist
    """
    logger.info(f"Download request for export {export_id}")

    # Fetch export record
    stmt = select(SP404Export).where(SP404Export.id == export_id)
    result = await db.execute(stmt)
    export_record = result.scalar_one_or_none()

    if not export_record:
        logger.warning(f"Export {export_id} not found")
        raise HTTPException(status_code=404, detail="Export not found")

    # Verify file exists
    file_path = Path(export_record.output_path)
    if not file_path.exists():
        logger.error(f"Export file not found: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Export file not found: {file_path}"
        )

    # Return file as streaming download
    logger.info(f"Serving export file: {file_path} ({file_path.stat().st_size} bytes)")

    return FileResponse(
        path=str(file_path),
        media_type="application/zip",
        filename=file_path.name
    )
