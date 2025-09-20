#!/usr/bin/env python3
"""
Example usage of the Spam Call Analysis API.
Demonstrates how to use the API to check phone numbers.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def example_single_check():
    """Example of checking a single phone number."""
    print("=== Single Number Check Example ===")
    
    # Prepare the request
    payload = {
        "phone_number": "+1234567890",
        "providers": ["hiya"],
        "timeout": 30
    }
    
    print(f"Checking: {payload['phone_number']}")
    print("Sending request...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Check completed!")
            print(f"  Overall Status: {result['overall_status']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Response Time: {result['total_response_time']:.2f}s")
            
            # Show provider-specific results
            for provider in result['providers']:
                print(f"  {provider['provider']}: {provider['status']} (confidence: {provider['confidence']:.2f})")
        else:
            print(f"✗ Request failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def example_batch_check():
    """Example of checking multiple phone numbers in batch."""
    print("\n=== Batch Check Example ===")
    
    # Prepare batch request
    payload = {
        "requests": [
            {"phone_number": "+1234567890", "providers": ["hiya"]},
            {"phone_number": "+1987654321", "providers": ["hiya"]},
            {"phone_number": "+1555123456", "providers": ["hiya"]}
        ]
    }
    
    print(f"Checking {len(payload['requests'])} numbers in batch...")
    
    try:
        # Start batch processing
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            batch_info = response.json()
            task_id = batch_info['task_id']
            print(f"✓ Batch started with task ID: {task_id}")
            
            # Monitor batch progress
            print("Monitoring batch progress...")
            for i in range(10):  # Check up to 10 times
                time.sleep(2)
                
                status_response = requests.get(f"{API_BASE_URL}/api/v1/batch/{task_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"  Progress: {status['processed_numbers']}/{status['total_numbers']} "
                          f"(Success: {status['successful_checks']}, Failed: {status['failed_checks']})")
                    
                    if status['status'] == 'completed':
                        print("✓ Batch completed!")
                        
                        # Get results
                        results_response = requests.get(f"{API_BASE_URL}/api/v1/batch/{task_id}/results")
                        if results_response.status_code == 200:
                            results = results_response.json()
                            print(f"  Results: {len(results['results'])} numbers processed")
                            
                            # Show summary
                            for result in results['results']:
                                print(f"    {result['phone_number']}: {result['overall_status']} "
                                      f"(confidence: {result['confidence']:.2f})")
                        break
                    elif status['status'] == 'failed':
                        print(f"✗ Batch failed: {status.get('error_message', 'Unknown error')}")
                        break
                else:
                    print(f"✗ Status check failed: {status_response.status_code}")
                    break
        else:
            print(f"✗ Batch request failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def example_health_check():
    """Example of checking API health."""
    print("\n=== Health Check Example ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✓ API Health: {health['status']}")
            print(f"  Uptime: {health['uptime']:.2f}s")
            print(f"  Version: {health['version']}")
            
            # Show provider health
            print("  Provider Health:")
            for provider, status in health['providers'].items():
                status_icon = "✓" if status else "✗"
                print(f"    {provider}: {status_icon}")
            
            # Show device health
            print("  Device Health:")
            for device, status in health['devices'].items():
                status_icon = "✓" if status else "✗"
                print(f"    {device}: {status_icon}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def example_get_providers():
    """Example of getting available providers."""
    print("\n=== Available Providers Example ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/providers")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Available providers: {data['providers']}")
        else:
            print(f"✗ Providers request failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    """Run all examples."""
    print("Spam Call Analysis API - Usage Examples")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running. Please start it with: python start_api.py")
            return
    except:
        print("❌ Cannot connect to API server. Please start it with: python start_api.py")
        return
    
    print("✓ API server is running")
    
    # Run examples
    example_health_check()
    example_get_providers()
    example_single_check()
    example_batch_check()
    
    print("\n" + "=" * 50)
    print("✅ All examples completed!")

if __name__ == "__main__":
    main()
