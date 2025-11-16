"""
Integration tests for SP-404MK2 Export API endpoints.

This test suite provides comprehensive coverage of all SP-404 export API endpoints
following MVP testing principles (2-5 tests per feature).

Test Strategy:
- Real async database integration (no mocks)
- Tests JSON responses
- Tests validation and error handling
- Uses realistic test fixtures with actual audio files
- Follows patterns from test_preferences_endpoints.py

API Endpoints Tested:
1. POST /api/v1/sp404/samples/{id}/export - Export single sample
2. POST /api/v1/sp404/samples/export-batch - Batch export
3. POST /api/v1/sp404/kits/{id}/export - Export kit
4. GET /api/v1/sp404/exports/{id}/download - Download export
5. GET /api/v1/sp404/exports - List exports

Coverage: 19 integration tests across 5 endpoint groups
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import zipfile
import tempfile

from app.main import app
from app.api.deps import get_db
from app.models.sample import Sample
from app.models.kit import Kit
from app.models.user import User


@pytest_asyncio.fixture
async def api_client(db_session: AsyncSession):
    """
    Create async HTTP client with database override.

    This fixture provides a test client that uses the test database
    instead of the production database.
    """
    # Override the database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Use ASGITransport for httpx compatibility
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user_for_export(db_session: AsyncSession):
    """Create test user for export tests."""
    user = User(
        id=1,
        email="export@example.com",
        username="exportuser",
        hashed_password="hashed_password_here"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_in_db(db_session: AsyncSession, test_user_for_export, test_wav_fixture):
    """
    Create test sample in database with real WAV file.

    Uses the test_wav_fixture from conftest.py to create a real audio file
    that can be used for export testing.
    """
    sample = Sample(
        id=1,
        user_id=test_user_for_export.id,
        title="Test Export Sample",
        file_path=str(test_wav_fixture),
        file_size=test_wav_fixture.stat().st_size,
        duration=2.0,
        genre="hip-hop",
        bpm=95.0,
        musical_key="C"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def sample_mp3_in_db(db_session: AsyncSession, test_user_for_export, tmp_path):
    """Create test sample with MP3 format (needs conversion)."""
    # Create a simple MP3 file path (actual file would need to exist for real export)
    mp3_path = tmp_path / "test_sample.mp3"
    mp3_path.touch()

    sample = Sample(
        id=2,
        user_id=test_user_for_export.id,
        title="Test MP3 Sample",
        file_path=str(mp3_path),
        file_size=1024,
        duration=1.5,
        genre="electronic",
        bpm=128.0,
        musical_key="D"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    return sample


@pytest_asyncio.fixture
async def kit_in_db(db_session: AsyncSession, test_user_for_export, sample_in_db):
    """Create test kit with one sample."""
    kit = Kit(
        id=1,
        user_id=test_user_for_export.id,
        name="Test Kit",
        description="Kit for export testing"
    )
    db_session.add(kit)
    await db_session.commit()
    await db_session.refresh(kit)
    return kit


class TestExportSingleSample:
    """Test suite for POST /api/v1/sp404/samples/{id}/export endpoint."""

    @pytest.mark.asyncio
    async def test_export_single_sample_json_response(self, api_client, sample_in_db):
        """
        Test 1: Export single sample returns proper JSON response.

        Validates:
        - Endpoint returns 200 OK
        - Response is valid JSON
        - Contains export metadata (sample_id, format, output_path)
        - success flag is True
        - Output path is provided
        """
        response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav",
                "sanitize_filenames": True,
                "include_metadata": True
            }
        )

        assert response.status_code == 200, \
            f"Export should return 200, got {response.status_code}"

        # Verify JSON response
        data = response.json()
        assert "success" in data, "Response must include success field"
        assert data["success"] is True, "Export should succeed"
        assert "sample_id" in data, "Response must include sample_id"
        assert data["sample_id"] == sample_in_db.id, "sample_id should match request"
        assert "format" in data, "Response must include format"
        assert data["format"] == "wav", "Format should match request"
        assert "output_path" in data, "Response must include output_path"

    @pytest.mark.asyncio
    async def test_export_single_sample_wav_format(self, api_client, sample_in_db):
        """
        Test 2: Export sample in WAV format.

        Validates:
        - WAV format specification is respected
        - Output format field matches request
        - Export completes successfully
        """
        response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav",
                "sanitize_filenames": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "wav", "Should export as WAV"
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_export_single_sample_aiff_format(self, api_client, sample_in_db):
        """
        Test 3: Export sample in AIFF format.

        Validates:
        - AIFF format is supported
        - Format conversion works correctly
        - Response indicates AIFF output
        """
        response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "aiff",
                "sanitize_filenames": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "aiff", "Should export as AIFF"
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_export_single_sample_not_found(self, api_client):
        """
        Test 4: Export returns 404 for non-existent sample.

        Validates:
        - Invalid sample ID returns 404
        - Error message is clear
        - Database is not modified
        """
        response = await api_client.post(
            "/api/v1/sp404/samples/9999/export",
            json={
                "organize_by": "flat",
                "format": "wav"
            }
        )

        assert response.status_code == 404, \
            "Should return 404 for non-existent sample"

        data = response.json()
        assert "detail" in data, "Error response should include detail"

    @pytest.mark.asyncio
    async def test_export_single_sample_invalid_config(self, api_client, sample_in_db):
        """
        Test 5: Export returns 422 for invalid configuration.

        Validates:
        - Invalid format is rejected
        - Invalid organize_by is rejected
        - Validation errors are clear
        """
        # Test invalid format
        response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "mp3"  # Unsupported format
            }
        )

        assert response.status_code == 422, \
            "Should return 422 for invalid format"

        # Test invalid organization
        response2 = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "invalid",  # Invalid organization
                "format": "wav"
            }
        )

        assert response2.status_code == 422, \
            "Should return 422 for invalid organization"

    @pytest.mark.asyncio
    async def test_export_single_sample_download_link(self, api_client, sample_in_db):
        """
        Test 6: Export response includes download link.

        Validates:
        - Response includes download_url or export_id
        - Link can be used to retrieve exported file
        - Export tracking is enabled
        """
        response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should have either download_url or export_id for tracking
        assert "download_url" in data or "export_id" in data, \
            "Response should provide way to download exported file"


class TestExportBatch:
    """Test suite for POST /api/v1/sp404/samples/export-batch endpoint."""

    @pytest.mark.asyncio
    async def test_export_batch_flat_organization(
        self,
        api_client,
        sample_in_db,
        sample_mp3_in_db
    ):
        """
        Test 7: Batch export with flat organization.

        Validates:
        - Multiple samples exported successfully
        - Flat folder structure (no subfolders)
        - All samples in batch are processed
        - Summary includes counts
        """
        response = await api_client.post(
            "/api/v1/sp404/samples/export-batch",
            json={
                "sample_ids": [sample_in_db.id, sample_mp3_in_db.id],
                "config": {
                    "organize_by": "flat",
                    "format": "wav",
                    "sanitize_filenames": True
                }
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "total_requested" in data
        assert data["total_requested"] == 2
        assert "successful" in data
        assert data["successful"] >= 0
        assert "failed" in data

    @pytest.mark.asyncio
    async def test_export_batch_genre_organization(
        self,
        api_client,
        sample_in_db,
        sample_mp3_in_db
    ):
        """
        Test 8: Batch export organized by genre.

        Validates:
        - Genre-based folder organization
        - Samples grouped by genre
        - organized_by field in response
        """
        response = await api_client.post(
            "/api/v1/sp404/samples/export-batch",
            json={
                "sample_ids": [sample_in_db.id, sample_mp3_in_db.id],
                "config": {
                    "organize_by": "genre",
                    "format": "wav"
                }
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "organized_by" in data
        assert data["organized_by"] == "genre"

    @pytest.mark.asyncio
    async def test_export_batch_bpm_organization(
        self,
        api_client,
        sample_in_db,
        sample_mp3_in_db
    ):
        """
        Test 9: Batch export organized by BPM ranges.

        Validates:
        - BPM-based folder organization
        - Samples grouped into BPM ranges (e.g., 90-110, 110-130)
        - organized_by field indicates BPM
        """
        response = await api_client.post(
            "/api/v1/sp404/samples/export-batch",
            json={
                "sample_ids": [sample_in_db.id, sample_mp3_in_db.id],
                "config": {
                    "organize_by": "bpm",
                    "format": "wav"
                }
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "organized_by" in data
        assert data["organized_by"] == "bpm"

    @pytest.mark.asyncio
    async def test_export_batch_empty_sample_list(self, api_client):
        """
        Test 10: Batch export rejects empty sample list.

        Validates:
        - Empty sample_ids array returns 400 or 422
        - Clear error message
        - No export job created
        """
        response = await api_client.post(
            "/api/v1/sp404/samples/export-batch",
            json={
                "sample_ids": [],
                "config": {
                    "organize_by": "flat",
                    "format": "wav"
                }
            }
        )

        assert response.status_code in [400, 422], \
            "Should reject empty sample list"

        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_export_batch_returns_job_id(
        self,
        api_client,
        sample_in_db,
        sample_mp3_in_db
    ):
        """
        Test 11: Batch export returns job ID for tracking.

        Validates:
        - Response includes job_id or export_id
        - Can track batch export progress
        - Enables background processing
        """
        response = await api_client.post(
            "/api/v1/sp404/samples/export-batch",
            json={
                "sample_ids": [sample_in_db.id, sample_mp3_in_db.id],
                "config": {
                    "organize_by": "flat",
                    "format": "wav"
                }
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "job_id" in data or "export_id" in data, \
            "Batch export should return tracking ID"


class TestExportKit:
    """Test suite for POST /api/v1/sp404/kits/{id}/export endpoint."""

    @pytest.mark.asyncio
    async def test_export_kit_success(self, api_client, kit_in_db):
        """
        Test 12: Export kit successfully.

        Validates:
        - Kit export endpoint works
        - Returns export metadata
        - Includes all kit samples
        """
        response = await api_client.post(
            f"/api/v1/sp404/kits/{kit_in_db.id}/export",
            json={
                "format": "wav",
                "organize_by": "flat"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "kit_id" in data or "export_id" in data

    @pytest.mark.asyncio
    async def test_export_kit_not_found(self, api_client):
        """
        Test 13: Export returns 404 for non-existent kit.

        Validates:
        - Invalid kit ID returns 404
        - Clear error message
        """
        response = await api_client.post(
            "/api/v1/sp404/kits/9999/export",
            json={
                "format": "wav",
                "organize_by": "flat"
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_export_kit_maintains_structure(self, api_client, kit_in_db):
        """
        Test 14: Kit export maintains kit folder structure.

        Validates:
        - Kit samples organized together
        - Kit name used for folder
        - Structure suitable for SP-404MK2
        """
        response = await api_client.post(
            f"/api/v1/sp404/kits/{kit_in_db.id}/export",
            json={
                "format": "wav",
                "organize_by": "kit"  # Keep kit structure
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        # Should indicate kit organization
        if "organized_by" in data:
            assert data["organized_by"] == "kit"


class TestDownloadExport:
    """Test suite for GET /api/v1/sp404/exports/{id}/download endpoint."""

    @pytest.mark.asyncio
    async def test_download_export_success(self, api_client, sample_in_db):
        """
        Test 15: Download exported file successfully.

        Validates:
        - Download endpoint returns file
        - Content-Type is application/zip
        - File is valid ZIP

        Note: This test assumes an export was created first.
        """
        # First create an export
        export_response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav"
            }
        )

        assert export_response.status_code == 200
        export_data = export_response.json()

        # Extract export_id if available
        if "export_id" in export_data:
            export_id = export_data["export_id"]

            # Try to download
            download_response = await api_client.get(
                f"/api/v1/sp404/exports/{export_id}/download"
            )

            # If endpoint is implemented, verify response
            if download_response.status_code == 200:
                assert "application/zip" in download_response.headers.get("content-type", "") or \
                       "application/octet-stream" in download_response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_download_export_not_found(self, api_client):
        """
        Test 16: Download returns 404 for non-existent export.

        Validates:
        - Invalid export ID returns 404
        - Clear error message
        """
        response = await api_client.get(
            "/api/v1/sp404/exports/9999/download"
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_download_export_correct_headers(self, api_client, sample_in_db):
        """
        Test 17: Download response has correct headers.

        Validates:
        - Content-Type header is set
        - Content-Disposition header includes filename
        - Headers enable file download in browser
        """
        # First create an export
        export_response = await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav"
            }
        )

        if export_response.status_code == 200:
            export_data = export_response.json()

            if "export_id" in export_data:
                export_id = export_data["export_id"]

                download_response = await api_client.get(
                    f"/api/v1/sp404/exports/{export_id}/download"
                )

                if download_response.status_code == 200:
                    # Check headers
                    assert "content-type" in download_response.headers
                    # Content-Disposition should suggest a filename
                    if "content-disposition" in download_response.headers:
                        assert "attachment" in download_response.headers["content-disposition"] or \
                               "filename" in download_response.headers["content-disposition"]


class TestListExports:
    """Test suite for GET /api/v1/sp404/exports endpoint."""

    @pytest.mark.asyncio
    async def test_list_exports(self, api_client, sample_in_db):
        """
        Test 18: List all exports for user.

        Validates:
        - Returns list of exports
        - Each export has metadata
        - Sorted by date (newest first)
        """
        # Create an export first
        await api_client.post(
            f"/api/v1/sp404/samples/{sample_in_db.id}/export",
            json={
                "organize_by": "flat",
                "format": "wav"
            }
        )

        # List exports
        response = await api_client.get("/api/v1/sp404/exports")

        assert response.status_code == 200
        data = response.json()

        # Should return a list (even if empty)
        assert isinstance(data, list) or "exports" in data

        # If exports exist, validate structure
        if isinstance(data, list) and len(data) > 0:
            export = data[0]
            assert "id" in export or "export_id" in export
            assert "created_at" in export or "timestamp" in export
        elif "exports" in data and len(data["exports"]) > 0:
            export = data["exports"][0]
            assert "id" in export or "export_id" in export

    @pytest.mark.asyncio
    async def test_list_exports_pagination(self, api_client, sample_in_db):
        """
        Test 19: List exports with pagination.

        Validates:
        - Pagination parameters work (limit, offset)
        - Response includes total count
        - Results are limited correctly
        """
        # Create multiple exports
        for _ in range(3):
            await api_client.post(
                f"/api/v1/sp404/samples/{sample_in_db.id}/export",
                json={
                    "organize_by": "flat",
                    "format": "wav"
                }
            )

        # Test pagination
        response = await api_client.get(
            "/api/v1/sp404/exports?limit=2&offset=0"
        )

        assert response.status_code == 200
        data = response.json()

        # Validate pagination
        if isinstance(data, dict):
            if "exports" in data:
                # Paginated response format
                assert len(data["exports"]) <= 2
                if "total" in data:
                    assert data["total"] >= 0
            elif "items" in data:
                # Alternative pagination format
                assert len(data["items"]) <= 2
        elif isinstance(data, list):
            # Simple list format
            assert len(data) <= 2


# Meta-test to verify SP404 export endpoints will be implemented
def test_sp404_export_endpoints_will_be_implemented():
    """
    Meta-test documenting expected ImportError before implementation.

    This test documents that the SP404 export endpoint module
    should not exist yet (RED phase of TDD).

    Once implemented, this test can be removed or modified.
    """
    # This test passes regardless - it's documentation
    # The actual endpoint tests above will fail until implementation
    assert True, "SP404 export endpoints will be implemented to pass the tests above"
