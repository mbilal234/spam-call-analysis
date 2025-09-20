#!/usr/bin/env python3
"""
Quick test script for Hiya provider - simple one-liner testing.
Usage: python test_hiya_quick.py [phone_number]
"""

import json
import requests
import sys
import time

def test_hiya(phone_number="+1234567890"):
    """Quick test of Hiya provider with a single phone number."""
    
    print(f"🔍 Testing Hiya Provider: {phone_number}")
    print("-" * 40)
    
    try:
        # Test API connection
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ API server not running. Start with: python api_server.py")
            return
        
        # Test Hiya provider
        payload = {
            "phone_number": phone_number,
            "providers": ["hiya"]
        }
        
        print("📤 Sending request...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/v1/check",
            json=payload,
            timeout=60  # 1 minute timeout
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received in {response_time:.1f}s")
            print(f"   Status: {result['overall_status']}")
            print(f"   Confidence: {result['confidence']}")
            
            # Show provider details
            for provider in result['providers']:
                print(f"   {provider['provider']}: {provider['status']} ({provider['confidence']})")
                if provider.get('error_message'):
                    print(f"   Error: {provider['error_message']}")
                if provider.get('raw_data'):
                    print(f"   Raw: {provider['raw_data']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout after {response_time:.1f}s - Android automation is slow")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Get phone number from command line or use default
    phone_number = "+1234567890"
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    
    # Validate phone number format
    if not phone_number.startswith('+'):
        print("❌ Phone number must start with + (e.g., +1234567890)")
        sys.exit(1)
    
    test_hiya(phone_number)
