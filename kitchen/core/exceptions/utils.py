"""
Utility functions for exception handling.

This module provides helper functions to make common exception
handling patterns easier and more consistent.
"""

from typing import Any, Callable, Optional, TypeVar, Dict, Type
from sqlalchemy.exc import IntegrityError
from .http import (
    NotFoundException, 
    ConflictException, 
    DatabaseException
)

T = TypeVar('T')


def handle_db_integrity_error(exc: IntegrityError, detail: str = "Database integrity error") -> None:
    """
    Handle SQLAlchemy IntegrityError and raise appropriate domain exception.
    
    Args:
        exc: The original IntegrityError
        detail: A user-friendly error message
        
    Raises:
        ConflictException: For integrity constraint violations
    """
    # Postgresql error codes can be checked if using psycopg2
    # e.g., if '23505' in str(exc): # unique_violation
    
    # Check if it's a unique constraint violation
    if "unique constraint" in str(exc).lower() or "duplicate key" in str(exc).lower():
        raise ConflictException(
            message=detail,
            details={"error": str(exc)}
        )
    
    # Handle other integrity errors
    raise DatabaseException(
        message=detail,
        details={"error": str(exc)}
    )


def get_or_404(
    result: Optional[T], 
    detail: str = "Resource not found",
    **kwargs: Any
) -> T:
    """
    Check if a result exists, otherwise raise NotFoundException.
    
    Args:
        result: The result to check
        detail: Error message if result is None
        kwargs: Additional details to include in the exception
        
    Returns:
        The result if it exists
        
    Raises:
        NotFoundException: If result is None
    """
    if result is None:
        raise NotFoundException(detail, details=kwargs or None)
    return result


async def get_or_404_async(
    getter_func: Callable[..., Any],
    *args: Any,
    error_message: str = "Resource not found",
    **kwargs: Any
) -> Any:
    """
    Call an async getter function and raise NotFoundException if result is None.
    
    Args:
        getter_func: Async function that retrieves a resource
        args: Positional arguments to pass to the getter function
        error_message: Error message if the resource is not found
        kwargs: Keyword arguments to pass to the getter function
        
    Returns:
        The resource if found
        
    Raises:
        NotFoundException: If resource is not found
    """
    result = await getter_func(*args, **kwargs)
    return get_or_404(result, error_message)


def try_with_db_exception(
    func: Callable[..., T],
    *args: Any,
    error_message: str = "Database operation failed",
    **kwargs: Any
) -> T:
    """
    Execute a function and wrap any database exceptions.
    
    Args:
        func: Function to execute
        args: Positional arguments to pass to the function
        error_message: Error message if an exception occurs
        kwargs: Keyword arguments to pass to the function
        
    Returns:
        The result of the function
        
    Raises:
        DatabaseException: If a database exception occurs
    """
    try:
        return func(*args, **kwargs)
    except IntegrityError as e:
        handle_db_integrity_error(e, error_message)
    except Exception as e:
        raise DatabaseException(
            message=error_message,
            details={"error": str(e)}
        )


def generate_error_docs() -> Dict[str, Dict[str, Any]]:
    """
    Generate documentation for all domain-specific error codes.
    
    This function collects all error codes from domain-specific error enums
    and organizes them by domain and category for documentation purposes.
    
    Returns:
        Dictionary with domain-specific error documentation
    """
    docs = {}
    
    # Import all domain error modules
    # This needs to be kept in sync with all domains that have error codes
    try:
        from domains.auth.errors import AuthErrorCode
        
        # Add all error enums to this list
        error_enums = [AuthErrorCode]
        
        # Process each error enum
        for error_enum in error_enums:
            # Extract domain name from class name (e.g., AuthErrorCode -> auth)
            domain = error_enum.__name__.replace("ErrorCode", "").lower()
            docs[domain] = {}
            
            # Process each error in the enum
            for error in error_enum:
                code = str(error)
                
                # Extract category from error code (second part of the code)
                # Example: AUTH_CREDENTIALS_INVALID_PASSWORD -> credentials
                category = code.split("_")[1].lower()
                
                # Initialize category if not exists
                if category not in docs[domain]:
                    docs[domain][category] = []
                    
                # Add error details to category
                docs[domain][category].append({
                    "code": code,
                    "name": error.name,
                    "description": getattr(error, "__doc__", "No description available")
                })
    except ImportError as e:
        # Handle case where domain modules aren't available
        docs["error"] = {"import_error": str(e)}
    
    return docs 