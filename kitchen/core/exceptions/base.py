from typing import Any, Dict, Optional
from http import HTTPStatus
from ..context import get_request_id


class AppException(Exception):
    """
    Base exception class for all application exceptions.
    
    This class is used as the base for all custom exceptions in the application.
    It supports HTTP status codes, error codes, and additional error details.
    
    Attributes:
        status_code: HTTP status code to be returned
        error_code: Application-specific error code
        message: Human-readable error description
        details: Additional context or details about the error
    """
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    
    def __init__(
        self, 
        message: str = "An unexpected error occurred", 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new AppException.
        
        Args:
            message: Human-readable error description
            details: Additional context or details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary representation.
        
        Returns:
            Dictionary containing all error details
        """
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "request_id": get_request_id(),  # Include request ID
        }
        
        # Add domain information if available
        if hasattr(self, 'domain'):
            result["domain"] = self.domain
            
        return result 