"""
Pytest fixtures for service layer tests.
"""
import pytest
import pytest_asyncio
import os

from app.services.usage_tracking_service import UsageTrackingService


@pytest_asyncio.fixture
async def usage_tracking_service(db_session):
    """
    Provide UsageTrackingService instance for testing.

    Uses the real database session from the parent conftest.py
    to enable integration testing with actual database operations.
    """
    return UsageTrackingService(db_session)


@pytest_asyncio.fixture
async def openrouter_service(usage_tracking_service):
    """
    Provide OpenRouterService instance for testing.

    This fixture will fail until the OpenRouterService is implemented.
    Uses real UsageTrackingService for integration testing.

    Requires OPENROUTER_API_KEY environment variable to be set.
    """
    from app.services.openrouter_service import OpenRouterService
    return OpenRouterService(usage_tracking_service)


@pytest.fixture
def openrouter_api_key():
    """
    Provide OpenRouter API key from environment.

    Tests requiring real API access should skip if this is not set.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY not set in environment")
    return api_key
