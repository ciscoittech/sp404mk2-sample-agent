"""
Kit Builder API endpoints.

Provides REST API for:
- Kit CRUD operations
- Pad assignment management
- Sample recommendations
- Kit export (ZIP download)

Supports both JSON and HTMX responses.
"""
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from io import BytesIO

from fastapi import APIRouter, Depends, Request, Header, HTTPException, status, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.kit_service import (
    KitService,
    KitNotFoundError,
    SampleNotFoundError,
    InvalidPadNumberError,
    InvalidPadBankError,
    PadAlreadyAssignedError,
)
from app.services.sp404_export_service import SP404ExportService
from app.schemas.kit import (
    KitCreate,
    KitUpdate,
    KitResponse,
    KitListResponse,
    PadAssignmentRequest,
    PadAssignmentResponse,
    PadAssignmentInfo,
    SampleInfo,
    SampleRecommendation,
    RecommendationsResponse,
)
from app.models.kit import Kit, KitSample

logger = logging.getLogger(__name__)

router = APIRouter()

# Hardcoded user ID for public API (no auth in MVP)
DEFAULT_USER_ID = 1


def kit_to_response(kit: Kit) -> KitResponse:
    """Convert Kit model to response schema."""
    # Convert samples relationship
    samples = []
    for assignment in kit.samples:
        sample_info = SampleInfo(
            id=assignment.sample.id,
            title=assignment.sample.title,
            file_path=assignment.sample.file_path,
            duration=assignment.sample.duration,
            bpm=assignment.sample.bpm,
            genre=assignment.sample.genre,
            tags=assignment.sample.tags or [],
        )

        pad_assignment = PadAssignmentInfo(
            kit_id=assignment.kit_id,
            sample_id=assignment.sample_id,
            pad_bank=assignment.pad_bank,
            pad_number=assignment.pad_number,
            volume=assignment.volume,
            pitch_shift=assignment.pitch_shift,
            sample=sample_info,
        )
        samples.append(pad_assignment)

    return KitResponse(
        id=kit.id,
        user_id=kit.user_id,
        name=kit.name,
        description=kit.description,
        is_public=kit.is_public,
        created_at=kit.created_at,
        updated_at=kit.updated_at,
        samples=samples,
    )


# ===========================
# Kit CRUD Endpoints
# ===========================

@router.get("", response_model=KitListResponse)
async def list_kits(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of kits to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum kits to return"),
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None),
):
    """
    List all kits for the user with pagination.

    Returns JSON by default, HTML template for HTMX requests.
    """
    logger.info(f"Listing kits (skip={skip}, limit={limit})")

    kit_service = KitService()
    kits = await kit_service.get_user_kits(
        db=db,
        user_id=DEFAULT_USER_ID,
        skip=skip,
        limit=limit,
    )

    # Get total count (separate query for accurate pagination)
    from sqlalchemy import select, func
    count_query = select(func.count()).select_from(Kit).where(Kit.user_id == DEFAULT_USER_ID)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # HTMX response
    if hx_request:
        from app.templates_config import templates

        kit_dicts = []
        for kit in kits:
            kit_dict = {
                "id": kit.id,
                "name": kit.name,
                "description": kit.description,
                "is_public": kit.is_public,
                "created_at": kit.created_at,
                "sample_count": len(kit.samples),
            }
            kit_dicts.append(kit_dict)

        return templates.TemplateResponse("kits/kit-list.html", {
            "request": request,
            "kits": kit_dicts,
            "total": total,
        })

    # JSON response
    kit_responses = [kit_to_response(kit) for kit in kits]
    return KitListResponse(
        kits=kit_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=KitResponse, status_code=status.HTTP_201_CREATED)
async def create_kit(
    kit_data: KitCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new kit.

    Always returns JSON (even for HTMX requests).
    """
    logger.info(f"Creating kit: {kit_data.name}")

    kit_service = KitService()

    try:
        kit = await kit_service.create_kit(
            db=db,
            user_id=DEFAULT_USER_ID,
            name=kit_data.name,
            description=kit_data.description,
        )
    except ValueError as e:
        logger.error(f"Validation error creating kit: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return kit_to_response(kit)


@router.get("/{kit_id}", response_model=KitResponse)
async def get_kit(
    kit_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None),
):
    """
    Get kit details by ID.

    Returns JSON by default, HTML template for HTMX requests.
    """
    logger.info(f"Getting kit {kit_id}")

    kit_service = KitService()
    kit = await kit_service.get_kit_by_id(
        db=db,
        kit_id=kit_id,
        user_id=DEFAULT_USER_ID,
    )

    if not kit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )

    # HTMX response
    if hx_request:
        from app.templates_config import templates

        # Convert to dict for template
        kit_dict = {
            "id": kit.id,
            "name": kit.name,
            "description": kit.description,
            "is_public": kit.is_public,
            "created_at": kit.created_at,
            "samples": []
        }

        for assignment in kit.samples:
            sample_dict = {
                "id": assignment.sample.id,
                "title": assignment.sample.title,
                "pad_bank": assignment.pad_bank,
                "pad_number": assignment.pad_number,
                "volume": assignment.volume,
                "pitch_shift": assignment.pitch_shift,
            }
            kit_dict["samples"].append(sample_dict)

        return templates.TemplateResponse("kits/kit-detail.html", {
            "request": request,
            "kit": kit_dict,
        })

    # JSON response
    return kit_to_response(kit)


@router.patch("/{kit_id}", response_model=KitResponse)
async def update_kit(
    kit_id: int,
    kit_data: KitUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update kit metadata (partial update allowed).
    """
    logger.info(f"Updating kit {kit_id}")

    kit_service = KitService()

    try:
        kit = await kit_service.update_kit(
            db=db,
            kit_id=kit_id,
            user_id=DEFAULT_USER_ID,
            name=kit_data.name,
            description=kit_data.description,
            is_public=kit_data.is_public,
        )
    except KitNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )
    except ValueError as e:
        logger.error(f"Validation error updating kit: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return kit_to_response(kit)


@router.delete("/{kit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kit(
    kit_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a kit and all its pad assignments.
    """
    logger.info(f"Deleting kit {kit_id}")

    kit_service = KitService()
    success = await kit_service.delete_kit(
        db=db,
        kit_id=kit_id,
        user_id=DEFAULT_USER_ID,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )

    return None


# ===========================
# Pad Assignment Endpoints
# ===========================

@router.post("/{kit_id}/assign", response_model=PadAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_sample_to_pad(
    kit_id: int,
    assignment_data: PadAssignmentRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None),
):
    """
    Assign a sample to a pad in the kit.

    Returns JSON by default, HTML template for HTMX requests.
    """
    logger.info(
        f"Assigning sample {assignment_data.sample_id} to kit {kit_id} "
        f"pad {assignment_data.pad_bank}{assignment_data.pad_number}"
    )

    kit_service = KitService()

    try:
        assignment = await kit_service.assign_sample_to_pad(
            db=db,
            kit_id=kit_id,
            sample_id=assignment_data.sample_id,
            pad_bank=assignment_data.pad_bank,
            pad_number=assignment_data.pad_number,
            user_id=DEFAULT_USER_ID,
            volume=assignment_data.volume,
            pitch_shift=assignment_data.pitch_shift,
        )
    except KitNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )
    except SampleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (InvalidPadBankError, InvalidPadNumberError, PadAlreadyAssignedError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Build response
    sample_info = SampleInfo(
        id=assignment.sample.id,
        title=assignment.sample.title,
        file_path=assignment.sample.file_path,
        duration=assignment.sample.duration,
        bpm=assignment.sample.bpm,
        genre=assignment.sample.genre,
        tags=assignment.sample.tags or [],
    )

    response = PadAssignmentResponse(
        kit_id=assignment.kit_id,
        sample_id=assignment.sample_id,
        pad_bank=assignment.pad_bank,
        pad_number=assignment.pad_number,
        volume=assignment.volume,
        pitch_shift=assignment.pitch_shift,
        sample=sample_info,
    )

    # HTMX response
    if hx_request:
        from app.templates_config import templates

        assignment_dict = {
            "pad_bank": assignment.pad_bank,
            "pad_number": assignment.pad_number,
            "sample_title": assignment.sample.title,
            "volume": assignment.volume,
            "pitch_shift": assignment.pitch_shift,
        }

        response = templates.TemplateResponse("kits/pad-assignment.html", {
            "request": request,
            "assignment": assignment_dict,
        })
        response.status_code = status.HTTP_201_CREATED
        return response

    # JSON response
    return response


@router.delete("/{kit_id}/pads/{pad_bank}/{pad_number}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_sample_from_pad(
    kit_id: int,
    pad_bank: str,
    pad_number: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a sample assignment from a pad.
    """
    logger.info(f"Removing sample from kit {kit_id} pad {pad_bank}{pad_number}")

    kit_service = KitService()

    try:
        success = await kit_service.remove_sample_from_pad(
            db=db,
            kit_id=kit_id,
            pad_bank=pad_bank,
            pad_number=pad_number,
            user_id=DEFAULT_USER_ID,
        )
    except KitNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sample assigned to pad {pad_bank}{pad_number}",
        )

    return None


# ===========================
# Recommendation Endpoints
# ===========================

@router.get("/{kit_id}/recommendations/{pad_number}", response_model=RecommendationsResponse)
async def get_recommendations_for_pad(
    kit_id: int,
    pad_number: int,
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendations"),
    db: AsyncSession = Depends(get_db),
    hx_request: Optional[str] = Header(None),
):
    """
    Get smart sample recommendations for a pad.

    Returns JSON by default, HTML template for HTMX requests.
    """
    logger.info(f"Getting recommendations for kit {kit_id} pad {pad_number}")

    kit_service = KitService()

    try:
        samples = await kit_service.get_recommended_samples(
            db=db,
            kit_id=kit_id,
            pad_number=pad_number,
            user_id=DEFAULT_USER_ID,
            limit=limit,
        )
    except InvalidPadNumberError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except KitNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )

    # Build recommendations with reasons
    recommendations = []
    for sample in samples:
        reason = f"Recommended for pad {pad_number}"

        # Add specific reason based on sample properties
        if sample.duration and sample.duration >= 3.0:
            reason = "Long sample suitable for loops"
        elif sample.duration and sample.duration <= 1.0:
            reason = "Short sample suitable for one-shots"

        if sample.tags:
            matching_tags = [t for t in sample.tags if t in ["kick", "snare", "hat", "loop"]]
            if matching_tags:
                reason = f"Matched tags: {', '.join(matching_tags)}"

        rec = SampleRecommendation(
            id=sample.id,
            title=sample.title,
            file_path=sample.file_path,
            duration=sample.duration,
            bpm=sample.bpm,
            genre=sample.genre,
            tags=sample.tags or [],
            recommendation_reason=reason,
        )
        recommendations.append(rec)

    # HTMX response
    if hx_request:
        from app.templates_config import templates

        rec_dicts = []
        for rec in recommendations:
            rec_dict = {
                "id": rec.id,
                "title": rec.title,
                "bpm": rec.bpm,
                "genre": rec.genre,
                "reason": rec.recommendation_reason,
            }
            rec_dicts.append(rec_dict)

        return templates.TemplateResponse("kits/recommendations-dropdown.html", {
            "request": request,
            "recommendations": rec_dicts,
            "pad_number": pad_number,
        })

    # JSON response
    return RecommendationsResponse(
        kit_id=kit_id,
        pad_number=pad_number,
        samples=recommendations,
        total=len(recommendations),
    )


# ===========================
# Export Endpoints
# ===========================

@router.post("/{kit_id}/export")
async def export_kit(
    kit_id: int,
    format: str = Query("wav", pattern="^(wav|aiff)$", description="Output format"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export kit as ZIP file with audio samples and pad assignments.

    Returns ZIP file for download.
    """
    logger.info(f"Exporting kit {kit_id} as {format}")

    kit_service = KitService()

    # Prepare export manifest
    try:
        manifest = await kit_service.prepare_kit_export(
            db=db,
            kit_id=kit_id,
            user_id=DEFAULT_USER_ID,
            output_format=format,
        )
    except KitNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kit {kit_id} not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Create ZIP file in memory
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add pad assignments text file
        pad_assignments_text = []
        for sample in sorted(manifest.samples, key=lambda s: s.pad_number):
            pad_assignments_text.append(
                f"Pad {sample.pad_number}: {sample.export_filename}"
            )

        assignments_content = "\n".join(pad_assignments_text)
        zip_file.writestr("pad_assignments.txt", assignments_content)

        # Add audio files (converted to SP-404 format)
        export_service = SP404ExportService(db)

        for sample_info in manifest.samples:
            input_path = Path(sample_info.file_path)

            # Check if file exists
            if not input_path.exists():
                logger.warning(f"Sample file not found: {input_path}")
                continue

            # Create temp file for conversion
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                temp_path = Path(temp_file.name)

            try:
                # Convert to SP-404 format
                await export_service.convert_to_sp404_format(
                    input_path=input_path,
                    output_path=temp_path,
                    format=format,
                )

                # Add to ZIP
                zip_file.write(temp_path, sample_info.export_filename)

            except Exception as e:
                logger.error(f"Error converting {input_path}: {e}")
                # Continue with other samples

            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()

    # Prepare response
    zip_buffer.seek(0)

    filename = f"{manifest.kit_name.replace(' ', '_')}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# ===========================
# AI Kit Builder Endpoint
# ===========================

@router.post("/build", response_model=KitResponse, status_code=status.HTTP_201_CREATED)
async def build_kit_from_prompt(
    request: Request,
    prompt: str = Query(..., description="Natural language description of desired kit"),
    num_samples: int = Query(12, ge=1, le=16, description="Number of samples to include"),
    create_kit: bool = Query(True, description="Whether to create and save the kit"),
    db: AsyncSession = Depends(get_db),
):
    """
    AI-powered kit builder from natural language prompt.

    Examples:
    - "lo-fi hip hop beat at 85 BPM"
    - "dark trap drums with heavy 808s"
    - "boom bap style with vinyl texture"
    """
    logger.info(f"Building kit from prompt: {prompt}")

    from app.tools.kit_assembler import KitAssemblerTool

    assembler = KitAssemblerTool()

    # Build kit using AI
    try:
        result = await assembler.build_kit_from_prompt(
            db=db,
            user_id=DEFAULT_USER_ID,
            prompt=prompt,
            num_samples=num_samples,
        )
    except Exception as e:
        logger.error(f"Error building kit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build kit: {str(e)}",
        )

    # Create kit if requested
    if create_kit:
        kit_service = KitService()

        # Generate kit name from prompt
        analysis = result.get("analysis", {})
        genre = analysis.get("genre", "Custom")
        kit_name = f"{genre.title()} Kit"

        try:
            kit = await kit_service.create_kit(
                db=db,
                user_id=DEFAULT_USER_ID,
                name=kit_name,
                description=f"AI-generated kit: {prompt}",
            )

            # Assign samples to pads
            for sample_info in result.get("samples", []):
                sample_id = sample_info.get("sample_id")
                pad_number = sample_info.get("pad_number")

                if not sample_id or not pad_number:
                    continue

                try:
                    await kit_service.assign_sample_to_pad(
                        db=db,
                        kit_id=kit.id,
                        sample_id=sample_id,
                        pad_bank="A",
                        pad_number=pad_number,
                        user_id=DEFAULT_USER_ID,
                    )
                except Exception as e:
                    logger.warning(f"Failed to assign sample {sample_id} to pad {pad_number}: {e}")
                    continue

            # Refresh kit with all assignments
            kit = await kit_service.get_kit_by_id(db, kit.id, DEFAULT_USER_ID)

            return kit_to_response(kit)

        except Exception as e:
            logger.error(f"Error creating kit: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create kit: {str(e)}",
            )

    # Return result without creating kit
    return JSONResponse(content=result)
