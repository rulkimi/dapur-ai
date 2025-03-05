from .protocols import LLMProvider, StreamingLLMProvider
from .models import ProviderType, ModelType, Message, Conversation
from .exceptions import ProviderError, AuthenticationError, RateLimitError, InvalidResponseError
from .factory import ProviderFactory

# Register providers
from .gemini.services import GeminiProvider
ProviderFactory.register(ProviderType.GEMINI, GeminiProvider)

# Convenience function for FastAPI dependency injection
def get_llm_provider(provider_type: ProviderType = ProviderType.GEMINI) -> LLMProvider:
    """Get an LLM provider for dependency injection."""
    return ProviderFactory.get_provider(provider_type) 