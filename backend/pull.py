import sqlite3
import requests
import logging
from datetime import datetime, timezone

from models.database import get_db_connection

API_TIMEOUT = 10


def _now_utc_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def current_price_timestamp():
    """Public helper for consistent UTC timestamp formatting."""
    return _now_utc_iso()


def _estimate_ingredient_cost(ingredient_text):
    """Very lightweight heuristic per ingredient line (USD)."""
    text = (ingredient_text or "").lower()
    if not text:
        return 0.0

    price_map = {
        "chicken": 3.50,
        "beef": 4.00,
        "steak": 4.50,
        "lamb": 4.50,
        "fish": 3.75,
        "shrimp": 4.00,
        "prawn": 4.00,
        "salmon": 4.50,
        "egg": 0.35,
        "milk": 1.25,
        "butter": 1.80,
        "cheese": 2.25,
        "flour": 0.90,
        "rice": 0.90,
        "pasta": 1.20,
        "noodle": 1.20,
        "bread": 1.75,
        "tomato": 0.90,
        "onion": 0.60,
        "garlic": 0.45,
        "potato": 0.80,
        "pepper": 0.70,
        "oil": 0.80,
        "sugar": 0.65,
        "cream": 1.75,
        "yogurt": 1.25,
        "lemon": 0.60,
    }

    for keyword, cost in price_map.items():
        if keyword in text:
            return cost

    # Fallback for pantry/unknown items.
    return 1.00


def estimate_meal_price(ingredients):
    """Estimate total price from a list of ingredient strings."""
    if not ingredients:
        return None
    total = sum(_estimate_ingredient_cost(item) for item in ingredients)
    return round(total, 2)


def estimate_meal_price_from_text(ingredients_text):
    """Estimate price from a comma-separated ingredients string."""
    if not ingredients_text:
        return None
    ingredients = [part.strip() for part in ingredients_text.split(",") if part.strip()]
    if not ingredients:
        return None
    return estimate_meal_price(ingredients)

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
                thumbnail TEXT,
                estimated_price REAL,
                currency TEXT DEFAULT 'USD',
                price_source TEXT,
                price_last_updated TEXT
            )
        ''')

        # Handle additive schema migrations safely.
        existing_columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(meals)").fetchall()
        }
        migration_columns = [
            ("ingredients", "TEXT"),
            ("estimated_price", "REAL"),
            ("currency", "TEXT DEFAULT 'USD'"),
            ("price_source", "TEXT"),
            ("price_last_updated", "TEXT"),
        ]
        for column_name, column_definition in migration_columns:
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE meals ADD COLUMN {column_name} {column_definition}"
                )

        # Backfill estimates for historical records that have ingredients but no price.
        meals_needing_prices = cursor.execute(
            """
            SELECT id, ingredients
            FROM meals
            WHERE estimated_price IS NULL
              AND ingredients IS NOT NULL
              AND TRIM(ingredients) != ''
            """
        ).fetchall()

        for meal in meals_needing_prices:
            estimated_price = estimate_meal_price_from_text(meal["ingredients"])
            if estimated_price is None:
                continue
            cursor.execute(
                """
                UPDATE meals
                SET estimated_price = ?,
                    currency = COALESCE(currency, 'USD'),
                    price_source = COALESCE(price_source, 'estimated'),
                    price_last_updated = COALESCE(price_last_updated, ?)
                WHERE id = ?
                """,
                (estimated_price, _now_utc_iso(), meal["id"]),
            )
        
        conn.commit()

def format_meal_data(meal_json):
    """Helper to turn messy API JSON into a clean dictionary."""
    ingredients = []
    for i in range(1, 21):
        ing = meal_json.get(f'strIngredient{i}')
        meas = meal_json.get(f'strMeasure{i}')
        if ing and ing.strip():
            ingredients.append(f"{meas} {ing}".strip())

    estimated_price = estimate_meal_price(ingredients)
    return {
        "id": meal_json.get('idMeal'),
        "name": meal_json.get('strMeal', '').lower(),
        "category": meal_json.get('strCategory'),
        "instructions": meal_json.get('strInstructions'),
        "ingredients": ", ".join(ingredients),
        "thumbnail": meal_json.get('strMealThumb'),
        "estimated_price": estimated_price,
        "currency": "USD",
        "price_source": "estimated",
        "price_last_updated": _now_utc_iso(),
    }

def save_to_db(meal_data):
    """Saves clean data to SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO meals (
                id, name, category, instructions, ingredients, thumbnail,
                estimated_price, currency, price_source, price_last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            meal_data['id'],
            meal_data['name'],
            meal_data['category'],
            meal_data['instructions'],
            meal_data['ingredients'],
            meal_data['thumbnail'],
            meal_data.get('estimated_price'),
            meal_data.get('currency', 'USD'),
            meal_data.get('price_source', 'estimated'),
            meal_data.get('price_last_updated', _now_utc_iso()),
        ))
        conn.commit()

def run_search(meal_query):
    """Logic for searching a specific meal."""
    init_db()
    query = (meal_query or "").strip().lower()
    if not query:
        return None

    # 1. Check DB first
    with get_db_connection() as conn:
        existing = conn.execute("SELECT * FROM meals WHERE name = ?", (query,)).fetchone()
        if existing:
            return dict(existing)

    # 2. Fetch from API if missing
    res = None
    try:
        url = "https://www.themealdb.com/api/json/v1/1/search.php"
        response = requests.get(url, params={"s": query}, timeout=API_TIMEOUT)
        response.raise_for_status()
        res = response.json()
    except requests.RequestException as e:
        logging.warning("API request failed for meal '%s': %s", query, e)
        return None

    if res and res.get('meals'):
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


def get_full_meal_by_id(meal_id: str):
    """Fetch full meal details from TheMealDB by meal ID."""
    lookup_id = (meal_id or "").strip()
    if not lookup_id:
        return None

    try:
        url = "https://www.themealdb.com/api/json/v1/1/lookup.php"
        response = requests.get(url, params={"i": lookup_id}, timeout=API_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return None

    meals = payload.get("meals") or []
    if not meals:
        return None

    meal = meals[0]

    # Cache the important fields in local DB for faster subsequent lookup.
    try:
        init_db()
        save_to_db(format_meal_data(meal))
    except Exception:
        pass

    return meal


def search_by_main_ingredient(ingredient: str, full_details: bool = False, first_only: bool = False):
    """
    Search meals by a main ingredient.

    - full_details=False: returns `filter.php` meal summaries.
    - full_details=True: expands each result via `lookup.php` for full meal objects.
    - first_only=True: only returns the first match (summary or full details based on full_details).
    """
    ingredient_query = (ingredient or "").strip()
    if not ingredient_query:
        return []

    try:
        url = "https://www.themealdb.com/api/json/v1/1/filter.php"
        response = requests.get(url, params={"i": ingredient_query}, timeout=API_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return []

    meals = payload.get("meals") or []
    if not meals:
        return []

    if first_only:
        meals = meals[:1]

    if not full_details:
        return meals

    full_meals = []
    for meal in meals:
        meal_id = meal.get("idMeal")
        detailed = get_full_meal_by_id(meal_id)
        if detailed:
            full_meals.append(detailed)

    return full_meals