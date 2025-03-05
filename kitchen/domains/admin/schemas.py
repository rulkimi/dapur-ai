from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class RequestLogResponse(BaseModel):
    """Schema for request log response."""
    request_id: str
    timestamp: datetime
    method: str
    path: str
    status_code: int
    duration_ms: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    exception: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EndpointAnalytics(BaseModel):
    """Schema for endpoint analytics."""
    path: str
    method: str
    request_count: int
    avg_duration_ms: float
    min_duration_ms: int
    max_duration_ms: int
    error_count: int
    error_rate: float

class RequestMetrics(BaseModel):
    """Schema for request metrics."""
    total_requests: int
    error_rate: float
    avg_response_time: float
    requests_by_day: Dict[str, int]
    common_errors: Dict[str, int]

# New schemas for endpoint management

class EndpointRegistryItem(BaseModel):
    """Schema for endpoint registry items."""
    path: str
    enabled: bool = True
    description: str = ""

class EndpointStatusUpdate(BaseModel):
    """Schema for updating endpoint status."""
    enabled: bool
    description: Optional[str] = None 