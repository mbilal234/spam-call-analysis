"""
Mock provider for testing the API without Android automation.
Returns simulated spam check results.
"""

import asyncio
import logging
import random
import time
from typing import Dict, Any

from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

class MockProvider(BaseProvider):
    """
    Mock provider that simulates spam detection results for testing.
    """
    
    def __init__(self, device_manager):
        super().__init__(device_manager)
        self.name = "mock"
        
    async def initialize(self):
        """Initialize the mock provider."""
        logger.info("Initializing Mock provider...")
        self.initialized = True
        logger.info("Mock provider initialized successfully")
        
    async def check_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Check a phone number using mock logic.
        
        Args:
            phone_number: Phone number to check
            
        Returns:
            Dictionary with mock spam check results
        """
        if not self.initialized:
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": "Provider not initialized"
            }
        
        try:
            # Simulate processing time
            await asyncio.sleep(random.uniform(1, 3))
            
            # Mock logic based on phone number patterns
            if phone_number.endswith("0000"):
                status = "blocked"
                confidence = 0.95
            elif phone_number.endswith("1111"):
                status = "caution"
                confidence = 0.75
            elif phone_number.startswith("+1"):
                status = "allowed"
                confidence = 0.85
            else:
                # Random result for other numbers
                status = random.choice(["allowed", "blocked", "caution"])
                confidence = random.uniform(0.6, 0.95)
            
            return {
                "status": status,
                "confidence": confidence,
                "raw_data": {
                    "mock_result": True,
                    "phone_pattern": phone_number[-4:],
                    "simulated": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in mock check for {phone_number}: {e}")
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": str(e)
            }
    
    async def cleanup(self):
        """Cleanup mock provider resources."""
        logger.info("Cleaning up Mock provider...")
        self.initialized = False
        logger.info("Mock provider cleanup completed")
    
    async def is_healthy(self) -> bool:
        """Check if mock provider is healthy."""
        return self.initialized
