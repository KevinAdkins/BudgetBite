"""
Test suite for validator measurement word fix.

Tests that measurement and descriptor words (thinly, shredded, tbsp, leaves)
are correctly filtered out and NOT reported as unmatched ingredients.

This test prevents regression of the validator fix applied in Sprint 2.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.validator import parse_recipe_ingredients, Ingredient


class TestMeasurementWordsFiltering:
    """Tests for filtering measurement and descriptor words."""

    def create_test_ingredients(self):
        """Create a basic set of ingredients for testing."""
        return [
            Ingredient(name="beef", quantity="1", unit="lb", category="meat", confidence=0.95),
            Ingredient(name="carrot", quantity="1", unit="", category="vegetable", confidence=0.95),
            Ingredient(name="garlic", quantity="3", unit="cloves", category="vegetable", confidence=0.95),
            Ingredient(name="lettuce", quantity="1", unit="", category="vegetable", confidence=0.95),
            Ingredient(name="radish", quantity="1", unit="", category="vegetable", confidence=0.95),
            Ingredient(name="potato", quantity="2", unit="", category="vegetable", confidence=0.95),
            Ingredient(name="cabbage", quantity="1", unit="", category="vegetable", confidence=0.95),
        ]

    def test_thinly_sliced_not_flagged(self):
        """Test that 'thinly' is not reported as an unmatched ingredient."""
        ingredients = self.create_test_ingredients()
        
        recipe = """
        Ingredients:
        - 1 lb beef
        - 2 carrots, thinly sliced
        - 3 cloves garlic, minced
        
        Instructions:
        Heat oil and cook beef. Add thinly sliced carrots and garlic.
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # 'thinly' should NOT be in unmatched ingredients
        assert 'thinly' not in result['unmatched'], \
            f"'thinly' should not be flagged as unmatched. Unmatched: {result['unmatched']}"
        
        # But the actual ingredients should be mentioned
        assert 'beef' in result['mentioned']
        assert 'carrot' in result['mentioned']
        assert 'garlic' in result['mentioned']

    def test_shredded_not_flagged(self):
        """Test that 'shredded' is not reported as an unmatched ingredient."""
        ingredients = self.create_test_ingredients()
        
        recipe = """
        Ingredients:
        - 1 cup red cabbage, shredded
        - 1 carrot, grated
        
        Instructions:
        Combine shredded cabbage with grated carrot for slaw.
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # 'shredded' should NOT be in unmatched ingredients
        assert 'shredded' not in result['unmatched'], \
            f"'shredded' should not be flagged as unmatched. Unmatched: {result['unmatched']}"
        
        # The actual ingredients should be mentioned
        assert 'cabbage' in result['mentioned']
        assert 'carrot' in result['mentioned']

    def test_tbsp_abbreviation_not_flagged(self):
        """Test that 'tbsp' measurement abbreviation is not reported as unmatched."""
        ingredients = self.create_test_ingredients()
        
        recipe = """
        Ingredients:
        - 2 tbsp olive oil
        - 3 cloves garlic, minced
        - 1 lb beef
        
        Instructions:
        Heat 2 tbsp oil in skillet. Add minced garlic and beef.
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # 'tbsp' should NOT be in unmatched ingredients
        assert 'tbsp' not in result['unmatched'], \
            f"'tbsp' should not be flagged as unmatched. Unmatched: {result['unmatched']}"
        
        # The actual ingredients should be mentioned
        assert 'garlic' in result['mentioned']
        assert 'beef' in result['mentioned']

    def test_leaves_not_flagged(self):
        """Test that 'leaves' is not reported as an unmatched ingredient."""
        ingredients = self.create_test_ingredients()
        
        recipe = """
        Ingredients:
        - 4 leaves of fresh lettuce
        - 2 tbsp vinaigrette
        
        Instructions:
        Arrange lettuce leaves on plate and drizzle with vinaigrette.
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # 'leaves' should NOT be in unmatched ingredients
        assert 'leaves' not in result['unmatched'], \
            f"'leaves' should not be flagged as unmatched. Unmatched: {result['unmatched']}"
        
        # But the actual ingredient should be mentioned
        assert 'lettuce' in result['mentioned']

    def test_complex_recipe_with_multiple_descriptors(self):
        """Test a more complex recipe with multiple descriptor words."""
        ingredients = self.create_test_ingredients()
        
        recipe = """
        Ingredients:
        - 1 lb beef, cubed
        - 2 carrots, thinly sliced
        - 1 cup red cabbage, shredded
        - 1 potato, diced
        - 3 cloves garlic, minced
        - 4 radishes, thinly sliced lengthwise
        - 4 leaves of iceberg lettuce
        - 2 tbsp olive oil
        - Salt and pepper to taste
        
        Instructions:
        Heat oil in skillet. Add cubed beef and cook until browned.
        Add thinly sliced carrots and shredded cabbage.
        Dice potato and add to pan with minced garlic.
        Arrange lettuce leaves on serving plate.
        Top with cooked mixture and garnish with radishes.
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # None of these measurement/descriptor words should be flagged as unmatched
        measurement_words = {'thinly', 'shredded', 'cubed', 'diced', 'minced', 'leaves', 'tbsp', 'lengthwise'}
        unmatched = result['unmatched']
        
        for word in measurement_words:
            assert word not in unmatched, \
                f"'{word}' should not be flagged as unmatched. Unmatched: {unmatched}"
        
        # All actual ingredients should be mentioned
        expected_ingredients = {'beef', 'carrot', 'cabbage', 'potato', 'garlic', 'radish', 'lettuce'}
        for ingredient in expected_ingredients:
            assert ingredient in result['mentioned'], \
                f"'{ingredient}' should be mentioned in the recipe"

    def test_valid_ingredients_correctly_identified(self):
        """Test that valid ingredients are correctly identified."""
        ingredients = self.create_test_ingredients()
        
        recipe = """
        Ingredients:
        - 1 lb beef
        - 2 carrots
        - 3 cloves garlic
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # Check that mentioned ingredients are correct
        assert 'beef' in result['mentioned']
        assert 'carrot' in result['mentioned']
        assert 'garlic' in result['mentioned']


class TestMeasurementWordsComprehensive:
    """Comprehensive tests for all measurement and descriptor terms."""

    def test_all_measurement_terms_filtered(self):
        """Test that all measurement-related terms are properly filtered."""
        ingredients = [
            Ingredient(name="beef", quantity="1", unit="lb", category="meat", confidence=0.95),
            Ingredient(name="vegetable", quantity="1", unit="", category="vegetable", confidence=0.95),
        ]
        
        # Include all measurement words that should be filtered
        recipe = """
        Ingredients:
        - 1 lb beef, thinly sliced
        - 1 vegetable, shredded
        - 2 tbsp oil
        - 1 tsp salt
        - 3 tablespoons sauce
        - 2 teaspoons spice
        - 1 cup broth
        - 3 tablespoons dressing
        - 4 leaves basil
        - 2 sprigs rosemary
        - 1 slice bread
        - 1 cup grated cheese
        - 2 cloves julienned
        - 1 carrot peeled
        - 1 cup cubed potato
        - 1 tablespoon crushed garlic
        - 1 cup crumbled feta
        - 1 can drained beans
        - 2 tbsp reserved oil
        """
        
        result = parse_recipe_ingredients(recipe, ingredients)
        
        # List of all measurement/descriptor words that should NOT be flagged
        measurement_words = {
            'thinly', 'shredded', 'tbsp', 'tsp', 'tablespoon', 'tablespoons',
            'teaspoon', 'teaspoons', 'cup', 'leaf', 'leaves', 'sprig', 'sprigs',
            'slice', 'grated', 'julienned', 'peeled', 'cubed', 'crushed',
            'crumbled', 'drained', 'reserved'
        }
        
        unmatched = result['unmatched']
        
        for word in measurement_words:
            assert word not in unmatched, \
                f"Measurement word '{word}' should not be flagged as unmatched. " \
                f"Unmatched words: {unmatched}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
