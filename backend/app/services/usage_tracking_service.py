"""
OpenRouter API Usage Tracking Service
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql import and_

from app.models.api_usage import ApiUsage
from app.core.config import settings


class UsageTrackingService:
    """Service for tracking OpenRouter API usage and costs"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = settings

    async def track_api_call(
        self,
        model: str,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        user_id: Optional[int] = None,
        sample_id: Optional[int] = None,
        batch_id: Optional[str] = None,
        extra_metadata: Optional[Dict] = None
    ) -> ApiUsage:
        """
        Track a single API call with token usage and calculated costs.

        Args:
            model: Model name (e.g., "google/gemma-3-27b-it")
            operation: Operation type ("chat", "collector_search", "collector_discover", "vibe_analysis")
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens
            user_id: Optional user ID for tracking
            sample_id: Optional sample ID if related to sample processing
            batch_id: Optional batch ID if part of batch operation
            extra_metadata: Additional metadata to store

        Returns:
            ApiUsage: The created usage record
        """
        # Calculate costs
        pricing = self.settings.model_pricing.get(model, {"input": 0.0, "output": 0.0})
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        total_cost = input_cost + output_cost
        total_tokens = input_tokens + output_tokens

        # Create usage record
        usage = ApiUsage(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            model=model,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            sample_id=sample_id,
            batch_id=batch_id,
            extra_metadata=extra_metadata or {}
        )

        self.db.add(usage)
        await self.db.commit()
        await self.db.refresh(usage)

        return usage

    async def get_usage_summary(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get summary of API usage for a time period.

        Returns:
            Dict with total_cost, total_tokens, call_count, breakdown by operation/model
        """
        # Build query conditions
        conditions = []
        if user_id:
            conditions.append(ApiUsage.user_id == user_id)
        if start_date:
            conditions.append(ApiUsage.created_at >= start_date)
        if end_date:
            conditions.append(ApiUsage.created_at <= end_date)

        where_clause = and_(*conditions) if conditions else True

        # Get totals
        result = await self.db.execute(
            select(
                func.sum(ApiUsage.total_cost).label("total_cost"),
                func.sum(ApiUsage.total_tokens).label("total_tokens"),
                func.sum(ApiUsage.input_tokens).label("input_tokens"),
                func.sum(ApiUsage.output_tokens).label("output_tokens"),
                func.count(ApiUsage.id).label("call_count")
            ).where(where_clause)
        )
        totals = result.first()

        # Get breakdown by operation
        operation_result = await self.db.execute(
            select(
                ApiUsage.operation,
                func.sum(ApiUsage.total_cost).label("cost"),
                func.count(ApiUsage.id).label("count")
            ).where(where_clause).group_by(ApiUsage.operation)
        )
        by_operation = {
            row.operation: {"cost": float(row.cost or 0), "count": row.count}
            for row in operation_result
        }

        # Get breakdown by model
        model_result = await self.db.execute(
            select(
                ApiUsage.model,
                func.sum(ApiUsage.total_cost).label("cost"),
                func.sum(ApiUsage.total_tokens).label("tokens"),
                func.count(ApiUsage.id).label("count")
            ).where(where_clause).group_by(ApiUsage.model)
        )
        by_model = {
            row.model: {
                "cost": float(row.cost or 0),
                "tokens": row.tokens or 0,
                "count": row.count
            }
            for row in model_result
        }

        return {
            "total_cost": float(totals.total_cost or 0),
            "total_tokens": totals.total_tokens or 0,
            "input_tokens": totals.input_tokens or 0,
            "output_tokens": totals.output_tokens or 0,
            "call_count": totals.call_count or 0,
            "by_operation": by_operation,
            "by_model": by_model
        }

    async def get_daily_totals(
        self,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> List[Dict]:
        """
        Get daily cost totals for the last N days.

        Returns:
            List of {date, cost, tokens, call_count} dictionaries
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        conditions = [ApiUsage.created_at >= start_date]
        if user_id:
            conditions.append(ApiUsage.user_id == user_id)

        result = await self.db.execute(
            select(
                func.date(ApiUsage.created_at).label("date"),
                func.sum(ApiUsage.total_cost).label("cost"),
                func.sum(ApiUsage.total_tokens).label("tokens"),
                func.count(ApiUsage.id).label("count")
            )
            .where(and_(*conditions))
            .group_by(func.date(ApiUsage.created_at))
            .order_by(func.date(ApiUsage.created_at))
        )

        return [
            {
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "cost": float(row.cost or 0),
                "tokens": row.tokens or 0,
                "call_count": row.count or 0
            }
            for row in result
        ]

    async def check_budget_limits(
        self,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        Check if user is approaching or exceeding budget limits.

        Returns:
            Dict with budget status, warnings, and usage percentages
        """
        # Get current month usage
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)

        monthly_summary = await self.get_usage_summary(
            user_id=user_id,
            start_date=month_start
        )

        # Get today's usage
        today_start = datetime(now.year, now.month, now.day)
        daily_summary = await self.get_usage_summary(
            user_id=user_id,
            start_date=today_start
        )

        # Calculate percentages
        monthly_budget = self.settings.monthly_budget_usd
        daily_token_limit = self.settings.daily_token_limit
        alert_threshold = self.settings.budget_alert_threshold

        monthly_used_pct = (monthly_summary["total_cost"] / monthly_budget) if monthly_budget > 0 else 0
        daily_tokens_pct = (daily_summary["total_tokens"] / daily_token_limit) if daily_token_limit > 0 else 0

        # Determine status
        status = "ok"
        warnings = []

        if monthly_used_pct >= 1.0:
            status = "exceeded"
            warnings.append(f"Monthly budget exceeded: ${monthly_summary['total_cost']:.2f} / ${monthly_budget:.2f}")
        elif monthly_used_pct >= alert_threshold:
            status = "warning"
            warnings.append(f"Approaching monthly budget limit: {monthly_used_pct*100:.1f}% used")

        if daily_tokens_pct >= 1.0:
            status = "exceeded"
            warnings.append(f"Daily token limit exceeded: {daily_summary['total_tokens']:,} / {daily_token_limit:,}")
        elif daily_tokens_pct >= alert_threshold:
            if status == "ok":
                status = "warning"
            warnings.append(f"Approaching daily token limit: {daily_tokens_pct*100:.1f}% used")

        return {
            "status": status,
            "warnings": warnings,
            "monthly": {
                "used": monthly_summary["total_cost"],
                "limit": monthly_budget,
                "percentage": monthly_used_pct,
                "remaining": max(0, monthly_budget - monthly_summary["total_cost"])
            },
            "daily": {
                "tokens_used": daily_summary["total_tokens"],
                "tokens_limit": daily_token_limit,
                "percentage": daily_tokens_pct,
                "tokens_remaining": max(0, daily_token_limit - daily_summary["total_tokens"])
            }
        }

    async def get_recent_calls(
        self,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[ApiUsage]:
        """Get recent API calls."""
        conditions = []
        if user_id:
            conditions.append(ApiUsage.user_id == user_id)

        where_clause = and_(*conditions) if conditions else True

        result = await self.db.execute(
            select(ApiUsage)
            .where(where_clause)
            .order_by(ApiUsage.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()
