"""Test database connection"""
import asyncio
from app.db.base import engine, Base
from app.models import user, sample

async def test_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database tables created successfully")
        
        # Test query
        from app.db.base import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            from app.models.user import User
            
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"✓ Found {len(users)} users in database")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())