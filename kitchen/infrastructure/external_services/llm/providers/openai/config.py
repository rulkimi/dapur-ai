from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any
from ..utils import get_env_var
from core.config import settings as core_settings

class OpenAIConfig(BaseSettings):
    """Configuration settings for the OpenAI provider."""
    
    # Try to get API key from core settings first, then environment variable
    api_key: str = Field(
        default_factory=lambda: getattr(core_settings, "OPENAI_API_KEY", "") or get_env_var("OPENAI_API_KEY")
    )
    model: str = "gpt-4"  # Default model
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Additional parameters for Pydantic AI
    extra_params: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"env_prefix": "OPENAI_"} 