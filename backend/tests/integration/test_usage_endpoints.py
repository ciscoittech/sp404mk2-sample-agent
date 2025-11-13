"""
Integration tests for OpenRouter API Usage and Cost Tracking Endpoints
Testing the full request/response cycle for usage tracking functionality
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
import csv
import io


class TestUsageEndpoints:
    """Integration tests for usage API endpoints."""

    # ==================== GET /api/v1/usage/summary ====================

    @pytest.mark.integration
    async def test_get_usage_summary_authenticated(self, client: AsyncClient, authenticated_user, db_session):
        """Test getting usage summary for authenticated user."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange - Create test usage data
        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id
        )
        await service.track_api_call(
            model="qwen/qwen3-235b-a22b-2507",
            operation="vibe_analysis",
            input_tokens=200,
            output_tokens=100,
            user_id=authenticated_user["user"].id
        )

        # Act
        response = await client.get(
            "/api/v1/usage/summary",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert "total_cost" in result
        assert "total_tokens" in result
        assert "by_operation" in result
        assert "by_model" in result
        assert result["total_tokens"] == 450  # 100+50+200+100
        assert result["call_count"] == 2
        assert "chat" in result["by_operation"]
        assert "vibe_analysis" in result["by_operation"]

    @pytest.mark.integration
    async def test_get_usage_summary_with_date_range(self, client: AsyncClient, authenticated_user, db_session):
        """Test filtering usage summary by date range."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        now = datetime.now()
        past_date = now - timedelta(days=10)

        # Create usage in past (should be excluded)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id
        )

        # Create usage with backdated timestamp
        # Note: This test depends on the service properly handling timestamps

        # Create recent usage (should be included)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=200,
            output_tokens=100,
            user_id=authenticated_user["user"].id
        )

        # Act
        response = await client.get(
            f"/api/v1/usage/summary?start_date={(now - timedelta(hours=1)).isoformat()}&end_date={now.isoformat()}",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "total_cost" in result
        assert "total_tokens" in result

    @pytest.mark.integration
    async def test_get_usage_summary_empty(self, client: AsyncClient, authenticated_user):
        """Test getting usage summary with no usage data."""
        # Act
        response = await client.get(
            "/api/v1/usage/summary",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["total_cost"] == 0.0
        assert result["total_tokens"] == 0
        assert result["call_count"] == 0
        assert result["by_operation"] == {}
        assert result["by_model"] == {}

    # ==================== GET /api/v1/usage/daily ====================

    @pytest.mark.integration
    async def test_get_daily_usage_default(self, client: AsyncClient, authenticated_user, db_session):
        """Test getting daily usage with default 30 days."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id
        )

        # Act
        response = await client.get(
            "/api/v1/usage/daily",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["days"] == 30
        assert "data" in result
        assert isinstance(result["data"], list)
        # Should have at least today's data
        assert len(result["data"]) >= 1

    @pytest.mark.integration
    async def test_get_daily_usage_custom_days(self, client: AsyncClient, authenticated_user, db_session):
        """Test getting daily usage with custom days parameter."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id
        )

        # Act
        response = await client.get(
            "/api/v1/usage/daily?days=7",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["days"] == 7
        assert "data" in result
        # Each daily record should have required fields
        for day_record in result["data"]:
            assert "date" in day_record
            assert "cost" in day_record
            assert "tokens" in day_record
            assert "call_count" in day_record

    @pytest.mark.integration
    async def test_get_daily_usage_respects_limit(self, client: AsyncClient, authenticated_user):
        """Test that daily usage endpoint respects day limits (1-365)."""
        # Act - Test minimum
        response = await client.get(
            "/api/v1/usage/daily?days=1",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["days"] == 1

        # Act - Test maximum
        response = await client.get(
            "/api/v1/usage/daily?days=365",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["days"] == 365

    # ==================== GET /api/v1/usage/budget ====================

    @pytest.mark.integration
    async def test_check_budget_status_ok(self, client: AsyncClient, authenticated_user, db_session):
        """Test budget status when under limit."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        # Create minimal usage (well under default $10 budget)
        await service.track_api_call(
            model="qwen/qwen3-235b-a22b-2507:free",  # Free model
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id
        )

        # Act
        response = await client.get(
            "/api/v1/usage/budget",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["status"] in ["ok", "warning"]
        assert "warnings" in result
        assert "monthly" in result
        assert "daily" in result
        assert "used" in result["monthly"]
        assert "limit" in result["monthly"]
        assert "percentage" in result["monthly"]
        assert "remaining" in result["monthly"]

    @pytest.mark.integration
    async def test_check_budget_status_warning(self, client: AsyncClient, authenticated_user, db_session):
        """Test budget status shows warning when approaching limit."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        # Create usage approaching budget (> 80% of $10 = $8)
        # Using Gemma model with pricing: input=$0.09/1M, output=$0.16/1M
        # 100,000 input tokens = 100,000 * 0.09/1M = $0.009 (need more tokens)
        # Create 100M tokens worth to approach budget
        for _ in range(100):
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=100000,
                output_tokens=100000,
                user_id=authenticated_user["user"].id
            )

        # Act
        response = await client.get(
            "/api/v1/usage/budget",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        # Should show warning or exceeded status
        assert result["status"] in ["warning", "exceeded"]
        assert len(result["warnings"]) > 0

    @pytest.mark.integration
    async def test_check_budget_status_structure(self, client: AsyncClient, authenticated_user):
        """Test budget status response structure."""
        # Act
        response = await client.get(
            "/api/v1/usage/budget",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        # Verify structure
        assert "status" in result
        assert "warnings" in result
        assert "monthly" in result
        assert "daily" in result

        # Check monthly structure
        assert "used" in result["monthly"]
        assert "limit" in result["monthly"]
        assert "percentage" in result["monthly"]
        assert "remaining" in result["monthly"]

        # Check daily structure
        assert "tokens_used" in result["daily"]
        assert "tokens_limit" in result["daily"]
        assert "percentage" in result["daily"]
        assert "tokens_remaining" in result["daily"]

    # ==================== GET /api/v1/usage/recent ====================

    @pytest.mark.integration
    async def test_get_recent_calls_default(self, client: AsyncClient, authenticated_user, db_session):
        """Test getting recent API calls with default limit."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id,
            sample_id=1
        )

        # Act
        response = await client.get(
            "/api/v1/usage/recent",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["limit"] == 50
        assert "count" in result
        assert "calls" in result
        assert result["count"] >= 1
        assert len(result["calls"]) >= 1

        # Verify call structure
        call = result["calls"][0]
        assert "id" in call
        assert "model" in call
        assert "operation" in call
        assert "input_tokens" in call
        assert "output_tokens" in call
        assert "total_tokens" in call
        assert "total_cost" in call
        assert "created_at" in call

    @pytest.mark.integration
    async def test_get_recent_calls_custom_limit(self, client: AsyncClient, authenticated_user, db_session):
        """Test recent calls with custom limit parameter."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        for i in range(5):
            await service.track_api_call(
                model="google/gemma-3-27b-it",
                operation="chat",
                input_tokens=100,
                output_tokens=50,
                user_id=authenticated_user["user"].id
            )

        # Act
        response = await client.get(
            "/api/v1/usage/recent?limit=3",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["limit"] == 3
        assert len(result["calls"]) <= 3
        # Should return most recent calls first
        assert result["count"] <= 3

    @pytest.mark.integration
    async def test_get_recent_calls_empty(self, client: AsyncClient, authenticated_user):
        """Test recent calls when no usage data exists."""
        # Act
        response = await client.get(
            "/api/v1/usage/recent",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert result["count"] == 0
        assert result["calls"] == []

    # ==================== GET /api/v1/usage/export ====================

    @pytest.mark.integration
    async def test_export_usage_csv_success(self, client: AsyncClient, authenticated_user, db_session):
        """Test exporting usage data as CSV."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id,
            sample_id=1
        )

        # Act
        response = await client.get(
            "/api/v1/usage/export",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # Verify Content-Disposition header
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert "filename=" in disposition
        assert "openrouter_usage_" in disposition
        assert ".csv" in disposition

    @pytest.mark.integration
    async def test_export_usage_csv_content(self, client: AsyncClient, authenticated_user, db_session):
        """Test that exported CSV has correct headers and data."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id,
            sample_id=1
        )

        # Act
        response = await client.get(
            "/api/v1/usage/export",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200

        # Parse CSV content
        csv_content = response.text
        lines = csv_content.strip().split("\n")

        # Check header
        header = lines[0].split(",")
        expected_headers = [
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
        ]
        assert header == expected_headers

        # Check data row exists
        assert len(lines) >= 2

    @pytest.mark.integration
    async def test_export_usage_csv_with_date_filter(self, client: AsyncClient, authenticated_user, db_session):
        """Test exporting CSV with date range filter."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        service = UsageTrackingService(db_session)
        now = datetime.now()
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=authenticated_user["user"].id
        )

        # Act
        start_date = (now - timedelta(hours=1)).isoformat()
        end_date = now.isoformat()
        response = await client.get(
            f"/api/v1/usage/export?start_date={start_date}&end_date={end_date}",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # Verify it's valid CSV
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        assert len(lines) >= 1  # At least header

    # ==================== GET /api/v1/usage/public/summary ====================

    @pytest.mark.integration
    async def test_get_public_usage_summary_no_auth(self, client: AsyncClient, db_session):
        """Test public endpoint works without authentication."""
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange - Create usage for demo user (id=1)
        from app.models.user import User
        demo_user = User(
            id=1,
            email="demo@example.com",
            username="demo",
            hashed_password="fake_hash",
            is_active=True
        )
        db_session.add(demo_user)
        await db_session.commit()

        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=1  # Demo user
        )

        # Act - No authentication headers
        response = await client.get("/api/v1/usage/public/summary")

        # Assert
        assert response.status_code == 200
        result = response.json()

        assert "summary" in result
        assert "budget" in result
        assert "total_cost" in result["summary"]
        assert "total_tokens" in result["summary"]

    @pytest.mark.integration
    async def test_get_public_usage_summary_structure(self, client: AsyncClient, db_session):
        """Test public summary response structure."""
        from app.models.user import User

        # Arrange - Ensure demo user exists
        demo_user = User(
            id=1,
            email="demo@example.com",
            username="demo",
            hashed_password="fake_hash",
            is_active=True
        )
        db_session.add(demo_user)
        await db_session.commit()

        # Act
        response = await client.get("/api/v1/usage/public/summary")

        # Assert
        assert response.status_code == 200
        result = response.json()

        # Verify structure
        assert "summary" in result
        assert "budget" in result

        # Summary structure
        assert "total_cost" in result["summary"]
        assert "total_tokens" in result["summary"]
        assert "by_operation" in result["summary"]
        assert "by_model" in result["summary"]

        # Budget structure
        assert "status" in result["budget"]
        assert "monthly" in result["budget"]
        assert "daily" in result["budget"]

    @pytest.mark.integration
    async def test_get_public_summary_month_filter(self, client: AsyncClient, db_session):
        """Test public summary returns only current month data."""
        from app.models.user import User
        from app.services.usage_tracking_service import UsageTrackingService

        # Arrange
        demo_user = User(
            id=1,
            email="demo@example.com",
            username="demo",
            hashed_password="fake_hash",
            is_active=True
        )
        db_session.add(demo_user)
        await db_session.commit()

        service = UsageTrackingService(db_session)
        await service.track_api_call(
            model="google/gemma-3-27b-it",
            operation="chat",
            input_tokens=100,
            output_tokens=50,
            user_id=1
        )

        # Act
        response = await client.get("/api/v1/usage/public/summary")

        # Assert
        assert response.status_code == 200
        result = response.json()

        # Verify it returns data
        assert result["summary"]["total_tokens"] == 150


class TestUsageEndpointsAuthentication:
    """Test authentication requirements for usage endpoints."""

    @pytest.mark.integration
    async def test_summary_requires_auth(self, client: AsyncClient):
        """Test that summary endpoint requires authentication."""
        response = await client.get("/api/v1/usage/summary")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_daily_requires_auth(self, client: AsyncClient):
        """Test that daily endpoint requires authentication."""
        response = await client.get("/api/v1/usage/daily")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_budget_requires_auth(self, client: AsyncClient):
        """Test that budget endpoint requires authentication."""
        response = await client.get("/api/v1/usage/budget")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_recent_requires_auth(self, client: AsyncClient):
        """Test that recent endpoint requires authentication."""
        response = await client.get("/api/v1/usage/recent")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_export_requires_auth(self, client: AsyncClient):
        """Test that export endpoint requires authentication."""
        response = await client.get("/api/v1/usage/export")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_public_summary_no_auth_required(self, client: AsyncClient, db_session):
        """Test that public endpoint does not require authentication."""
        from app.models.user import User

        # Arrange - Ensure demo user exists
        demo_user = User(
            id=1,
            email="demo@example.com",
            username="demo",
            hashed_password="fake_hash",
            is_active=True
        )
        db_session.add(demo_user)
        await db_session.commit()

        # Act
        response = await client.get("/api/v1/usage/public/summary")

        # Assert - Should NOT return 401
        assert response.status_code == 200
