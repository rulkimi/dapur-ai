from enum import Enum
from typing import Any, Dict, Optional
from core.exceptions import AppException


class RecipeErrorCode(Enum):
    """Error codes for the recipes domain."""
    # Recipe errors
    RECIPE_NOT_FOUND = "RECIPE_NOT_FOUND"
    RECIPE_GENERATION_FAILED = "RECIPE_GENERATION_FAILED"
    RECIPE_VALIDATION_FAILED = "RECIPE_VALIDATION_FAILED"
    
    # User preference errors
    USER_PREFERENCES_NOT_FOUND = "USER_PREFERENCES_NOT_FOUND"
    
    def __str__(self) -> str:
        return self.value


class RecipeException(AppException):
    """Base exception for Recipe domain errors."""
    domain = "recipe"


class RecipeNotFoundError(RecipeException):
    """Exception for recipe not found errors."""
    def __init__(
        self,
        error_code: RecipeErrorCode = RecipeErrorCode.RECIPE_NOT_FOUND,
        message: str = "Recipe not found",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)


class RecipeGenerationError(RecipeException):
    """Exception for recipe generation errors."""
    def __init__(
        self,
        error_code: RecipeErrorCode = RecipeErrorCode.RECIPE_GENERATION_FAILED,
        message: str = "Failed to generate recipe",
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = str(error_code)
        super().__init__(message, details)


def raise_recipe_not_found(
    recipe_id: int,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Raise a recipe not found error."""
    raise RecipeNotFoundError(
        message=message or f"Recipe with ID {recipe_id} not found",
        details=details
    )


def raise_recipe_generation_error(
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Raise a recipe generation error."""
    raise RecipeGenerationError(
        message=message or "Failed to generate recipe",
        details=details
    ) 