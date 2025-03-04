from sqlalchemy import Column, String, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship
from db.base import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=True)
    
    # Relationship with Auth User
    user = relationship("Auth", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, name={self.name})>" 