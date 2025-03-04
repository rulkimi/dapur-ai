from enum import Enum
from typing import Any, Dict, Optional

from core.exceptions import (
    AppException, 
    UnauthorizedException, 
    ForbiddenException,
)


class AuthErrorCode(Enum):
    """
    Enumeration of error codes for the Auth domain.
    
    Each error code follows the format: AUTH_{CATEGORY}_{SPECIFIC_ERROR}
    """
    # Credential errors
    CREDENTIALS_INVALID_USERNAME = "AUTH_CREDENTIALS_INVALID_USERNAME"
    CREDENTIALS_INVALID_PASSWORD = "AUTH_CREDENTIALS_INVALID_PASSWORD"
    CREDENTIALS_ACCOUNT_LOCKED = "AUTH_CREDENTIALS_ACCOUNT_LOCKED"
    
    # Token errors
    TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    TOKEN_REVOKED = "AUTH_TOKEN_REVOKED"
    
    # Permission errors
    PERMISSION_INSUFFICIENT = "AUTH_PERMISSION_INSUFFICIENT"
    PERMISSION_ROLE_REQUIRED = "AUTH_PERMISSION_ROLE_REQUIRED"
    
    def __str__(self) -> str:
        return self.value


class AuthException(AppException):
    """Base exception for Auth domain errors."""
    domain = "auth"


class AuthCredentialException(UnauthorizedException, AuthException):
    """Exception for authentication credential failures."""
    def __init__(
        self,
        error_code: AuthErrorCode,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)


class AuthPermissionException(ForbiddenException, AuthException):
    """Exception for authorization/permission failures."""
    def __init__(
        self,
        error_code: AuthErrorCode, 
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)


class AuthTokenException(UnauthorizedException, AuthException):
    """Exception for token-related failures."""
    def __init__(
        self,
        error_code: AuthErrorCode,
        message: str = "Token validation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)


# Helper Functions

def raise_credential_error(
    error_code: AuthErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Raise a unified AuthCredentialException with the given error code, message, and details.
    This provides a consistent way to handle auth credential errors.
    """
    # Only set default messages if a custom message is not provided
    if message is None:
        if error_code == AuthErrorCode.CREDENTIALS_INVALID_USERNAME:
            message = "User not found"
        elif error_code == AuthErrorCode.CREDENTIALS_INVALID_PASSWORD:
            message = "Invalid password"
        elif error_code == AuthErrorCode.CREDENTIALS_ACCOUNT_LOCKED:
            message = "Account has been locked due to too many failed attempts"
            
    raise AuthCredentialException(error_code, message, details)


def raise_permission_error(
    error_code: AuthErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Raise an appropriate permission error exception.
    
    Args:
        error_code: Specific permission error code
        message: Custom error message (optional)
        details: Additional error details (optional)
    """
    if message is None:
        message = "Permission denied"
        
        # Provide more specific messages based on error code
        if error_code == AuthErrorCode.PERMISSION_INSUFFICIENT:
            message = "Insufficient permissions to perform this action"
        elif error_code == AuthErrorCode.PERMISSION_ROLE_REQUIRED:
            message = "This action requires a specific role"
            
    raise AuthPermissionException(error_code, message, details)


def raise_token_error(
    error_code: AuthErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Raise an appropriate token error exception.
    
    Args:
        error_code: Specific token error code
        message: Custom error message (optional)
        details: Additional error details (optional)
    """
    if message is None:
        message = "Token error"
        
        # Provide more specific messages based on error code
        if error_code == AuthErrorCode.TOKEN_EXPIRED:
            message = "Token has expired"
        elif error_code == AuthErrorCode.TOKEN_INVALID:
            message = "Token is invalid"
        elif error_code == AuthErrorCode.TOKEN_REVOKED:
            message = "Token has been revoked"
            
    raise AuthTokenException(error_code, message, details) 