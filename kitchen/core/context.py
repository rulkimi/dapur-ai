import contextvars
import uuid
from typing import Optional

# Create context variable for request ID
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_var.get()

def set_request_id(request_id: Optional[str] = None) -> None:
    """Set the current request ID in context."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

def reset_request_id() -> None:
    """Reset the request ID to an empty string."""
    request_id_var.set("") 