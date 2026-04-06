from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import pull
import kroger_pricing
from routes.meal_routes import meal_bp
from routes.pricing_routes import pricing_bp
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

load_dotenv()
app = Flask(__name__)

# Enable CORS for frontned access
CORS(app)
# Maintainer note:
# Keep DB initialization before blueprint registration so first request does not
# race table creation when running in a fresh environment.
pull.init_db()

app.register_blueprint(meal_bp, url_prefix='/api')
app.register_blueprint(pricing_bp, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({
        "message": "BudgetBite API",
        "version": "1.0",
        "endpoints": {
            "GET /api/meals": "Get all meals",
            "GET /api/meals/<name>": "Get specific meal",
            "GET /api/meals/search?name=<name>": "Search for meal",
            "POST /api/analyze": "Analyze fridge image",
            "POST /api/pricing/ingredients": "Estimate ingredient pricing via blueprint route",
            "POST /api/kroger/pricing/ingredients": "Estimate ingredient pricing via app route",
            "GET /api/kroger/pricing/strategies": "List allowed Kroger pricing strategies"
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        budget_tier = data.get('budget_tier', 'tier1')
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

        # Step 2: Match to recipes in DB
        meals = get_all_meals()
        matches = match_ingredients_to_meals(ingredients, meals)

        # Return top 5 matches
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

        # Step 3: Generate a new recipe using extracted ingredients + matched recipes.
        extracted_ingredient_names = [
            ing["name"].strip().lower()
            for ing in ingredients
            if isinstance(ing.get("name"), str) and ing["name"].strip()
        ]

        generated_recipe = None
        recipe_generation_error = None
        if top_matches and extracted_ingredient_names:
            try:
                generated_recipe = generate_recipe(top_matches, extracted_ingredient_names)
            except Exception as recipe_error:
                recipe_generation_error = str(recipe_error)

        # Step 4: Parse generated recipe ingredients and estimate pricing.
        generated_recipe_pricing = None
        generated_recipe_pricing_error = None
        generated_recipe_pricing_ingredients = []
        if generated_recipe:
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

        return jsonify({
            "ingredients": ingredients,
            "non_food_items_detected": result.non_food_items_detected,
            "matched_recipes": top_matches,
            "generated_recipe": generated_recipe,
            "recipe_generation_error": recipe_generation_error,
            "generated_recipe_pricing_ingredients": generated_recipe_pricing_ingredients,
            "generated_recipe_pricing": generated_recipe_pricing,
            "generated_recipe_pricing_error": generated_recipe_pricing_error,
        })

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
