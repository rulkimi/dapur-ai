from typing import Optional
from domains.profiles.repositories import ProfileRepository
from domains.profiles.schemas import ProfileCreate, ProfileUpdate
from domains.profiles.models import Profile


class ProfileService:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository
    
    async def get_profile(self, user_id: int) -> Optional[Profile]:
        """Get a user's profile by user ID"""
        return await self.repository.get_by_user_id(user_id)
    
    async def create_profile(self, user_id: int, profile_data: ProfileCreate) -> Profile:
        """Create a new profile for a user"""
        return await self.repository.create_profile(
            user_id=user_id,
            name=profile_data.name,
            dob=profile_data.dob
        )
    
    async def update_profile(self, user_id: int, profile_data: ProfileUpdate) -> Optional[Profile]:
        """Update an existing profile"""
        profile = await self.get_profile(user_id)
        if not profile:
            return None
        
        return await self.repository.update_profile(
            profile=profile,
            name=profile_data.name if hasattr(profile_data, 'name') and profile_data.name is not None else None,
            dob=profile_data.dob if hasattr(profile_data, 'dob') and profile_data.dob is not None else None
        )
    
    async def get_or_create_profile(self, user_id: int, default_name: str = "") -> Profile:
        """Get a profile or create it if it doesn't exist"""
        profile = await self.get_profile(user_id)
        if not profile:
            profile = await self.repository.create_profile(
                user_id=user_id,
                name=default_name,
                dob=None
            )
        return profile 