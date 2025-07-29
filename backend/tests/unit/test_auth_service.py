"""
TDD: Authentication Service Tests
Written BEFORE implementation following TDD approach
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, Token
from app.core.security import verify_password


class TestAuthService:
    """Test cases for authentication service."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session):
        """Test creating a new user with hashed password."""
        # Arrange
        auth_service = AuthService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!"
        )
        
        # Act
        user = await auth_service.create_user(user_data)
        
        # Assert
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.id is not None
        assert user.hashed_password != "SecurePass123!"  # Password should be hashed
        assert verify_password("SecurePass123!", user.hashed_password)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session):
        """Test that duplicate emails are rejected."""
        # Arrange
        auth_service = AuthService(db_session)
        user_data = UserCreate(
            email="duplicate@example.com",
            username="user1",
            password="password123"
        )
        
        # Create first user
        await auth_service.create_user(user_data)
        
        # Act & Assert - Try to create user with same email
        user_data2 = UserCreate(
            email="duplicate@example.com",
            username="user2",
            password="password123"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.create_user(user_data2)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session):
        """Test successful user authentication."""
        # Arrange
        auth_service = AuthService(db_session)
        
        # Create a user first
        user_data = UserCreate(
            email="auth@example.com",
            username="authuser",
            password="MyPassword123"
        )
        created_user = await auth_service.create_user(user_data)
        
        # Act
        authenticated_user = await auth_service.authenticate_user(
            email="auth@example.com",
            password="MyPassword123"
        )
        
        # Assert
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == "auth@example.com"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session):
        """Test authentication fails with wrong password."""
        # Arrange
        auth_service = AuthService(db_session)
        
        # Create a user
        user_data = UserCreate(
            email="wrong@example.com",
            username="wronguser",
            password="CorrectPassword"
        )
        await auth_service.create_user(user_data)
        
        # Act
        result = await auth_service.authenticate_user(
            email="wrong@example.com",
            password="WrongPassword"
        )
        
        # Assert
        assert result is None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_access_token(self):
        """Test JWT access token creation."""
        # Arrange
        auth_service = AuthService(None)  # No DB needed for token creation
        user_id = 123
        
        # Act
        token = auth_service.create_access_token(user_id=user_id)
        
        # Assert
        assert isinstance(token, str)
        
        # Decode and verify token (without verification for test)
        payload = jwt.decode(
            token,
            auth_service.secret_key,
            algorithms=[auth_service.algorithm],
            options={"verify_exp": False}
        )
        assert payload["sub"] == str(user_id)
        assert "exp" in payload
        
        # Check expiration is in future (convert to UTC for comparison)
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        assert exp_datetime > datetime.now(timezone.utc)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_refresh_token(self):
        """Test refresh token creation with longer expiry."""
        # Arrange
        auth_service = AuthService(None)
        user_id = 456
        
        # Act
        refresh_token = auth_service.create_refresh_token(user_id=user_id)
        
        # Assert
        payload = jwt.decode(
            refresh_token,
            auth_service.secret_key,
            algorithms=[auth_service.algorithm],
            options={"verify_exp": False}
        )
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        
        # Refresh token should have longer expiry
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        assert exp_datetime > datetime.now(timezone.utc) + timedelta(days=6)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_valid(self):
        """Test verifying a valid token."""
        # Arrange
        auth_service = AuthService(None)
        user_id = 789
        token = auth_service.create_access_token(user_id=user_id)
        
        # Act
        verified_user_id = await auth_service.verify_token(token)
        
        # Assert
        assert verified_user_id == user_id
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_expired(self):
        """Test verifying an expired token."""
        # Arrange
        auth_service = AuthService(None)
        
        # Create an expired token
        payload = {
            "sub": "123",
            "exp": datetime.now() - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(
            payload,
            auth_service.secret_key,
            algorithm=auth_service.algorithm
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Token has expired"):
            await auth_service.verify_token(expired_token)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self):
        """Test verifying an invalid token."""
        # Arrange
        auth_service = AuthService(None)
        invalid_token = "invalid.jwt.token"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid token"):
            await auth_service.verify_token(invalid_token)