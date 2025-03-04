from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_auth
from domains.auth.models import Auth
from domains.profiles.schemas import ProfileResponse, ProfileCreate, ProfileUpdate
from domains.profiles.services import ProfileService
from domains.profiles.repositories import ProfileRepository
from db.repository import get_repository_session

router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_profile_service(
    repository: Annotated[ProfileRepository, Depends()]
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


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
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


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
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


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    user_id: int,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Auth = Depends(get_current_auth)
) -> Any:
    """
    Get a profile by user ID (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    profile = await profile_service.get_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile 