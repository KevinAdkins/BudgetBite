from flask import Flask, request, jsonify
import sqlite3
import pull  # pull.py script

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("backend/data/meals.db")
    conn.row_factory = sqlite3.Row  
    return conn

@app.route('/search', methods=['GET'])
def search_meal():
    meal_name = request.args.get('name')
    if not meal_name:
        return jsonify({"error": "No meal name provided"}), 400

    conn = get_db_connection()
    # 1. Check if we already have it
    meal = conn.execute("SELECT * FROM meals WHERE name LIKE ?", (f"%{meal_name}%",)).fetchone()
    conn.close()

    if meal:
        print(f"--- Found {meal_name} in Database ---")
        return jsonify(dict(meal))

    # 2. If not in DB, trigger the 'pull' logic
    print(f"--- {meal_name} not found. Pulling from API... ---")
    pull.fetch_and_save_meal(meal_name)
    
    # 3. Check DB again after the pull
    conn = get_db_connection()
    meal = conn.execute("SELECT * FROM meals WHERE name LIKE ?", (f"%{meal_name}%",)).fetchone()
    conn.close()

    if meal:
        return jsonify(dict(meal))
    else:
        return jsonify({"error": "Meal not found in API either"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)