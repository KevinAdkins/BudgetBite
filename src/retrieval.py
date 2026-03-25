"""
Retrieval Script - Connects Ingredient Extractor to Backend API
Reads ingredients from JSON output and queries the BudgetBite backend API at localhost:5000
"""

import json
import sys
import requests
from pathlib import Path
from typing import List, Dict, Any

# Backend API configuration
BACKEND_URL = "http://127.0.0.1:5001"


def load_ingredients(json_file: str) -> List[Dict[str, Any]]:
    """Load ingredients from the JSON output file."""
    print(f"📖 Loading ingredients from: {json_file}")
    
    if not Path(json_file).exists():
        raise FileNotFoundError(f"Ingredients file not found: {json_file}")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Handle different JSON structures from various extractors
    ingredients = []
    
    if 'ingredients' in data:
        if isinstance(data['ingredients'], list):
            ingredients = data['ingredients']
        else:
            ingredients = [data['ingredients']]
    elif 'raw_output' in data:
        print("⚠️  Warning: Raw output detected, attempting to parse...")
        # For LLaVA raw output, we'll extract what we can
        ingredients = [{"name": "mixed items", "notes": data['raw_output'][:100]}]
    else:
        ingredients = [data]  # Assume entire structure is ingredient data
    
    print(f"✅ Loaded {len(ingredients)} ingredients\n")
    return ingredients


def query_backend_api(endpoint: str) -> Dict[str, Any]:
    """Query the backend API."""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to backend at {BACKEND_URL}")
        print("   Make sure the Flask server is running: python backend/app.py")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return {}


def search_meals_by_ingredient(ingredient_name: str) -> Dict[str, Any]:
    """Search for meals that match a specific ingredient."""
    print(f"🔍 Searching for meals with: {ingredient_name}")
    return query_backend_api(f"/api/meals/search?name={ingredient_name}")


def get_all_meals() -> List[Dict[str, Any]]:
    """Retrieve all meals from the database."""
    print("📚 Fetching all meals from database...")
    result = query_backend_api("/api/meals")
    return result.get('meals', [])


def match_ingredients_to_meals(ingredients: List[Dict], meals: List[Dict]) -> List[Dict]:
    """Match extracted ingredients to available meals."""
    print("\n🔄 Matching ingredients to recipes...\n")
    
    # Extract ingredient names (handle different JSON structures)
    ingredient_names = set()
    for ing in ingredients:
        if isinstance(ing, dict):
            name = ing.get('name', '')
            if name:
                ingredient_names.add(name.lower())
        elif isinstance(ing, str):
            ingredient_names.add(ing.lower())
    
    print(f"Detected ingredients: {', '.join(sorted(ingredient_names))}\n")
    
    matches = []
    
    for meal in meals:
        if not meal.get('ingredients'):
            continue
        
        # Parse meal ingredients (comma-separated string)
        meal_ingredients = [
            ing.strip().lower() 
            for ing in meal['ingredients'].split(',')
        ]
        
        # Calculate match score
        matching_count = 0
        for detected in ingredient_names:
            for meal_ing in meal_ingredients:
                if detected in meal_ing or meal_ing in detected:
                    matching_count += 1
                    break
        
        if matching_count > 0:
            match_percentage = (matching_count / len(meal_ingredients)) * 100
            matches.append({
                'meal': meal,
                'matching_count': matching_count,
                'total_ingredients': len(meal_ingredients),
                'match_percentage': match_percentage,
                'missing_count': len(meal_ingredients) - matching_count
            })
    
    # Sort by match percentage
    matches.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return matches


def save_matches(matches: List[Dict], output_file: str = "matched_recipes.json"):
    """Save matched recipes to a JSON file."""
    print(f"\n💾 Saving matches to: {output_file}")
    
    # Simplify the structure for easier consumption
    simplified = []
    for match in matches:
        meal = match['meal']
        simplified.append({
            'name': meal['name'],
            'category': meal.get('category', 'unknown'),
            'ingredients': meal.get('ingredients', ''),
            'instructions': meal.get('instructions', ''),
            'match_score': {
                'percentage': round(match['match_percentage'], 1),
                'matching': match['matching_count'],
                'total': match['total_ingredients'],
                'missing': match['missing_count']
            }
        })
    
    with open(output_file, 'w') as f:
        json.dump(simplified, f, indent=2)
    
    print(f"✅ Saved {len(simplified)} matched recipes\n")
    return output_file


def display_top_matches(matches: List[Dict], top_n: int = 5):
    """Display the top matching recipes."""
    if not matches:
        print("❌ No matching recipes found")
        return
    
    print(f"\n{'='*70}")
    print(f"🍽️  TOP {min(top_n, len(matches))} MATCHING RECIPES")
    print(f"{'='*70}\n")
    
    for i, match in enumerate(matches[:top_n], 1):
        meal = match['meal']
        print(f"{i}. {meal['name'].upper()}")
        print(f"   Category: {meal.get('category', 'N/A')}")
        print(f"   Match: {match['matching_count']}/{match['total_ingredients']} ingredients "
              f"({match['match_percentage']:.0f}%)")
        print(f"   Missing: {match['missing_count']} ingredients")
        print()


def main():
    """Main execution function."""
    print("="*70)
    print("🍽️  BUDGETBITE RECIPE RETRIEVAL SYSTEM")
    print("="*70)
    print()
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python src/retrieval.py <ingredients_json_file> [output_file]")
        print("\nExample:")
        print("  python src/retrieval.py ingredients.json matched_recipes.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "matched_recipes.json"
    
    # Step 1: Load ingredients
    ingredients = load_ingredients(input_file)
    
    # Step 2: Get all meals from backend
    meals = get_all_meals()
    
    if not meals:
        print("❌ No meals found in database. Run: python backend/seed.py")
        sys.exit(1)
    
    print(f"✅ Retrieved {len(meals)} meals from database\n")
    
    # Step 3: Match ingredients to meals
    matches = match_ingredients_to_meals(ingredients, meals)
    
    # Step 4: Display results
    display_top_matches(matches, top_n=5)
    
    # Step 5: Save to file
    save_matches(matches, output_file)
    
    print(f"{'='*70}")
    print(f"✅ Retrieval complete! Results saved to: {output_file}")
    print(f"{'='*70}\n")
    
    return output_file


if __name__ == "__main__":
    main()
