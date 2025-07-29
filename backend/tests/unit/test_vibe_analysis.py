"""Tests for vibe analysis service."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.vibe_analysis import VibeAnalysisService
from app.models.sample import Sample


@pytest.mark.asyncio
async def test_analyze_sample(db_session: AsyncSession):
    """Test sample vibe analysis."""
    # Create a test user first
    from app.models.user import User
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create a test sample
    sample = Sample(
        title="Test Beat",
        file_path="/test/beat.wav",
        genre="hip-hop",
        bpm=90.0,
        user_id=user.id
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    
    # Analyze the sample
    service = VibeAnalysisService(db_session)
    analysis = await service.analyze_sample(sample.id)
    
    # Check analysis results
    assert analysis["sample_id"] == sample.id
    assert analysis["mood_primary"] in ["energetic", "melancholic", "aggressive", "chill", "mysterious", "uplifting"]
    assert analysis["mood_secondary"] in ["energetic", "melancholic", "aggressive", "chill", "mysterious", "uplifting"]
    assert 0.7 <= analysis["mood_confidence"] <= 0.95
    assert 0.3 <= analysis["energy_level"] <= 0.9
    assert 0 <= analysis["energy_variance"] <= 0.3
    assert 0.4 <= analysis["danceability"] <= 0.9
    assert 0 <= analysis["acousticness"] <= 0.7
    assert 0 <= analysis["instrumentalness"] <= 0.9
    assert len(analysis["texture_tags"]) == 3
    assert analysis["bpm"] == 90.0  # Should use the sample's BPM
    assert analysis["key"] is not None
    assert len(analysis["compatible_genres"]) > 0


@pytest.mark.asyncio
async def test_analyze_sample_without_bpm(db_session: AsyncSession):
    """Test analysis estimates BPM when not provided."""
    # Create user
    from app.models.user import User
    user = User(email="test2@example.com", username="test2", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    
    sample = Sample(
        title="No BPM Sample",
        file_path="/test/sample.wav",
        genre="ambient",
        user_id=user.id
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)
    
    service = VibeAnalysisService(db_session)
    analysis = await service.analyze_sample(sample.id)
    
    # Should estimate BPM based on mood
    assert analysis["bpm"] is not None
    assert 60 <= analysis["bpm"] <= 180


@pytest.mark.asyncio
async def test_analyze_nonexistent_sample(db_session: AsyncSession):
    """Test analysis fails for nonexistent sample."""
    service = VibeAnalysisService(db_session)
    
    with pytest.raises(ValueError, match="Sample 9999 not found"):
        await service.analyze_sample(9999)


@pytest.mark.asyncio
async def test_calculate_compatibility_same_mood(db_session: AsyncSession):
    """Test compatibility calculation for samples with same mood."""
    # Create user
    from app.models.user import User
    user = User(email="test3@example.com", username="test3", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    
    # Create two samples that will have the same mood (based on title hash)
    sample1 = Sample(title="Beat A", file_path="/test/a.wav", bpm=120, user_id=user.id)
    sample2 = Sample(title="Beat A Copy", file_path="/test/b.wav", bpm=120, user_id=user.id)
    
    db_session.add_all([sample1, sample2])
    await db_session.commit()
    await db_session.refresh(sample1)
    await db_session.refresh(sample2)
    
    service = VibeAnalysisService(db_session)
    
    # Mock analyze_sample to return same mood
    original_analyze = service.analyze_sample
    async def mock_analyze(sample_id):
        result = await original_analyze(sample_id)
        result["mood"] = "energetic"
        result["mood_primary"] = "energetic"
        result["energy"] = 0.8
        result["energy_level"] = 0.8
        return result
    
    service.analyze_sample = mock_analyze
    
    compatibility = await service.calculate_compatibility(sample1.id, sample2.id)
    
    # High compatibility for same mood and similar energy
    assert compatibility >= 0.7


@pytest.mark.asyncio
async def test_calculate_compatibility_different_bpm(db_session: AsyncSession):
    """Test compatibility with different BPMs."""
    # Create user
    from app.models.user import User
    user = User(email="test4@example.com", username="test4", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    
    sample1 = Sample(title="Fast", file_path="/test/fast.wav", bpm=140, user_id=user.id)
    sample2 = Sample(title="Slow", file_path="/test/slow.wav", bpm=70, user_id=user.id)  # Half-time
    
    db_session.add_all([sample1, sample2])
    await db_session.commit()
    await db_session.refresh(sample1)
    await db_session.refresh(sample2)
    
    service = VibeAnalysisService(db_session)
    compatibility = await service.calculate_compatibility(sample1.id, sample2.id)
    
    # Should have some compatibility due to harmonic BPM relationship
    assert compatibility > 0


def test_estimate_key_by_mood():
    """Test key estimation based on mood."""
    service = VibeAnalysisService(None)  # No DB needed for this test
    
    # Test multiple times to account for randomness
    minor_count = 0
    for _ in range(20):
        key = service._estimate_key("melancholic")
        if "minor" in key:
            minor_count += 1
    
    # Melancholic mood should mostly produce minor keys
    assert minor_count > 15


def test_compatible_genres():
    """Test genre compatibility mapping."""
    service = VibeAnalysisService(None)
    
    genres = service._get_compatible_genres("energetic")
    assert "house" in genres
    assert "drum & bass" in genres
    
    genres = service._get_compatible_genres("chill")
    assert "ambient" in genres
    assert "downtempo" in genres


def test_mood_compatibility():
    """Test mood compatibility checking."""
    service = VibeAnalysisService(None)
    
    assert service._are_moods_compatible("energetic", "uplifting")
    assert service._are_moods_compatible("melancholic", "chill")
    assert not service._are_moods_compatible("aggressive", "chill")
    assert not service._are_moods_compatible("energetic", "melancholic")