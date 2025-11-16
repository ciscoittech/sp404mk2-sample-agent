"""
Tests for Kit API endpoints.

Tests use FastAPI TestClient with REAL database.
Tests validate both JSON and HTMX responses.
All tests written to FAIL initially (TDD Red phase).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.models.kit import Kit
from app.models.sample import Sample


@pytest.mark.asyncio
async def test_list_kits_json(client: AsyncClient, db_session: AsyncSession):
    """Test GET /api/v1/kits returns JSON."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create test kits
    await kit_service.create_kit(db_session, user_id=1, name="Kit 1")
    await kit_service.create_kit(db_session, user_id=1, name="Kit 2")

    response = await client.get("/api/v1/kits")

    assert response.status_code == 200
    data = response.json()
    assert "kits" in data
    assert "total" in data
    assert isinstance(data["kits"], list)
    assert len(data["kits"]) == 2


@pytest.mark.asyncio
async def test_list_kits_htmx(client: AsyncClient, db_session: AsyncSession):
    """Test GET /api/v1/kits returns HTMX template."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create test kit
    await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    response = await client.get(
        "/api/v1/kits",
        headers={"HX-Request": "true"}
    )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # Verify HTML contains kit cards
    html = response.text
    assert "Test Kit" in html
    assert "kit-card" in html or "card" in html


@pytest.mark.asyncio
async def test_list_kits_pagination(client: AsyncClient, db_session: AsyncSession):
    """Test pagination parameters work correctly."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create 5 kits
    for i in range(5):
        await kit_service.create_kit(db_session, user_id=1, name=f"Kit {i}")

    # Get first page
    response = await client.get("/api/v1/kits?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["kits"]) == 2
    assert data["total"] == 5

    # Get second page
    response = await client.get("/api/v1/kits?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["kits"]) == 2


@pytest.mark.asyncio
async def test_create_kit_success(client: AsyncClient):
    """Test POST /api/v1/kits creates kit."""
    response = await client.post(
        "/api/v1/kits",
        json={
            "name": "My New Kit",
            "description": "Test description"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My New Kit"
    assert data["description"] == "Test description"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_kit_minimal_data(client: AsyncClient):
    """Test creating kit with only required fields."""
    response = await client.post(
        "/api/v1/kits",
        json={"name": "Minimal Kit"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Kit"
    assert data["description"] is None or data["description"] == ""


@pytest.mark.asyncio
async def test_create_kit_validation_error(client: AsyncClient):
    """Test POST /api/v1/kits with invalid data."""
    response = await client.post(
        "/api/v1/kits",
        json={
            "name": "A" * 300,  # Too long!
            "description": "Test"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "255" in data["detail"] or "exceed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_kit_empty_name(client: AsyncClient):
    """Test creating kit with empty name fails."""
    response = await client.post(
        "/api/v1/kits",
        json={
            "name": "",
            "description": "Test"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "name" in data["detail"].lower() or "empty" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_kit_success(client: AsyncClient, test_kit: Kit):
    """Test GET /api/v1/kits/{id} returns kit details."""
    response = await client.get(f"/api/v1/kits/{test_kit.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_kit.id
    assert data["name"] == test_kit.name
    assert "samples" in data  # Should include pad assignments


@pytest.mark.asyncio
async def test_get_kit_not_found(client: AsyncClient):
    """Test GET /api/v1/kits/{id} with non-existent ID."""
    response = await client.get("/api/v1/kits/99999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_kit_success(client: AsyncClient, test_kit: Kit):
    """Test PATCH /api/v1/kits/{id} updates kit."""
    response = await client.patch(
        f"/api/v1/kits/{test_kit.id}",
        json={
            "name": "Updated Name",
            "description": "Updated Description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Description"


@pytest.mark.asyncio
async def test_update_kit_partial(client: AsyncClient, test_kit: Kit):
    """Test partial update (name only)."""
    original_description = test_kit.description

    response = await client.patch(
        f"/api/v1/kits/{test_kit.id}",
        json={"name": "New Name Only"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name Only"
    assert data["description"] == original_description


@pytest.mark.asyncio
async def test_update_kit_not_found(client: AsyncClient):
    """Test update non-existent kit returns 404."""
    response = await client.patch(
        "/api/v1/kits/99999",
        json={"name": "New Name"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_kit_success(client: AsyncClient, test_kit: Kit):
    """Test DELETE /api/v1/kits/{id} removes kit."""
    response = await client.delete(f"/api/v1/kits/{test_kit.id}")

    assert response.status_code == 204

    # Verify kit deleted
    get_response = await client.get(f"/api/v1/kits/{test_kit.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_kit_not_found(client: AsyncClient):
    """Test deleting non-existent kit returns 404."""
    response = await client.delete("/api/v1/kits/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_assign_sample_success(client: AsyncClient, test_kit: Kit, test_sample: Sample):
    """Test POST /api/v1/kits/{id}/assign."""
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1,
            "volume": 0.8,
            "pitch_shift": 2
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["pad_bank"] == "A"
    assert data["pad_number"] == 1
    assert data["volume"] == 0.8
    assert data["pitch_shift"] == 2
    assert data["sample"]["id"] == test_sample.id


@pytest.mark.asyncio
async def test_assign_sample_minimal_data(client: AsyncClient, test_kit: Kit, test_sample: Sample):
    """Test assign with only required fields (defaults applied)."""
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "B",
            "pad_number": 5
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["volume"] == 1.0  # Default
    assert data["pitch_shift"] == 0  # Default


@pytest.mark.asyncio
async def test_assign_sample_invalid_pad_number(client: AsyncClient, test_kit: Kit, test_sample: Sample):
    """Test assign with invalid pad number."""
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 17  # Invalid!
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "pad" in data["detail"].lower()


@pytest.mark.asyncio
async def test_assign_sample_invalid_bank(client: AsyncClient, test_kit: Kit, test_sample: Sample):
    """Test assign with invalid bank."""
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "E",  # Invalid!
            "pad_number": 1
        }
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_assign_sample_duplicate_error(client: AsyncClient, test_kit: Kit, test_sample: Sample):
    """Test assigning to already-assigned pad fails."""
    # First assignment
    await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )

    # Second assignment to same pad
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "already assigned" in data["detail"].lower()


@pytest.mark.asyncio
async def test_remove_sample_success(client: AsyncClient, test_kit: Kit, test_sample: Sample):
    """Test DELETE /api/v1/kits/{id}/pads/{bank}/{number}."""
    # First assign sample
    await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )

    # Remove sample
    response = await client.delete(f"/api/v1/kits/{test_kit.id}/pads/A/1")

    assert response.status_code == 204

    # Verify removed
    kit_response = await client.get(f"/api/v1/kits/{test_kit.id}")
    kit_data = kit_response.json()
    pad_assignments = [s for s in kit_data["samples"] if s["pad_bank"] == "A" and s["pad_number"] == 1]
    assert len(pad_assignments) == 0


@pytest.mark.asyncio
async def test_remove_sample_empty_pad(client: AsyncClient, test_kit: Kit):
    """Test removing from empty pad returns 404."""
    response = await client.delete(f"/api/v1/kits/{test_kit.id}/pads/A/1")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_recommendations_success(
    client: AsyncClient,
    test_kit: Kit,
    sample_kick_short: Sample
):
    """Test GET /api/v1/kits/{id}/recommendations/{pad_number}."""
    response = await client.get(
        f"/api/v1/kits/{test_kit.id}/recommendations/13"  # Pad 13 = kicks
    )

    assert response.status_code == 200
    data = response.json()
    assert "samples" in data
    assert isinstance(data["samples"], list)
    assert "pad_number" in data
    assert data["pad_number"] == 13

    # Should include kick sample
    sample_ids = [s["id"] for s in data["samples"]]
    assert sample_kick_short.id in sample_ids


@pytest.mark.asyncio
async def test_get_recommendations_with_limit(client: AsyncClient, test_kit: Kit):
    """Test recommendations with custom limit."""
    response = await client.get(
        f"/api/v1/kits/{test_kit.id}/recommendations/1?limit=5"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["samples"]) <= 5


@pytest.mark.asyncio
async def test_get_recommendations_invalid_pad(client: AsyncClient, test_kit: Kit):
    """Test recommendations with invalid pad number."""
    response = await client.get(
        f"/api/v1/kits/{test_kit.id}/recommendations/17"  # Invalid
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_export_kit_success(
    client: AsyncClient,
    test_kit: Kit,
    test_sample: Sample,
    sample_kick_short: Sample
):
    """Test POST /api/v1/kits/{id}/export returns ZIP."""
    # Assign samples first
    await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )
    await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": sample_kick_short.id,
            "pad_bank": "A",
            "pad_number": 13
        }
    )

    # Export kit
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/export?format=wav"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    # Verify it's a valid ZIP
    import zipfile
    zip_buffer = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        files = zip_file.namelist()
        assert len(files) > 0
        assert "pad_assignments.txt" in files or any(".wav" in f for f in files)


@pytest.mark.asyncio
async def test_export_kit_empty_kit(client: AsyncClient, test_kit: Kit):
    """Test exporting empty kit returns 400."""
    response = await client.post(f"/api/v1/kits/{test_kit.id}/export")

    assert response.status_code == 400
    data = response.json()
    assert "no samples" in data["detail"].lower()


@pytest.mark.asyncio
async def test_export_kit_not_found(client: AsyncClient):
    """Test exporting non-existent kit returns 404."""
    response = await client.post("/api/v1/kits/99999/export")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_kit_aiff_format(
    client: AsyncClient,
    test_kit: Kit,
    test_sample: Sample
):
    """Test export with AIFF format."""
    # Assign sample
    await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )

    # Export as AIFF
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/export?format=aiff"
    )

    assert response.status_code == 200

    # Verify AIFF files in ZIP
    import zipfile
    zip_buffer = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        files = zip_file.namelist()
        aiff_files = [f for f in files if ".aif" in f.lower()]
        assert len(aiff_files) > 0


@pytest.mark.asyncio
async def test_htmx_responses_for_assign(
    client: AsyncClient,
    test_kit: Kit,
    test_sample: Sample
):
    """Test HTMX template response for assign endpoint."""
    response = await client.post(
        f"/api/v1/kits/{test_kit.id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1
        },
        headers={"HX-Request": "true"}
    )

    assert response.status_code == 201

    # Should return HTML template
    if "text/html" in response.headers.get("content-type", ""):
        html = response.text
        assert "pad" in html.lower() or test_sample.title in html
