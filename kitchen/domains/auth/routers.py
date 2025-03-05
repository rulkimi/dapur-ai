from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from domains.auth.schemas import AuthCreate, TokenSchema, AuthResponse, TokenResponse, ClientCredentialsRequest, AuthLogin
from domains.auth.services import AuthService, get_auth_service
from core.security import (
    get_current_auth, 
    client_credentials_manager
)
from domains.auth.models import Auth
from fastapi.security import OAuth2PasswordRequestForm
from core.config import settings
from core.dependencies import controllable_endpoint, ControllableAPIRouter

router = ControllableAPIRouter(prefix="/auth", tags=["auth"])

@router.post("/register-by-email-password", response_model=TokenSchema)
@controllable_endpoint(
    path="/api/v1/auth/register-by-email-password:POST",
    enabled=True,
    description="Register a new user with email and password"
)
async def register_by_email_password(
    auth_data: AuthCreate,
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenSchema:
    """Register a new user and return access token."""
    return await service.create_auth_by_email_password(auth_data)

@router.post("/login-by-email-password", response_model=TokenSchema)
@controllable_endpoint(
    path="/api/v1/auth/login-by-email-password:POST",
    enabled=True,
    description="Login with email and password via form"
)
async def login_by_email_password(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenSchema:
    """Authenticate user and return access token using form data.
    
    This endpoint expects form data with username and password fields.
    
    - **username**: Email address of the user
    - **password**: Password for authentication
    
    Note: The field is called 'username' but should contain the user's email address.
    This naming is due to the OAuth2 specification.
    
    Example curl request:
    ```bash
    curl -X 'POST' \\
      'http://localhost:8000/api/v1/auth/login-by-email-password' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'username=user@example.com&password=yourpassword'
    ```
    """
    return await service.login_by_email_password(form_data.username, form_data.password)

@router.post("/login-json", response_model=TokenSchema)
@controllable_endpoint(
    path="/api/v1/auth/login-json:POST",
    enabled=True,
    description="Login with email and password via JSON"
)
async def login_json(
    login_data: AuthLogin,
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenSchema:
    """Authenticate user and return access token using JSON.
    
    This endpoint accepts JSON with email and password fields.
    
    Example request body:
    ```json
    {
        "email": "user@example.com",
        "password": "yourpassword"
    }
    ```
    """
    return await service.login_by_email_password(login_data.email, login_data.password)

@router.get("/me", response_model=AuthResponse)
@controllable_endpoint(
    path="/api/v1/auth/me:GET",
    enabled=True,
    description="Get current authenticated user information"
)
async def get_current_auth_info(
    current_auth: Annotated[Auth, Depends(get_current_auth)]
) -> AuthResponse:
    """Get current user information."""
    return current_auth

@router.post("/token/client-credentials", response_model=TokenResponse)
@controllable_endpoint(
    path="/api/v1/auth/token/client-credentials:POST",
    enabled=True,
    description="Get a token using client credentials"
)
async def get_client_credentials_token(
    request: ClientCredentialsRequest
) -> TokenResponse:
    """OAuth2 client credentials flow token endpoint"""
    if not client_credentials_manager.verify_client_credentials(
        request.client_id,
        request.client_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials"
        )

    # Validate requested scopes
    requested_scopes = request.scope.split() if request.scope else []
    available_scopes = settings.OAUTH2_SCOPES.keys()
    
    invalid_scopes = [s for s in requested_scopes if s not in available_scopes]
    if invalid_scopes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scopes: {', '.join(invalid_scopes)}"
        )

    return client_credentials_manager.create_client_token(requested_scopes) 