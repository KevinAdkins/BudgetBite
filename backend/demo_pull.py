import sqlite3
import requests
import os
from dotenv import load_dotenv

# 1. Configuration & Setup
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY") 
DB_PATH = os.path.join("backend", "data", "demo.db")

# --- SAMPLE MODE SETTINGS ---
# Using a public API that doesn't need a key to test your "plumbing"
SAMPLE_URL = "https://jsonplaceholder.typicode.com/posts"
# REAL_URL = "https://food-calories-and-macros.p.rapidapi.com/v1/nutrition"

def get_db_connection():
    """Ensures the directory exists and connects to SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Creates the table structure if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Keeping your original columns for the final schema
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

def fetch_and_save_sample(food_query):
    """Pulls sample data and maps it to your nutrition columns for testing."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step A: Local Check
    cursor.execute("SELECT * FROM food_items WHERE name = ?", (food_query.lower(),))
    existing_item = cursor.fetchone()

    if existing_item:
        print(f"✅ Found '{food_query}' in local database. Skipping API call.")
        conn.close()
        return existing_item

    # Step B: Pulling from the sample API
    print(f"🔍 '{food_query}' not found. Fetching sample data...")
    try:
        response = requests.get(SAMPLE_URL)
        response.raise_for_status()
        data = response.json()

        # Since this is a test, we just grab one sample and "pretend" it's food
        sample_item = data[0]
        
        # Mapping sample data to your food columns
        # In the real demo, you'll use item.get('calories'), etc.
        mock_food_name = food_query.lower()
        mock_calories = 250.0  # Placeholder values
        mock_protein = 15.5
        mock_fat = 8.0
        mock_carbs = 30.0

        # Step C: Save to SQLite
        cursor.execute('''
            INSERT OR REPLACE INTO food_items (name, calories, protein_g, fat_g, carbs_g)
            VALUES (?, ?, ?, ?, ?)
        ''', (mock_food_name, mock_calories, mock_protein, mock_fat, mock_carbs))
        
        conn.commit()
        print(f"💾 Successfully saved '{mock_food_name}' (Sample Mode) to SQLite.")
        return mock_food_name

    except Exception as e:
        print(f"❌ Error during sample pull: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    item_to_find = input("Enter a food item to test: ").strip()
    fetch_and_save_sample(item_to_find)