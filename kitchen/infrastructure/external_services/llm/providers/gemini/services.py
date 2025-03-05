from typing import AsyncIterable, List, Dict, Type, Any, Optional, Union
import asyncio
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.result import FinalResult, AgentStream

from ..protocols import StreamingLLMProvider
from ..exceptions import AuthenticationError, RateLimitError, InvalidResponseError, ConfigurationError
from ..adapters import ResponseAdapter
from .config import GeminiConfig

class GeminiProvider(StreamingLLMProvider):
    """Provider implementation for Google's Gemini models."""
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        
        try:
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
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                **kwargs
            }
            
            # Ensure max_tokens is positive if set
            if "max_tokens" in params and params["max_tokens"] is not None:
                if params["max_tokens"] <= 0:
                    # Remove the parameter instead of setting a default value
                    params.pop("max_tokens")
            
            # Using the correct API parameters from the Agent.run method:
            # run(user_prompt, result_type, message_history, model, deps, model_settings...)
            result = await self.agent.run(user_prompt=prompt, model_settings=params)
            
            # Handle the result properly
            if isinstance(result, FinalResult) and hasattr(result, 'data'):
                return str(result.data)
                
            # If the result is already the string, return it
            return str(result.data)
                
        except Exception as e:
            error_message = str(e).lower()
            if "authentication" in error_message or "api key" in error_message or "unauthorized" in error_message:
                raise AuthenticationError(f"Authentication failed with Gemini: {str(e)}")
            if "rate limit" in error_message or "quota" in error_message:
                raise RateLimitError(f"Rate limit exceeded with Gemini: {str(e)}")
            raise InvalidResponseError(f"Error with Gemini: {str(e)}")
            
    async def extract(self, prompt: str, schema: Type[BaseModel], **kwargs) -> BaseModel:
        """Extract structured data using Pydantic AI with Gemini."""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        
        if not schema or not issubclass(schema, BaseModel):
            raise ValueError("Schema must be a valid Pydantic model class")
            
        try:
            params = {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                **kwargs
            }
            
            # Ensure max_tokens is positive if set
            if "max_tokens" in params and params["max_tokens"] is not None:
                if params["max_tokens"] <= 0:
                    # Remove the parameter instead of setting a default value
                    params.pop("max_tokens")
            
            # Replace run_sync with the async run method and properly await it
            # The result_type parameter is for specifying the return type
            result = await self.agent.run(
                user_prompt=prompt,
                result_type=schema,
                model_settings=params
            )
            print("extract -- ",result)
            
            # Handle various result types that might come from the agent
            # Handle the case of result being a FinalResult object with data attribute
            if isinstance(result, FinalResult) and hasattr(result, 'data'):
                return result.data
            
            # Handle the case of result being an AgentRunResult with data attribute
            if hasattr(result, 'data') and result.data is not None:
                if isinstance(result.data, schema):
                    return result.data
                elif isinstance(result.data, dict):
                    return schema.model_validate(result.data)
                else:
                    # Try to serialize and deserialize the result.data if it's not matching directly
                    try:
                        result_dict = result.data
                        if hasattr(result.data, "__dict__"):
                            result_dict = result.data.__dict__
                        elif hasattr(result.data, "model_dump"):
                            result_dict = result.data.model_dump()
                        
                        return schema.model_validate(result_dict)
                    except Exception as conversion_error:
                        print(f"Error converting result.data to schema: {conversion_error}")
                        # Continue to other handling methods
            
            # If the result is directly an instance of the schema, return it
            if isinstance(result, schema):
                return result
            
            # If the result is a dictionary, try to validate it against the schema
            if isinstance(result, dict):
                return schema.model_validate(result)
            
            # Last attempt: serialize the result to a JSON-compatible format and then validate
            try:
                if hasattr(result, "model_dump"):
                    return schema.model_validate(result.model_dump())
                elif hasattr(result, "__dict__"):
                    return schema.model_validate(result.__dict__)
                else:
                    # Fallback to direct validation if all else fails
                    return schema.model_validate(result)
            except Exception as e:
                raise ValueError(f"Could not convert result to schema {schema.__name__}: {e}")
            
        except Exception as e:
            error_message = str(e).lower()
            if "authentication" in error_message or "api key" in error_message:
                raise AuthenticationError(f"Authentication failed with Gemini: {str(e)}")
            if "rate limit" in error_message or "quota" in error_message:
                raise RateLimitError(f"Rate limit exceeded with Gemini: {str(e)}")
            if "schema" in error_message or "validation" in error_message:
                from ..exceptions import SchemaValidationError
                raise SchemaValidationError(f"Failed to extract schema from Gemini response: {str(e)}")
            raise InvalidResponseError(f"Failed to extract schema from Gemini response: {str(e)}")
            
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat response using Gemini."""
        if not messages or not isinstance(messages, list) or len(messages) == 0:
            raise ValueError("Messages must be a non-empty list")
            
        try:
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                **kwargs
            }
            
            # Ensure max_tokens is positive if set
            if "max_tokens" in params and params["max_tokens"] is not None:
                if params["max_tokens"] <= 0:
                    # Remove the parameter instead of setting a default value
                    params.pop("max_tokens")
            
            # With pydantic_ai.Agent, we need to take a different approach for chat
            # Create a prompt that summarizes the conversation and the last question
            conversation_summary = ""
            user_question = ""
            
            for msg in messages:
                if "role" not in msg or "content" not in msg:
                    raise ValueError("Each message must have 'role' and 'content' keys")
                    
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    # Store the latest user question
                    user_question = content
                    # Also add to conversation summary
                    conversation_summary += f"User: {content}\n"
                elif role == "model" or role == "assistant":
                    conversation_summary += f"Assistant: {content}\n"
                elif role == "system":
                    conversation_summary += f"System: {content}\n"
                    
            # If there's no user question, use the last message content
            if not user_question:
                user_question = messages[-1]["content"]
                
            # Build a prompt that includes conversation history and the question
            prompt = f"Previous conversation:\n{conversation_summary}\n\nUser's question: {user_question}\n\nPlease respond to the user's last question."
            
            # Now use the regular generate method
            result = await self.agent.run(
                user_prompt=prompt,
                model_settings=params
            )
            
            # Handle the result
            if isinstance(result, FinalResult) and hasattr(result, 'data'):
                return str(result.data)
            return str(result)
            
        except ValueError as e:
            # Re-raise ValueError as-is to preserve the specific validation message
            raise e 
        except Exception as e:
            # Handle chat errors
            error_message = str(e).lower()
            if "authentication" in error_message or "api key" in error_message:
                raise AuthenticationError(f"Authentication failed with Gemini: {str(e)}")
            if "rate limit" in error_message or "quota" in error_message:
                raise RateLimitError(f"Rate limit exceeded with Gemini: {str(e)}")
            raise InvalidResponseError(f"Error in Gemini chat: {str(e)}")
            
    async def stream(self, prompt: str, **kwargs) -> AsyncIterable[str]:
        """Stream a response from Gemini."""
        try:
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                **kwargs
            }
            
            # Ensure max_tokens is positive if set
            if "max_tokens" in params and params["max_tokens"] is not None:
                if params["max_tokens"] <= 0:
                    # Remove the parameter instead of setting a default value
                    params.pop("max_tokens")
            
            # For streaming with pydantic_ai, we use run_stream which returns a context manager
            stream_ctx = self.agent.run_stream(
                user_prompt=prompt,
                model_settings=params
            )
            
            async with stream_ctx as stream:
                async for chunk in stream:
                    if hasattr(chunk, 'text'):
                        yield chunk.text
                    elif hasattr(chunk, 'data'):
                        yield str(chunk.data)
                    else:
                        yield str(chunk)
                
        except ValueError as e:
            # Re-raise ValueError as-is to preserve the specific validation message
            raise e 
        except Exception as e:
            # Handle streaming errors
            error_message = str(e).lower()
            if "authentication" in error_message or "api key" in error_message:
                raise AuthenticationError(f"Authentication failed with Gemini: {str(e)}")
            if "rate limit" in error_message or "quota" in error_message:
                raise RateLimitError(f"Rate limit exceeded with Gemini: {str(e)}")
            raise InvalidResponseError(f"Error in Gemini streaming: {str(e)}")
            
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterable[str]:
        """Stream a chat response from Gemini."""
        if not messages or not isinstance(messages, list) or len(messages) == 0:
            raise ValueError("Messages must be a non-empty list")
            
        try:
            # Merge config with kwargs, with kwargs taking precedence
            params = {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                **kwargs
            }
            
            # Ensure max_tokens is positive if set
            if "max_tokens" in params and params["max_tokens"] is not None:
                if params["max_tokens"] <= 0:
                    # Remove the parameter instead of setting a default value
                    params.pop("max_tokens")
            
            # With pydantic_ai.Agent, we need to take a different approach for chat streaming
            # Create a prompt that summarizes the conversation and the last question
            conversation_summary = ""
            user_question = ""
            
            for msg in messages:
                if "role" not in msg or "content" not in msg:
                    raise ValueError("Each message must have 'role' and 'content' keys")
                    
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    # Store the latest user question
                    user_question = content
                    # Also add to conversation summary
                    conversation_summary += f"User: {content}\n"
                elif role == "model" or role == "assistant":
                    conversation_summary += f"Assistant: {content}\n"
                elif role == "system":
                    conversation_summary += f"System: {content}\n"
                    
            # If there's no user question, use the last message content
            if not user_question:
                user_question = messages[-1]["content"]
                
            # Build a prompt that includes conversation history and the question
            prompt = f"Previous conversation:\n{conversation_summary}\n\nUser's question: {user_question}\n\nPlease respond to the user's last question."
            
            # Now use the regular stream method
            stream_ctx = self.agent.run_stream(
                user_prompt=prompt,
                model_settings=params
            )
            
            async with stream_ctx as stream:
                async for chunk in stream:
                    if hasattr(chunk, 'text'):
                        yield chunk.text
                    elif hasattr(chunk, 'data'):
                        yield str(chunk.data)
                    else:
                        yield str(chunk)
            
        except ValueError as e:
            # Re-raise ValueError as-is to preserve the specific validation message
            raise e 
        except Exception as e:
            # Handle streaming chat errors
            error_message = str(e).lower()
            if "authentication" in error_message or "api key" in error_message:
                raise AuthenticationError(f"Authentication failed with Gemini: {str(e)}")
            if "rate limit" in error_message or "quota" in error_message:
                raise RateLimitError(f"Rate limit exceeded with Gemini: {str(e)}")
            raise InvalidResponseError(f"Error in Gemini chat streaming: {str(e)}") 