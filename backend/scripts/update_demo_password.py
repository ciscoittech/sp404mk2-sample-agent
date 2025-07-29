#!/usr/bin/env python3
"""Update demo user password"""
import asyncio
import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def update_password():
    """Update demo user password"""
    async with AsyncSessionLocal() as db:
        # Hash the password
        hashed = pwd_context.hash("demo123")
        
        # Update the user
        await db.execute(
            text("UPDATE users SET hashed_password = :password WHERE email = 'demo@example.com'"),
            {"password": hashed}
        )
        await db.commit()
        print("✅ Updated demo user password to 'demo123'")

if __name__ == "__main__":
    asyncio.run(update_password())