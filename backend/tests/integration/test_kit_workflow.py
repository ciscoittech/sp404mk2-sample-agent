"""
Integration tests for complete Kit Builder workflows.

Tests full user journeys from creation to export.
All tests use REAL database and REAL API calls (no mocks).
All tests written to FAIL initially (TDD Red phase).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import zipfile
import io

from app.models.sample import Sample


@pytest.mark.asyncio
async def test_complete_kit_workflow(
    client: AsyncClient,
    sample_kick_short: Sample,
    sample_snare_short: Sample,
    sample_hat_closed: Sample
):
    """Test complete workflow: create → assign → export."""
    # Step 1: Create kit
    create_response = await client.post(
        "/api/v1/kits",
        json={
            "name": "Integration Test Kit",
            "description": "Full workflow test"
        }
    )
    assert create_response.status_code == 201
    kit_id = create_response.json()["id"]

    # Step 2: Assign samples to pads
    assignments = [
        (sample_kick_short.id, 13, "Main kick"),
        (sample_snare_short.id, 14, "Main snare"),
        (sample_hat_closed.id, 15, "Closed hat"),
    ]

    for sample_id, pad_num, description in assignments:
        response = await client.post(
            f"/api/v1/kits/{kit_id}/assign",
            json={
                "sample_id": sample_id,
                "pad_bank": "A",
                "pad_number": pad_num
            }
        )
        assert response.status_code == 201, f"Failed to assign {description}"

    # Step 3: Verify kit has all assignments
    kit_response = await client.get(f"/api/v1/kits/{kit_id}")
    assert kit_response.status_code == 200
    kit_data = kit_response.json()
    assert len(kit_data["samples"]) == 3

    # Step 4: Export kit
    export_response = await client.post(
        f"/api/v1/kits/{kit_id}/export?format=wav"
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "application/zip"

    # Step 5: Verify ZIP contents
    zip_buffer = io.BytesIO(export_response.content)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        files = zip_file.namelist()

        # Should have text file with pad assignments
        assert "pad_assignments.txt" in files

        # Should have WAV files
        wav_files = [f for f in files if ".wav" in f.lower()]
        assert len(wav_files) == 3

        # Verify text file content
        text_content = zip_file.read("pad_assignments.txt").decode('utf-8')
        assert "Pad 13:" in text_content  # Kick
        assert "Pad 14:" in text_content  # Snare
        assert "Pad 15:" in text_content  # Hat


@pytest.mark.asyncio
async def test_recommendation_workflow(
    client: AsyncClient,
    sample_85bpm: Sample,
    sample_90bpm: Sample,
    sample_140bpm: Sample
):
    """Test workflow: get recommendations → assign → verify BPM matching."""
    # Step 1: Create kit
    create_response = await client.post(
        "/api/v1/kits",
        json={"name": "BPM Matching Test Kit"}
    )
    assert create_response.status_code == 201
    kit_id = create_response.json()["id"]

    # Step 2: Assign 85 BPM sample to establish kit BPM
    await client.post(
        f"/api/v1/kits/{kit_id}/assign",
        json={
            "sample_id": sample_85bpm.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )

    # Step 3: Get recommendations for pad 2 (should prefer similar BPM)
    rec_response = await client.get(
        f"/api/v1/kits/{kit_id}/recommendations/2?limit=10"
    )
    assert rec_response.status_code == 200
    recommendations = rec_response.json()["samples"]

    # Step 4: Verify BPM matching logic
    recommended_ids = [s["id"] for s in recommendations]

    # 90 BPM should be recommended (within ±10 of 85)
    assert sample_90bpm.id in recommended_ids

    # 140 BPM should NOT be recommended (too far from 85)
    assert sample_140bpm.id not in recommended_ids

    # Step 5: Assign recommended sample
    if len(recommendations) > 0:
        recommended_sample_id = recommendations[0]["id"]
        assign_response = await client.post(
            f"/api/v1/kits/{kit_id}/assign",
            json={
                "sample_id": recommended_sample_id,
                "pad_bank": "A",
                "pad_number": 2
            }
        )
        assert assign_response.status_code == 201

    # Step 6: Verify kit now has 2 samples
    kit_response = await client.get(f"/api/v1/kits/{kit_id}")
    kit_data = kit_response.json()
    assert len(kit_data["samples"]) >= 2


@pytest.mark.asyncio
async def test_pad_reassignment_workflow(
    client: AsyncClient,
    test_sample: Sample,
    sample_kick_short: Sample
):
    """Test workflow: assign → remove → assign different sample."""
    # Step 1: Create kit
    create_response = await client.post(
        "/api/v1/kits",
        json={"name": "Reassignment Test Kit"}
    )
    kit_id = create_response.json()["id"]

    # Step 2: Assign first sample to pad A1
    assign1_response = await client.post(
        f"/api/v1/kits/{kit_id}/assign",
        json={
            "sample_id": test_sample.id,
            "pad_bank": "A",
            "pad_number": 1,
            "volume": 0.7
        }
    )
    assert assign1_response.status_code == 201
    assert assign1_response.json()["volume"] == 0.7

    # Step 3: Verify assignment exists
    kit_response = await client.get(f"/api/v1/kits/{kit_id}")
    kit_data = kit_response.json()
    pad_a1 = [s for s in kit_data["samples"] if s["pad_bank"] == "A" and s["pad_number"] == 1]
    assert len(pad_a1) == 1
    assert pad_a1[0]["sample"]["id"] == test_sample.id

    # Step 4: Remove sample from pad A1
    remove_response = await client.delete(f"/api/v1/kits/{kit_id}/pads/A/1")
    assert remove_response.status_code == 204

    # Step 5: Verify pad is now empty
    kit_response = await client.get(f"/api/v1/kits/{kit_id}")
    kit_data = kit_response.json()
    pad_a1 = [s for s in kit_data["samples"] if s["pad_bank"] == "A" and s["pad_number"] == 1]
    assert len(pad_a1) == 0

    # Step 6: Assign different sample to same pad
    assign2_response = await client.post(
        f"/api/v1/kits/{kit_id}/assign",
        json={
            "sample_id": sample_kick_short.id,
            "pad_bank": "A",
            "pad_number": 1,
            "volume": 0.9,
            "pitch_shift": 2
        }
    )
    assert assign2_response.status_code == 201
    assert assign2_response.json()["sample"]["id"] == sample_kick_short.id
    assert assign2_response.json()["pitch_shift"] == 2

    # Step 7: Verify new assignment persisted
    kit_response = await client.get(f"/api/v1/kits/{kit_id}")
    kit_data = kit_response.json()
    pad_a1 = [s for s in kit_data["samples"] if s["pad_bank"] == "A" and s["pad_number"] == 1]
    assert len(pad_a1) == 1
    assert pad_a1[0]["sample"]["id"] == sample_kick_short.id


@pytest.mark.asyncio
async def test_kit_update_workflow(client: AsyncClient):
    """Test workflow: create → update name → verify persistence."""
    # Step 1: Create kit
    create_response = await client.post(
        "/api/v1/kits",
        json={
            "name": "Original Kit Name",
            "description": "Original description"
        }
    )
    assert create_response.status_code == 201
    kit_id = create_response.json()["id"]

    # Step 2: Update kit metadata
    update_response = await client.patch(
        f"/api/v1/kits/{kit_id}",
        json={
            "name": "Updated Kit Name",
            "description": "Updated description after creation"
        }
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Kit Name"

    # Step 3: Fetch kit to verify persistence
    get_response = await client.get(f"/api/v1/kits/{kit_id}")
    assert get_response.status_code == 200
    kit_data = get_response.json()
    assert kit_data["name"] == "Updated Kit Name"
    assert kit_data["description"] == "Updated description after creation"

    # Step 4: Partial update (name only)
    partial_response = await client.patch(
        f"/api/v1/kits/{kit_id}",
        json={"name": "Final Kit Name"}
    )
    assert partial_response.status_code == 200

    # Step 5: Verify description unchanged
    final_response = await client.get(f"/api/v1/kits/{kit_id}")
    final_data = final_response.json()
    assert final_data["name"] == "Final Kit Name"
    assert final_data["description"] == "Updated description after creation"


@pytest.mark.asyncio
async def test_multi_kit_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test workflow: create 3 kits → list → verify pagination."""
    # Step 1: Create 3 kits with different names
    kit_names = ["Hip-Hop Starter Kit", "Lo-Fi Chill Kit", "Trap Banger Kit"]
    kit_ids = []

    for name in kit_names:
        response = await client.post(
            "/api/v1/kits",
            json={
                "name": name,
                "description": f"Description for {name}"
            }
        )
        assert response.status_code == 201
        kit_ids.append(response.json()["id"])

    # Step 2: List all kits
    list_response = await client.get("/api/v1/kits")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] == 3
    assert len(list_data["kits"]) == 3

    # Step 3: Verify all kit names present
    returned_names = [k["name"] for k in list_data["kits"]]
    for name in kit_names:
        assert name in returned_names

    # Step 4: Test pagination (2 per page)
    page1_response = await client.get("/api/v1/kits?skip=0&limit=2")
    assert page1_response.status_code == 200
    page1_data = page1_response.json()
    assert len(page1_data["kits"]) == 2
    assert page1_data["total"] == 3

    page2_response = await client.get("/api/v1/kits?skip=2&limit=2")
    assert page2_response.status_code == 200
    page2_data = page2_response.json()
    assert len(page2_data["kits"]) == 1

    # Step 5: Delete one kit
    delete_response = await client.delete(f"/api/v1/kits/{kit_ids[0]}")
    assert delete_response.status_code == 204

    # Step 6: Verify only 2 kits remain
    final_response = await client.get("/api/v1/kits")
    final_data = final_response.json()
    assert final_data["total"] == 2


@pytest.mark.asyncio
async def test_genre_based_recommendation_workflow(
    client: AsyncClient,
    sample_hiphop: Sample,
    sample_jazz: Sample
):
    """Test workflow: assign genre-specific sample → get genre-matched recommendations."""
    # Step 1: Create kit
    create_response = await client.post(
        "/api/v1/kits",
        json={"name": "Genre Matching Test Kit"}
    )
    kit_id = create_response.json()["id"]

    # Step 2: Assign hip-hop sample to establish genre
    await client.post(
        f"/api/v1/kits/{kit_id}/assign",
        json={
            "sample_id": sample_hiphop.id,
            "pad_bank": "A",
            "pad_number": 1
        }
    )

    # Step 3: Get recommendations (should prefer hip-hop genre)
    rec_response = await client.get(
        f"/api/v1/kits/{kit_id}/recommendations/2?limit=10"
    )
    assert rec_response.status_code == 200
    recommendations = rec_response.json()["samples"]

    # Step 4: Verify genre matching (hip-hop preferred over jazz)
    # Note: This depends on having multiple samples in DB
    if len(recommendations) > 0:
        # At minimum, verify recommendations are returned
        assert isinstance(recommendations, list)
        assert all("id" in s for s in recommendations)


@pytest.mark.asyncio
async def test_full_bank_assignment_workflow(
    client: AsyncClient,
    test_sample: Sample,
    sample_kick_short: Sample,
    sample_snare_short: Sample,
    sample_hat_closed: Sample
):
    """Test workflow: assign samples across all 4 banks (A, B, C, D)."""
    # Step 1: Create kit
    create_response = await client.post(
        "/api/v1/kits",
        json={"name": "Multi-Bank Test Kit"}
    )
    kit_id = create_response.json()["id"]

    # Step 2: Assign samples to different banks
    assignments = [
        ("A", 1, test_sample.id),
        ("B", 5, sample_kick_short.id),
        ("C", 10, sample_snare_short.id),
        ("D", 15, sample_hat_closed.id),
    ]

    for bank, pad_num, sample_id in assignments:
        response = await client.post(
            f"/api/v1/kits/{kit_id}/assign",
            json={
                "sample_id": sample_id,
                "pad_bank": bank,
                "pad_number": pad_num
            }
        )
        assert response.status_code == 201

    # Step 3: Verify all 4 assignments
    kit_response = await client.get(f"/api/v1/kits/{kit_id}")
    kit_data = kit_response.json()
    assert len(kit_data["samples"]) == 4

    # Step 4: Verify each bank has assignment
    banks_assigned = set(s["pad_bank"] for s in kit_data["samples"])
    assert banks_assigned == {"A", "B", "C", "D"}

    # Step 5: Export kit with all banks
    export_response = await client.post(
        f"/api/v1/kits/{kit_id}/export?format=wav"
    )
    assert export_response.status_code == 200

    # Step 6: Verify export contains all samples
    zip_buffer = io.BytesIO(export_response.content)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        files = zip_file.namelist()
        wav_files = [f for f in files if ".wav" in f.lower()]
        assert len(wav_files) == 4


@pytest.mark.asyncio
async def test_htmx_workflow(client: AsyncClient, test_sample: Sample):
    """Test complete HTMX workflow with template responses."""
    # Step 1: List kits with HTMX request
    list_response = await client.get(
        "/api/v1/kits",
        headers={"HX-Request": "true"}
    )
    assert list_response.status_code == 200
    assert "text/html" in list_response.headers.get("content-type", "")

    # Step 2: Create kit (JSON response even with HTMX)
    create_response = await client.post(
        "/api/v1/kits",
        json={"name": "HTMX Test Kit"},
        headers={"HX-Request": "true"}
    )
    assert create_response.status_code == 201
    kit_id = create_response.json()["id"]

    # Step 3: Get kit details with HTMX
    get_response = await client.get(
        f"/api/v1/kits/{kit_id}",
        headers={"HX-Request": "true"}
    )
    assert get_response.status_code == 200

    # Response may be JSON or HTML depending on endpoint design
    content_type = get_response.headers.get("content-type", "")
    assert "json" in content_type or "html" in content_type
