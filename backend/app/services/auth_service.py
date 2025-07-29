"""
Authentication service implementation
Following TDD - implementing just enough to pass the tests
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password, create_token, decode_token
from app.core.config import settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Check if email already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing_username.scalar_one_or_none():
            raise ValueError("Username already taken")
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_access_token(self, user_id: int) -> str:
        """Create a JWT access token."""
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_token(
            subject=user_id,
            token_type="access",
            expires_delta=expires_delta
        )
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create a JWT refresh token with longer expiry."""
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return create_token(
            subject=user_id,
            token_type="refresh",
            expires_delta=expires_delta
        )
    
    async def verify_token(self, token: str) -> int:
        """Verify a token and return the user ID."""
        try:
            payload = decode_token(token)
            user_id = int(payload["sub"])
            return user_id
        except (ValueError, KeyError, JWTError) as e:
            if "expired" in str(e).lower():
                raise ValueError("Token has expired")
            raise ValueError("Invalid token")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()