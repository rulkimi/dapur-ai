from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any
from ..utils import get_env_var

class GeminiConfig(BaseSettings):
    """Configuration settings for the Gemini provider."""
    
    api_key: str = Field(default_factory=lambda: get_env_var("GEMINI_API_KEY"))
    model: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None
    top_p: float = 0.95
    top_k: int = 40
    
    model_config = {"env_prefix": "GEMINI_"} 