"""
Recipe Generator - Uses matched recipes from backend to generate new recipe suggestions
Takes matched_recipes.json as input and generates creative recipes using Gemini AI.
"""

import json
import sys
import re
import os
from pathlib import Path
from typing import List, Dict
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Gemini client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def load_matched_recipes(json_file: str) -> List[Dict]:
    """Load matched recipes from retrieval output."""
    print(f"📖 Loading matched recipes from: {json_file}")
    
    if not Path(json_file).exists():
        raise FileNotFoundError(f"Matched recipes file not found: {json_file}")
    
    with open(json_file, 'r') as f:
        recipes = json.load(f)
    
    print(f"✅ Loaded {len(recipes)} matched recipes\n")
    return recipes

def format_recipes_for_prompt(recipes: List[Dict], max_recipes: int = 3) -> str:
    """Format the top matched recipes for the AI prompt."""
    recipe_text = ""
    for i, recipe in enumerate(recipes[:max_recipes], 1):
        recipe_text += f"\n{i}. {recipe['name'].upper()}\n"
        recipe_text += f"   Category: {recipe['category']}\n"
        recipe_text += f"   Match Score: {recipe['match_score']['percentage']}%\n"
        recipe_text += f"   Ingredients: {recipe['ingredients']}\n"
        recipe_text += f"   Instructions: {recipe['instructions'][:200]}...\n"
    return recipe_text

def extract_available_ingredients(recipes: List[Dict]) -> List[str]:
    """Extract all unique ingredients from matched recipes."""
    ingredients = set()
    for recipe in recipes:
        ing_list = recipe.get('ingredients', '').split(',')
        for ing in ing_list:
            ing_clean = ing.strip().lower()
            if ing_clean:
                ingredients.add(ing_clean)
    return sorted(list(ingredients))

def generate_recipe(matched_recipes: List[Dict], budget_limit: float = 15.00) -> str:
    """Generate a new recipe and check if it fits the budget."""
    
    if not matched_recipes:
        raise ValueError("No matched recipes provided")
    
    print(f"🤖 Generating creative recipe (Budget Limit: ${budget_limit:.2f})...\n")
    
    top_recipes = matched_recipes[:3]
    available_ingredients = extract_available_ingredients(matched_recipes[:5])
    
    recipes_context = format_recipes_for_prompt(top_recipes)
    ingredients_list = "\n".join([f"  • {ing}" for ing in available_ingredients[:15]])
    
    RECIPE_GENERATION_PROMPT = f"""You are a creative chef and recipe developer.

TASK: Create ONE delicious, practical recipe based on available ingredients.

RULES:
1. Use ONLY ingredients from the "Available Ingredients" list.
2. Estimate the "Total Estimated Cost" in USD for the whole meal.
3. You may assume salt, pepper, and basic cooking oil are available ($0.00 cost).
4. Do NOT add ingredients not in the list.

OUTPUT FORMAT:
Recipe Name: [Name]
Total Estimated Cost: $[Amount]
Category: [Category]
Prep Time: [Time]
Servings: [Number]

Ingredients:
• [List]

Instructions:
1. [Steps]

Chef's Notes:
[Tips]
"""

    prompt_content = f"""
Here are the top matching recipes:
{recipes_context}

Available Ingredients:
{ingredients_list}

Please create a new recipe and estimate the cost.
"""

    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            config=types.GenerateContentConfig(
                system_instruction=RECIPE_GENERATION_PROMPT,
                response_mime_type='text/plain',
            ),
            contents=[prompt_content]
        )
        
        recipe_text = response.text.strip()
        
        # --- BUDGET CHECK LOGIC ---
        # Search for "$DD.CC" in the AI output
        cost_match = re.search(r"Total Estimated Cost: \$(\d+\.?\d*)", recipe_text)
        
        if cost_match:
            estimated_cost = float(cost_match.group(1))
            
            # THE IF-ELSE STATEMENT
            if estimated_cost <= budget_limit:
                status_header = f"✅ BUDGET-FRIENDLY: This meal costs ${estimated_cost:.2f} (Under ${budget_limit:.2f})\n"
                print(f"💰 Result: Within budget.")
            else:
                status_header = f"⚠️ PREMIUM SELECTION: This meal costs ${estimated_cost:.2f} (Exceeds ${budget_limit:.2f})\n"
                print(f"⚠️ Result: Over budget.")
        else:
            status_header = "❓ BUDGET STATUS: Unknown (Cost not detected)\n"

        return status_header + "-"*30 + "\n" + recipe_text
        
    except Exception as e:
        print(f"❌ Error generating recipe: {e}")
        raise

def save_generated_recipe(recipe_text: str, output_file: str = "generated_recipe.txt"):
    """Save the generated recipe to a file."""
    print(f"\n💾 Saving to: {output_file}")
    with open(output_file, 'w') as f:
        f.write(recipe_text)
    print(f"✅ Recipe saved successfully\n")

def display_recipe(recipe_text: str):
    """Display the generated recipe."""
    print("\n" + "="*70)
    print("🍽️  GENERATED RECIPE RESULTS")
    print("="*70 + "\n")
    print(recipe_text)
    print("\n" + "="*70 + "\n")

def main():
    """Main execution function."""
    print("="*70)
    print("🍳 BUDGETBITE RECIPE GENERATOR")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("Usage: python src/recipe_generator.py <matched_recipes_json> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "generated_recipe.txt"
    
    matched_recipes = load_matched_recipes(input_file)
    
    # You can change the budget_limit value here
    recipe_text = generate_recipe(matched_recipes, budget_limit=12.50)
    
    display_recipe(recipe_text)
    save_generated_recipe(recipe_text, output_file)
    
    print(f"✅ Generation complete!")
    return output_file

if __name__ == "__main__":
    main()