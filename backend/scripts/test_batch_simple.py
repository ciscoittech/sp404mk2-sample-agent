#!/usr/bin/env python3
"""Simple batch test"""
import requests
import json

# Test the public batch endpoint
url = "http://localhost:8000/api/v1/public/batch/test"
data = {
    "collection_path": "test_batch_collection",
    "name": "Test Batch", 
    "batch_size": 5,
    "options": {
        "vibe_analysis": True
    }
}

print("Testing batch creation...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 500:
        print("\n⚠️  Server Error - Check server logs for details")
except Exception as e:
    print(f"Error: {e}")