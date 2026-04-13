"""
Pipeline Integration Helpers - Bridges between pipeline_routes and AI modules

This module provides integration points for:
- Recipe generator (AI generation from ingredients + context)
- Ingredient validator (checking output against input)
- Budget pricing (Kroger API integration)
"""

import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Recipe Generator Integration
# ═══════════════════════════════════════════════════════════════════════════

def format_retrieved_recipes_for_context(recipes: List[Dict], max_count: int = 3) -> str:
    """
    Format retrieved database recipes as grounding context for the generator.
    
    Usage: Pass this as context to the recipe generator to guide generation.
    """
    if not recipes:
        return ""

    context = "# Reference Recipes from Database:\n"
    for i, recipe in enumerate(recipes[:max_count], 1):
        context += f"\n## {i}. {recipe.get('name', 'Unknown')}\n"
        context += f"- Category: {recipe.get('category', 'N/A')}\n"
        context += f"- Match Score: {recipe.get('match_score', {}).get('percentage', 'N/A')}%\n"
        context += f"- Ingredients: {recipe.get('ingredients', 'N/A')}\n"

    return context


def extract_recipe_ingredients_from_text(recipe_text: str) -> List[str]:
    """
    Extract ingredient list from natural language recipe text.
    
    Looks for common patterns like:
    - "Ingredients:"
    - Bullet points with measurements
    - Comma-separated lists
    
    Returns list of cleaned ingredient strings.
    """
    lines = recipe_text.split('\n')
    ingredients = []
    in_ingredient_section = False

    for line in lines:
        line = line.strip()

        # Detect ingredient section start
        if 'ingredient' in line.lower():
            in_ingredient_section = True
            continue

        # Detect section end
        if in_ingredient_section and any(x in line.lower() for x in ['instruction', 'direction', 'step']):
            break

        # Extract from ingredient section
        if in_ingredient_section and line:
            # Remove bullet points and numbers
            cleaned = line.lstrip('- •*123456789. ')
            if cleaned and not cleaned.isupper():  # Skip all-caps headers
                ingredients.append(cleaned)

    return [ing.strip() for ing in ingredients if ing.strip()]


# ═══════════════════════════════════════════════════════════════════════════
# Ingredient Validation Integration
# ═══════════════════════════════════════════════════════════════════════════

def parse_confidence_scores_from_extraction(
    extraction_data: Dict,
    threshold: float = 0.7
) -> Dict[str, float]:
    """
    Parse confidence scores from ingredient extraction.
    
    Extracts ingredients that meet the confidence threshold.
    
    Returns: dict of {ingredient_name: confidence_score}
    """
    confidence_map = {}

    try:
        ingredients = extraction_data.get("ingredients", [])

        if isinstance(ingredients, list):
            for ing in ingredients:
                if isinstance(ing, dict):
                    name = ing.get("name", "")
                    confidence = float(ing.get("confidence", 0.0))

                    if name and confidence >= threshold:
                        confidence_map[name] = confidence

        return confidence_map

    except Exception as e:
        logger.error(f"Error parsing confidence scores: {str(e)}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# Budget/Pricing Integration
# ═══════════════════════════════════════════════════════════════════════════

def estimate_recipe_cost_from_ingredients(
    ingredients: List[str],
    pricing_map: Optional[Dict[str, float]] = None
) -> float:
    """
    Estimate total recipe cost from ingredient list.
    
    Uses either:
    1. Provided pricing_map (from Kroger API)
    2. Simple heuristic based on ingredient keywords
    
    Returns: estimated cost in USD
    """
    if not ingredients:
        return 0.0

    # Default price heuristic (from pull.py)
    price_heuristic = {
        "chicken": 3.50,
        "beef": 4.00,
        "steak": 4.50,
        "lamb": 4.50,
        "fish": 3.75,
        "shrimp": 4.00,
        "prawn": 4.00,
        "salmon": 4.50,
        "egg": 0.35,
        "milk": 1.25,
        "butter": 1.80,
        "cheese": 2.25,
        "flour": 0.90,
        "rice": 0.90,
        "pasta": 1.20,
        "noodle": 1.20,
        "bread": 1.75,
        "tomato": 0.90,
        "onion": 0.60,
        "garlic": 0.45,
        "potato": 0.80,
        "pepper": 0.70,
        "oil": 0.80,
        "sugar": 0.65,
        "cream": 1.75,
        "yogurt": 1.25,
        "lemon": 0.60,
    }

    total = 0.0
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()

        # Check provided pricing map first
        if pricing_map:
            for price_key, price_value in pricing_map.items():
                if ingredient_lower in str(price_key).lower():
                    total += price_value
                    break
            else:
                # Not in pricing map, use heuristic
                price = next(
                    (v for k, v in price_heuristic.items() if k in ingredient_lower),
                    1.00
                )
                total += price
        else:
            # Use heuristic only
            price = next(
                (v for k, v in price_heuristic.items() if k in ingredient_lower),
                1.00
            )
            total += price

    return round(total, 2)


# ═══════════════════════════════════════════════════════════════════════════
# Response Formatting
# ═══════════════════════════════════════════════════════════════════════════

def format_recipe_response(
    recipe: Dict,
    validation_result: Optional[Dict] = None,
    budget_check: Optional[Dict] = None,
    pipeline_status: str = "success",
    iterations: int = 1,
) -> Dict:
    """
    Format a complete recipe response with all pipeline stages.
    
    Provides a clean, structured output for API clients.
    """
    return {
        "success": pipeline_status == "success",
        "recipe": {
            "name": recipe.get("name"),
            "category": recipe.get("category"),
            "ingredients": recipe.get("ingredients_list") or recipe.get("ingredients", []),
            "instructions": recipe.get("instructions"),
            "estimated_price": recipe.get("estimated_price"),
            "metadata": recipe.get("metadata", {}),
        },
        "validation": validation_result or {},
        "budget_check": budget_check or {},
        "pipeline_status": pipeline_status,
        "iterations": iterations,
    }
