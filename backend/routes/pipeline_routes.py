"""
Pipeline Routes - Main end-to-end recipe generation pipeline

Flow:
1. Input validation + refusal handling (reject invalid input)
2. Database retrieval - top-k recipe matching
3. Recipe generation - use retrieved recipes as grounding context
4. Output ingredient validation - compare against input ingredients
5. Budget check - if budget provided, validate total cost
6. Regeneration loop - if validation fails, loop back to generation with refined context
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Optional, Tuple
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports to work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core modules
from models import database
import pull
import kroger_pricing

# Import AI modules (optional - graceful fallback if not available)
try:
    from src.recipe_generator import generate_recipe_from_context
except ImportError:
    generate_recipe_from_context = None

try:
    from src.validator import validate_recipe_ingredients, Ingredient
except ImportError:
    validate_recipe_ingredients = None

pipeline_bp = Blueprint('pipeline_bp', __name__)

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

MAX_REGENERATION_LOOPS = 3
TOP_K_RETRIEVED = 5
CONFIDENCE_THRESHOLD = 0.7

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: Input Validation & Refusal Handling
# ═══════════════════════════════════════════════════════════════════════════

def validate_pipeline_input(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Validate pipeline input and return (is_valid, error_message, normalized_data).
    
    Returns:
        (True, None, normalized_dict) if valid
        (False, error_msg, None) if invalid
    """
    if not data:
        return False, "Request body cannot be empty", None

    # Required field: ingredients
    ingredients = data.get("ingredients")
    if not ingredients:
        return False, "ingredients field is required and must not be empty", None

    if not isinstance(ingredients, list):
        return False, "ingredients must be a list", None

    if len(ingredients) == 0:
        return False, "ingredients list cannot be empty", None

    # Sanitize ingredients
    cleaned_ingredients = []
    for ing in ingredients:
        if isinstance(ing, str):
            cleaned = ing.strip()
            if cleaned:
                cleaned_ingredients.append(cleaned)
        elif isinstance(ing, dict) and "name" in ing:
            cleaned = str(ing.get("name", "")).strip()
            if cleaned:
                cleaned_ingredients.append(cleaned)

    if not cleaned_ingredients:
        return False, "No valid ingredients provided after sanitization", None

    # Optional: budget (in USD)
    budget = data.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
            if budget < 0:
                return False, "budget must be non-negative", None
        except (TypeError, ValueError):
            return False, "budget must be a valid number", None

    # Optional: dietary restrictions
    dietary_restrictions = data.get("dietaryRestrictions", [])
    if not isinstance(dietary_restrictions, list):
        dietary_restrictions = [dietary_restrictions] if dietary_restrictions else []

    # Optional: cuisine preference
    cuisine = data.get("cuisine", "").strip()

    # Optional: zip code for pricing
    zip_code = data.get("zipCode", "").strip()

    normalized = {
        "ingredients": cleaned_ingredients,
        "budget": budget,
        "dietary_restrictions": dietary_restrictions,
        "cuisine": cuisine,
        "zip_code": zip_code,
    }

    return True, None, normalized


# ═══════════════════════════════════════════════════════════════════════════
# Step 2: Database Retrieval - Top-K Matching
# ═══════════════════════════════════════════════════════════════════════════

def retrieve_top_k_recipes(ingredients: List[str], k: int = 5) -> List[Dict]:
    """
    Retrieve top-k recipes from database that match the ingredients.
    
    Strategy:
    - Query database for meals containing ANY of the ingredients
    - Rank by ingredient overlap
    - Return top-k with metadata
    """
    try:
        # Query database for all meals
        all_meals = database.get_all_meals()

        if not all_meals:
            logger.warning("No meals in database, returning empty list")
            return []

        # Score each meal by ingredient overlap
        scored_meals = []
        ing_lower = [i.lower() for i in ingredients]

        for meal in all_meals:
            meal_ingredients_text = (meal.get("ingredients") or "").lower()
            
            # Count overlapping ingredients (simple token matching)
            overlap_count = sum(
                1 for ing in ing_lower
                if ing in meal_ingredients_text
            )

            if overlap_count > 0:
                score = overlap_count / len(ing_lower)  # Normalized score
                scored_meals.append({
                    **meal,
                    "match_score": {
                        "overlap": overlap_count,
                        "percentage": round(score * 100, 1)
                    }
                })

        # Sort by score descending
        scored_meals.sort(key=lambda x: x["match_score"]["overlap"], reverse=True)

        # Return top-k
        result = scored_meals[:k]
        logger.info(f"Retrieved {len(result)} matching recipes from database (top-{k})")
        return result

    except Exception as e:
        logger.error(f"Error retrieving recipes: {str(e)}", exc_info=True)
        return []


# ═══════════════════════════════════════════════════════════════════════════
# Step 3: Recipe Generation (Mocked & Real)
# ═══════════════════════════════════════════════════════════════════════════

def generate_recipe_mock(
    ingredients: List[str],
    retrieved_context: Optional[List[Dict]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    iteration: int = 1,
) -> Dict:
    """
    MOCKED recipe generation - returns a valid structure without AI calls.
    Use this to test the full pipeline end-to-end before integrating the real generator.
    """
    # Simple mock based on ingredients
    main_ingredient = ingredients[0] if ingredients else "vegetables"
    
    mock_recipe = {
        "name": f"Creative {cuisine or 'Mixed'} Dish with {main_ingredient.title()}",
        "category": cuisine or "Mixed",
        "instructions": f"1. Prepare {', '.join(ingredients[:3])}\n2. Cook until done\n3. Serve hot",
        "ingredients": ", ".join(ingredients),
        "ingredients_list": ingredients,  # For validation
        "estimated_price": round(len(ingredients) * 1.5, 2),
        "metadata": {
            "iteration": iteration,
            "type": "mock",
            "generated_at": pull.current_price_timestamp(),
        }
    }

    logger.info(f"Generated MOCK recipe (iteration {iteration}): {mock_recipe['name']}")
    return mock_recipe


def generate_recipe_real(
    ingredients: List[str],
    retrieved_context: Optional[List[Dict]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    iteration: int = 1,
) -> Optional[Dict]:
    """
    REAL recipe generation using the recipe_generator module.
    Requires the full src.recipe_generator module to be available.
    """
    if generate_recipe_from_context is None:
        logger.warning("recipe_generator module not available, falling back to mock")
        return generate_recipe_mock(ingredients, retrieved_context, dietary_restrictions, cuisine, iteration)

    try:
        # TODO: Implement once recipe_generator is integrated
        logger.info("Real recipe generation not yet implemented")
        return generate_recipe_mock(ingredients, retrieved_context, dietary_restrictions, cuisine, iteration)
    except Exception as e:
        logger.error(f"Real recipe generation failed: {str(e)}", exc_info=True)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Step 4: Output Ingredient Validation
# ═══════════════════════════════════════════════════════════════════════════

def validate_recipe_output(
    generated_recipe: Dict,
    input_ingredients: List[str],
) -> Tuple[bool, Dict]:
    """
    Validate that generated recipe only uses ingredients from the input list.
    
    Returns:
        (is_valid, validation_result_dict)
    """
    validation_result = {
        "is_valid": False,
        "input_ingredients": input_ingredients,
        "recipe_ingredients": [],
        "missing_ingredients": [],
        "validation_errors": [],
        "confidence_issues": [],
    }

    try:
        # Parse recipe ingredients
        recipe_ing_str = generated_recipe.get("ingredients_list") or generated_recipe.get("ingredients", "")
        
        if isinstance(recipe_ing_str, list):
            recipe_ingredients = recipe_ing_str
        else:
            recipe_ingredients = [ing.strip() for ing in str(recipe_ing_str).split(",") if ing.strip()]

        validation_result["recipe_ingredients"] = recipe_ingredients

        # Check each recipe ingredient against input
        input_ing_lower = [i.lower() for i in input_ingredients]
        
        missing = []
        for recipe_ing in recipe_ingredients:
            recipe_ing_lower = recipe_ing.lower()
            
            # Check if this ingredient matches any input ingredient
            found = any(
                recipe_ing_lower in ing_lower or ing_lower in recipe_ing_lower
                for ing_lower in input_ing_lower
            )

            if not found:
                missing.append(recipe_ing)

        if missing:
            validation_result["missing_ingredients"] = missing
            validation_result["validation_errors"].append(
                f"Recipe uses ingredients not in input list: {', '.join(missing)}"
            )
        else:
            validation_result["is_valid"] = True

        logger.info(f"Validation result: valid={validation_result['is_valid']}, missing={len(missing)}")
        return validation_result["is_valid"], validation_result

    except Exception as e:
        validation_result["validation_errors"].append(f"Validation error: {str(e)}")
        logger.error(f"Validation failed: {str(e)}", exc_info=True)
        return False, validation_result


# ═══════════════════════════════════════════════════════════════════════════
# Step 5: Budget Checking
# ═══════════════════════════════════════════════════════════════════════════

def check_budget(
    recipe: Dict,
    budget: Optional[float],
    zip_code: Optional[str],
) -> Tuple[bool, Dict]:
    """
    Check if recipe fits within budget using pricing API if available.
    
    Returns:
        (is_within_budget, budget_check_result)
    """
    budget_check = {
        "has_budget_constraint": budget is not None,
        "budget": budget,
        "estimated_cost": None,
        "is_within_budget": None,
        "message": "",
        "pricing_source": "estimate",
    }

    if budget is None:
        budget_check["message"] = "No budget constraint provided"
        return True, budget_check

    try:
        # Get simplified estimate from recipe
        estimated_cost = recipe.get("estimated_price", 0.0)
        budget_check["estimated_cost"] = estimated_cost

        if estimated_cost <= budget:
            budget_check["is_within_budget"] = True
            budget_check["message"] = f"Recipe cost (${estimated_cost:.2f}) is within budget (${budget:.2f})"
        else:
            budget_check["is_within_budget"] = False
            budget_check["message"] = f"Recipe cost (${estimated_cost:.2f}) exceeds budget (${budget:.2f})"

        # TODO: If zip_code provided, fetch real pricing from kroger_pricing API

        logger.info(budget_check["message"])
        return budget_check["is_within_budget"], budget_check

    except Exception as e:
        budget_check["message"] = f"Budget check error: {str(e)}"
        budget_check["is_within_budget"] = None
        logger.error(f"Budget check failed: {str(e)}", exc_info=True)
        return True, budget_check  # Soft fail - don't block on pricing error


# ═══════════════════════════════════════════════════════════════════════════
# Step 6: Regeneration Loop
# ═══════════════════════════════════════════════════════════════════════════

def regenerate_with_feedback(
    original_recipe: Dict,
    validation_result: Dict,
    budget_check: Dict,
    ingredients: List[str],
    retrieved_context: List[Dict],
    iteration: int,
) -> Optional[Dict]:
    """
    Generate a refined recipe based on validation/budget feedback.
    """
    feedback = []

    if not validation_result["is_valid"]:
        feedback.append(f"Avoid: {', '.join(validation_result['missing_ingredients'])}")

    if budget_check.get("is_within_budget") is False:
        feedback.append(f"Keep cost under ${budget_check['budget']:.2f}")

    context_note = "\n".join([f"Reference: {r['name']}" for r in retrieved_context[:2]])

    logger.info(f"Regenerating recipe (iteration {iteration}) with feedback: {feedback}")

    # Generate with refined parameters
    refined_recipe = generate_recipe_mock(
        ingredients,
        retrieved_context,
        iteration=iteration,
    )

    refined_recipe["metadata"]["feedback"] = feedback
    refined_recipe["metadata"]["iteration"] = iteration

    return refined_recipe


# ═══════════════════════════════════════════════════════════════════════════
# Main Pipeline Endpoint
# ═══════════════════════════════════════════════════════════════════════════

@pipeline_bp.route('/pipeline/generate-recipe', methods=['POST'])
def generate_recipe_pipeline():
    """
    Main pipeline endpoint: Generate recipe from ingredients with validation + budget check.

    Request JSON:
    {
        "ingredients": ["chicken", "tomato", "basil"],
        "budget": 15.00,                           # Optional
        "zipCode": "78207",                        # Optional (for real pricing)
        "dietaryRestrictions": ["vegetarian"],    # Optional
        "cuisine": "Italian"                       # Optional
    }

    Response:
    {
        "success": true,
        "recipe": {...},
        "validation": {...},
        "budget_check": {...},
        "pipeline_status": "success" | "failed" | "budget_exceeded",
        "iterations": 1,
        "timestamp": "..."
    }
    """
    data = request.get_json(silent=True) or {}

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Input Validation
    # ─────────────────────────────────────────────────────────────────────────
    is_valid, error_msg, normalized_input = validate_pipeline_input(data)

    if not is_valid:
        logger.warning(f"Input validation failed: {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg,
            "pipeline_status": "input_rejected",
            "timestamp": pull.current_price_timestamp(),
        }), 400

    ingredients = normalized_input["ingredients"]
    budget = normalized_input["budget"]
    dietary_restrictions = normalized_input["dietary_restrictions"]
    cuisine = normalized_input["cuisine"]
    zip_code = normalized_input["zip_code"]

    try:
        # ─────────────────────────────────────────────────────────────────────
        # STEP 2: Database Retrieval
        # ─────────────────────────────────────────────────────────────────────
        retrieved_recipes = retrieve_top_k_recipes(ingredients, k=TOP_K_RETRIEVED)

        # ─────────────────────────────────────────────────────────────────────
        # STEPS 3-6: Generation Loop with Validation
        # ─────────────────────────────────────────────────────────────────────
        final_recipe = None
        final_validation = None
        final_budget_check = None
        iteration = 0

        for iteration in range(1, MAX_REGENERATION_LOOPS + 1):
            logger.info(f"─ Pipeline iteration {iteration}/{MAX_REGENERATION_LOOPS}")

            # Step 3: Generate recipe
            recipe = generate_recipe_mock(
                ingredients=ingredients,
                retrieved_context=retrieved_recipes,
                dietary_restrictions=dietary_restrictions,
                cuisine=cuisine,
                iteration=iteration,
            )

            if not recipe:
                logger.error("Recipe generation failed")
                return jsonify({
                    "success": False,
                    "error": "Failed to generate recipe",
                    "pipeline_status": "generation_failed",
                    "timestamp": pull.current_price_timestamp(),
                }), 500

            # Step 4: Validate output
            is_valid_ing, validation = validate_recipe_output(recipe, ingredients)

            # Step 5: Budget check
            is_within_budget, budget_check = check_budget(recipe, budget, zip_code)

            logger.info(
                f"  Validation: {is_valid_ing} | Budget: {is_within_budget}"
            )

            # Success: both validation and budget pass
            if is_valid_ing and is_within_budget:
                final_recipe = recipe
                final_validation = validation
                final_budget_check = budget_check
                break

            # Partial success: save for later, but try to improve
            if is_valid_ing:
                final_recipe = recipe
                final_validation = validation
                final_budget_check = budget_check
                # Don't break - try to fit budget in next iteration

            # Step 6: Regenerate if not valid
            if not is_valid_ing or not is_within_budget:
                if iteration < MAX_REGENERATION_LOOPS:
                    recipe = regenerate_with_feedback(
                        original_recipe=recipe,
                        validation_result=validation,
                        budget_check=budget_check,
                        ingredients=ingredients,
                        retrieved_context=retrieved_recipes,
                        iteration=iteration + 1,
                    )
                    # Continue to next iteration
                else:
                    logger.warning("Max regeneration loops reached")

        # ─────────────────────────────────────────────────────────────────────
        # Prepare Final Response
        # ─────────────────────────────────────────────────────────────────────
        if not final_recipe:
            return jsonify({
                "success": False,
                "error": "Failed to generate valid recipe after all attempts",
                "pipeline_status": "failed",
                "iterations": iteration,
                "timestamp": pull.current_price_timestamp(),
            }), 500

        # Determine pipeline status
        pipeline_status = "success"
        if not final_validation.get("is_valid"):
            pipeline_status = "validation_failed"
        elif final_budget_check.get("is_within_budget") is False:
            pipeline_status = "budget_exceeded"

        response = {
            "success": pipeline_status == "success",
            "recipe": final_recipe,
            "validation": final_validation,
            "budget_check": final_budget_check,
            "pipeline_status": pipeline_status,
            "iterations": iteration,
            "retrieved_context_count": len(retrieved_recipes),
            "timestamp": pull.current_price_timestamp(),
        }

        status_code = 200 if pipeline_status == "success" else 202  # 202 = Accepted but incomplete

        logger.info(f"Pipeline complete: {pipeline_status} (iterations={iteration})")
        return jsonify(response), status_code

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Internal pipeline error: {str(e)}",
            "pipeline_status": "error",
            "timestamp": pull.current_price_timestamp(),
        }), 500
