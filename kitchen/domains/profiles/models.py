from sqlalchemy import Column, String, Date, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=True)
    
    # New fields for onboarding
    system_prompt = Column(Text, nullable=True)
    
    # Relationship with Auth User
    user = relationship("Auth", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, name={self.name})>"


class UserFoodPreference(Base):
    """Model for storing array-type food preferences (dietary restrictions, allergies, cuisines)."""
    __tablename__ = "user_food_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), index=True)
    preference_type = Column(String(50), index=True)  # 'dietary_restrictions', 'allergies', 'preferred_cuisines'
    preference_value = Column(String(255), index=True)
    
    # Add a unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('user_id', 'preference_type', 'preference_value', name='unique_user_preference'),
    )
    
    # Relationship with Auth User (will need to add the back reference in the Auth model)
    
    def __repr__(self) -> str:
        return f"<UserFoodPreference(user_id={self.user_id}, type={self.preference_type}, value={self.preference_value})>"


class UserPreferenceSettings(Base):
    """Model for storing scalar user preferences (spice level, additional info)."""
    __tablename__ = "user_preference_settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), index=True, unique=True)
    spice_level = Column(String(50), nullable=True)
    additional_info = Column(Text, nullable=True)
    
    # Relationship with Auth User (will need to add the back reference in the Auth model)
    
    def __repr__(self) -> str:
        return f"<UserPreferenceSettings(user_id={self.user_id}, spice_level={self.spice_level})>" 