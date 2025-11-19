"""
Preferences API endpoints.
Provides user preference management.
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.api.deps import get_db
from app.services.preferences_service import PreferencesService
from app.schemas.preferences import UserPreferenceResponse, UserPreferenceUpdate

router = APIRouter()


@router.get("")
async def get_preferences(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user preferences.
    Auto-creates default preferences if none exist.
    """
    service = PreferencesService(db)
    preferences = await service.get_preferences()
    return preferences


@router.patch("")
async def update_preferences(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Update user preferences (partial updates allowed).
    Accepts JSON body OR form-encoded data.
    """
    service = PreferencesService(db)

    # Handle both JSON and form-encoded requests
    content_type = request.headers.get("content-type", "")

    try:
        if "application/json" in content_type:
            # JSON request - let FastAPI/Pydantic handle validation
            body = await request.json()
            update_data = UserPreferenceUpdate(**body)
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            # Form-encoded request - parse form data
            form_data = await request.form()

            # Convert form data to dict, handling boolean strings
            update_dict = {}
            if "vibe_analysis_model" in form_data:
                update_dict["vibe_analysis_model"] = form_data["vibe_analysis_model"]
            if "auto_vibe_analysis" in form_data:
                update_dict["auto_vibe_analysis"] = form_data["auto_vibe_analysis"].lower() == "true"
            if "auto_audio_features" in form_data:
                update_dict["auto_audio_features"] = form_data["auto_audio_features"].lower() == "true"
            if "batch_processing_model" in form_data:
                update_dict["batch_processing_model"] = form_data["batch_processing_model"]
            if "batch_auto_analyze" in form_data:
                update_dict["batch_auto_analyze"] = form_data["batch_auto_analyze"].lower() == "true"
            if "max_cost_per_request" in form_data:
                val = form_data["max_cost_per_request"]
                update_dict["max_cost_per_request"] = float(val) if val else None

            update_data = UserPreferenceUpdate(**update_dict)
        else:
            # No content - return current preferences unchanged
            update_data = UserPreferenceUpdate()
    except ValidationError as e:
        # Convert Pydantic ValidationError to FastAPI RequestValidationError
        # This ensures proper 422 response with error details
        raise RequestValidationError(errors=e.errors())

    # Update preferences
    updated_preferences = await service.update_preferences(update_data)
    return updated_preferences


@router.get("/models")
async def get_available_models(db: AsyncSession = Depends(get_db)):
    """
    Get available AI models with pricing.

    Returns JSON only (no HTMX variant).
    Provides model metadata for UI dropdowns and cost estimation.
    """
    return await PreferencesService.get_available_models()
