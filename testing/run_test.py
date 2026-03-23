from testing.test_cases import TEST_CASES
from validator import extract_ingredients  
from validator import generate_recipe          
from rapidfuzz import fuzz
import json, time

def score_extraction(detected: list[str], expected: list[str]) -> dict:
    """Measures ingredient extraction accuracy."""
    if not expected:
        return {"accuracy": None, "note": "No expected ingredients defined"}

    matched = sum(
        1 for exp in expected
        if any(fuzz.WRatio(exp, det) >= 75 for det in detected)
    )
    hallucinated = [
        det for det in detected
        if not any(fuzz.WRatio(det, exp) >= 75 for exp in expected)
    ]
    return {
        "accuracy": round(matched / len(expected), 2),
        "matched": matched,
        "total_expected": len(expected),
        "hallucinated": hallucinated,
        "hallucination_rate": round(len(hallucinated) / max(len(detected), 1), 2),
    }

def run_all_tests():
    results = []

    for case in TEST_CASES:
        print(f"\nRunning {case['id']} ({case['difficulty']})...")
        result = {"id": case["id"], "difficulty": case["difficulty"]}

        try:
            # Run extraction
            extracted = extract_ingredients(case["image"])
            detected_names = [i.name for i in extracted.ingredients]

            # Score extraction
            extraction_score = score_extraction(detected_names, case["expected_ingredients"])
            result["extraction"] = extraction_score
            result["detected_ingredients"] = detected_names
            result["non_food_detected"] = extracted.non_food_items_detected

            # Check edge case refusal
            if not case["should_detect_food"]:
                if len(extracted.ingredients) == 0:
                    result["refusal"] = "PASS — correctly returned no ingredients"
                else:
                    result["refusal"] = f"FAIL — detected food in non-food image: {detected_names}"
                results.append(result)
                continue

            # Run recipe generation
            recipe = generate_recipe(extracted) # pyright: ignore[reportArgumentType]
            result["recipe_name"] = recipe.name # type: ignore
            result["recipe_ingredients"] = recipe.ingredients # type: ignore
            result["recipe_steps"] = len(recipe.steps) # type: ignore

            # Check hallucination in recipe
            recipe_hallucinations = [
                ing for ing in recipe.ingredients # type: ignore
                if not any(fuzz.WRatio(ing, det) >= 75 for det in detected_names)
            ]
            result["recipe_hallucinations"] = recipe_hallucinations
            result["status"] = "PASS" if not recipe_hallucinations else "WARN"

        except ValueError as e:
            result["status"] = "PASS" if not case["should_detect_food"] else "FAIL"
            result["error"] = str(e)
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        results.append(result)
        time.sleep(1)  # avoid rate limiting

    # ── Print summary ──────────────────────────────────────────────
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    warned = sum(1 for r in results if r.get("status") == "WARN")

    for r in results:
        status = r.get("status", "?")
        extraction = r.get("extraction", {})
        acc = extraction.get("accuracy")
        hall = extraction.get("hallucination_rate")
        acc_str = f"extraction={acc:.0%}" if acc is not None else "no expected defined"
        hall_str = f"hallucination={hall:.0%}" if hall is not None else ""
        print(f"  [{status}] {r['id']} — {acc_str} {hall_str}")

    print(f"\nTotal: {len(results)} | Pass: {passed} | Fail: {failed} | Warn: {warned}")

    # Save full results to JSON
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull results saved to test_results.json")

if __name__ == "__main__":
    run_all_tests()