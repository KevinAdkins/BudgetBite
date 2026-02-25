import os
import time
import sqlite3
from flask import Blueprint, request, jsonify

recipe_bp = Blueprint('recipe_bp', __name__)

# --- DATABASE CONFIGURATION ---
DB_PATH = os.path.join("backend", "data", "demo.db")

def save_recipe_to_db(ingredients, recipe_data):
    """Saves the generated recipe and ingredients list to SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create a table for saved recipes if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                ingredients TEXT,
                instructions TEXT,
                cost_estimate TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert the new recipe results
        cursor.execute('''
            INSERT INTO saved_recipes (title, ingredients, instructions, cost_estimate)
            VALUES (?, ?, ?, ?)
        ''', (
            recipe_data['title'], 
            ", ".join(ingredients), # Converts list to a string
            recipe_data['instructions'], 
            recipe_data['cost_estimate']
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")


def fetch_all_recipes():
    """Reads all saved recipes from SQLite for quick verification."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure the table exists even if no recipes were saved yet
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            ingredients TEXT,
            instructions TEXT,
            cost_estimate TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        SELECT id, title, ingredients, instructions, cost_estimate, created_at
        FROM saved_recipes
        ORDER BY created_at DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    # Map rows to a JSON-friendly structure
    return [
        {
            "id": row[0],
            "title": row[1],
            "ingredients": row[2].split(", ") if row[2] else [],
            "instructions": row[3],
            "cost_estimate": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]

# --- AI SERVICE CALLS ---
def run_cv_model(image_path):
    # This simulates your Computer Vision model identifying items
    return ["egg", "rice", "spinach"] 

def run_llm_recipe_gen(ingredients):
    # This generates the budget-friendly recipe
    return {
        "title": "Budget Fried Rice",
        "instructions": "1. Scramble eggs. 2. Add rice and spinach. 3. Season and serve.",
        "cost_estimate": "$2.50"
    }

# --- ROUTES ---
@recipe_bp.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    start_time = time.time()
    
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files['image']
    # Save the temp image in the data folder to keep the root clean
    temp_path = os.path.join("backend", "data", f"temp_{image.filename}")
    image.save(temp_path)

    try:
        # 1. Trigger AI to find ingredients
        ingredients = run_cv_model(temp_path)
        
        if not ingredients:
            return jsonify({"error": "No food ingredients detected."}), 400

        # 2. Privacy: Delete image immediately after processing
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # 3. Trigger LLM to generate recipe
        recipe = run_llm_recipe_gen(ingredients)

        # 4. Save the result for the user
        save_recipe_to_db(ingredients, recipe)

        total_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "ingredients": ingredients,
            "recipe": recipe,
            "processing_time": f"{total_time:.2f}s"
        }), 200

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500


@recipe_bp.route('/recipes', methods=['POST'])
def create_recipe():
    # Manual insert endpoint for testing and quick data entry
    data = request.get_json(silent=True) or {}

    title = (data.get('title') or '').strip()
    ingredients = data.get('ingredients') or []
    instructions = (data.get('instructions') or '').strip()
    cost_estimate = (data.get('cost_estimate') or '').strip()

    if not title:
        return jsonify({"error": "title is required"}), 400
    if not instructions:
        return jsonify({"error": "instructions are required"}), 400
    if not isinstance(ingredients, list) or not all(isinstance(i, str) for i in ingredients):
        return jsonify({"error": "ingredients must be a list of strings"}), 400

    save_recipe_to_db(ingredients, {
        "title": title,
        "instructions": instructions,
        "cost_estimate": cost_estimate
    })

    return jsonify({"success": True}), 201


@recipe_bp.route('/recipes', methods=['GET'])
def list_recipes():
    # Simple read endpoint to verify inserts from Postman or the frontend
    recipes = fetch_all_recipes()
    return jsonify({"recipes": recipes}), 200