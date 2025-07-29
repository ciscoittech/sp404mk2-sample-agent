"""
Add batch processing table to database
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine
from app.db.base import Base
from app.models.batch import Batch


async def create_batch_table():
    """Create batch table if it doesn't exist"""
    async with engine.begin() as conn:
        # Create table
        await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Batch table created successfully")
        
        # Verify table exists
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='batches';")
        )
        table_exists = result.fetchone()
        
        if table_exists:
            print("✅ Verified: 'batches' table exists")
        else:
            print("❌ Error: 'batches' table was not created")


if __name__ == "__main__":
    asyncio.run(create_batch_table())