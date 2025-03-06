from typing import Optional, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_auth, get_current_user
from domains.auth.models import Auth
from db.session import get_async_session
from domains.recipes.services import RecipeService
from domains.recipes.schemas import RecipeGenerationRequest, RecipeResponse, RecipeListResponse
from core.dependencies import controllable_endpoint, ControllableAPIRouter

# Replace the standard APIRouter with ControllableAPIRouter and add authentication dependency
router = ControllableAPIRouter(
    prefix="/recipes", 
    tags=["recipes"],
    dependencies=[Depends(get_current_user)]  # This enforces authentication for all routes
)


@router.post("/generate", response_model=List[RecipeResponse])
@controllable_endpoint(
    enabled=True,
    description="Generate recipes based on user preferences using LLM."
)
async def generate_recipes(
    request: RecipeGenerationRequest,
    current_user: Auth = Depends(get_current_auth),
    session: AsyncSession = Depends(get_async_session)
):
    """Generate recipes based on user preferences using LLM."""
    try:
        recipe_service = RecipeService(session)
        recipes = await recipe_service.generate_recipe(
            user_id=current_user.id,
            number_of_recipes=request.number_of_recipes
        )
        return recipes
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recipes: {str(e)}")


@router.get("", response_model=RecipeListResponse)
@controllable_endpoint(
    enabled=True,
    description="Get the current user's recipes with optional filtering."
)
async def get_recipes(
    difficulty: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Auth = Depends(get_current_auth),
    session: AsyncSession = Depends(get_async_session)
):
    """Get the current user's recipes with optional filtering."""
    recipe_service = RecipeService(session)
    recipes, total = await recipe_service.get_recipes(
        user_id=current_user.id,
        difficulty=difficulty,
        tag=tag,
        limit=limit,
        offset=offset
    )
    return RecipeListResponse(recipes=recipes, total=total)


@router.get("/{recipe_id}", response_model=RecipeResponse)
@controllable_endpoint(
    enabled=True,
    description="Get a recipe by ID."
)
async def get_recipe(
    recipe_id: int,
    current_user: Auth = Depends(get_current_auth),
    session: AsyncSession = Depends(get_async_session)
):
    """Get a recipe by ID."""
    recipe_service = RecipeService(session)
    recipe = await recipe_service.get_recipe(recipe_id)
    
    # Check if recipe belongs to the current user
    if recipe and recipe.id:
        # Access user_id from the recipe object
        if hasattr(recipe, 'user_id') and recipe.user_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="You don't have permission to access this recipe"
            )
    
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with ID {recipe_id} not found")
    
    return recipe


@router.delete("/{recipe_id}", status_code=204)
@controllable_endpoint(
    enabled=True,
    description="Delete a recipe by ID."
)
async def delete_recipe(
    recipe_id: int,
    current_user: Auth = Depends(get_current_auth),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a recipe by ID."""
    # First get the recipe to check ownership
    recipe_service = RecipeService(session)
    
    # Get the recipe first to verify ownership
    recipe = await recipe_service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with ID {recipe_id} not found")
    
    # Check if recipe belongs to the current user or if user is an admin
    if hasattr(recipe, 'user_id') and recipe.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, 
            detail="You don't have permission to delete this recipe"
        )
    
    # Proceed with deletion
    await recipe_service.delete_recipe(recipe_id)
    return None 