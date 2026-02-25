import sqlite3
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_KEY = os.getenv("FOOD_API_KEY")
DB_DIR = "backend/data"
DB_PATH = os.path.join(DB_DIR, "nutrition.db")
API_URL = "https://api.api-ninjas.com/v1/nutrition?query="

def setup_environment():
    """Ensure the database directory exists."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"Created directory: {DB_DIR}")

def pull_nutrition_data(food_query):
    setup_environment()
    
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(API_URL + food_query, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Added 'last_updated' for senior project documentation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                calories REAL,
                protein_g REAL,
                fat_g REAL,
                carbs_g REAL,
                last_updated DATETIME
            )
        ''')

        for item in data:
            cursor.execute('''
                INSERT OR REPLACE INTO food_items 
                (name, calories, protein_g, fat_g, carbs_g, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item['name'], item['calories'], item['protein_g'], 
                item['fat_total_g'], item['carbohydrates_total_g'],
                datetime.now()
            ))

        conn.commit()
        conn.close()
        print(f"Stored {len(data)} items for '{food_query}'")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    food = input("What food should we pull? ")
    pull_nutrition_data(food)