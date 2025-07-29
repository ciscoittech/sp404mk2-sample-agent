#!/usr/bin/env python3
"""Test batch processing directly"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.services.batch_service import BatchService

async def test_batch_processing():
    """Test batch processing directly"""
    async with AsyncSessionLocal() as db:
        batch_service = BatchService(db)
        
        # Create a batch job
        print("Creating batch job...")
        batch = await batch_service.create_batch(
            user_id=2,  # Demo user ID
            collection_path="/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/test_batch_collection",
            options={
                "name": "Test Batch Processing",
                "vibe_analysis": True,
                "batch_size": 5
            }
        )
        
        print(f"✅ Created batch: {batch.id}")
        print(f"   Status: {batch.status}")
        print(f"   Collection: {batch.collection_path}")
        
        # Start processing
        print("\n🚀 Starting batch processing...")
        print("   Note: This will process audio files with AI analysis")
        print("   Rate limiting: 5 samples per call, 12 second intervals")
        
        # Process the batch
        await batch_service.process_batch(batch.id)
        
        # Get final status
        final_batch = await batch_service.get_batch_by_id(batch.id)
        print(f"\n✅ Processing complete!")
        print(f"   Status: {final_batch.status}")
        print(f"   Total samples: {final_batch.total_samples}")
        print(f"   Processed: {final_batch.processed_samples}")
        print(f"   Success: {final_batch.success_count}")
        print(f"   Errors: {final_batch.error_count}")
        
        if final_batch.export_path:
            print(f"   Export: {final_batch.export_path}")

if __name__ == "__main__":
    print("SP404MK2 Batch Processing Test")
    print("=" * 50)
    asyncio.run(test_batch_processing())