from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import pull
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

load_dotenv()
app = Flask(__name__)
CORS(app)
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
            "POST /api/analyze": "Analyze fridge image"
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        # Decode base64 image to temp file
        image_data = base64.b64decode(data['image'])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(image_data)
            tmp_path = tmp.name

        # Extract ingredients via Gemini
        result = extract_ingredients(tmp_path)
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

        # Match to recipes in DB
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

        return jsonify({
            "ingredients": ingredients,
            "non_food_items_detected": result.non_food_items_detected,
            "matched_recipes": top_matches
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
