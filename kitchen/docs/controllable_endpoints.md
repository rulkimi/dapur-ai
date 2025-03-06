# Controllable Endpoints Documentation

## Overview

The `@controllable_endpoint` decorator provides a mechanism to dynamically enable or disable API endpoints at runtime without requiring application restarts. This feature allows for fine-grained control over endpoint availability, making it useful for feature flagging, maintenance modes, or gradual rollouts of new functionality.

## Key Features

- Runtime enabling/disabling of endpoints
- Auto-hiding disabled endpoints from OpenAPI documentation
- 404 responses for disabled endpoints
- Admin interface for managing endpoints
- Self-registration of endpoints in the global registry
- Compatible with FastAPI's existing routing system

## Required Usage

**All domain routes must use the `@controllable_endpoint` decorator to ensure proper control and management.**

## How to Apply the Decorator

The decorator must be applied in the correct order relative to other decorators:

```python
@router.get("/path")  # FastAPI route decorator FIRST
@controllable_endpoint(description="Endpoint description")  # controllable_endpoint SECOND
async def your_endpoint_function(request: Request):
    # Your endpoint logic here
    return {"result": "data"}
```

## Parameters

The `@controllable_endpoint` decorator accepts the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | `None` | Optional explicit path for the endpoint. If not provided, the path will be auto-derived from the router path and HTTP method. |
| `enabled` | `bool` | `True` | Initial enabled status for the endpoint. |
| `description` | `str` | `""` | Description of the endpoint functionality. |

## Path Specification Options

### Option 1: Auto-derived Path (Recommended)

Let the system automatically derive the path based on the router path and HTTP method:

```python
@router.get("/users/{user_id}")
@controllable_endpoint(description="Get user details")
async def get_user(user_id: int, request: Request):
    return {"user_id": user_id}
```

### Option 2: Explicit Path

Manually specify the full path including the HTTP method:

```python
@router.get("/users/{user_id}")
@controllable_endpoint(
    path="/api/v1/users/{user_id}:GET",
    description="Get user details"
)
async def get_user(user_id: int, request: Request):
    return {"user_id": user_id}
```

### Option 3: Using Wildcards for Path Parameters

For endpoints with path parameters, you can use the path parameter syntax directly:

```python
@router.get("/{user_id}")
@controllable_endpoint(
    path="/api/v1/profiles/{user_id}",
    description="Get profile by user ID"
)
async def get_profile(user_id: int, request: Request):
    return {"profile_id": user_id}
```

## How It Works

1. The `@controllable_endpoint` decorator wraps your endpoint function in a new function that:
   - Checks if the endpoint is enabled before processing requests
   - Returns a 404 error if the endpoint is disabled
   - Passes the request to your original function if enabled

2. The custom `ControllableAPIRouter` class (which extends FastAPI's `APIRouter`) works in tandem with the decorator to:
   - Register endpoints in the global registry
   - Update OpenAPI documentation to hide disabled endpoints
   - Store routing information for endpoint management

3. The global `ENDPOINT_REGISTRY` maintains the state of all controllable endpoints, including:
   - Path information
   - Enabled/disabled status
   - Description

## Admin Endpoints

The system provides administrative endpoints for managing controllable endpoints:

- `GET /api/v1/admin/controllable-endpoints` - List all controllable endpoints and their status
- `POST /api/v1/admin/controllable-endpoints/{endpoint_path}/enable` - Enable a specific endpoint
- `POST /api/v1/admin/controllable-endpoints/{endpoint_path}/disable` - Disable a specific endpoint

## Common Mistakes and How to Avoid Them

### 1. Incorrect Decorator Order

```python
# ❌ INCORRECT - controllable_endpoint must be AFTER the route decorator
@controllable_endpoint(description="Description")
@router.get("/path")
async def endpoint(request: Request):
    return {"result": "data"}

# ✅ CORRECT - FastAPI route decorator first, then controllable_endpoint
@router.get("/path")
@controllable_endpoint(description="Description")
async def endpoint(request: Request):
    return {"result": "data"}
```

### 2. Missing `Request` Parameter

The endpoint needs access to the request object to check if it's enabled:

```python
# ❌ INCORRECT - missing Request parameter
@router.get("/path")
@controllable_endpoint(description="Description")
async def endpoint():  # No Request parameter
    return {"result": "data"}

# ✅ CORRECT - Request parameter included
@router.get("/path")
@controllable_endpoint(description="Description")
async def endpoint(request: Request):  # Request parameter added
    return {"result": "data"}
```

### 3. Path Conflicts

When manually specifying paths, be careful to avoid conflicts:

```python
# ❌ INCORRECT - path conflict, both use the same path
@router.get("/users")
@controllable_endpoint(path="/api/v1/users:GET", description="Get all users")
async def get_users(request: Request):
    return {"users": [...]}

@router.get("/users")
@controllable_endpoint(path="/api/v1/users:GET", description="Another endpoint")
async def another_function(request: Request):
    return {"something": "else"}

# ✅ CORRECT - unique paths
@router.get("/users")
@controllable_endpoint(path="/api/v1/users:GET", description="Get all users")
async def get_users(request: Request):
    return {"users": [...]}

@router.get("/users/active")
@controllable_endpoint(path="/api/v1/users/active:GET", description="Get active users")
async def get_active_users(request: Request):
    return {"active_users": [...]}
```

### 4. Forgetting the Decorator Entirely

Every endpoint in a domain router should have the `@controllable_endpoint` decorator:

```python
# ❌ INCORRECT - missing controllable_endpoint decorator
@router.get("/path")
async def endpoint(request: Request):
    return {"result": "data"}

# ✅ CORRECT - controllable_endpoint decorator added
@router.get("/path")
@controllable_endpoint(description="Description")
async def endpoint(request: Request):
    return {"result": "data"}
```

## Troubleshooting

### Endpoint Returns 404 When It Should Be Enabled

1. Check if the endpoint is registered correctly:
   ```python
   from core.dependencies import ENDPOINT_REGISTRY
   print(ENDPOINT_REGISTRY)
   ```

2. Verify the path being used to check if the endpoint is enabled:
   ```python
   # Add debugging to see what path is being checked
   @router.get("/path")
   @controllable_endpoint(description="Description")
   async def endpoint(request: Request):
       # Print the request path and method
       print(f"Request path: {request.scope['path']}")
       print(f"Request method: {request.scope['method']}")
       return {"result": "data"}
   ```

3. Ensure the endpoint is enabled in the registry:
   ```python
   from core.dependencies import enable_endpoint
   enable_endpoint("/api/v1/your/path:METHOD")
   ```

### Endpoint Not Appearing in Admin List

1. Ensure your endpoint has the `@controllable_endpoint` decorator
2. Check if the path is generated correctly
3. Verify the router is properly registered in the domain discovery process

## Best Practices

1. **Use Auto-Derived Paths** when possible to avoid path conflicts and maintenance overhead.

2. **Include Descriptive Comments** for your endpoints to make administration easier:
   ```python
   @router.get("/users/{user_id}")
   @controllable_endpoint(description="Get detailed user information including profile, settings, and preferences")
   async def get_user(user_id: int, request: Request):
       # ...
   ```

3. **Group Related Endpoints** with consistent path patterns:
   ```python
   # User management endpoints
   @router.get("/users")
   @controllable_endpoint(description="List all users")
   
   @router.get("/users/{user_id}")
   @controllable_endpoint(description="Get user details")
   
   @router.post("/users")
   @controllable_endpoint(description="Create new user")
   ```

4. **Consider Security Implications** of enabling/disabling endpoints, especially for authentication-related endpoints.

5. **Use Feature Flags** for new functionality by setting `enabled=False` initially:
   ```python
   @router.post("/new-feature")
   @controllable_endpoint(enabled=False, description="New experimental feature")
   async def new_feature(request: Request):
       # ...
   ```

## Summary

The `@controllable_endpoint` decorator is a powerful tool for managing API endpoints at runtime. By following this documentation, you can ensure that all domain routes in your application are properly controllable, helping to avoid errors and maintain consistency across your API surface. 