from typing import Optional, Dict, List
from datetime import date
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.repository import BaseRepository, get_repository_session
from domains.profiles.models import Profile, UserFoodPreference, UserPreferenceSettings

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
        system_prompt: Optional[str] = None
    ) -> Profile:
        """Create a new profile"""
        profile = Profile(
            id=user_id, 
            name=name, 
            dob=dob,
            system_prompt=system_prompt
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
        system_prompt: Optional[str] = None
    ) -> Profile:
        """Update an existing profile"""
        if name is not None:
            profile.name = name
        if dob is not None:
            profile.dob = dob
        if system_prompt is not None:
            profile.system_prompt = system_prompt
        
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
        
    # New methods for food preferences
    
    async def save_food_preferences(
        self,
        user_id: int,
        dietary_restrictions: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        preferred_cuisines: Optional[List[str]] = None
    ) -> List[UserFoodPreference]:
        """Save multiple food preferences for a user"""
        # Delete existing preferences first
        if dietary_restrictions is not None:
            await self.session.execute(
                delete(UserFoodPreference)
                .where(
                    UserFoodPreference.user_id == user_id,
                    UserFoodPreference.preference_type == 'dietary_restrictions'
                )
            )
            
        if allergies is not None:
            await self.session.execute(
                delete(UserFoodPreference)
                .where(
                    UserFoodPreference.user_id == user_id,
                    UserFoodPreference.preference_type == 'allergies'
                )
            )
            
        if preferred_cuisines is not None:
            await self.session.execute(
                delete(UserFoodPreference)
                .where(
                    UserFoodPreference.user_id == user_id,
                    UserFoodPreference.preference_type == 'preferred_cuisines'
                )
            )
        
        # Create new preferences
        preferences = []
        
        if dietary_restrictions:
            for restriction in dietary_restrictions:
                pref = UserFoodPreference(
                    user_id=user_id,
                    preference_type='dietary_restrictions',
                    preference_value=restriction
                )
                self.session.add(pref)
                preferences.append(pref)
                
        if allergies:
            for allergy in allergies:
                pref = UserFoodPreference(
                    user_id=user_id,
                    preference_type='allergies',
                    preference_value=allergy
                )
                self.session.add(pref)
                preferences.append(pref)
                
        if preferred_cuisines:
            for cuisine in preferred_cuisines:
                pref = UserFoodPreference(
                    user_id=user_id,
                    preference_type='preferred_cuisines',
                    preference_value=cuisine
                )
                self.session.add(pref)
                preferences.append(pref)
        
        if preferences:
            await self.session.commit()
            
        return preferences
    
    async def save_preference_settings(
        self,
        user_id: int,
        spice_level: Optional[str] = None,
        additional_info: Optional[str] = None
    ) -> UserPreferenceSettings:
        """Save or update preference settings for a user"""
        # Check if settings already exist
        query = select(UserPreferenceSettings).where(UserPreferenceSettings.user_id == user_id)
        result = await self.session.execute(query)
        settings = result.scalars().first()
        
        if settings:
            # Update existing settings
            if spice_level is not None:
                settings.spice_level = spice_level
            if additional_info is not None:
                settings.additional_info = additional_info
        else:
            # Create new settings
            settings = UserPreferenceSettings(
                user_id=user_id,
                spice_level=spice_level,
                additional_info=additional_info
            )
            self.session.add(settings)
        
        await self.session.commit()
        await self.session.refresh(settings)
        return settings
    
    async def get_food_preferences(self, user_id: int) -> Dict[str, List[str]]:
        """Get all food preferences for a user, organized by type"""
        query = select(UserFoodPreference).where(UserFoodPreference.user_id == user_id)
        result = await self.session.execute(query)
        preferences = result.scalars().all()
        
        # Organize preferences by type
        organized = {
            "dietary_restrictions": [],
            "allergies": [],
            "preferred_cuisines": []
        }
        
        for pref in preferences:
            if pref.preference_type in organized:
                organized[pref.preference_type].append(pref.preference_value)
        
        return organized
    
    async def get_preference_settings(self, user_id: int) -> Optional[UserPreferenceSettings]:
        """Get preference settings for a user"""
        query = select(UserPreferenceSettings).where(UserPreferenceSettings.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_structured_preferences(self, user_id: int) -> Dict:
        """Get structured food preferences for a user."""
        # Get food preferences
        food_prefs = await self.get_food_preferences(user_id)
        
        # Get preference settings
        settings = await self.get_preference_settings(user_id)
        
        # Combine into a structured format
        result = {
            "dietary_restrictions": food_prefs.get("dietary_restrictions", []),
            "allergies": food_prefs.get("allergies", []),
            "preferred_cuisines": food_prefs.get("preferred_cuisines", []),
            "spice_level": settings.spice_level if settings else None,
            "additional_info": settings.additional_info if settings else None
        }
        
        return result

def get_profile_repository(session: AsyncSession = Depends(get_repository_session)) -> ProfileRepository:
    """
    Provides a ProfileRepository instance for dependency injection.
    
    Args:
        session: The database session
        
    Returns:
        An instance of ProfileRepository
    """
    return ProfileRepository(session) 