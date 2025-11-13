"""
Unit tests for UsageTrackingService
Tests API usage tracking, cost calculation, budget monitoring, and analytics
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from app.services.usage_tracking_service import UsageTrackingService
from app.models.api_usage import ApiUsage


class TestTrackApiCall:
    """Test cases for track_api_call() method"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_creates_record(self, db_session):
        """Test that track_api_call creates ApiUsage record correctly."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act
        usage = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50
        )

        # Assert
        assert usage.id is not None
        assert usage.model == "google/gemma-3-27b-it"
        assert usage.operation == "chat"
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.request_id is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_calculates_costs_correctly(self, db_session):
        """Test that costs are calculated accurately using model pricing."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act - Use gemma model with known pricing
        usage = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1_000_000,  # 1M tokens
            output_tokens=1_000_000   # 1M tokens
        )

        # Assert
        # Gemma: input=$0.09/1M, output=$0.16/1M
        expected_input_cost = 0.09
        expected_output_cost = 0.16
        expected_total_cost = expected_input_cost + expected_output_cost

        assert abs(usage.input_cost - expected_input_cost) < 0.0001
        assert abs(usage.output_cost - expected_output_cost) < 0.0001
        assert abs(usage.total_cost - expected_total_cost) < 0.0001

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_with_optional_user_id(self, db_session):
        """Test track_api_call with optional user_id parameter."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act
        usage = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=42
        )

        # Assert
        assert usage.user_id == 42

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_with_sample_id(self, db_session):
        """Test track_api_call with optional sample_id parameter."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act
        usage = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="vibe_analysis",
            input_tokens=100,
            output_tokens=50,
            sample_id=7
        )

        # Assert
        assert usage.sample_id == 7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_with_batch_id(self, db_session):
        """Test track_api_call with optional batch_id parameter."""
        # Arrange
        service = UsageTrackingService(db_session)
        batch_uuid = "batch-123-abc-def"

        # Act
        usage = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="collector_search",
            input_tokens=100,
            output_tokens=50,
            batch_id=batch_uuid
        )

        # Assert
        assert usage.batch_id == batch_uuid

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_stores_extra_metadata(self, db_session):
        """Test that extra_metadata is stored correctly."""
        # Arrange
        service = UsageTrackingService(db_session)
        metadata = {
            "video_id": "dQw4w9WgXcQ",
            "duration_seconds": 212,
            "confidence_score": 0.92
        }

        # Act
        usage = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            extra_metadata=metadata
        )

        # Assert
        assert usage.extra_metadata == metadata
        assert usage.extra_metadata["video_id"] == "dQw4w9WgXcQ"
        assert usage.extra_metadata["confidence_score"] == 0.92

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_free_model_zero_cost(self, db_session):
        """Test that free models calculate zero cost."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act
        usage = await service.track_api_call(
            model="qwen/qwen3-235b-a22b-2507:free",
            operation="collector_search",
            input_tokens=100_000,
            output_tokens=50_000
        )

        # Assert
        assert usage.input_cost == 0.0
        assert usage.output_cost == 0.0
        assert usage.total_cost == 0.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_track_api_call_unknown_model_zero_cost(self, db_session):
        """Test that unknown models default to zero cost."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act
        usage = await service.track_api_call(
            model="unknown/model",
            operation="chat",
            input_tokens=100,
            output_tokens=50
        )

        # Assert
        assert usage.input_cost == 0.0
        assert usage.output_cost == 0.0
        assert usage.total_cost == 0.0


class TestGetUsageSummary:
    """Test cases for get_usage_summary() method"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_summary_returns_correct_totals(self, db_session):
        """Test that get_usage_summary returns correct totals."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create multiple usage records
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500
        )
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=2000,
            output_tokens=1000
        )

        # Act
        summary = await service.get_usage_summary()

        # Assert
        assert summary["total_tokens"] == 4500
        assert summary["input_tokens"] == 3000
        assert summary["output_tokens"] == 1500
        assert summary["call_count"] == 2
        assert summary["total_cost"] > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_summary_filters_by_user_id(self, db_session):
        """Test that get_usage_summary filters by user_id correctly."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create records for different users
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500,
            user_id=1
        )
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=2000,
            output_tokens=1000,
            user_id=2
        )

        # Act
        user1_summary = await service.get_usage_summary(user_id=1)
        user2_summary = await service.get_usage_summary(user_id=2)

        # Assert
        assert user1_summary["call_count"] == 1
        assert user1_summary["total_tokens"] == 1500
        assert user2_summary["call_count"] == 1
        assert user2_summary["total_tokens"] == 3000

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_summary_filters_by_date_range(self, db_session):
        """Test that get_usage_summary filters by date range correctly."""
        # Arrange
        service = UsageTrackingService(db_session)
        now = datetime.now()

        # Create usage with mocked dates
        usage1 = await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500
        )

        # Manually adjust one record's timestamp for testing
        usage1.created_at = now - timedelta(days=5)
        db_session.add(usage1)
        await db_session.commit()

        # Create current record
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=2000,
            output_tokens=1000
        )

        # Act - Get only today's usage
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_summary = await service.get_usage_summary(start_date=start_date)

        # Assert - Should only have 1 call from today
        assert today_summary["call_count"] == 1
        assert today_summary["total_tokens"] == 3000

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_summary_breakdown_by_operation(self, db_session):
        """Test that get_usage_summary provides correct breakdown by operation."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create records for different operations
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500
        )
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="vibe_analysis",
            input_tokens=2000,
            output_tokens=1000
        )

        # Act
        summary = await service.get_usage_summary()

        # Assert
        assert "by_operation" in summary
        assert "chat" in summary["by_operation"]
        assert "vibe_analysis" in summary["by_operation"]
        assert summary["by_operation"]["chat"]["count"] == 1
        assert summary["by_operation"]["vibe_analysis"]["count"] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_summary_breakdown_by_model(self, db_session):
        """Test that get_usage_summary provides correct breakdown by model."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create records for different models
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500
        )
        await service.track_api_call(
            model="qwen/qwen3-235b-a22b-2507",
            operation="chat",
            input_tokens=2000,
            output_tokens=1000
        )

        # Act
        summary = await service.get_usage_summary()

        # Assert
        assert "by_model" in summary
        assert "google/gemma-3-27b-it" in summary["by_model"]
        assert "qwen/qwen3-235b-a22b-2507" in summary["by_model"]
        assert summary["by_model"]["google/gemma-3-27b-it"]["count"] == 1
        assert summary["by_model"]["qwen/qwen3-235b-a22b-2507"]["count"] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_summary_empty_results(self, db_session):
        """Test get_usage_summary handles empty results correctly."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act - No records created
        summary = await service.get_usage_summary()

        # Assert
        assert summary["total_cost"] == 0
        assert summary["total_tokens"] == 0
        assert summary["call_count"] == 0
        assert summary["by_operation"] == {}
        assert summary["by_model"] == {}


class TestGetDailyTotals:
    """Test cases for get_daily_totals() method"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_daily_totals_returns_daily_data(self, db_session):
        """Test that get_daily_totals returns data for specified number of days."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create records for today
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500
        )

        # Act
        daily_totals = await service.get_daily_totals(days=30)

        # Assert
        assert isinstance(daily_totals, list)
        assert len(daily_totals) >= 1
        assert "date" in daily_totals[0]
        assert "cost" in daily_totals[0]
        assert "tokens" in daily_totals[0]
        assert "call_count" in daily_totals[0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_daily_totals_groups_by_date(self, db_session):
        """Test that get_daily_totals groups by date correctly."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create multiple records for today
        for _ in range(3):
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=1000,
                output_tokens=500
            )

        # Act
        daily_totals = await service.get_daily_totals(days=1)

        # Assert
        # All records should be grouped into today's entry
        assert len(daily_totals) == 1
        assert daily_totals[0]["call_count"] == 3
        assert daily_totals[0]["tokens"] == 4500

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_daily_totals_filters_by_user_id(self, db_session):
        """Test that get_daily_totals filters by user_id correctly."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create records for different users
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=1000,
            output_tokens=500,
            user_id=1
        )
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=2000,
            output_tokens=1000,
            user_id=2
        )

        # Act
        user1_totals = await service.get_daily_totals(user_id=1)
        user2_totals = await service.get_daily_totals(user_id=2)

        # Assert
        assert user1_totals[0]["call_count"] == 1
        assert user1_totals[0]["tokens"] == 1500
        assert user2_totals[0]["call_count"] == 1
        assert user2_totals[0]["tokens"] == 3000


class TestCheckBudgetLimits:
    """Test cases for check_budget_limits() method"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_budget_limits_ok_status(self, db_session):
        """Test that check_budget_limits returns ok status when under budget."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create small usage record
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50
        )

        # Act
        result = await service.check_budget_limits()

        # Assert
        assert result["status"] == "ok"
        assert result["warnings"] == []
        assert result["monthly"]["percentage"] < 0.8

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_budget_limits_warning_status(self, db_session):
        """Test that check_budget_limits returns warning at alert threshold (80%)."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create expensive usage close to budget limit
        # Using gemma model: input=$0.18/2M, output=$0.32/2M = $0.50 per 4M tokens
        # With $5 budget, need $4 to reach 80%
        # 8 calls * $0.50 = $4.00 (80% of $5)
        with patch.object(service.settings, 'monthly_budget_usd', 5.0), \
             patch.object(service.settings, 'daily_token_limit', 50_000_000):  # High limit to avoid daily token exceeded
            # Create 8 calls of 4M tokens each = $4.00 (32M tokens total, under 50M limit)
            for _ in range(8):
                await service.track_api_call(
                    model="google/gemma-3-27b-it",
                    operation="chat",
                    input_tokens=2_000_000,
                    output_tokens=2_000_000,
                    user_id=1
                )

            # Act
            result = await service.check_budget_limits(user_id=1)

            # Assert
            assert result["status"] == "warning"
            assert len(result["warnings"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_budget_limits_exceeded_status(self, db_session):
        """Test that check_budget_limits returns exceeded when over budget."""
        # Arrange
        service = UsageTrackingService(db_session)

        with patch.object(service.settings, 'monthly_budget_usd', 5.0):
            # Create expensive usage exceeding budget
            for _ in range(20):
                await service.track_api_call(
                    model="qwen/qwen3-235b-a22b-2507",
                    operation="collector_search",
                    input_tokens=1_000_000,
                    output_tokens=1_000_000
                )

            # Act
            result = await service.check_budget_limits()

            # Assert
            assert result["status"] == "exceeded"
            assert len(result["warnings"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_budget_limits_daily_token_limit(self, db_session):
        """Test that check_budget_limits checks daily token limit."""
        # Arrange
        service = UsageTrackingService(db_session)

        with patch.object(service.settings, 'daily_token_limit', 1000):
            # Create usage exceeding daily token limit
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=600,
                output_tokens=500
            )

            # Act
            result = await service.check_budget_limits()

            # Assert
            assert result["daily"]["percentage"] > 1.0
            assert result["status"] == "exceeded"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_budget_limits_returns_warnings_array(self, db_session):
        """Test that check_budget_limits returns correct warnings array."""
        # Arrange
        service = UsageTrackingService(db_session)

        with patch.object(service.settings, 'monthly_budget_usd', 5.0):
            for _ in range(20):
                await service.track_api_call(
                    model="qwen/qwen3-235b-a22b-2507",
                    operation="collector_search",
                    input_tokens=1_000_000,
                    output_tokens=1_000_000
                )

            # Act
            result = await service.check_budget_limits()

            # Assert
            assert isinstance(result["warnings"], list)
            assert len(result["warnings"]) > 0
            assert any("Monthly budget" in w for w in result["warnings"])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_budget_limits_with_user_id(self, db_session):
        """Test that check_budget_limits respects user_id filter."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create expensive usage for user 2
        for _ in range(20):
            await service.track_api_call(
                model="qwen/qwen3-235b-a22b-2507",
                operation="collector_search",
                input_tokens=1_000_000,
                output_tokens=1_000_000,
                user_id=2
            )

        # Act - Check budget for user 1 (no usage)
        user1_result = await service.check_budget_limits(user_id=1)

        # Assert
        assert user1_result["status"] == "ok"
        assert user1_result["monthly"]["used"] == 0


class TestGetRecentCalls:
    """Test cases for get_recent_calls() method"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_recent_calls_returns_correct_limit(self, db_session):
        """Test that get_recent_calls respects limit parameter."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create 10 records
        for _ in range(10):
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=100,
                output_tokens=50
            )

        # Act
        recent = await service.get_recent_calls(limit=5)

        # Assert
        assert len(recent) == 5

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_recent_calls_orders_by_created_at_desc(self, db_session):
        """Test that get_recent_calls orders by created_at descending."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create 3 records
        usage_list = []
        for i in range(3):
            usage = await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=100 * (i + 1),
                output_tokens=50 * (i + 1)
            )
            usage_list.append(usage)

        # Act
        recent = await service.get_recent_calls(limit=10)

        # Assert
        assert len(recent) == 3
        # Most recent should be first
        assert recent[0].id == usage_list[-1].id
        assert recent[1].id == usage_list[-2].id
        assert recent[2].id == usage_list[-3].id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_recent_calls_filters_by_user_id(self, db_session):
        """Test that get_recent_calls filters by user_id correctly."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Create records for different users
        for _ in range(3):
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=100,
                output_tokens=50,
                user_id=1
            )

        for _ in range(2):
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=100,
                output_tokens=50,
                user_id=2
            )

        # Act
        user1_calls = await service.get_recent_calls(user_id=1, limit=10)
        user2_calls = await service.get_recent_calls(user_id=2, limit=10)

        # Assert
        assert len(user1_calls) == 3
        assert len(user2_calls) == 2
        assert all(call.user_id == 1 for call in user1_calls)
        assert all(call.user_id == 2 for call in user2_calls)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_recent_calls_empty_result(self, db_session):
        """Test that get_recent_calls returns empty list when no records."""
        # Arrange
        service = UsageTrackingService(db_session)

        # Act - No records created
        recent = await service.get_recent_calls(limit=10)

        # Assert
        assert recent == []
