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

        # Verify table exists using SQLAlchemy inspector (cross-database compatible)
        from sqlalchemy import inspect
        inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
        table_names = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

        if 'batches' in table_names:
            print("✅ Verified: 'batches' table exists")
        else:
            print("❌ Error: 'batches' table was not created")


if __name__ == "__main__":
    asyncio.run(create_batch_table())