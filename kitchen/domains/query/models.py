from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, event
from sqlalchemy.orm import relationship
from db.base import Base
from uuid import uuid4

class Query(Base):
    """Model representing a user query to an LLM."""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, index=True, nullable=True)  # Optional: link to a user if authenticated
    prompt = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    temperature = Column(Integer, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    parameters = Column(JSON, nullable=True)  # Additional parameters for the LLM
    session_id = Column(String(36), ForeignKey("query_sessions.session_id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("QuerySession", back_populates="queries")
    responses = relationship("QueryResponse", back_populates="query", cascade="all, delete-orphan")

# Add direct event listeners on the Query class
@event.listens_for(Query, 'before_insert')
def receive_before_insert(mapper, connection, target):
    if hasattr(target, 'session_id') and target.session_id is not None:
        if isinstance(target.session_id, str):
            if target.session_id.lower().strip() in ('string', '', 'null', 'none', 'undefined'):
                target.session_id = None
        
@event.listens_for(Query, 'before_update')
def receive_before_update(mapper, connection, target):
    if hasattr(target, 'session_id') and target.session_id is not None:
        if isinstance(target.session_id, str):
            if target.session_id.lower().strip() in ('string', '', 'null', 'none', 'undefined'):
                target.session_id = None

class QueryResponse(Base):
    """Model representing a response from an LLM to a query."""
    __tablename__ = "query_responses"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid4()))
    query_id = Column(String(36), ForeignKey("queries.query_id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    usage = Column(JSON, nullable=True)  # Token usage information
    execution_time = Column(Integer, nullable=True)  # Execution time in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query = relationship("Query", back_populates="responses")

class QuerySession(Base):
    """Model representing a session of related queries (conversation)."""
    __tablename__ = "query_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, index=True, nullable=True)  # Optional: link to a user if authenticated
    title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    queries = relationship("Query", back_populates="session", cascade="all, delete-orphan") 