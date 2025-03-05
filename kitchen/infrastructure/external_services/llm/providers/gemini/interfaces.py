from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class GeminiRole(str, Enum):
    """Roles in a Gemini conversation."""
    USER = "user"
    MODEL = "model"
    SYSTEM = "system"

class GeminiMessage(BaseModel):
    """A message in a Gemini conversation."""
    role: GeminiRole
    content: str
    
class GeminiRequestParams(BaseModel):
    """Parameters for Gemini requests."""
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None
    top_p: float = 0.95
    top_k: int = 40
    
class GeminiUsage(BaseModel):
    """Token usage information from Gemini."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int 