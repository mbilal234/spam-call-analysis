"""
Pydantic models for the Spam Call Analysis API.
Defines request/response schemas and data validation.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
import re

class PhoneNumberRequest(BaseModel):
    """Request model for checking a phone number."""
    
    phone_number: str = Field(
        ...,
        description="Phone number to check (with country code, e.g., +1234567890)",
        example="+1234567890"
    )
    
    providers: Optional[List[str]] = Field(
        default=None,
        description="Specific providers to check against. If None, uses all available providers.",
        example=["hiya", "truecaller"]
    )
    
    timeout: Optional[int] = Field(
        default=30,
        description="Timeout in seconds for the check operation",
        ge=5,
        le=300
    )
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Must start with + and have at least 10 digits
        if not cleaned.startswith('+'):
            raise ValueError('Phone number must start with +')
        
        digits_only = cleaned[1:]  # Remove the +
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must have 10-15 digits after country code')
        
        # Check for valid characters
        if not re.match(r'^\+\d{10,15}$', cleaned):
            raise ValueError('Phone number format is invalid')
        
        return cleaned

class ProviderStatus(BaseModel):
    """Status information for a specific provider."""
    
    provider: str = Field(..., description="Provider name (e.g., 'hiya', 'truecaller')")
    status: Literal["allowed", "blocked", "caution", "timeout", "error"] = Field(
        ..., description="Spam status from this provider"
    )
    confidence: float = Field(
        ..., 
        description="Confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    response_time: float = Field(
        ..., 
        description="Response time in seconds",
        ge=0.0
    )
    error_message: Optional[str] = Field(
        None, 
        description="Error message if status is 'error'"
    )
    raw_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw response data from the provider"
    )

class SpamCheckResponse(BaseModel):
    """Response model for spam check results."""
    
    phone_number: str = Field(..., description="The phone number that was checked")
    overall_status: Literal["allowed", "blocked", "caution", "timeout", "error"] = Field(
        ..., description="Overall spam status based on all providers"
    )
    confidence: float = Field(
        ..., 
        description="Overall confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    providers: List[ProviderStatus] = Field(
        ..., description="Results from individual providers"
    )
    total_response_time: float = Field(
        ..., 
        description="Total time taken for all checks in seconds",
        ge=0.0
    )
    timestamp: str = Field(..., description="ISO timestamp when the check was performed")
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }

class BatchRequest(BaseModel):
    """Request model for batch processing."""
    
    requests: List[PhoneNumberRequest] = Field(
        ...,
        description="List of phone number requests to process",
        max_items=100
    )

class BatchStatus(BaseModel):
    """Status information for batch processing."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ..., description="Current batch processing status"
    )
    total_numbers: int = Field(..., description="Total number of phone numbers to process")
    processed_numbers: int = Field(..., description="Number of phone numbers processed so far")
    successful_checks: int = Field(..., description="Number of successful checks")
    failed_checks: int = Field(..., description="Number of failed checks")
    started_at: str = Field(..., description="ISO timestamp when processing started")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when processing completed")
    error_message: Optional[str] = Field(None, description="Error message if status is 'failed'")

class BatchResults(BaseModel):
    """Results for batch processing."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: Literal["completed", "failed"] = Field(..., description="Final batch processing status")
    results: List[SpamCheckResponse] = Field(..., description="Individual check results")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    completed_at: str = Field(..., description="ISO timestamp when processing completed")

class HealthStatus(BaseModel):
    """Health status information."""
    
    healthy: bool = Field(..., description="Overall health status")
    providers: Dict[str, bool] = Field(..., description="Health status of individual providers")
    devices: Dict[str, bool] = Field(..., description="Health status of Android devices")
    uptime: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="ISO timestamp when error occurred")
