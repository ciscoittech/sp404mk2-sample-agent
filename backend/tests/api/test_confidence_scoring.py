"""
Tests for confidence scoring API endpoints and UI display.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sample import Sample as SampleModel


@pytest.mark.asyncio
class TestConfidenceScoringAPI:
    """Tests for confidence scoring in API responses."""

    async def test_sample_response_includes_confidence_scores(
        self, client: AsyncClient, authenticated_user, db_session: AsyncSession
    ):
        """Test that sample API returns confidence scores."""
        # Create a sample with confidence scores
        sample = SampleModel(
            user_id=authenticated_user["user"].id,
            title="Test Sample with Confidence",
            file_path="/tmp/test.wav",
            bpm=90.5,
            bpm_confidence=87,
            genre="Hip-Hop",
            genre_confidence=72,
            musical_key="C minor",
            key_confidence=65,
            analysis_metadata={
                "bpm_method": "rhythm_extractor_2013",
                "bpm_raw": 90.3,
                "was_corrected": False
            }
        )
        db_session.add(sample)
        await db_session.commit()
        await db_session.refresh(sample)

        # Act
        response = await client.get(
            f"/api/v1/samples/{sample.id}",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["bpm_confidence"] == 87
        assert data["genre_confidence"] == 72
        assert data["key_confidence"] == 65
        assert 0 <= data["bpm_confidence"] <= 100
        assert 0 <= data["genre_confidence"] <= 100

    async def test_sample_without_confidence_scores(
        self, client: AsyncClient, authenticated_user, db_session: AsyncSession
    ):
        """Test backward compatibility - samples without confidence scores."""
        # Create a sample without confidence scores
        sample = SampleModel(
            user_id=authenticated_user["user"].id,
            title="Legacy Sample",
            file_path="/tmp/legacy.wav",
            bpm=120.0,
            genre="Jazz"
        )
        db_session.add(sample)
        await db_session.commit()
        await db_session.refresh(sample)

        # Act
        response = await client.get(
            f"/api/v1/samples/{sample.id}",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["bpm"] == 120.0
        assert data["genre"] == "Jazz"
        assert data["bpm_confidence"] is None
        assert data["genre_confidence"] is None

    async def test_analysis_debug_endpoint_returns_full_metadata(
        self, client: AsyncClient, authenticated_user, db_session: AsyncSession
    ):
        """Test debug endpoint returns complete analysis metadata."""
        # Create a sample with detailed metadata
        sample = SampleModel(
            user_id=authenticated_user["user"].id,
            title="Debug Test Sample",
            file_path="/tmp/debug.wav",
            bpm=90.5,
            bpm_confidence=87,
            genre="Hip-Hop",
            genre_confidence=72,
            analysis_metadata={
                "bpm_method": "rhythm_extractor_2013",
                "bpm_raw": 90.3,
                "was_corrected": False,
                "sp404_category": "Hip-Hop/Trap",
                "genre_top_3": [
                    {"genre": "Hip-Hop", "confidence": 72},
                    {"genre": "Boom Bap", "confidence": 18},
                    {"genre": "Lo-Fi", "confidence": 6}
                ]
            }
        )
        db_session.add(sample)
        await db_session.commit()
        await db_session.refresh(sample)

        # Act
        response = await client.get(
            f"/api/v1/samples/{sample.id}/analysis-debug",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "sample_id" in data
        assert "bpm" in data
        assert "genre" in data
        assert "metadata" in data

        # Check BPM debug info
        assert data["bpm"]["value"] == 90.5
        assert data["bpm"]["confidence"] == 87
        assert data["bpm"]["raw_value"] == 90.3
        assert data["bpm"]["was_corrected"] is False
        assert data["bpm"]["method"] == "rhythm_extractor_2013"

        # Check genre debug info
        assert data["genre"]["value"] == "Hip-Hop"
        assert data["genre"]["confidence"] == 72
        assert data["genre"]["sp404_category"] == "Hip-Hop/Trap"
        assert len(data["genre"]["top_3"]) == 3

    async def test_analysis_debug_endpoint_missing_sample(
        self, client: AsyncClient, authenticated_user
    ):
        """Test debug endpoint returns 404 for missing sample."""
        # Act
        response = await client.get(
            "/api/v1/samples/99999/analysis-debug",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Sample not found"

    async def test_analysis_debug_with_minimal_metadata(
        self, client: AsyncClient, authenticated_user, db_session: AsyncSession
    ):
        """Test debug endpoint works with minimal metadata."""
        # Create a sample with no analysis metadata
        sample = SampleModel(
            user_id=authenticated_user["user"].id,
            title="Minimal Sample",
            file_path="/tmp/minimal.wav",
            bpm=100.0,
            bpm_confidence=50
        )
        db_session.add(sample)
        await db_session.commit()
        await db_session.refresh(sample)

        # Act
        response = await client.get(
            f"/api/v1/samples/{sample.id}/analysis-debug",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["bpm"]["value"] == 100.0
        assert data["bpm"]["confidence"] == 50
        assert data["bpm"]["raw_value"] is None
        assert data["bpm"]["was_corrected"] is None
        assert data["bpm"]["method"] is None
        assert data["genre"] is None
        assert data["metadata"] == {}

    async def test_list_samples_includes_confidence(
        self, client: AsyncClient, authenticated_user, db_session: AsyncSession
    ):
        """Test that list endpoint includes confidence scores."""
        # Create a sample with confidence
        sample = SampleModel(
            user_id=authenticated_user["user"].id,
            title="Sample with Confidence",
            file_path="/tmp/sample_list.wav",
            bpm=90.0,
            bpm_confidence=85,
            genre="Hip-Hop",
            genre_confidence=75
        )
        db_session.add(sample)
        await db_session.commit()
        await db_session.refresh(sample)

        # Act - Get the specific sample to verify confidence is returned
        response = await client.get(
            f"/api/v1/samples/{sample.id}",
            headers=authenticated_user["headers"]
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["bpm_confidence"] == 85
        assert data["genre_confidence"] == 75

    async def test_confidence_scores_in_sample_schema(
        self, client: AsyncClient, authenticated_user, db_session: AsyncSession
    ):
        """Test that SampleUpdate schema accepts confidence scores."""
        from app.schemas.sample import SampleUpdate

        # Verify schema accepts confidence scores
        update_data = SampleUpdate(
            bpm_confidence=85,
            genre_confidence=75,
            key_confidence=60
        )

        # Assert
        assert update_data.bpm_confidence == 85
        assert update_data.genre_confidence == 75
        assert update_data.key_confidence == 60
