"""
Recipe Generator - Uses matched recipes from backend to generate new recipe suggestions
Takes matched_recipes.json as input and generates creative recipes using Gemini AI
"""
from dotenv import load_dotenv
load_dotenv()
import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


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
    """Format top matched recipe metadata for inspiration-only context."""
    recipe_text = ""
    
    for i, recipe in enumerate(recipes[:max_recipes], 1):
        recipe_text += f"\n{i}. {recipe['name'].upper()}\n"
        recipe_text += f"   Category: {recipe['category']}\n"
        recipe_text += f"   Match Score: {recipe['match_score']['percentage']}%\n"
    
    return recipe_text


def load_extracted_ingredients(json_file: str) -> List[str]:
    """Load ingredients detected directly from the input image."""
    if not Path(json_file).exists():
        raise FileNotFoundError(f"Ingredients file not found: {json_file}")

    with open(json_file, 'r') as f:
        data = json.load(f)

    ingredients = data.get('ingredients', [])
    extracted_names = []
    for ing in ingredients:
        if isinstance(ing, dict):
            name = str(ing.get('name', '')).strip().lower()
        else:
            name = str(ing).strip().lower()
        if name:
            extracted_names.append(name)

    unique = []
    seen = set()
    for name in extracted_names:
        if name not in seen:
            seen.add(name)
            unique.append(name)

    return unique


def generate_recipe(matched_recipes: List[Dict], extracted_ingredients: List[str]) -> str:
    """Generate a new recipe based on matched recipes from database."""
    
    if not matched_recipes:
        raise ValueError("No matched recipes provided")
    if not extracted_ingredients:
        raise ValueError("No extracted image ingredients provided")
    
    print("🤖 Generating creative recipe using AI...\n")
    
    # Get top recipes and allowed ingredients from image extraction only.
    top_recipes = matched_recipes[:3]
    available_ingredients = extracted_ingredients
    
    # Format context
    recipes_context = format_recipes_for_prompt(top_recipes)
    ingredients_list = "\n".join([f"  • {ing}" for ing in available_ingredients])
    
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
    
    parser = argparse.ArgumentParser(
        description="Generate a recipe from matched recipes using image-extracted ingredients.",
    )
    parser.add_argument("matched_recipes_json", help="Path to matched_recipes.json")
    parser.add_argument("output_file", nargs="?", default="generated_recipe.txt", help="Output file path")
    parser.add_argument(
        "--ingredients-file",
        default="ingredients.json",
        help="Path to ingredient extractor output JSON (default: ingredients.json)",
    )
    args = parser.parse_args()
    input_file = args.matched_recipes_json
    output_file = args.output_file
    
    # Step 1: Load matched recipes
    matched_recipes = load_matched_recipes(input_file)
    
    if not matched_recipes:
        print("❌ No matched recipes found. Run retrieval.py first.")
        sys.exit(1)

    extracted_ingredients = load_extracted_ingredients(args.ingredients_file)
    if not extracted_ingredients:
        print("❌ No extracted ingredients found. Run ingredient_extractor.py first.")
        sys.exit(1)
    
    # Step 2: Generate new recipe
    recipe_text = generate_recipe(matched_recipes, extracted_ingredients)
    
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
