#!/usr/bin/env python3
"""
Test script for the Spam Call Analysis API.
Tests the API endpoints and functionality.
"""

import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_providers():
    """Test the providers endpoint."""
    print("\nTesting providers endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/providers")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Providers endpoint: {data['providers']}")
            return True
        else:
            print(f"✗ Providers endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Providers endpoint error: {e}")
        return False

def test_single_check():
    """Test checking a single phone number."""
    print("\nTesting single number check...")
    try:
        payload = {
            "phone_number": "+1234567890",
            "providers": ["hiya"],
            "timeout": 30
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Single check passed:")
            print(f"  Phone: {data['phone_number']}")
            print(f"  Status: {data['overall_status']}")
            print(f"  Confidence: {data['confidence']}")
            print(f"  Response time: {data['total_response_time']:.2f}s")
            return True
        else:
            print(f"✗ Single check failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Single check error: {e}")
        return False

def test_batch_check():
    """Test batch checking multiple phone numbers."""
    print("\nTesting batch check...")
    try:
        payload = {
            "requests": [
                {"phone_number": "+1234567890", "providers": ["hiya"]},
                {"phone_number": "+1987654321", "providers": ["hiya"]}
            ]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Batch check started:")
            print(f"  Task ID: {data['task_id']}")
            print(f"  Numbers: {data['numbers_count']}")
            return data['task_id']
        else:
            print(f"✗ Batch check failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Batch check error: {e}")
        return None

def test_batch_status(task_id):
    """Test checking batch status."""
    if not task_id:
        return False
        
    print(f"\nTesting batch status for task {task_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/batch/{task_id}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Batch status:")
            print(f"  Status: {data['status']}")
            print(f"  Processed: {data['processed_numbers']}/{data['total_numbers']}")
            print(f"  Successful: {data['successful_checks']}")
            print(f"  Failed: {data['failed_checks']}")
            return True
        else:
            print(f"✗ Batch status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Batch status error: {e}")
        return False

def main():
    """Run all tests."""
    print("Spam Call Analysis API - Test Suite")
    print("=" * 50)
    
    # Test basic endpoints
    health_ok = test_health()
    providers_ok = test_providers()
    
    if not health_ok or not providers_ok:
        print("\n❌ Basic tests failed. Make sure the API server is running.")
        sys.exit(1)
    
    # Test single number check
    single_ok = test_single_check()
    
    # Test batch check
    task_id = test_batch_check()
    if task_id:
        # Wait a bit and check status
        time.sleep(2)
        test_batch_status(task_id)
    
    print("\n" + "=" * 50)
    if health_ok and providers_ok and single_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
