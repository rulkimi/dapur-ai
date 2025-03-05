from typing import TypeVar, Generic, Type, Dict, Any, Optional
from pydantic import BaseModel, create_model, Field
from pydantic_ai import Agent

# Type variable for generic output schema
T = TypeVar('T', bound=BaseModel)

class BaseInputSchema(BaseModel):
    """Base schema for inputs to LLM providers."""
    prompt: str
    
class BaseOutputSchema(BaseModel):
    """Base schema for outputs from LLM providers."""
    pass
    
class ExtractorAgent(Generic[T]):
    """Agent that uses Pydantic AI to extract structured data from LLM outputs."""
    
    def __init__(self, schema: Type[T], agent: Agent):
        self.schema = schema
        self.agent = agent
        
    async def extract(self, prompt: str, **kwargs) -> T:
        """Extract structured data using Pydantic AI."""
        result = await self.agent.extract(self.schema, prompt=prompt, **kwargs)
        return result 