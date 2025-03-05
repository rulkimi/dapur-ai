from typing import List, Optional, Dict, Any, Type
from fastapi import Depends
import time
from pydantic import BaseModel
from infrastructure.external_services.llm.providers.factory import ProviderFactory
from infrastructure.external_services.llm.providers.models import ProviderType, ModelType, Message
from infrastructure.external_services.llm.providers.exceptions import ProviderError

from domains.query.repositories import QueryRepository, get_query_repository
from domains.query.models import Query, QueryResponse, QuerySession
from domains.query.schemas import (
    QueryCreate, 
    QueryUpdate, 
    QueryOut, 
    QuerySessionCreate, 
    QuerySessionUpdate,
    ChatCreate
)
from domains.query.errors import (
    QueryErrorCode, 
    raise_query_error, 
    raise_service_error, 
    InvalidSessionIdException,
    QueryValidationException,
    QueryServiceException,
    QueryNotFoundException,
    raise_validation_error
)

class QueryService:
    """Service for handling queries to LLM providers."""
    
    def __init__(self, repository: QueryRepository):
        """
        Initialize QueryService with repository.
        
        Args:
            repository: QueryRepository for data access
        """
        self.repository = repository
    
    async def create_query(self, query_data: QueryCreate, user_id: Optional[int] = None) -> QueryOut:
        """
        Create a new query and get a response from the LLM provider.
        
        Args:
            query_data: The query data
            user_id: Optional user ID
            
        Returns:
            Query with response from LLM
            
        Raises:
            QueryValidationException: If the query data is invalid
            QueryServiceException: If there's an error with the LLM provider
        """
        try:
            # Validate input data
            if not query_data.prompt or query_data.prompt.strip() == "":
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Prompt cannot be empty",
                    {"prompt": query_data.prompt}
                )
                
            # Validate session_id if provided
            session_id = await self._validate_session_id(query_data.session_id)
            
            # Validate model support for the selected provider
            try:
                provider_type = ProviderType(query_data.provider.value)
                # Get the provider instance
                provider = ProviderFactory.get_provider(provider_type)
            except ValueError:
                raise_validation_error(
                    QueryErrorCode.PROVIDER_NOT_SUPPORTED,
                    f"Provider '{query_data.provider.value}' is not supported",
                    {"provider": query_data.provider.value}
                )
            
            # Create query record
            try:
                query = await self.repository.create_query(
                    prompt=query_data.prompt,
                    provider=query_data.provider.value,
                    model=query_data.model.value,
                    temperature=query_data.temperature,
                    max_tokens=query_data.max_tokens,
                    parameters=query_data.parameters,
                    session_id=session_id,
                    user_id=user_id
                )
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    f"Error creating query record: {str(e)}",
                    {"error": str(e)}
                )
            
            # Measure execution time
            start_time = time.time()
            
            # Generate response
            try:
                # Ensure max_tokens is positive or None
                max_tokens = query_data.max_tokens
                if max_tokens is not None and max_tokens <= 0:
                    max_tokens = None
                
                response_content = await provider.generate(
                    query_data.prompt,
                    model=query_data.model.value,
                    temperature=query_data.temperature,
                    max_tokens=max_tokens,
                    **query_data.parameters
                )
            except ProviderError as e:
                # Update query to mark as failed
                await self.repository.update_query(
                    query_id=query.query_id,
                    parameters={**query_data.parameters, "error": str(e)}
                )
                raise_service_error(
                    QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                    f"Error from LLM provider: {str(e)}",
                    {"provider": query_data.provider.value, "error": str(e)}
                )
            
            # Calculate execution time in milliseconds
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create response record
            try:
                response = await self.repository.create_query_response(
                    query_id=query.query_id,
                    content=response_content,
                    execution_time=execution_time
                )
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                    f"Error creating response record: {str(e)}",
                    {"error": str(e)}
                )
            
            # Fetch the query again with responses loaded to avoid lazy loading issues
            query = await self.repository.get_query(query.query_id)
            
            return query
            
        except (QueryValidationException, QueryServiceException):
            # Re-raise known exceptions to be caught by the router
            raise
        except ProviderError as e:
            raise_service_error(
                QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                f"Error from LLM provider: {str(e)}",
                {"provider": query_data.provider.value, "error": str(e)}
            )
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                f"Unexpected error: {str(e)}",
                {"error": str(e)}
            )
    
    async def extract_structured_data(self, 
                                    query_data: QueryCreate, 
                                    schema: Type[BaseModel],
                                    user_id: Optional[int] = None) -> BaseModel:
        """
        Extract structured data from an LLM provider using a Pydantic schema.
        
        Args:
            query_data: The query data
            schema: Pydantic model to extract
            user_id: Optional user ID
            
        Returns:
            Structured data as a Pydantic model
            
        Raises:
            QueryValidationException: If the query data is invalid
            QueryServiceException: If there's an error with the LLM provider or extraction process
            InvalidSessionIdException: If the provided session ID is invalid
        """
        try:
            # Validate input data
            if not query_data.prompt or query_data.prompt.strip() == "":
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Prompt cannot be empty",
                    {"prompt": query_data.prompt}
                )
                
            # Validate schema is a valid Pydantic model
            if not issubclass(schema, BaseModel):
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Schema must be a valid Pydantic model",
                    {"schema": str(schema)}
                )
                
            # Validate session_id if provided
            if query_data.session_id:
                await self._validate_session_id(query_data.session_id)
            
            # Validate model support for the selected provider
            try:
                provider_type = ProviderType(query_data.provider.value)
                provider = ProviderFactory.get_provider(provider_type)
            except ValueError:
                raise_validation_error(
                    QueryErrorCode.PROVIDER_NOT_SUPPORTED,
                    f"Provider '{query_data.provider.value}' is not supported",
                    {"provider": query_data.provider.value}
                )
            
            # Create query record
            try:
                query = await self.repository.create_query(
                    prompt=query_data.prompt,
                    provider=query_data.provider.value,
                    model=query_data.model.value,
                    temperature=query_data.temperature,
                    max_tokens=query_data.max_tokens,
                    parameters=query_data.parameters,
                    session_id=query_data.session_id,
                    user_id=user_id
                )
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    f"Error creating query record: {str(e)}",
                    {"error": str(e)}
                )
            
            # Measure execution time
            start_time = time.time()
            
            # Extract structured data
            try:
                # Ensure max_tokens is positive or None
                max_tokens = query_data.max_tokens
                if max_tokens is not None and max_tokens <= 0:
                    max_tokens = None
                
                result = await provider.extract(
                    query_data.prompt,
                    schema=schema,
                    model=query_data.model.value,
                    temperature=query_data.temperature,
                    max_tokens=max_tokens,
                    **query_data.parameters
                )
            except ProviderError as e:
                # Update query to mark as failed
                await self.repository.update_query(
                    query_id=query.query_id,
                    parameters={**query_data.parameters, "error": str(e)}
                )
                raise_service_error(
                    QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                    f"Error from LLM provider: {str(e)}",
                    {"provider": query_data.provider.value, "error": str(e)}
                )
            except Exception as e:
                # Update query to mark as failed
                await self.repository.update_query(
                    query_id=query.query_id,
                    parameters={**query_data.parameters, "error": str(e)}
                )
                raise_service_error(
                    QueryErrorCode.SERVICE_EXTRACTION_ERROR,
                    f"Error extracting structured data: {str(e)}",
                    {"error": str(e)}
                )
            
            # Calculate execution time in milliseconds
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create response record with the serialized result
            try:
                response = await self.repository.create_query_response(
                    query_id=query.query_id,
                    content=result.model_dump_json(),
                    execution_time=execution_time
                )
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SERVICE_EXTRACTION_ERROR,
                    f"Error creating response record: {str(e)}",
                    {"error": str(e)}
                )
            
            return result
            
        except InvalidSessionIdException:
            # Re-raise InvalidSessionIdException to be caught by the router
            raise
        except (QueryValidationException, QueryServiceException):
            # Re-raise known exceptions to be caught by the router
            raise
        except ProviderError as e:
            raise_service_error(
                QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                f"Error from LLM provider: {str(e)}",
                {"provider": query_data.provider.value, "error": str(e)}
            )
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SERVICE_EXTRACTION_ERROR,
                f"Unexpected error during extraction: {str(e)}",
                {"error": str(e)}
            )
    
    async def chat(self, chat_data: ChatCreate, user_id: Optional[int] = None) -> QueryOut:
        """
        Create a chat query and get a response from the LLM provider.
        
        Args:
            chat_data: The chat data with messages
            user_id: Optional user ID
            
        Returns:
            Query with response from LLM
            
        Raises:
            QueryValidationException: If the chat data is invalid
            QueryServiceException: If there's an error with the LLM provider
            InvalidSessionIdException: If the provided session ID is invalid
        """
        try:
            # Validate input data
            if not chat_data.messages or len(chat_data.messages) == 0:
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Chat messages cannot be empty",
                    {"messages": []}
                )
            
            # Validate session_id if provided
            if chat_data.session_id:
                await self._validate_session_id(chat_data.session_id)
                
            # Validate model support for the selected provider
            try:
                provider_type = ProviderType(chat_data.provider.value)
                provider = ProviderFactory.get_provider(provider_type)
            except ValueError:
                raise_validation_error(
                    QueryErrorCode.PROVIDER_NOT_SUPPORTED,
                    f"Provider '{chat_data.provider.value}' is not supported",
                    {"provider": chat_data.provider.value}
                )
            
            # Convert messages to the format expected by the provider
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in chat_data.messages
            ]
            
            # Create a combined prompt for logging purposes
            combined_prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in chat_data.messages])
            
            # Create query record
            try:
                query = await self.repository.create_query(
                    prompt=combined_prompt,
                    provider=chat_data.provider.value,
                    model=chat_data.model.value,
                    temperature=chat_data.temperature,
                    max_tokens=chat_data.max_tokens,
                    parameters=chat_data.parameters,
                    session_id=chat_data.session_id,
                    user_id=user_id
                )
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    f"Error creating chat query record: {str(e)}",
                    {"error": str(e)}
                )
            
            # Measure execution time
            start_time = time.time()
            
            # Generate chat response
            try:
                # Ensure max_tokens is positive or None
                max_tokens = chat_data.max_tokens
                if max_tokens is not None and max_tokens <= 0:
                    max_tokens = None
                
                response_content = await provider.chat(
                    messages=messages,
                    model=chat_data.model.value,
                    temperature=chat_data.temperature,
                    max_tokens=max_tokens,
                    **chat_data.parameters
                )
            except ProviderError as e:
                # Update query to mark as failed
                await self.repository.update_query(
                    query_id=query.query_id,
                    parameters={**chat_data.parameters, "error": str(e)}
                )
                raise_service_error(
                    QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                    f"Error from chat LLM provider: {str(e)}",
                    {"provider": chat_data.provider.value, "error": str(e)}
                )
            
            # Calculate execution time in milliseconds
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create response record
            try:
                response = await self.repository.create_query_response(
                    query_id=query.query_id,
                    content=response_content,
                    execution_time=execution_time
                )
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                    f"Error creating chat response record: {str(e)}",
                    {"error": str(e)}
                )
            
            return query
            
        except InvalidSessionIdException:
            # Re-raise InvalidSessionIdException to be caught by the router
            raise
        except (QueryValidationException, QueryServiceException):
            # Re-raise known exceptions to be caught by the router
            raise
        except ProviderError as e:
            raise_service_error(
                QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                f"Error from chat LLM provider: {str(e)}",
                {"provider": chat_data.provider.value, "error": str(e)}
            )
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                f"Unexpected error during chat: {str(e)}",
                {"error": str(e)}
            )
    
    async def get_query(self, query_id: str) -> Optional[Query]:
        """
        Get a query by its ID.
        
        Args:
            query_id: The unique identifier of the query
            
        Returns:
            The query or None if not found
            
        Raises:
            QueryNotFoundException: If the query is not found
        """
        try:
            # Use repository to get query
            query = await self.repository.get_query(query_id)
            
            if not query:
                raise_query_error(
                    QueryErrorCode.QUERY_NOT_FOUND,
                    f"Query with ID '{query_id}' not found",
                    {"query_id": query_id}
                )
                
            return query
        except QueryNotFoundException:
            # Re-raise query not found exceptions
            raise
        except Exception as e:
            # Log and wrap other exceptions
            raise_service_error(
                QueryErrorCode.QUERY_SERVICE_ERROR,
                f"Error retrieving query: {str(e)}",
                {"error": str(e)}
            )
    
    async def get_queries(self, 
                        user_id: Optional[int] = None, 
                        session_id: Optional[str] = None, 
                        limit: int = 100, 
                        offset: int = 0) -> List[Query]:
        """
        Get queries filtered by user ID and/or session ID.
        
        Args:
            user_id: Optional user ID filter
            session_id: Optional session ID filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of queries matching the criteria
            
        Raises:
            QueryValidationException: If filter parameters are invalid
            InvalidSessionIdException: If the provided session ID is invalid
        """
        try:
            # Validate limit and offset
            if limit < 1:
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Limit must be at least 1",
                    {"limit": limit}
                )
            
            if offset < 0:
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Offset cannot be negative",
                    {"offset": offset}
                )
                
            # Validate session_id if provided
            if session_id:
                valid_session_id = await self._validate_session_id(session_id)
                session_id = valid_session_id
                
            # Get the queries
            try:
                queries = await self.repository.get_queries(user_id, session_id, limit, offset)
                return queries
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                    f"Error retrieving queries: {str(e)}",
                    {"error": str(e)}
                )
                
        except (QueryValidationException, InvalidSessionIdException):
            # Re-raise known exceptions to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SERVICE_LLM_PROVIDER_ERROR,
                f"Unexpected error retrieving queries: {str(e)}",
                {"error": str(e)}
            )
    
    async def update_query(self, query_id: str, query_data: QueryUpdate) -> Query:
        """
        Update a query.
        
        Args:
            query_id: The ID of the query to update
            query_data: The updated query data
            
        Returns:
            The updated query
            
        Raises:
            QueryNotFoundException: If the query with the specified ID is not found
            QueryValidationException: If the updated data is invalid
        """
        try:
            # First verify the query exists
            query = await self.get_query(query_id)
            
            # Validate temperature if provided
            if query_data.temperature is not None and (query_data.temperature < 0 or query_data.temperature > 1):
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Temperature must be between 0 and 1",
                    {"temperature": query_data.temperature}
                )
            
            # Validate prompt if provided
            if query_data.prompt is not None and query_data.prompt.strip() == "":
                raise_validation_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    "Prompt cannot be empty",
                    {"prompt": query_data.prompt}
                )
                
            # Validate max_tokens if provided
            if query_data.max_tokens is not None and query_data.max_tokens <= 0:
                query_data.max_tokens = None
                
            # Update the query
            try:
                updated_query = await self.repository.update_query(
                    query_id=query_id,
                    prompt=query_data.prompt,
                    temperature=query_data.temperature,
                    max_tokens=query_data.max_tokens,
                    parameters=query_data.parameters
                )
                
                if not updated_query:
                    raise_query_error(
                        QueryErrorCode.QUERY_NOT_FOUND,
                        f"Failed to update query with ID {query_id}",
                        {"query_id": query_id}
                    )
                    
                return updated_query
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    f"Error updating query: {str(e)}",
                    {"query_id": query_id, "error": str(e)}
                )
                
        except (QueryNotFoundException, QueryValidationException):
            # Re-raise known exceptions to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.QUERY_VALIDATION_ERROR,
                f"Unexpected error updating query: {str(e)}",
                {"query_id": query_id, "error": str(e)}
            )
    
    async def delete_query(self, query_id: str) -> bool:
        """
        Delete a query by its ID.
        
        Args:
            query_id: The ID of the query to delete
            
        Returns:
            True if the query was deleted, False otherwise
            
        Raises:
            QueryNotFoundException: If the query with the specified ID is not found
        """
        try:
            # First verify the query exists
            query = await self.get_query(query_id)
            
            # Delete the query
            try:
                result = await self.repository.delete_query(query_id)
                if not result:
                    raise_query_error(
                        QueryErrorCode.QUERY_NOT_FOUND,
                        f"Failed to delete query with ID {query_id}",
                        {"query_id": query_id}
                    )
                return result
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.QUERY_VALIDATION_ERROR,
                    f"Error deleting query: {str(e)}",
                    {"query_id": query_id, "error": str(e)}
                )
                
        except QueryNotFoundException:
            # Re-raise QueryNotFoundException to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.QUERY_VALIDATION_ERROR,
                f"Unexpected error deleting query: {str(e)}",
                {"query_id": query_id, "error": str(e)}
            )
    
    # Query Session methods
    async def create_session(self, session_data: QuerySessionCreate, user_id: Optional[int] = None) -> QuerySession:
        """
        Create a new query session.
        
        Args:
            session_data: The session data
            user_id: Optional user ID
            
        Returns:
            The newly created session
            
        Raises:
            QueryValidationException: If the session data is invalid
        """
        try:
            # Normalize empty titles to None
            title = session_data.title
            if title is not None and title.strip() == "":
                title = None
                
            # Create the session
            try:
                session = await self.repository.create_query_session(
                    title=title,
                    user_id=user_id
                )
                return session
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SESSION_VALIDATION_ERROR,
                    f"Error creating session: {str(e)}",
                    {"error": str(e)}
                )
                
        except QueryValidationException:
            # Re-raise QueryValidationException to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SESSION_VALIDATION_ERROR,
                f"Unexpected error creating session: {str(e)}",
                {"error": str(e)}
            )
    
    async def get_session(self, session_id: str) -> Optional[QuerySession]:
        """
        Get a session by its ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session object if found
            
        Raises:
            QueryNotFoundException: If the session with the specified ID is not found
        """
        if not session_id:
            raise_validation_error(
                QueryErrorCode.SESSION_VALIDATION_ERROR,
                "Session ID cannot be empty",
                {"session_id": session_id}
            )
            
        session = await self.repository.get_session_by_id(session_id)
        if not session:
            raise_query_error(
                QueryErrorCode.SESSION_NOT_FOUND,
                f"Session with ID {session_id} not found",
                {"session_id": session_id}
            )
        return session
    
    async def get_sessions(self, 
                         user_id: Optional[int] = None, 
                         limit: int = 100, 
                         offset: int = 0) -> List[QuerySession]:
        """
        Get query sessions filtered by user ID.
        
        Args:
            user_id: Optional user ID filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of sessions matching the criteria
            
        Raises:
            QueryValidationException: If filter parameters are invalid
        """
        try:
            # Validate limit and offset
            if limit < 1:
                raise_validation_error(
                    QueryErrorCode.SESSION_VALIDATION_ERROR,
                    "Limit must be at least 1",
                    {"limit": limit}
                )
            
            if offset < 0:
                raise_validation_error(
                    QueryErrorCode.SESSION_VALIDATION_ERROR,
                    "Offset cannot be negative",
                    {"offset": offset}
                )
                
            # Get the sessions
            try:
                sessions = await self.repository.get_sessions(user_id, limit, offset)
                return sessions
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SESSION_VALIDATION_ERROR,
                    f"Error retrieving sessions: {str(e)}",
                    {"error": str(e)}
                )
                
        except QueryValidationException:
            # Re-raise known exceptions to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SESSION_VALIDATION_ERROR,
                f"Unexpected error retrieving sessions: {str(e)}",
                {"error": str(e)}
            )
    
    async def update_session(self, session_id: str, session_data: QuerySessionUpdate) -> QuerySession:
        """
        Update a query session.
        
        Args:
            session_id: The ID of the session to update
            session_data: The updated session data
            
        Returns:
            The updated session
            
        Raises:
            QueryNotFoundException: If the session with the specified ID is not found
            QueryValidationException: If the updated data is invalid
        """
        try:
            # First verify the session exists
            session = await self.get_session(session_id)
            
            # Validate title if provided
            if session_data.title is not None and session_data.title.strip() == "":
                # Convert empty titles to None
                session_data.title = None
                
            # Update the session
            try:
                updated_session = await self.repository.update_session(
                    session_id=session_id,
                    title=session_data.title,
                    is_active=session_data.is_active
                )
                
                if not updated_session:
                    raise_query_error(
                        QueryErrorCode.SESSION_NOT_FOUND,
                        f"Failed to update session with ID {session_id}",
                        {"session_id": session_id}
                    )
                    
                return updated_session
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SESSION_VALIDATION_ERROR,
                    f"Error updating session: {str(e)}",
                    {"session_id": session_id, "error": str(e)}
                )
                
        except (QueryNotFoundException, QueryValidationException):
            # Re-raise known exceptions to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SESSION_VALIDATION_ERROR,
                f"Unexpected error updating session: {str(e)}",
                {"session_id": session_id, "error": str(e)}
            )
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by its ID.
        
        Args:
            session_id: The ID of the session to delete
            
        Returns:
            True if the session was deleted, False otherwise
            
        Raises:
            QueryNotFoundException: If the session with the specified ID is not found
        """
        try:
            # First verify the session exists
            session = await self.get_session(session_id)
            
            # Delete the session
            try:
                result = await self.repository.delete_session(session_id)
                if not result:
                    raise_query_error(
                        QueryErrorCode.SESSION_NOT_FOUND,
                        f"Failed to delete session with ID {session_id}",
                        {"session_id": session_id}
                    )
                return result
            except Exception as e:
                raise_service_error(
                    QueryErrorCode.SESSION_VALIDATION_ERROR,
                    f"Error deleting session: {str(e)}",
                    {"session_id": session_id, "error": str(e)}
                )
                
        except QueryNotFoundException:
            # Re-raise QueryNotFoundException to be caught by the router
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            raise_service_error(
                QueryErrorCode.SESSION_VALIDATION_ERROR,
                f"Unexpected error deleting session: {str(e)}",
                {"session_id": session_id, "error": str(e)}
            )

    async def _validate_session_id(self, session_id: Optional[str]) -> Optional[str]:
        """
        Validate a session ID. Returns None for invalid IDs or empty/null values,
        and verifies existence in the database.
        
        Args:
            session_id: The session ID to validate, or None
            
        Returns:
            The validated session ID or None
        """
        if session_id is None:
            return None
        
        # Check for invalid placeholder values
        if isinstance(session_id, str):
            session_id_lower = session_id.lower().strip()
            if session_id_lower in ("string", "", "null", "none", "undefined"):
                return None
        
        # Verify the session exists in the database
        try:
            session = await self.repository.get_session_by_id(session_id)
            if not session:
                # Return None for non-existent session IDs
                return None
            return session_id
        except Exception:
            # Return None for any database errors
            return None

def get_query_service(repository: QueryRepository = Depends(get_query_repository)) -> QueryService:
    """
    Dependency to get QueryService instance.
    
    Args:
        repository: QueryRepository instance
    
    Returns:
        QueryService instance
    """
    return QueryService(repository) 