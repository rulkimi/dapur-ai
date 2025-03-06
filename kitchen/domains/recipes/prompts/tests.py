"""
Unit tests for prompt templates.

This module contains tests for the prompt template system.
"""

import unittest
from typing import List, Dict, Any, Optional

from domains.recipes.prompts import (
    get_prompt_template,
    TemplateType,
    RecipeGenerationTemplate
)


class TestRecipeGenerationTemplate(unittest.TestCase):
    """Tests for the recipe generation template."""
    
    def test_empty_preferences(self):
        """Test prompt generation with empty preferences."""
        template = get_prompt_template(TemplateType.RECIPE_GENERATION)
        
        prompt = template.format(
            system_prompt="",
            user_name="Test User",
            number_of_recipes=1
        )
        
        # Basic assertions that the prompt contains expected text
        self.assertIn("I need to generate 1 recipe", prompt)
        self.assertIn("A creative name", prompt)
        self.assertIn("Total cooking time", prompt)
        self.assertIn("Difficulty level", prompt)
        self.assertIn("list of all ingredients", prompt)
        
    def test_with_preferences(self):
        """Test prompt generation with user preferences."""
        template = get_prompt_template(TemplateType.RECIPE_GENERATION)
        
        prompt = template.format(
            system_prompt="You are a helpful cooking assistant.",
            user_name="Jane Doe",
            dietary_restrictions=["Vegetarian", "Gluten-free"],
            allergies=["Nuts", "Shellfish"],
            preferred_cuisines=["Italian", "Japanese"],
            spice_level="Medium",
            additional_info="Quick meals under 30 minutes preferred",
            number_of_recipes=2
        )
        
        # Basic assertions to verify preferences are included
        self.assertIn("You are a helpful cooking assistant", prompt)
        self.assertIn("I need to generate 2 recipe", prompt)
        self.assertIn("Dietary Restrictions: Vegetarian, Gluten-free", prompt)
        self.assertIn("Allergies: Nuts, Shellfish", prompt)
        self.assertIn("Preferred Cuisines: Italian, Japanese", prompt)
        self.assertIn("Spice Level: Medium", prompt)
        self.assertIn("Additional Information: Quick meals under 30 minutes preferred", prompt)
        
    def test_template_version(self):
        """Test that the template has the expected version."""
        template = RecipeGenerationTemplate()
        self.assertEqual(template.version, "1.0.0")
        
    def test_template_type(self):
        """Test that the template has the expected type."""
        template = RecipeGenerationTemplate()
        self.assertEqual(template.template_type, TemplateType.RECIPE_GENERATION.value)


if __name__ == "__main__":
    unittest.main() 