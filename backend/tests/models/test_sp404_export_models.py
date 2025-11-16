"""
Tests for SP-404MK2 Export database models
"""
import pytest
from sqlalchemy import select

from app.models import SP404Export, SP404ExportSample, Sample, User


@pytest.mark.asyncio
async def test_create_sp404_export(db_session, test_user):
    """Test creating export record."""
    export = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/path/to/export",
        organized_by="flat",
        format="wav",
        total_size_bytes=1024000,
        export_duration_seconds=2.5
    )

    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    assert export.id is not None
    assert export.created_at is not None
    assert export.export_type == "single"
    assert export.sample_count == 1
    assert export.output_path == "/path/to/export"
    assert export.organized_by == "flat"
    assert export.format == "wav"
    assert export.total_size_bytes == 1024000
    assert export.export_duration_seconds == 2.5


@pytest.mark.asyncio
async def test_sp404_export_relationships(db_session, test_user):
    """Test exported_samples relationship."""
    # Create export
    export = SP404Export(
        user_id=test_user.id,
        export_type="batch",
        sample_count=2,
        output_path="/path/to/export",
        organized_by="genre",
        format="wav"
    )
    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    # Create sample
    sample = Sample(
        user_id=test_user.id,
        title="Test Sample",
        file_path="/path/to/sample.wav",
        genre="hip-hop"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Create export sample
    export_sample1 = SP404ExportSample(
        export_id=export.id,
        sample_id=sample.id,
        output_filename="test_sample_1.wav",
        conversion_successful=True,
        file_size_bytes=512000,
        conversion_time_seconds=1.2
    )
    export_sample2 = SP404ExportSample(
        export_id=export.id,
        sample_id=sample.id,
        output_filename="test_sample_2.wav",
        conversion_successful=True,
        file_size_bytes=512000,
        conversion_time_seconds=1.3
    )

    db_session.add_all([export_sample1, export_sample2])
    await db_session.commit()

    # Refresh with eager loading
    from sqlalchemy.orm import selectinload
    result = await db_session.execute(
        select(SP404Export)
        .where(SP404Export.id == export.id)
        .options(selectinload(SP404Export.exported_samples))
    )
    export = result.scalar_one()

    # Test relationship
    assert len(export.exported_samples) == 2
    assert export.exported_samples[0].output_filename in ["test_sample_1.wav", "test_sample_2.wav"]
    assert export.exported_samples[0].conversion_successful is True


@pytest.mark.asyncio
async def test_sp404_export_sample_relationship(db_session, test_user):
    """Test SP404ExportSample link to Sample model."""
    # Create sample
    sample = Sample(
        user_id=test_user.id,
        title="Test Sample",
        file_path="/path/to/sample.wav",
        genre="electronic",
        bpm=128.0
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Create export
    export = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/path/to/export",
        organized_by="flat",
        format="wav"
    )
    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    # Create export sample
    export_sample = SP404ExportSample(
        export_id=export.id,
        sample_id=sample.id,
        output_filename="electronic_sample.wav",
        conversion_successful=True
    )
    db_session.add(export_sample)
    await db_session.commit()
    await db_session.refresh(export_sample)

    # Test relationship to Sample
    assert export_sample.sample.id == sample.id
    assert export_sample.sample.title == "Test Sample"
    assert export_sample.sample.genre == "electronic"


@pytest.mark.asyncio
async def test_export_with_user(db_session, test_user):
    """Test User relationship (nullable)."""
    # Create export with user
    export1 = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/path/to/export1",
        organized_by="flat",
        format="wav"
    )
    db_session.add(export1)

    # Create export without user (system export)
    export2 = SP404Export(
        user_id=None,
        export_type="batch",
        sample_count=5,
        output_path="/path/to/export2",
        organized_by="genre",
        format="aiff"
    )
    db_session.add(export2)

    await db_session.commit()
    await db_session.refresh(export1)
    await db_session.refresh(export2)

    # Test user relationship
    assert export1.user.id == test_user.id
    assert export1.user.email == test_user.email
    assert export2.user is None


@pytest.mark.asyncio
async def test_export_cascade_delete(db_session, test_user):
    """Test cascade delete to ExportSample records."""
    # Create sample
    sample = Sample(
        user_id=test_user.id,
        title="Test Sample",
        file_path="/path/to/sample.wav"
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(sample)

    # Create export
    export = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/path/to/export",
        organized_by="flat",
        format="wav"
    )
    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    # Create export samples
    export_sample = SP404ExportSample(
        export_id=export.id,
        sample_id=sample.id,
        output_filename="test.wav",
        conversion_successful=True
    )
    db_session.add(export_sample)
    await db_session.commit()

    export_id = export.id

    # Verify export sample exists
    result = await db_session.execute(
        select(SP404ExportSample).where(SP404ExportSample.export_id == export_id)
    )
    assert result.scalar_one_or_none() is not None

    # Delete export
    await db_session.delete(export)
    await db_session.commit()

    # Verify cascade delete of export samples
    result = await db_session.execute(
        select(SP404ExportSample).where(SP404ExportSample.export_id == export_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_export_timestamps(db_session, test_user):
    """Test created_at auto-populated."""
    export = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/path/to/export",
        organized_by="flat",
        format="wav"
    )
    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    # Verify timestamp is set
    assert export.created_at is not None
    import datetime
    assert isinstance(export.created_at, datetime.datetime)


@pytest.mark.asyncio
async def test_export_query_by_type(db_session, test_user):
    """Test filter by export_type."""
    # Create different export types
    export_single = SP404Export(
        user_id=test_user.id,
        export_type="single",
        sample_count=1,
        output_path="/path/to/single",
        organized_by="flat",
        format="wav"
    )
    export_batch = SP404Export(
        user_id=test_user.id,
        export_type="batch",
        sample_count=10,
        output_path="/path/to/batch",
        organized_by="genre",
        format="wav"
    )
    db_session.add_all([export_single, export_batch])
    await db_session.commit()

    # Query single exports
    result = await db_session.execute(
        select(SP404Export).where(SP404Export.export_type == "single")
    )
    single_exports = result.scalars().all()
    assert len(single_exports) == 1
    assert single_exports[0].sample_count == 1

    # Query batch exports
    result = await db_session.execute(
        select(SP404Export).where(SP404Export.export_type == "batch")
    )
    batch_exports = result.scalars().all()
    assert len(batch_exports) == 1
    assert batch_exports[0].sample_count == 10


@pytest.mark.asyncio
async def test_export_aggregates(db_session, test_user):
    """Test total size and count calculations."""
    # Create export with multiple samples
    export = SP404Export(
        user_id=test_user.id,
        export_type="batch",
        sample_count=3,
        output_path="/path/to/export",
        organized_by="flat",
        format="wav",
        total_size_bytes=0  # Will be calculated
    )
    db_session.add(export)
    await db_session.commit()
    await db_session.refresh(export)

    # Create samples
    sample1 = Sample(user_id=test_user.id, title="Sample 1", file_path="/s1.wav")
    sample2 = Sample(user_id=test_user.id, title="Sample 2", file_path="/s2.wav")
    sample3 = Sample(user_id=test_user.id, title="Sample 3", file_path="/s3.wav")
    db_session.add_all([sample1, sample2, sample3])
    await db_session.commit()

    # Create export samples with sizes
    export_sample1 = SP404ExportSample(
        export_id=export.id,
        sample_id=sample1.id,
        output_filename="s1.wav",
        conversion_successful=True,
        file_size_bytes=1000000
    )
    export_sample2 = SP404ExportSample(
        export_id=export.id,
        sample_id=sample2.id,
        output_filename="s2.wav",
        conversion_successful=True,
        file_size_bytes=2000000
    )
    export_sample3 = SP404ExportSample(
        export_id=export.id,
        sample_id=sample3.id,
        output_filename="s3.wav",
        conversion_successful=True,
        file_size_bytes=1500000
    )
    db_session.add_all([export_sample1, export_sample2, export_sample3])
    await db_session.commit()

    # Refresh with eager loading
    from sqlalchemy.orm import selectinload
    result = await db_session.execute(
        select(SP404Export)
        .where(SP404Export.id == export.id)
        .options(selectinload(SP404Export.exported_samples))
    )
    export = result.scalar_one()

    # Calculate total size
    total_size = sum(es.file_size_bytes for es in export.exported_samples)

    assert total_size == 4500000  # 1M + 2M + 1.5M
    assert len(export.exported_samples) == 3
    assert export.sample_count == 3
