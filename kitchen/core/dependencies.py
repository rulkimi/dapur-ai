from fastapi import Depends, HTTPException, status, APIRouter, Request
from .config import settings
from typing import Callable, Optional, Any, TypeVar, cast, List, Dict, Union
import re
import functools
from fastapi.routing import APIRoute

# Registry to track enabled/disabled status of individual endpoints
# Format: {"endpoint_path": {"enabled": bool, "description": str}}
ENDPOINT_REGISTRY = {}

def feature_flag(flag_name: str, default_enabled: bool = True) -> Callable:
    """
    Creates a dependency that checks if a feature flag is enabled.
    
    Args:
        flag_name: The name of the feature flag to check
        default_enabled: Default value if the flag is not found
        
    Returns:
        A dependency function that will raise HTTPException if the feature is disabled
        
    Example:
        @router.get("/endpoint", dependencies=[Depends(feature_flag("my_feature"))])
        async def my_endpoint():
            return {"message": "This endpoint is enabled"}
    """
    def check_feature_enabled() -> None:
        if not settings.FEATURE_FLAGS.get(flag_name, default_enabled):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint not found"
            )
    
    return check_feature_enabled

def route_enabled(flag_name: str, default_enabled: bool = True, path: str = None) -> bool:
    """
    Decorator for router.route() to conditionally register routes.
    This is an alternative to the feature_flag dependency when you want to
    completely disable route registration rather than returning a 404.
    
    This function now also checks the endpoint registry if a path is provided.
    
    Args:
        flag_name: The name of the feature flag to check 
        default_enabled: Default value if the flag is not found
        path: Optional path to check in the endpoint registry
        
    Returns:
        A boolean indicating whether the route should be enabled
        
    Example:
        @router.get("/endpoint", include_in_schema=route_enabled("my_feature"))
        async def my_endpoint():
            return {"message": "This endpoint is enabled"}
    """
    # Check feature flag first
    flag_enabled = settings.FEATURE_FLAGS.get(flag_name, default_enabled)
    
    # If the feature flag is disabled, return False
    if not flag_enabled:
        return False
        
    # If path is provided, also check the endpoint registry
    if path and path in ENDPOINT_REGISTRY:
        return ENDPOINT_REGISTRY[path]["enabled"]
        
    return flag_enabled

T = TypeVar('T')

def conditional_router(router: APIRouter, flag_name: str, default_enabled: bool = True) -> APIRouter:
    """
    Creates a router that will only register routes if the specified feature flag is enabled.
    
    This is a powerful approach that completely skips registering routes when disabled,
    rather than returning a 404 response.
    
    Args:
        router: Original APIRouter to wrap
        flag_name: The name of the feature flag to check
        default_enabled: Default value if the flag is not found
        
    Returns:
        Either the original router if feature is enabled, or a dummy router if disabled
        
    Example:
        base_router = APIRouter()
        # Create conditional router (only included if feature flag is True)
        admin_router = conditional_router(
            APIRouter(prefix="/admin", tags=["admin"]),
            "enable_admin_features"
        )
        
        # Add routes to admin_router
        @admin_router.get("/stats")
        async def get_stats():
            return {"status": "enabled"}
            
        # Include in main router
        base_router.include_router(admin_router)
    """
    # Return original router if feature is enabled
    if settings.FEATURE_FLAGS.get(flag_name, default_enabled):
        return router
    
    # Otherwise, return a dummy router that doesn't register routes
    dummy_router = APIRouter()
    
    # Override route registration methods to do nothing
    original_add_api_route = dummy_router.add_api_route
    
    def noop_add_api_route(*args: Any, **kwargs: Any) -> None:
        # Do nothing when registering routes
        pass
    
    # Replace add_api_route with our noop version
    dummy_router.add_api_route = noop_add_api_route  # type: ignore
    
    # Copy necessary attributes from original router
    dummy_router.prefix = router.prefix
    dummy_router.tags = router.tags
    
    # Return the dummy router that won't register any routes
    return dummy_router

# New functions for dynamic endpoint enabling/disabling

def register_endpoint(path: str, enabled: bool = True, description: str = "") -> None:
    """
    Register an endpoint with its enabled status in the global registry.
    
    Args:
        path: The full path of the endpoint (including prefix)
        enabled: Whether the endpoint is enabled by default
        description: Optional description of the endpoint
    """
    ENDPOINT_REGISTRY[path] = {
        "enabled": enabled,
        "description": description
    }

def is_endpoint_enabled(path: str) -> bool:
    """
    Check if an endpoint is enabled.
    
    Args:
        path: The full path of the endpoint (including prefix)
        
    Returns:
        bool: True if the endpoint is enabled, False otherwise
    """
    # If the path is not in the registry, default to True
    if path not in ENDPOINT_REGISTRY:
        return True
    
    return ENDPOINT_REGISTRY[path]["enabled"]

def enable_endpoint(path: str) -> None:
    """
    Enable an endpoint.
    
    Args:
        path: The full path of the endpoint (including prefix)
    """
    if path in ENDPOINT_REGISTRY:
        ENDPOINT_REGISTRY[path]["enabled"] = True
    else:
        register_endpoint(path, enabled=True)

def disable_endpoint(path: str) -> None:
    """
    Disable an endpoint.
    
    Args:
        path: The full path of the endpoint (including prefix)
    """
    if path in ENDPOINT_REGISTRY:
        ENDPOINT_REGISTRY[path]["enabled"] = False
    else:
        register_endpoint(path, enabled=False)

def toggle_endpoint(path: str) -> bool:
    """
    Toggle the enabled status of an endpoint.
    
    Args:
        path: The full path of the endpoint (including prefix)
    
    Returns:
        bool: The new enabled status
    """
    current_status = is_endpoint_enabled(path)
    if path in ENDPOINT_REGISTRY:
        ENDPOINT_REGISTRY[path]["enabled"] = not current_status
    else:
        register_endpoint(path, enabled=not current_status)
    
    return not current_status

def endpoint_control(path_pattern: str = None) -> Callable:
    """
    Creates a dependency that checks if an endpoint is enabled.
    This works with the dynamic endpoint registry.
    
    Args:
        path_pattern: Optional regex pattern to match against the endpoint path.
                     If not provided, the exact path will be used.
    
    Returns:
        A dependency function that will raise HTTPException if the endpoint is disabled
    
    Example:
        @router.get("/users", dependencies=[Depends(endpoint_control())])
        async def get_users():
            return {"message": "Endpoint is enabled"}
    """
    def check_endpoint_enabled(request) -> None:
        # Get the full path including router prefix
        full_path = request.scope["path"]
        
        # If path_pattern is provided, check if path matches the pattern
        if path_pattern:
            if re.match(path_pattern, full_path):
                for registered_path, info in ENDPOINT_REGISTRY.items():
                    if re.match(registered_path, full_path) and not info["enabled"]:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Endpoint not found"
                        )
        # Otherwise, check the exact path
        elif not is_endpoint_enabled(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint not found"
            )
    
    return check_endpoint_enabled 

# Create a custom APIRouter that tracks the routes added to it
class ControllableAPIRouter(APIRouter):
    """
    Custom APIRouter that tracks routes for use with controllable_endpoint decorator.
    """
    def add_api_route(self, path: str, endpoint: Callable, **kwargs):
        """Override add_api_route to track the route on the endpoint function."""
        # Get the include_in_schema parameter
        include_in_schema = kwargs.get("include_in_schema", True)
        
        # Extract the HTTP method from the kwargs - this is how FastAPI sets it
        methods = kwargs.get("methods", {"GET"})
        # Convert methods set to list or get the first item directly
        http_method = next(iter(methods)) if methods else "GET"
        
        # Check if endpoint has controllable attributes
        is_controllable = hasattr(endpoint, "__controllable__")
        if is_controllable:
            endpoint_path = None
            
            # Check if endpoint has a predefined path
            if hasattr(endpoint, "__endpoint_path__"):
                endpoint_path = getattr(endpoint, "__endpoint_path__")
            else:
                # Construct the path with the API prefix, router prefix and HTTP method
                router_prefix = self.prefix if hasattr(self, "prefix") else ""
                derived_path = f"/api/v1{router_prefix}{path}:{http_method}"
                endpoint_path = derived_path
                
                # Store the derived path on the endpoint
                setattr(endpoint, "__endpoint_path__", endpoint_path)
            
            # Get enabled status and description
            enabled = getattr(endpoint, "__enabled__", True)
            description = getattr(endpoint, "__description__", "")
            
            # Register the endpoint in the registry
            register_endpoint(endpoint_path, enabled, description)
            
            # Update include_in_schema based on endpoint enabled status
            include_in_schema = enabled
            kwargs["include_in_schema"] = include_in_schema
        
        # Call the parent add_api_route
        route = super().add_api_route(path, endpoint, **kwargs)
        
        # Store the route and routing information on the endpoint for future reference
        setattr(endpoint, "__route_set__", route)
        setattr(endpoint, "__http_method__", http_method)
        setattr(endpoint, "__router_path__", path)
        setattr(endpoint, "__router_prefix__", self.prefix if hasattr(self, "prefix") else "")
        
        # If this is a wrapped function, also set attributes on the original function
        if hasattr(endpoint, "__wrapped__"):
            wrapped = getattr(endpoint, "__wrapped__")
            setattr(wrapped, "__route_set__", route)
            setattr(wrapped, "__http_method__", http_method)
            setattr(wrapped, "__router_path__", path)
            setattr(wrapped, "__router_prefix__", self.prefix if hasattr(self, "prefix") else "")
            
            # If controllable, also copy those attributes
            if is_controllable and hasattr(endpoint, "__endpoint_path__"):
                setattr(wrapped, "__endpoint_path__", getattr(endpoint, "__endpoint_path__"))
                
        return route

# Patch the decorator to explicitly clear any route information when applied
def controllable_endpoint(
    path: str = None, 
    enabled: bool = True, 
    description: str = ""
) -> Callable:
    """
    Decorator to register an endpoint in the registry and make it controllable.
    
    This decorator should be used AFTER the FastAPI route decorator but BEFORE the endpoint
    function definition. If the endpoint is disabled, it will be completely hidden from the
    OpenAPI documentation and will return a 404 when accessed.
    
    Args:
        path: Optional override for the endpoint path (if not provided, will be automatically 
            derived from the router path and HTTP method)
        enabled: Initial enabled status
        description: Description of the endpoint
        
    Returns:
        The original endpoint function or a function that returns 404 if disabled
        
    Example:
        @router.get("/users/{user_id}")
        @controllable_endpoint(description="Get user by ID")  # Path will be auto-derived
        async def get_user(user_id: int, request: Request):
            return {"user_id": user_id}
    """
    def decorator(func: Callable) -> Callable:
        # Get the endpoint path from the function
        endpoint_path = path
        
        # Store it for later if it was provided manually
        if endpoint_path:
            # Ensure the path has a method suffix if not already present
            if ":" not in endpoint_path:
                # Try to infer the method from the function name
                method = None
                func_name = func.__name__.lower()
                if "get" in func_name:
                    method = "GET"
                elif "post" in func_name:
                    method = "POST"
                elif "put" in func_name:
                    method = "PUT"
                elif "delete" in func_name:
                    method = "DELETE"
                elif "patch" in func_name:
                    method = "PATCH"
                
                if method:
                    endpoint_path = f"{endpoint_path}:{method}"
            
            # Register the endpoint
            register_endpoint(endpoint_path, enabled, description)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs if available
            request = next((arg for arg in args if isinstance(arg, Request)), 
                          kwargs.get('request'))
            
            # If we have a request, we can dynamically check if the endpoint is enabled
            if request:
                # Get the actual path from the request
                actual_path = request.scope["path"]
                
                # Get the HTTP method
                http_method = request.scope["method"]
                
                # Use the stored path if available, otherwise derive from the request
                check_path = None
                if endpoint_path:
                    check_path = endpoint_path
                elif hasattr(wrapper, "__endpoint_path__"):
                    # Try to get the path from the wrapper if it was set during route registration
                    check_path = getattr(wrapper, "__endpoint_path__")
                else:
                    # Derive the path from the request
                    router_prefix = ""
                    # Extract router prefix from the path if possible
                    for prefix in ["/queries", "/auth", "/admin", "/profiles"]:  # Add common prefixes
                        if actual_path.startswith(prefix):
                            router_prefix = prefix
                            break
                    
                    # Construct the path with prefix
                    api_path = f"/api/v1{actual_path}:{http_method}"
                    check_path = api_path
                
                # If the check_path doesn't include the method and doesn't end with a method suffix
                # append the method for better distinction between endpoints at the same URL
                if check_path and ":" not in check_path:
                    check_path = f"{check_path}:{http_method}"
                
                # Register the endpoint if not already registered
                if check_path and check_path not in ENDPOINT_REGISTRY:
                    register_endpoint(check_path, enabled, description)
                    
                # Check if the endpoint is enabled
                if check_path and not is_endpoint_enabled(check_path):
                    # Return 404 if the endpoint is disabled
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Endpoint not found"
                    )
            
            # If enabled or no request available (can't check), call the original function
            return await func(*args, **kwargs)
        
        # Store the controllable attributes on the wrapper function
        setattr(wrapper, "__controllable__", True)
        setattr(wrapper, "__enabled__", enabled)
        setattr(wrapper, "__description__", description)
        if endpoint_path:
            setattr(wrapper, "__endpoint_path__", endpoint_path)
        
        return wrapper
    
    return decorator

# Helper function to check if an endpoint should be included in the OpenAPI schema
def get_include_in_schema(path: str) -> bool:
    """
    Check if an endpoint should be included in the OpenAPI schema based on its enabled status.
    
    Args:
        path: The full path of the endpoint
        
    Returns:
        bool: True if the endpoint is enabled, False otherwise
    """
    # First check if the endpoint is registered
    if path in ENDPOINT_REGISTRY:
        return ENDPOINT_REGISTRY[path]["enabled"]
    
    # If not registered yet, register it as enabled by default
    register_endpoint(path, True, "")
    return True

# Get all endpoints with their status
def get_all_endpoints() -> dict:
    """
    Get all registered endpoints with their enabled status and descriptions.
    
    Returns:
        dict: Dictionary of endpoints with their status information
        
    Example:
        {
            "/api/v1/users": {
                "enabled": True,
                "description": "List all users",
                "feature_flag": "enable_users_endpoints"
            },
            ...
        }
    """
    # Create a copy of the registry to avoid modifying the original
    endpoints = {}
    
    for path, info in ENDPOINT_REGISTRY.items():
        # Create a copy of the endpoint info
        endpoint_info = info.copy()
        
        # Try to determine which feature flag controls this endpoint
        flag_name = None
        
        # Check if the path is in PATH_FEATURE_FLAGS
        for prefix, flag in settings.PATH_PREFIX_FEATURE_FLAGS.items():
            if path.startswith(prefix):
                flag_name = flag
                break
        
        # Add the feature flag to the endpoint info
        if flag_name:
            endpoint_info["feature_flag"] = flag_name
        
        endpoints[path] = endpoint_info
    
    return endpoints

# Bulk enable/disable endpoints by pattern
def bulk_update_endpoints(pattern: str, enabled: bool) -> int:
    """
    Enable or disable all endpoints matching a pattern.
    
    Args:
        pattern: Regex pattern to match endpoint paths
        enabled: Whether to enable or disable the endpoints
        
    Returns:
        int: Number of endpoints updated
    """
    count = 0
    pattern_re = re.compile(pattern)
    
    for path in ENDPOINT_REGISTRY.keys():
        if pattern_re.match(path):
            if enabled:
                enable_endpoint(path)
            else:
                disable_endpoint(path)
            count += 1
    
    return count 

def get_registered_endpoints() -> dict:
    """
    Get all registered endpoints and their status.
    
    Returns:
        dict: Dictionary with endpoint paths as keys and their status as values
    """
    return {path: {"enabled": info["enabled"], "description": info.get("description", "")} 
            for path, info in ENDPOINT_REGISTRY.items()} 