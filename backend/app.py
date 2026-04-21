from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
import pull
import kroger_pricing
from routes.meal_routes import meal_bp
from routes.pricing_routes import pricing_bp
from routes.pipeline_routes import pipeline_bp
import base64
import tempfile
import os
import sys

# Add src to path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ingredient_extractor import extract_ingredients
from retrieval import get_all_meals, match_ingredients_to_meals
from recipe_generator import generate_recipe
from pricing import extract_ingredients_from_recipe_text, filter_pricing_ingredients

app = Flask(__name__)

BUDGET_TIER_LIMITS = {
    'tier1': 25.0,
    'tier2': 50.0,
    'tier3': None,
}


def _extract_estimated_total(pricing_payload):
    if not isinstance(pricing_payload, dict):
        return None
    total = pricing_payload.get('estimatedTotal')
    if total is None:
        total = pricing_payload.get('subtotal')
    if total is None:
        return None
    try:
        return float(total)
    except (TypeError, ValueError):
        return None


def _is_recipe_over_budget(estimated_total, budget_tier):
    budget_limit = BUDGET_TIER_LIMITS.get(budget_tier)
    if budget_limit is None or estimated_total is None:
        return False
    return estimated_total > budget_limit


def _is_recipe_below_budget_floor(estimated_total, budget_tier):
    # Medium tier targets a range ($25-$50), so values below the floor are out of range.
    if estimated_total is None:
        return False
    if budget_tier == 'tier2':
        return estimated_total < 25.0
    return False


def _build_top_matches(ingredients):
    meals = get_all_meals()
    matches = match_ingredients_to_meals(ingredients, meals)

    top_matches = []
    for match in matches[:5]:
        meal = match['meal']
        top_matches.append({
            "name": meal['name'],
            "category": meal.get('category', 'unknown'),
            "ingredients": meal.get('ingredients', ''),
            "instructions": meal.get('instructions', ''),
            "match_score": {
                "percentage": round(match['match_percentage'], 1),
                "matching": match['matching_count'],
                "total": match['total_ingredients'],
                "missing": match['missing_count']
            }
        })

    return top_matches


def _analyze_ingredients_pipeline(
    ingredients,
    budget_tier,
    zip_code,
    requested_strategy,
    regenerate_recipe=False,
    max_regeneration_attempts=3,
    non_food_items_detected=False,
):
    top_matches = _build_top_matches(ingredients)

    extracted_ingredient_names = [
        ing["name"].strip().lower()
        for ing in ingredients
        if isinstance(ing.get("name"), str) and ing["name"].strip()
    ]

    generated_recipe = None
    recipe_generation_error = None
    generated_recipe_pricing = None
    generated_recipe_pricing_error = None
    generated_recipe_pricing_ingredients = []
    recipe_over_budget = False
    recipe_under_budget = False
    regeneration_prompt = None
    generation_attempts = 0
    budget_limit = BUDGET_TIER_LIMITS.get(budget_tier)

    generation_attempt_limit = max_regeneration_attempts if regenerate_recipe else 1

    if top_matches and extracted_ingredient_names:
        while generation_attempts < generation_attempt_limit:
            generation_attempts += 1
            recipe_over_budget = False
            recipe_under_budget = False
            generated_recipe_pricing = None
            generated_recipe_pricing_error = None
            generated_recipe_pricing_ingredients = []

            try:
                generated_recipe = generate_recipe(top_matches, extracted_ingredient_names)
            except Exception as recipe_error:
                recipe_generation_error = str(recipe_error)
                break

            try:
                parsed_recipe_ingredients = extract_ingredients_from_recipe_text(generated_recipe)
                generated_recipe_pricing_ingredients = filter_pricing_ingredients(parsed_recipe_ingredients)

                if generated_recipe_pricing_ingredients:
                    generated_recipe_pricing = kroger_pricing.estimate_ingredient_total(
                        generated_recipe_pricing_ingredients,
                        zip_code,
                        price_strategy=requested_strategy,
                    )
            except Exception as pricing_error:
                generated_recipe_pricing_error = str(pricing_error)
                break

            estimated_total = _extract_estimated_total(generated_recipe_pricing)
            recipe_over_budget = _is_recipe_over_budget(estimated_total, budget_tier)
            recipe_under_budget = _is_recipe_below_budget_floor(estimated_total, budget_tier)
            recipe_outside_budget_range = recipe_over_budget or recipe_under_budget

            if not recipe_outside_budget_range:
                break

            if not regenerate_recipe:
                if recipe_under_budget and estimated_total is not None:
                    regeneration_prompt = (
                        f"This recipe is estimated at ${estimated_total:.2f}, which is below your "
                        "tier2 target range ($25.00-$50.00). Regenerate recipe?"
                    )
                elif budget_limit is not None and estimated_total is not None:
                    regeneration_prompt = (
                        f"This recipe is estimated at ${estimated_total:.2f}, which exceeds your "
                        f"{budget_tier} limit (${budget_limit:.2f}). Regenerate recipe?"
                    )
                elif budget_limit is not None:
                    regeneration_prompt = (
                        f"This recipe may exceed your {budget_tier} limit (${budget_limit:.2f}). "
                        "Regenerate recipe?"
                    )
                break

        if regenerate_recipe and (recipe_over_budget or recipe_under_budget):
            if recipe_under_budget:
                regeneration_prompt = (
                    f"Tried {generation_attempts} generation attempt(s), but the latest recipe is still "
                    "below the tier2 target range ($25.00-$50.00)."
                )
            elif budget_limit is not None:
                regeneration_prompt = (
                    f"Tried {generation_attempts} generation attempt(s), but the latest recipe still "
                    f"exceeds your {budget_tier} limit (${budget_limit:.2f})."
                )

    return {
        "ingredients": ingredients,
        "non_food_items_detected": non_food_items_detected,
        "matched_recipes": top_matches,
        "generated_recipe": generated_recipe,
        "recipe_generation_error": recipe_generation_error,
        "generated_recipe_pricing_ingredients": generated_recipe_pricing_ingredients,
        "generated_recipe_pricing": generated_recipe_pricing,
        "generated_recipe_pricing_error": generated_recipe_pricing_error,
        "recipe_over_budget": recipe_over_budget,
        "recipe_under_budget": recipe_under_budget,
        "budget_limit": budget_limit,
        "generation_attempts": generation_attempts,
        "regeneration_requested": regenerate_recipe,
        "regeneration_prompt": regeneration_prompt,
        "can_regenerate": recipe_over_budget or recipe_under_budget,
    }

# Enable CORS for frontned access
CORS(app)
# Maintainer note:
# Keep DB initialization before blueprint registration so first request does not
# race table creation when running in a fresh environment.
pull.init_db()

app.register_blueprint(meal_bp, url_prefix='/api')
app.register_blueprint(pricing_bp, url_prefix='/api')
app.register_blueprint(pipeline_bp, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({
        "message": "BudgetBite API",
        "version": "1.0",
        "endpoints": {
            "GET /api/meals": "Get all meals",
            "GET /api/meals/<name>": "Get specific meal",
            "GET /api/meals/search?name=<name>": "Search for meal (DB + API)",
            "GET /api/meals/search-by-ingredient?ingredient=<ingredient>&full=true&first=true": "Search by ingredient and optionally return full details for first match",
            "POST /api/analyze": "Analyze fridge image",
            "POST /api/analyze-text": "Analyze text ingredients",
            "POST /api/pricing/ingredients": "Estimate total ingredient cost with Kroger API",
            "POST /api/kroger/pricing/ingredients": "Estimate ingredient pricing via app route",
            "GET /api/kroger/pricing/strategies": "List allowed Kroger pricing strategies",
            "POST /api/pipeline/generate-recipe": "Main pipeline: Generate recipe from ingredients with validation + budget checking",
            "POST /api/meals": "Add new meal",
            "PUT /api/meals/<name>": "Update meal",
            "PATCH /api/meals/<name>/instructions": "Update instructions only",
            "DELETE /api/meals/<name>": "Delete meal"
        }
    })

# Image input route
@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        budget_tier = data.get('budget_tier', 'tier1')
        regenerate_recipe = bool(data.get('regenerate_recipe', False))
        max_regeneration_attempts = data.get('max_regeneration_attempts', 3)
        try:
            max_regeneration_attempts = int(max_regeneration_attempts)
        except (TypeError, ValueError):
            max_regeneration_attempts = 3
        max_regeneration_attempts = max(1, min(max_regeneration_attempts, 5))

        budget_labels = {
            'tier1': 'less than $25 (budget-friendly, cheap ingredients)',
            'tier2': 'between $25 and $50 (moderate budget)',
            'tier3': 'greater than $50 (premium ingredients allowed)'
        }
        budget_description = budget_labels.get(budget_tier, 'less than $25')
        zip_code = (data.get('zipCode') or os.getenv("KROGER_ZIP_CODE", "78201")).strip()
        requested_strategy = (data.get('priceStrategy') or kroger_pricing.DEFAULT_PRICE_STRATEGY).strip()

        # Decode base64 image to temp file
        image_data = base64.b64decode(data['image'])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(image_data)
            tmp_path = tmp.name

        # Step 1: Extract ingredients via Gemini
        result = extract_ingredients(tmp_path, budget_description)
        os.unlink(tmp_path)

        ingredients = [
            {
                "name": ing.name,
                "quantity": ing.quantity,
                "unit": ing.unit,
                "category": ing.category
            }
            for ing in result.ingredients
        ]

        return jsonify(
            _analyze_ingredients_pipeline(
                ingredients=ingredients,
                budget_tier=budget_tier,
                zip_code=zip_code,
                requested_strategy=requested_strategy,
                regenerate_recipe=regenerate_recipe,
                max_regeneration_attempts=max_regeneration_attempts,
                non_food_items_detected=result.non_food_items_detected,
            )
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Text input route
@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        if not data or 'ingredients' not in data:
            return jsonify({"error": "No ingredients provided"}), 400

        budget_tier = data.get('budget_tier', 'tier1')
        regenerate_recipe = bool(data.get('regenerate_recipe', False))
        max_regeneration_attempts = data.get('max_regeneration_attempts', 3)
        try:
            max_regeneration_attempts = int(max_regeneration_attempts)
        except (TypeError, ValueError):
            max_regeneration_attempts = 3
        max_regeneration_attempts = max(1, min(max_regeneration_attempts, 5))

        zip_code = (data.get('zipCode') or os.getenv("KROGER_ZIP_CODE", "78201")).strip()
        requested_strategy = (data.get('priceStrategy') or kroger_pricing.DEFAULT_PRICE_STRATEGY).strip()

        # Parse comma text input
        raw = data['ingredients']
        ingredients = [
            {"name": i.strip(), "quantity": None, "unit": None, "category": "unknown"}
            for i in raw.split(',') if i.strip()
        ]

        return jsonify(
            _analyze_ingredients_pipeline(
                ingredients=ingredients,
                budget_tier=budget_tier,
                zip_code=zip_code,
                requested_strategy=requested_strategy,
                regenerate_recipe=regenerate_recipe,
                max_regeneration_attempts=max_regeneration_attempts,
                non_food_items_detected=False,
            )
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/kroger/pricing/strategies', methods=['GET'])
def kroger_pricing_strategies():
    """Expose allowed pricing strategy values for frontend/backoffice callers."""
    return jsonify(
        {
            "default": kroger_pricing.DEFAULT_PRICE_STRATEGY,
            "allowed": list(kroger_pricing.ALLOWED_PRICE_STRATEGIES),
        }
    ), 200


@app.route('/api/kroger/pricing/ingredients', methods=['POST'])
def kroger_price_ingredients():
    """Estimate ingredient pricing using Kroger API (app-local route)."""
    data = request.get_json(silent=True) or {}
    ingredients = data.get('ingredients') or []
    zip_code = (data.get('zipCode') or '').strip()
    requested_strategy = (data.get('priceStrategy') or kroger_pricing.DEFAULT_PRICE_STRATEGY).strip()

    if not isinstance(ingredients, list) or not ingredients:
        return jsonify({"error": "ingredients must be a non-empty list"}), 400
    if not zip_code:
        return jsonify({"error": "zipCode is required"}), 400
    if requested_strategy and requested_strategy.lower() not in kroger_pricing.ALLOWED_PRICE_STRATEGIES:
        return jsonify(
            {
                "error": "Invalid priceStrategy",
                "allowed": list(kroger_pricing.ALLOWED_PRICE_STRATEGIES),
            }
        ), 400

    normalized = [str(i).strip() for i in ingredients if str(i).strip()]
    if not normalized:
        return jsonify({"error": "ingredients must contain at least one non-empty value"}), 400

    try:
        result = kroger_pricing.estimate_ingredient_total(
            normalized,
            zip_code,
            price_strategy=requested_strategy,
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to estimate ingredient pricing: {str(e)}"}), 502



if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
