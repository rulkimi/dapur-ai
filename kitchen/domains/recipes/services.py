from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from domains.recipes.repositories import RecipeRepository
from domains.recipes.models import DifficultyLevel, PreferenceType
from domains.recipes.schemas import LLMRecipeSchema, RecipeResponse
from domains.recipes.errors import raise_recipe_not_found, raise_recipe_generation_error
from domains.recipes.prompts import get_prompt_template, TemplateType

from domains.profiles.repositories import ProfileRepository, UserFoodPreferenceRepository, UserPreferenceSettingsRepository

from infrastructure.external_services.llm.providers import get_llm_provider, ProviderType


class RecipeService:
    """Service for recipe-related operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.recipe_repository = RecipeRepository(session)
        self.profile_repository = ProfileRepository(session)
        self.food_preference_repository = UserFoodPreferenceRepository(session)
        self.preference_settings_repository = UserPreferenceSettingsRepository(session)
        
    async def generate_recipe(self, user_id: int, number_of_recipes: int = 1) -> List[RecipeResponse]:
        """Generate recipe(s) based on user preferences using LLM."""
        try:
            # Get user profile and system prompt
            profile = await self.profile_repository.get_by_user_id(user_id)
            if not profile:
                raise ValueError(f"User profile not found for user ID {user_id}")
                
            # Get user's food preferences
            food_preferences = await self.food_preference_repository.get_user_food_preferences(user_id)
            
            # Convert food preferences to dictionary by type
            preferences_by_type = {}
            for pref in food_preferences:
                if pref.preference_type not in preferences_by_type:
                    preferences_by_type[pref.preference_type] = []
                preferences_by_type[pref.preference_type].append(pref.preference_value)
            
            # Get user's preference settings
            preference_settings = await self.preference_settings_repository.get_user_preference_settings(user_id)
            
            # Get the recipe generation template
            template = get_prompt_template(TemplateType.RECIPE_GENERATION)
            
            # Create the LLM prompt using the template
            prompt = template.format(
                system_prompt=profile.system_prompt if profile.system_prompt else "",
                user_name=profile.name,
                dietary_restrictions=preferences_by_type.get('dietary_restrictions', []),
                allergies=preferences_by_type.get('allergies', []),
                preferred_cuisines=preferences_by_type.get('preferred_cuisines', []),
                spice_level=preference_settings.spice_level if preference_settings else None,
                additional_info=preference_settings.additional_info if preference_settings else None,
                number_of_recipes=number_of_recipes
            )
            
            # Call the LLM service
            llm_provider = get_llm_provider(ProviderType.GEMINI)
            
            # Process recipes concurrently
            generated_recipes = []
            
            async def generate_single_recipe() -> Optional[RecipeResponse]:
                try:
                    # Extract structured data using the schema
                    recipe_data = await llm_provider.extract(prompt, LLMRecipeSchema)
                    
                    # Convert the recipe data to database format and save it
                    recipe = await self._save_recipe(user_id, recipe_data)
                    
                    # Get the newly created recipe with all related data
                    saved_recipe = await self.recipe_repository.get_recipe(recipe.id)
                    
                    # Convert to response format
                    return RecipeResponse.model_validate(saved_recipe)
                    
                except Exception as e:
                    # Log the error but continue with other recipes
                    print(f"Error generating recipe: {str(e)}")
                    return None
            
            # Create tasks for concurrent execution
            import asyncio
            tasks = [generate_single_recipe() for _ in range(number_of_recipes)]
            
            # Execute all tasks concurrently
            recipe_results = await asyncio.gather(*tasks)
            
            # Filter out None results (failed generations)
            generated_recipes = [recipe for recipe in recipe_results if recipe is not None]
            
            if not generated_recipes:
                raise_recipe_generation_error("Failed to generate any recipes")
                
            return generated_recipes
            
        except ValueError as e:
            raise_recipe_generation_error(f"Value error: {str(e)}")
        except Exception as e:
            raise_recipe_generation_error(f"Unexpected error: {str(e)}")
    
    async def get_recipe(self, recipe_id: int) -> RecipeResponse:
        """Get a recipe by ID."""
        recipe = await self.recipe_repository.get_recipe(recipe_id)
        if not recipe:
            raise_recipe_not_found(recipe_id)
        return RecipeResponse.model_validate(recipe)
    
    async def get_recipes(
        self, 
        user_id: Optional[int] = None, 
        difficulty: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 10, 
        offset: int = 0
    ) -> Tuple[List[RecipeResponse], int]:
        """Get recipes with optional filtering."""
        recipes, total = await self.recipe_repository.get_recipes(
            user_id=user_id,
            difficulty=difficulty,
            tag=tag,
            limit=limit,
            offset=offset
        )
        
        return [RecipeResponse.model_validate(recipe) for recipe in recipes], total
    
    async def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe by ID."""
        success = await self.recipe_repository.delete_recipe(recipe_id)
        if not success:
            raise_recipe_not_found(recipe_id)
        return True
    
    async def _save_recipe(self, user_id: int, recipe_data: LLMRecipeSchema) -> Any:
        """Save recipe data from LLM to database."""
        # Extract data from the LLM response
        ingredients_data = [
            {
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "measurement": ingredient.measurement
            }
            for ingredient in recipe_data.ingredients
        ]
        
        # Prepare preferences data
        preferences = {
            PreferenceType.DIETARY_RESTRICTION.value: recipe_data.dietary_restrictions,
            PreferenceType.ALLERGY.value: recipe_data.allergies,
            PreferenceType.PREFERRED_CUISINE.value: recipe_data.preferred_cuisines
        }
        
        # Prepare preference settings
        preference_settings = {}
        if recipe_data.spice_level:
            preference_settings = {
                PreferenceType.PREFERRED_CUISINE.value: {
                    "spice_level": recipe_data.spice_level
                }
            }
        
        # Create recipe with all related entities
        return await self.recipe_repository.create_recipe(
            user_id=user_id,
            name=recipe_data.name,
            description=recipe_data.description,
            duration=recipe_data.duration,
            difficulty=recipe_data.difficulty,
            ingredients=ingredients_data,
            tags=recipe_data.tags,
            preferences=preferences,
            preference_settings=preference_settings
        ) 