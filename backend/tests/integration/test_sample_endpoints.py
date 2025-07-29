"""
TDD: Sample API Endpoints Integration Tests
Testing the full request/response cycle
"""
import pytest
from httpx import AsyncClient
import json


class TestSampleEndpoints:
    """Integration tests for sample-related endpoints."""
    
    @pytest.mark.integration
    async def test_create_sample_success(self, client: AsyncClient, authenticated_user, sample_file):
        """Test successful sample creation with file upload."""
        # Arrange
        files = {
            "file": ("test_beat.wav", sample_file, "audio/wav")
        }
        data = {
            "title": "Test Hip Hop Beat",
            "genre": "hip-hop",
            "tags": json.dumps(["drums", "90s", "boom-bap"])  # JSON string for form data
        }
        
        # Act
        response = await client.post(
            "/api/v1/samples",
            files=files,
            data=data,
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 201
        result = response.json()
        
        # Check required fields
        assert result["id"] is not None
        assert result["title"] == "Test Hip Hop Beat"
        assert result["genre"] == "hip-hop"
        assert result["file_url"] is not None
        assert "drums" in result["tags"]
        assert result["user_id"] == authenticated_user["user"]["id"]
        
        # Check timestamps
        assert result["created_at"] is not None
        assert result["analyzed_at"] is None  # Not analyzed yet
    
    @pytest.mark.integration
    async def test_create_sample_invalid_file_type(self, client: AsyncClient, authenticated_user):
        """Test that non-audio files are rejected."""
        # Arrange
        files = {
            "file": ("document.pdf", b"fake pdf content", "application/pdf")
        }
        data = {
            "title": "Invalid File"
        }
        
        # Act
        response = await client.post(
            "/api/v1/samples",
            files=files,
            data=data,
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    @pytest.mark.integration
    async def test_list_samples_pagination(self, client: AsyncClient, authenticated_user):
        """Test listing samples with pagination."""
        # Create some test samples first
        for i in range(25):
            await client.post(
                "/api/v1/samples",
                files={"file": (f"test{i}.wav", b"fake audio", "audio/wav")},
                data={"title": f"Sample {i}"},
                headers=authenticated_user["headers"]
            )
        
        # Act - Get first page
        response = await client.get(
            "/api/v1/samples?page=1&limit=10",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        
        assert result["page"] == 1
        assert result["limit"] == 10
        assert result["total"] >= 25
        assert len(result["items"]) == 10
        assert result["pages"] >= 3
        
        # Check items are properly formatted
        first_item = result["items"][0]
        assert "id" in first_item
        assert "title" in first_item
        assert "created_at" in first_item
    
    @pytest.mark.integration
    async def test_search_samples(self, client: AsyncClient, authenticated_user):
        """Test searching samples with filters."""
        # Create test samples with different properties
        test_samples = [
            {"title": "Jazz Drums 93 BPM", "genre": "jazz", "bpm": 93},
            {"title": "Hip Hop Beat", "genre": "hip-hop", "bpm": 90},
            {"title": "Jazz Bass Line", "genre": "jazz", "bpm": 120},
            {"title": "Electronic Loop", "genre": "electronic", "bpm": 140}
        ]
        
        for sample in test_samples:
            await client.post(
                "/api/v1/samples",
                files={"file": ("test.wav", b"audio", "audio/wav")},
                data=sample,
                headers=authenticated_user["headers"]
            )
        
        # Act - Search for jazz samples
        response = await client.get(
            "/api/v1/samples/search",
            params={
                "q": "jazz",
                "genre": "jazz",
                "bpm_min": 90,
                "bpm_max": 100
            },
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        results = response.json()
        
        assert len(results) == 1  # Only "Jazz Drums 93 BPM" matches all criteria
        assert results[0]["title"] == "Jazz Drums 93 BPM"
        assert results[0]["bpm"] == 93
    
    @pytest.mark.integration
    async def test_get_sample_by_id(self, client: AsyncClient, authenticated_user):
        """Test retrieving a specific sample."""
        # Create a sample first
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("test.wav", b"audio", "audio/wav")},
            data={"title": "Get By ID Test", "bpm": 120},
            headers=authenticated_user["headers"]
        )
        sample_id = create_response.json()["id"]
        
        # Act
        response = await client.get(
            f"/api/v1/samples/{sample_id}",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        sample = response.json()
        assert sample["id"] == sample_id
        assert sample["title"] == "Get By ID Test"
        assert sample["bpm"] == 120
    
    @pytest.mark.integration
    async def test_update_sample_metadata(self, client: AsyncClient, authenticated_user):
        """Test updating sample metadata."""
        # Create a sample
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("test.wav", b"audio", "audio/wav")},
            data={"title": "Original Title"},
            headers=authenticated_user["headers"]
        )
        sample_id = create_response.json()["id"]
        
        # Act - Update metadata
        update_data = {
            "title": "Updated Title",
            "genre": "jazz",
            "bpm": 93,
            "tags": ["updated", "jazz", "drums"]
        }
        response = await client.patch(
            f"/api/v1/samples/{sample_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Updated Title"
        assert updated["genre"] == "jazz"
        assert updated["bpm"] == 93
        assert "updated" in updated["tags"]
    
    @pytest.mark.integration
    async def test_trigger_sample_analysis(self, client: AsyncClient, authenticated_user):
        """Test triggering AI analysis on a sample."""
        # Create a sample
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("analyze.wav", b"audio", "audio/wav")},
            data={"title": "To Be Analyzed"},
            headers=authenticated_user["headers"]
        )
        sample_id = create_response.json()["id"]
        
        # Act - Trigger analysis
        response = await client.post(
            f"/api/v1/samples/{sample_id}/analyze",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 202  # Accepted
        result = response.json()
        assert result["status"] == "processing"
        assert result["message"] == "Analysis queued"
        assert "job_id" in result
    
    @pytest.mark.integration
    async def test_delete_sample(self, client: AsyncClient, authenticated_user):
        """Test deleting a sample."""
        # Create a sample
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("delete.wav", b"audio", "audio/wav")},
            data={"title": "To Be Deleted"},
            headers=authenticated_user["headers"]
        )
        sample_id = create_response.json()["id"]
        
        # Act - Delete
        response = await client.delete(
            f"/api/v1/samples/{sample_id}",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = await client.get(
            f"/api/v1/samples/{sample_id}",
            headers=authenticated_user["headers"]
        )
        assert get_response.status_code == 404
    
    @pytest.mark.integration
    async def test_user_can_only_access_own_samples(self, client: AsyncClient, authenticated_user, user_factory):
        """Test that users can only access their own samples."""
        # Create a sample with first user
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("private.wav", b"audio", "audio/wav")},
            data={"title": "Private Sample"},
            headers=authenticated_user["headers"]
        )
        sample_id = create_response.json()["id"]
        
        # Create another user
        other_user = user_factory()
        other_auth = {
            "user": other_user,
            "token": "other-token",
            "headers": {"Authorization": "Bearer other-token"}
        }
        
        # Act - Try to access first user's sample
        response = await client.get(
            f"/api/v1/samples/{sample_id}",
            headers=other_auth["headers"]
        )
        
        # Assert
        assert response.status_code == 404  # Not found for other user
    
    @pytest.mark.integration
    async def test_unauthenticated_access_denied(self, client: AsyncClient):
        """Test that unauthenticated requests are denied."""
        # Act - Try without auth header
        response = await client.get("/api/v1/samples")
        
        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"