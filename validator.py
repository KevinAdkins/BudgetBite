"""
Recipe Validation Script
This script validates that generated recipes only use ingredients that were actually detected in the image.

Workflow:
1. Extract ingredients from image (with confidence scores)
2. Generate recipe based on extracted ingredients
3. Parse recipe to identify mentioned ingredients
4. Validate that all recipe ingredients match extracted ingredients
5. Report validation results and discrepancies
"""

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import re
import time
from typing import List, Dict, Set
from backend.pull import run_search 

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

CONFIDENCE_THRESHOLD = 0.7  # Only use ingredients with confidence >= 0.7
IMAGE_PATH = 'foodImages/easy/spaghetti-ingredients.jpg'

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: Ingredient Extraction with Confidence
# ═══════════════════════════════════════════════════════════════════════════

class Ingredient(BaseModel):
    name: str
    quantity: str | None
    unit: str | None
    category: str
    confidence: float  # 0.0 to 1.0 - LLM rates its own certainty

class IngredientList(BaseModel):
    ingredients: list[Ingredient]
    non_food_items_detected: bool

def get_mime_type(image_path: str) -> str:
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".webp": "image/webp",
    }
    return mime_types.get(ext, "image/jpg")

def extract_ingredients(image_path: str, max_retries: int = 3) -> IngredientList: # pyright: ignore[reportReturnType]
    """Extract ingredients from image with confidence scores."""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    EXTRACTION_PROMPT = """You are a food ingredient extraction specialist.
RULES (strictly enforced):
1. Extract ONLY edible food ingredients visible in the image
2. IGNORE all non-food items (utensils, containers, packaging, hands, etc.)
3. Use standard culinary names (e.g. "scallion" not "green onion stem")
4. If you cannot confidently identify a food item, skip it
5. Do NOT infer ingredients that are not visually present
6. Quantities should reflect what is visible, not recipe amounts
7. Assign a confidence score (0.0-1.0) based on how certain you are of the identification
"""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=EXTRACTION_PROMPT,
                    response_mime_type='application/json',
                    response_schema=IngredientList,
                ),
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=get_mime_type(image_path)),
                    'Extract only food ingredients visible in this image with confidence scores. Be conservative — if unsure, exclude it or assign low confidence.'
                ]
            )

            if response.text is None:
                raise ValueError("Extraction returned no response")

            return IngredientList.model_validate_json(response.text)
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"  ⚠ API error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                print(f"  ⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

# ═══════════════════════════════════════════════════════════════════════════
# Step 2: Filter by Confidence
# ═══════════════════════════════════════════════════════════════════════════

def filter_by_confidence(ingredient_list: IngredientList, threshold: float = 0.7) -> List[Ingredient]:
    """Filter out low confidence items."""
    validated_ingredients = [
        ing for ing in ingredient_list.ingredients
        if ing.confidence >= threshold
    ]
    return validated_ingredients

# ═══════════════════════════════════════════════════════════════════════════
# Step 3: Generate Recipe
# ═══════════════════════════════════════════════════════════════════════════

def generate_recipe(ingredients: List[Ingredient], max_retries: int = 3) -> tuple[str,dict | None]: # pyright: ignore[reportReturnType]
    """Generate recipe based on validated ingredients."""
    
    if len(ingredients) == 0:
        raise ValueError("No ingredients with sufficient confidence")

    # Format ingredients for recipe generator
    ingredient_lines = []
    for ing in ingredients:
        qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else ""
        ingredient_lines.append(f"- {qty} {ing.name}".strip())
    
    ingredient_text = "\n".join(ingredient_lines)

    # Get database context
    def get_best_search_term(ingredients: List[Ingredient]) -> str:
        priority = ["protein", "vegetable", "grain"]
        for category in priority:
            match = next((i for i in ingredients if i.category == category), None)
            if match:
                return match.name
        return ingredients[0].name if ingredients else ""

    search_term = get_best_search_term(ingredients)
    meal = run_search(search_term)

    if meal:
        db_context = f"""
Here is a similar recipe from our database for reference:
Name: {meal['name']}
Category: {meal['category']}
Ingredients: {meal['ingredients']}
Instructions: {meal['instructions']}
"""
    else:
        db_context = ""

    RECIPE_PROMPT = """You are a helpful and creative recipe suggestion assistant.
RULES:
1. Suggest one recipe based on the following list of ingredients.
2. Use ONLY the ingredients provided, do not suggest adding any new ingredients.
3. Provide a simple recipe name and a brief description of the dish.
4. Provide a clear list of the ingredients used in the recipe, referencing the provided ingredient list.
5. Provide the steps to prepare the dish, keeping it simple and easy to follow.
6. Use the similar recipe from the database as inspiration, but do not copy it. Focus on the provided ingredients.
7. If the ingredients cannot make a coherent dish, suggest a simple way to combine them.
8. Assume the user has salt and pepper on hand, but do not assume any other ingredients or special equipment.
"""

    for attempt in range(max_retries):
        try:
            recipe_response = client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=RECIPE_PROMPT,
                    response_mime_type='text/plain',
                ),
                contents=[
                    f"Based on the following ingredients, suggest a recipe:\n{ingredient_text}\n and use the recipe for context:\n{db_context}"
                ]
            )

            if recipe_response.text is None:
                raise ValueError("Recipe generation returned no response")

            return recipe_response.text.strip(), meal # type: ignore
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"  ⚠ API error (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
                print(f"  ⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

# ═══════════════════════════════════════════════════════════════════════════
# Step 4: Parse Recipe to Extract Mentioned Ingredients
# ═══════════════════════════════════════════════════════════════════════════

def parse_recipe_ingredients(recipe_text: str, valid_ingredients: List[Ingredient]) -> Dict:
    """
    Parse the recipe to find which ingredients are mentioned.
    Returns a dictionary with matched and unmatched ingredients.
    """
    # Create a set of valid ingredient names (lowercase for matching)
    valid_names = {ing.name.lower() for ing in valid_ingredients}
    
    # Extract ingredient section from recipe (heuristic approach)
    recipe_lower = recipe_text.lower()
    
    # Find ingredients mentioned in the recipe
    mentioned_ingredients = set()
    
    # Look for ingredient names in the recipe text
    for valid_name in valid_names:
        # Check if ingredient name appears in recipe (with word boundaries)
        pattern = r'\b' + re.escape(valid_name) + r'\b'
        if re.search(pattern, recipe_lower):
            mentioned_ingredients.add(valid_name)
    
    # Extract the ingredients section from the recipe text
    ingredients_section = ""
    in_ingredients_section = False
    lines = recipe_text.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        # Detect start of ingredients section
        if 'ingredients' in line_lower and ':' in line:
            in_ingredients_section = True
            continue
        # Detect end of ingredients section (start of instructions)
        if in_ingredients_section and ('instructions' in line_lower or 'steps' in line_lower or 'directions' in line_lower):
            break
        # Collect ingredient lines
        if in_ingredients_section and line.strip():
            ingredients_section += line + "\n"
    
    # Common cooking terms and descriptive words that are NOT ingredients
    cooking_terms = {
        'salt', 'pepper', 'water', 'oil', 'taste', 'optional', 'needed',
        'finely', 'diced', 'chopped', 'minced', 'sliced', 'whole', 'fresh',
        'serve', 'serving', 'serves', 'instructions', 'step', 'steps',
        'heat', 'cook', 'cooking', 'bake', 'baking', 'boil', 'boiling',
        'simmer', 'simmering', 'stirring', 'mixing', 'prepared', 'medium',
        'large', 'small', 'pieces', 'piece', 'cups', 'tablespoons', 'teaspoons',
        'prepare', 'preparation', 'aromatics', 'uniform', 'remove', 'dice',
        'oven', 'stove', 'skillet', 'dish', 'bowl', 'place', 'until',
        'about', 'minutes', 'hours', 'stalks', 'cloves', 'bulbs'
    }
    
    # Look for potential unmatched ingredients in the ingredients section only
    unmatched_ingredients = set()
    
    if ingredients_section:
        # Parse ingredient lines only
        for line in ingredients_section.split('\n'):
            line_clean = re.sub(r'^\*\s*|\s*\*\s*$', '', line)  # Remove markdown bullets
            line_clean = re.sub(r'^\d+\.?\s*', '', line_clean)  # Remove numbered lists
            line_clean = re.sub(r'^\-\s*', '', line_clean)  # Remove dashes
            line_clean = re.sub(r'\(.*?\)', '', line_clean)  # Remove parenthetical notes
            
            words = re.findall(r'\b[a-z]+\b', line_clean.lower())
            
            for word in words:
                # Skip if it's a cooking term, measurement, or too short
                if len(word) <= 3 or word in cooking_terms:
                    continue
                    
                # Skip if it's part of a valid ingredient name
                is_part_of_valid = False
                for valid_name in valid_names:
                    if word in valid_name or valid_name in word:
                        is_part_of_valid = True
                        break
                
                # If not part of valid ingredients and not a common term, flag it
                if not is_part_of_valid:
                    unmatched_ingredients.add(word)
    
    return {
        'mentioned': mentioned_ingredients,
        'unmatched': unmatched_ingredients,
        'valid_names': valid_names
    }

# ═══════════════════════════════════════════════════════════════════════════
# Step 5: Validation and Reporting
# ═══════════════════════════════════════════════════════════════════════════

def validate_recipe(extracted: IngredientList, validated_ingredients: List[Ingredient], 
                    recipe: str) -> Dict:
    """Validate that the recipe only uses ingredients that were detected in the image."""
    
    # Parse recipe to find mentioned ingredients
    parsing_result = parse_recipe_ingredients(recipe, validated_ingredients)
    
    # Calculate validation metrics
    total_extracted = len(extracted.ingredients)
    total_validated = len(validated_ingredients)
    low_confidence_count = total_extracted - total_validated
    mentioned_count = len(parsing_result['mentioned'])
    unmatched_count = len(parsing_result['unmatched'])
    
    validation_passed = unmatched_count == 0
    
    return {
        'passed': validation_passed,
        'total_extracted': total_extracted,
        'total_validated': total_validated,
        'low_confidence_filtered': low_confidence_count,
        'ingredients_mentioned_in_recipe': mentioned_count,
        'unmatched_ingredients': parsing_result['unmatched'],
        'mentioned_ingredients': parsing_result['mentioned'],
        'valid_ingredient_names': parsing_result['valid_names']
    }

# ═══════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("RECIPE VALIDATION SYSTEM")
    print("=" * 80)
    print(f"Image: {IMAGE_PATH}")
    print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print("=" * 80)
    
    # Step 1: Extract ingredients
    print("\n[STEP 1] Extracting ingredients from image...")
    extracted = extract_ingredients(IMAGE_PATH)
    print(f"✓ Extracted {len(extracted.ingredients)} ingredients")
    print(f"  Non-food items detected: {extracted.non_food_items_detected}")
    
    print("\n[ALL EXTRACTED INGREDIENTS]")
    for ing in extracted.ingredients:
        qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else "unknown qty"
        confidence_icon = "✓" if ing.confidence >= CONFIDENCE_THRESHOLD else "✗"
        print(f"  {confidence_icon} {ing.name} ({ing.category}): {qty} [confidence: {ing.confidence:.2f}]")
    
    # Step 2: Filter by confidence
    print(f"\n[STEP 2] Filtering by confidence (>= {CONFIDENCE_THRESHOLD})...")
    validated_ingredients = filter_by_confidence(extracted, CONFIDENCE_THRESHOLD)
    print(f"✓ {len(validated_ingredients)} ingredients passed confidence threshold")
    
    if len(extracted.ingredients) - len(validated_ingredients) > 0:
        print(f"  ⚠ Filtered out {len(extracted.ingredients) - len(validated_ingredients)} low-confidence ingredients")
    
    print("\n[VALIDATED INGREDIENTS]")
    for ing in validated_ingredients:
        qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else "unknown qty"
        print(f"  • {ing.name} ({ing.category}): {qty}")
    
    # Step 3: Generate recipe
    print("\n[STEP 3] Generating recipe...")
    recipe, db_meal = generate_recipe(validated_ingredients)

    if db_meal:
        print("\n[DATABASE REFERENCE MEAL]")
        print("-" * 80)
        print(f"Name: {db_meal['name']}") # type: ignore
        print(f"Category: {db_meal['category']}") # type: ignore
        print(f"Ingredients: {db_meal['ingredients']}") # type: ignore
        print(f"Instructions: {db_meal['instructions']}") # type: ignore
        print("-" * 80)
    else:
        print("\nNo similar meal found in database for additional context.")

    print("✓ Recipe generated")
    
    print("\n[GENERATED RECIPE]")
    print("-" * 80)
    print(recipe)
    print("-" * 80)
    
    # Step 4: Validate recipe
    print("\n[STEP 4] Validating recipe against extracted ingredients...")
    validation_result = validate_recipe(extracted, validated_ingredients, recipe)
    
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print(f"Total Extracted: {validation_result['total_extracted']}")
    print(f"Validated (high confidence): {validation_result['total_validated']}")
    print(f"Filtered (low confidence): {validation_result['low_confidence_filtered']}")
    print(f"Ingredients mentioned in recipe: {validation_result['ingredients_mentioned_in_recipe']}")
    
    if validation_result['passed']:
        print("\n✓✓✓ VALIDATION PASSED ✓✓✓")
        print("All recipe ingredients match the extracted ingredients from the image!")
    else:
        print("\n✗✗✗ VALIDATION FAILED ✗✗✗")
        print(f"Found {len(validation_result['unmatched_ingredients'])} unmatched ingredients in recipe:")
        for unmatched in validation_result['unmatched_ingredients']:
            print(f"  ⚠ {unmatched}")
    
    print("\n[DETAILED ANALYSIS]")
    print(f"Expected ingredients: {', '.join(sorted(validation_result['valid_ingredient_names']))}")
    print(f"Mentioned in recipe: {', '.join(sorted(validation_result['mentioned_ingredients']))}")
    
    unused_ingredients = validation_result['valid_ingredient_names'] - validation_result['mentioned_ingredients']
    if unused_ingredients:
        print(f"\nUnused ingredients: {', '.join(sorted(unused_ingredients))}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
