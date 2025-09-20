"""
Base provider class that defines the interface for all spam detection providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """
    Abstract base class for all spam detection providers.
    Defines the common interface that all providers must implement.
    """
    
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.initialized = False
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def initialize(self):
        """Initialize the provider and any required resources."""
        pass
    
    @abstractmethod
    async def check_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Check a phone number for spam status.
        
        Args:
            phone_number: Phone number to check (with country code)
            
        Returns:
            Dictionary with keys:
            - status: "allowed", "blocked", "caution", "timeout", "error"
            - confidence: float between 0.0 and 1.0
            - error_message: optional error description
            - raw_data: optional raw response data
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup provider resources."""
        pass
    
    async def is_healthy(self) -> bool:
        """
        Check if the provider is healthy and ready to process requests.
        
        Returns:
            True if healthy, False otherwise
        """
        return self.initialized
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.
        
        Returns:
            Dictionary with provider information
        """
        return {
            "name": self.name,
            "initialized": self.initialized,
            "healthy": self.initialized
        }
