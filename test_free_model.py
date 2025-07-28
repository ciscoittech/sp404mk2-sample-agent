#!/usr/bin/env python3
"""
Test script to verify the free qwen model works correctly.
Tests rate limiting and basic functionality.
"""

import asyncio
import os
from datetime import datetime
import httpx
from dotenv import load_dotenv
from src.config import settings

# Load environment
load_dotenv()

async def test_free_model():
    """Test the free qwen model with a simple prompt."""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    print(f"🔧 Testing model: {settings.collector_model}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Simple test prompt
    prompt = "Analyze this sample name and suggest a vibe: 'Adrian Younge Presents Venice Dawn.wav'"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/bhunt/sp404mk2-sample-agent",
        "X-Title": "SP404MK2 Sample Agent Test"
    }
    
    data = {
        "model": settings.collector_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 200
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("📡 Sending request to OpenRouter...")
            
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ Success! Model responded:\n")
                print(f"📝 {content}")
                return True
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        return False

async def test_rate_limits():
    """Test the 5 RPM rate limit."""
    print("\n🔄 Testing rate limits (5 requests per minute)...")
    
    results = []
    for i in range(6):  # Try 6 requests to hit the limit
        print(f"\n📨 Request {i+1}/6 at {datetime.now().strftime('%H:%M:%S')}")
        success = await test_free_model()
        results.append(success)
        
        if i < 5:  # Don't wait after last request
            print("⏳ Waiting 12 seconds before next request...")
            await asyncio.sleep(12)  # 5 requests per 60 seconds = 12 seconds between
    
    successful = sum(results)
    print(f"\n📊 Results: {successful}/6 requests successful")
    
    if successful >= 5:
        print("✅ Rate limiting working correctly!")
    else:
        print("⚠️  Some requests failed - check API key and model availability")

if __name__ == "__main__":
    print("🧪 SP404MK2 Sample Agent - Free Model Test")
    print("=" * 50)
    
    # Run single test
    asyncio.run(test_free_model())
    
    # Uncomment to test rate limits (takes ~1 minute)
    # asyncio.run(test_rate_limits())