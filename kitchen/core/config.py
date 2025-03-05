from typing import Any, Optional, Dict, Callable
from pydantic import PostgresDsn, field_validator, SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import re
from urllib.parse import urlparse
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Function to discover all domain names - now just a utility function
def discover_domains() -> list[str]:
    """
    Discover all domain names in the domains directory.
    
    Returns:
        List of domain names
    """
    domains = []
    domains_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "domains")
    
    # Check if domains directory exists
    if not os.path.isdir(domains_dir):
        return domains
        
    # List all domain directories
    for domain_name in os.listdir(domains_dir):
        domain_path = os.path.join(domains_dir, domain_name)
        
        # Skip if not a directory
        if not os.path.isdir(domain_path):
            continue
            
        # Skip if domain has no routers.py file
        router_path = os.path.join(domain_path, "routers.py")
        if not os.path.isfile(router_path):
            continue
            
        domains.append(domain_name)
    
    return domains

# Dynamic settings provider class
class DynamicSettings:
    """
    Dynamic settings provider that discovers domains on demand.
    
    This allows us to avoid static configuration in settings for domains.
    """
    
    def __init__(self):
        """Initialize with empty caches."""
        self._domains = None
        self._feature_flags = None
        self._path_prefix_feature_flags = None
    
    def clear_cache(self):
        """Clear all cached values to force rediscovery."""
        self._domains = None
        self._feature_flags = None
        self._path_prefix_feature_flags = None
    
    @property
    def domains(self) -> list[str]:
        """Discover domains on first access and cache the result."""
        if self._domains is None:
            self._domains = discover_domains()
            logger.info(f"Discovered domains: {self._domains}")
        return self._domains
    
    @property
    def feature_flags(self) -> Dict[str, bool]:
        """Generate feature flags for all domains on first access."""
        if self._feature_flags is None:
            # Generate domain-specific feature flags
            domain_flags = {
                f"enable_{domain}_endpoints": True 
                for domain in self.domains
            }
            
            # Add any hardcoded feature flags
            extra_flags = {
                # Add any additional feature flags here that aren't domain-specific
            }
            
            self._feature_flags = {**domain_flags, **extra_flags}
            logger.info(f"Generated feature flags for domains: {list(domain_flags.keys())}")
        
        return self._feature_flags
    
    @property
    def path_prefix_feature_flags(self) -> Dict[str, str]:
        """Generate path prefix mappings for all domains on first access."""
        if self._path_prefix_feature_flags is None:
            # Generate standard path prefixes for all domains
            standard_prefixes = {
                f"/api/v1/{domain}/": f"enable_{domain}_endpoints"
                for domain in self.domains
            }
            
            # Add special case for query domain to handle both singular and plural forms
            if "query" in self.domains:
                standard_prefixes["/api/v1/queries/"] = "enable_query_endpoints"
            
            self._path_prefix_feature_flags = standard_prefixes
            logger.info(f"Generated path prefix mappings for domains: {list(self._path_prefix_feature_flags.keys())}")
        
        return self._path_prefix_feature_flags
    
    def get_feature_flag(self, flag_name: str, default: bool = True) -> bool:
        """Get a feature flag value with fallback to default."""
        return self.feature_flags.get(flag_name, default)
    
    def set_feature_flag(self, flag_name: str, value: bool) -> None:
        """Set a feature flag value."""
        if self._feature_flags is None:
            # Initialize feature flags if needed
            _ = self.feature_flags
        
        self._feature_flags[flag_name] = value
        logger.info(f"Set feature flag {flag_name} to {value}")

# Create a singleton instance
dynamic_settings = DynamicSettings()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_assignment=True
    )

    # Environment Settings
    ENVIRONMENT: str
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
    
    # Feature Flags - Now accessed through dynamic_settings rather than static config
    @property
    def FEATURE_FLAGS(self) -> Dict[str, bool]:
        """Dynamic access to feature flags."""
        return dynamic_settings.feature_flags
    
    # Path Feature Flags - Empty static dict, we'll use dynamic_settings
    PATH_FEATURE_FLAGS: Dict[str, str] = {}
    
    # Dynamic path prefix mappings
    @property
    def PATH_PREFIX_FEATURE_FLAGS(self) -> Dict[str, str]:
        """Dynamic access to path prefix mappings."""
        return dynamic_settings.path_prefix_feature_flags
    
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

    # Custom method to get a feature flag with default fallback
    def get_feature_flag(self, flag_name: str, default: bool = True) -> bool:
        """Get a feature flag value with fallback to default."""
        return dynamic_settings.get_feature_flag(flag_name, default)
    
    # Custom method to set a feature flag
    def set_feature_flag(self, flag_name: str, value: bool) -> None:
        """Set a feature flag value."""
        dynamic_settings.set_feature_flag(flag_name, value)
    
    # Helper to rediscover domains and refresh all dynamic settings
    def refresh_domains(self) -> list[str]:
        """Rediscover domains and refresh all dynamic settings."""
        dynamic_settings.clear_cache()
        return dynamic_settings.domains


settings = Settings() 