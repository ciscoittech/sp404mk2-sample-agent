"""
Tests for Collections API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.collection import Collection
from app.models.sample import Sample


class TestCollectionAPI:
    """Test collection API endpoints."""

    @pytest.mark.asyncio
    async def test_create_collection(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test creating a new collection."""
        payload = {
            "name": "Test Collection",
            "description": "A test collection",
            "is_smart": False
        }

        response = await async_client.post(
            "/api/v1/collections",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Collection"
        assert data["description"] == "A test collection"
        assert data["is_smart"] is False
        assert data["sample_count"] == 0
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_collections(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test listing collections."""
        # Create test collections
        collection1 = Collection(
            user_id=test_user.id,
            name="Collection 1",
            sample_count=0
        )
        collection2 = Collection(
            user_id=test_user.id,
            name="Collection 2",
            sample_count=0
        )
        db_session.add(collection1)
        db_session.add(collection2)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/collections",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_collection(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting a specific collection."""
        collection = Collection(
            user_id=test_user.id,
            name="Test Collection",
            description="Test description",
            sample_count=0
        )
        db_session.add(collection)
        await db_session.commit()
        await db_session.refresh(collection)

        response = await async_client.get(
            f"/api/v1/collections/{collection.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == collection.id
        assert data["name"] == "Test Collection"
        assert data["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_update_collection(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test updating a collection."""
        collection = Collection(
            user_id=test_user.id,
            name="Original Name",
            sample_count=0
        )
        db_session.add(collection)
        await db_session.commit()
        await db_session.refresh(collection)

        payload = {
            "name": "Updated Name",
            "description": "New description"
        }

        response = await async_client.put(
            f"/api/v1/collections/{collection.id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_delete_collection(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test deleting a collection."""
        collection = Collection(
            user_id=test_user.id,
            name="To Delete",
            sample_count=0
        )
        db_session.add(collection)
        await db_session.commit()
        await db_session.refresh(collection)

        response = await async_client.delete(
            f"/api/v1/collections/{collection.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify it's deleted
        from sqlalchemy import select
        result = await db_session.execute(
            select(Collection).where(Collection.id == collection.id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_add_samples_to_collection(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test adding samples to a collection."""
        # Create collection
        collection = Collection(
            user_id=test_user.id,
            name="Test Collection",
            sample_count=0
        )
        db_session.add(collection)

        # Create samples
        sample1 = Sample(
            user_id=test_user.id,
            title="Sample 1",
            file_path="/test/sample1.wav"
        )
        sample2 = Sample(
            user_id=test_user.id,
            title="Sample 2",
            file_path="/test/sample2.wav"
        )
        db_session.add(sample1)
        db_session.add(sample2)
        await db_session.commit()
        await db_session.refresh(collection)
        await db_session.refresh(sample1)
        await db_session.refresh(sample2)

        payload = {
            "sample_ids": [sample1.id, sample2.id]
        }

        response = await async_client.post(
            f"/api/v1/collections/{collection.id}/samples",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    @pytest.mark.asyncio
    async def test_create_smart_collection(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test creating a smart collection with rules."""
        # Create some test samples
        sample1 = Sample(
            user_id=test_user.id,
            title="Jazz Sample",
            file_path="/test/jazz.wav",
            genre="Jazz",
            bpm=120.0
        )
        sample2 = Sample(
            user_id=test_user.id,
            title="Hip-Hop Sample",
            file_path="/test/hiphop.wav",
            genre="Hip-Hop",
            bpm=90.0
        )
        db_session.add(sample1)
        db_session.add(sample2)
        await db_session.commit()

        # Create smart collection
        payload = {
            "name": "Jazz Samples",
            "description": "All jazz samples",
            "is_smart": True,
            "smart_rules": {
                "genres": ["Jazz"],
                "bpm_min": 100.0,
                "bpm_max": 140.0
            }
        }

        response = await async_client.post(
            "/api/v1/collections",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_smart"] is True
        assert data["smart_rules"]["genres"] == ["Jazz"]
        # Smart collection should auto-evaluate and find 1 matching sample
        assert data["sample_count"] == 1

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test that users can't access other users' collections."""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="other",
            hashed_password="fake_hash"
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create collection for other user
        collection = Collection(
            user_id=other_user.id,
            name="Other User Collection",
            sample_count=0
        )
        db_session.add(collection)
        await db_session.commit()
        await db_session.refresh(collection)

        # Try to access with test_user's token
        response = await async_client.get(
            f"/api/v1/collections/{collection.id}",
            headers=auth_headers
        )

        assert response.status_code == 404  # Not found (user authorization check)
