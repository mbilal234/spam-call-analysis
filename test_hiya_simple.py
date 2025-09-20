#!/usr/bin/env python3
"""
Simple test script for Hiya provider - tests one phone number with detailed output.
"""

import json
import requests
import time

def test_hiya_provider(phone_number="+1234567890"):
    """Test Hiya provider with a single phone number."""
    
    print(f"📱 Testing Hiya Provider with: {phone_number}")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running. Start it with: python api_server.py")
            return
    except:
        print("❌ Cannot connect to API server. Start it with: python api_server.py")
        return
    
    print("✅ API server is running")
    
    # Test the check endpoint
    payload = {
        "phone_number": phone_number,
        "providers": ["hiya"]
    }
    
    print(f"📤 Sending request to Hiya provider...")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/check",
            json=payload,
            timeout=120  # 2 minutes timeout
        )
        
        response_time = time.time() - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS - Response received:")
            print("=" * 50)
            print(json.dumps(result, indent=2))
            
            # Extract key information
            print(f"\n📋 Summary:")
            print(f"   Phone Number: {result['phone_number']}")
            print(f"   Overall Status: {result['overall_status']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Total Response Time: {result['total_response_time']:.2f}s")
            
            # Show provider details
            for provider in result['providers']:
                print(f"\n🔍 Provider: {provider['provider']}")
                print(f"   Status: {provider['status']}")
                print(f"   Confidence: {provider['confidence']}")
                print(f"   Response Time: {provider['response_time']:.2f}s")
                if provider.get('error_message'):
                    print(f"   Error: {provider['error_message']}")
                if provider.get('raw_data'):
                    print(f"   Raw Data: {provider['raw_data']}")
            
        else:
            print(f"\n❌ ERROR - Request failed:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏰ TIMEOUT - Request took longer than 120 seconds")
        print("   This is common with Android automation - the emulator might be slow")
        
    except Exception as e:
        print(f"\n❌ ERROR - {e}")

if __name__ == "__main__":
    import sys
    
    # Allow custom phone number as command line argument
    phone_number = "+1234567890"
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    
    test_hiya_provider(phone_number)
