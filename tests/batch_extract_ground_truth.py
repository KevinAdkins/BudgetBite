"""
Batch Ingredient Extraction for Ground Truth Testing
Processes folder-based dataset where each folder name is the ingredient label
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add BudgetBite root directory to path (go up 1 level: tests -> BudgetBite)
budgetbite_root = Path(__file__).parent.parent
sys.path.insert(0, str(budgetbite_root))

from src.ingredient_extractor import extract_ingredients


def is_rate_limit_error(error: Exception) -> bool:
    """Check if the error is a rate limit error."""
    error_str = str(error)
    return "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower()


def extract_retry_delay(error: Exception) -> Optional[int]:
    """Extract the retry delay from rate limit error message."""
    import re
    error_str = str(error)
    # Look for patterns like "retry in 53.252880651s" or "retryDelay': '53s'"
    match = re.search(r"retry in (\d+)", error_str) or re.search(r"retryDelay.*?(\d+)", error_str)
    if match:
        return int(match.group(1))
    return 60  # Default to 60 seconds if we can't parse it


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name for matching by removing common plural endings.
    Handles: peppers->pepper, tomatoes->tomato, etc.
    """
    name = name.lower().strip()
    # Simple pluralization handling - remove 's', 'es'
    if name.endswith('es') and len(name) > 3:
        return name[:-2]  # tomatoes -> tomato
    elif name.endswith('s') and len(name) > 2:
        return name[:-1]  # peppers -> pepper
    return name


def ingredients_match(ground_truth: str, ai_ingredient: str) -> bool:
    """
    Check if two ingredients match with flexible matching rules.
    Handles:
    - Direct substring matching: "yogurt" in "greek yogurt"
    - Singular/plural variations: "peppers" matches "bell pepper"
    - Word boundary matching: "pepper" as a word in "green bell pepper"
    """
    gt_lower = ground_truth.lower().strip()
    ai_lower = ai_ingredient.lower().strip()
    
    # Direct substring matching (either direction)
    if gt_lower in ai_lower or ai_lower in gt_lower:
        return True
    
    # Normalize both and check again
    gt_normalized = normalize_ingredient_name(gt_lower)
    ai_normalized = normalize_ingredient_name(ai_lower)
    
    if gt_normalized in ai_normalized or ai_normalized in gt_normalized:
        return True
    
    # Check if normalized ground truth appears as a word in AI ingredient
    # e.g., "pepper" in "green bell pepper"
    ai_words = ai_normalized.split()
    if gt_normalized in ai_words or any(gt_normalized in word for word in ai_words):
        return True
    
    # Check if any word from ground truth is in AI ingredient words
    gt_words = gt_normalized.split()
    for gt_word in gt_words:
        if gt_word in ai_words or any(gt_word in word for word in ai_words):
            return True
    
    return False


def load_coco_annotations(annotation_file: Path) -> Dict:
    """Load COCO format annotations from JSON file."""
    with open(annotation_file, 'r') as f:
        return json.load(f)


def get_ground_truth_ingredients(image_id: int, coco_data: Dict) -> List[str]:
    """
    Extract ground truth ingredients for a specific image from COCO annotations.
    
    Args:
        image_id: The ID of the image in COCO format
        coco_data: COCO format dictionary with categories and annotations
    
    Returns:
        Sorted list of ingredient names (deduplicated)
    
    Raises:
        KeyError: If a category_id in annotations doesn't exist in categories
    """
    # Get all annotations for this image
    image_annotations = [ann for ann in coco_data["annotations"] if ann["image_id"] == image_id]
    
    # Get category IDs
    category_ids = set(ann["category_id"] for ann in image_annotations)
    
    # Map category IDs to names
    category_map = {cat["id"]: cat["name"] for cat in coco_data["categories"]}
    
    # Get ingredient names and sort (will raise KeyError if category_id not found)
    ingredients = sorted([category_map[cat_id] for cat_id in category_ids])
    
    return ingredients


def get_all_images_from_folders(dataset_path: Path) -> List[Tuple[Path, str]]:
    """
    Get all images from folder-based dataset.
    Returns list of (image_path, ground_truth_label) tuples.
    Folder name is the ground truth label.
    """
    image_paths = []
    
    # Iterate through all subdirectories
    for folder in sorted(dataset_path.iterdir()):
        if folder.is_dir():
            ground_truth = folder.name  # Folder name is the label
            
            # Get all jpg images in this folder
            for image_file in sorted(folder.glob("*.jpg")):
                image_paths.append((image_file, ground_truth))
    
    return image_paths


def load_progress(progress_file: Path) -> Dict:
    """Load progress from previous run."""
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {"completed_images": [], "results": []}


def save_progress(progress_file: Path, completed_images: List[str], results: List[Dict]):
    """Save progress after each image."""
    progress = {
        "completed_images": completed_images,
        "results": results
    }
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)


def process_dataset(dataset_path: Path, progress_file: Optional[Path] = None):
    """Process all images in folder-based dataset with resume capability."""
    print("="*70)
    print("🔬 PROCESSING DATASET")
    print("="*70)
    print()
    
    if not dataset_path.exists():
        print(f"⚠️  Dataset directory not found: {dataset_path}")
        return None
    
    # Get all images from folder structure
    all_images = get_all_images_from_folders(dataset_path)
    
    if not all_images:
        print("⚠️  No images found in dataset")
        return None
    
    # Get unique categories
    categories = sorted(set([gt for _, gt in all_images]))
    print(f"📋 Found {len(all_images)} images across {len(categories)} ingredient classes")
    print(f"📦 Classes: {', '.join(categories)}")
    print()
    
    # Load progress if resuming
    progress = load_progress(progress_file) if progress_file else {"completed_images": [], "results": []}
    completed_images = set(progress["completed_images"])
    results = progress["results"]
    
    if completed_images:
        print(f"🔄 RESUMING: Found {len(completed_images)} already processed images")
        current = len(completed_images) + 1
        total = len(all_images)
        print(f"   Continuing from image {current}/{total}")
        print()
    
    # Process each image
    for idx, (image_path, ground_truth) in enumerate(all_images, 1):
        image_name = image_path.name
        
        # Skip if already processed
        if image_name in completed_images:
            continue
        
        total_images = len(all_images)
        print(f"\n[{idx}/{total_images}] Processing: {image_name}")
        
        try:
            # Ground truth is the folder name (single ingredient)
            print(f"   Ground Truth: {ground_truth}")
            
            # Extract ingredients using AI (pass image path, not folder name)
            ai_result = extract_ingredients(str(image_path))
            ai_ingredients = sorted([ing.name.lower() for ing in ai_result.ingredients])
            print(f"   AI Extracted: {', '.join(ai_ingredients) if ai_ingredients else '(none)'}")
            
            # Calculate matches with fuzzy matching
            # Match if ground truth is contained in AI ingredient (e.g., "yogurt" in "greek yogurt")
            ground_truth_lower = ground_truth.lower()
            
            # Find matches using improved matching function
            matches = []
            matched_ai_ingredients = set()
            
            for ai_ing in ai_ingredients:
                # Use flexible matching that handles plurals and word boundaries
                if ingredients_match(ground_truth_lower, ai_ing):
                    matches.append(ai_ing)
                    matched_ai_ingredients.add(ai_ing)
            
            # False positives: AI ingredients that didn't match
            false_positives = [ing for ing in ai_ingredients if ing not in matched_ai_ingredients]
            
            # False negatives: ground truth not found if no matches
            false_negatives = [] if matches else [ground_truth_lower]
            
            # Store result
            result = {
                "image": image_name,
                "folder": ground_truth,
                "ground_truth": [ground_truth],
                "ai_extracted": ai_ingredients,
                "matches": matches,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "precision": len(matches) / len(ai_ingredients) if ai_ingredients else 0,
                "recall": 1.0 if matches else 0.0,  # Single item: either found or not
                "non_food_detected": ai_result.non_food_items_detected
            }
            
            # Calculate F1 score
            if result['precision'] + result['recall'] > 0:
                result['f1_score'] = 2 * (result['precision'] * result['recall']) / (result['precision'] + result['recall'])
            else:
                result['f1_score'] = 0
            
            results.append(result)
            completed_images.add(image_name)
            
            print(f"   ✓ Correct: {'YES' if matches else 'NO'} | FP: {len(false_positives)} | FN: {len(false_negatives)}")
            print(f"   📊 Precision: {result['precision']:.2%} | Recall: {result['recall']:.2%} | F1: {result['f1_score']:.2%}")
            
            # Save progress after each image
            if progress_file:
                save_progress(progress_file, list(completed_images), results)
                completed = len(completed_images)
                total = len(all_images)
                print(f"   💾 Progress saved ({completed}/{total})")
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if this is a rate limit error
            if is_rate_limit_error(e):
                retry_delay = extract_retry_delay(e)
                print(f"   ⏸️  Rate limit reached!")
                print(f"   API requests per minute exceeded")
                print(f"   Suggested wait time: {retry_delay} seconds")
                print()
                print("="*70)
                print("🛑 PAUSED DUE TO RATE LIMITS")
                print("="*70)
                print()
                print(f"✅ Progress saved: {len(completed_images)}/{len(all_images)} images completed")
                print(f"📊 Processed: {len(results)} successful results")
                print()
                print("To resume testing:")
                print(f"  1. Wait at least {retry_delay} seconds for API quota to reset")
                print(f"  2. Run the same command again: python batch_extract_ground_truth.py")
                print(f"  3. The script will automatically resume from image {len(completed_images) + 1}")
                print()
                # Save progress but DON'T mark this image as completed
                if progress_file:
                    save_progress(progress_file, list(completed_images), results)
                # Exit gracefully - don't mark as complete so it will retry
                return results
            
            # For non-rate-limit errors, print and skip this image
            print(f"   ❌ Error processing image: {error_msg[:100]}")
            # Mark as completed so we don't retry non-rate-limit errors
            completed_images.add(image_name)
            if progress_file:
                save_progress(progress_file, list(completed_images), results)
            continue
    
    return results


def generate_report(results: List[Dict], output_file: Path):
    """Generate summary report with metrics."""
    if not results:
        print("⚠️  No results to generate report")
        return
    
    print("\n" + "="*70)
    print("📊 GENERATING SUMMARY REPORT")
    print("="*70)
    print()
    
    # Calculate aggregate metrics
    total_images = len(results)
    avg_precision = sum(r['precision'] for r in results) / total_images
    avg_recall = sum(r['recall'] for r in results) / total_images
    avg_f1 = sum(r['f1_score'] for r in results) / total_images
    
    total_matches = sum(len(r['matches']) for r in results)
    total_false_positives = sum(len(r['false_positives']) for r in results)
    total_false_negatives = sum(len(r['false_negatives']) for r in results)
    
    summary = {
        "test_date": "2026-03-24",
        "dataset": "Folder-based ingredient dataset",
        "total_images": total_images,
        "metrics": {
            "average_precision": round(avg_precision, 4),
            "average_recall": round(avg_recall, 4),
            "average_f1_score": round(avg_f1, 4),
            "total_correct_matches": total_matches,
            "total_false_positives": total_false_positives,
            "total_false_negatives": total_false_negatives
        },
        "per_image_results": results
    }
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📄 Report saved to: {output_file}")
    print()
    print(f"Total Images Processed: {total_images}")
    print(f"Average Precision:      {avg_precision:.2%}")
    print(f"Average Recall:         {avg_recall:.2%}")
    print(f"Average F1 Score:       {avg_f1:.2%}")
    print(f"Total Correct Matches:  {total_matches}")
    print(f"Total False Positives:  {total_false_positives}")
    print(f"Total False Negatives:  {total_false_negatives}")
    print()


def main():
    """Main execution."""
    print("\n" + "="*70)
    print("🧪 GROUND TRUTH INGREDIENT EXTRACTION TEST")
    print("="*70)
    print()
    
    # Setup paths - script is in tests/ folder
    script_dir = Path(__file__).parent  # This is tests/
    
    # Use the folder-based dataset structure
    # Default: GTDatasetTest/archive (2)/test
    default_dataset = script_dir / "GTDatasetTest" / "archive (2)" / "test"
    
    # You can override this by setting a different path
    dataset_path = default_dataset
    
    if not dataset_path.exists():
        print(f"❌ Dataset not found at: {dataset_path}")
        print(f"   Please ensure your dataset is at: {dataset_path}")
        print(f"   Or modify the dataset_path variable in main()")
        sys.exit(1)
    
    print(f"📂 Dataset location: {dataset_path}")
    print()
    
    try:
        # Define progress file
        progress_file = script_dir / "gt_progress.json"
        
        # Process the dataset
        results = process_dataset(dataset_path, progress_file)
        
        if results:
            # Save report in tests/ folder
            report_file = script_dir / "gt_test_results.json"
            generate_report(results, report_file)
            
            # Only clean up progress file if ALL images completed
            if progress_file.exists():
                # Check if we completed all images
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                    completed_count = len(progress_data.get("completed_images", []))
                    
                # Count total images
                all_image_count = sum(1 for _ in dataset_path.rglob("*.jpg"))
                
                if completed_count >= all_image_count:
                    progress_file.unlink()
                    print(f"🧹 Cleaned up progress file: {progress_file.name}\n")
                else:
                    print(f"📝 Progress file saved: {progress_file.name}")
                    print(f"   Resume by running this script again\n")
        
        print("="*70)
        
        # Check if we have a progress file (meaning we didn't finish)
        if progress_file.exists():
            print("⏸️  TESTING PAUSED (Rate Limit Reached)")
            print("="*70)
            print()
            print("Run the script again to resume testing after the rate limit resets.")
        else:
            print("✅ TESTING COMPLETE!")
            print("="*70)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
