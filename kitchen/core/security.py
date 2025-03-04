from typing import Annotated, Union, Any, Dict, TYPE_CHECKING
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from passlib.context import CryptContext
from core.config import settings
from domains.auth.models import Auth, Anonymous
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository import get_repository_session
from core.exceptions import (
    UnauthorizedException, 
    ForbiddenException, 
    ServiceException
)

if TYPE_CHECKING:
    # Import for type checking only
    from domains.auth.repositories import AuthRepository

# Password handling
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",  # Explicitly set the bcrypt identifier
    bcrypt__min_rounds=12  # Set default rounds
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login-by-email-password",
    scopes=settings.OAUTH2_SCOPES,
    auto_error=False  # This makes the token optional
)

async def get_current_auth(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_repository_session)
):
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = UnauthorizedException(
        message="Could not validate credentials",
        details={"authenticate": "Bearer"}
    )
    
    # Handle case where token is None (unauthenticated request)
    if token is None:
        return Anonymous()
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        auth_id: str = payload.get("sub")
        if auth_id is None:
            raise credentials_exception
            
        # Check if user data is in token
        user_data = payload.get("user")
        if user_data:
            # Create Auth instance from token data
            auth = Auth(
                id=user_data.get("id"),
                email=user_data.get("email"),
                is_active=user_data.get("is_active", True),
                hashed_password="",  # Not needed for most operations
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            # Set additional attributes if available
            if "is_superuser" in user_data:
                auth.is_superuser = user_data.get("is_superuser")
            if "is_verified" in user_data:
                auth.is_verified = user_data.get("is_verified")
                
            return auth
    except JWTError:
        raise credentials_exception
        
    # Import here to avoid circular import
    from domains.auth.repositories import AuthRepository
    repository = AuthRepository(session)
    auth = await repository.get_auth_by_id(int(auth_id))
    
    if auth is None:
        raise credentials_exception
        
    return auth

def get_optional_current_active_user(
    current_auth: Union[Auth, Anonymous] = Depends(get_current_auth)
) -> Union[Auth, Anonymous]:
    """
    Returns the current user if authenticated, or an anonymous user instance.
    """
    if isinstance(current_auth, Anonymous):
        return current_auth
    
    if not current_auth.is_active:
        raise ForbiddenException(message="Inactive user")
    return current_auth

def get_current_user(
    current_auth: Auth = Depends(get_current_auth)
) -> Dict[str, Any]:
    """
    Returns the current authenticated user as a dictionary.
    Raises an exception if the user is not authenticated or not active.
    
    This is used for endpoints that require authentication.
    """
    if isinstance(current_auth, Anonymous):
        raise UnauthorizedException(
            message="Authentication required",
            details={"authenticate": "Bearer"}
        )
    
    if not current_auth.is_active:
        raise ForbiddenException(message="Inactive user")
    
    print("current_auth",current_auth)
    # Convert Auth model to dict with additional info
    user_data = {
        "id": current_auth.id,
        "email": current_auth.email,
        "is_active": current_auth.is_active,
        "is_superuser": getattr(current_auth, "is_superuser", False),
        "created_at": current_auth.created_at,
        "updated_at": current_auth.updated_at
    }
    
    return user_data

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None, user_data: Dict[str, Any] = None
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Add user data to token if provided
    if user_data:
        to_encode.update({"user": user_data})
        
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

class ClientCredentialsManager:
    def __init__(self):
        self.client_id = settings.OAUTH2_CLIENT_ID
        self.client_secret = settings.OAUTH2_CLIENT_SECRET
        self.allowed_urls = settings.PROCESSED_CLIENT_URLS
        self.token_expire_minutes = settings.CLIENT_CREDENTIALS_EXPIRE_MINUTES

    def create_client_token(self, scopes: list[str]) -> dict:
        """Create a new client credentials token"""
        if not self.client_id or not self.client_secret:
            raise ServiceException(
                message="Client credentials not configured",
                details={"missing_config": "OAuth2 client credentials"}
            )

        data = {
            "sub": self.client_id,
            "scopes": scopes,
            "token_type": "client_credentials",
            "exp": datetime.now(UTC) + timedelta(minutes=self.token_expire_minutes)
        }

        token = jwt.encode(
            data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": self.token_expire_minutes * 60,
            "scope": " ".join(scopes)
        }

    def verify_client_credentials(
        self,
        client_id: str,
        client_secret: SecretStr
    ) -> bool:
        """Verify client credentials"""
        # Handle case where client_secret is None
        if not self.client_id or not self.client_secret:
            return False
            
        return (
            client_id == self.client_id and
            client_secret.get_secret_value() == self.client_secret.get_secret_value()
        )

    def validate_client_origin(self, origin: str) -> bool:
        """Validate if the client origin is allowed"""
        return origin in self.allowed_urls

client_credentials_manager = ClientCredentialsManager() 