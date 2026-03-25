import os
import re
import time
from dataclasses import dataclass

import requests
from requests.auth import HTTPBasicAuth


API_TIMEOUT = 10
DEFAULT_KROGER_BASE_URL = "https://api-ce.kroger.com"
DEFAULT_KROGER_SCOPE = "product.compact"
DEFAULT_PRICE_STRATEGY = "average_top3"


def _normalize_ingredient(term: str) -> str:
    """Normalize ingredient labels so product search terms are cleaner."""
    cleaned = (term or "").strip().lower()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    aliases = {
        "scallion": "green onion",
        "cilantro": "coriander",
        "cherry tomatoes": "tomato",
    }
    return aliases.get(cleaned, cleaned)


def _extract_price(product: dict) -> float | None:
    """Extract the first available regular/promo price from a Kroger product payload."""
    items = product.get("items") or []
    for item in items:
        price_obj = item.get("price") or {}
        regular = price_obj.get("regular")
        promo = price_obj.get("promo")
        chosen = regular if regular is not None else promo
        if chosen is None:
            continue
        try:
            return float(chosen)
        except (TypeError, ValueError):
            continue
    return None


def _collect_priced_candidates(products: list[dict]) -> list[dict]:
    """Build a list of priced product candidates from Kroger response items."""
    candidates = []
    for product in products:
        price = _extract_price(product)
        if price is None:
            continue
        candidates.append(
            {
                "price": float(price),
                "description": product.get("description"),
                "brand": product.get("brand"),
                "upc": product.get("upc"),
            }
        )
    return candidates


def _select_price(candidates: list[dict], strategy: str) -> tuple[float, dict] | None:
    """Select ingredient price from candidates using strategy."""
    if not candidates:
        return None

    normalized_strategy = (strategy or "").strip().lower() or DEFAULT_PRICE_STRATEGY
    if normalized_strategy == "first":
        chosen = candidates[0]
        return round(chosen["price"], 2), chosen

    by_price = sorted(candidates, key=lambda c: c["price"])
    if normalized_strategy == "cheapest":
        chosen = by_price[0]
        return round(chosen["price"], 2), chosen

    # Default: average of the cheapest 3 items to reduce premium outliers.
    top = by_price[:3]
    avg = sum(item["price"] for item in top) / len(top)
    representative = top[0]
    return round(avg, 2), representative


@dataclass
class _TokenCache:
    token: str | None = None
    expires_at: float = 0.0


_TOKEN_CACHE = _TokenCache()


def _clean_env(value: str | None) -> str | None:
    """Trim whitespace and surrounding quotes from env vars."""
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


def get_access_token() -> str:
    """Get and cache Kroger OAuth token using client credentials."""
    now = time.time()
    if _TOKEN_CACHE.token and now < _TOKEN_CACHE.expires_at:
        return _TOKEN_CACHE.token

    client_id = _clean_env(os.getenv("KROGER_CLIENT_ID"))
    client_secret = _clean_env(os.getenv("KROGER_CLIENT_SECRET"))
    if not client_id or not client_secret:
        raise ValueError("Missing KROGER_CLIENT_ID or KROGER_CLIENT_SECRET")

    base_url = _clean_env(os.getenv("KROGER_BASE_URL")) or DEFAULT_KROGER_BASE_URL
    base_url = base_url.rstrip("/")
    scope = _clean_env(os.getenv("KROGER_SCOPE")) or DEFAULT_KROGER_SCOPE

    response = requests.post(
        f"{base_url}/v1/connect/oauth2/token",
        auth=HTTPBasicAuth(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials", "scope": scope},
        timeout=API_TIMEOUT,
    )
    if response.status_code == 401:
        raise ValueError(
            "Kroger OAuth unauthorized (401). Verify KROGER_CLIENT_ID/KROGER_CLIENT_SECRET, "
            "confirm app is configured for client credentials, and ensure product scope access."
        )
    response.raise_for_status()

    payload = response.json()
    token = payload.get("access_token")
    expires_in = int(payload.get("expires_in", 1800))
    if not token:
        raise ValueError("Kroger token response did not include access_token")

    _TOKEN_CACHE.token = token
    _TOKEN_CACHE.expires_at = now + max(60, expires_in - 60)
    return token


def get_location_id(zip_code: str, token: str) -> str:
    """Resolve locationId from zip code."""
    zipcode = (zip_code or "").strip()
    if not zipcode:
        raise ValueError("zipCode is required")

    base_url = _clean_env(os.getenv("KROGER_BASE_URL")) or DEFAULT_KROGER_BASE_URL
    base_url = base_url.rstrip("/")
    response = requests.get(
        f"{base_url}/v1/locations",
        headers={"Authorization": f"Bearer {token}"},
        params={"filter.zipCode": zipcode},
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()

    payload = response.json()
    locations = payload.get("data") or []
    if not locations:
        raise ValueError(f"No Kroger locations found for zip code {zipcode}")

    location_id = locations[0].get("locationId")
    if not location_id:
        raise ValueError("Kroger location response missing locationId")
    return location_id


def get_ingredient_price(ingredient: str, location_id: str, token: str, price_strategy: str = DEFAULT_PRICE_STRATEGY) -> dict:
    """Get ingredient price using configurable product selection strategy."""
    term = _normalize_ingredient(ingredient)
    if not term:
        return {
            "ingredient": ingredient,
            "searchTerm": term,
            "found": False,
            "price": None,
            "product": None,
            "reason": "empty_ingredient",
        }

    base_url = _clean_env(os.getenv("KROGER_BASE_URL")) or DEFAULT_KROGER_BASE_URL
    base_url = base_url.rstrip("/")
    try:
        response = requests.get(
            f"{base_url}/v1/products",
            headers={"Authorization": f"Bearer {token}"},
            params={"filter.term": term, "filter.locationId": location_id, "filter.limit": 20},
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "ingredient": ingredient,
            "searchTerm": term,
            "found": False,
            "price": None,
            "product": None,
            "reason": "api_error",
            "error": str(e),
        }

    payload = response.json()
    products = payload.get("data") or []
    if not products:
        return {
            "ingredient": ingredient,
            "searchTerm": term,
            "found": False,
            "price": None,
            "product": None,
            "reason": "no_products",
        }

    candidates = _collect_priced_candidates(products)
    selected = _select_price(candidates, price_strategy)

    if selected is None:
        return {
            "ingredient": ingredient,
            "searchTerm": term,
            "found": False,
            "price": None,
            "product": None,
            "reason": "no_price",
        }

    selected_price, selected_product = selected

    return {
        "ingredient": ingredient,
        "searchTerm": term,
        "found": True,
        "price": selected_price,
        "selectionStrategy": (price_strategy or DEFAULT_PRICE_STRATEGY),
        "samplePrices": [round(c["price"], 2) for c in sorted(candidates, key=lambda c: c["price"])[:5]],
        "product": {
            "description": selected_product.get("description"),
            "brand": selected_product.get("brand"),
            "upc": selected_product.get("upc"),
        },
        "reason": None,
    }


def estimate_ingredient_total(ingredients: list[str], zip_code: str, price_strategy: str = DEFAULT_PRICE_STRATEGY) -> dict:
    """Price all ingredients for one zip code and return subtotal + details."""
    if not ingredients:
        raise ValueError("ingredients list is required")

    token = get_access_token()
    location_id = get_location_id(zip_code, token)

    line_items = []
    subtotal = 0.0
    missing = []

    for ingredient in ingredients:
        result = get_ingredient_price(ingredient, location_id, token, price_strategy=price_strategy)
        line_items.append(result)
        if result["found"] and result["price"] is not None:
            subtotal += float(result["price"])
        else:
            missing.append(ingredient)

    return {
        "zipCode": zip_code,
        "locationId": location_id,
        "lineItems": line_items,
        "missingIngredients": missing,
        "subtotal": round(subtotal, 2),
        "estimatedTotal": round(subtotal, 2),
        "priceStrategy": (price_strategy or DEFAULT_PRICE_STRATEGY),
        "pricedCount": len([i for i in line_items if i["found"]]),
        "requestedCount": len(ingredients),
    }