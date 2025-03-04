from http import HTTPStatus
from typing import Any, Dict, Optional
from .base import AppException


class BadRequestException(AppException):
    """
    Exception for invalid request data or parameters.
    
    Use this when the client sends a request with invalid data formats,
    missing required fields, or other validation issues.
    """
    status_code: int = HTTPStatus.BAD_REQUEST
    error_code: str = "BAD_REQUEST"
    
    def __init__(
        self, 
        message: str = "Invalid request parameters", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class UnauthorizedException(AppException):
    """
    Exception for authentication failures.
    
    Use this when a user provides invalid credentials or no credentials
    when authentication is required.
    """
    status_code: int = HTTPStatus.UNAUTHORIZED
    error_code: str = "UNAUTHORIZED"
    
    def __init__(
        self, 
        message: str = "Authentication required", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ForbiddenException(AppException):
    """
    Exception for authorization failures.
    
    Use this when an authenticated user doesn't have sufficient permissions
    to access a resource or perform an action.
    """
    status_code: int = HTTPStatus.FORBIDDEN
    error_code: str = "FORBIDDEN"
    
    def __init__(
        self, 
        message: str = "You don't have permission to perform this action", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class NotFoundException(AppException):
    """
    Exception for resources that do not exist.
    
    Use this when a requested resource (user, product, etc.) cannot be found.
    """
    status_code: int = HTTPStatus.NOT_FOUND
    error_code: str = "NOT_FOUND"
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ConflictException(AppException):
    """
    Exception for resource conflicts.
    
    Use this when a request conflicts with the current state of the server,
    such as trying to create a resource with a name that already exists.
    """
    status_code: int = HTTPStatus.CONFLICT
    error_code: str = "CONFLICT"
    
    def __init__(
        self, 
        message: str = "Resource conflict", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ValidationException(BadRequestException):
    """
    Exception for validation errors.
    
    Use this when input data fails validation rules.
    This is a specialized type of BadRequestException.
    """
    error_code: str = "VALIDATION_ERROR"
    
    def __init__(
        self, 
        message: str = "Validation error", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ServiceException(AppException):
    """
    Exception for service-level errors.
    
    Use this for errors in business logic or when a service operation fails.
    """
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "SERVICE_ERROR"
    
    def __init__(
        self, 
        message: str = "Service operation failed", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class DatabaseException(ServiceException):
    """
    Exception for database-related errors.
    
    Use this when database operations fail.
    """
    error_code: str = "DATABASE_ERROR"
    
    def __init__(
        self, 
        message: str = "Database operation failed", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ExternalServiceException(ServiceException):
    """
    Exception for external service integration errors.
    
    Use this when calls to external APIs or services fail.
    """
    error_code: str = "EXTERNAL_SERVICE_ERROR"
    
    def __init__(
        self, 
        message: str = "External service request failed", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details) 