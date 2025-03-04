from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from domains.auth.models import Auth
from core.security import get_password_hash, verify_password
from db.repository import BaseRepository, get_repository_session
from sqlalchemy.exc import IntegrityError
from core.exceptions import (
    ConflictException, 
    get_or_404, 
    handle_db_integrity_error
)

class AuthRepository(BaseRepository[Auth]):
    def __init__(self, session: AsyncSession = Depends(get_repository_session)):
        super().__init__(Auth, session)

    async def get_auth_by_email(self, username: str) -> Optional[Auth]:
        """Get auth record by email."""
        result = await self.session.execute(
            select(Auth).where(Auth.email == username)
        )
        return result.scalar_one_or_none()

    async def get_auth_by_id(self, auth_id: int) -> Optional[Auth]:
        """Get auth record by id."""
        return await self.get(auth_id)

    async def create_auth_by_email_password(self, email: str, password: str) -> Auth:
        """Create new auth record."""
        # Check if user already exists to prevent race conditions
        existing_user = await self.get_auth_by_email(email)
        if existing_user:
            raise ConflictException(
                message="Email already registered",
                details={"field": "email"}
            )
            
        auth = Auth(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=False,
            is_verified=False,
            failed_login_attempts=0,
            is_locked=False
        )
        
        try:
            self.session.add(auth)
            await self.session.commit()
            await self.session.refresh(auth)
            return auth
        except IntegrityError as e:
            await self.session.rollback()
            # Handle integrity errors
            handle_db_integrity_error(e, "Email already registered")
            # The line below will never be executed as handle_db_integrity_error always raises an exception
            # But it's included for completeness
            return None  # type: ignore

    async def update_auth(self, auth: Auth) -> Auth:
        """
        Update auth record.
        
        Args:
            auth: Auth object with updated values
            
        Returns:
            Updated Auth object
        """
        self.session.add(auth)
        await self.session.commit()
        await self.session.refresh(auth)
        return auth

    async def authenticate(self, email: str, password: str) -> Optional[Auth]:
        """
        Verify email and password and return auth if valid.
        
        Args:
            email: User's email
            password: User's plain password
            
        Returns:
            Auth object if credentials are valid, None otherwise
        """
        auth = await self.get_auth_by_email(email)
        if not auth:
            return None
            
        if not verify_password(password, auth.hashed_password):
            return None
            
        if not auth.is_active:
            return None
            
        return auth

    async def delete_auth(self, auth: Auth) -> None:
        """Soft delete auth record."""
        auth.is_active = False
        auth.is_deleted = True
        await self.update_auth(auth) 