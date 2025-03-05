from typing import Dict, Type, Optional, Any
from .protocols import LLMProvider
from .models import ProviderType
from .exceptions import ConfigurationError

class ProviderFactory:
    """Factory for creating and managing LLM provider instances."""
    
    _registry: Dict[ProviderType, Type[LLMProvider]] = {}
    _instances: Dict[ProviderType, LLMProvider] = {}
    
    @classmethod
    def register(cls, provider_type: ProviderType, provider_class: Type[LLMProvider]) -> None:
        """Register a provider class for a specific provider type."""
        cls._registry[provider_type] = provider_class
        
    @classmethod
    def get_provider(cls, provider_type: ProviderType, **kwargs) -> LLMProvider:
        """Get a provider instance, creating it if it doesn't exist."""
        if provider_type not in cls._instances:
            if provider_type not in cls._registry:
                raise ConfigurationError(f"Provider {provider_type} not registered")
            
            provider_class = cls._registry[provider_type]
            cls._instances[provider_type] = provider_class(**kwargs)
            
        return cls._instances[provider_type]
        
    @classmethod
    def reset(cls) -> None:
        """Reset all provider instances."""
        cls._instances.clear() 