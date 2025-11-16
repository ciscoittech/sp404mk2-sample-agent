"""
Preferences API endpoints.
Provides user preference management with dual JSON/HTMX response support.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Header, Request, Form, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import os

from app.api.deps import get_db
from app.services.preferences_service import PreferencesService
from app.schemas.preferences import UserPreferenceResponse, UserPreferenceUpdate

router = APIRouter()

# Initialize templates locally to avoid circular import with app.main
# Templates are in backend/templates
# From: backend/app/api/v1/endpoints/preferences.py
# Need: backend/templates
# That's 5 levels up from __file__
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
local_templates = os.path.join(backend_dir, "templates")
docker_templates = "/app/backend/templates"

# Use local path if it exists, otherwise fall back to Docker path
if os.path.exists(local_templates):
    templates_dir = local_templates
elif os.path.exists(docker_templates):
    templates_dir = docker_templates
else:
    # Fallback: try to find templates relative to this file
    templates_dir = os.path.join(backend_dir, "templates")

templates = Jinja2Templates(directory=templates_dir)


@router.get("")
async def get_preferences(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user preferences.

    Returns JSON when no HX-Request header is present.
    Returns HTML form when HX-Request header is present (for HTMX).
    Auto-creates default preferences if none exist.
    """
    service = PreferencesService(db)
    preferences = await service.get_preferences()

    # Return HTML for HTMX requests
    if hx_request:
        # Get available models for form dropdown
        models_response = await PreferencesService.get_available_models()

        return templates.TemplateResponse("preferences/preferences-form.html", {
            "request": request,
            "preferences": preferences,
            "models": models_response.models
        })

    # Return JSON for API requests
    return preferences


@router.patch("")
async def update_preferences(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user preferences (partial updates allowed).

    Accepts JSON body OR form-encoded data.
    Returns JSON when no HX-Request header is present.
    Returns HTML success message when HX-Request header is present (for HTMX).
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

    # Return HTML for HTMX requests
    if hx_request:
        return templates.TemplateResponse("preferences/preferences-success.html", {
            "request": request,
            "preferences": updated_preferences
        })

    # Return JSON for API requests
    return updated_preferences


@router.get("/models")
async def get_available_models(db: AsyncSession = Depends(get_db)):
    """
    Get available AI models with pricing.

    Returns JSON only (no HTMX variant).
    Provides model metadata for UI dropdowns and cost estimation.
    """
    return await PreferencesService.get_available_models()
