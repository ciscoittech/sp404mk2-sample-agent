"""
Integration tests for sample API endpoints.
Tests the full request/response cycle.
"""
import pytest
from httpx import AsyncClient
import io


class TestSamplesAPI:
    """Integration tests for /api/samples endpoints."""
    
    @pytest.mark.integration
    async def test_create_sample_full_flow(self, client: AsyncClient, authenticated_user, sample_file):
        """Test complete sample creation flow with file upload."""
        # Arrange
        files = {
            "file": ("test.wav", sample_file, "audio/wav")
        }
        data = {
            "title": "Integration Test Beat",
            "tags": ["test", "integration"]
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
        assert result["title"] == "Integration Test Beat"
        assert result["file_url"] is not None
        assert "test" in result["tags"]
        assert result["id"] is not None
    
    @pytest.mark.integration
    async def test_list_samples_with_pagination(self, client: AsyncClient, authenticated_user):
        """Test listing samples with pagination."""
        # Act
        response = await client.get(
            "/api/v1/samples?page=1&limit=10",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "pages" in result
        assert len(result["items"]) <= 10
    
    @pytest.mark.integration
    async def test_search_samples(self, client: AsyncClient, authenticated_user):
        """Test searching samples with filters."""
        # Act
        response = await client.get(
            "/api/v1/samples/search",
            params={
                "q": "jazz",
                "genre": "jazz",
                "bpm_min": 90,
                "bpm_max": 110
            },
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # All results should match search criteria
        for sample in results:
            assert "jazz" in sample["title"].lower() or sample["genre"] == "jazz"
            assert 90 <= sample["bpm"] <= 110
    
    @pytest.mark.integration
    async def test_analyze_sample(self, client: AsyncClient, authenticated_user):
        """Test triggering sample analysis."""
        # First create a sample
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("test.wav", b"fake-audio", "audio/wav")},
            data={"title": "Test for Analysis"},
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
        assert result["job_id"] is not None
    
    @pytest.mark.integration
    async def test_get_sample_with_analysis(self, client: AsyncClient, authenticated_user):
        """Test retrieving a sample with its analysis results."""
        # Assuming sample ID 1 exists with analysis
        response = await client.get(
            "/api/v1/samples/1",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        sample = response.json()
        assert "id" in sample
        assert "title" in sample
        if sample.get("vibe_analysis"):
            assert "mood_primary" in sample["vibe_analysis"]
            assert "energy_level" in sample["vibe_analysis"]
    
    @pytest.mark.integration
    async def test_update_sample_metadata(self, client: AsyncClient, authenticated_user):
        """Test updating sample metadata."""
        # Act
        response = await client.patch(
            "/api/v1/samples/1",
            json={
                "title": "Updated Title",
                "tags": ["updated", "test"]
            },
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Updated Title"
        assert "updated" in updated["tags"]
    
    @pytest.mark.integration
    async def test_delete_sample(self, client: AsyncClient, authenticated_user):
        """Test deleting a sample."""
        # First create a sample to delete
        create_response = await client.post(
            "/api/v1/samples",
            files={"file": ("delete-me.wav", b"fake-audio", "audio/wav")},
            data={"title": "To Be Deleted"},
            headers=authenticated_user["headers"]
        )
        sample_id = create_response.json()["id"]
        
        # Act - Delete the sample
        response = await client.delete(
            f"/api/v1/samples/{sample_id}",
            headers=authenticated_user["headers"]
        )
        
        # Assert
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = await client.get(
            f"/api/v1/samples/{sample_id}",
            headers=authenticated_user["headers"]
        )
        assert get_response.status_code == 404
    
    @pytest.mark.integration
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test that endpoints require authentication."""
        # Act - Try without auth header
        response = await client.get("/api/v1/samples")
        
        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"