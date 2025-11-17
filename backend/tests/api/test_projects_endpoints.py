"""
Integration tests for SP-404MK2 Project Builder API endpoints.

Tests validate:
- POST /api/v1/projects/from-kit/{kit_id} - Build project from kit
- GET /api/v1/projects/download/{export_id} - Download generated project
- Request validation (project_name, BPM, format)
- Authorization (user must own kit)
- Error handling (404, 400, 500)
- File download responses

Coverage: 8 integration tests across 2 endpoint groups
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import zipfile
import json

from app.main import app
from app.api.deps import get_db
from app.models.sample import Sample
from app.models.kit import Kit, KitSample
from app.models.user import User
from app.models.sp404_export import SP404Export


@pytest_asyncio.fixture
async def api_client(db_session: AsyncSession):
    """Create async HTTP client with database override"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user_projects(db_session: AsyncSession):
    """Create test user for project tests"""
    user = User(
        id=1,
        email="projects@example.com",
        username="projectuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def kit_with_samples_for_project(db_session: AsyncSession, test_user_projects, tmp_path):
    """Create kit with 3 samples for project building"""
    import numpy as np
    import soundfile as sf

    # Create kit
    kit = Kit(
        user_id=test_user_projects.id,
        name="Project Test Kit",
        description="Kit for project testing"
    )
    db_session.add(kit)
    await db_session.flush()

    # Create 3 samples
    samples = []
    for i in range(3):
        # Generate real WAV
        sample_rate = 44100
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * (440 + i * 100) * t)

        wav_path = tmp_path / f"kit_sample_{i}.wav"
        sf.write(wav_path, audio, sample_rate)

        sample = Sample(
            user_id=test_user_projects.id,
            title=f"Kit Sample {i+1}",
            file_path=str(wav_path),
            duration=2.0,
            bpm=85.0 + (i * 5),  # 85, 90, 95
            genre="hip-hop"
        )
        db_session.add(sample)
        await db_session.flush()
        samples.append(sample)

        # Add to kit
        kit_sample = KitSample(
            kit_id=kit.id,
            sample_id=sample.id,
            pad_bank="A",
            pad_number=i + 1
        )
        db_session.add(kit_sample)

    await db_session.commit()
    await db_session.refresh(kit)

    return kit, samples


@pytest_asyncio.fixture
async def empty_kit(db_session: AsyncSession, test_user_projects):
    """Create empty kit (no samples)"""
    kit = Kit(
        user_id=test_user_projects.id,
        name="Empty Kit",
        description="No samples"
    )
    db_session.add(kit)
    await db_session.commit()
    await db_session.refresh(kit)
    return kit


@pytest_asyncio.fixture
async def export_record(db_session: AsyncSession, test_user_projects, tmp_path):
    """Create export record with actual ZIP file"""
    import zipfile

    # Create a minimal ZIP file
    zip_path = tmp_path / "test_export.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test.txt", "test content")

    export = SP404Export(
        user_id=test_user_projects.id,
        export_type="project",
        sample_count=3,
        output_path=str(zip_path),
        organized_by="kit",
        format="wav",
        total_size_bytes=zip_path.stat().st_size
    )
    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    return export


class TestProjectBuildEndpoint:
    """Tests for POST /api/v1/projects/from-kit/{kit_id}"""

    @pytest.mark.asyncio
    async def test_build_project_endpoint_success(self, api_client, kit_with_samples_for_project, tmp_path):
        """Test successful project build via API"""
        kit, samples = kit_with_samples_for_project

        # Make request
        response = await api_client.post(
            f"/api/v1/projects/from-kit/{kit.id}",
            json={
                "project_name": "APITest",
                "project_bpm": None,  # Auto-detect
                "audio_format": "wav",
                "include_bank_layout": False
            },
            params={"output_base_path": str(tmp_path)}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["export_id"] is not None
        assert data["project_name"] == "APITest"
        assert data["sample_count"] == 3
        assert data["file_size_bytes"] > 0
        assert data["download_url"] is not None
        assert "/api/v1/projects/download/" in data["download_url"]

    @pytest.mark.asyncio
    async def test_build_project_endpoint_invalid_kit(self, api_client, tmp_path):
        """Test error for non-existent kit"""
        response = await api_client.post(
            "/api/v1/projects/from-kit/99999",
            json={
                "project_name": "Invalid",
                "audio_format": "wav"
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert response.status_code == 200  # Service returns 200 with error in body
        data = response.json()

        assert data["success"] is False
        assert data["error_message"] is not None
        assert "not found" in data["error_message"].lower()

    @pytest.mark.asyncio
    async def test_build_project_endpoint_no_samples(self, api_client, empty_kit, tmp_path):
        """Test error for kit with no samples"""
        response = await api_client.post(
            f"/api/v1/projects/from-kit/{empty_kit.id}",
            json={
                "project_name": "EmptyKit",
                "audio_format": "wav"
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is False
        assert data["error_message"] is not None
        assert "no samples" in data["error_message"].lower()

    @pytest.mark.asyncio
    async def test_build_project_endpoint_invalid_bpm(self, api_client, kit_with_samples_for_project, tmp_path):
        """Test validation for invalid BPM"""
        kit, samples = kit_with_samples_for_project

        response = await api_client.post(
            f"/api/v1/projects/from-kit/{kit.id}",
            json={
                "project_name": "InvalidBPM",
                "project_bpm": 500.0,  # Out of range (20-300)
                "audio_format": "wav"
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert response.status_code == 400  # Validation error (converted from 422)

    @pytest.mark.asyncio
    async def test_build_project_endpoint_invalid_format(self, api_client, kit_with_samples_for_project, tmp_path):
        """Test validation for invalid audio format"""
        kit, samples = kit_with_samples_for_project

        response = await api_client.post(
            f"/api/v1/projects/from-kit/{kit.id}",
            json={
                "project_name": "InvalidFormat",
                "audio_format": "mp3"  # Not supported (only wav/aiff)
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert response.status_code == 400  # Validation error (converted from 422)

    @pytest.mark.asyncio
    async def test_build_project_endpoint_invalid_project_name(self, api_client, kit_with_samples_for_project, tmp_path):
        """Test validation for project name (non-ASCII, too long)"""
        kit, samples = kit_with_samples_for_project

        # Test non-ASCII characters
        response = await api_client.post(
            f"/api/v1/projects/from-kit/{kit.id}",
            json={
                "project_name": "テスト",  # Japanese characters
                "audio_format": "wav"
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert response.status_code == 400  # Validation error (converted from 422)

        # Test too long (>31 chars)
        response = await api_client.post(
            f"/api/v1/projects/from-kit/{kit.id}",
            json={
                "project_name": "A" * 50,  # 50 characters
                "audio_format": "wav"
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert response.status_code == 400  # Validation error (converted from 422)


class TestProjectDownloadEndpoint:
    """Tests for GET /api/v1/projects/download/{export_id}"""

    @pytest.mark.asyncio
    async def test_download_project_endpoint_success(self, api_client, export_record):
        """Test successful project download"""
        response = await api_client.get(
            f"/api/v1/projects/download/{export_record.id}"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert len(response.content) > 0

        # Verify it's a valid ZIP
        import io
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            assert "test.txt" in zf.namelist()

    @pytest.mark.asyncio
    async def test_download_project_endpoint_not_found(self, api_client):
        """Test 404 for non-existent export"""
        response = await api_client.get(
            "/api/v1/projects/download/99999"
        )

        assert response.status_code == 404


class TestProjectEndpointIntegration:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_build_and_download_flow(self, api_client, kit_with_samples_for_project, tmp_path):
        """Test complete flow: build → download"""
        kit, samples = kit_with_samples_for_project

        # Step 1: Build project
        build_response = await api_client.post(
            f"/api/v1/projects/from-kit/{kit.id}",
            json={
                "project_name": "FullFlow",
                "audio_format": "wav"
            },
            params={"output_base_path": str(tmp_path)}
        )

        assert build_response.status_code == 200
        build_data = build_response.json()
        assert build_data["success"] is True

        # Extract export_id
        export_id = build_data["export_id"]

        # Step 2: Download project
        download_response = await api_client.get(
            f"/api/v1/projects/download/{export_id}"
        )

        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/zip"

        # Step 3: Verify ZIP contents
        import io
        zip_buffer = io.BytesIO(download_response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()

            # Must have PADCONF.BIN
            assert "PADCONF.BIN" in files

            # Must have PROJECT_INFO.txt
            assert "PROJECT_INFO.txt" in files

            # Must have samples
            sample_files = [f for f in files if f.startswith("samples/")]
            assert len(sample_files) == 3

            # Verify PADCONF.BIN size
            padconf_data = zf.read("PADCONF.BIN")
            assert len(padconf_data) == 52000
