from typing import Optional
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
    
    async def create_profile(self, user_id: int, name: str, dob: Optional[date] = None) -> Profile:
        """Create a new profile"""
        profile = Profile(id=user_id, name=name, dob=dob)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def update_profile(self, profile: Profile, name: str = None, dob: Optional[date] = None) -> Profile:
        """Update an existing profile"""
        if name is not None:
            profile.name = name
        if dob is not None:
            profile.dob = dob
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def save(self, profile: Profile) -> Profile:
        """Save a profile to the database"""
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile 