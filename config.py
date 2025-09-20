"""
Configuration settings for the Spam Call Analysis API.
"""

import os
from typing import List

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "1"))
    
    # Device Settings
    MAX_DEVICES: int = int(os.getenv("MAX_DEVICES", "1"))
    DEVICE_TIMEOUT: int = int(os.getenv("DEVICE_TIMEOUT", "30"))
    
    # Provider Settings
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    ENABLED_PROVIDERS: List[str] = os.getenv("ENABLED_PROVIDERS", "hiya").split(",")
    
    # Google Account (for apps that require it)
    GOOGLE_USERNAME: str = os.getenv("GOOGLE_USERNAME", "")
    GOOGLE_PASSWORD: str = os.getenv("GOOGLE_PASSWORD", "")
    
    # Appium Settings
    APPIUM_SERVER_URL: str = os.getenv("APPIUM_SERVER_URL", "http://localhost:4723")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # File Paths
    APK_DIRECTORY: str = os.getenv("APK_DIRECTORY", "apks")
    REFERENCE_IMAGES_DIR: str = os.getenv("REFERENCE_IMAGES_DIR", "reference_images")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "out")
    
    # Batch Processing
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "100"))
    BATCH_TIMEOUT: int = int(os.getenv("BATCH_TIMEOUT", "3600"))  # 1 hour
    
    # Health Check
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))  # 1 minute

# Global settings instance
settings = Settings()
