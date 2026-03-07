"""
Recipe Generator - Uses matched recipes from backend to generate new recipe suggestions
Takes matched_recipes.json as input and generates creative recipes using Gemini AI
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

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


def generate_recipe(matched_recipes: List[Dict]) -> str:
    """Generate a new recipe based on matched recipes from database."""
    
    if not matched_recipes:
        raise ValueError("No matched recipes provided")
    
    print("🤖 Generating creative recipe using AI...\n")
    
    # Get top recipes and available ingredients
    top_recipes = matched_recipes[:3]
    available_ingredients = extract_available_ingredients(matched_recipes[:5])
    
    # Format context
    recipes_context = format_recipes_for_prompt(top_recipes)
    ingredients_list = "\n".join([f"  • {ing}" for ing in available_ingredients[:15]])
    
    RECIPE_GENERATION_PROMPT = """You are a creative chef and recipe developer.

TASK: Create ONE delicious, practical recipe based on the available ingredients and similar recipes from our database.

RULES:
1. Use ONLY ingredients from the "Available Ingredients" list
2. The recipes from our database are for INSPIRATION ONLY - create something new
3. Focus on the highest-matching recipe's style and techniques
4. Keep it simple and achievable for home cooks
5. Provide clear, step-by-step instructions
6. You may assume salt, pepper, and basic cooking oil are available
7. Do NOT add ingredients not in the available list

OUTPUT FORMAT:
Recipe Name: [Creative name]
Category: [e.g., Main Course, Side Dish, etc.]
Prep Time: [estimated time]
Servings: [number of servings]

Ingredients:
• [ingredient 1 with quantity]
• [ingredient 2 with quantity]
...

Instructions:
1. [Step 1]
2. [Step 2]
...

Chef's Notes:
[Any helpful tips or variations]
"""

    prompt_content = f"""
Here are the top matching recipes from our database:
{recipes_context}

Available Ingredients:
{ingredients_list}

Please create a new recipe using these ingredients, inspired by the database recipes above.
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
        
        if response.text is None:
            raise ValueError("Recipe generation returned no response")
        
        generated_recipe = response.text.strip()
        return generated_recipe
        
    except Exception as e:
        print(f"❌ Error generating recipe: {e}")
        raise


def save_generated_recipe(recipe_text: str, output_file: str = "generated_recipe.txt"):
    """Save the generated recipe to a file."""
    print(f"\n💾 Saving generated recipe to: {output_file}")
    
    with open(output_file, 'w') as f:
        f.write(recipe_text)
    
    print(f"✅ Recipe saved successfully\n")
    return output_file


def display_recipe(recipe_text: str):
    """Display the generated recipe in a nice format."""
    print("\n" + "="*70)
    print("🍽️  GENERATED RECIPE")
    print("="*70 + "\n")
    print(recipe_text)
    print("\n" + "="*70 + "\n")


def main():
    """Main execution function."""
    print("="*70)
    print("🍳 BUDGETBITE RECIPE GENERATOR")
    print("="*70)
    print()
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python src/recipe_generator.py <matched_recipes_json> [output_file]")
        print("\nExample:")
        print("  python src/recipe_generator.py matched_recipes.json generated_recipe.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "generated_recipe.txt"
    
    # Step 1: Load matched recipes
    matched_recipes = load_matched_recipes(input_file)
    
    if not matched_recipes:
        print("❌ No matched recipes found. Run retrieval.py first.")
        sys.exit(1)
    
    # Step 2: Generate new recipe
    recipe_text = generate_recipe(matched_recipes)
    
    # Step 3: Display recipe
    display_recipe(recipe_text)
    
    # Step 4: Save to file
    save_generated_recipe(recipe_text, output_file)
    
    print(f"{'='*70}")
    print(f"✅ Recipe generation complete!")
    print(f"{'='*70}\n")
    
    return output_file


if __name__ == "__main__":
    main()