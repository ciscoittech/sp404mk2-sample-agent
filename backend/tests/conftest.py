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
    from httpx import ASGITransport

    # Override the database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
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


# Audio Features Service fixtures

@pytest.fixture
def audio_service():
    """
    Provide AudioFeaturesService instance for testing.

    Returns a real service instance (not mocked) for integration testing.
    """
    from app.services.audio_features_service import AudioFeaturesService
    return AudioFeaturesService()


@pytest.fixture
def test_wav_fixture(tmp_path):
    """
    Create a minimal real WAV file for testing.

    Generates a 2-second, 440Hz sine wave (A4 note) at 44.1kHz sample rate.
    This is a real audio file that can be analyzed by librosa.

    Returns:
        Path: Path to the generated WAV file
    """
    import numpy as np
    try:
        import soundfile as sf
    except ImportError:
        # Fallback to scipy if soundfile not available
        from scipy.io import wavfile

        output_path = tmp_path / "test_sample.wav"

        # Generate 2 seconds of 440Hz sine wave
        sample_rate = 44100
        duration = 2.0
        frequency = 440

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = (0.5 * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

        wavfile.write(output_path, sample_rate, audio)
        return output_path

    output_path = tmp_path / "test_sample.wav"

    # Generate 2 seconds of 440Hz sine wave
    sample_rate = 44100
    duration = 2.0
    frequency = 440

    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)

    sf.write(output_path, audio, sample_rate)
    return output_path


# ===========================
# Kit Builder Test Fixtures
# ===========================

@pytest_asyncio.fixture
async def test_kit(db_session: AsyncSession):
    """Create a test kit."""
    from app.models.kit import Kit

    kit = Kit(
        user_id=1,
        name="Test Kit",
        description="A test kit for testing",
        pad_layout={},
        bank_config={}
    )
    db_session.add(kit)
    await db_session.commit()
    await db_session.refresh(kit)
    return kit


@pytest_asyncio.fixture
async def test_sample(db_session: AsyncSession, tmp_path):
    """Create a basic test sample with real audio file."""
    from app.models.sample import Sample
    import numpy as np
    import soundfile as sf

    # Create a real WAV file for export tests
    sample_rate = 44100
    duration = 2.0
    frequency = 440
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)

    wav_path = tmp_path / "test_sample.wav"
    sf.write(wav_path, audio, sample_rate)

    sample = Sample(
        user_id=1,
        title="Test Sample",
        file_path=str(wav_path),
        duration=2.0,
        bpm=85.0,
        genre="hip-hop",
        tags=["test", "sample"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_loop_long(db_session: AsyncSession):
    """Create a long loop sample (5 seconds) for pad 1-4 recommendations."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="Long Loop",
        file_path="/test/loop_5sec.wav",
        duration=5.0,
        bpm=85.0,
        genre="lofi",
        tags=["loop", "melodic", "chill", "sample"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_kick_short(db_session: AsyncSession, tmp_path):
    """Create a short kick sample (0.5 seconds) for pad 13 recommendations."""
    from app.models.sample import Sample
    import numpy as np
    import soundfile as sf

    # Create real audio file
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * 60 * t)  # 60Hz for kick

    wav_path = tmp_path / "kick.wav"
    sf.write(wav_path, audio, sample_rate)

    sample = Sample(
        user_id=1,
        title="Kick Drum",
        file_path=str(wav_path),
        duration=0.5,
        bpm=None,
        genre="hip-hop",
        tags=["kick", "808", "punchy", "bass drum"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_snare_short(db_session: AsyncSession, tmp_path):
    """Create a short snare sample (0.4 seconds) for pad 14 recommendations."""
    from app.models.sample import Sample
    import numpy as np
    import soundfile as sf

    # Create real audio file
    sample_rate = 44100
    duration = 0.4
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * 200 * t)  # 200Hz for snare

    wav_path = tmp_path / "snare.wav"
    sf.write(wav_path, audio, sample_rate)

    sample = Sample(
        user_id=1,
        title="Snare Drum",
        file_path=str(wav_path),
        duration=0.4,
        bpm=None,
        genre="hip-hop",
        tags=["snare", "clap", "crack"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_hat_closed(db_session: AsyncSession, tmp_path):
    """Create a closed hi-hat sample (0.3 seconds) for pad 15 recommendations."""
    from app.models.sample import Sample
    import numpy as np
    import soundfile as sf

    # Create real audio file
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * 5000 * t)  # 5kHz for hi-hat

    wav_path = tmp_path / "hat_closed.wav"
    sf.write(wav_path, audio, sample_rate)

    sample = Sample(
        user_id=1,
        title="Closed Hi-Hat",
        file_path=str(wav_path),
        duration=0.3,
        bpm=None,
        genre="hip-hop",
        tags=["hihat", "closed hat", "chh", "tight"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_hat_open(db_session: AsyncSession):
    """Create an open hi-hat sample (0.8 seconds) for pad 16 recommendations."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="Open Hi-Hat",
        file_path="/test/hat_open.wav",
        duration=0.8,
        bpm=None,
        genre="hip-hop",
        tags=["hihat", "open hat", "ohh", "sizzle"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_85bpm(db_session: AsyncSession):
    """Create a sample at 85 BPM for BPM matching tests."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="85 BPM Loop",
        file_path="/test/85bpm.wav",
        duration=4.0,
        bpm=85.0,
        genre="lofi",
        tags=["loop", "chill"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_90bpm(db_session: AsyncSession):
    """Create a sample at 90 BPM for BPM matching tests (within ±10 of 85)."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="90 BPM Loop",
        file_path="/test/90bpm.wav",
        duration=4.0,
        bpm=90.0,
        genre="lofi",
        tags=["loop", "groovy"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_140bpm(db_session: AsyncSession):
    """Create a sample at 140 BPM for BPM matching tests (outside ±10 range)."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="140 BPM Loop",
        file_path="/test/140bpm.wav",
        duration=2.0,
        bpm=140.0,
        genre="trap",
        tags=["loop", "fast"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_hiphop(db_session: AsyncSession):
    """Create a hip-hop genre sample for genre matching tests."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="Hip-Hop Sample",
        file_path="/test/hiphop.wav",
        duration=3.0,
        bpm=88.0,
        genre="hip-hop",
        tags=["loop", "boom bap"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_jazz(db_session: AsyncSession):
    """Create a jazz genre sample for genre matching tests."""
    from app.models.sample import Sample

    sample = Sample(
        user_id=1,
        title="Jazz Sample",
        file_path="/test/jazz.wav",
        duration=5.0,
        bpm=110.0,
        genre="jazz",
        tags=["loop", "smooth", "vintage"]
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample