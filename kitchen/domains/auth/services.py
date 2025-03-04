from typing import Annotated, Optional
from datetime import datetime, timedelta, UTC
from fastapi import Depends
from domains.auth.repositories import AuthRepository
from domains.auth.schemas import AuthCreate, TokenSchema
from domains.auth.models import Auth
from core.security import create_access_token
from core.config import settings
from core.exceptions import (
    ValidationException, 
    ConflictException, 
    UnauthorizedException, 
    ForbiddenException,
    get_or_404
)
from domains.auth.errors import (
    AuthErrorCode,
    raise_credential_error,
    raise_permission_error,
    raise_token_error
)
from sqlalchemy.ext.asyncio import AsyncSession

# Fixed MAX_LOGIN_ATTEMPTS issue - using LOGIN_ATTEMPTS_LIMIT instead
class AuthService:
    def __init__(self, repository: AuthRepository):
        """
        Initialize AuthService with auth repository.
        Service should never directly interact with the database session.
        
        Args:
            repository: AuthRepository for data access
        """
        self.repository = repository

    async def create_auth_by_email_password(self, auth_data: AuthCreate) -> TokenSchema:
        """Register a new auth record and return access token."""
        # Validate password confirmation
        if auth_data.password != auth_data.confirm_password:
            raise ValidationException(
                message="Passwords do not match",
                details={"field": "confirm_password"}
            )

        # Check if auth already exists
        existing_auth = await self.repository.get_auth_by_email(auth_data.email)
        if existing_auth:
            raise ConflictException(
                message="Email already registered",
                details={"field": "email"}
            )

        # Create new auth record
        auth = await self.repository.create_auth_by_email_password(
            email=auth_data.email,
            password=auth_data.password
        )

        # Create access token
        access_token = create_access_token(
            subject=str(auth.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            user_data={
                "id": auth.id,
                "email": auth.email,
                "is_active": auth.is_active,
                "is_superuser": getattr(auth, "is_superuser", False),
                "is_verified": getattr(auth, "is_verified", False)
            }
        )

        return TokenSchema(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def login_by_email_password(self, email: str, password: str) -> TokenSchema:
        """Authenticate user and return access token."""
        # Get auth record
        auth = await self.repository.get_auth_by_email(email)
        
        # Check if user exists
        if auth is None:
            raise_credential_error(
                AuthErrorCode.CREDENTIALS_INVALID_USERNAME,
                "Incorrect email or password",
                {"authenticate": "bearer"}
            )
        
        # Check if account is locked
        if auth.is_locked:
            if auth.locked_at and datetime.now(UTC) - auth.locked_at >= timedelta(hours=settings.LOGIN_ATTEMPTS_LOCK_TIME):
                # Unlock the account if lock time has passed
                auth.is_locked = False
                auth.locked_at = None
                auth.failed_login_attempts = 0
                await self.repository.update_auth(auth)
            else:
                # Calculate remaining lock time
                if auth.locked_at:
                    remaining_time = timedelta(hours=settings.LOGIN_ATTEMPTS_LOCK_TIME) - (datetime.now(UTC) - auth.locked_at)
                    remaining_minutes = int(remaining_time.total_seconds() / 60)
                    raise_credential_error(
                        AuthErrorCode.CREDENTIALS_ACCOUNT_LOCKED,
                        f"Account is locked. Please try again in {remaining_minutes} minutes",
                        {"remaining_minutes": remaining_minutes}
                    )
        
        # Check password
        if not auth.verify_password(password):
            # Increment failed login attempts
            auth.failed_login_attempts += 1
            
            # Lock account if max attempts reached
            if auth.failed_login_attempts >= settings.LOGIN_ATTEMPTS_LIMIT:
                auth.is_locked = True
                auth.locked_at = datetime.now(UTC)
                await self.repository.update_auth(auth)
                raise_credential_error(
                    AuthErrorCode.CREDENTIALS_ACCOUNT_LOCKED,
                    f"Account locked due to too many failed attempts. Try again in {settings.LOGIN_ATTEMPTS_LOCK_TIME} hours",
                    {"lock_hours": settings.LOGIN_ATTEMPTS_LOCK_TIME}
                )
            
            await self.repository.update_auth(auth)
            raise_credential_error(
                AuthErrorCode.CREDENTIALS_INVALID_PASSWORD,
                "Incorrect email or password",
                {
                    "authenticate": "bearer",
                    "attempts_remaining": settings.LOGIN_ATTEMPTS_LIMIT - auth.failed_login_attempts
                }
            )
            
        # Reset failed login attempts
        if auth.failed_login_attempts > 0:
            auth.failed_login_attempts = 0
            await self.repository.update_auth(auth)
            
        # Create access token
        access_token = create_access_token(
            subject=auth.id,
            user_data={
                "id": auth.id,
                "email": auth.email,
                "is_active": auth.is_active,
                "is_superuser": getattr(auth, "is_superuser", False),
                "is_verified": getattr(auth, "is_verified", False)
            }
        )
        
        return TokenSchema(
            access_token=access_token, 
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )


def get_auth_service(
    repository: Annotated[AuthRepository, Depends()]
) -> AuthService:
    """
    Dependency for getting auth service instance.
    
    This abstraction ensures that services can be injected and mocked in tests.
    
    Args:
        repository: Auth repository instance from dependency injection
        
    Returns:
        Initialized auth service
    """
    return AuthService(repository) 
    return AuthService(repository) 