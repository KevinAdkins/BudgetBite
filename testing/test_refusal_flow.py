#!/usr/bin/env python3
"""
Test script for pipeline input validation (refusal flow)
"""

import sys
from typing import Dict, Optional, Tuple, List

def validate_pipeline_input(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Validate pipeline input and return (is_valid, error_message, normalized_data).

    Returns:
        (True, None, normalized_dict) if valid
        (False, error_msg, None) if invalid
    """
    if not data:
        return False, "Request body cannot be empty", None

    # Required field: ingredients
    ingredients = data.get("ingredients")
    if not ingredients:
        return False, "ingredients field is required and must not be empty", None

    if not isinstance(ingredients, list):
        return False, "ingredients must be a list", None

    if len(ingredients) == 0:
        return False, "ingredients list cannot be empty", None

    # Sanitize ingredients
    cleaned_ingredients = []
    for ing in ingredients:
        if isinstance(ing, str):
            cleaned = ing.strip()
            if cleaned:
                cleaned_ingredients.append(cleaned)
        elif isinstance(ing, dict) and "name" in ing:
            cleaned = str(ing.get("name", "")).strip()
            if cleaned:
                cleaned_ingredients.append(cleaned)

    if not cleaned_ingredients:
        return False, "No valid ingredients provided after sanitization", None

    # Optional: budget (in USD)
    budget = data.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
            if budget < 0:
                return False, "budget must be non-negative", None
        except (TypeError, ValueError):
            return False, "budget must be a valid number", None

    # Optional: dietary restrictions
    dietary_restrictions = data.get("dietaryRestrictions", [])
    if not isinstance(dietary_restrictions, list):
        dietary_restrictions = [dietary_restrictions] if dietary_restrictions else []

    # Optional: cuisine preference
    cuisine = data.get("cuisine", "").strip()

    # Optional: zip code for pricing
    zip_code = data.get("zipCode", "").strip()

    normalized = {
        "ingredients": cleaned_ingredients,
        "budget": budget,
        "dietary_restrictions": dietary_restrictions,
        "cuisine": cuisine,
        "zip_code": zip_code,
    }

    return True, None, normalized

def test_refusal_cases():
    """Test various invalid inputs that should be rejected"""

    test_cases = [
        # Empty request
        {
            "name": "Empty request body",
            "input": {},
            "expected_error": "Request body cannot be empty"
        },

        # Missing ingredients
        {
            "name": "Missing ingredients field",
            "input": {"budget": 10.0},
            "expected_error": "ingredients field is required and must not be empty"
        },

        # Empty ingredients list
        {
            "name": "Empty ingredients list",
            "input": {"ingredients": []},
            "expected_error": "ingredients field is required and must not be empty"
        },

        # Non-list ingredients
        {
            "name": "Ingredients not a list",
            "input": {"ingredients": "chicken, tomato"},
            "expected_error": "ingredients must be a list"
        },

        # Ingredients with empty strings
        {
            "name": "Ingredients with only empty strings",
            "input": {"ingredients": ["", "  ", ""]},
            "expected_error": "No valid ingredients provided after sanitization"
        },

        # Invalid budget
        {
            "name": "Invalid budget type",
            "input": {"ingredients": ["chicken"], "budget": "ten dollars"},
            "expected_error": "budget must be a valid number"
        },

        # Negative budget
        {
            "name": "Negative budget",
            "input": {"ingredients": ["chicken"], "budget": -5.0},
            "expected_error": "budget must be non-negative"
        }
    ]

    print("🧪 Testing Pipeline Input Validation (Refusal Flow)")
    print("=" * 60)

    passed = 0
    total = len(test_cases)

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print(f"   Input: {case['input']}")

        is_valid, error_msg, normalized = validate_pipeline_input(case['input'])

        if not is_valid:
            if error_msg == case['expected_error']:
                print(f"   ✅ PASS: Correctly rejected with '{error_msg}'")
                passed += 1
            else:
                print(f"   ❌ FAIL: Expected '{case['expected_error']}', got '{error_msg}'")
        else:
            print(f"   ❌ FAIL: Expected rejection but input was accepted")
            print(f"   Normalized: {normalized}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All refusal flow tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = test_refusal_cases()
    sys.exit(0 if success else 1)