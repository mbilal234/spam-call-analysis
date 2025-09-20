#!/usr/bin/env python3
"""
Test script specifically for the Hiya provider.
This script tests the Hiya provider with real Android automation.
"""

import asyncio
import json
import time
import requests
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"
HIYA_PROVIDER = "hiya"

def test_api_connection():
    """Test if the API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False

def test_providers():
    """Test the providers endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/providers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"📋 Available providers: {providers}")
            if HIYA_PROVIDER in providers:
                print(f"✅ Hiya provider is available")
                return True
            else:
                print(f"❌ Hiya provider not found in {providers}")
                return False
        else:
            print(f"❌ Providers endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking providers: {e}")
        return False

def test_hiya_single_number(phone_number):
    """Test a single phone number with Hiya provider."""
    print(f"\n🔍 Testing Hiya Provider: {phone_number}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        payload = {
            "phone_number": phone_number,
            "providers": [HIYA_PROVIDER]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check",
            json=payload,
            timeout=120  # 2 minutes timeout for Android automation
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result['overall_status']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Response Time: {response_time:.2f}s")
            
            # Show provider-specific details
            for provider_result in result['providers']:
                print(f"   {provider_result['provider']}: {provider_result['status']} ({provider_result['confidence']})")
                if provider_result.get('error_message'):
                    print(f"   ⚠️  Error: {provider_result['error_message']}")
                if provider_result.get('raw_data'):
                    print(f"   📝 Raw data: {provider_result['raw_data']}")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Request timed out after {response_time:.2f}s")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def test_hiya_batch_numbers(phone_numbers):
    """Test multiple phone numbers with Hiya provider."""
    print(f"\n🚀 Testing Hiya Provider - Batch Processing")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Create list of PhoneNumberRequest objects (direct list, not wrapped)
        requests_list = []
        for phone_number in phone_numbers:
            requests_list.append({
                "phone_number": phone_number,
                "providers": [HIYA_PROVIDER]
            })
        
        payload = requests_list  # Direct list, not wrapped in a dict
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check/batch",
            json=payload,
            timeout=300  # 5 minutes timeout for batch processing
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch processing started in {response_time:.2f}s")
            print(f"   Task ID: {result['task_id']}")
            print(f"   Numbers to process: {result['numbers_count']}")
            print(f"   Status endpoint: {result['status_endpoint']}")
            print(f"   Message: {result['message']}")
            
            # Note: In a real implementation, you would poll the status endpoint
            # to get the actual results when processing is complete
            print(f"   ℹ️  Note: Batch processing is asynchronous. Check status at: {result['status_endpoint']}")
            
            return True
        else:
            print(f"❌ Batch request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Batch request timed out after {response_time:.2f}s")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Batch request error: {e}")
        return False

def main():
    """Main test function."""
    print("📱 Spam Call Analysis API - Hiya Provider Test")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ Cannot proceed without API server")
        return
    
    # Test providers
    if not test_providers():
        print("\n❌ Cannot proceed without Hiya provider")
        return
    
    # Test phone numbers
    test_numbers = [
        "+1234567890",      # US number
        "+1987654321",      # US number
        "+1555123456",      # US number
        "+44123456789",     # UK number
        "+33123456789",     # French number
    ]
    
    print(f"\n🧪 Testing Hiya Provider with {len(test_numbers)} numbers")
    print("=" * 60)
    
    # Test individual numbers
    success_count = 0
    for phone_number in test_numbers:
        if test_hiya_single_number(phone_number):
            success_count += 1
        time.sleep(2)  # Wait between requests
    
    print(f"\n📊 Individual Tests Summary: {success_count}/{len(test_numbers)} successful")
    
    # Test batch processing
    print(f"\n🚀 Testing Batch Processing with Hiya Provider")
    print("=" * 60)
    
    batch_numbers = test_numbers[:3]  # Test with first 3 numbers for batch
    if test_hiya_batch_numbers(batch_numbers):
        print("✅ Batch processing test completed")
    else:
        print("❌ Batch processing test failed")
    
    print(f"\n🎉 Hiya provider tests completed!")
    print(f"   Individual tests: {success_count}/{len(test_numbers)}")
    print(f"   Batch test: {'✅' if test_hiya_batch_numbers(batch_numbers) else '❌'}")

if __name__ == "__main__":
    main()
