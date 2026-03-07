"""""
Recipe Generator
Extracts ingredients from a food image and suggests a recipe using Gemini 3 Flash Preview.

Workflow:
1. Extract ingredients from image 
2. Normalize and filter ingredients
3. Generate recipe based on filtered ingredients
"""""
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from backend.pull import search_multiple
# Load environment variables from .env file
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

# Shared client instance for both extraction and generation steps
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

#Image to be processed - Change this path to test with different images in the foodImages folder
img = 'foodImages/easy/burger.jpg'

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: Ingredient Extraction
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

with open(img, 'rb') as f:
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

extraction_response = client.models.generate_content(
    model='gemini-3-flash-preview',
    config=types.GenerateContentConfig(
        system_instruction=EXTRACTION_PROMPT,
        response_mime_type='application/json',
        response_schema=IngredientList,
    ),
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
        types.Part.from_text(text='Extract only food ingredients visible in this image. Be conservative — if unsure, exclude it.'),
    ]
)

if extraction_response.text is None:
    raise ValueError("Extraction returned no response")

extracted = IngredientList.model_validate_json(extraction_response.text)

def validate_extraction(extracted: IngredientList) -> None:
    if len(extracted.ingredients) == 0:
        raise ValueError("No ingredients detected — image may not contain food")

validate_extraction(extracted)

# Filter by confidence threshold
CONFIDENCE_THRESHOLD = 0.7
validated_ingredients = [
    ing for ing in extracted.ingredients
    if ing.confidence >= CONFIDENCE_THRESHOLD
]

if len(validated_ingredients) == 0:
    raise ValueError(f"No ingredients with confidence >= {CONFIDENCE_THRESHOLD}")

print(f"Extracted {len(extracted.ingredients)} ingredients, using {len(validated_ingredients)} with confidence >= {CONFIDENCE_THRESHOLD}")
print(f"Non-food items detected: {extracted.non_food_items_detected}\n")

print("[ALL EXTRACTED INGREDIENTS]")
for ing in extracted.ingredients:
    qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else ""
    print(f"  {qty} {ing.name} ({ing.category}) - confidence: {ing.confidence}")

def get_best_search_term(ingredients: list[Ingredient]) -> str:
    priority = ["protein", "vegetable", "grain"]
    for category in priority:
        match = next((i for i in ingredients if i.category == category), None)
        if match:
            return match.name
    return ingredients[0].name if ingredients else ""

search_term = get_best_search_term(validated_ingredients)
# ── Step 2: Format ingredients for recipe generator ────────────────────────
ingredient_lines = []
for ing in validated_ingredients:
    qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else ""
    ingredient_lines.append(f"- {qty} {ing.name}".strip())

ingredient_text = "\n".join(ingredient_lines)

# ── Step 3: Fetch similar recipe from database for context ─────────────────
# Search using top ingredients from the image
def get_search_terms(ingredients: IngredientList, max_terms=2) -> list[str]:
    priority = ["protein", "vegetable", "grain"]
    terms = []
    for category in priority:
        match = next((i for i in ingredients.ingredients if i.category == category), None)
        if match:
            terms.append(match.name)
    return terms[:max_terms]

search_terms = get_search_terms(extracted)
print(f"Searching database for recipes with: {', '.join(search_terms)}")
meals = search_multiple(search_terms)

# Format all meals as context
def format_db_context(meals: list[dict]) -> str:
    if not meals:
        return ""
    
    context = "Here are similar recipes from our database for reference:\n"
    for i, meal in enumerate(meals, 1):
        context += f"""
Recipe {i}: {meal['name']}
  Category: {meal['category']}
  Ingredients: {meal['ingredients']}
  Instructions: {meal['instructions']}
"""
    return context

db_context = format_db_context(meals)
print(f"Found {len(meals)} reference recipes from database")

# ═══════════════════════════════════════════════════════════════════════════
# Step 4: Generate Recipe
# ═══════════════════════════════════════════════════════════════════════════

RECIPE_PROMPT = """You are a helpful and creative recipe suggestion assistant.
RULES:
1. Suggest one recipe based on the following list of ingredients.
2. Use only the ingredients provided, do not suggest adding any new ingredients.
3. Provide a simple recipe name and a brief description of the dish.
4. Provide a clear list of the ingredients used in the recipe, referencing the provided ingredient list.
5. Provide the steps to prepare the dish, keeping it simple and easy to follow.
6. Use the similar recipe from the database as inspiration, but do not copy it. Focus on the provided ingredients.
7. If the ingredients cannot make a coherent dish, suggest a simple way to combine them.
8. Assume the user has salt and pepper on hand, but do not assume any other ingredients or special equipment.
"""

recipe_response = client.models.generate_content(
    model='gemini-3-flash-preview',
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

print("\nRecipe Suggestion:\n")
print(recipe_response.text.strip())