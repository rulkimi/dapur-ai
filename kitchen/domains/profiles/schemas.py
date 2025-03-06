from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class UserFoodPreferenceCreate(BaseModel):
    """Schema for creating a food preference."""
    preference_type: str
    preference_value: str


class UserFoodPreferenceOut(UserFoodPreferenceCreate):
    """Schema for food preference output."""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)


class UserPreferenceSettingsCreate(BaseModel):
    """Schema for creating preference settings."""
    spice_level: Optional[str] = None
    additional_info: Optional[str] = None


class UserPreferenceSettingsOut(UserPreferenceSettingsCreate):
    """Schema for preference settings output."""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)


class StructuredFoodPreferencesOut(BaseModel):
    """Schema for structured food preferences output."""
    dietary_restrictions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    preferred_cuisines: List[str] = Field(default_factory=list)
    spice_level: Optional[str] = None
    additional_info: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProfileBase(BaseModel):
    """Base schema for profile data"""
    name: str
    dob: Optional[date] = None
    system_prompt: Optional[str] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""
    pass


class ProfileUpdate(BaseModel):
    """Schema for updating an existing profile"""
    name: Optional[str] = None
    dob: Optional[date] = None
    system_prompt: Optional[str] = None


class ProfileOut(ProfileBase):
    """Schema for profile output."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)  # For Pydantic v2 compatibility


class ProfileDetailOut(ProfileOut):
    """Schema for detailed profile output including structured food preferences."""
    structured_preferences: Optional[StructuredFoodPreferencesOut] = None


class ProfileResponse(ProfileOut):
    """Schema for profile API responses."""
    user_id: int  # Link to the user
    
    model_config = ConfigDict(from_attributes=True)