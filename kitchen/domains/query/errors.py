from enum import Enum
from typing import Any, Dict, Optional

from core.exceptions import (
    AppException, 
    NotFoundException, 
    ValidationException,
    ServiceException
)

class QueryErrorCode(Enum):
    """Error codes for the query domain."""
    
    # Query errors
    QUERY_NOT_FOUND = "QUERY_NOT_FOUND"
    QUERY_VALIDATION_ERROR = "QUERY_VALIDATION_ERROR"
    
    # Session errors
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_VALIDATION_ERROR = "SESSION_VALIDATION_ERROR"
    
    # Service errors
    SERVICE_LLM_PROVIDER_ERROR = "SERVICE_LLM_PROVIDER_ERROR"
    SERVICE_EXTRACTION_ERROR = "SERVICE_EXTRACTION_ERROR"
    
    # New errors
    INVALID_SESSION_ID = "INVALID_SESSION_ID"
    MODEL_NOT_SUPPORTED = "MODEL_NOT_SUPPORTED"
    PROVIDER_NOT_SUPPORTED = "PROVIDER_NOT_SUPPORTED"
    
    # Onboarding errors
    SYSTEM_PROMPT_GENERATION_FAILED = "SYSTEM_PROMPT_GENERATION_FAILED"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    
    def __str__(self) -> str:
        return self.value

class QueryException(AppException):
    """Base exception for query domain errors."""
    domain = "query"

class QueryNotFoundException(NotFoundException, QueryException):
    """Exception for query not found errors."""
    def __init__(
        self,
        error_code: QueryErrorCode,
        message: str = "Query not found",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)

class QueryValidationException(ValidationException, QueryException):
    """Exception for query validation errors."""
    def __init__(
        self,
        error_code: QueryErrorCode,
        message: str = "Query validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)

class QueryServiceException(ServiceException, QueryException):
    """Exception for query service errors."""
    def __init__(
        self,
        error_code: QueryErrorCode,
        message: str = "Query service error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)

class InvalidSessionIdException(ValidationException):
    """Exception raised when an invalid session ID is provided."""
    
    def __init__(self, message: str):
        """
        Initialize the exception.
        
        Args:
            message: The error message
        """
        # ValidationException doesn't accept error_code parameter
        super().__init__(message=message)
        self.error_code = str(QueryErrorCode.INVALID_SESSION_ID)

def raise_query_error(
    error_code: QueryErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Raise an appropriate query error exception."""
    if error_code in [QueryErrorCode.QUERY_NOT_FOUND, QueryErrorCode.SESSION_NOT_FOUND]:
        raise QueryNotFoundException(error_code, message, details)
    elif error_code in [QueryErrorCode.QUERY_VALIDATION_ERROR, QueryErrorCode.SESSION_VALIDATION_ERROR]:
        raise QueryValidationException(error_code, message, details)
    else:
        raise QueryException(message, details)

def raise_validation_error(
    error_code: QueryErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Raise a query validation error exception."""
    raise QueryValidationException(error_code, message, details)

def raise_service_error(
    error_code: QueryErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Raise a query service error exception."""
    raise QueryServiceException(error_code, message, details) 