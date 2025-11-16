"""
OpenRouter API Usage and Cost Tracking Endpoints
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.usage_tracking_service import UsageTrackingService


router = APIRouter()
public_router = APIRouter()


@router.get("/summary")
async def get_usage_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for usage summary"),
    end_date: Optional[datetime] = Query(None, description="End date for usage summary"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get usage summary for the current user (or all users if admin).

    Returns total costs, token counts, and breakdowns by operation and model.
    """
    service = UsageTrackingService(db)

    # Use current user's ID (or None for admin to see all)
    user_id = current_user.id if not current_user.is_superuser else None

    summary = await service.get_usage_summary(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

    return summary


@router.get("/daily")
async def get_daily_usage(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get daily usage totals for the last N days.

    Returns a list of daily usage with costs and token counts.
    """
    service = UsageTrackingService(db)

    user_id = current_user.id if not current_user.is_superuser else None

    daily_totals = await service.get_daily_totals(
        user_id=user_id,
        days=days
    )

    return {"days": days, "data": daily_totals}


@router.get("/budget")
async def check_budget_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check current budget status and limits.

    Returns budget usage percentages, warnings, and remaining budget.
    """
    service = UsageTrackingService(db)

    user_id = current_user.id if not current_user.is_superuser else None

    budget_status = await service.check_budget_limits(user_id=user_id)

    return budget_status


@router.get("/recent")
async def get_recent_calls(
    limit: int = Query(50, ge=1, le=500, description="Number of recent calls to retrieve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent API calls with details.

    Returns a list of recent API usage records.
    """
    service = UsageTrackingService(db)

    user_id = current_user.id if not current_user.is_superuser else None

    recent = await service.get_recent_calls(
        user_id=user_id,
        limit=limit
    )

    # Convert to dict for JSON serialization
    return {
        "limit": limit,
        "count": len(recent),
        "calls": [
            {
                "id": call.id,
                "model": call.model,
                "operation": call.operation,
                "input_tokens": call.input_tokens,
                "output_tokens": call.output_tokens,
                "total_tokens": call.total_tokens,
                "total_cost": call.total_cost,
                "created_at": call.created_at.isoformat(),
                "sample_id": call.sample_id,
                "batch_id": call.batch_id
            }
            for call in recent
        ]
    }


@router.get("/export")
async def export_usage_csv(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export usage data as CSV file.

    Returns a CSV file with all usage records for the specified period.
    """
    service = UsageTrackingService(db)

    user_id = current_user.id if not current_user.is_superuser else None

    # Get all recent calls (up to 10,000)
    calls = await service.get_recent_calls(user_id=user_id, limit=10000)

    # Filter by date if specified
    if start_date or end_date:
        filtered_calls = []
        for call in calls:
            if start_date and call.created_at < start_date:
                continue
            if end_date and call.created_at > end_date:
                continue
            filtered_calls.append(call)
        calls = filtered_calls

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Date",
        "Model",
        "Operation",
        "Input Tokens",
        "Output Tokens",
        "Total Tokens",
        "Input Cost (USD)",
        "Output Cost (USD)",
        "Total Cost (USD)",
        "Sample ID",
        "Batch ID"
    ])

    # Data rows
    for call in calls:
        writer.writerow([
            call.created_at.isoformat(),
            call.model,
            call.operation,
            call.input_tokens,
            call.output_tokens,
            call.total_tokens,
            f"{call.input_cost:.6f}",
            f"{call.output_cost:.6f}",
            f"{call.total_cost:.6f}",
            call.sample_id or "",
            call.batch_id or ""
        ])

    # Prepare response
    output.seek(0)

    # Generate filename with date range
    filename = f"openrouter_usage_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# Public endpoints (for demo user, no auth required)
@public_router.get("/summary")
async def get_public_usage_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get usage summary for public/demo user (user_id=1).

    Does not require authentication.
    """
    service = UsageTrackingService(db)

    # Get current month usage for demo user
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)

    summary = await service.get_usage_summary(
        user_id=1,  # Demo user
        start_date=month_start
    )

    # Also get budget status
    budget = await service.check_budget_limits(user_id=1)

    return {
        "summary": summary,
        "budget": budget
    }


@public_router.get("/budget")
async def get_public_budget_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Check current budget status and limits for public/demo user (user_id=1).

    Does not require authentication.
    """
    service = UsageTrackingService(db)
    budget_status = await service.check_budget_limits(user_id=1)
    return budget_status


@public_router.get("/daily")
async def get_public_daily_usage(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get daily usage totals for the last N days for public/demo user (user_id=1).

    Does not require authentication.
    """
    service = UsageTrackingService(db)
    daily_totals = await service.get_daily_totals(user_id=1, days=days)
    return {"days": days, "data": daily_totals}


@public_router.get("/recent")
async def get_public_recent_calls(
    limit: int = Query(50, ge=1, le=500, description="Number of recent calls to retrieve"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent API calls with details for public/demo user (user_id=1).

    Does not require authentication.
    """
    service = UsageTrackingService(db)
    recent = await service.get_recent_calls(user_id=1, limit=limit)

    # Convert to dict for JSON serialization
    return {
        "limit": limit,
        "count": len(recent),
        "calls": [
            {
                "id": call.id,
                "model": call.model,
                "operation": call.operation,
                "input_tokens": call.input_tokens,
                "output_tokens": call.output_tokens,
                "total_tokens": call.total_tokens,
                "total_cost": call.total_cost,
                "created_at": call.created_at.isoformat(),
                "sample_id": call.sample_id,
                "batch_id": call.batch_id
            }
            for call in recent
        ]
    }
