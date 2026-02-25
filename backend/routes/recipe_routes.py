import os
import time
from flask import Blueprint, request, jsonify

recipe_bp = Blueprint('recipe_bp', __name__)

# Simulated AI Service Calls (Replace these with your actual model logic)
def run_cv_model(image_path):
    # Success check: System must identify 75% of items
    # In production, this would call your Computer Vision model [cite: 18]
    return ["egg", "rice", "spinach"] 

def run_llm_recipe_gen(ingredients):
    # Must respect "Budget-Friendly" constraints
    return {
        "title": "Budget Fried Rice",
        "instructions": "1. Scramble eggs. 2. Add rice and spinach. 3. Season and serve.",
        "cost_estimate": "$2.50"
    }

@recipe_bp.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    start_time = time.time()
    
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files['image']
    temp_path = f"temp_{image.filename}"
    image.save(temp_path)

    try:
        # 1. Trigger CV Model [cite: 39]
        ingredients = run_cv_model(temp_path)
        
        # Edge Case: Handle no food detected
        if not ingredients:
            return jsonify({"error": "No food ingredients detected. Please try again."}), 400

        # 2. Privacy: Delete image immediately after processing
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # 3. Trigger LLM [cite: 22, 23]
        recipe = run_llm_recipe_gen(ingredients)

        # 4. Performance Check: Must be under 10 seconds
        total_time = time.time() - start_time
        if total_time > 10:
            print(f"Warning: Processing took {total_time:.2f} seconds")

        # 5. TODO: Alvaro (Database) will help integrate the SQLite save here [cite: 40, 77]
        
        return jsonify({
            "success": True,
            "ingredients": ingredients,
            "recipe": recipe,
            "processing_time": f"{total_time:.2f}s"
        }), 200

    except Exception as e:
        # Fail safely and display error message
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500