from typing import Optional, Dict
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.repository import BaseRepository, get_repository_session
from domains.profiles.models import Profile

class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session: AsyncSession = Depends(get_repository_session)):
        super().__init__(Profile, session)

    async def get_by_user_id(self, user_id: int) -> Optional[Profile]:
        """Get profile by user ID"""
        query = select(Profile).where(Profile.id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def create_profile(
        self, 
        user_id: int, 
        name: str, 
        dob: Optional[date] = None,
        system_prompt: Optional[str] = None,
        food_preferences: Optional[Dict] = None,
        additional_info: Optional[str] = None
    ) -> Profile:
        """Create a new profile"""
        profile = Profile(
            id=user_id, 
            name=name, 
            dob=dob,
            system_prompt=system_prompt,
            food_preferences=food_preferences,
            additional_info=additional_info
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def update_profile(
        self, 
        profile: Profile, 
        name: str = None, 
        dob: Optional[date] = None,
        system_prompt: Optional[str] = None,
        food_preferences: Optional[Dict] = None,
        additional_info: Optional[str] = None
    ) -> Profile:
        """Update an existing profile"""
        if name is not None:
            profile.name = name
        if dob is not None:
            profile.dob = dob
        if system_prompt is not None:
            profile.system_prompt = system_prompt
        if food_preferences is not None:
            profile.food_preferences = food_preferences
        if additional_info is not None:
            profile.additional_info = additional_info
        
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def update_system_prompt(self, user_id: int, system_prompt: str) -> Optional[Profile]:
        """Update just the system prompt for a user"""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None
        
        profile.system_prompt = system_prompt
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def save(self, profile: Profile) -> Profile:
        """Save a profile to the database"""
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

def get_profile_repository(session: AsyncSession = Depends(get_repository_session)) -> ProfileRepository:
    """
    Provides a ProfileRepository instance for dependency injection.
    
    Args:
        session: The database session
        
    Returns:
        An instance of ProfileRepository
    """
    return ProfileRepository(session) 