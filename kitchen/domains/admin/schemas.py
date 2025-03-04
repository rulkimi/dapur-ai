from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class RequestLogResponse(BaseModel):
    """Schema for request log response."""
    request_id: str
    timestamp: datetime
    method: str
    path: str
    status_code: int
    duration_ms: int
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    exception: Optional[str] = None
    
    class Config:
        from_attributes = True

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