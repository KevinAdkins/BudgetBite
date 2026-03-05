# Take in recipes from the database and generate a recipe suggesting using AI
from google import genai
from google.genai import types
from pydantic import BaseModel

# Define strict schema - only food items allowed
class Ingredient(BaseModel):
    name: str
    quantity: str | None  # e.g. "2 cups", "1 tbsp"
    unit: str | None      # normalized unit if detectable
    category: str         # e.g. "vegetable", "protein", "dairy", "spice"

class IngredientList(BaseModel):
    ingredients: list[Ingredient]
    non_food_items_detected: bool  # flag if image contains non-food items

with open('Nichi-Fridge.jpg', 'rb') as f:
    image_bytes = f.read()

client = genai.Client()

SYSTEM_PROMPT = """You are a food ingredient extraction specialist.

RULES (strictly enforced):
1. Extract ONLY edible food ingredients visible in the image
2. IGNORE all non-food items (utensils, containers, packaging, hands, etc.)
3. Use standard culinary names (e.g. "scallion" not "green onion stem")
4. If you cannot confidently identify a food item, skip it
5. Do NOT infer ingredients that are not visually present
6. Quantities should reflect what is visible, not recipe amounts
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

print(f"Non-food items detected: {result.non_food_items_detected}\n")
for ing in result.ingredients:
    qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else "unknown qty"
    print(f"- {ing.name} ({ing.category}): {qty}")