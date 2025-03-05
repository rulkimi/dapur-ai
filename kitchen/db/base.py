from datetime import datetime, UTC
from typing import Any, Optional
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, event


class Base(DeclarativeBase):
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)


# Import all models to register them with Base.metadata
# Do not move this import as it would create circular imports
from db import models  # noqa


# Register a listener for session_id sanitization
def register_engine_events(engine):
    """
    Register engine-level event listeners to prevent foreign key violations
    with invalid session_id values.
    """
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(Engine, "before_execute", retval=True)
    def before_execute(conn, clauseelement, multiparams, params):
        # Check if this is an INSERT or UPDATE on the queries table
        sql_str = str(clauseelement).lower()
        if ("insert into queries" in sql_str or "update queries" in sql_str) and multiparams:
            # Sanitize session_id in the parameters if it's 'string'
            for idx, param_dict in enumerate(multiparams):
                if isinstance(param_dict, dict) and 'session_id' in param_dict and param_dict['session_id'] == 'string':
                    # Create a new dict with sanitized session_id
                    new_params = dict(param_dict)
                    new_params['session_id'] = None
                    multiparams = list(multiparams)
                    multiparams[idx] = new_params
        
        # Return the possibly modified statement and parameters
        return clauseelement, multiparams, params

