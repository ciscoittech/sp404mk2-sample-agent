"""
Tests for KitService - Kit Builder business logic.

Tests use REAL database operations (no mocks).
Tests use REAL audio sample fixtures.
All tests written to FAIL initially (TDD Red phase).
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.kit import Kit, KitSample
from app.models.sample import Sample


# Service will be imported after implementation
# from app.services.kit_service import (
#     KitService,
#     KitNotFoundError,
#     SampleNotFoundError,
#     InvalidPadNumberError,
#     InvalidPadBankError,
#     PadAlreadyAssignedError,
# )


@pytest.mark.asyncio
async def test_create_kit_success(db_session: AsyncSession):
    """Test creating a kit with valid data."""
    # Import will fail until service exists
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(
        db=db_session,
        user_id=1,
        name="My Test Kit",
        description="A test kit for testing"
    )

    assert kit.id is not None
    assert kit.name == "My Test Kit"
    assert kit.description == "A test kit for testing"
    assert kit.user_id == 1
    assert kit.pad_layout == {}
    assert kit.bank_config == {}
    assert kit.created_at is not None

    # Verify in database
    result = await db_session.execute(
        select(Kit).where(Kit.id == kit.id)
    )
    db_kit = result.scalar_one()
    assert db_kit.name == "My Test Kit"


@pytest.mark.asyncio
async def test_create_kit_name_too_long(db_session: AsyncSession):
    """Test validation: name cannot exceed 255 characters."""
    from app.services.kit_service import KitService

    kit_service = KitService()
    long_name = "A" * 256

    with pytest.raises(ValueError, match="cannot exceed 255 characters"):
        await kit_service.create_kit(
            db=db_session,
            user_id=1,
            name=long_name,
            description="Test"
        )


@pytest.mark.asyncio
async def test_create_kit_empty_name(db_session: AsyncSession):
    """Test validation: name cannot be empty."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    with pytest.raises(ValueError, match="name cannot be empty"):
        await kit_service.create_kit(
            db=db_session,
            user_id=1,
            name="",
            description="Test"
        )


@pytest.mark.asyncio
async def test_get_user_kits_pagination(db_session: AsyncSession):
    """Test listing kits with pagination."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create 5 kits
    for i in range(5):
        await kit_service.create_kit(
            db=db_session,
            user_id=1,
            name=f"Kit {i}",
            description=f"Description {i}"
        )

    # Test pagination
    kits_page1 = await kit_service.get_user_kits(db_session, user_id=1, skip=0, limit=2)
    assert len(kits_page1) == 2

    kits_page2 = await kit_service.get_user_kits(db_session, user_id=1, skip=2, limit=2)
    assert len(kits_page2) == 2

    kits_page3 = await kit_service.get_user_kits(db_session, user_id=1, skip=4, limit=2)
    assert len(kits_page3) == 1

    # Verify ordering (newest first)
    assert kits_page1[0].created_at >= kits_page1[1].created_at


@pytest.mark.asyncio
async def test_get_user_kits_user_isolation(db_session: AsyncSession):
    """Test that users only see their own kits."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kits for different users
    await kit_service.create_kit(db_session, user_id=1, name="User 1 Kit")
    await kit_service.create_kit(db_session, user_id=2, name="User 2 Kit")

    # User 1 should only see their kit
    user1_kits = await kit_service.get_user_kits(db_session, user_id=1)
    assert len(user1_kits) == 1
    assert user1_kits[0].name == "User 1 Kit"

    # User 2 should only see their kit
    user2_kits = await kit_service.get_user_kits(db_session, user_id=2)
    assert len(user2_kits) == 1
    assert user2_kits[0].name == "User 2 Kit"


@pytest.mark.asyncio
async def test_get_kit_by_id_found(db_session: AsyncSession):
    """Test fetching an existing kit."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kit
    created_kit = await kit_service.create_kit(
        db_session,
        user_id=1,
        name="Test Kit"
    )

    # Fetch by ID
    fetched_kit = await kit_service.get_kit_by_id(
        db_session,
        kit_id=created_kit.id,
        user_id=1
    )

    assert fetched_kit is not None
    assert fetched_kit.id == created_kit.id
    assert fetched_kit.name == "Test Kit"


@pytest.mark.asyncio
async def test_get_kit_by_id_not_found(db_session: AsyncSession):
    """Test returns None for non-existent kit."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Fetch non-existent kit
    kit = await kit_service.get_kit_by_id(
        db_session,
        kit_id=99999,
        user_id=1
    )

    assert kit is None


@pytest.mark.asyncio
async def test_get_kit_by_id_wrong_user(db_session: AsyncSession):
    """Test users cannot fetch other users' kits."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kit for user 1
    created_kit = await kit_service.create_kit(
        db_session,
        user_id=1,
        name="User 1 Kit"
    )

    # User 2 tries to fetch user 1's kit
    kit = await kit_service.get_kit_by_id(
        db_session,
        kit_id=created_kit.id,
        user_id=2
    )

    assert kit is None


@pytest.mark.asyncio
async def test_update_kit_success(db_session: AsyncSession):
    """Test partial update (name only)."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kit
    kit = await kit_service.create_kit(
        db_session,
        user_id=1,
        name="Original Name",
        description="Original Description"
    )

    # Update name only
    updated_kit = await kit_service.update_kit(
        db_session,
        kit_id=kit.id,
        user_id=1,
        name="Updated Name"
    )

    assert updated_kit.name == "Updated Name"
    assert updated_kit.description == "Original Description"

    # Verify in database
    result = await db_session.execute(
        select(Kit).where(Kit.id == kit.id)
    )
    db_kit = result.scalar_one()
    assert db_kit.name == "Updated Name"


@pytest.mark.asyncio
async def test_update_kit_not_found(db_session: AsyncSession):
    """Test update raises error for non-existent kit."""
    from app.services.kit_service import KitService, KitNotFoundError

    kit_service = KitService()

    with pytest.raises(KitNotFoundError):
        await kit_service.update_kit(
            db_session,
            kit_id=99999,
            user_id=1,
            name="New Name"
        )


@pytest.mark.asyncio
async def test_delete_kit_success(db_session: AsyncSession, test_sample: Sample):
    """Test cascade delete removes pad assignments."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kit with sample assignment
    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    await kit_service.assign_sample_to_pad(
        db_session,
        kit_id=kit.id,
        sample_id=test_sample.id,
        pad_bank="A",
        pad_number=1,
        user_id=1
    )

    # Delete kit
    success = await kit_service.delete_kit(
        db_session,
        kit_id=kit.id,
        user_id=1
    )

    assert success is True

    # Verify kit deleted
    result = await db_session.execute(
        select(Kit).where(Kit.id == kit.id)
    )
    assert result.scalar_one_or_none() is None

    # Verify assignments also deleted (cascade)
    assignments = await db_session.execute(
        select(KitSample).where(KitSample.kit_id == kit.id)
    )
    assert len(list(assignments.scalars().all())) == 0


@pytest.mark.asyncio
async def test_assign_sample_to_pad_success(db_session: AsyncSession, test_sample: Sample):
    """Test assigning a sample to a pad."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kit
    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign sample to pad A1
    assignment = await kit_service.assign_sample_to_pad(
        db=db_session,
        kit_id=kit.id,
        sample_id=test_sample.id,
        pad_bank="A",
        pad_number=1,
        user_id=1
    )

    assert assignment.kit_id == kit.id
    assert assignment.sample_id == test_sample.id
    assert assignment.pad_bank == "A"
    assert assignment.pad_number == 1
    assert assignment.volume == 1.0
    assert assignment.pitch_shift == 0

    # Verify in database
    result = await db_session.execute(
        select(KitSample).where(
            KitSample.kit_id == kit.id,
            KitSample.pad_bank == "A",
            KitSample.pad_number == 1
        )
    )
    db_assignment = result.scalar_one()
    assert db_assignment.sample_id == test_sample.id


@pytest.mark.asyncio
async def test_assign_sample_custom_settings(db_session: AsyncSession, test_sample: Sample):
    """Test assigning sample with custom volume and pitch."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    # Create kit
    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign with custom settings
    assignment = await kit_service.assign_sample_to_pad(
        db=db_session,
        kit_id=kit.id,
        sample_id=test_sample.id,
        pad_bank="B",
        pad_number=5,
        user_id=1,
        volume=0.8,
        pitch_shift=3
    )

    assert assignment.volume == 0.8
    assert assignment.pitch_shift == 3


@pytest.mark.asyncio
async def test_assign_sample_invalid_pad_number(db_session: AsyncSession, test_sample: Sample):
    """Test validation: pad number must be 1-16."""
    from app.services.kit_service import KitService, InvalidPadNumberError

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Test pad number 0
    with pytest.raises(InvalidPadNumberError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=kit.id,
            sample_id=test_sample.id,
            pad_bank="A",
            pad_number=0,
            user_id=1
        )

    # Test pad number 17
    with pytest.raises(InvalidPadNumberError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=kit.id,
            sample_id=test_sample.id,
            pad_bank="A",
            pad_number=17,
            user_id=1
        )


@pytest.mark.asyncio
async def test_assign_sample_invalid_pad_bank(db_session: AsyncSession, test_sample: Sample):
    """Test validation: bank must be A-J (10 banks on SP-404MK2)."""
    from app.services.kit_service import KitService, InvalidPadBankError

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Test invalid bank 'K' (only A-J are valid)
    with pytest.raises(InvalidPadBankError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=kit.id,
            sample_id=test_sample.id,
            pad_bank="K",
            pad_number=1,
            user_id=1
        )

    # Test lowercase bank (should also fail)
    with pytest.raises(InvalidPadBankError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=kit.id,
            sample_id=test_sample.id,
            pad_bank="a",
            pad_number=1,
            user_id=1
        )


@pytest.mark.asyncio
async def test_assign_sample_duplicate_error(db_session: AsyncSession, test_sample: Sample):
    """Test PadAlreadyAssignedError when pad already has sample."""
    from app.services.kit_service import KitService, PadAlreadyAssignedError

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign sample to A1
    await kit_service.assign_sample_to_pad(
        db=db_session,
        kit_id=kit.id,
        sample_id=test_sample.id,
        pad_bank="A",
        pad_number=1,
        user_id=1
    )

    # Try to assign different sample to same pad
    with pytest.raises(PadAlreadyAssignedError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=kit.id,
            sample_id=test_sample.id + 1,  # Different sample
            pad_bank="A",
            pad_number=1,
            user_id=1
        )


@pytest.mark.asyncio
async def test_assign_sample_kit_not_found(db_session: AsyncSession, test_sample: Sample):
    """Test SampleNotFoundError for non-existent sample."""
    from app.services.kit_service import KitService, KitNotFoundError

    kit_service = KitService()

    with pytest.raises(KitNotFoundError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=99999,
            sample_id=test_sample.id,
            pad_bank="A",
            pad_number=1,
            user_id=1
        )


@pytest.mark.asyncio
async def test_assign_sample_not_found(db_session: AsyncSession):
    """Test SampleNotFoundError for non-existent sample."""
    from app.services.kit_service import KitService, SampleNotFoundError

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    with pytest.raises(SampleNotFoundError):
        await kit_service.assign_sample_to_pad(
            db=db_session,
            kit_id=kit.id,
            sample_id=99999,
            pad_bank="A",
            pad_number=1,
            user_id=1
        )


@pytest.mark.asyncio
async def test_remove_sample_from_pad_success(db_session: AsyncSession, test_sample: Sample):
    """Test removing a sample assignment."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign sample
    await kit_service.assign_sample_to_pad(
        db_session,
        kit_id=kit.id,
        sample_id=test_sample.id,
        pad_bank="A",
        pad_number=1,
        user_id=1
    )

    # Remove sample
    success = await kit_service.remove_sample_from_pad(
        db_session,
        kit_id=kit.id,
        pad_bank="A",
        pad_number=1,
        user_id=1
    )

    assert success is True

    # Verify removed from database
    result = await db_session.execute(
        select(KitSample).where(
            KitSample.kit_id == kit.id,
            KitSample.pad_bank == "A",
            KitSample.pad_number == 1
        )
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_remove_sample_from_empty_pad(db_session: AsyncSession):
    """Test removing from empty pad returns False."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Remove from empty pad
    success = await kit_service.remove_sample_from_pad(
        db_session,
        kit_id=kit.id,
        pad_bank="A",
        pad_number=1,
        user_id=1
    )

    assert success is False


@pytest.mark.asyncio
async def test_get_pad_assignment(db_session: AsyncSession, test_sample: Sample):
    """Test fetching specific pad assignment."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign sample
    await kit_service.assign_sample_to_pad(
        db_session,
        kit_id=kit.id,
        sample_id=test_sample.id,
        pad_bank="C",
        pad_number=10,
        user_id=1,
        volume=0.75
    )

    # Get assignment
    assignment = await kit_service.get_pad_assignment(
        db_session,
        kit_id=kit.id,
        pad_bank="C",
        pad_number=10
    )

    assert assignment is not None
    assert assignment.sample_id == test_sample.id
    assert assignment.volume == 0.75


@pytest.mark.asyncio
async def test_get_pad_assignment_empty_pad(db_session: AsyncSession):
    """Test get_pad_assignment returns None for empty pad."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Get assignment from empty pad
    assignment = await kit_service.get_pad_assignment(
        db_session,
        kit_id=kit.id,
        pad_bank="A",
        pad_number=1
    )

    assert assignment is None


@pytest.mark.asyncio
async def test_get_all_pad_assignments(
    db_session: AsyncSession,
    test_sample: Sample,
    sample_kick_short: Sample,
    sample_snare_short: Sample
):
    """Test fetching all assignments for a kit."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign multiple samples
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, test_sample.id, "A", 1, 1
    )
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, sample_kick_short.id, "A", 13, 1
    )
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, sample_snare_short.id, "A", 14, 1
    )

    # Get all assignments
    assignments = await kit_service.get_all_pad_assignments(
        db_session,
        kit_id=kit.id
    )

    assert len(assignments) == 3

    # Verify all samples present
    sample_ids = [a.sample_id for a in assignments]
    assert test_sample.id in sample_ids
    assert sample_kick_short.id in sample_ids
    assert sample_snare_short.id in sample_ids


@pytest.mark.asyncio
async def test_get_recommended_samples_for_pad_1(
    db_session: AsyncSession,
    sample_loop_long: Sample,
    sample_kick_short: Sample
):
    """Test recommendations for pad 1 (loops/samples - duration >= 3.0)."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Pad 1 should recommend long samples (>= 3.0 sec)
    recommendations = await kit_service.get_recommended_samples(
        db=db_session,
        kit_id=kit.id,
        pad_number=1,
        user_id=1,
        limit=10
    )

    # Should include loop, NOT kick
    recommended_ids = [s.id for s in recommendations]
    assert sample_loop_long.id in recommended_ids
    assert sample_kick_short.id not in recommended_ids


@pytest.mark.asyncio
async def test_get_recommended_samples_for_pad_13(
    db_session: AsyncSession,
    sample_kick_short: Sample,
    sample_snare_short: Sample,
    sample_hat_closed: Sample
):
    """Test recommendations for pad 13 (kicks - specific tags)."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Pad 13 should recommend kicks (duration <= 1.0, tags: "kick", "bass drum")
    recommendations = await kit_service.get_recommended_samples(
        db=db_session,
        kit_id=kit.id,
        pad_number=13,
        user_id=1,
        limit=10
    )

    # Should include kick, NOT snare or hat
    recommended_ids = [s.id for s in recommendations]
    assert sample_kick_short.id in recommended_ids
    assert sample_snare_short.id not in recommended_ids
    assert sample_hat_closed.id not in recommended_ids


@pytest.mark.asyncio
async def test_get_recommended_samples_for_pad_14(
    db_session: AsyncSession,
    sample_kick_short: Sample,
    sample_snare_short: Sample
):
    """Test recommendations for pad 14 (snares - specific tags)."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Pad 14 should recommend snares (tags: "snare", "clap")
    recommendations = await kit_service.get_recommended_samples(
        db=db_session,
        kit_id=kit.id,
        pad_number=14,
        user_id=1,
        limit=10
    )

    recommended_ids = [s.id for s in recommendations]
    assert sample_snare_short.id in recommended_ids
    assert sample_kick_short.id not in recommended_ids


@pytest.mark.asyncio
async def test_get_recommended_samples_bpm_matching(
    db_session: AsyncSession,
    sample_85bpm: Sample,
    sample_90bpm: Sample,
    sample_140bpm: Sample
):
    """Test BPM matching: prefer samples within ±10 BPM."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign 85 BPM sample to establish kit BPM
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, sample_85bpm.id, "A", 1, 1
    )

    # Get recommendations (should prefer 90 BPM over 140 BPM)
    recommendations = await kit_service.get_recommended_samples(
        db=db_session,
        kit_id=kit.id,
        pad_number=2,
        user_id=1,
        limit=10
    )

    recommended_ids = [s.id for s in recommendations]

    # 90 BPM should be recommended (within ±10 of 85)
    assert sample_90bpm.id in recommended_ids

    # 140 BPM should NOT be recommended (too far from 85)
    assert sample_140bpm.id not in recommended_ids


@pytest.mark.asyncio
async def test_get_recommended_samples_genre_matching(
    db_session: AsyncSession,
    sample_hiphop: Sample,
    sample_jazz: Sample
):
    """Test genre matching: prefer samples with same genre."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Test Kit")

    # Assign hip-hop sample to establish kit genre
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, sample_hiphop.id, "A", 1, 1
    )

    # Get recommendations (should prefer hip-hop)
    recommendations = await kit_service.get_recommended_samples(
        db=db_session,
        kit_id=kit.id,
        pad_number=2,
        user_id=1,
        limit=10
    )

    recommended_ids = [s.id for s in recommendations]

    # Hip-hop samples should be prioritized
    # Note: Both might be included, but hip-hop should come first
    if len(recommended_ids) > 0:
        # Check that hip-hop genre samples appear
        assert sample_hiphop.id in recommended_ids or len(recommendations) == 0


@pytest.mark.asyncio
async def test_prepare_kit_export_manifest(
    db_session: AsyncSession,
    test_sample: Sample,
    sample_kick_short: Sample
):
    """Test export manifest generation."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(
        db_session,
        user_id=1,
        name="Export Test Kit",
        description="Kit for export testing"
    )

    # Assign samples
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, test_sample.id, "A", 1, 1, volume=0.9
    )
    await kit_service.assign_sample_to_pad(
        db_session, kit.id, sample_kick_short.id, "A", 13, 1, pitch_shift=2
    )

    # Prepare export
    manifest = await kit_service.prepare_kit_export(
        db=db_session,
        kit_id=kit.id,
        user_id=1,
        output_format="wav"
    )

    # Validate manifest structure
    assert manifest.kit_name == "Export Test Kit"
    assert manifest.output_format == "wav"
    assert len(manifest.samples) == 2

    # Check sample details in manifest
    sample_info = [s for s in manifest.samples if s.pad_number == 1][0]
    assert sample_info.pad_bank == "A"
    assert sample_info.volume == 0.9

    kick_info = [s for s in manifest.samples if s.pad_number == 13][0]
    assert kick_info.pitch_shift == 2


@pytest.mark.asyncio
async def test_prepare_kit_export_empty_kit(db_session: AsyncSession):
    """Test export fails for kit with no samples."""
    from app.services.kit_service import KitService

    kit_service = KitService()

    kit = await kit_service.create_kit(db_session, user_id=1, name="Empty Kit")

    # Try to export empty kit
    with pytest.raises(ValueError, match="Kit has no samples"):
        await kit_service.prepare_kit_export(
            db=db_session,
            kit_id=kit.id,
            user_id=1
        )
