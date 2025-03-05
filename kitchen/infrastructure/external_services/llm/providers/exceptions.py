class ProviderError(Exception):
    """Base exception for all provider errors."""
    pass

class AuthenticationError(ProviderError):
    """Raised when there's an authentication failure with the provider."""
    pass
    
class RateLimitError(ProviderError):
    """Raised when a rate limit is hit."""
    pass
    
class InvalidResponseError(ProviderError):
    """Raised when a provider returns an invalid response."""
    pass
    
class ConfigurationError(ProviderError):
    """Raised when there's a configuration issue."""
    pass
    
class SchemaValidationError(ProviderError):
    """Raised when schema validation fails."""
    pass 