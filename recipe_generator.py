from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Shared client instance for both extraction and generation steps
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# ── Step 1: Ingredient Extraction ──────────────────────────────────────────
class Ingredient(BaseModel):
    name: str
    quantity: str | None
    unit: str | None
    category: str

class IngredientList(BaseModel):
    ingredients: list[Ingredient]
    non_food_items_detected: bool

with open('Nichi-Fridge.jpg', 'rb') as f:
    image_bytes = f.read()

EXTRACTION_PROMPT = """You are a food ingredient extraction specialist.
RULES (strictly enforced):
1. Extract ONLY edible food ingredients visible in the image
2. IGNORE all non-food items (utensils, containers, packaging, hands, etc.)
3. Use standard culinary names (e.g. "scallion" not "green onion stem")
4. If you cannot confidently identify a food item, skip it
5. Do NOT infer ingredients that are not visually present
6. Quantities should reflect what is visible, not recipe amounts
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
        'Extract only food ingredients visible in this image. Be conservative — if unsure, exclude it.'
    ]
)

if extraction_response.text is None:
    raise ValueError("Extraction returned no response")

extracted = IngredientList.model_validate_json(extraction_response.text)

print(f"Non-food items detected: {extracted.non_food_items_detected}\n")
for ing in extracted.ingredients:
    qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else "unknown qty"
    print(f"  - {ing.name} ({ing.category}): {qty}")

# ── Step 2: Format ingredients for recipe generator ────────────────────────
ingredient_lines = []
for ing in extracted.ingredients:
    qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else ""
    ingredient_lines.append(f"- {qty} {ing.name}".strip())

ingredient_text = "\n".join(ingredient_lines)

# ── Step 3: Recipe Generation ──────────────────────────────────────────────
RECIPE_PROMPT = """You are a helpful and creative recipe suggestion assistant.
RULES:
1. Suggest one recipe based on the following list of ingredients.
2. Use only the ingredients provided, do not suggest adding any new ingredients.
3. Provide a simple recipe name and a brief description of the dish.
4. Provide a clear list of the ingredients used in the recipe, referencing the provided ingredient list.
5. Provide the steps to prepare the dish, keeping it simple and easy to follow.
6. If the ingredients cannot make a coherent dish, suggest a simple way to combine them.
"""

recipe_response = client.models.generate_content(
    model='gemini-3-flash-preview',
    config=types.GenerateContentConfig(
        system_instruction=RECIPE_PROMPT,
        response_mime_type='text/plain',
    ),
    contents=[
        f"Based on the following ingredients, suggest a recipe:\n{ingredient_text}"
    ]
)

if recipe_response.text is None:
    raise ValueError("Recipe generation returned no response")

print("\nRecipe Suggestion:\n")
print(recipe_response.text.strip())