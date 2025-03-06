"""
Protocols for prompt templates in the recipes domain.

This module defines the interfaces that all prompt templates must implement.
"""

from typing import Protocol, Any, Dict


class PromptTemplate(Protocol):
    """Base protocol for prompt templates."""
    
    @property
    def version(self) -> str:
        """Return the version of the template."""
        ...
    
    @property
    def template_type(self) -> str:
        """Return the type of the template."""
        ...
    
    def format(self, **kwargs: Any) -> str:
        """
        Format the template with the provided parameters.
        
        Args:
            **kwargs: The parameters to use for formatting the template.
            
        Returns:
            str: The formatted prompt.
        """
        ... 