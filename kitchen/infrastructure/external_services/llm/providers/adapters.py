from typing import Dict, Any, Type
from infrastructure.external_services.llm.providers.models import LLMResponse, ProviderType, ModelType
from .protocols import LLMProvider

class ResponseAdapter:
    """Adapts provider-specific responses to a standardized format."""
    
    @staticmethod
    def adapt_gemini_response(response: Any, model: str) -> LLMResponse:
        """Adapt a Gemini response to the standard LLMResponse format."""
        return LLMResponse(
            content=response.text,
            provider=ProviderType.GEMINI,
            model=model,
            raw_response=response
        )
    
    # Add more adapters as needed for different providers 