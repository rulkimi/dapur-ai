import asyncio
import sys
import os
import importlib
import inspect
from fastapi import APIRouter

# Fix for Windows asyncio loop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.exceptions import register_exception_handlers
from core.dependencies import conditional_router, register_endpoint, is_endpoint_enabled, ControllableAPIRouter, ENDPOINT_REGISTRY
from db.repository import DatabaseRepository
from db.base import register_engine_events
# Remove individual router imports as we'll discover them automatically
import logging
from core.logging import configure_logging
from core.middleware import RequestIDMiddleware, FeatureFlagMiddleware
import traceback
from sqlalchemy import text


# Configure logging with request ID support
logger = configure_logging()

# Function to automatically discover and register domain routers
def discover_domain_routers() -> dict[str, dict]:
    """
    Automatically discover and register all domain routers.
    
    Returns:
        A dictionary mapping domain names to their router info
    """
    # First refresh domains to ensure we have the latest
    domains = settings.refresh_domains()
    logger.info(f"Discovered domains: {domains}")
    
    domain_routers = {}
    domains_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains")
    
    # Check if domains directory exists
    if not os.path.isdir(domains_dir):
        logger.warning(f"Domains directory not found at {domains_dir}")
        return domain_routers
        
    # List all domain directories
    for domain_name in os.listdir(domains_dir):
        domain_path = os.path.join(domains_dir, domain_name)
        
        # Skip if not a directory
        if not os.path.isdir(domain_path):
            continue
            
        # Skip if domain has no routers.py file
        router_path = os.path.join(domain_path, "routers.py")
        if not os.path.isfile(router_path):
            logger.warning(f"Domain {domain_name} has no routers.py file")
            continue
            
        try:
            # Import the router module
            module_path = f"domains.{domain_name}.routers"
            module = importlib.import_module(module_path)
            
            # Look for an APIRouter instance
            for name, obj in inspect.getmembers(module):
                if (isinstance(obj, APIRouter) or isinstance(obj, ControllableAPIRouter)) and name == "router":
                    # Create feature flag name
                    flag_name = f"enable_{domain_name}_endpoints"
                    
                    # If it's not already a ControllableAPIRouter, create one with the same settings
                    if not isinstance(obj, ControllableAPIRouter):
                        logger.info(f"Upgrading router for domain {domain_name} to ControllableAPIRouter")
                        controllable_router = ControllableAPIRouter(
                            prefix=obj.prefix, 
                            tags=obj.tags,
                            dependencies=obj.dependencies,
                        )
                        
                        # Copy all routes from the original router
                        for route in obj.routes:
                            # Extract necessary arguments for add_api_route
                            path = route.path
                            # Remove the router prefix to avoid duplication
                            if obj.prefix and path.startswith(obj.prefix):
                                path = path[len(obj.prefix):]
                                
                            # Get the endpoint function
                            endpoint = route.endpoint
                            
                            # Extract additional route properties
                            route_kwargs = {
                                "response_model": getattr(route, "response_model", None),
                                "status_code": getattr(route, "status_code", 200),
                                "methods": route.methods,
                                "dependencies": route.dependencies,
                                "summary": route.summary,
                                "description": route.description,
                                "response_description": route.response_description,
                                "tags": route.tags,
                                "include_in_schema": route.include_in_schema,
                            }
                            
                            # Remove None values which should use defaults
                            route_kwargs = {k: v for k, v in route_kwargs.items() if v is not None}
                            
                            # Add the route to the controllable router
                            controllable_router.add_api_route(path, endpoint, **route_kwargs)
                            
                        # Use the new controllable router instead
                        obj = controllable_router
                        
                        # Replace the router in the module for future reference
                        setattr(module, name, obj)
                    
                    # Register the router with its domain name
                    domain_routers[domain_name] = {
                        "router": obj,
                        "flag_name": flag_name
                    }
                    logger.info(f"Discovered domain router: {domain_name}")
                    break
            else:
                logger.warning(f"No router found in domain {domain_name}")
        except Exception as e:
            logger.error(f"Error importing router for domain {domain_name}: {str(e)}")
            logger.error(traceback.format_exc())
    
    return domain_routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Startup: Initialize database connection
    try:
        logger.info("Initializing database...")
        # Import sync module to ensure it's available
        from db.sync import ensure_database_exists, sync_models_with_db
        
        # Initialize the database with better error handling
        try:
            logger.info("Checking database connection...")
            db_initialized = await DatabaseRepository.init_db()
            if db_initialized:
                logger.info("Database initialized successfully")
            else:
                logger.warning("Database initialization may not have completed successfully. Check connection settings.")
                
            # Verify database connection by performing a simple query
            from db.repository import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("Database connection verified successfully")
                else:
                    logger.warning("Database connection test returned unexpected result")
        except Exception as db_error:
            error_trace = traceback.format_exc()
            logger.error(f"Database connection error: {str(db_error)}")
            logger.error(f"Error details: {error_trace}")
            logger.warning("Application will continue, but database operations may fail")
        
        # Register engine-level event listeners after database initialization
        from db.repository import engine
        register_engine_events(engine)
        logger.info("Event listeners registered for database engine")
        
        # Set feature flags discovery complete flag for proper OpenAPI generation
        app.state.domains_discovered = True
        
        # Register all endpoints from the OpenAPI schema
        logger.info("Registering endpoints from OpenAPI schema...")
        try:
            # Get the OpenAPI schema
            openapi_schema = app.openapi()
            
            # Register all paths from the schema
            for path, path_item in openapi_schema.get("paths", {}).items():
                for method in path_item:
                    if method.lower() in ("get", "post", "put", "delete", "patch"):
                        operation = path_item[method]
                        endpoint_path = path
                        description = operation.get("summary", "") or operation.get("description", "")
                        
                        # Get any tags for the operation
                        tags = operation.get("tags", [])
                        tag_str = ", ".join(tags) if tags else ""
                        
                        # Register the endpoint with a descriptive name
                        full_path = f"{settings.API_V1_STR}{endpoint_path}" if not endpoint_path.startswith("/api") else endpoint_path
                        register_endpoint(
                            path=full_path,
                            enabled=True,  # Default to enabled
                            description=f"{description} [{tag_str}]".strip()
                        )
                        logger.debug(f"Registered endpoint: {full_path}")
            
            logger.info(f"Registered {len(openapi_schema.get('paths', {}))} endpoints from OpenAPI schema")
            
            # Update route visibility based on endpoint registry
            logger.info("Updating route visibility...")
            update_route_visibility()
        except Exception as e:
            logger.error(f"Error registering endpoints: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Modify the OpenAPI schema to filter out disabled endpoints
        logger.info("Setting up OpenAPI filtering for disabled endpoints...")
        FeatureFlagMiddleware.modify_openapi(app)
        
        # Startup message
        logger.info(f"Application starting up - Environment: {settings.ENVIRONMENT}")
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Startup error: {str(e)}")
        logger.error(f"Error details: {error_trace}")
        # We don't re-raise the exception to allow the application to start
        # even if the database is not available initially
        
    yield
    
    # Shutdown
    logger.info("Application shutting down")
    # No need to explicitly close the engine as it will be handled by SQLAlchemy

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Register exception handlers
register_exception_handlers(app)

# Specifically enable the onboarding endpoint (overriding any wildcard matches)
# logger.info("Explicitly enabling the onboarding endpoint...")
# register_endpoint("/api/v1/queries/onboarding", enabled=True, description="User onboarding endpoint")

# Add middlewares - order matters! Feature flag middleware should be one of the first
app.add_middleware(FeatureFlagMiddleware)
app.add_middleware(RequestIDMiddleware)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "1.0.0"
    }

# Create a single API router with the API_V1_STR prefix
api_router = ControllableAPIRouter(prefix=settings.API_V1_STR)

# Automatically discover and include domain routers
logger.info("Discovering domain routers...")
domain_routers = discover_domain_routers()

# Register discovered domain routers
for domain_name, router_info in domain_routers.items():
    router = router_info["router"]
    flag_name = router_info["flag_name"]
    
    # Special case for auth router which should always be enabled
    if domain_name == "auth":
        logger.info(f"Including auth router (always enabled)")
        api_router.include_router(router)
    else:
        logger.info(f"Including conditional router for domain: {domain_name} with flag: {flag_name}")
        # Get default enabled value from settings if available, otherwise default to True
        default_enabled = settings.get_feature_flag(flag_name, True)
        
        # Include router with feature flag control
        api_router.include_router(
            conditional_router(
                router, 
                flag_name, 
                default_enabled=default_enabled
            )
        )

# Include the single api_router in the app
app.include_router(api_router)

# Helper function to register all routes with include_in_schema based on enabled status
def update_route_visibility():
    """
    Update route visibility based on feature flags and endpoint registry.
    This function should be called whenever feature flags or endpoint registry is updated.
    """
    try:
        # Iterate through all registered endpoints
        for endpoint_path, info in ENDPOINT_REGISTRY.items():
            enabled = info["enabled"]
            
            # Find all routes that match this endpoint
            for route in app.routes:
                # Skip routes without an endpoint
                if not hasattr(route, "endpoint"):
                    continue
                
                # Get the endpoint function  
                endpoint = route.endpoint
                
                # Skip if the endpoint doesn't have the controllable attribute
                if not hasattr(endpoint, "__controllable__"):
                    continue
                
                # Skip if the endpoint doesn't have an endpoint path
                if not hasattr(endpoint, "__endpoint_path__"):
                    continue
                    
                # Get the endpoint path from the route
                route_endpoint_path = endpoint.__endpoint_path__
                
                # If this route matches the endpoint we're checking
                if route_endpoint_path == endpoint_path:
                    # Update the include_in_schema property safely
                    if hasattr(route, "include_in_schema"):
                        route.include_in_schema = enabled
                    # We've found and updated the route, no need to continue searching
                    break
            
        logger.info("Route visibility updated")
    except Exception as e:
        logger.error(f"Error updating route visibility: {str(e)}")
        logger.error(traceback.format_exc())

# Update route visibility (will be called by the lifespan context)
update_route_visibility()

# Add admin endpoint to refresh domains
@app.post("/api/v1/admin/refresh-domains")
async def refresh_domains():
    """
    Admin endpoint to rediscover domains at runtime.
    This is useful when adding new domains without restarting the server.
    """
    # Refresh domains in dynamic settings
    domains = settings.refresh_domains()
    
    # Rediscover routers
    domain_routers = discover_domain_routers()
    
    # Update route visibility
    update_route_visibility()
    
    return {
        "status": "success",
        "message": "Domains refreshed successfully",
        "domains": domains,
        "discovered_routers": list(domain_routers.keys())
    }

# Add admin endpoint to view the endpoint registry
@app.get("/api/v1/admin/endpoints")
async def get_endpoints():
    """
    Admin endpoint to view the current endpoint registry.
    This is useful for debugging feature flag issues.
    """
    return {
        "status": "success",
        "endpoints": ENDPOINT_REGISTRY
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    ) 