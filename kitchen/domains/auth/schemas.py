from pydantic import BaseModel, EmailStr, Field, ConfigDict, SecretStr
from typing import Optional
from datetime import datetime

class AuthBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class AuthCreate(BaseModel):
    """Schema for user creation"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "confirm_password": "strongpassword123"
            }
        }
    )

class AuthLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }
    )

class TokenSchema(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    )

class AuthResponse(BaseModel):
    """Schema for auth response"""
    id: int
    email: str
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "is_verified": True,
                "last_login": "2024-03-20T10:00:00Z",
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z"
            }
        }
    )

class ClientCredentialsRequest(BaseModel):
    client_id: str
    client_secret: SecretStr
    scope: str = ""  # Space-separated list of scopes

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str 