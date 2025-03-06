"""
Prompt templates for recipe generation and manipulation with LLMs.

This package contains standardized templates for generating prompts
for Large Language Models (LLMs) related to recipe operations.
"""

from domains.recipes.prompts.factory import get_prompt_template, TemplateType
from domains.recipes.prompts.templates import (
    PromptTemplate,
    RecipeGenerationTemplate,
)

__all__ = [
    "get_prompt_template",
    "TemplateType",
    "PromptTemplate",
    "RecipeGenerationTemplate",
] 