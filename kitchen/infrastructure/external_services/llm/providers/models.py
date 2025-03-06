from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ProviderType(str, Enum):
    """Types of LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    # Add more as needed

class ModelType(str, Enum):
    """Types of models available for each provider."""
    # Gemini models
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_FLASH = "gemini-1.5-flash"
    # OpenAI models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    # Add more as needed

class Message(BaseModel):
    """A message in a conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    
class Conversation(BaseModel):
    """A conversation between a user and an LLM."""
    messages: List[Message]
    
class LLMRequest(BaseModel):
    """A request to an LLM provider."""
    provider: ProviderType
    model: ModelType
    prompt: Optional[str] = None
    messages: Optional[List[Message]] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    extra_params: Dict[str, Any] = Field(default_factory=dict)
    
class LLMResponse(BaseModel):
    """A response from an LLM provider."""
    content: str
    provider: ProviderType
    model: ModelType
    usage: Optional[Dict[str, int]] = None
    raw_response: Optional[Any] = None 