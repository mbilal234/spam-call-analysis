"""
Android Device Manager for handling multiple Android devices/emulators.
Manages device allocation, health monitoring, and cleanup.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from appsetupscripts.driver_manager import DriverManager
from config import settings

logger = logging.getLogger(__name__)

@dataclass
class DeviceInfo:
    """Information about an Android device."""
    device_id: str
    status: str  # "available", "busy", "error", "offline"
    thread_index: int
    driver_manager: Optional[DriverManager] = None
    last_used: Optional[float] = None
    error_count: int = 0

class AndroidDeviceManager:
    """
    Manages multiple Android devices for spam checking operations.
    Handles device allocation, health monitoring, and resource cleanup.
    """
    
    def __init__(self, max_devices: int = None):
        self.max_devices = max_devices or settings.MAX_DEVICES
        self.devices: Dict[str, DeviceInfo] = {}
        self.device_queue: asyncio.Queue = asyncio.Queue()
        self.initialized = False
        self.cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the device manager and create devices."""
        try:
            logger.info(f"Initializing Android Device Manager with {self.max_devices} devices...")
            
            # Create devices
            for i in range(self.max_devices):
                device_id = f"device_{i}"
                device_info = DeviceInfo(
                    device_id=device_id,
                    status="available",
                    thread_index=i
                )
                self.devices[device_id] = device_info
                await self.device_queue.put(device_id)
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.initialized = True
            logger.info(f"Android Device Manager initialized with {len(self.devices)} devices")
            
        except Exception as e:
            logger.error(f"Failed to initialize Android Device Manager: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup all devices and resources."""
        try:
            logger.info("Cleaning up Android Device Manager...")
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Cleanup all devices
            for device_info in self.devices.values():
                if device_info.driver_manager:
                    try:
                        device_info.driver_manager.finish()
                    except Exception as e:
                        logger.warning(f"Error cleaning up device {device_info.device_id}: {e}")
            
            self.devices.clear()
            self.initialized = False
            logger.info("Android Device Manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during device manager cleanup: {e}")
    
    async def get_device(self, timeout: int = 30) -> Optional[DeviceInfo]:
        """
        Get an available device for spam checking.
        
        Args:
            timeout: Timeout in seconds to wait for a device
            
        Returns:
            DeviceInfo if available, None if timeout
        """
        if not self.initialized:
            raise RuntimeError("Device manager not initialized")
        
        try:
            # Wait for an available device
            device_id = await asyncio.wait_for(
                self.device_queue.get(),
                timeout=timeout
            )
            
            device_info = self.devices[device_id]
            
            # Initialize driver if not already done
            if not device_info.driver_manager:
                try:
                    device_info.driver_manager = DriverManager(
                        device_info.thread_index, 
                        headless=True
                    )
                    device_info.status = "available"
                    logger.info(f"Initialized driver for device {device_id}")
                except Exception as e:
                    logger.error(f"Failed to initialize driver for device {device_id}: {e}")
                    device_info.status = "error"
                    device_info.error_count += 1
                    # Put device back in queue for retry
                    await self.device_queue.put(device_id)
                    return None
            
            # Mark device as busy
            device_info.status = "busy"
            device_info.last_used = time.time()
            
            logger.info(f"Allocated device {device_id}")
            return device_info
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for available device")
            return None
        except Exception as e:
            logger.error(f"Error getting device: {e}")
            return None
    
    async def release_device(self, device_info: DeviceInfo):
        """
        Release a device back to the available pool.
        
        Args:
            device_info: Device to release
        """
        if not self.initialized:
            return
        
        try:
            device_info.status = "available"
            device_info.last_used = time.time()
            
            # Put device back in queue
            await self.device_queue.put(device_info.device_id)
            
            logger.info(f"Released device {device_info.device_id}")
            
        except Exception as e:
            logger.error(f"Error releasing device {device_info.device_id}: {e}")
    
    async def mark_device_error(self, device_info: DeviceInfo, error: str):
        """
        Mark a device as having an error.
        
        Args:
            device_info: Device that had an error
            error: Error description
        """
        device_info.status = "error"
        device_info.error_count += 1
        
        logger.warning(f"Device {device_info.device_id} marked as error: {error}")
        
        # If too many errors, mark as offline
        if device_info.error_count >= 3:
            device_info.status = "offline"
            logger.error(f"Device {device_info.device_id} marked as offline due to repeated errors")
        else:
            # Put back in queue for retry
            await self.device_queue.put(device_info.device_id)
    
    async def get_health_status(self) -> Dict[str, bool]:
        """Get health status of all devices."""
        health_status = {}
        
        for device_id, device_info in self.devices.items():
            if device_info.status in ["available", "busy"]:
                health_status[device_id] = True
            else:
                health_status[device_id] = False
        
        return health_status
    
    async def get_device_stats(self) -> Dict[str, Any]:
        """Get statistics about device usage."""
        stats = {
            "total_devices": len(self.devices),
            "available_devices": sum(1 for d in self.devices.values() if d.status == "available"),
            "busy_devices": sum(1 for d in self.devices.values() if d.status == "busy"),
            "error_devices": sum(1 for d in self.devices.values() if d.status == "error"),
            "offline_devices": sum(1 for d in self.devices.values() if d.status == "offline"),
            "queue_size": self.device_queue.qsize()
        }
        
        return stats
    
    async def _cleanup_loop(self):
        """Background task to clean up idle devices and monitor health."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = time.time()
                idle_threshold = 300  # 5 minutes
                
                for device_info in self.devices.values():
                    # Cleanup idle devices
                    if (device_info.status == "available" and 
                        device_info.last_used and 
                        current_time - device_info.last_used > idle_threshold):
                        
                        if device_info.driver_manager:
                            try:
                                device_info.driver_manager.finish()
                                device_info.driver_manager = None
                                logger.info(f"Cleaned up idle device {device_info.device_id}")
                            except Exception as e:
                                logger.warning(f"Error cleaning up idle device {device_info.device_id}: {e}")
                    
                    # Reset error count for devices that have been stable
                    if (device_info.status == "error" and 
                        device_info.last_used and 
                        current_time - device_info.last_used > 300):
                        
                        device_info.error_count = 0
                        device_info.status = "available"
                        await self.device_queue.put(device_info.device_id)
                        logger.info(f"Reset error count for device {device_info.device_id}")
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
