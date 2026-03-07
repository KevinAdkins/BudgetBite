# Take in recipes from the database and generate a recipe suggesting using AI
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Define strict schema - only food items allowed
class Ingredient(BaseModel):
    name: str
    quantity: str | None  # e.g. "2 cups", "1 tbsp"
    unit: str | None      # normalized unit if detectable
    category: str         # e.g. "vegetable", "protein", "dairy", "spice"
    confidence: float     # 0.0 to 1.0 - LLM rates its own certainty

class IngredientList(BaseModel):
    ingredients: list[Ingredient]
    non_food_items_detected: bool  # flag if image contains non-food items

with open('foodImages/burger-ingredients.jpg', 'rb') as f:
    image_bytes = f.read()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM_PROMPT = """You are a food ingredient extraction specialist.

RULES (strictly enforced):
1. Extract ONLY edible food ingredients visible in the image
2. IGNORE all non-food items (utensils, containers, packaging, hands, etc.)
3. Use standard culinary names (e.g. "scallion" not "green onion stem")
4. If you cannot confidently identify a food item, skip it
5. Do NOT infer ingredients that are not visually present
6. Quantities should reflect what is visible, not recipe amounts
7. Assign a confidence score (0.0-1.0) based on how certain you are of the identification
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
    ]
)

if response.text is None:
    raise ValueError("Model returned no text response")
result = IngredientList.model_validate_json(response.text)

print(f"Non-food items detected: {result.non_food_items_detected}\n")

# After extraction, filter out low confidence items
CONFIDENCE_THRESHOLD = 0.7
validated_ingredients = [
    ing for ing in result.ingredients
    if ing.confidence >= CONFIDENCE_THRESHOLD
]

print(f"Extracted {len(result.ingredients)} ingredients, {len(validated_ingredients)} with confidence >= {CONFIDENCE_THRESHOLD}\n")

for ing in result.ingredients:
    qty = f"{ing.quantity} {ing.unit}".strip() if ing.quantity else "unknown qty"
    confidence_icon = "✓" if ing.confidence >= CONFIDENCE_THRESHOLD else "✗"
    print(f"{confidence_icon} {ing.name} ({ing.category}): {qty} [confidence: {ing.confidence:.2f}]")