"""
Pipeline Integration Tests - Demonstrates end-to-end pipeline usage

This test file shows:
1. How to call the pipeline endpoint
2. Expected request/response structure
3. Different scenarios (success, validation failure, budget exceeded)
4. How to interpret results

Run this AFTER starting the Flask server:
    python backend/app.py

Then in another terminal:
    cd testing && python test_pipeline.py
"""

import requests
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

BASE_URL = "http://127.0.0.1:5001/api"
PIPELINE_ENDPOINT = f"{BASE_URL}/pipeline/generate-recipe"

# ═══════════════════════════════════════════════════════════════════════════
# Test Cases
# ═══════════════════════════════════════════════════════════════════════════

def test_basic_pipeline():
    """Test 1: Basic pipeline with minimal input"""
    print("\n" + "="*70)
    print("TEST 1: Basic Pipeline (minimal input)")
    print("="*70)

    payload = {
        "ingredients": ["chicken", "tomato", "basil", "olive oil"]
    }

    print(f"\n📤 REQUEST:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(PIPELINE_ENDPOINT, json=payload)
        print(f"\n📥 RESPONSE ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS: {data['recipe']['name']}")
            print(f"   Iterations: {data['iterations']}")
            print(f"   Validation: {data['validation']['is_valid']}")
        elif response.status_code == 202:
            print("\n⚠️  PARTIAL SUCCESS: Recipe generated but validation/budget issues")
        else:
            print(f"\n❌ FAILED")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_with_budget():
    """Test 2: Pipeline with budget constraint"""
    print("\n" + "="*70)
    print("TEST 2: Pipeline with Budget Constraint")
    print("="*70)

    payload = {
        "ingredients": ["chicken", "rice", "soy sauce", "garlic", "ginger"],
        "budget": 12.00,
        "cuisine": "Asian"
    }

    print(f"\n📤 REQUEST:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(PIPELINE_ENDPOINT, json=payload)
        print(f"\n📥 RESPONSE ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            print(f"\n✅ Recipe fits budget!")
        else:
            print(f"\n⚠️  Recipe may exceed budget or has validation issues")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_invalid_input():
    """Test 3: Invalid input handling (refusal)"""
    print("\n" + "="*70)
    print("TEST 3: Invalid Input Handling")
    print("="*70)

    payload = {
        "ingredients": []  # Empty - should be rejected
    }

    print(f"\n📤 REQUEST:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(PIPELINE_ENDPOINT, json=payload)
        print(f"\n📥 RESPONSE ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 400:
            print(f"\n✅ Correctly rejected invalid input")
        else:
            print(f"\n❌ Should have rejected empty ingredients")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_with_dietary_restrictions():
    """Test 4: Pipeline with dietary restrictions"""
    print("\n" + "="*70)
    print("TEST 4: Pipeline with Dietary Restrictions")
    print("="*70)

    payload = {
        "ingredients": ["tofu", "broccoli", "mushroom", "quinoa"],
        "dietaryRestrictions": ["vegetarian", "vegan"],
        "budget": 10.00
    }

    print(f"\n📤 REQUEST:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(PIPELINE_ENDPOINT, json=payload)
        print(f"\n📥 RESPONSE ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_with_pricing_lookup():
    """Test 5: Pipeline with zip code for real pricing lookup"""
    print("\n" + "="*70)
    print("TEST 5: Pipeline with Pricing Lookup (zip code)")
    print("="*70)

    payload = {
        "ingredients": ["salmon", "lemon", "dill", "asparagus"],
        "budget": 20.00,
        "zipCode": "78207",  # San Antonio area
        "cuisine": "Mediterranean"
    }

    print(f"\n📤 REQUEST:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(PIPELINE_ENDPOINT, json=payload)
        print(f"\n📥 RESPONSE ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_response_shape():
    """Test 6: Verify response shape matches specification"""
    print("\n" + "="*70)
    print("TEST 6: Response Shape Validation")
    print("="*70)

    payload = {
        "ingredients": ["pasta", "marinara", "parmesan"],
        "budget": 8.00
    }

    try:
        response = requests.post(PIPELINE_ENDPOINT, json=payload)
        data = response.json()

        required_fields = [
            "success",
            "recipe",
            "validation",
            "budget_check",
            "pipeline_status",
            "iterations",
            "timestamp"
        ]

        print("\n📋 Required Response Fields:")
        for field in required_fields:
            if field in data:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} (MISSING)")

        if "recipe" in data:
            recipe_fields = ["name", "category", "ingredients", "instructions", "estimated_price"]
            print("\n📋 Recipe Sub-fields:")
            for field in recipe_fields:
                if field in data.get("recipe", {}):
                    print(f"  ✅ {field}")
                else:
                    print(f"  ❌ {field} (MISSING)")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🚀 BudgetBite Pipeline Integration Tests")
    print(f"   Endpoint: {PIPELINE_ENDPOINT}")

    # Run tests
    test_basic_pipeline()
    test_with_budget()
    test_invalid_input()
    test_with_dietary_restrictions()
    test_with_pricing_lookup()
    test_response_shape()

    print("\n" + "="*70)
    print("✅ All tests completed")
    print("="*70)
