from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any
from ..utils import get_env_var
from core.config import settings as core_settings

class GeminiConfig(BaseSettings):
    """Configuration settings for the Gemini provider."""
    
    # Try to get API key from core settings first, then environment variable
    api_key: str = Field(
        default_factory=lambda: getattr(core_settings, "GEMINI_API_KEY", "") or get_env_var("GEMINI_API_KEY")
    )
    model: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None
    top_p: float = 0.95
    top_k: int = 40
    
    model_config = {"env_prefix": "GEMINI_"} 