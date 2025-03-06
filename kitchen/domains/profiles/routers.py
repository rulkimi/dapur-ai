from fastapi import Depends, HTTPException, status, Request, Path, Query
from typing import Any, Annotated, List, Optional, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_auth
from core.dependencies import controllable_endpoint, ControllableAPIRouter
from domains.auth.models import Auth, Anonymous
from domains.profiles.schemas import (
    ProfileResponse, ProfileCreate, ProfileUpdate, ProfileOut, ProfileDetailOut,
    UserFoodPreferenceCreate, UserFoodPreferenceOut,
    UserPreferenceSettingsCreate, UserPreferenceSettingsOut,
    StructuredFoodPreferencesOut
)
from domains.profiles.services import ProfileService
from domains.profiles.repositories import ProfileRepository, get_profile_repository
from db.repository import get_repository_session

router = ControllableAPIRouter(prefix="/profiles", tags=["profiles"])


def get_profile_service(
    repository: Annotated[ProfileRepository, Depends(get_profile_repository)]
) -> ProfileService:
    """
    Dependency for getting profile service instance.
    
    This abstraction ensures that services can be injected and mocked in tests.
    
    Args:
        repository: Profile repository instance from dependency injection
        
    Returns:
        Initialized profile service
    """
    return ProfileService(repository)


# Method 1: Using the controllable_endpoint decorator
@router.get(
    "/me", 
    response_model=ProfileResponse
)
@controllable_endpoint(description="Get current user's profile", path="/api/v1/profiles/me:GET", enabled=True)
async def get_my_profile(
    request: Request,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Auth = Depends(get_current_auth)
) -> Any:
    """
    Get current user's profile
    """
    # Add check to prevent anonymous users from accessing profiles
    if hasattr(current_user, "is_anonymous") and current_user.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access profile"
        )
        
    profile = await profile_service.get_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


# Method 2: Using the controllable_endpoint decorator
@router.put("/me", response_model=ProfileResponse)
@controllable_endpoint(description="Update current user's profile")
async def update_my_profile(
    profile_update: ProfileUpdate,
    request: Request,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Auth = Depends(get_current_auth)
) -> Any:
    """
    Update current user's profile
    """
    # Add check to prevent anonymous users from updating profiles
    if hasattr(current_user, "is_anonymous") and current_user.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to update profile"
        )
    
    profile = await profile_service.update_profile(
        user_id=current_user.id,
        profile_data=profile_update
    )
    if not profile:
        # If profile doesn't exist, create it
        profile = await profile_service.create_profile(
            user_id=current_user.id,
            profile_data=ProfileCreate(
                name=profile_update.name or "",
                dob=profile_update.dob
            )
        )
    return profile


# Method 3: Using the controllable_endpoint decorator only
@router.get(
    "/{user_id}", 
    response_model=ProfileOut
)
@controllable_endpoint(
    path="/api/v1/profiles/{user_id}",  # Use wildcard path for better registry control
    enabled=True,
    description="Get a profile by user ID (admin only)"
)
async def get_profile(
    user_id: int,
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
    current_auth: Annotated[Auth, Depends(get_current_auth)]
):
    """
    Get a user profile by ID.
    Only authenticated users can access this endpoint.
    """
    # Check if user is requesting their own profile or is a superuser
    if current_auth.id != user_id and not current_auth.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    profile = await profile_repository.get_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.get("/{user_id}/detailed", response_model=ProfileDetailOut)
async def get_detailed_profile(
    user_id: int,
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
    current_auth: Annotated[Auth, Depends(get_current_auth)]
):
    """
    Get a detailed user profile including structured food preferences.
    Only authenticated users can access this endpoint.
    """
    # Check if user is requesting their own profile or is a superuser
    if current_auth.id != user_id and not current_auth.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    # Get basic profile
    profile = await profile_repository.get_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get structured preferences
    structured_preferences = await profile_repository.get_structured_preferences(user_id)
    
    # Create detailed profile response
    detailed_profile = ProfileDetailOut.model_validate(profile)
    detailed_profile.structured_preferences = StructuredFoodPreferencesOut.model_validate(structured_preferences)
    
    return detailed_profile


@router.put("/{user_id}/food-preferences", response_model=StructuredFoodPreferencesOut)
async def update_food_preferences(
    preferences: Dict[str, List[str]],
    user_id: int,
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
    current_auth: Annotated[Auth, Depends(get_current_auth)]
):
    """
    Update food preferences for a user.
    Only authenticated users can update their own preferences, or superusers can update any.
    """
    # Check if user is updating their own profile or is a superuser
    if current_auth.id != user_id and not current_auth.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Save array-type preferences
    await profile_repository.save_food_preferences(
        user_id=user_id,
        dietary_restrictions=preferences.get('dietary_restrictions'),
        allergies=preferences.get('allergies'),
        preferred_cuisines=preferences.get('preferred_cuisines')
    )
    
    # Get structured preferences
    result = await profile_repository.get_structured_preferences(user_id)
    
    return StructuredFoodPreferencesOut.model_validate(result)


@router.put("/{user_id}/preference-settings", response_model=UserPreferenceSettingsOut)
async def update_preference_settings(
    settings: UserPreferenceSettingsCreate,
    user_id: int,
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
    current_auth: Annotated[Auth, Depends(get_current_auth)]
):
    """
    Update preference settings for a user.
    Only authenticated users can update their own settings, or superusers can update any.
    """
    # Check if user is updating their own profile or is a superuser
    if current_auth.id != user_id and not current_auth.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Save preference settings
    result = await profile_repository.save_preference_settings(
        user_id=user_id,
        spice_level=settings.spice_level,
        additional_info=settings.additional_info
    )
    
    return result 