"""
Kroger pricing utility.

This script is intentionally focused on one job: estimate ingredient cost
through the backend Kroger pricing endpoint.
"""

import argparse
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
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
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
    text = re.sub(
        r"^\d+[\d/\.]*\s*(cup|cups|tbsp|tsp|teaspoon|teaspoons|tablespoon|tablespoons|"
        r"oz|ounce|ounces|lb|lbs|pound|pounds|g|kg|ml|l|portion|portions|slice|slices|"
        r"piece|pieces|ring|rings|head|heads|small|medium|large|bowl|bowls|full|half)\b",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
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
        "black pepper",
        "pepper",
        "water",
        "cooking oil",
        "oil",
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


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for pricing utility."""
    parser = argparse.ArgumentParser(
        description="Estimate Kroger ingredient pricing from ingredients or recipe text.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--ingredients",
        help="Comma-separated ingredients (example: 'eggs,milk,bread').",
    )
    source_group.add_argument(
        "--recipe-file",
        help="Path to recipe text file. Ingredients are extracted from the Ingredients section.",
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
    return parser


def main() -> int:
    """Main execution function."""
    load_dotenv()
    args = build_parser().parse_args()

    if args.ingredients:
        source_ingredients = parse_csv_ingredients(args.ingredients)
    else:
        recipe_text = load_recipe_text(args.recipe_file)
        source_ingredients = extract_ingredients_from_recipe_text(recipe_text)

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
    )
    if not pricing:
        return 2

    print("\n[KROGER PRICING RESULT]")
    estimated_total = pricing.get("estimatedTotal")
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
    print(f"Tier: {tier}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

