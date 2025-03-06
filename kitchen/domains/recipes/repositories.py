from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.recipes.models import (
    Recipe, 
    Ingredient, 
    RecipeTag, 
    RecipePreference, 
    RecipePreferenceSetting,
    DifficultyLevel,
    PreferenceType
)


class RecipeRepository:
    """Repository for recipes data access."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_recipe(
        self, 
        user_id: int, 
        name: str, 
        description: str, 
        duration: int, 
        difficulty: DifficultyLevel,
        ingredients: List[Dict[str, Any]] = None,
        tags: List[str] = None,
        preferences: Dict[str, List[str]] = None,
        preference_settings: Dict[str, Any] = None
    ) -> Recipe:
        """Create a new recipe with related entities."""
        # Create recipe
        recipe = Recipe(
            user_id=user_id,
            name=name,
            description=description,
            duration=duration,
            difficulty=difficulty
        )
        self.session.add(recipe)
        await self.session.flush()  # This gives us the recipe.id
        
        # Add ingredients if provided
        if ingredients:
            for ingredient_data in ingredients:
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    name=ingredient_data.get("name"),
                    quantity=ingredient_data.get("quantity"),
                    measurement=ingredient_data.get("measurement")
                )
                self.session.add(ingredient)
        
        # Add tags if provided
        if tags:
            for tag_value in tags:
                tag = RecipeTag(
                    recipe_id=recipe.id,
                    value=tag_value
                )
                self.session.add(tag)
        
        # Add preferences if provided
        if preferences:
            for pref_type, pref_values in preferences.items():
                if not pref_values:
                    continue
                    
                # Create preference entry for this type
                preference = RecipePreference(
                    recipe_id=recipe.id,
                    type=pref_type
                )
                self.session.add(preference)
                await self.session.flush()  # This gives us the preference.id
                
                # If there are specific settings for this preference
                if preference_settings and pref_type in preference_settings:
                    for key, value in preference_settings[pref_type].items():
                        setting = RecipePreferenceSetting(
                            preference_id=preference.id,
                            key=key,
                            value=value
                        )
                        self.session.add(setting)
        
        await self.session.commit()
        await self.session.refresh(recipe)
        return recipe
    
    async def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID with all related data."""
        query = (
            select(Recipe)
            .options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.tags),
                selectinload(Recipe.preferences).selectinload(RecipePreference.settings)
            )
            .where(Recipe.id == recipe_id)
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_recipes(
        self, 
        user_id: Optional[int] = None, 
        difficulty: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 10, 
        offset: int = 0
    ) -> tuple[List[Recipe], int]:
        """Get recipes with optional filtering."""
        query = (
            select(Recipe)
            .options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.tags),
                selectinload(Recipe.preferences).selectinload(RecipePreference.settings)
            )
        )
        
        # Apply filters
        if user_id is not None:
            query = query.where(Recipe.user_id == user_id)
        
        if difficulty is not None:
            query = query.where(Recipe.difficulty == difficulty)
            
        if tag is not None:
            query = query.join(RecipeTag).where(RecipeTag.value == tag)
        
        # Add pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await self.session.execute(query)
        recipes = result.scalars().all()
        
        # Count total recipes (without pagination)
        count_query = select(func.count()).select_from(Recipe)
        
        # Apply the same filters to the count query
        if user_id is not None:
            count_query = count_query.where(Recipe.user_id == user_id)
        
        if difficulty is not None:
            count_query = count_query.where(Recipe.difficulty == difficulty)
            
        if tag is not None:
            count_query = count_query.join(RecipeTag).where(RecipeTag.value == tag)
            
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        return recipes, total
    
    async def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe by ID."""
        query = delete(Recipe).where(Recipe.id == recipe_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0 