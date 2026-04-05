"""
Ingredient Extractor - Extract ingredients from fridge/pantry images using Gemini AI
Outputs structured JSON for use in the recipe pipeline
"""

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys
import json
from pathlib import Path

load_dotenv()  # Load environment variables from .env file


# Define strict schema - only food items allowed
class Ingredient(BaseModel):
    name: str
    quantity: str | None  # e.g. "2 cups", "1 tbsp"
    unit: str | None      # normalized unit if detectable
    category: str         # e.g. "vegetable", "protein", "dairy", "spice"


class IngredientList(BaseModel):
    ingredients: list[Ingredient]
    non_food_items_detected: bool  # flag if image contains non-food items


def extract_ingredients(image_path: str, budget: str = "less than $25") -> IngredientList:
    """Extract ingredients from an image using Gemini Vision API."""
    
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    print(f"🔍 Analyzing image: {image_path}")
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    SYSTEM_PROMPT = """You are a food ingredient extraction specialist. Budget constraint: {budget}

RULES (strictly enforced):
1. Extract ONLY edible food ingredients visible in the image
2. IGNORE all non-food items (utensils, containers, packaging, hands, etc.)
3. Use standard culinary names (e.g. "scallion" not "green onion stem")
4. If you cannot confidently identify a food item, skip it
5. Do NOT infer ingredients that are not visually present
6. Quantities should reflect what is visible, not recipe amounts
7. Keep the budget constraint in mind when suggesting recipes
"""

    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type='application/json',
            response_schema=IngredientList,
        ),
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
            'Extract only food ingredients visible in this image. Be conservative — if unsure, exclude it.'
        ]
    )

    if response.text is None:
        raise ValueError("Model returned no text response")
    
    result = IngredientList.model_validate_json(response.text)
    return result


def save_to_json(result: IngredientList, output_file: str):
    """Save extracted ingredients to JSON file."""
    print(f"💾 Saving to: {output_file}")
    
    # Convert to dict for JSON serialization
    output_data = {
        "ingredients": [
            {
                "name": ing.name,
                "quantity": ing.quantity,
                "unit": ing.unit,
                "category": ing.category
            }
            for ing in result.ingredients
        ],
        "non_food_items_detected": result.non_food_items_detected
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Saved {len(result.ingredients)} ingredients\n")


def display_results(result: IngredientList):
    """Display extracted ingredients in a nice format."""
    print("\n" + "="*70)
    print("🥘  EXTRACTED INGREDIENTS")
    print("="*70 + "\n")
    
    print(f"Non-food items detected: {result.non_food_items_detected}\n")
    
    if result.ingredients:
        for i, ing in enumerate(result.ingredients, 1):
            qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else "some"
            print(f"{i:2d}. {ing.name} ({ing.category}): {qty}")
    else:
        print("No ingredients detected in image")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main execution function."""
    print("="*70)
    print("📸 BUDGETBITE INGREDIENT EXTRACTOR")
    print("="*70)
    print()
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python src/ingredient_extractor.py <image_path> [output_file]")
        print("\nExample:")
        print("  python src/ingredient_extractor.py Nichi-Fridge.jpg ingredients.json")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "ingredients.json"
    
    try:
        # Extract ingredients
        result = extract_ingredients(image_path)
        
        # Display results
        display_results(result)
        
        # Save to JSON
        save_to_json(result, output_file)
        
        print("="*70)
        print("✅ Extraction complete!")
        print("="*70)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

