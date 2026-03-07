import sqlite3
import requests
import os
from contextlib import contextmanager

# Centralized paths
BACKEND_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BACKEND_DIR, "data", "meals.db")
API_TIMEOUT = 10

@contextmanager
def get_db_connection():
    """Context manager for database connections - ensures proper cleanup."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Creates the meals table if it does not already exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                instructions TEXT,
                ingredients TEXT,
                thumbnail TEXT
            )
        ''')
        
        # Handle schema migration: add ingredients column if it doesn't exist
        try:
            cursor.execute("SELECT ingredients FROM meals LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE meals ADD COLUMN ingredients TEXT")
        
        conn.commit()

def format_meal_data(meal_json):
    """Helper to turn messy API JSON into a clean dictionary."""
    ingredients = []
    for i in range(1, 21):
        ing = meal_json.get(f'strIngredient{i}')
        meas = meal_json.get(f'strMeasure{i}')
        if ing and ing.strip():
            ingredients.append(f"{meas} {ing}".strip())

    return {
        "id": meal_json.get('idMeal'),
        "name": meal_json.get('strMeal', '').lower(),
        "category": meal_json.get('strCategory'),
        "instructions": meal_json.get('strInstructions'),
        "ingredients": ", ".join(ingredients),
        "thumbnail": meal_json.get('strMealThumb')
    }

def save_to_db(meal_data):
    """Saves clean data to SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO meals (id, name, category, instructions, ingredients, thumbnail)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (meal_data['id'], meal_data['name'], meal_data['category'],
              meal_data['instructions'], meal_data['ingredients'], meal_data['thumbnail']))
        conn.commit()

def run_search(meal_query):
    """Logic for searching a specific meal."""
    init_db()
    query = (meal_query or "").strip().lower()
    if not query:
        return None

    # 1. Check DB first
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        existing = conn.execute("SELECT * FROM meals WHERE name = ?", (query,)).fetchone()
        if existing:
            return dict(existing)

    # 2. Fetch from API if missing
    try:
        url = "https://www.themealdb.com/api/json/v1/1/search.php"
        response = requests.get(url, params={"s": query}, timeout=API_TIMEOUT)
        response.raise_for_status()
        res = response.json()
    except requests.RequestException as e:
        import logging
        logging.warning(f"API request failed for meal '{query}': {e}")

    if res.get('meals'):
        meal_data = format_meal_data(res['meals'][0])
        save_to_db(meal_data)
        return meal_data

    return None

def search_multiple(queries: list[str]) -> list[dict]:
    """Search for multiple meals and return all results."""
    results = []
    for query in queries:
        meal = run_search(query)
        if meal:
            results.append(meal)
    return results

def fetch_and_save_meal(meal_query):
    """Backward-compatible wrapper around run_search."""
    return run_search(meal_query)