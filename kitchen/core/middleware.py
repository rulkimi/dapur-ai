import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .context import set_request_id, reset_request_id, get_request_id
import logging
import time
from datetime import datetime, UTC
import traceback
from typing import Callable, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db_session
from db.models.request_log import RequestLog
from starlette.datastructures import FormData
import json
from .config import settings

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that adds request ID tracking to all requests."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Extract request ID from header if provided, otherwise generate new UUID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set request ID in context
        set_request_id(request_id)
        
        # Start timing the request
        start_time = time.time()
        
        # Prepare log record
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }
        
        # Initial request log
        logger.info(f"Request started: {request.method} {request.url.path}", 
                    extra=log_data)
        
        # Process response with error handling
        status_code = 500
        exception_detail = None
        
        # Check if the current path is in the sensitive paths list
        is_sensitive = self._is_sensitive_path(request.url.path)
        
        # Pre-process request body for logging before the body is consumed
        request_body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                content_type = request.headers.get("content-type", "")
                # Don't attempt to log these content types since they might contain 
                # binary data or be too large
                skip_content_types = [
                    "multipart/form-data",
                    "application/octet-stream"
                ]
                
                should_skip = any(ct in content_type for ct in skip_content_types)
                
                # Don't log request body for sensitive paths
                if is_sensitive:
                    request_body = {"redacted": "sensitive data"}
                elif not should_skip:
                    if "application/json" in content_type:
                        # Clone the request body for json data
                        body_bytes = await request.body()
                        request_body = json.loads(body_bytes.decode()) if body_bytes else None
                        
                        # Create a new request object with the same body
                        request = Request(
                            request.scope,
                            receive=request._receive,
                            send=request._send
                        )
                        
                    elif "application/x-www-form-urlencoded" in content_type:
                        # For form data, we'll log it after the fact since
                        # there's no good way to clone form data without affecting dependencies
                        pass
            except Exception as e:
                # If we can't parse the body, log the error
                request_body = {
                    "non_serializable": "Request body couldn't be parsed",
                    "error": str(e)
                }
        
        try:
            # Process the request
            response = await call_next(request)
            status_code = response.status_code
            
            # Add request ID to response header
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            logger.exception("Unhandled exception in request", extra=log_data)
            exception_detail = str(e)
            raise
        finally:
            # Calculate request duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Complete the log data
            log_data.update({
                "status_code": status_code,
                "duration_ms": duration_ms,
                "exception": exception_detail,
            })
            
            # Log request completion
            log_level = logging.ERROR if status_code >= 500 else (
                logging.WARNING if status_code >= 400 else logging.INFO
            )
            logger.log(
                log_level,
                f"Request completed: {request.method} {request.url.path} - "
                f"Status: {status_code}, Duration: {duration_ms}ms",
                extra=log_data
            )
            
            # Store request in database
            try:
                # Use a new session for request logging to ensure it commits even if 
                # the main request's session is rolled back
                async with get_db_session() as session:
                    session: AsyncSession
                    
                    # Get user_id from request state if authenticated
                    user_id = None
                    if hasattr(request.state, "user"):
                        user_id = getattr(request.state.user, "id", None)
                    
                    # Create log entry with the pre-captured request body
                    # Ensure timestamp is timezone-aware
                    current_time = datetime.now(UTC)
                    
                    try:
                        # Safely create and add request log
                        request_log = RequestLog(
                            request_id=request_id,
                            timestamp=current_time,
                            method=request.method,
                            path=request.url.path,
                            status_code=status_code,
                            duration_ms=duration_ms,
                            user_id=user_id,
                            ip_address=request.client.host if request.client else None,
                            user_agent=request.headers.get("User-Agent"),
                            request_data=request_body,
                            exception=exception_detail,
                        )
                        
                        session.add(request_log)
                        await session.commit()
                    except Exception as model_error:
                        # Handle specific errors that might occur when creating the model
                        await session.rollback()
                        error_traceback = traceback.format_exc()
                        logger.error(
                            f"Error creating request log model: {str(model_error)}", 
                            extra={
                                "request_id": request_id,
                                "error_type": type(model_error).__name__,
                                "traceback": error_traceback
                            }
                        )
                        # Re-raise for outer exception handler
                        raise
            except Exception as db_e:
                # Don't let database logging errors affect the response
                error_traceback = traceback.format_exc()
                logger.error(
                    f"Failed to save request log: {str(db_e)}", 
                    extra={
                        "request_id": request_id,
                        "error_type": type(db_e).__name__,
                        "error_detail": str(db_e),
                        "traceback": error_traceback
                    }
                )
            
            # Reset context
            reset_request_id()
            
    def _is_sensitive_path(self, path: str) -> bool:
        """
        Check if the given path is considered sensitive and should have its request data redacted.
        
        Args:
            path: The request path to check
            
        Returns:
            bool: True if the path is sensitive, False otherwise
        """
        # Check exact path matches
        if path in settings.SENSITIVE_PATHS:
            return True
            
        # Check path prefixes
        for prefix in settings.SENSITIVE_PATH_PREFIXES:
            if path.startswith(prefix):
                return True
                
        return False 