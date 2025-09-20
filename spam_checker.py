"""
Core spam checking service that manages Android devices and provider integrations.
Handles Hiya integration for Phase 1 and provides extensible architecture for other providers.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (
    PhoneNumberRequest, 
    SpamCheckResponse, 
    ProviderStatus, 
    BatchStatus, 
    BatchResults,
    HealthStatus
)
from providers.hiya_provider import HiyaProvider
from providers.mock_provider import MockProvider
from device_manager import AndroidDeviceManager

logger = logging.getLogger(__name__)

class SpamCheckerService:
    """
    Main service class that orchestrates spam checking across multiple providers.
    Manages Android devices and coordinates provider-specific implementations.
    """
    
    def __init__(self):
        self.device_manager: Optional[AndroidDeviceManager] = None
        self.providers: Dict[str, Any] = {}
        self.batch_tasks: Dict[str, BatchStatus] = {}
        self.start_time = time.time()
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service and all providers."""
        try:
            logger.info("Initializing Spam Checker Service...")
            
            # Initialize device manager
            self.device_manager = AndroidDeviceManager()
            await self.device_manager.initialize()
            
            # Initialize providers
            await self._initialize_providers()
            
            self.initialized = True
            logger.info("Spam Checker Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spam Checker Service: {e}")
            raise
    
    async def _initialize_providers(self):
        """Initialize all available providers."""
        try:
            # Initialize Mock provider for testing
            mock_provider = MockProvider(self.device_manager)
            await mock_provider.initialize()
            self.providers["mock"] = mock_provider
            logger.info("Mock provider initialized")
            
            # Initialize Hiya provider (Phase 1) - with error handling
            try:
                hiya_provider = HiyaProvider(self.device_manager)
                await hiya_provider.initialize()
                self.providers["hiya"] = hiya_provider
                logger.info("Hiya provider initialized")
            except Exception as hiya_error:
                logger.warning(f"Hiya provider failed to initialize: {hiya_error}")
                logger.info("Continuing with mock provider only")
            
            # TODO: Add other providers in future phases
            # truecaller_provider = TruecallerProvider(self.device_manager)
            # await truecaller_provider.initialize()
            # self.providers["truecaller"] = truecaller_provider
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources and shutdown providers."""
        try:
            logger.info("Cleaning up Spam Checker Service...")
            
            # Cleanup providers
            for provider in self.providers.values():
                if hasattr(provider, 'cleanup'):
                    await provider.cleanup()
            
            # Cleanup device manager
            if self.device_manager:
                await self.device_manager.cleanup()
            
            self.initialized = False
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def check_number(
        self, 
        phone_number: str, 
        providers: Optional[List[str]] = None,
        timeout: int = 30
    ) -> SpamCheckResponse:
        """
        Check a single phone number against specified providers.
        
        Args:
            phone_number: Phone number to check
            providers: List of provider names to use (None for all)
            timeout: Timeout in seconds
            
        Returns:
            SpamCheckResponse with normalized results
        """
        if not self.initialized:
            raise RuntimeError("Service not initialized")
        
        start_time = time.time()
        provider_results = []
        
        # Determine which providers to use
        providers_to_use = providers or list(self.providers.keys())
        
        # Validate providers
        invalid_providers = [p for p in providers_to_use if p not in self.providers]
        if invalid_providers:
            raise ValueError(f"Invalid providers: {invalid_providers}")
        
        logger.info(f"Checking {phone_number} against providers: {providers_to_use}")
        
        # Check with each provider
        for provider_name in providers_to_use:
            try:
                provider = self.providers[provider_name]
                provider_start = time.time()
                
                # Check with provider
                result = await asyncio.wait_for(
                    provider.check_number(phone_number),
                    timeout=timeout
                )
                
                provider_time = time.time() - provider_start
                
                # Create provider status
                provider_status = ProviderStatus(
                    provider=provider_name,
                    status=result["status"],
                    confidence=result["confidence"],
                    response_time=provider_time,
                    error_message=result.get("error_message"),
                    raw_data=result.get("raw_data")
                )
                
                provider_results.append(provider_status)
                logger.info(f"Provider {provider_name} result: {result['status']} (confidence: {result['confidence']})")
                
            except asyncio.TimeoutError:
                logger.warning(f"Provider {provider_name} timed out for {phone_number}")
                provider_status = ProviderStatus(
                    provider=provider_name,
                    status="timeout",
                    confidence=0.0,
                    response_time=timeout,
                    error_message="Provider timeout"
                )
                provider_results.append(provider_status)
                
            except Exception as e:
                logger.error(f"Provider {provider_name} error for {phone_number}: {e}")
                provider_status = ProviderStatus(
                    provider=provider_name,
                    status="error",
                    confidence=0.0,
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
                provider_results.append(provider_status)
        
        # Determine overall status and confidence
        overall_status, overall_confidence = self._calculate_overall_status(provider_results)
        total_time = time.time() - start_time
        
        response = SpamCheckResponse(
            phone_number=phone_number,
            overall_status=overall_status,
            confidence=overall_confidence,
            providers=provider_results,
            total_response_time=total_time,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        logger.info(f"Check completed for {phone_number}: {overall_status} (confidence: {overall_confidence})")
        return response
    
    def _calculate_overall_status(
        self, 
        provider_results: List[ProviderStatus]
    ) -> tuple[str, float]:
        """
        Calculate overall status and confidence from provider results.
        
        Args:
            provider_results: List of provider results
            
        Returns:
            Tuple of (overall_status, overall_confidence)
        """
        if not provider_results:
            return "error", 0.0
        
        # Filter out error and timeout results for status calculation
        valid_results = [r for r in provider_results if r.status not in ["error", "timeout"]]
        
        if not valid_results:
            return "error", 0.0
        
        # Count statuses
        status_counts = {}
        total_confidence = 0.0
        
        for result in valid_results:
            status = result.status
            status_counts[status] = status_counts.get(status, 0) + 1
            total_confidence += result.confidence
        
        # Determine overall status based on majority vote
        # Priority: blocked > caution > allowed
        if status_counts.get("blocked", 0) > 0:
            overall_status = "blocked"
        elif status_counts.get("caution", 0) > 0:
            overall_status = "caution"
        else:
            overall_status = "allowed"
        
        # Calculate average confidence
        overall_confidence = total_confidence / len(valid_results)
        
        return overall_status, overall_confidence
    
    async def check_numbers_batch(self, requests: List[PhoneNumberRequest]) -> str:
        """
        Start batch processing of multiple phone numbers.
        
        Args:
            requests: List of phone number requests
            
        Returns:
            Task ID for tracking the batch
        """
        task_id = str(uuid.uuid4())
        
        batch_status = BatchStatus(
            task_id=task_id,
            status="pending",
            total_numbers=len(requests),
            processed_numbers=0,
            successful_checks=0,
            failed_checks=0,
            started_at=datetime.utcnow().isoformat() + "Z"
        )
        
        self.batch_tasks[task_id] = batch_status
        logger.info(f"Created batch task {task_id} with {len(requests)} numbers")
        
        return task_id
    
    async def process_batch_task(self, task_id: str):
        """Process a batch task in the background."""
        if task_id not in self.batch_tasks:
            logger.error(f"Batch task {task_id} not found")
            return
        
        batch_status = self.batch_tasks[task_id]
        batch_status.status = "processing"
        
        results = []
        successful = 0
        failed = 0
        
        try:
            # Get the requests for this batch (this would need to be stored)
            # For now, we'll assume they're passed somehow
            logger.info(f"Processing batch task {task_id}")
            
            # TODO: Implement actual batch processing
            # This would involve getting the original requests and processing them
            
            batch_status.status = "completed"
            batch_status.processed_numbers = batch_status.total_numbers
            batch_status.successful_checks = successful
            batch_status.failed_checks = failed
            batch_status.completed_at = datetime.utcnow().isoformat() + "Z"
            
        except Exception as e:
            logger.error(f"Batch task {task_id} failed: {e}")
            batch_status.status = "failed"
            batch_status.error_message = str(e)
            batch_status.completed_at = datetime.utcnow().isoformat() + "Z"
    
    async def get_batch_status(self, task_id: str) -> BatchStatus:
        """Get status of a batch task."""
        if task_id not in self.batch_tasks:
            raise ValueError(f"Batch task {task_id} not found")
        
        return self.batch_tasks[task_id]
    
    async def get_batch_results(self, task_id: str) -> BatchResults:
        """Get results of a completed batch task."""
        if task_id not in self.batch_tasks:
            raise ValueError(f"Batch task {task_id} not found")
        
        batch_status = self.batch_tasks[task_id]
        if batch_status.status != "completed":
            raise ValueError(f"Batch task {task_id} is not completed")
        
        # TODO: Return actual results
        return BatchResults(
            task_id=task_id,
            status="completed",
            results=[],  # Would contain actual results
            summary={},
            completed_at=batch_status.completed_at
        )
    
    async def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    async def get_health_status(self) -> HealthStatus:
        """Get health status of the service and all components."""
        if not self.initialized:
            return HealthStatus(
                healthy=False,
                providers={},
                devices={},
                uptime=0.0,
                version="1.0.0"
            )
        
        # Check provider health
        provider_health = {}
        for name, provider in self.providers.items():
            try:
                if hasattr(provider, 'is_healthy'):
                    provider_health[name] = await provider.is_healthy()
                else:
                    provider_health[name] = True
            except:
                provider_health[name] = False
        
        # Check device health
        device_health = {}
        if self.device_manager:
            try:
                device_health = await self.device_manager.get_health_status()
            except:
                device_health = {"default": False}
        
        # Overall health
        all_providers_healthy = all(provider_health.values())
        all_devices_healthy = all(device_health.values()) if device_health else False
        healthy = all_providers_healthy and all_devices_healthy
        
        return HealthStatus(
            healthy=healthy,
            providers=provider_health,
            devices=device_health,
            uptime=time.time() - self.start_time,
            version="1.0.0"
        )
