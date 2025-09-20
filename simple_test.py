#!/usr/bin/env python3
"""
Simple test to check if the API is working.
"""

import requests
import time

def test_api():
    """Test basic API functionality."""
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✓ Root endpoint working")
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health endpoint working: {data.get('status', 'unknown')}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Health endpoint error: {e}")
        return False
    
    # Test providers endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/providers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Providers endpoint working: {data.get('providers', [])}")
        else:
            print(f"✗ Providers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Providers endpoint error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Simple API Test")
    print("=" * 30)
    
    # Wait a moment for API to start
    print("Waiting for API to start...")
    time.sleep(5)
    
    if test_api():
        print("\n✅ API is working!")
    else:
        print("\n❌ API has issues")
