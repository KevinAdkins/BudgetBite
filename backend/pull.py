import sqlite3
import requests
import os
from dotenv import load_dotenv

# 1. Load the Key from your .env file
load_dotenv()
API_KEY = os.getenv("X-RapidAPI-Key")
REQUEST_URL = "https://rapidapi.com"
DB_PATH = "backend/data/nutrition.db"

def pull_data_to_sqlite(food_query):
    # 2. Setup the headers and parameters
    # If using RapidAPI, ensure these header names match your documentation
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "food-calories-and-macros.p.rapidapi.com"
    }
    params = {"query": food_query}

    try:
        # 3. Make the request
        response = requests.get(REQUEST_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # 4. Connect to your database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create table if it doesn't exist
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

        # 5. Insert data
        for item in data:
            cursor.execute('''
                INSERT OR REPLACE INTO food_items (name, calories, protein_g, fat_g, carbs_g)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['name'], item['calories'], item['protein_g'], 
                  item.get('fat_total_g', 0), item.get('carbohydrates_total_g', 0)))

        conn.commit()
        conn.close()
        print(f"Successfully saved data for: {food_query}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    item = input("Enter a food item to save to your DB: ")
    pull_data_to_sqlite(item)