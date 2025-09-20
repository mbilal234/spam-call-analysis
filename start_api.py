#!/usr/bin/env python3
"""
Startup script for the Spam Call Analysis API.
Handles environment setup and starts the API server.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import appium
        import selenium
        import cv2
        import numpy
        print("✓ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_appium():
    """Check if Appium server is running."""
    try:
        import requests
        response = requests.get(f"{settings.APPIUM_SERVER_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✓ Appium server is running")
            return True
    except:
        pass
    
    print("✗ Appium server is not running")
    print("Please start Appium with: appium")
    return False

def check_android_emulators():
    """Check if Android emulators are available."""
    try:
        result = subprocess.run(
            ["adb", "devices"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line for line in lines if line.strip() and 'device' in line]
            if devices:
                print(f"✓ Found {len(devices)} Android device(s)")
                return True
    except:
        pass
    
    print("✗ No Android devices found")
    print("Please start Android emulators or connect physical devices")
    return False

def check_apk_files():
    """Check if required APK files are present."""
    apk_dir = Path(settings.APK_DIRECTORY)
    if not apk_dir.exists():
        print(f"✗ APK directory not found: {apk_dir}")
        return False
    
    required_apks = [
        "com.webascender.callerid.apk",  # Hiya
        "com.truecaller.apk",  # Truecaller
    ]
    
    missing_apks = []
    for apk in required_apks:
        if not (apk_dir / apk).exists():
            missing_apks.append(apk)
    
    if missing_apks:
        print(f"✗ Missing APK files: {missing_apks}")
        return False
    
    print("✓ Required APK files found")
    return True

def main():
    """Main startup function."""
    print("Spam Call Analysis API - Startup Check")
    print("=" * 50)
    
    # Check all requirements
    checks = [
        ("Python Dependencies", check_dependencies),
        ("Appium Server", check_appium),
        ("Android Devices", check_android_emulators),
        ("APK Files", check_apk_files),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\nChecking {check_name}...")
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Some checks failed. Please fix the issues above before starting the API.")
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting API server...")
    print(f"API will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
    print("Press Ctrl+C to stop the server")
    
    # Start the API server
    try:
        import uvicorn
        uvicorn.run(
            "api_server:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            workers=settings.API_WORKERS,
            log_level=settings.LOG_LEVEL.lower()
        )
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"\n❌ Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
