import uuid
from fastapi import Request, HTTPException
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
from starlette.responses import JSONResponse, Response
import re
from .dependencies import ENDPOINT_REGISTRY, is_endpoint_enabled

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

class FeatureFlagMiddleware(BaseHTTPMiddleware):
    """Middleware that checks feature flags for routes and returns 404 if disabled."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get the path of the request
        path = request.url.path
        method = request.method
        
        # Add enhanced logging for debugging
        logger.info(f"FeatureFlagMiddleware processing request: {method} {path}")
        
        # Check if there are any path-specific feature flags
        disabled = self._check_path_against_feature_flags(path)
        
        if disabled:
            logger.info(f"Path {path} - Disabled by feature flag")
        else:
            logger.debug(f"Path {path} - Feature flag check: enabled")
        
        # Now also check the dynamic endpoint registry
        logger.debug(f"ENDPOINT_REGISTRY entries: {len(ENDPOINT_REGISTRY)}")
        
        # Check for path with method suffix
        path_with_method = f"{path}:{method}"
        if path_with_method in ENDPOINT_REGISTRY:
            logger.debug(f"Found exact match for {path_with_method} in registry: enabled={ENDPOINT_REGISTRY[path_with_method]['enabled']}")
            if not ENDPOINT_REGISTRY[path_with_method]['enabled']:
                disabled = True
                logger.info(f"Path {path_with_method} - Disabled by exact match in endpoint registry")
        
        # Also check for path without method suffix (legacy)
        elif path in ENDPOINT_REGISTRY:
            logger.debug(f"Found exact match for {path} in registry: enabled={ENDPOINT_REGISTRY[path]['enabled']}")
            if not ENDPOINT_REGISTRY[path]['enabled']:
                disabled = True
                logger.info(f"Path {path} - Disabled by exact match in endpoint registry")
            
        # Also check if the path matches any registered endpoint patterns (regex)
        if not disabled:
            for registered_path, info in ENDPOINT_REGISTRY.items():
                # Strip method suffix for comparison if present
                base_registered_path = registered_path.split(':', 1)[0] if ':' in registered_path else registered_path
                
                # Check if the registered path is a regex pattern and matches the current path
                if base_registered_path.startswith("^") and re.match(base_registered_path, path) and not info["enabled"]:
                    disabled = True
                    logger.info(f"Path {path} - Disabled by pattern match: {base_registered_path}")
                    break
                
                # Special case for wildcard paths (non-regex)
                if "{" in base_registered_path and "}" in base_registered_path:
                    # Skip the onboarding endpoint for wildcard matching
                    if path == "/api/v1/queries/onboarding":
                        logger.info(f"Path {path} - Skipping wildcard pattern match for onboarding endpoint")
                        continue
                        
                    # Convert wildcard path to regex pattern
                    pattern = base_registered_path.replace("{", "(?P<").replace("}", ">[^/]+)")
                    if re.match(pattern, path) and not info["enabled"]:
                        disabled = True
                        logger.info(f"Path {path} - Disabled by wildcard pattern match: {base_registered_path}")
                        break
        
        # If the path is disabled, return a 404 Response
        if disabled:
            logger.info(f"Path {path} - Access rejected by feature flag middleware")
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )
        
        # Otherwise, proceed with the request
        return await call_next(request)
    
    def _check_path_against_feature_flags(self, path: str) -> bool:
        """
        Check if a path should be disabled based on feature flags.
        
        Args:
            path: The request path to check
            
        Returns:
            bool: True if the path should be disabled, False otherwise
        """
        # Special case for the onboarding endpoint
        if path == "/api/v1/queries/onboarding":
            logger.info(f"Path {path} - Explicitly enabled as onboarding endpoint")
            return False
            
        # First check if there are direct path mappings in the settings
        path_flags = settings.PATH_FEATURE_FLAGS or {}
        
        # Check for exact path match
        if path in path_flags:
            flag_name = path_flags[path]
            if not settings.get_feature_flag(flag_name, True):
                logger.info(f"Path {path} disabled by exact path match - flag: {flag_name}")
                return True
        
        # Check for path prefix matches
        for prefix, flag_name in settings.PATH_PREFIX_FEATURE_FLAGS.items():
            if path.startswith(prefix):
                if not settings.get_feature_flag(flag_name, True):
                    logger.info(f"Path {path} disabled by prefix match: {prefix} - flag: {flag_name}")
                    return True
                    
        return False

    @staticmethod
    def modify_openapi(app: "FastAPI") -> None:
        """
        Modify the OpenAPI generation to hide disabled endpoints.
        
        This method should be called during application startup.
        
        Args:
            app: The FastAPI application instance
        """
        original_openapi = app.openapi
        
        def filtered_openapi() -> dict:
            """Custom OpenAPI schema generator that filters out disabled endpoints."""
            if app.openapi_schema:
                # Return cached schema if we have it
                return app.openapi_schema
                
            # Generate the standard schema
            openapi_schema = original_openapi()
            
            # Create a new paths dictionary excluding disabled endpoints
            paths = openapi_schema.get("paths", {})
            filtered_paths = {}
            
            # Include only enabled paths
            for path, path_item in paths.items():
                # API paths might not include the API prefix, so check with and without
                full_path = f"{settings.API_V1_STR}{path}" if not path.startswith("/api") else path
                
                # Check each HTTP method for this path
                methods_enabled = {}
                for method in path_item.keys():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        # Check path with method suffix
                        path_with_method = f"{full_path}:{method.upper()}"
                        if path_with_method in ENDPOINT_REGISTRY:
                            methods_enabled[method] = ENDPOINT_REGISTRY[path_with_method]["enabled"]
                        else:
                            # Fall back to checking the path without method suffix
                            methods_enabled[method] = is_endpoint_enabled(full_path)
                
                # If any method is enabled, include the path with only the enabled methods
                if any(methods_enabled.values()):
                    filtered_path_item = {}
                    for method, enabled in methods_enabled.items():
                        if enabled:
                            filtered_path_item[method] = path_item[method]
                    
                    if filtered_path_item:
                        filtered_paths[path] = filtered_path_item
            
            # Replace the paths in the schema
            openapi_schema["paths"] = filtered_paths
            
            # Cache and return the filtered schema
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        
        # Replace the original openapi method with our filtered version
        app.openapi = filtered_openapi