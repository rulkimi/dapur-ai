from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from db.base import Base

class Auth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Add the relationship to Profile
    profile = relationship("Profile", back_populates="user", uselist=False)
    
    # Add relationships to food preferences models
    food_preferences = relationship("UserFoodPreference", 
                                    cascade="all, delete-orphan",
                                    backref="user")
    preference_settings = relationship("UserPreferenceSettings", 
                                       cascade="all, delete-orphan", 
                                       uselist=False,
                                       backref="user")

    def verify_password(self, plain_password: str) -> bool:
        """Verify if the provided plain password matches the stored hashed password"""
        from core.security import verify_password as verify_pwd
        return verify_pwd(plain_password, self.hashed_password)

    def __repr__(self) -> str:
        return f"<Auth(email={self.email}, is_active={self.is_active}, is_superuser={self.is_superuser})>"


class Anonymous:
    """Represents an anonymous/unauthenticated user"""
    id: int = 0
    email: str = "anonymous@example.com"
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False
    is_deleted: bool = False
    is_locked: bool = False
    is_anonymous: bool = True
    last_login: datetime | None = None
    failed_login_attempts: int = 0
    locked_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __repr__(self) -> str:
        return "<Anonymous User>"

