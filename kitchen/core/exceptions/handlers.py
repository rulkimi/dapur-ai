from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Callable, Type
from sqlalchemy.exc import SQLAlchemyError
import logging
from .base import AppException
from .http import DatabaseException, TokenException
from ..context import get_request_id


logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler for all exceptions that inherit from AppException.
    
    Args:
        request: The FastAPI request
        exc: The exception that was raised
        
    Returns:
        JSONResponse with the error details
    """
    error_response = exc.to_dict()
    request_id = get_request_id()
    
    # Log the exception
    logger.error(
        f"AppException handled: {exc.error_code} - {exc.message} - Request ID: {request_id}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "details": exc.details,
            "request_id": request_id
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def token_exception_handler(request: Request, exc: TokenException) -> JSONResponse:
    """
    Specialized handler for token exceptions, adding WWW-Authenticate header.
    
    Args:
        request: The FastAPI request
        exc: The token exception that was raised
        
    Returns:
        JSONResponse with the error details and WWW-Authenticate header
    """
    error_response = exc.to_dict()
    request_id = get_request_id()
    
    # Log the exception with token-specific information
    logger.error(
        f"Token exception: {exc.error_code} - {exc.message} - Type: {exc.details.get('error_type', 'unknown')} - Request ID: {request_id}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "details": exc.details,
            "request_id": request_id,
            "error_type": exc.details.get("error_type")
        },
        exc_info=True
    )
    
    # Build WWW-Authenticate header
    auth_type = exc.details.get("authenticate", "Bearer")
    auth_value = f'{auth_type} error="{exc.details.get("error_type", "invalid_token")}"'
    if exc.details.get("error_type") == "token_expired":
        auth_value += ', error_description="Token expired"'
    
    # Return response with WWW-Authenticate header
    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )
    response.headers["WWW-Authenticate"] = auth_value
    
    return response


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy exceptions to convert them to DatabaseException.
    
    Args:
        request: The FastAPI request
        exc: The SQLAlchemy exception that was raised
        
    Returns:
        JSONResponse with the error details
    """
    request_id = get_request_id()
    
    # Convert SQLAlchemy exceptions to our DatabaseException
    db_exc = DatabaseException(
        message="A database error occurred",
        details={"error_type": exc.__class__.__name__, "error": str(exc)}
    )
    
    # Log the error
    logger.error(
        f"Database exception: {str(exc)} - Request ID: {request_id}",
        extra={
            "error_code": db_exc.error_code,
            "status_code": db_exc.status_code,
            "path": request.url.path,
            "request_id": request_id
        },
        exc_info=True
    )
    
    return await app_exception_handler(request, db_exc)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Register handler for token exceptions (must come before AppException handler)
    app.add_exception_handler(TokenException, token_exception_handler)
    
    # Register handler for all custom exceptions
    app.add_exception_handler(AppException, app_exception_handler)
    
    # Register handler for SQLAlchemy exceptions
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Log the registration
    logger.info("Exception handlers registered successfully") 