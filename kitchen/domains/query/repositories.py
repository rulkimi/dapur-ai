from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository import BaseRepository, get_repository_session
from domains.query.models import Query, QueryResponse, QuerySession
import time
from fastapi import Depends
from domains.query.errors import InvalidSessionIdException
from sqlalchemy.orm import selectinload

class QueryRepository(BaseRepository):
    """Repository for query-related database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        super().__init__(Query, session)
    
    # Query operations
    async def create_query(self, 
                          prompt: str, 
                          provider: str, 
                          model: str, 
                          temperature: Optional[float] = None, 
                          max_tokens: Optional[int] = None, 
                          parameters: Optional[Dict[str, Any]] = None, 
                          session_id: Optional[str] = None,
                          user_id: Optional[int] = None) -> Query:
        """Create a new query."""
        # Ensure session_id is valid if provided
        if session_id is not None:
            try:
                # Check if the session exists
                session = await self.get_session_by_id(session_id)
                if not session:
                    # If session doesn't exist, set session_id to None
                    session_id = None
            except Exception:
                # Handle any unexpected errors by defaulting to None
                session_id = None
        
        # Ensure max_tokens is positive or None
        if max_tokens is not None and max_tokens <= 0:
            max_tokens = None
            
        query = Query(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            parameters=parameters,
            session_id=session_id,
            user_id=user_id
        )
        
        self.session.add(query)
        await self.session.flush()
        await self.session.refresh(query)
        await self.session.commit()
        return query
    
    async def get_query(self, query_id: str) -> Optional[Query]:
        """
        Get a query by its query_id.
        
        Args:
            query_id: The unique ID of the query
            
        Returns:
            The query or None if not found
        """
        # Use selectinload to eager load the responses relationship in a single query
        stmt = select(Query).where(Query.query_id == query_id).options(
            selectinload(Query.responses)
        )
        result = await self.session.execute(stmt)
        query = result.scalar_one_or_none()
        
        return query
    
    async def get_queries(self, 
                         user_id: Optional[int] = None, 
                         session_id: Optional[str] = None, 
                         limit: int = 100, 
                         offset: int = 0) -> List[Query]:
        """
        Get queries with optional filtering.
        
        Args:
            user_id: Filter by user ID
            session_id: Filter by session ID
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of queries
        """
        # Base query with eager loading of responses
        query = select(Query).options(selectinload(Query.responses))
        
        # Apply filters
        if user_id is not None:
            query = query.where(Query.user_id == user_id)
        
        if session_id is not None:
            query = query.where(Query.session_id == session_id)
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        query = query.order_by(Query.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_query(self, 
                          query_id: str, 
                          prompt: Optional[str] = None, 
                          temperature: Optional[float] = None, 
                          max_tokens: Optional[int] = None, 
                          parameters: Optional[Dict[str, Any]] = None) -> Optional[Query]:
        """Update a query."""
        update_data = {}
        
        if prompt is not None:
            update_data["prompt"] = prompt
        
        if temperature is not None:
            update_data["temperature"] = temperature
        
        if max_tokens is not None:
            # Ensure max_tokens is positive or None
            if max_tokens <= 0:
                max_tokens = None
            update_data["max_tokens"] = max_tokens
        
        if parameters is not None:
            update_data["parameters"] = parameters
        
        if not update_data:
            # Nothing to update
            return await self.get_query(query_id)
        
        stmt = update(Query).where(Query.query_id == query_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_query(query_id)
    
    async def delete_query(self, query_id: str) -> bool:
        """Delete a query by its ID."""
        stmt = delete(Query).where(Query.query_id == query_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    # Query Response operations
    async def create_query_response(self, 
                                   query_id: str, 
                                   content: str, 
                                   usage: Optional[Dict[str, int]] = None,
                                   execution_time: Optional[int] = None) -> QueryResponse:
        """Create a response for a query."""
        response = QueryResponse(
            query_id=query_id,
            content=content,
            usage=usage,
            execution_time=execution_time
        )
        
        self.session.add(response)
        await self.session.flush()
        await self.session.refresh(response)
        await self.session.commit()
        return response
    
    async def get_query_responses(self, query_id: str) -> List[QueryResponse]:
        """Get all responses for a query."""
        stmt = select(QueryResponse).where(QueryResponse.query_id == query_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    # Query Session operations
    async def create_query_session(self, 
                                  title: Optional[str] = None, 
                                  user_id: Optional[int] = None) -> QuerySession:
        """Create a new query session."""
        session = QuerySession(
            title=title,
            user_id=user_id
        )
        
        self.session.add(session)
        await self.session.flush()
        await self.session.refresh(session)
        await self.session.commit()
        return session
    
    async def get_session_by_id(self, session_id: str) -> Optional[QuerySession]:
        """Get a session by its ID."""
        stmt = select(QuerySession).where(QuerySession.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_sessions(self, 
                          user_id: Optional[int] = None, 
                          limit: int = 100, 
                          offset: int = 0) -> List[QuerySession]:
        """Get query sessions filtered by user ID."""
        stmt = select(QuerySession).order_by(QuerySession.updated_at.desc())
        
        if user_id is not None:
            stmt = stmt.where(QuerySession.user_id == user_id)
        
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_session(self, 
                            session_id: str, 
                            title: Optional[str] = None, 
                            is_active: Optional[bool] = None) -> Optional[QuerySession]:
        """Update a query session."""
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
        
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if not update_data:
            # Nothing to update
            return await self.get_session_by_id(session_id)
        
        stmt = update(QuerySession).where(QuerySession.session_id == session_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_session_by_id(session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session by its ID."""
        stmt = delete(QuerySession).where(QuerySession.session_id == session_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

async def get_query_repository(session: AsyncSession = Depends(get_repository_session)) -> QueryRepository:
    """
    Dependency to get QueryRepository instance.
    
    Args:
        session: AsyncSession instance
        
    Returns:
        QueryRepository instance
    """
    return QueryRepository(session) 