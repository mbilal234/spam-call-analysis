#!/usr/bin/env python3
"""
Test script using the mock provider to demonstrate API functionality.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_mock_provider():
    """Test the API using the mock provider."""
    print("🧪 Testing API with Mock Provider")
    print("=" * 50)
    
    # Test different phone numbers
    test_numbers = [
        "+1234567000",  # Should be blocked (ends with 0000)
        "+1234567111",  # Should be caution (ends with 1111)
        "+1234567890",  # Should be allowed (starts with +1)
        "+44123456789", # Random result
        "+33123456789", # Random result
    ]
    
    for number in test_numbers:
        print(f"\n🔍 Testing: {number}")
        print("-" * 30)
        
        payload = {
            "phone_number": number,
            "providers": ["mock"],  # Use mock provider
            "timeout": 30
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/v1/check",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result['overall_status']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Response Time: {end_time - start_time:.2f}s")
                
                for provider in result['providers']:
                    print(f"   {provider['provider']}: {provider['status']} ({provider['confidence']:.2f})")
                    if provider.get('raw_data', {}).get('simulated'):
                        print(f"   📝 Mock data: {provider['raw_data']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"💥 Error: {e}")

def test_batch_mock():
    """Test batch processing with mock provider."""
    print(f"\n🚀 Testing Batch Processing with Mock Provider")
    print("=" * 50)
    
    payload = {
        "requests": [
            {"phone_number": "+1234567000", "providers": ["mock"]},
            {"phone_number": "+1234567111", "providers": ["mock"]},
            {"phone_number": "+1234567890", "providers": ["mock"]},
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check/batch",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            batch_info = response.json()
            print(f"✅ Batch started: {batch_info['task_id']}")
            print(f"   Numbers: {batch_info['numbers_count']}")
            
            # Wait and check status
            time.sleep(3)
            status_response = requests.get(f"{API_BASE_URL}/api/v1/batch/{batch_info['task_id']}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   Status: {status['status']}")
                print(f"   Processed: {status['processed_numbers']}/{status['total_numbers']}")
        else:
            print(f"❌ Batch failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def test_available_providers():
    """Test getting available providers."""
    print(f"\n📋 Available Providers")
    print("=" * 30)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/providers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Providers: {data['providers']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"💥 Error: {e}")

def main():
    """Main test function."""
    print("📱 Spam Call Analysis API - Mock Provider Test")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running")
            return
    except:
        print("❌ Cannot connect to API server")
        print("   Start it with: python api_server.py")
        return
    
    print("✅ API server is running")
    
    # Test available providers
    test_available_providers()
    
    # Test mock provider
    test_mock_provider()
    
    # Test batch processing
    test_batch_mock()
    
    print(f"\n🎉 Mock provider tests completed!")

if __name__ == "__main__":
    main()
