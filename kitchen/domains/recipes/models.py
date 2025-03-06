from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Integer, Text, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from db.base import Base


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


class Recipe(Base):
    """Model for storing recipes."""
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    difficulty = Column(ENUM(DifficultyLevel, name='difficultylevel', create_type=False), nullable=False)
    user_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), index=True)
    
    # Relationships
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    tags = relationship("RecipeTag", back_populates="recipe", cascade="all, delete-orphan")
    preferences = relationship("RecipePreference", back_populates="recipe", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, name={self.name}, difficulty={self.difficulty})>"


class Ingredient(Base):
    """Model for storing recipe ingredients."""
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    measurement = Column(String(50), nullable=False)
    
    # Relationship with Recipe
    recipe = relationship("Recipe", back_populates="ingredients")
    
    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name={self.name}, quantity={self.quantity}, measurement={self.measurement})>"


class RecipeTag(Base):
    """Model for storing recipe tags."""
    __tablename__ = "recipe_tags"
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    value = Column(String(255), nullable=False, index=True)
    
    # Add a unique constraint to prevent duplicate tags for a recipe
    __table_args__ = (
        UniqueConstraint('recipe_id', 'value', name='unique_recipe_tag'),
    )
    
    # Relationship with Recipe
    recipe = relationship("Recipe", back_populates="tags")
    
    def __repr__(self) -> str:
        return f"<RecipeTag(id={self.id}, value={self.value})>"


class RecipePreference(Base):
    """Model for storing recipe preferences (dietary_restrictions, allergies, preferred_cuisines)."""
    __tablename__ = "recipe_preferences"
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    type = Column(String(50), nullable=False, index=True)  # Uses PreferenceType enum values
    
    # Relationship with Recipe
    recipe = relationship("Recipe", back_populates="preferences")
    
    # Relationship with RecipePreferenceSetting
    settings = relationship("RecipePreferenceSetting", back_populates="preference", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<RecipePreference(id={self.id}, type={self.type})>"


class RecipePreferenceSetting(Base):
    """Model for storing recipe preference settings (like spice_level)."""
    __tablename__ = "recipe_preference_settings"
    
    id = Column(Integer, primary_key=True)
    preference_id = Column(Integer, ForeignKey("recipe_preferences.id", ondelete="CASCADE"), index=True)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    
    # Add a unique constraint to prevent duplicate settings for a preference
    __table_args__ = (
        UniqueConstraint('preference_id', 'key', name='unique_preference_setting'),
    )
    
    # Relationship with RecipePreference
    preference = relationship("RecipePreference", back_populates="settings")
    
    def __repr__(self) -> str:
        return f"<RecipePreferenceSetting(id={self.id}, key={self.key}, value={self.value})>" 