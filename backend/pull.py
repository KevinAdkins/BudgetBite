import sqlite3
import requests
import os
from dotenv import load_dotenv

# 1. Configuration & Setup
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY") 
# Shared DB for both recipes and nutrition data
DB_PATH = os.path.join("backend", "data", "demo.db")
# Ensure the specific endpoint URL is used, not just the website domain
REQUEST_URL = "https://food-calories-and-macros.p.rapidapi.com/v1/nutrition"

def get_db_connection():
    """Ensures the directory exists and connects to SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Creates the table structure if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            calories REAL,
            protein_g REAL,
            fat_g REAL,
            carbs_g REAL
        )
    ''') 
    conn.commit()
    conn.close()

def fetch_and_save_food(food_query):
    """Checks local DB first, then pulls from API if missing."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step A: Check if we already have this data locally
    cursor.execute("SELECT * FROM food_items WHERE name = ?", (food_query.lower(),))
    existing_item = cursor.fetchone()

    if existing_item:
        print(f"✅ Found '{food_query}' in local database. Skipping API call.") # cite: 1.1
        conn.close()
        return existing_item

    # Step B: If not found, call the API
    print(f"🔍 '{food_query}' not found. Fetching from API...")
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "food-calories-and-macros.p.rapidapi.com"
    }
    params = {"query": food_query}

    try:
        response = requests.get(REQUEST_URL, headers=headers, params=params)
        response.raise_for_status() # cite: 1.1
        data = response.json() # cite: 1.1

        if not data:
            print(f"❌ No results found for: {food_query}")
            return None

        # Step C: Save the first result to the database
        item = data[0] # Assuming the first result is the best match
        cursor.execute('''
            INSERT OR REPLACE INTO food_items (name, calories, protein_g, fat_g, carbs_g)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            item.get('name').lower(), 
            item.get('calories'), 
            item.get('protein'), 
            item.get('fat'), 
            item.get('carbohydrates')
        )) # cite: 1.1
        
        conn.commit()
        print(f"💾 Successfully saved {item.get('name')} to SQLite.")
        return item

    except Exception as e:
        print(f"❌ Error during API pull: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    item_to_find = input("Enter a food item: ").strip()
    fetch_and_save_food(item_to_find)