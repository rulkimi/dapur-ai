from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """Enum for recipe difficulty levels."""
    EASY = "Easy"
    MEDIUM = "Medium"
    DIFFICULT = "Difficult"


class PreferenceType(str, Enum):
    """Enum for recipe preference types."""
    DIETARY_RESTRICTION = "dietary_restrictions"
    ALLERGY = "allergies"
    PREFERRED_CUISINE = "preferred_cuisines"


# Request Schemas
class RecipeGenerationRequest(BaseModel):
    """Schema for recipe generation request."""
    number_of_recipes: int = Field(default=1, ge=1, le=5)


# Response Schemas
class IngredientResponse(BaseModel):
    """Schema for ingredient response."""
    id: int = Field(description="The ID of the ingredient")
    name: str = Field(description="The name of the ingredient")
    quantity: float = Field(description="The quantity of the ingredient")
    measurement: str = Field(description="The unit of measurement of quantity")
    
    class Config:
        from_attributes = True


class PreferenceSettingResponse(BaseModel):
    """Schema for preference setting response."""
    id: int = Field(description="The ID of the preference setting")
    key: str = Field(description="The key of the preference setting")
    value: str = Field(description="The value of the preference setting")
    
    class Config:
        from_attributes = True


class PreferenceResponse(BaseModel):
    """Schema for preference response."""
    id: int = Field(description="The ID of the preference")
    type: str = Field(description="The type of the preference")
    settings: List[PreferenceSettingResponse] = Field(description="The settings of the preference")
    
    class Config:
        from_attributes = True


class RecipeTagResponse(BaseModel):
    """Schema for recipe tag response."""
    id: int = Field(description="The ID of the recipe tag")
    value: str = Field(description="The value of the recipe tag")
    
    class Config:
        from_attributes = True


class RecipeResponse(BaseModel):
    """Schema for recipe response."""
    id: int = Field(description="The ID of the recipe") 
    name: str = Field(description="The name of the recipe")
    description: str = Field(description="The description of the recipe")
    duration: int = Field(description="The duration of the recipe")
    difficulty: str = Field(description="The difficulty of the recipe")
    ingredients: List[IngredientResponse] = Field(description="The ingredients of the recipe")
    tags: List[RecipeTagResponse] = Field(description="The tags of the recipe")
    preferences: List[PreferenceResponse] = Field(description="The preferences of the recipe")
    
    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Schema for recipe list response."""
    recipes: List[RecipeResponse] = Field(description="The list of recipes")
    total: int = Field(description="The total number of recipes")


# LLM Schemas
class LLMIngredient(BaseModel):
    """Schema for ingredient in LLM response."""
    name: str = Field(description="The name of the ingredient")
    quantity: float = Field(description="The quantity of the ingredient (numeric value)")
    measurement: str = Field(description="The unit of measurement (e.g., cups, tablespoons, grams)")


class LLMRecipeSchema(BaseModel):
    """Schema for extracting recipe data from LLM response."""
    name: str = Field(description="The name of the recipe")
    description: str = Field(description="A description of the recipe, including what it is and its flavor profile")
    duration: int = Field(description="The total cooking time in minutes")
    difficulty: DifficultyLevel = Field(description="The difficulty level of the recipe: Easy, Medium, or Difficult")
    ingredients: List[LLMIngredient] = Field(description="List of ingredients with their quantities and measurements")
    tags: List[str] = Field(description="List of tags for the recipe (e.g., 'vegetarian', 'breakfast', 'low-carb')")
    dietary_restrictions: List[str] = Field(default=[], description="List of dietary restrictions this recipe accommodates")
    allergies: List[str] = Field(default=[], description="List of allergies this recipe avoids")
    preferred_cuisines: List[str] = Field(default=[], description="List of cuisines this recipe belongs to")
    spice_level: Optional[str] = Field(default=None, description="The spice level of this recipe (e.g., 'mild', 'medium', 'hot')") 