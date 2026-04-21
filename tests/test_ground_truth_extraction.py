"""
Ground Truth Ingredient Extraction Test
Compares Gemini API extraction results against manually labeled ground truth data.

Metrics calculated:
- Precision: Of the ingredients extracted by API, how many are correct?
- Recall: Of the ground truth ingredients, how many did the API find?
- F1 Score: Harmonic mean of precision and recall
- Exact matches vs fuzzy matches (e.g., "banana" vs "bananna")
"""

import sys
import os
from pathlib import Path
from difflib import SequenceMatcher
import json

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ingredient_extractor import extract_ingredients


def normalize_ingredient_name(name: str) -> str:
    """Normalize ingredient names for comparison (lowercase, strip whitespace)."""
    return name.lower().strip()


def fuzzy_match(str1: str, str2: str, threshold=0.85) -> bool:
    """Check if two strings match with fuzzy matching (handles typos)."""
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold


def find_fuzzy_matches(extracted: list[str], ground_truth: list[str], threshold=0.85) -> dict:
    """
    Match extracted ingredients to ground truth with fuzzy matching.
    Returns dict with matches, misses, and false positives.
    """
    matched_extracted = set()
    matched_ground_truth = set()
    fuzzy_matches = []
    
    # Find matches (exact and fuzzy)
    for ext_ing in extracted:
        for gt_ing in ground_truth:
            if fuzzy_match(ext_ing, gt_ing, threshold):
                matched_extracted.add(ext_ing)
                matched_ground_truth.add(gt_ing)
                if ext_ing.lower() != gt_ing.lower():
                    fuzzy_matches.append((ext_ing, gt_ing))
                break
    
    # Calculate misses and false positives
    misses = [gt for gt in ground_truth if gt not in matched_ground_truth]
    false_positives = [ext for ext in extracted if ext not in matched_extracted]
    
    return {
        "matched_count": len(matched_extracted),
        "fuzzy_matches": fuzzy_matches,
        "misses": misses,
        "false_positives": false_positives,
    }


def calculate_metrics(matched: int, total_extracted: int, total_ground_truth: int) -> dict:
    """Calculate precision, recall, and F1 score."""
    precision = matched / total_extracted if total_extracted > 0 else 0
    recall = matched / total_ground_truth if total_ground_truth > 0 else 0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1_score, 3),
    }


def load_ground_truth(txt_path: Path) -> list[str]:
    """Load ground truth ingredients from text file."""
    with open(txt_path, 'r') as f:
        ingredients = [normalize_ingredient_name(line) for line in f if line.strip()]
    return [ing for ing in ingredients if ing]  # Remove empty lines


def test_single_image(image_path: Path, ground_truth_path: Path, budget: str = "less than $25") -> dict:
    """Test ingredient extraction on a single image."""
    print(f"\n{'='*70}")
    print(f"Testing: {image_path.name}")
    print(f"{'='*70}")
    
    # Load ground truth
    ground_truth_ingredients = load_ground_truth(ground_truth_path)
    print(f"📋 Ground Truth ({len(ground_truth_ingredients)} ingredients):")
    for ing in ground_truth_ingredients:
        print(f"   • {ing}")
    
    # Extract ingredients via Gemini API
    print(f"\n🔍 Extracting with Gemini API...")
    try:
        result = extract_ingredients(str(image_path), budget)
        extracted_ingredients = [normalize_ingredient_name(ing.name) for ing in result.ingredients]
        
        print(f"\n🤖 Gemini Extracted ({len(extracted_ingredients)} ingredients):")
        for ing in result.ingredients:
            print(f"   • {ing.name} ({ing.category})")
        
        # Compare results
        matches = find_fuzzy_matches(extracted_ingredients, ground_truth_ingredients)
        metrics = calculate_metrics(
            matches["matched_count"], 
            len(extracted_ingredients), 
            len(ground_truth_ingredients)
        )
        
        # Print analysis
        print(f"\n📊 Analysis:")
        print(f"   ✅ Matched: {matches['matched_count']}/{len(ground_truth_ingredients)}")
        
        if matches["fuzzy_matches"]:
            print(f"   🔤 Fuzzy matches (typos/variations):")
            for ext, gt in matches["fuzzy_matches"]:
                print(f"      • '{ext}' ≈ '{gt}'")
        
        if matches["misses"]:
            print(f"   ❌ Missed (in ground truth, not extracted): {len(matches['misses'])}")
            for miss in matches["misses"]:
                print(f"      • {miss}")
        
        if matches["false_positives"]:
            print(f"   ⚠️  False Positives (extracted, not in ground truth): {len(matches['false_positives'])}")
            for fp in matches["false_positives"]:
                print(f"      • {fp}")
        
        print(f"\n📈 Metrics:")
        print(f"   Precision: {metrics['precision']:.1%} (of extracted, how many are correct)")
        print(f"   Recall:    {metrics['recall']:.1%} (of ground truth, how many found)")
        print(f"   F1 Score:  {metrics['f1_score']:.1%} (overall accuracy)")
        
        return {
            "image": image_path.name,
            "success": True,
            "metrics": metrics,
            "matches": matches,
            "ground_truth_count": len(ground_truth_ingredients),
            "extracted_count": len(extracted_ingredients),
        }
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "image": image_path.name,
            "success": False,
            "error": str(e),
        }


def run_all_tests(dataset_dir: Path, budget: str = "less than $25") -> dict:
    """Run tests on all images in the ground truth dataset."""
    print("\n" + "="*70)
    print("🧪 GROUND TRUTH INGREDIENT EXTRACTION TEST SUITE")
    print("="*70)
    
    # Find all image files with corresponding .txt files
    image_extensions = {'.webp', '.jpg', '.jpeg', '.png'}
    test_cases = []
    
    for img_path in dataset_dir.iterdir():
        if img_path.suffix.lower() in image_extensions:
            txt_path = img_path.with_suffix('.txt')
            if txt_path.exists():
                test_cases.append((img_path, txt_path))
    
    if not test_cases:
        print("❌ No test cases found (need image + .txt pairs)")
        return {}
    
    print(f"\n📁 Found {len(test_cases)} test cases in {dataset_dir}")
    
    # Run tests
    results = []
    for img_path, txt_path in sorted(test_cases):
        result = test_single_image(img_path, txt_path, budget)
        results.append(result)
    
    # Aggregate statistics
    successful_tests = [r for r in results if r["success"]]
    
    if not successful_tests:
        print("\n❌ No successful tests to aggregate")
        return {"results": results}
    
    avg_precision = sum(r["metrics"]["precision"] for r in successful_tests) / len(successful_tests)
    avg_recall = sum(r["metrics"]["recall"] for r in successful_tests) / len(successful_tests)
    avg_f1 = sum(r["metrics"]["f1_score"] for r in successful_tests) / len(successful_tests)
    
    total_ground_truth = sum(r["ground_truth_count"] for r in successful_tests)
    total_extracted = sum(r["extracted_count"] for r in successful_tests)
    total_matched = sum(r["matches"]["matched_count"] for r in successful_tests)
    
    # Print summary
    print(f"\n{'='*70}")
    print("📊 OVERALL SUMMARY")
    print(f"{'='*70}")
    print(f"Tests Run: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(results) - len(successful_tests)}")
    print(f"\nAggregate Stats:")
    print(f"  Total Ground Truth Ingredients: {total_ground_truth}")
    print(f"  Total Extracted Ingredients: {total_extracted}")
    print(f"  Total Matched: {total_matched}")
    print(f"\nAverage Metrics:")
    print(f"  Avg Precision: {avg_precision:.1%}")
    print(f"  Avg Recall:    {avg_recall:.1%}")
    print(f"  Avg F1 Score:  {avg_f1:.1%}")
    
    return {
        "results": results,
        "summary": {
            "total_tests": len(results),
            "successful": len(successful_tests),
            "failed": len(results) - len(successful_tests),
            "avg_precision": round(avg_precision, 3),
            "avg_recall": round(avg_recall, 3),
            "avg_f1": round(avg_f1, 3),
            "total_ground_truth": total_ground_truth,
            "total_extracted": total_extracted,
            "total_matched": total_matched,
        }
    }


def save_results(results: dict, output_path: Path):
    """Save test results to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    # Setup paths
    script_dir = Path(__file__).parent
    dataset_dir = script_dir / "ground_truth_dataset"
    output_file = script_dir / "ground_truth_test_results.json"
    
    if not dataset_dir.exists():
        print(f"❌ Dataset directory not found: {dataset_dir}")
        sys.exit(1)
    
    # Run tests
    results = run_all_tests(dataset_dir, budget="less than $25")
    
    # Save results
    if results:
        save_results(results, output_file)
    
    print("\n✅ Testing complete!\n")
