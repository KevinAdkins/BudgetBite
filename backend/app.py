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
from google import genai
from google.genai import types
from recipe_generator import generate_recipe
from pricing import extract_ingredients_from_recipe_text, filter_pricing_ingredients

# Initialize Gemini client for recipe generation
genai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

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

def generate_recipe_with_llm(ingredients: list, matched_recipes: list) -> dict:
    """Generate a practical recipe using Gemini LLM based on matched recipes."""
    
    # Format ingredients
    ingredient_names = [ing['name'] for ing in ingredients]
    ingredients_list = "\n".join([f"  • {name}" for name in ingredient_names])
    
    # Format top matched recipes for context
    recipes_context = ""
    for i, match in enumerate(matched_recipes[:3], 1):
        meal = match['meal']
        recipes_context += f"\n{i}. {meal['name'].upper()}\n"
        recipes_context += f"   Category: {meal.get('category', 'Unknown')}\n"
        recipes_context += f"   Match Score: {match['match_percentage']:.1f}%\n"
    
    RECIPE_GENERATION_PROMPT = """You are a home cook creating EXTREMELY SIMPLE, BEGINNER-FRIENDLY recipes.

TASK: Create ONE super simple recipe that anyone can make in 10 minutes or less.

CRITICAL COMPATIBILITY CHECK:
- Before creating a recipe, verify the ingredients can make a REAL, APPETIZING dish that people actually eat
- If ingredients are incompatible or would create an unappetizing combination, respond with EXACTLY: "INCOMPATIBLE_INGREDIENTS"
- Examples of BAD combinations to REFUSE: vanilla yogurt + savory items, sweet + savory mismatch, random unrelated items
- Only create recipes people would actually want to eat!

STRICT RULES:
1. Use ONLY ingredients from the "Available Ingredients" list - NO EXCEPTIONS
2. Keep it EXTREMELY SIMPLE - only basic techniques:
   - Scramble (eggs)
   - Mix together (salads, wraps)
   - Heat/warm (microwave, stovetop)
   - Spread/assemble (sandwiches, wraps)
3. Maximum 5 steps - fewer is better
4. NO cooking terminology (sauté, blanch, etc.) - use plain English
5. You may assume common kitchen staples: salt, pepper, oil, butter, mayo, ketchup, mustard, soy sauce
6. Recipe must be a REAL dish people have heard of (Egg Wrap, Yogurt Bowl, Grilled Cheese, etc.)
7. Think: "What would a college student make in 5 minutes?"

OUTPUT FORMAT (follow exactly):
Recipe Name: [Ultra-simple name like "Egg and Cheese Wrap" or "Strawberry Yogurt Bowl"]
Category: [Breakfast/Lunch/Dinner/Snack]
Prep Time: [5-10 minutes]
Servings: [1-2]

Ingredients:
- [ingredient from list] - [simple amount like "2 eggs" or "handful"]
- [ingredient from list] - [simple amount]

Instructions:
1. [One simple action in plain English]
2. [One simple action]
3. [One simple action]

Quick Tip: [One sentence tip]"""

    prompt_content = f"""
Available Ingredients:
{ingredients_list}

Similar recipes from database (for inspiration only):
{recipes_context}

Create a practical, budget-friendly recipe using ONLY the available ingredients.
"""
    
    try:
        response = genai_client.models.generate_content(
            model='gemini-3-flash-preview',
            config=types.GenerateContentConfig(
                system_instruction=RECIPE_GENERATION_PROMPT,
                response_mime_type='text/plain',
                temperature=0.7,
            ),
            contents=[prompt_content]
        )
        
        if not response.text:
            raise ValueError("No response from LLM")
        
        # Check if LLM refused due to incompatible ingredients
        recipe_text = response.text.strip()
        if "INCOMPATIBLE_INGREDIENTS" in recipe_text:
            print("⚠️ LLM determined ingredients are incompatible")
            return None  # Signal incompatibility to caller
        
        # Parse the generated recipe
        lines = recipe_text.split('\n')
        
        # Extract name and category
        recipe_name = "Generated Recipe"
        category = "Main Course"
        for line in lines[:10]:
            if line.startswith("Recipe Name:"):
                recipe_name = line.replace("Recipe Name:", "").strip()
            elif line.startswith("Category:"):
                category = line.replace("Category:", "").strip()
        
        # Calculate accurate match percentage
        # Extract recipe ingredient names (between "Ingredients:" and "Instructions:")
        recipe_ingredients = []
        in_ingredients_section = False
        for line in lines:
            if "Ingredients:" in line:
                in_ingredients_section = True
                continue
            if "Instructions:" in line or "Quick Tip:" in line:
                break
            if in_ingredients_section and line.strip().startswith('-'):
                # Extract ingredient name (before the dash description)
                ing_text = line.strip()[1:].strip()  # Remove leading dash
                # Get first word or two (the ingredient name)
                ing_name = ing_text.split('-')[0].split('(')[0].strip().lower()
                # Remove quantity words
                for word in ing_name.split():
                    if not any(c.isdigit() for c in word) and len(word) > 2:
                        recipe_ingredients.append(word)
                        break
        
        # Common household items that don't count against match percentage
        # These are assumed to be available in most kitchens
        HOUSEHOLD_STAPLES = {
            'salt', 'pepper', 'oil', 'water', 'butter', 'sugar',
            'mayo', 'mayonnaise', 'ketchup', 'mustard', 'soy sauce',
            'vinegar', 'hot sauce', 'sriracha'
        }
        
        # Count ingredients from detected list (exclude household staples)
        detected_names = {name.lower() for name in ingredient_names}
        recipe_ingredients_filtered = [ing for ing in recipe_ingredients if ing not in HOUSEHOLD_STAPLES]
        
        matching_count = 0
        for recipe_ing in recipe_ingredients_filtered:
            # Check if this ingredient or part of it matches detected ingredients
            if any(recipe_ing in detected or detected in recipe_ing for detected in detected_names):
                matching_count += 1
        
        # Calculate match percentage
        total_recipe_ingredients = len(recipe_ingredients_filtered)
        if total_recipe_ingredients > 0:
            match_percentage = (matching_count / total_recipe_ingredients) * 100
        else:
            match_percentage = 100.0  # If no ingredients, default to 100%
        
        return {
            "name": recipe_name,
            "category": category,
            "instructions": recipe_text,
            "ingredients": ", ".join(ingredient_names),
            "generated": True,
            "match_percentage": match_percentage,
            "matching_count": matching_count,
            "total_count": total_recipe_ingredients
        }
        
    except Exception as e:
        print(f"❌ Error generating recipe: {e}")
        # Fallback to first matched recipe if generation fails
        if matched_recipes:
            meal = matched_recipes[0]['meal']
            return {
                "name": meal['name'],
                "category": meal.get('category', 'unknown'),
                "ingredients": meal.get('ingredients', ''),
                "instructions": meal.get('instructions', ''),
                "generated": False,
                "error": str(e)
            }
        raise

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
    """
    Analyze fridge image and return recipe matches with validation and budget checking.
    Implements complete flow per UML diagrams (valid-flow, refusal-flow, budget-flow).
    """
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

        # Step 3a: Extract ingredients via Gemini Vision API (with budget context)
        result = extract_ingredients(tmp_path, budget_description)
        os.unlink(tmp_path)

        # Step 4: Structure ingredients
        ingredients = [
            {
                "name": ing.name,
                "quantity": ing.quantity,
                "unit": ing.unit,
                "category": ing.category
            }
            for ing in result.ingredients
        ]

        # REFUSAL CHECK 1: Insufficient Ingredients (< 3 minimum)
        # Per UML: valid-flow.drawio and refusal-flow.drawio Type 1
        MINIMUM_INGREDIENTS = 3
        if len(ingredients) < MINIMUM_INGREDIENTS:
            return jsonify({
                "status": "refusal",
                "reason": "insufficient_ingredients",
                "details": {
                    "count": len(ingredients),
                    "required": MINIMUM_INGREDIENTS
                },
                "ingredients": ingredients,
                "suggestions": [
                    "Add more ingredients to your fridge",
                    "Take a clearer photo with better lighting",
                    "Enter ingredients manually"
                ]
            }), 400

        # Step 6: Query Recipe Database and match ingredients
        # Database matches used for INSPIRATION only (not gatekeeping)
        meals = get_all_meals()
        matches = match_ingredients_to_meals(ingredients, meals)
        
        # Log matches for debugging
        if len(matches) > 0:
            print(f"📊 Found {len(matches)} database matches (using for inspiration)")
            print(f"   Top match: {matches[0]['meal']['name']} ({matches[0]['match_percentage']:.1f}%)")
        else:
            print("📊 No database matches found (LLM will create recipe from scratch)")

        # Step 7: Generate NEW recipe using LLM (not database recipe)
        # LLM can generate recipes even with 0 database matches or low quality matches
        # Database matches only provide inspiration/context
        print("🤖 Generating recipe with Gemini LLM...")
        generated_recipe = generate_recipe_with_llm(ingredients, matches)
        
        # REFUSAL CHECK 2: Incompatible Ingredients
        # If LLM determines ingredients can't make a good recipe
        if generated_recipe is None:
            ingredient_names = [ing['name'] for ing in ingredients]
            return jsonify({
                "status": "refusal",
                "reason": "incompatible_ingredients",
                "ingredients": ingredients,
                "detected_items": ingredient_names,
                "suggestions": [
                    "These ingredients don't combine well into a tasty recipe",
                    "Try adding complementary ingredients",
                    "Take a photo with more compatible food items",
                    "Consider making separate dishes with these ingredients"
                ]
            }), 400
        
        # Format as single recipe response
        # Show actual match percentage: how many recipe ingredients came from the image
        # (excluding household staples like salt, pepper, oil)
        top_matches = [{
            "name": generated_recipe['name'],
            "category": generated_recipe['category'],
            "ingredients": generated_recipe['ingredients'],
            "instructions": generated_recipe['instructions'],
            "match_score": {
                "percentage": round(generated_recipe.get('match_percentage', 100.0), 1),
                "matching": generated_recipe.get('matching_count', len(ingredients)),
                "total": generated_recipe.get('total_count', len(ingredients)),
                "missing": max(0, generated_recipe.get('total_count', len(ingredients)) - generated_recipe.get('matching_count', len(ingredients)))
            },
            "generated": generated_recipe.get('generated', False)
        }]

        # Step 8: Parse generated recipe ingredients and estimate pricing
        # Integration from main branch for pricing functionality
        # TEMPORARILY DISABLED - No Kroger API key configured
        generated_recipe_pricing = None
        generated_recipe_pricing_error = "Pricing temporarily disabled (no Kroger API key)"
        generated_recipe_pricing_ingredients = []
        
        # Uncomment below when Kroger API credentials are available
        # if generated_recipe and generated_recipe.get('instructions'):
        #     try:
        #         # Extract ingredients from generated recipe text for pricing
        #         parsed_recipe_ingredients = extract_ingredients_from_recipe_text(generated_recipe['instructions'])
        #         generated_recipe_pricing_ingredients = filter_pricing_ingredients(parsed_recipe_ingredients)

        #         if generated_recipe_pricing_ingredients:
        #             from kroger_pricing import KrogerPricingClient
        #             kroger_pricing = KrogerPricingClient()
        #             requested_strategy = data.get('pricing_strategy', 'cheapest')
        #             zip_code = data.get('zip_code', '90210')
        #             
        #             generated_recipe_pricing = kroger_pricing.estimate_ingredient_total(
        #                 generated_recipe_pricing_ingredients,
        #                 zip_code,
        #                 price_strategy=requested_strategy,
        #             )
        #     except Exception as pricing_error:
        #         generated_recipe_pricing_error = str(pricing_error)
        #         print(f"⚠️ Pricing estimation failed: {pricing_error}")

        # SUCCESS: Return complete response
        return jsonify({
            "status": "success",
            "ingredients": ingredients,
            "non_food_items_detected": result.non_food_items_detected,
            "matched_recipes": top_matches,
            "generated_recipe": generated_recipe.get('instructions') if generated_recipe else None,
            "generated_recipe_pricing_ingredients": generated_recipe_pricing_ingredients,
            "generated_recipe_pricing": generated_recipe_pricing,
            "generated_recipe_pricing_error": generated_recipe_pricing_error,
        }), 200

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/kroger/pricing/strategies', methods=['GET'])
def kroger_pricing_strategies():
    """Expose allowed pricing strategy values for frontend/backoffice callers."""
    from kroger_pricing import KrogerPricingClient
    kroger_pricing = KrogerPricingClient()
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
