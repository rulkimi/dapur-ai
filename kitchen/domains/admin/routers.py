from fastapi import Depends, HTTPException, status, Request, Response, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, cast, Date
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from enum import Enum
import re
from pydantic import BaseModel, Field

from db.repository import get_repository_session
from db.models.request_log import RequestLog
from core.security import get_current_user
from core.dependencies import (
    ENDPOINT_REGISTRY, register_endpoint, enable_endpoint, 
    disable_endpoint, toggle_endpoint, is_endpoint_enabled, 
    get_all_endpoints, bulk_update_endpoints, endpoint_control,
    get_registered_endpoints, controllable_endpoint, ControllableAPIRouter,
    feature_flag, route_enabled, conditional_router
)
from core.config import settings
from .schemas import RequestLogResponse, EndpointAnalytics, RequestMetrics, EndpointRegistryItem, EndpointStatusUpdate
from core.security import get_current_auth
from domains.auth.models import Auth

# For timezone-aware queries
UTC = timezone.utc

# Define schemas used in this module
class BulkEndpointAction(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"

class BulkEndpointUpdate(BaseModel):
    """Schema for bulk updating endpoints by pattern."""
    pattern: str
    enabled: bool
    description: Optional[str] = None

class FeatureFlagUpdate(BaseModel):
    """Schema for updating a feature flag's value."""
    value: bool
    description: Optional[str] = None

router = ControllableAPIRouter(prefix="/admin", tags=["admin"])

# Helper function to check if user is admin
async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency to check if the current user is an admin."""
    print("current_user",current_user)
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=403, 
            detail="Admin access required"
        )
    return current_user

@router.get("/logs", response_model=List[Dict[str, Any]])
async def get_logs(
    level: Optional[str] = None,
    request_id: Optional[str] = None,
    module: Optional[str] = None,
    method: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = Query(None, description="Default is now"),
    limit: int = Query(100, le=1000),
    session: AsyncSession = Depends(get_repository_session),
    _: dict = Depends(get_admin_user),  # Ensure admin access
) -> List[Dict[str, Any]]:
    """Query request logs for debugging."""
    query = select(RequestLog).order_by(desc(RequestLog.timestamp))
    
    # Apply filters
    if request_id:
        query = query.filter(RequestLog.request_id == request_id)
    if level:
        query = query.filter(RequestLog.level == level)
    if module:
        query = query.filter(RequestLog.module == module)
    if method:
        query = query.filter(RequestLog.method == method)
        
    # Date range filtering
    if from_date:
        query = query.filter(RequestLog.timestamp >= from_date)
    if to_date:
        query = query.filter(RequestLog.timestamp <= to_date)
    else:
        # Default to now if to_date not provided
        query = query.filter(RequestLog.timestamp <= datetime.now(UTC))
        
    # Limit results
    query = query.limit(limit)
    
    result = await session.execute(query)
    logs = result.scalars().all()
    
    return logs

@router.get("/request/{request_id}", response_model=RequestLogResponse)
async def get_request_details(
    request_id: str,
    session: AsyncSession = Depends(get_repository_session),
    _: dict = Depends(get_admin_user),  # Admin access only
):
    """Get detailed information about a specific request by ID."""
    result = await session.execute(
        select(RequestLog).filter(RequestLog.request_id == request_id)
    )
    log = result.scalars().first()
    
    if not log:
        raise HTTPException(status_code=404, detail=f"Request ID {request_id} not found")
    
    return log

@router.get("/metrics", response_model=RequestMetrics)
async def get_request_metrics(
    days: int = Query(7, ge=1, le=30),
    session: AsyncSession = Depends(get_repository_session),
    _: dict = Depends(get_admin_user),
) -> RequestMetrics:
    """Get request metrics for dashboard."""
    cutoff_date = datetime.now(UTC) - timedelta(days=days)
    
    # Total requests
    total_result = await session.execute(
        select(func.count(RequestLog.id)).where(RequestLog.timestamp >= cutoff_date)
    )
    total_requests = total_result.scalar_one_or_none() or 0
    
    # Error rate
    error_result = await session.execute(
        select(func.count(RequestLog.id)).where(
            RequestLog.timestamp >= cutoff_date,
            RequestLog.status_code >= 400
        )
    )
    error_requests = error_result.scalar_one_or_none() or 0
    error_rate = round((error_requests / total_requests * 100) if total_requests else 0, 2)
    
    # Average response time
    time_result = await session.execute(
        select(func.avg(RequestLog.duration_ms)).where(RequestLog.timestamp >= cutoff_date)
    )
    avg_response_time = round(time_result.scalar_one_or_none() or 0, 2)
    
    # Requests by day
    day_results = await session.execute(
        select(
            func.date(RequestLog.timestamp).label("day"),
            func.count(RequestLog.id).label("count")
        ).where(
            RequestLog.timestamp >= cutoff_date
        ).group_by(
            func.date(RequestLog.timestamp)
        ).order_by(
            func.date(RequestLog.timestamp)
        )
    )
    requests_by_day = {
        str(day): count for day, count in day_results.all()
    }
    
    # Most common errors
    error_results = await session.execute(
        select(
            RequestLog.exception,
            func.count(RequestLog.id).label("count")
        ).where(
            RequestLog.timestamp >= cutoff_date,
            RequestLog.exception.is_not(None)
        ).group_by(
            RequestLog.exception
        ).order_by(
            desc("count")
        ).limit(5)
    )
    common_errors = {
        str(error): count for error, count in error_results.all()
    }
    
    return {
        "total_requests": total_requests,
        "error_rate": error_rate,
        "avg_response_time": avg_response_time,
        "requests_by_day": requests_by_day,
        "common_errors": common_errors
    }

@router.get("/endpoints", response_model=List[EndpointAnalytics])
async def get_endpoint_analytics(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=5, le=100),
    session: AsyncSession = Depends(get_repository_session),
    _: dict = Depends(get_admin_user),
) -> List[EndpointAnalytics]:
    """Get analytics for the most used endpoints."""
    cutoff_date = datetime.now(UTC) - timedelta(days=days)
    
    # Most used endpoints
    endpoint_results = await session.execute(
        select(
            RequestLog.path,
            RequestLog.method,
            func.count(RequestLog.id).label("count"),
            func.avg(RequestLog.duration_ms).label("avg_duration"),
            func.min(RequestLog.duration_ms).label("min_duration"),
            func.max(RequestLog.duration_ms).label("max_duration"),
            func.sum(
                func.case(
                    (RequestLog.status_code >= 400, 1),
                    else_=0
                )
            ).label("error_count")
        ).where(
            RequestLog.timestamp >= cutoff_date
        ).group_by(
            RequestLog.path,
            RequestLog.method
        ).order_by(
            desc("count")
        ).limit(limit)
    )
    
    endpoints = []
    for row in endpoint_results:
        total = row.count
        error_count = row.error_count
        error_rate = round((error_count / total * 100) if total else 0, 2)
        
        endpoints.append({
            "path": row.path,
            "method": row.method,
            "request_count": total,
            "avg_duration_ms": round(row.avg_duration, 2),
            "min_duration_ms": row.min_duration,
            "max_duration_ms": row.max_duration,
            "error_count": error_count,
            "error_rate": error_rate
        })
    
    return endpoints

# Endpoint management routes
@router.get("/endpoints/registry", dependencies=[Depends(endpoint_control())])
async def list_endpoint_registry():
    """
    List all registered endpoints with their status.
    
    Returns:
        Dictionary of endpoints with their status information
    """
    return {
        "endpoints": get_all_endpoints(),
        "feature_flags": settings.FEATURE_FLAGS
    }

@router.patch("/endpoints/{path:path}", dependencies=[Depends(endpoint_control())])
async def update_endpoint(path: str, update: EndpointStatusUpdate):
    """
    Update the enabled status and description of an endpoint.
    
    Args:
        path: The endpoint path
        update: The update data
        
    Returns:
        The updated endpoint info
    """
    if update.enabled:
        enable_endpoint(path)
    else:
        disable_endpoint(path)
    
    # Update description if provided
    if update.description is not None and path in ENDPOINT_REGISTRY:
        ENDPOINT_REGISTRY[path]["description"] = update.description
    
    return {
        "path": path,
        "enabled": update.enabled,
        "description": update.description
    }

# Consolidated bulk update endpoint
@router.post("/endpoints/bulk", dependencies=[Depends(get_admin_user)])
async def bulk_endpoint_update(update: BulkEndpointUpdate):
    """
    Bulk enable or disable endpoints by pattern.
    
    Args:
        update: Bulk update parameters including pattern and enabled status
        
    Returns:
        Success message with list of matched endpoints
    """
    count = bulk_update_endpoints(update.pattern, update.enabled)
    
    return {
        "pattern": update.pattern,
        "enabled": update.enabled,
        "updated_count": count,
        "description": update.description
    }

# Feature flag management
@router.get("/feature-flags", dependencies=[Depends(endpoint_control())])
async def get_feature_flags():
    """
    Get all feature flags.
    
    Returns:
        Dictionary of feature flags
    """
    return {
        "feature_flags": settings.FEATURE_FLAGS
    }

@router.patch("/feature-flags/{flag_name}", dependencies=[Depends(endpoint_control())])
async def update_feature_flag(flag_name: str, update: FeatureFlagUpdate):
    """
    Update a feature flag's value.
    
    Args:
        flag_name: The name of the feature flag to update
        update: The update data with the new value
        
    Returns:
        Updated feature flag
    """
    # Set the feature flag to the new value
    settings.set_feature_flag(flag_name, update.value)
    
    return {
        "flag_name": flag_name,
        "value": update.value,
        "description": update.description
    }

@router.post("/refresh-domains", dependencies=[Depends(endpoint_control())])
async def admin_refresh_domains():
    """
    Refresh domains and update feature flags.
    
    This is useful after adding new domains to the project.
    
    Returns:
        Updated domains and feature flags
    """
    # Refresh domains
    domains = settings.refresh_domains()
    
    return {
        "status": "success",
        "message": "Domains refreshed successfully",
        "domains": domains,
        "feature_flags": settings.FEATURE_FLAGS,
        "path_prefixes": settings.PATH_PREFIX_FEATURE_FLAGS
    }

@router.get("/debug/endpoint-registry")
async def debug_endpoint_registry(
    admin_user: dict = Depends(get_admin_user)
):
    """Get the current endpoint registry for debugging purposes (admin only)."""
    return get_registered_endpoints()

@router.get("/endpoint-status/{path:path}")
async def check_endpoint_status(
    path: str,
    admin_user: dict = Depends(get_admin_user)
):
    """Check if a specific endpoint is enabled or disabled (admin only)."""
    # Check both with and without method
    path_with_method = path
    path_without_method = path.split(":", 1)[0] if ":" in path else path
    
    # Check various combinations (with method, without method)
    results = {
        "exact_path": path,
        "is_enabled_exact": is_endpoint_enabled(path),
        "in_registry_exact": path in ENDPOINT_REGISTRY,
        "path_without_method": path_without_method,
        "is_enabled_without_method": is_endpoint_enabled(path_without_method),
        "in_registry_without_method": path_without_method in ENDPOINT_REGISTRY,
    }
    
    # Add method-specific variations for common HTTP methods
    if ":" not in path:
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
        method_variations = {}
        for method in methods:
            path_with_method = f"{path}:{method}"
            method_variations[method] = {
                "path": path_with_method,
                "is_enabled": is_endpoint_enabled(path_with_method),
                "in_registry": path_with_method in ENDPOINT_REGISTRY
            }
        results["method_variations"] = method_variations
    
    return results 

@router.get("/controllable-endpoints", response_model=List[EndpointRegistryItem])
async def get_controllable_endpoints(
    _: dict = Depends(get_admin_user),
) -> List[EndpointRegistryItem]:
    """
    Get all controllable endpoints and their current status.
    
    This endpoint returns information about all endpoints that have been registered
    with the controllable_endpoint decorator, including their enabled status and descriptions.
    """
    endpoints = get_all_endpoints()
    return [
        EndpointRegistryItem(
            path=path,
            enabled=info["enabled"],
            description=info["description"] or ""
        )
        for path, info in endpoints.items()
    ]

@router.post("/controllable-endpoints/{endpoint_path}/enable", response_model=EndpointStatusUpdate)
async def enable_controllable_endpoint(
    endpoint_path: str,
    _: dict = Depends(get_admin_user),
) -> EndpointStatusUpdate:
    """Enable a controllable endpoint by its path."""
    enable_endpoint(endpoint_path)
    return EndpointStatusUpdate(path=endpoint_path, enabled=True)

@router.post("/controllable-endpoints/{endpoint_path}/disable", response_model=EndpointStatusUpdate)
async def disable_controllable_endpoint(
    endpoint_path: str,
    _: dict = Depends(get_admin_user),
) -> EndpointStatusUpdate:
    """Disable a controllable endpoint by its path."""
    disable_endpoint(endpoint_path)
    return EndpointStatusUpdate(path=endpoint_path, enabled=False) 