import os
import sys
from pathlib import Path


os.environ.setdefault("GEMINI_API_KEY", "test-key")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.validator import Ingredient, parse_recipe_ingredients


def test_measurement_words_are_not_reported_as_unmatched():
    valid_ingredients = [
        Ingredient(name="red cabbage", quantity=None, unit=None, category="produce", confidence=0.98),
        Ingredient(name="carrot", quantity=None, unit=None, category="produce", confidence=0.97),
        Ingredient(name="iceberg lettuce", quantity=None, unit=None, category="produce", confidence=0.96),
        Ingredient(name="pea pods", quantity=None, unit=None, category="produce", confidence=0.95),
        Ingredient(name="russet potatoes", quantity=None, unit=None, category="produce", confidence=0.94),
        Ingredient(name="ground beef", quantity=None, unit=None, category="meat", confidence=0.99),
    ]

    recipe_text = """Ingredients:
- 1 cup red cabbage, shredded
- 1 large carrot, grated
- 4 leaves iceberg lettuce
- 1/2 cup pea pods, thinly sliced lengthwise
- 1 tbsp ground beef
- 2 russet potatoes, peeled

Instructions:
1. Combine the shredded cabbage with the grated carrot.
2. Serve on lettuce leaves with the pea pods.
"""

    result = parse_recipe_ingredients(recipe_text, valid_ingredients)

    assert result["unmatched"].isdisjoint({"thinly", "shredded", "tbsp", "leaves"})
