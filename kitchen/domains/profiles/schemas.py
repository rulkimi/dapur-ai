from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ProfileBase(BaseModel):
    """Base schema for profile data"""
    name: str = Field(..., min_length=1, max_length=255)
    dob: Optional[date] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""
    pass


class ProfileUpdate(BaseModel):
    """Schema for updating an existing profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    dob: Optional[date] = None


class ProfileResponse(ProfileBase):
    """Schema for profile response"""
    id: int
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility
        from_attributes = True  # For backwards compatibility with Pydantic v1 