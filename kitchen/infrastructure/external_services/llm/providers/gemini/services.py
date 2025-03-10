from typing import AsyncIterable, List, Dict, Type, Any, Optional, Union
import asyncio
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.result import FinalResult, AgentStream
import json
import re
from pydantic import ValidationError

# Import core settings
from core.config import settings

from ..protocols import StreamingLLMProvider
from ..exceptions import AuthenticationError, RateLimitError, InvalidResponseError, ConfigurationError, SchemaValidationError, ProviderError
from ..adapters import ResponseAdapter
from .config import GeminiConfig

class GeminiProvider(StreamingLLMProvider):
    """Provider implementation for Google's Gemini models."""
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        
        try:
            # Use API key from core settings if not already set in config
            if not self.config.api_key and hasattr(settings, 'GEMINI_API_KEY'):
                self.config.api_key = settings.GEMINI_API_KEY
                
            # Check if API key is set
            if not self.config.api_key:
                raise ConfigurationError("Gemini API key is not set. Please set the GEMINI_API_KEY environment variable or in your application settings.")
                
            # Setup for Generative Language API
            self.model = GeminiModel(
                self.config.model,
                api_key=self.config.api_key
            )
                
            self.agent = Agent(self.model)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize GeminiProvider: {str(e)}")
            
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using Gemini."""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
            
        try:
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_output_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k)
            }
            
            # Filter out None values
            params = {k: v for k, v in params.items() if v is not None}
            
            # Using the correct API parameters from the Agent.run method:
            # run(user_prompt, result_type, message_history, model, deps, model_settings...)
            result = await self.agent.run(
                user_prompt=prompt, 
                model_settings=params
            )
            
            # Handle AgentRunResult object
            if hasattr(result, 'data'):
                return str(result.data)
            else:
                return str(result)
            
        except Exception as e:
            self._handle_gemini_error(e)
            
    async def extract(self, prompt: str, schema: Type[BaseModel], **kwargs) -> BaseModel:
        """Extract structured data from LLM responses using Pydantic schemas."""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        
        try:
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_output_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k)
            }
            
            # Filter out None values
            params = {k: v for k, v in params.items() if v is not None}
            
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
            
            # Use the run method
            response = await self.agent.run(
                user_prompt=full_prompt,
                model_settings=params
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
            self._handle_gemini_error(e)
            
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
        """Generate a response based on chat history."""
        try:
            if not messages or not isinstance(messages, list):
                raise ValueError("Messages must be a non-empty list")
                
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_output_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k)
            }
            
            # Filter out None values
            params = {k: v for k, v in params.items() if v is not None}
            
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
            
            # Generate response
            result = await self.agent.run(
                user_prompt=conversation,
                model_settings=params
            )
            
            # Handle AgentRunResult object
            if hasattr(result, 'data'):
                return str(result.data)
            else:
                return str(result)
                
        except Exception as e:
            self._handle_gemini_error(e)
            
    async def stream(self, prompt: str, **kwargs) -> AsyncIterable[str]:
        """Stream text generation results from Gemini."""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
            
        try:
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_output_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "stream": True
            }
            
            # Filter out None values
            params = {k: v for k, v in params.items() if v is not None}
            
            # Check if the model has streaming capability
            if hasattr(self.agent, 'stream'):
                try:
                    # Use streaming capability
                    async with self.agent.stream(
                        user_prompt=prompt,
                        model_settings=params
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
                    self._handle_gemini_error(e)
            else:
                # Fallback to run method if stream is not available
                result = await self.agent.run(
                    user_prompt=prompt,
                    model_settings=params
                )
                
                # Handle AgentRunResult object
                if hasattr(result, 'data'):
                    yield str(result.data)
                else:
                    yield str(result)
        except Exception as e:
            self._handle_gemini_error(e)
            
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterable[str]:
        """Stream chat responses from Gemini."""
        try:
            if not messages or not isinstance(messages, list):
                raise ValueError("Messages must be a non-empty list")
                
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_output_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "stream": True
            }
            
            # Filter out None values
            params = {k: v for k, v in params.items() if v is not None}
            
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
            
            # Check if the model has streaming capability
            if hasattr(self.agent, 'stream'):
                try:
                    # Use streaming capability
                    async with self.agent.stream(
                        user_prompt=conversation,
                        model_settings=params
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
                    self._handle_gemini_error(e)
            else:
                # Fallback to run method if stream is not available
                result = await self.agent.run(
                    user_prompt=conversation,
                    model_settings=params
                )
                
                # Handle AgentRunResult object
                if hasattr(result, 'data'):
                    yield str(result.data)
                else:
                    yield str(result)
        except Exception as e:
            self._handle_gemini_error(e)

    def _handle_gemini_error(self, error: Exception) -> None:
        """Handle Gemini-specific errors and convert them to our exception types."""
        error_message = str(error).lower()
        
        if "authentication" in error_message or "api key" in error_message:
            raise AuthenticationError(f"Authentication failed with Gemini: {str(error)}")
        elif "rate limit" in error_message or "quota" in error_message:
            raise RateLimitError(f"Rate limit exceeded with Gemini: {str(error)}")
        elif "schema" in error_message or "validation" in error_message:
            raise SchemaValidationError(f"Schema validation error: {str(error)}")
        else:
            raise ProviderError(f"Gemini error: {str(error)}") 