"""
Kroger pricing utility.

This script is intentionally focused on one job: estimate ingredient cost
through the backend Kroger pricing endpoint.
Usage examples:
Priceing tier listing:
  python pricing.py --ingredients "eggs,milk,bread"
Pricing from ingredient_extractor output:
  python pricing.py --ingredients-json path/to/ingredients.json
Expensive item handling:
  python pricing.py --ingredients "saffron,vanilla bean,black truffle"
"""

import argparse
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv


def estimate_kroger_cost(
    ingredient_names: list[str],
    zip_code: str,
    price_strategy: str = "average_top3",
    api_url: str = "http://127.0.0.1:5001/api/pricing/ingredients",
    request_timeout: int = 60,
) -> dict | None:
    """Call backend pricing endpoint and return pricing summary."""
    payload = {
        "ingredients": ingredient_names,
        "zipCode": zip_code,
        "priceStrategy": price_strategy,
    }
    try:
        response = requests.post(
            api_url,
            json=payload,
            timeout=request_timeout,
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        print(f"Kroger pricing unavailable: request timed out after {request_timeout}s")
        return None
    except requests.RequestException as exc:
        details = ""
        if hasattr(exc, "response") and exc.response is not None:
            details = f" | response: {exc.response.text}"
        print(f"Kroger pricing unavailable: {exc}{details}")
        return None


def normalize_generated_ingredient(line: str) -> str:
    """Strip bullets and quantity phrases to improve store product matching."""
    text = line.strip()
    text = re.sub(r"^[\u2022\u00b7\*-]\s*", "", text)
    text = re.sub(r"\([^)]*\)", "", text).strip()
    text = re.sub(r"^\*+|\*+$", "", text).strip()
    text = re.sub(
        r"^(ingredients used|ingredients|recipe name|category|prep time|servings|chef's notes|description|steps|preparation steps|instructions|directions)\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # Remove leading quantities like "1", "1/2", "1.5" optionally followed by words.
    text = re.sub(r"^\d+(?:[\./]\d+)?\s+", "", text)
    text = re.sub(r"^\d+\s*[-–]\s*\d+\s+", "", text)
    text = re.sub(
        r"^(?:an?\s+)?(cup|cups|tbsp|tsp|teaspoon|teaspoons|tablespoon|tablespoons|"
        r"oz|ounce|ounces|lb|lbs|pound|pounds|g|kg|ml|l|portion|portions|slice|slices|"
        r"piece|pieces|ring|rings|head|heads|small|medium|large|bowl|bowls|full|half|"
        r"clove|cloves|stalk|stalks|bunch|bunches|can|cans|jar|jars|package|packages|pinch|pinches)\b",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    # Remove trailing prep/detail clauses that are not useful for product search.
    text = re.sub(
        r",?\s*\b(?:very\s+)?(?:finely\s+|roughly\s+)?(minced|chopped|diced|sliced|crushed|grated)\b.*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        r",?\s*\b(?:very\s+)?(finely|roughly|thinly|thin|fine|coarsely|coarse|lightly|just)\b\s+"
        r"(minced|chopped|diced|sliced|crushed|grated|shredded|julienned|crumbled|peeled|cubed|halved|quartered)\b.*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        r",?\s*(?:very\s+)?(?:finely|roughly|thinly|thin|fine|coarsely|coarse|lightly|just)?\s*"
        r"(minced|chopped|diced|sliced|crushed|grated|shredded|julienned|crumbled|peeled|cubed|halved|quartered)\b.*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        r",?\s*\b(?:very\s+)?(thinly|finely|roughly|thin|fine|coarsely|coarse)\b.*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(r",?\s*shredded\b.*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r",?\s*(?:pat\s+dry|well\s+drained|thoroughly\s+rinsed)\b.*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r",?\s*(?:rinsed\s+and\s+drained|drained\s+and\s+rinsed|rinsed|drained)\b.*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r",?\s*cut\s+into\s+\w+\b.*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r",?\s*to\s+taste\b.*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s+", " ", text).strip(" ,.-")
    text = re.sub(r"^[0-9]+[\.)]\s*", "", text).strip()
    return re.sub(r"\s+", " ", text)


def extract_ingredients_from_recipe_text(recipe_text: str) -> list[str]:
    """Parse ingredient bullets from a recipe text block."""
    lines = recipe_text.splitlines()
    collecting = False
    extracted_names: list[str] = []

    for raw in lines:
        line = raw.strip()
        lower = line.lower()

        if lower.startswith("ingredients"):
            collecting = True
            continue

        if collecting and (
            lower.startswith("instructions")
            or lower.startswith("steps")
            or lower.startswith("directions")
            or lower.startswith("chef")
        ):
            break

        if collecting and (line.startswith(("*", "-", "•", "·")) or re.match(r"^\d+[\.)]", line)):
            name = normalize_generated_ingredient(line)
            if name and not re.search(
                r"\b(recipe name|description|step|preparation steps|instruction|direction)\b",
                name,
                flags=re.IGNORECASE,
            ):
                extracted_names.append(name)

    if not extracted_names:
        for raw in lines:
            line = raw.strip()
            if line.startswith(("*", "-", "•", "·")):
                name = normalize_generated_ingredient(line)
                if name and not re.search(
                    r"\b(recipe name|description|step|preparation steps|instruction|direction)\b",
                    name,
                    flags=re.IGNORECASE,
                ):
                    extracted_names.append(name)

    seen = set()
    unique = []
    for name in extracted_names:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            unique.append(name)

    return unique


def filter_pricing_ingredients(ingredients: list[str]) -> list[str]:
    """Remove pantry basics typically assumed on hand to avoid inflated totals."""
    excluded = {
        "salt",
        "salt and pepper",
        "black pepper",
        "pepper",
        "water",
        "cooking oil",
        "oil",
        "salt and pepper to taste",
        "onion powder",
        "garlic powder",
        "olive oil",
        "vegetable oil",
        "canola oil",
        "avocado oil",
        "butter",
        "flour",
        "sugar",
    }
    filtered = []
    for ingredient in ingredients:
        lowered = ingredient.strip().lower()
        if lowered in excluded:
            continue
        if re.search(
            r"\b(recipe name|description|step|preparation steps|instruction|direction|chef's notes)\b",
            lowered,
        ):
            continue
        filtered.append(ingredient)
    return filtered or ingredients


def parse_csv_ingredients(raw: str) -> list[str]:
    """Parse comma-separated ingredient values into a list."""
    return [item.strip() for item in raw.split(",") if item.strip()]


def get_pricing_tier(total: float) -> str:
    """Classify total cost into cheap, medium, or expensive tiers."""
    if total < 25:
        return "cheap"
    if total <= 50:
        return "medium"
    return "expensive"


def load_recipe_text(recipe_file: str) -> str:
    """Load recipe text file content."""
    path = Path(recipe_file)
    if not path.exists():
        raise FileNotFoundError(f"Recipe file not found: {recipe_file}")
    return path.read_text(encoding="utf-8")


def load_ingredients_json(ingredients_file: str) -> list[str]:
    """Load ingredient names from ingredient_extractor JSON output."""
    path = Path(ingredients_file)
    if not path.exists():
        raise FileNotFoundError(f"Ingredients file not found: {ingredients_file}")

    data = json.loads(path.read_text(encoding="utf-8"))
    raw_ingredients = data.get("ingredients", [])
    if not isinstance(raw_ingredients, list):
        return []

    names: list[str] = []
    for item in raw_ingredients:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
        else:
            name = str(item).strip()
        if name:
            names.append(name)

    seen = set()
    unique_names = []
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_names.append(name)
    return unique_names


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for pricing utility."""
    parser = argparse.ArgumentParser(
        description="Estimate Kroger ingredient pricing from ingredients input.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--ingredients",
        help="Comma-separated ingredients (example: 'eggs,milk,bread').",
    )
    source_group.add_argument(
        "--recipe-file",
        help="Path to generated recipe text file. Ingredients are parsed from the Ingredients section.",
    )
    source_group.add_argument(
        "--ingredients-json",
        help="Path to ingredients.json from ingredient_extractor.py. Uses each ingredient 'name' for Kroger search.",
    )
    parser.add_argument(
        "--zip-code",
        default=os.getenv("KROGER_ZIP_CODE", "78201"),
        help="Zip code used to resolve Kroger location (default from KROGER_ZIP_CODE or 78201).",
    )
    parser.add_argument(
        "--strategy",
        default="average_top3",
        choices=["average_top3", "cheapest", "first"],
        help="Pricing strategy for ingredient line-item selection.",
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:5001/api/pricing/ingredients",
        help="Backend pricing endpoint URL.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=int(os.getenv("KROGER_REQUEST_TIMEOUT", "60")),
        help="Timeout in seconds for the Kroger pricing API request (default: 60).",
    )
    return parser


def main() -> int:
    """Main execution function."""
    load_dotenv()
    args = build_parser().parse_args()

    if args.ingredients:
        source_ingredients = parse_csv_ingredients(args.ingredients)
    elif args.recipe_file:
        recipe_text = load_recipe_text(args.recipe_file)
        source_ingredients = extract_ingredients_from_recipe_text(recipe_text)
    else:
        source_ingredients = load_ingredients_json(args.ingredients_json)

    pricing_ingredients = filter_pricing_ingredients(source_ingredients)
    if not pricing_ingredients:
        print("No valid ingredients found for pricing.")
        return 1

    print("[KROGER PRICING REQUEST]")
    print(f"Ingredients: {', '.join(pricing_ingredients)}")
    print(f"Zip: {args.zip_code}")
    print(f"Strategy: {args.strategy}")

    pricing = estimate_kroger_cost(
        pricing_ingredients,
        zip_code=args.zip_code,
        price_strategy=args.strategy,
        api_url=args.api_url,
        request_timeout=args.request_timeout,
    )
    if not pricing:
        return 2

    print("\n[KROGER PRICING RESULT]")
    estimated_total = pricing.get("estimatedTotal")
    line_items = pricing.get("lineItems") or []

    if line_items:
        print("Item Prices:")
        for item in line_items:
            ingredient = item.get("ingredient", "unknown")
            price = item.get("price")
            if item.get("found") and price is not None:
                print(f"  - {ingredient}: ${float(price):.2f}")
            else:
                reason = item.get("reason", "not_found")
                print(f"  - {ingredient}: N/A ({reason})")

    print(f"Priced Count: {pricing.get('pricedCount')} / {pricing.get('requestedCount')}")
    print(f"Estimated Total: ${estimated_total}")
    print(f"Location: {pricing.get('locationId')} ({pricing.get('zipCode')})")
    if pricing.get("missingIngredients"):
        print(f"Missing: {', '.join(pricing['missingIngredients'])}")

    tier = "unknown"
    if estimated_total is not None:
        try:
            tier = get_pricing_tier(float(estimated_total))
        except (TypeError, ValueError):
            tier = "unknown"

    selected_tier = args.strategy
    if selected_tier == "cheapest":
        selected_tier = "cheap"
    elif selected_tier == "average_top3":
        selected_tier = "medium"
    elif selected_tier == "first":
        selected_tier = "expensive"

    tier_status = "unknown"
    if tier != "unknown":
        tier_status = "pass" if tier == selected_tier else "fail"

    print(f"Tier: {tier} | Selected Tier: {selected_tier} | Result: {tier_status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

