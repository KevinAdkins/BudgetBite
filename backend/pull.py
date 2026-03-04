import sqlite3
import requests
import os
from dotenv import load_dotenv

# 1. Configuration & Setup
load_dotenv()
# TheMealDB has a free public tier using '1' as the API key
API_KEY = "1" 
DB_PATH = os.path.join("backend", "data", "meals.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Updated schema to match MealDB data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            category TEXT,
            instructions TEXT,
            thumbnail TEXT
        )
    ''') 
    conn.commit()
    conn.close()

def fetch_and_save_meal(meal_query):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step A: Check local DB
    cursor.execute("SELECT * FROM meals WHERE name = ?", (meal_query.lower(),))
    existing_item = cursor.fetchone()

    if existing_item:
        print(f"✅ Found '{meal_query}' in local database.")
        conn.close()
        return existing_item

    # Step B: Call TheMealDB API
    print(f"🔍 '{meal_query}' not found. Fetching from API...")
    
    # URL for searching by name
    request_url = f"https://www.themealdb.com/api/json/v1/{API_KEY}/search.php"
    params = {"s": meal_query}

    try:
        response = requests.get(request_url, params=params)
        response.raise_for_status()
        data = response.json()

        # TheMealDB returns {"meals": [ ... ]} or {"meals": null}
        if not data['meals']:
            print(f"❌ No meals found for: {meal_query}")
            return None

        # Step C: Save the first result
        meal = data['meals'][0] 
        
        cursor.execute('''
            INSERT OR REPLACE INTO meals (id, name, category, instructions, thumbnail)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            meal.get('idMeal'),
            meal.get('strMeal').lower(), 
            meal.get('strCategory'), 
            meal.get('strInstructions'), 
            meal.get('strMealThumb')
        ))
        
        conn.commit()
        print(f"💾 Successfully saved {meal.get('strMeal')} to SQLite.")
        return meal

    except Exception as e:
        print(f"❌ Error during API pull: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    meal_to_find = input("Enter a meal name (e.g., Arrabiata): ").strip()
    fetch_and_save_meal(meal_to_find)