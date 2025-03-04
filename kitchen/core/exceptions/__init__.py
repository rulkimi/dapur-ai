"""
Exceptions module for centralized error handling.

This module provides a hierarchy of exception classes that can be used 
throughout the application to handle different error scenarios consistently.

Usage:
    from core.exceptions import NotFoundException, ValidationException

    # In a service
    def get_user(user_id: int):
        user = repository.get_user(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user
"""

# Base exception
from .base import AppException

# HTTP exceptions
from .http import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
    ServiceException,
    DatabaseException,
    ExternalServiceException,
)

# Handler registration
from .handlers import register_exception_handlers

# Utility functions
from .utils import (
    handle_db_integrity_error,
    get_or_404,
    get_or_404_async,
    try_with_db_exception,
    generate_error_docs,
)

__all__ = [
    # Base exception
    "AppException",
    
    # HTTP exceptions
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
    "ServiceException",
    "DatabaseException",
    "ExternalServiceException",
    
    # Handler registration
    "register_exception_handlers",
    
    # Utility functions
    "handle_db_integrity_error",
    "get_or_404",
    "get_or_404_async",
    "try_with_db_exception",
    "generate_error_docs",
] 