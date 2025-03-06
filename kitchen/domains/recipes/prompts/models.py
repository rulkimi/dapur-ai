"""
Pydantic models for prompt templates.

This module defines the data models used in prompt templates.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TemplateType(str, Enum):
    """Types of prompt templates."""
    RECIPE_GENERATION = "recipe_generation"
    RECIPE_VARIATION = "recipe_variation"
    INGREDIENT_SUBSTITUTION = "ingredient_substitution"
    # Add more template types as needed


class RecipeGenerationInput(BaseModel):
    """Input parameters for recipe generation prompt."""
    system_prompt: str = Field(default="", description="System prompt for the LLM")
    user_name: str = Field(description="Name of the user")
    dietary_restrictions: List[str] = Field(default_factory=list, description="User's dietary restrictions")
    allergies: List[str] = Field(default_factory=list, description="User's allergies")
    preferred_cuisines: List[str] = Field(default_factory=list, description="User's preferred cuisines")
    spice_level: Optional[str] = Field(default=None, description="User's preferred spice level")
    additional_info: Optional[str] = Field(default=None, description="Additional information about user preferences")
    number_of_recipes: int = Field(default=1, description="Number of recipes to generate")
    

class TemplateConfig(BaseModel):
    """Configuration for a prompt template."""
    version: str = Field(description="Version of the template")
    template_type: TemplateType = Field(description="Type of the template")
    description: str = Field(description="Description of the template")
    
    class Config:
        frozen = True  # Make the config immutable 