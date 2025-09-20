#!/usr/bin/env python3
"""
Spam Call Analysis API Server
Backend service for checking phone numbers against spam providers like Hiya and Truecaller.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spam_checker import SpamCheckerService
from models import PhoneNumberRequest, SpamCheckResponse, ProviderStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instance
spam_checker_service: Optional[SpamCheckerService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown tasks."""
    global spam_checker_service
    
    # Startup
    logger.info("Starting Spam Checker API Server...")
    try:
        spam_checker_service = SpamCheckerService()
        await spam_checker_service.initialize()
        logger.info("Spam Checker Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Spam Checker Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Spam Checker API Server...")
    if spam_checker_service:
        await spam_checker_service.cleanup()
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Spam Call Analysis API",
    description="API for checking phone numbers against spam providers like Hiya and Truecaller",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Spam Call Analysis API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "check_number": "/api/v1/check",
            "check_batch": "/api/v1/check/batch",
            "health": "/api/v1/health",
            "providers": "/api/v1/providers"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    if not spam_checker_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    service_status = await spam_checker_service.get_health_status()
    return {
        "status": "healthy" if service_status.healthy else "unhealthy",
        "details": service_status.dict()
    }

@app.get("/api/v1/providers")
async def get_providers():
    """Get available spam detection providers."""
    if not spam_checker_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return {
        "providers": await spam_checker_service.get_available_providers()
    }

@app.post("/api/v1/check", response_model=SpamCheckResponse)
async def check_phone_number(request: PhoneNumberRequest):
    """
    Check a single phone number against spam providers.
    
    Args:
        request: Phone number request with optional provider preferences
        
    Returns:
        SpamCheckResponse with normalized results
    """
    if not spam_checker_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await spam_checker_service.check_number(
            phone_number=request.phone_number,
            providers=request.providers,
            timeout=request.timeout
        )
        return result
    except Exception as e:
        logger.error(f"Error checking phone number {request.phone_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/check/batch")
async def check_phone_numbers_batch(
    requests: List[PhoneNumberRequest],
    background_tasks: BackgroundTasks
):
    """
    Check multiple phone numbers in batch.
    
    Args:
        requests: List of phone number requests
        background_tasks: FastAPI background tasks
        
    Returns:
        Batch processing information
    """
    if not spam_checker_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if len(requests) > 100:  # Limit batch size
        raise HTTPException(status_code=400, detail="Batch size too large. Maximum 100 numbers per batch.")
    
    try:
        # Process batch asynchronously
        task_id = await spam_checker_service.check_numbers_batch(requests)
        
        # Start background task to process the batch
        background_tasks.add_task(
            spam_checker_service.process_batch_task,
            task_id
        )
        
        return {
            "message": "Batch processing started",
            "task_id": task_id,
            "numbers_count": len(requests),
            "status_endpoint": f"/api/v1/batch/{task_id}/status"
        }
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/batch/{task_id}/status")
async def get_batch_status(task_id: str):
    """Get status of a batch processing task."""
    if not spam_checker_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        status = await spam_checker_service.get_batch_status(task_id)
        return status
    except Exception as e:
        logger.error(f"Error getting batch status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/batch/{task_id}/results")
async def get_batch_results(task_id: str):
    """Get results of a completed batch processing task."""
    if not spam_checker_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = await spam_checker_service.get_batch_results(task_id)
        return results
    except Exception as e:
        logger.error(f"Error getting batch results for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    # Configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    
    logger.info(f"Starting API server on {host}:{port} with {workers} workers")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )
