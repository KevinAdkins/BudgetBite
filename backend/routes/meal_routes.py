from flask import Blueprint, request, jsonify
from models import database
import pull
import time

meal_bp = Blueprint('meal_bp', __name__)

# Maintainer note:
# Search endpoint intentionally checks local DB first (via pull.run_search)
# and only falls back to the external API when missing to keep latency/cost low.

# --- GET Routes (Order matters: specific routes before wildcards) ---

@meal_bp.route('/meals', methods=['GET'])
def get_all_meals():
    """Get all meals from the database."""
    try:
        meals = database.get_all_meals()
        return jsonify({"meals": meals, "count": len(meals)}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch meals: {str(e)}"}), 500


@meal_bp.route('/meals/search', methods=['GET'])
def search_meal():
    """Search for a meal (checks DB first, then API). Must come before /<name> route."""
    meal_name = (request.args.get('name') or '').strip()
    if not meal_name:
        return jsonify({"error": "No meal name provided"}), 400

    # Use the pull module's search logic
    meal = pull.run_search(meal_name)

    if meal:
        return jsonify(meal), 200
    else:
        return jsonify({"error": "Meal not found in database or API"}), 404


@meal_bp.route('/meals/search-by-ingredient', methods=['GET'])
def search_meal_by_ingredient():
    """Search meals by ingredient, with optional full details lookup."""
    ingredient = (request.args.get('ingredient') or '').strip()
    if not ingredient:
        return jsonify({"error": "No ingredient provided"}), 400

    full_details = (request.args.get('full') or '').strip().lower() in {'1', 'true', 'yes'}
    first_only = (request.args.get('first') or '').strip().lower() in {'1', 'true', 'yes'}

    meals = pull.search_by_main_ingredient(
        ingredient=ingredient,
        full_details=full_details,
        first_only=first_only
    )

    if not meals:
        return jsonify({"error": f"No meals found for ingredient '{ingredient}'"}), 404

    if first_only:
        return jsonify({"meal": meals[0], "count": 1}), 200

    return jsonify({"meals": meals, "count": len(meals)}), 200


@meal_bp.route('/meals/<string:name>', methods=['GET'])
def get_meal(name):
    """Get a specific meal by name."""
    meal = database.get_meal_by_name(name)
    if meal:
        return jsonify(meal), 200
    else:
        return jsonify({"error": f"Meal '{name}' not found"}), 404


# --- POST Routes ---

@meal_bp.route('/meals', methods=['POST'])
def create_meal():
    """Manually add a meal to the database."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name'):
            return jsonify({"error": "Meal name is required"}), 400
        
        # Generate an ID if not provided
        if not data.get('id'):
            data['id'] = str(int(time.time() * 1000))

        # Validate/normalize optional pricing fields.
        if data.get('estimated_price') is not None:
            try:
                data['estimated_price'] = round(float(data['estimated_price']), 2)
                if data['estimated_price'] < 0:
                    return jsonify({"error": "estimated_price must be >= 0"}), 400
            except (TypeError, ValueError):
                return jsonify({"error": "estimated_price must be a valid number"}), 400
        elif data.get('ingredients'):
            data['estimated_price'] = pull.estimate_meal_price_from_text(data.get('ingredients'))

        if data.get('estimated_price') is not None:
            data['currency'] = (data.get('currency') or 'USD').upper()
            data['price_source'] = data.get('price_source') or 'estimated'
            data['price_last_updated'] = data.get('price_last_updated') or pull.current_price_timestamp()
        
        database.add_meal(data)
        return jsonify({"message": "Meal added successfully", "meal": data}), 201
    
    except Exception as e:
        return jsonify({"error": f"Failed to create meal: {str(e)}"}), 500


# --- PUT/PATCH Routes ---

@meal_bp.route('/meals/<string:name>', methods=['PUT'])
def update_meal(name):
    """Update a meal's details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Check if meal exists
        existing = database.get_meal_by_name(name)
        if not existing:
            return jsonify({"error": f"Meal '{name}' not found"}), 404
        
        success = database.update_meal(name, data)
        
        if success:
            updated_meal = database.get_meal_by_name(name)
            return jsonify({"message": "Meal updated successfully", "meal": updated_meal}), 200
        else:
            return jsonify({"error": "No valid fields to update"}), 400
    
    except Exception as e:
        return jsonify({"error": f"Failed to update meal: {str(e)}"}), 500


@meal_bp.route('/meals/<string:name>/instructions', methods=['PATCH'])
def update_instructions(name):
    """Update only the instructions for a meal."""
    try:
        data = request.get_json()
        if not data or not data.get('instructions'):
            return jsonify({"error": "Instructions field is required"}), 400
        
        success = database.update_meal_instructions(name, data['instructions'])
        
        if success:
            return jsonify({"message": "Instructions updated successfully"}), 200
        else:
            return jsonify({"error": f"Meal '{name}' not found"}), 404
    
    except Exception as e:
        return jsonify({"error": f"Failed to update instructions: {str(e)}"}), 500


# --- DELETE Routes ---

@meal_bp.route('/meals/<string:name>', methods=['DELETE'])
def delete_meal(name):
    """Delete a meal by name."""
    try:
        success = database.delete_meal_by_name(name)
        
        if success:
            return jsonify({"message": f"Meal '{name}' deleted successfully"}), 200
        else:
            return jsonify({"error": f"Meal '{name}' not found"}), 404
    
    except Exception as e:
        return jsonify({"error": f"Failed to delete meal: {str(e)}"}), 500
