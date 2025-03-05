# LLM Integration with Pydantic AI and Google/Gemini

This module provides a flexible and extensible integration with Large Language Models (LLMs), starting with Google's Gemini models. It uses Pydantic AI for structured data extraction and validation.

## Features

- **Provider-agnostic interface**: Common interface for all LLM providers
- **Structured data extraction**: Extract typed data from LLM responses using Pydantic schemas
- **Streaming support**: Stream responses for better UX in chat applications
- **Error handling**: Comprehensive exception system for different error types
- **Factory pattern**: Easy provider registration and instantiation
- **Configuration management**: Flexible configuration options for each provider

## Directory Structure

```
providers/
├── __init__.py        # Exports key components and initializes module
├── adapters.py        # Adapter classes for converting between formats
├── protocols.py       # Core interface definitions all providers must implement 
├── exceptions.py      # Custom exceptions for standardized error handling
├── models.py          # Internal data models for consistent representation
├── schemas.py         # Pydantic schemas for validation with PydanticAI
├── utils.py           # Utility functions shared across providers
├── factory.py         # Provider factory/registry for instantiation
├── examples.py        # Usage examples
└── gemini/            # Gemini-specific implementation
   ├── __init__.py     # Exports Gemini components
   ├── config.py       # Configuration settings for Gemini
   ├── services.py     # Implementation of provider interfaces
   └── interfaces.py   # Gemini-specific interface details
```

## Usage Examples

### Basic Text Generation

```python
from providers import get_llm_provider, ProviderType

async def generate_text(prompt: str) -> str:
    provider = get_llm_provider(ProviderType.GEMINI)
    response = await provider.generate(prompt)
    return response
```

### Schema Extraction

```python
from pydantic import BaseModel, Field
from typing import List
from providers import get_llm_provider, ProviderType

class UserInfo(BaseModel):
    name: str = Field(description="The user's full name")
    age: int = Field(description="The user's age in years")
    interests: List[str] = Field(description="List of the user's interests or hobbies")

async def extract_user_info(text: str) -> UserInfo:
    provider = get_llm_provider(ProviderType.GEMINI)
    result = await provider.extract(text, UserInfo)
    return result
```

### Chat Completion

```python
from providers import get_llm_provider, ProviderType

async def chat_with_llm(messages: list) -> str:
    provider = get_llm_provider(ProviderType.GEMINI)
    response = await provider.chat(messages)
    return response
```

### Streaming Response

```python
from fastapi import WebSocket
from providers import get_llm_provider, ProviderType

async def stream_to_websocket(websocket: WebSocket, prompt: str):
    provider = get_llm_provider(ProviderType.GEMINI)
    
    await websocket.accept()
    
    try:
        async for chunk in provider.stream(prompt):
            await websocket.send_text(chunk)
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()
```

## Configuration

### Environment Variables

For Gemini:
- `GEMINI_API_KEY`: API key for Gemini
- `GEMINI_MODEL`: Model to use (default: "gemini-1.5-pro")
- `GEMINI_USE_VERTEX_AI`: Whether to use VertexAI (default: false)
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID (for VertexAI)

## Dependencies

- `pydantic`: Data validation
- `pydantic-ai`: LLM integration with Pydantic
- `httpx`: HTTP client

## Adding New Providers

To add a new provider:

1. Create a new subdirectory for the provider
2. Implement the provider interfaces defined in `protocols.py`
3. Register the provider in `__init__.py`

## Error Handling

The module provides several exception types for different error scenarios:

- `ProviderError`: Base exception for all provider errors
- `AuthenticationError`: Authentication failures
- `RateLimitError`: Rate limit exceeded
- `InvalidResponseError`: Invalid responses from the provider
- `ConfigurationError`: Configuration issues
- `SchemaValidationError`: Schema validation failures 