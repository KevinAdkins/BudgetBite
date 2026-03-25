# Ground Truth Testing

This folder contains scripts for testing ingredient extraction accuracy against labeled Roboflow datasets.

## Setup

1. Make sure you have your Gemini API key in `.env`:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```

2. Activate your virtual environment:
   ```bash
   source ../.venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

## Running the Batch Test

The batch test script will:
- Download the Roboflow dataset (COCO format)
- Extract ingredients from all images using AI
- Compare with ground truth labels
- Generate detailed accuracy reports

```bash
cd tests
python batch_extract_ground_truth.py
```

### ✨ Resume Feature

The script automatically saves progress after each image. If the script is interrupted:

1. **Progress is automatically saved** in `gt_progress_<split>.json` files
2. **Simply rerun the script** - it will automatically resume from the last processed image
3. **Progress files are cleaned up** automatically when each split completes successfully

You can stop and restart the script at any time without losing progress!

## Output Files

After running, you'll get:
- `GTDatasetTest/` - Downloaded dataset with images and annotations
- `gt_test_results_train.json` - Results for training split
- `gt_test_results_valid.json` - Results for validation split
- `gt_test_results_test.json` - Results for test split
- `gt_test_results_combined.json` - Overall results across all splits
- `gt_progress_<split>.json` - Progress files (temporary, auto-deleted on completion)

## Metrics Calculated

For each image:
- **Precision**: % of AI predictions that were correct
- **Recall**: % of ground truth ingredients found by AI
- **F1 Score**: Harmonic mean of precision and recall
- **Matches**: Correctly identified ingredients
- **False Positives**: AI detected but not in ground truth
- **False Negatives**: In ground truth but missed by AI

## Example Output

```json
{
  "image": "fridge_001.jpg",
  "ground_truth": ["apple", "carrot", "milk"],
  "ai_extracted": ["apple", "carrot", "orange"],
  "matches": ["apple", "carrot"],
  "false_positives": ["orange"],
  "false_negatives": ["milk"],
  "precision": 0.67,
  "recall": 0.67,
  "f1_score": 0.67
}
```
