from typing import Protocol, AsyncIterable, Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel

class LLMProvider(Protocol):
    """Base protocol for LLM providers."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        ...
    
    async def extract(self, prompt: str, schema: Type[BaseModel], **kwargs) -> BaseModel:
        """Extract structured data from LLM responses using Pydantic schemas."""
        ...
        
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response based on a conversation history."""
        ...

class StreamingLLMProvider(LLMProvider, Protocol):
    """Protocol for providers that support streaming responses."""
    
    async def stream(self, prompt: str, **kwargs) -> AsyncIterable[str]:
        """Stream text generation results."""
        ...
    
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterable[str]:
        """Stream chat responses."""
        ... 