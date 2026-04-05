import sqlite3
import os
import json
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager

# Shared DB location for backend modules.
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "data", "meals.db")

@contextmanager
def get_db_connection():
    """Return a SQLite connection with dict-like rows and guaranteed cleanup."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# --- READ Operations ---

def get_all_meals():
    """The 'GET' all action - returns all meals from the database."""
    with get_db_connection() as conn:
        meals = conn.execute("SELECT * FROM meals ORDER BY name").fetchall()
    return [dict(meal) for meal in meals]

def get_meal_by_name(name):
    """The 'GET' single action - fetch a specific meal by name."""
    with get_db_connection() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE name = ?", (name.lower(),)).fetchone()
    return dict(meal) if meal else None

def get_meal_by_id(meal_id):
    """Fetch a meal by its ID."""
    with get_db_connection() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
    return dict(meal) if meal else None

# --- CREATE/UPDATE Operations ---

def add_meal(meal_data):
    """The 'POST' action - adds or updates a full meal entry."""
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO meals (
                id, name, category, instructions, ingredients, thumbnail,
                estimated_price, currency, price_source, price_last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            meal_data.get('id'),
            meal_data.get('name', '').lower(),
            meal_data.get('category'),
            meal_data.get('instructions'),
            meal_data.get('ingredients'),
            meal_data.get('thumbnail'),
            meal_data.get('estimated_price'),
            meal_data.get('currency', 'USD'),
            meal_data.get('price_source'),
            meal_data.get('price_last_updated')
        ))
        conn.commit()

def update_meal_instructions(name, instructions):
    """The 'PUT/PATCH' action - update only the instructions field."""
    with get_db_connection() as conn:
        cursor = conn.execute("UPDATE meals SET instructions = ? WHERE name = ?", 
                              (instructions, name.lower()))
        rows_affected = cursor.rowcount
        conn.commit()
    return rows_affected > 0

def update_meal(name, updates):
    """Generic update - allows updating multiple fields at once."""
    valid_fields = [
        'category',
        'instructions',
        'ingredients',
        'thumbnail',
        'estimated_price',
        'currency',
        'price_source',
        'price_last_updated',
    ]
    set_clause = ', '.join([f"{field} = ?" for field in updates.keys() if field in valid_fields])
    values = [updates[field] for field in updates.keys() if field in valid_fields]
    values.append(name.lower())
    
    if not set_clause:
        return False
    
    with get_db_connection() as conn:
        cursor = conn.execute(f"UPDATE meals SET {set_clause} WHERE name = ?", values)
        rows_affected = cursor.rowcount
        conn.commit()
    
    return rows_affected > 0

# --- DELETE Operations ---

def delete_meal_by_name(name):
    """The 'DELETE' action - removes a meal by name."""
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM meals WHERE name = ?", (name.lower(),))
        rows_affected = cursor.rowcount
        conn.commit()
    return rows_affected > 0

def delete_meal_by_id(meal_id):
    """Delete a meal by its ID."""
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
        rows_affected = cursor.rowcount
        conn.commit()
    return rows_affected > 0


# --- Pricing Persistence ---

def _now_utc_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def save_pricing_run(pricing_result, meal_id=None, source="api"):
    """Persist one pricing response and its line items to SQLite."""
    if not isinstance(pricing_result, dict):
        raise ValueError("pricing_result must be a dictionary")

    run_id = str(uuid.uuid4())
    created_at = _now_utc_iso()
    line_items = pricing_result.get("lineItems") or []

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO pricing_runs (
                id, created_at, zip_code, location_id, strategy,
                subtotal, estimated_total, priced_count, requested_count,
                meal_id, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                created_at,
                pricing_result.get("zipCode"),
                pricing_result.get("locationId"),
                pricing_result.get("priceStrategy"),
                pricing_result.get("subtotal"),
                pricing_result.get("estimatedTotal"),
                pricing_result.get("pricedCount"),
                pricing_result.get("requestedCount"),
                meal_id,
                source,
            ),
        )

        for item in line_items:
            product = item.get("product") or {}
            sample_prices = item.get("samplePrices")
            conn.execute(
                """
                INSERT INTO pricing_line_items (
                    run_id, ingredient, search_term, found, price, reason,
                    product_description, product_brand, product_upc, sample_prices_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    item.get("ingredient"),
                    item.get("searchTerm"),
                    1 if item.get("found") else 0,
                    item.get("price"),
                    item.get("reason"),
                    product.get("description"),
                    product.get("brand"),
                    product.get("upc"),
                    json.dumps(sample_prices) if sample_prices is not None else None,
                ),
            )

        conn.commit()

    return run_id