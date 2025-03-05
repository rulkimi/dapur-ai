import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_env_var(name: str, default: Optional[str] = None) -> str:
    """Get an environment variable, with a default fallback."""
    value = os.environ.get(name, default)
    if value is None:
        logger.warning(f"Environment variable {name} not set")
        return ""
    return value
    
def count_tokens(text: str) -> int:
    """Approximate token count for a string."""
    # Simple approximation, not accurate for all models
    return len(text.split())
    
# Add more utility functions as needed 