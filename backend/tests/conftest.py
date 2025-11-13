"""
Pytest configuration and fixtures for backend tests.
"""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
import factory
from faker import Faker
import tempfile
import shutil
import os

from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.models import User, Sample, Kit, ApiUsage, Batch, VibeAnalysis
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override."""
    # Override the database dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides after test
    app.dependency_overrides.clear()


# Factory fixtures for test data
class UserFactory(factory.Factory):
    """Factory for creating test users."""
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n)
    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    is_active = True


class SampleFactory(factory.Factory):
    """Factory for creating test samples."""
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    file_path = factory.LazyAttribute(lambda _: f"samples/{fake.uuid4()}.wav")
    duration_ms = factory.LazyAttribute(lambda _: fake.random_int(min=1000, max=30000))
    bpm = factory.LazyAttribute(lambda _: fake.random_int(min=60, max=180))
    genre = factory.LazyAttribute(lambda _: fake.random_element(["hip-hop", "jazz", "electronic"]))


@pytest.fixture
def user_factory():
    """Provide user factory."""
    return UserFactory


@pytest.fixture
def sample_factory():
    """Provide sample factory."""
    return SampleFactory


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user in the database."""
    auth_service = AuthService(db_session)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPassword123!"
    )
    user = await auth_service.create_user(user_data)
    return user


@pytest_asyncio.fixture
async def authenticated_user(test_user, db_session):
    """Create an authenticated user with token."""
    auth_service = AuthService(db_session)
    access_token = auth_service.create_access_token(test_user.id)
    
    return {
        "user": test_user,
        "token": access_token,
        "headers": {"Authorization": f"Bearer {access_token}"}
    }


@pytest.fixture
def sample_file():
    """Create a test audio file."""
    # Simple WAV header + minimal data
    wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    return wav_header + b'\x00' * 100  # Minimal audio data


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_upload_dir):
    """Set up test environment variables."""
    monkeypatch.setenv("UPLOAD_DIR", temp_upload_dir)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ENVIRONMENT", "test")


# Utility functions for tests
def auth_headers(user_data: dict) -> dict:
    """Generate authorization headers for a user."""
    return {"Authorization": f"Bearer {user_data.get('token', 'test-token')}"}


async def create_test_samples(db_session, count: int, user_id: int):
    """Create multiple test samples."""
    from app.models.sample import Sample
    samples = []
    for i in range(count):
        sample = Sample(
            user_id=user_id,
            title=f"Test Sample {i}",
            file_path=f"/fake/path/sample_{i}.wav",
            genre=fake.random_element(["hip-hop", "jazz", "electronic"]),
            bpm=fake.random_int(min=60, max=180)
        )
        db_session.add(sample)
        samples.append(sample)
    
    await db_session.commit()
    return samples