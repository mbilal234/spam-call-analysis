"""
Provider implementations for different spam detection services.
Each provider implements a common interface for checking phone numbers.
"""

from .base_provider import BaseProvider
from .hiya_provider import HiyaProvider

__all__ = ["BaseProvider", "HiyaProvider"]
