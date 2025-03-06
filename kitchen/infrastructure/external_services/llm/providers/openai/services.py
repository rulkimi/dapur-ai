import json
import re
from typing import Type, List, Dict, Any, AsyncIterable, Optional, Union
from pydantic import BaseModel, ValidationError

# Import Pydantic AI components
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent

# Import core settings
from core.config import settings

from ..protocols import StreamingLLMProvider
from ..models import ProviderType, ModelType, Message
from ..exceptions import (
    ProviderError, 
    AuthenticationError, 
    RateLimitError, 
    InvalidResponseError, 
    ConfigurationError, 
    SchemaValidationError
)
from .config import OpenAIConfig

class OpenAIProvider(StreamingLLMProvider):
    """Provider implementation for OpenAI models using Pydantic AI."""
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        """Initialize the OpenAI provider with a configuration."""
        self.config = config or OpenAIConfig()
        
        try:
            # Use API key from core settings if not already set in config
            if not self.config.api_key and hasattr(settings, 'OPENAI_API_KEY'):
                self.config.api_key = settings.OPENAI_API_KEY
                
            # Check if API key is set
            if not self.config.api_key:
                raise ConfigurationError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable or in your application settings.")
                
            # Initialize using Pydantic AI's OpenAI model - only pass essential parameters
            self.model = OpenAIModel(
                model_name=self.config.model,
                api_key=self.config.api_key
            )
            
            # Create an Agent instance with the model
            self.agent = Agent(self.model)
            
            # Save config for later use in methods
            self.temperature = self.config.temperature
            self.max_tokens = self.config.max_tokens
            self.top_p = self.config.top_p
            self.frequency_penalty = self.config.frequency_penalty
            self.presence_penalty = self.config.presence_penalty
            self.extra_params = self.config.extra_params
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize OpenAIProvider: {str(e)}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using OpenAI models via Pydantic AI."""
        try:
            # Get parameters from kwargs or use defaults from config
            generation_kwargs = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            }
            
            # Filter out None values
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # Use Pydantic AI's agent for text generation
            result = await self.agent.run(
                user_prompt=prompt,
                model_settings=generation_kwargs
            )
            
            # Handle AgentRunResult object
            if hasattr(result, 'data'):
                return str(result.data)
            else:
                return str(result)
        except Exception as e:
            self._handle_openai_error(e)
            
    async def extract(self, prompt: str, schema: Type[BaseModel], **kwargs) -> BaseModel:
        """Extract structured data from LLM responses using Pydantic schemas."""
        try:
            # Get parameters from kwargs or use defaults from config
            generation_kwargs = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            }
            
            # Filter out None values
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # Create a detailed system prompt with the schema
            schema_json = schema.model_json_schema()
            schema_json_str = json.dumps(schema_json, indent=2)
            
            system_prompt = f"""
You are a helpful assistant that extracts structured data from text.
Your response must be a valid JSON object matching the following schema:

{schema_json_str}

Important instructions:
1. Return ONLY the JSON object, with no other text before or after
2. Do NOT include markdown formatting or code blocks
3. Ensure all required fields are included
4. Make sure the output is valid JSON that can be parsed by Python's json.loads()
5. Ensure enum fields use the correct values
6. Do not include any fields not specified in the schema
"""
            
            # Set a system prompt for the agent
            full_prompt = f"{system_prompt}\n\nExtract information from this text: {prompt}"
            
            # Use the run method instead of chat
            response = await self.agent.run(
                user_prompt=full_prompt,
                model_settings=generation_kwargs
            )
            
            # Extract JSON from response - handle AgentRunResult object
            if hasattr(response, 'data'):
                json_response = response.data
            else:
                json_response = str(response)
            
            # Try to extract JSON from the response
            json_data = self._extract_json(json_response)
            
            try:
                # Validate the extracted data against the schema
                validated_data = schema.model_validate_json(json_data)
                return validated_data
            except ValidationError as e:
                raise SchemaValidationError(f"Failed to validate schema: {str(e)}\nResponse: {json_response}")
                
        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Failed to parse JSON from response: {str(e)}\nResponse: {json_response}")
        except Exception as e:
            self._handle_openai_error(e)
            
    def _extract_json(self, text: str) -> str:
        """Extract JSON from a text string that might contain other text."""
        # Look for JSON content between triple backticks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        
        if json_match:
            return json_match.group(1).strip()
            
        # If no triple backticks, try to find JSON between { and }
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            return json_match.group(0).strip()
            
        # If nothing else works, return the whole text
        return text.strip()
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat response."""
        try:
            # Get parameters from kwargs or use defaults from config
            generation_kwargs = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            }
            
            # Filter out None values
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # Format messages as conversation
            conversation = ""
            for msg in messages:
                if "role" not in msg or "content" not in msg:
                    raise ValueError("Each message must have 'role' and 'content' keys")
                    
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    conversation += f"User: {content}\n"
                elif role == "model" or role == "assistant":
                    conversation += f"Assistant: {content}\n"
                elif role == "system":
                    conversation += f"System: {content}\n"
            
            # Add final prompt for assistant
            conversation += "Assistant: "
            
            # Generate response using run method
            result = await self.agent.run(
                user_prompt=conversation,
                model_settings=generation_kwargs
            )
            
            # Handle AgentRunResult object
            if hasattr(result, 'data'):
                return str(result.data)
            else:
                return str(result)
        except Exception as e:
            self._handle_openai_error(e)
    
    async def stream(self, prompt: str, **kwargs) -> AsyncIterable[str]:
        """Stream text generation results."""
        try:
            # Get parameters from kwargs or use defaults from config
            generation_kwargs = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
                "stream": True
            }
            
            # Filter out None values
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # Check if the model has streaming capability (some older models might not)
            if hasattr(self.agent, 'stream'):
                # Use streaming capability
                try:
                    async with self.agent.stream(
                        user_prompt=prompt,
                        model_settings=generation_kwargs
                    ) as stream:
                        async for chunk in stream:
                            # Handle different chunk formats
                            if hasattr(chunk, 'text'):
                                yield chunk.text
                            elif hasattr(chunk, 'data'):
                                yield str(chunk.data)
                            elif hasattr(chunk, 'content'):
                                yield chunk.content
                            else:
                                yield str(chunk)
                except Exception as e:
                    self._handle_openai_error(e)
            else:
                # Fallback to run method if stream is not available
                result = await self.agent.run(
                    user_prompt=prompt,
                    model_settings=generation_kwargs
                )
                
                # Handle AgentRunResult object
                if hasattr(result, 'data'):
                    yield str(result.data)
                else:
                    yield str(result)
        except Exception as e:
            self._handle_openai_error(e)
            
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterable[str]:
        """Stream chat responses."""
        try:
            # Get parameters from kwargs or use defaults from config
            generation_kwargs = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
                "stream": True
            }
            
            # Filter out None values
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # Format messages as conversation
            conversation = ""
            for msg in messages:
                if "role" not in msg or "content" not in msg:
                    raise ValueError("Each message must have 'role' and 'content' keys")
                    
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    conversation += f"User: {content}\n"
                elif role == "model" or role == "assistant":
                    conversation += f"Assistant: {content}\n"
                elif role == "system":
                    conversation += f"System: {content}\n"
            
            # Add final prompt for assistant
            conversation += "Assistant: "
            
            # Check if the model has streaming capability (some older models might not)
            if hasattr(self.agent, 'stream'):
                # Use streaming capability
                try:
                    async with self.agent.stream(
                        user_prompt=conversation,
                        model_settings=generation_kwargs
                    ) as stream:
                        async for chunk in stream:
                            # Handle different chunk formats
                            if hasattr(chunk, 'text'):
                                yield chunk.text
                            elif hasattr(chunk, 'data'):
                                yield str(chunk.data)
                            elif hasattr(chunk, 'content'):
                                yield chunk.content
                            else:
                                yield str(chunk)
                except Exception as e:
                    self._handle_openai_error(e)
            else:
                # Fallback to run method if stream is not available
                result = await self.agent.run(
                    user_prompt=conversation,
                    model_settings=generation_kwargs
                )
                
                # Handle AgentRunResult object
                if hasattr(result, 'data'):
                    yield str(result.data)
                else:
                    yield str(result)
        except Exception as e:
            self._handle_openai_error(e)
    
    def _handle_openai_error(self, error: Exception) -> None:
        """Handle OpenAI-specific errors and convert them to our exception types."""
        error_message = str(error)
        
        if "Unauthorized" in error_message or "Authentication" in error_message:
            raise AuthenticationError(f"OpenAI authentication error: {error_message}")
        elif "Rate limit" in error_message or "RateLimitError" in error_message:
            raise RateLimitError(f"OpenAI rate limit error: {error_message}")
        elif "validation error" in error_message.lower():
            raise SchemaValidationError(f"Schema validation error: {error_message}")
        else:
            raise ProviderError(f"OpenAI error: {error_message}") 