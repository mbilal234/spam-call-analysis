#!/usr/bin/env python3
"""
Test script to check actual phone numbers using the API.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_phone_number(phone_number):
    """Test checking a specific phone number."""
    print(f"\n🔍 Testing phone number: {phone_number}")
    print("=" * 50)
    
    # Prepare the request
    payload = {
        "phone_number": phone_number,
        "providers": ["hiya"],
        "timeout": 60  # Give it more time for the first check
    }
    
    print("📤 Sending request to API...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minute timeout for the request
        )
        
        end_time = time.time()
        request_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Check completed in {request_time:.2f} seconds!")
            print(f"\n📊 Results:")
            print(f"   Phone Number: {result['phone_number']}")
            print(f"   Overall Status: {result['overall_status']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Total Response Time: {result['total_response_time']:.2f}s")
            print(f"   Timestamp: {result['timestamp']}")
            
            # Show provider-specific results
            print(f"\n🔍 Provider Details:")
            for provider in result['providers']:
                print(f"   {provider['provider'].upper()}:")
                print(f"     Status: {provider['status']}")
                print(f"     Confidence: {provider['confidence']:.2f}")
                print(f"     Response Time: {provider['response_time']:.2f}s")
                if provider.get('error_message'):
                    print(f"     Error: {provider['error_message']}")
                if provider.get('raw_data'):
                    print(f"     Raw Data: {provider['raw_data']}")
            
            return result
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏰ Request timed out after 120 seconds")
        return None
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

def test_multiple_numbers():
    """Test multiple phone numbers."""
    test_numbers = [
        "+1234567890",  # Test number
        "+1987654321",  # Another test number
        "+1555123456",  # Another test number
    ]
    
    print("🚀 Testing Multiple Phone Numbers")
    print("=" * 50)
    
    results = []
    for number in test_numbers:
        result = test_phone_number(number)
        if result:
            results.append(result)
        time.sleep(2)  # Wait between requests
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"   Total Numbers Tested: {len(test_numbers)}")
    print(f"   Successful Checks: {len(results)}")
    
    if results:
        status_counts = {}
        for result in results:
            status = result['overall_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"   Status Distribution:")
        for status, count in status_counts.items():
            print(f"     {status}: {count}")

def check_api_status():
    """Check if API is running and healthy."""
    print("🔍 Checking API Status...")
    
    try:
        # Check health
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is healthy: {health['status']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the API server is running with: python api_server.py")
        return False

def main():
    """Main test function."""
    print("📱 Spam Call Analysis API - Phone Number Test")
    print("=" * 60)
    
    # Check API status first
    if not check_api_status():
        return
    
    # Test single number
    print("\n" + "="*60)
    print("🧪 SINGLE NUMBER TEST")
    print("="*60)
    
    # You can change this number to test different ones
    test_number = "+1234567890"
    result = test_phone_number(test_number)
    
    if result:
        print(f"\n🎉 Single number test completed successfully!")
        
        # Ask if user wants to test more numbers
        print(f"\n" + "="*60)
        print("🧪 MULTIPLE NUMBERS TEST")
        print("="*60)
        test_multiple_numbers()
    else:
        print(f"\n💥 Single number test failed!")

if __name__ == "__main__":
    main()
