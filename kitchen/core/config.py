from typing import Any, Optional
from pydantic import PostgresDsn, field_validator, SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import re
from urllib.parse import urlparse


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_assignment=True
    )

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # PostgreSQL Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URI: str | None = None
    
    # Security Settings
    LOGIN_ATTEMPTS_LIMIT: int = 3
    LOGIN_ATTEMPTS_LOCK_TIME: int = 4  # hours
    
    # Construct Database URL
    @field_validator("SQLALCHEMY_DATABASE_URI")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: Any) -> Any:
        if isinstance(v, str):
            return v

        host = info.data.get("POSTGRES_SERVER", "host.docker.internal").strip()
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=host,
            port=int(info.data.get("POSTGRES_PORT", 5432)),
            path=f"{info.data.get('POSTGRES_DB', '')}"
        ).unicode_string()

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] | str = []
    
    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: list[str] | str) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            # If it's a string but not a JSON array, treat it as a comma-separated list
            if not v:
                return []
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            validated_origins = []
            
            for origin in origins:
                # Ensure the origin has a scheme
                if not re.match(r'^\w+://', origin):
                    origin = f"http://{origin}"
                
                try:
                    # Basic URL validation
                    result = urlparse(origin)
                    if not all([result.scheme, result.netloc]):
                        raise ValueError(f"Invalid URL format: {origin}")
                    
                    if result.scheme not in ("http", "https"):
                        raise ValueError(f"URL must use http or https scheme: {origin}")
                    
                    validated_origins.append(origin)
                except Exception as e:
                    raise ValueError(f"Invalid origin URL: {origin}. Error: {str(e)}")
            
            return list(dict.fromkeys(validated_origins))
        return v

    # File Upload Settings
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_FILE_SIZE: int = 100_000_000  # 100MB in bytes

    # FTP Settings - Made optional with default values
    FTP_HOST: Optional[str] = None
    FTP_USER: Optional[str] = None
    FTP_PASSWORD: Optional[str] = None
    FTP_PORT: int = 21
    FTP_ROOT_DIR: Optional[str] = None

    # OAuth2 Client Credentials Settings
    OAUTH2_CLIENT_ID: Optional[str] = None
    OAUTH2_CLIENT_SECRET: Optional[SecretStr] = None
    OAUTH2_TOKEN_URL: str = f"{API_V1_STR}/auth/login-by-email-password"
    OAUTH2_SCOPES: dict[str, str] = {
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access"
    }
    
    # Client Credentials Settings
    CLIENT_CREDENTIALS_EXPIRE_MINUTES: int = 60
    ALLOWED_CLIENT_URLS: str = ""  # Changed to str to accept raw string from .env
    PROCESSED_CLIENT_URLS: list[str] = []  # New field for processed URLs
    
    # Request Logging Settings
    SENSITIVE_PATHS: list[str] = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/users/reset-password",
        "/api/v1/payments/process",
        "/api/v1/auth/register-by-email-password",
    ]
    
    SENSITIVE_PATH_PREFIXES: list[str] = [
        "/api/v1/auth/token",
        "/api/v1/payments/", 
        "/api/v1/users/profile",
    ]
    
    @field_validator("PROCESSED_CLIENT_URLS", mode="before")
    @classmethod
    def process_client_urls(cls, v: Any, info: Any) -> list[str]:
        """
        Process ALLOWED_CLIENT_URLS from raw string to validated list of URLs
        """
        raw_urls = info.data.get("ALLOWED_CLIENT_URLS", "")
        
        def validate_url(url: str) -> str:
            url = url.strip()
            if not re.match(r'^\w+://', url):
                url = f"http://{url}"
            
            try:
                result = urlparse(url)
                if not all([result.scheme, result.netloc]):
                    raise ValueError(f"Invalid URL format: {url}")
                
                if result.scheme not in ("http", "https"):
                    raise ValueError(f"URL must use http or https scheme: {url}")
                
                return url
            except Exception as e:
                raise ValueError(f"Invalid URL: {url}. Error: {str(e)}")

        if not raw_urls:
            return []
            
        # Split and validate URLs
        urls = [url.strip() for url in raw_urls.split(",") if url.strip()]
        validated_urls = []
        
        for url in urls:
            try:
                validated_url = validate_url(url)
                validated_urls.append(validated_url)
            except ValueError as e:
                raise ValueError(f"URL validation failed: {str(e)}")

        return list(dict.fromkeys(validated_urls))


settings = Settings() 