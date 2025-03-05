from typing import Annotated, List, Optional, Type
from fastapi import Depends, Query, HTTPException, Request, Response
from pydantic import BaseModel
from core.dependencies import controllable_endpoint, ControllableAPIRouter

from domains.query.schemas import (
    QueryCreate, 
    QueryUpdate, 
    QueryOut, 
    QueryResponse,
    QuerySessionCreate, 
    QuerySessionUpdate, 
    QuerySessionOut,
    QuerySessionWithQueries,
    ChatCreate
)
from domains.query.services import QueryService, get_query_service
from domains.query.errors import InvalidSessionIdException
from core.security import get_optional_current_active_user  # Use for optional authentication
from domains.auth.models import Auth, Anonymous

router = ControllableAPIRouter(prefix="/queries", tags=["queries"])


# Session endpoints
@router.post("/sessions", response_model=QuerySessionOut)
@controllable_endpoint(
    enabled=True,
    description="Create a new query session"
)
async def create_session(
    session_data: QuerySessionCreate,
    request: Request,
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QuerySessionOut:
    """
    Create a new query session.
    
    A query session groups related queries together and maintains conversation state for chat-based LLM interactions.
    
    - **name**: Optional name for the session
    """
    return await service.create_session(session_data)

@router.get("/sessions/{session_id}", response_model=QuerySessionWithQueries)
@controllable_endpoint(
    enabled=True,
    description="Get a query session by ID"
)
async def get_session(
    session_id: str,
    request: Request,
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QuerySessionWithQueries:
    """
    Get a query session by ID with all associated queries.
    
    - **session_id**: The unique identifier of the session
    """
    try:
        return await service.get_session_with_queries(session_id)
    except InvalidSessionIdException:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

@router.get("/sessions", response_model=List[QuerySessionOut])
@controllable_endpoint(
    enabled=True,
    description="Get a list of query sessions"
)
async def get_sessions(
    request: Request,
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[QuerySessionOut]:
    """
    Get a list of query sessions.
    
    - **limit**: Maximum number of sessions to return
    - **offset**: Number of sessions to skip
    """
    return await service.get_sessions(limit=limit, offset=offset)

@router.patch("/sessions/{session_id}", response_model=QuerySessionOut)
@controllable_endpoint(
    enabled=True,
    description="Update a query session"
)
async def update_session(
    session_id: str,
    session_data: QuerySessionUpdate,
    request: Request,
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QuerySessionOut:
    """
    Update a query session.
    
    - **session_id**: The unique identifier of the session
    - **session_data**: The session data to update
    """
    return await service.update_session(session_id, session_data)

@router.delete("/sessions/{session_id}")
@controllable_endpoint(
    enabled=True,
    description="Delete a query session"
)
async def delete_session(
    session_id: str,
    request: Request,
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> dict:
    """
    Delete a query session.
    
    - **session_id**: The unique identifier of the session
    """
    result = await service.delete_session(session_id)
    return {"success": result} 

# Query endpoints
@router.post("/", response_model=QueryOut)
@controllable_endpoint(
    enabled=True,
    description="Create a new query (admin only)"
)
async def create_query(
    query_data: QueryCreate,
    request: Request,
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QueryOut:
    """
    Create a new query to an LLM provider.
    
    This endpoint sends a prompt to the specified LLM provider and returns the query with response.
    
    - **prompt**: The text prompt to send to the LLM
    - **provider**: The LLM provider to use (e.g., "gemini", "openai")
    - **model**: The specific model to use (e.g., "gemini-1.5-pro")
    - **temperature**: Controls randomness (0-1)
    """
    return await service.create_query(query_data)

@router.post("/chat", response_model=QueryOut)
@controllable_endpoint( # Add HTTP method to make path unique
    enabled=False,
    description="Create a new chat query with message history (admin only)"
)
async def create_chat_query(
    chat_data: ChatCreate,
    request: Request,  # Add explicit request parameter
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QueryOut:
    """
    Create a new chat query with message history.
    
    This endpoint sends a conversation history to the specified LLM provider 
    and returns the query with response.
    """
    try:
        user_id = getattr(current_auth, "id", None)
        return await service.chat(chat_data, user_id)
    except InvalidSessionIdException:
        # Convert the session_id to None and retry the operation
        chat_data.session_id = None
        user_id = getattr(current_auth, "id", None)
        return await service.chat(chat_data, user_id)

@router.post("/extract")
@controllable_endpoint(
    enabled=False,
    description="Extract structured data from an LLM provider using a Pydantic schema (admin only)"
)
async def extract_structured_data(
    query_data: QueryCreate,
    schema_class: str,  # Fully qualified name of the Pydantic model class
    request: Request,  # Add explicit request parameter
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None,
):
    """
    Extract structured data from an LLM provider using a Pydantic schema.
    
    This endpoint submits a query to the LLM provider and asks it to extract 
    structured data according to the specified Pydantic schema.
    """
    # Try to import the schema class
    try:
        module_path, class_name = schema_class.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        schema = getattr(module, class_name)
    except (ImportError, AttributeError):
        raise HTTPException(status_code=400, detail=f"Schema class {schema_class} not found")
    
    # Validate that it's a Pydantic model
    if not issubclass(schema, BaseModel):
        raise HTTPException(status_code=400, detail=f"Schema class {schema_class} is not a valid Pydantic model")
    
    # Process the extraction request
    try:
        user_id = getattr(current_auth, "id", None)
        result = await service.extract_structured_data(query_data, schema, user_id)
        
        # Return the structured data directly
        if isinstance(result, BaseModel):
            return result
        else:
            # If not a Pydantic model, convert to dict for JSON
            return result
    except InvalidSessionIdException:
        # Convert the session_id to None and retry the operation
        query_data.session_id = None
        user_id = getattr(current_auth, "id", None)
        return await service.extract_structured_data(query_data, schema, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{query_id}", response_model=QueryOut)
@controllable_endpoint(
    enabled=False,
    description="Get a query by its ID (admin only)"
)
async def get_query(
    query_id: str,
    request: Request,  # Add explicit request parameter
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QueryOut:
    """
    Get a query by its ID.
    
    - **query_id**: The unique identifier of the query
    """
    return await service.get_query(query_id)

@router.get("/", response_model=List[QueryOut])
@controllable_endpoint(
    enabled=False,
    description="Get a list of queries (admin only)"
)
async def get_queries(
    request: Request,  # Add explicit request parameter
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None,
    session_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[QueryOut]:
    """
    Get a list of queries.
    
    - **session_id**: Optional session ID to filter queries
    - **limit**: Maximum number of queries to return (1-1000)
    - **offset**: Number of queries to skip
    """
    user_id = current_auth.id if current_auth else None
    return await service.get_queries(user_id, session_id, limit, offset)

@router.patch("/{query_id}", response_model=QueryOut)
@controllable_endpoint(
    enabled=False,
    description="Update a query (admin only)"
)
async def update_query(
    query_id: str,
    query_data: QueryUpdate,
    request: Request,  # Add explicit request parameter
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> QueryOut:
    """
    Update a query.
    
    - **query_id**: The unique identifier of the query
    - **query_data**: The data to update
    """
    return await service.update_query(query_id, query_data)

@router.delete("/{query_id}")
@controllable_endpoint(
    enabled=False,
    description="Delete a query (admin only)"
)
async def delete_query(
    query_id: str,
    request: Request,  # Add explicit request parameter
    service: Annotated[QueryService, Depends(get_query_service)],
    current_auth: Annotated[Optional[Auth], Depends(get_optional_current_active_user)] = None
) -> dict:
    """
    Delete a query.
    
    - **query_id**: The unique identifier of the query
    """
    result = await service.delete_query(query_id)
    return {"success": result}