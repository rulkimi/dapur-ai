from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta, UTC

from db.repository import get_repository_session
from db.models.request_log import RequestLog
from core.security import get_current_user
from .schemas import RequestLogResponse, EndpointAnalytics, RequestMetrics

router = APIRouter(prefix="/admin", tags=["admin"])

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

@router.get("/request-logs", response_model=List[RequestLogResponse])
async def get_request_logs(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    path: Optional[str] = None,
    status_code: Optional[int] = None,
    method: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = Query(None, description="Default is now"),
    limit: int = Query(100, le=1000),
    session: AsyncSession = Depends(get_repository_session),
    _: dict = Depends(get_admin_user),  # Ensure admin access
):
    """Query request logs for debugging."""
    query = select(RequestLog).order_by(desc(RequestLog.timestamp))
    
    # Apply filters
    if request_id:
        query = query.filter(RequestLog.request_id == request_id)
    if user_id:
        query = query.filter(RequestLog.user_id == user_id)
    if path:
        query = query.filter(RequestLog.path.contains(path))
    if status_code:
        query = query.filter(RequestLog.status_code == status_code)
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
):
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
):
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