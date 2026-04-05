import sqlite3
import os
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