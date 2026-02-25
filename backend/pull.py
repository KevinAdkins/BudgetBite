import sqlite3
import requests
import os
from dotenv import load_dotenv

# 1. Load the Key from your .env file
load_dotenv()
# IMPORTANT: This must match the name BEFORE the '=' in your .env file
API_KEY = os.getenv("RAPIDAPI_KEY") 

# 2. This is the actual Request URL for the nutrition data
REQUEST_URL = "https://food-calories-and-macros.p.rapidapi.com/v1/nutrition"
DB_PATH = "backend/data/nutrition.db"

def pull_data_to_sqlite(food_query):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "food-calories-and-macros.p.rapidapi.com"
    }
    params = {"query": food_query}

    try:
        # 3. Make the request to the correct endpoint
        response = requests.get(REQUEST_URL, headers=headers, params=params)
        
        # This will tell us if the key or URL is wrong before it crashes
        print(f"DEBUG: Response Status: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()

        # 4. Connect to your database folder
        conn = sqlite3.connect(DB_PATH)
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

        # 5. Insert data and print output for confirmation
        if not data:
            print(f"No results found for: {food_query}")
            return

        for item in data:
            cursor.execute('''
                INSERT OR REPLACE INTO food_items (name, calories, protein_g, fat_g, carbs_g)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['name'], item['calories'], item['protein_g'], 
                  item.get('fat_total_g', 0), item.get('carbohydrates_total_g', 0)))
            print(f"Output: Saved {item['name']} ({item['calories']} cal)")

        conn.commit()
        conn.close()
        print(f"--- Database Update Complete for: {food_query} ---")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    item = input("Enter a food item to save to your DB: ")
    pull_data_to_sqlite(item)