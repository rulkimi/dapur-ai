from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
from infrastructure.external_services.llm.providers.models import ProviderType, ModelType

class QueryCreate(BaseModel):
    """Schema for creating a new query."""
    prompt: str
    provider: ProviderType
    model: ModelType
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Temperature must be between 0 and 1')
        return v
        
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if v is not None and v <= 0:
            return None  # Return None instead of an invalid value
        return v
        
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Normalize the string and check for invalid values
            v_lower = v.lower().strip()
            if v_lower in ('', 'string', 'null', 'none', 'undefined'):
                return None
        return v

class QueryUpdate(BaseModel):
    """Schema for updating an existing query."""
    prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Temperature must be between 0 and 1')
        return v

class QueryResponse(BaseModel):
    """Schema for a query response."""
    response_id: str
    content: str
    usage: Optional[Dict[str, int]] = None
    execution_time: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class QueryOut(BaseModel):
    """Schema for query output."""
    query_id: str
    prompt: str
    provider: str
    model: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    responses: List[QueryResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class QuerySessionCreate(BaseModel):
    """Schema for creating a new query session."""
    title: Optional[str] = None

class QuerySessionUpdate(BaseModel):
    """Schema for updating a query session."""
    title: Optional[str] = None
    is_active: Optional[bool] = None

class QuerySessionOut(BaseModel):
    """Schema for query session output."""
    session_id: str
    title: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class QuerySessionWithQueries(QuerySessionOut):
    """Schema for query session with all queries."""
    queries: List[QueryOut] = []
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    """Schema for creating a chat message."""
    role: str  # 'user', 'assistant', 'system'
    content: str

class ChatCreate(BaseModel):
    """Schema for creating a chat query."""
    messages: List[MessageCreate]
    provider: ProviderType
    model: ModelType
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Temperature must be between 0 and 1')
        return v
        
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if v is not None and v <= 0:
            return None  # Return None instead of an invalid value
        return v
        
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Normalize the string and check for invalid values
            v_lower = v.lower().strip()
            if v_lower in ('', 'string', 'null', 'none', 'undefined'):
                return None
        return v 
    


class EventRamadan(BaseModel):
    """Schema for answer of event ramadan."""
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # For Pydantic v2 compatibility


