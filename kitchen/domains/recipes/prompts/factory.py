"""
Factory functions for prompt templates.

This module provides functions to retrieve and manage prompt templates.
"""

from typing import Dict, Optional, Type

from domains.recipes.prompts.models import TemplateType
from domains.recipes.prompts.protocols import PromptTemplate
from domains.recipes.prompts.templates import RecipeGenerationTemplate


# Registry of template classes by type
_TEMPLATE_REGISTRY: Dict[str, Type[PromptTemplate]] = {
    TemplateType.RECIPE_GENERATION.value: RecipeGenerationTemplate,
    # Add other template types here as they are implemented
}


# Cache of template instances
_TEMPLATE_CACHE: Dict[str, PromptTemplate] = {}


def get_prompt_template(template_type: TemplateType, version: Optional[str] = None) -> PromptTemplate:
    """
    Get a prompt template instance by type and optionally version.
    
    Args:
        template_type: The type of template to retrieve
        version: Optional specific version to retrieve (if None, gets latest)
        
    Returns:
        A prompt template instance
        
    Raises:
        ValueError: If the template type is not registered
        ValueError: If the requested version is not available
    """
    template_key = template_type.value
    
    if template_key not in _TEMPLATE_REGISTRY:
        raise ValueError(f"Template type '{template_key}' is not registered")
    
    # For now, we don't have versioning implemented yet, so we always return
    # the current version of the template
    if template_key not in _TEMPLATE_CACHE:
        template_class = _TEMPLATE_REGISTRY[template_key]
        _TEMPLATE_CACHE[template_key] = template_class()
    
    template = _TEMPLATE_CACHE[template_key]
    
    # If a specific version was requested, check if it matches
    if version is not None and template.version != version:
        raise ValueError(f"Template version '{version}' not available for type '{template_key}'")
    
    return template


def register_template(template_type: str, template_class: Type[PromptTemplate]) -> None:
    """
    Register a new template class for a template type.
    
    Args:
        template_type: The template type to register
        template_class: The template class to register
        
    Raises:
        ValueError: If the template type is already registered
    """
    if template_type in _TEMPLATE_REGISTRY:
        raise ValueError(f"Template type '{template_type}' is already registered")
    
    _TEMPLATE_REGISTRY[template_type] = template_class
    
    # Clear the cache for this template type
    if template_type in _TEMPLATE_CACHE:
        del _TEMPLATE_CACHE[template_type] 