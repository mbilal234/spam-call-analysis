"""
Hiya provider implementation for spam detection.
Uses Android automation to interact with the Hiya app and extract spam status.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
import base64
import os

from .base_provider import BaseProvider
from appsetupscripts.setup import WebascenderCallerID

logger = logging.getLogger(__name__)

class HiyaProvider(BaseProvider):
    """
    Provider implementation for Hiya spam detection.
    Uses the existing WebascenderCallerID class which is the Hiya app.
    """
    
    def __init__(self, device_manager):
        super().__init__(device_manager)
        self.name = "hiya"
        self.app_class = WebascenderCallerID
        self.current_device: Optional[Any] = None
        self.app_instance: Optional[WebascenderCallerID] = None
        
    async def initialize(self):
        """Initialize the Hiya provider."""
        try:
            logger.info("Initializing Hiya provider...")
            
            # Get a device for this provider
            self.current_device = await self.device_manager.get_device(timeout=60)
            if not self.current_device:
                raise RuntimeError("No available devices for Hiya provider")
            
            # Initialize the app
            apk_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apks')
            
            # Don't initialize driver here - let it be done lazily
            self.apk_directory = apk_directory
            
            self.initialized = True
            logger.info("Hiya provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hiya provider: {e}")
            if self.current_device:
                await self.device_manager.mark_device_error(self.current_device, str(e))
            raise
    
    async def _initialize_app(self):
        """Initialize the app instance with the device driver."""
        try:
            if not self.current_device.driver_manager:
                # Initialize driver if not already done
                self.current_device.driver_manager = DriverManager(
                    self.current_device.thread_index, 
                    headless=True
                )
            
            self.app_instance = self.app_class(
                self.current_device.driver_manager.driver,
                self.apk_directory
            )
            
            # Install the app
            logger.info("Installing Hiya app...")
            self.app_instance.install()
            
            # Wait for app to be ready
            await asyncio.sleep(5)
            
            # Setup the app with error handling
            logger.info("Setting up Hiya app...")
            try:
                self.app_instance.setup()
                logger.info("App setup completed successfully")
            except Exception as setup_error:
                logger.warning(f"App setup failed, but continuing: {setup_error}")
                # Continue anyway - the app might still work
            
            logger.info("App instance initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize app instance: {e}")
            raise
    
    async def check_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Check a phone number using Hiya.
        
        Args:
            phone_number: Phone number to check
            
        Returns:
            Dictionary with spam check results
        """
        if not self.initialized:
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": "Provider not initialized"
            }
        
        try:
            logger.info(f"Checking {phone_number} with Hiya")
            
            # Initialize app instance if not already done
            if not self.app_instance:
                await self._initialize_app()
            
            # Use the existing perform_analysis method but adapt it for single number
            result = await self._check_single_number(phone_number)
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking {phone_number} with Hiya: {e}")
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": str(e)
            }
    
    async def _check_single_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Check a single phone number using the existing app logic.
        
        Args:
            phone_number: Phone number to check
            
        Returns:
            Dictionary with spam check results
        """
        try:
            # Create a temporary output file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                temp_file = f.name
            
            # Write CSV header
            with open(temp_file, 'w') as f:
                f.write("number,package_name,status,delta,accuracy\n")
            
            # Perform analysis for single number with timeout handling
            try:
                logger.info(f"Starting analysis for {phone_number}")
                self.app_instance.perform_analysis(
                    [phone_number], 
                    temp_file, 
                    print_csv_line=False, 
                    save_screenshot=False
                )
                logger.info(f"Analysis completed for {phone_number}")
            except Exception as analysis_error:
                logger.warning(f"Analysis failed for {phone_number}: {analysis_error}")
                # Write a timeout result
                with open(temp_file, 'a') as f:
                    f.write(f"{phone_number},com.webascender.callerid,timeout,10.0,0.0\n")
            
            # Read the result
            result = await self._parse_result_file(temp_file, phone_number)
            
            # Cleanup temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error in single number check: {e}")
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": str(e)
            }
    
    async def _parse_result_file(self, file_path: str, phone_number: str) -> Dict[str, Any]:
        """
        Parse the result file to extract spam status.
        
        Args:
            file_path: Path to the CSV result file
            phone_number: Phone number that was checked
            
        Returns:
            Dictionary with parsed results
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Skip header line
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 4 and parts[0] == phone_number:
                        status = parts[2]
                        delta = float(parts[3]) if parts[3] else 0.0
                        accuracy = float(parts[4]) if len(parts) > 4 and parts[4] else 1.0
                        
                        # Map status to our standard format
                        if status == "blocked":
                            return {
                                "status": "blocked",
                                "confidence": accuracy,
                                "raw_data": {
                                    "delta": delta,
                                    "original_status": status
                                }
                            }
                        elif status == "caution":
                            return {
                                "status": "caution", 
                                "confidence": accuracy,
                                "raw_data": {
                                    "delta": delta,
                                    "original_status": status
                                }
                            }
                        elif status == "allowed":
                            return {
                                "status": "allowed",
                                "confidence": accuracy,
                                "raw_data": {
                                    "delta": delta,
                                    "original_status": status
                                }
                            }
                        elif status == "timeout":
                            return {
                                "status": "timeout",
                                "confidence": 0.0,
                                "raw_data": {
                                    "delta": delta,
                                    "original_status": status
                                }
                            }
                        else:
                            return {
                                "status": "error",
                                "confidence": 0.0,
                                "error_message": f"Unknown status: {status}"
                            }
            
            # If no result found
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": "No result found in output file"
            }
            
        except Exception as e:
            logger.error(f"Error parsing result file: {e}")
            return {
                "status": "error",
                "confidence": 0.0,
                "error_message": f"Error parsing results: {str(e)}"
            }
    
    async def cleanup(self):
        """Cleanup Hiya provider resources."""
        try:
            logger.info("Cleaning up Hiya provider...")
            
            if self.app_instance:
                try:
                    self.app_instance.uninstall()
                except Exception as e:
                    logger.warning(f"Error uninstalling Hiya app: {e}")
                self.app_instance = None
            
            if self.current_device:
                await self.device_manager.release_device(self.current_device)
                self.current_device = None
            
            self.initialized = False
            logger.info("Hiya provider cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during Hiya provider cleanup: {e}")
    
    async def is_healthy(self) -> bool:
        """Check if Hiya provider is healthy."""
        if not self.initialized:
            return False
        
        if not self.current_device or not self.app_instance:
            return False
        
        # Check if device is still healthy
        device_health = await self.device_manager.get_health_status()
        device_id = self.current_device.device_id
        if device_id not in device_health or not device_health[device_id]:
            return False
        
        return True
