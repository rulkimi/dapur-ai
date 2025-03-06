"""
Concrete implementations of prompt templates.

This module contains the implementations of various prompt templates
used for recipe-related LLM operations.
"""

from typing import Any, Dict, List, Optional

from domains.recipes.prompts.models import TemplateType, TemplateConfig, RecipeGenerationInput


class PromptTemplate:
    """Base class for prompt templates."""
    
    def __init__(self, config: TemplateConfig):
        self._config = config
    
    @property
    def version(self) -> str:
        """Return the version of the template."""
        return self._config.version
    
    @property
    def template_type(self) -> str:
        """Return the type of the template."""
        return self._config.template_type.value
    
    def format(self, **kwargs: Any) -> str:
        """Format the template with the provided parameters."""
        raise NotImplementedError("Subclasses must implement this method")


class RecipeGenerationTemplate(PromptTemplate):
    """Template for generating recipe prompts."""
    
    def __init__(self):
        """Initialize the recipe generation template."""
        config = TemplateConfig(
            version="1.0.0",
            template_type=TemplateType.RECIPE_GENERATION,
            description="Prompt template for generating recipes based on user preferences"
        )
        super().__init__(config)
    
    def format(self, **kwargs: Any) -> str:
        """
        Format the recipe generation prompt with user preferences.
        
        Args:
            **kwargs: Should include parameters matching RecipeGenerationInput fields.
            
        Returns:
            str: The formatted prompt for recipe generation.
        """
        # Convert kwargs to validated input model
        input_data = RecipeGenerationInput(**kwargs)
        
        # Start building the prompt
        prompt = f"{input_data.system_prompt}\n\n"
        prompt += f"I need to generate {input_data.number_of_recipes} recipe(s) based on the following preferences:\n\n"
        
        # Add user preferences if present
        if input_data.dietary_restrictions:
            prompt += f"Dietary Restrictions: {', '.join(input_data.dietary_restrictions)}\n"
        
        if input_data.allergies:
            prompt += f"Allergies: {', '.join(input_data.allergies)}\n"
        
        if input_data.preferred_cuisines:
            prompt += f"Preferred Cuisines: {', '.join(input_data.preferred_cuisines)}\n"
        
        if input_data.spice_level:
            prompt += f"Spice Level: {input_data.spice_level}\n"
        
        if input_data.additional_info:
            prompt += f"Additional Information: {input_data.additional_info}\n"
        
        # Add the standard instructions for recipe generation
        prompt += """
        Please generate a detailed recipe that matches these preferences. The recipe should include:
        
        1. A creative name
        2. A detailed description explaining what the dish is and its flavor profile
        3. Total cooking time in minutes
        4. Difficulty level (Easy, Medium, or Difficult)
        5. A list of all ingredients with precise quantities and measurements
        6. Relevant tags for the recipe
        
        Make sure the recipe:
        - Takes into account all dietary restrictions and allergies
        - Matches preferred cuisines when possible
        - Adjusts to the specified spice level
        - Provides measurements in standard units (cups, tablespoons, grams, etc.)
        """
        
        return prompt 