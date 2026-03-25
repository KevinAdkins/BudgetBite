# Ground Truth Testing

This folder contains scripts for testing ingredient extraction accuracy against labeled food image datasets.

## Dataset Source

The test images come from the **Singular Food Items** dataset on Kaggle:
- **Source**: [Kaggle - Singular Food Items Dataset](https://www.kaggle.com/datasets/liamboyd1/singular-food-items)
- **Format**: Folder-based organization where each folder name represents the ingredient label
- **Structure**: `ground_truth_dataset/<ingredient>/<image_files>`

## Setup

1. Download the dataset from Kaggle and place it in the `ground_truth_dataset/` folder

2. Make sure you have your Gemini API key in `.env`:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```

3. Activate your virtual environment:
   ```bash
   source ../.venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

## Running the Batch Test

The batch test script will:
- Process all images from the `ground_truth_dataset/` folder
- Extract ingredients from each image using AI
- Compare AI predictions with ground truth labels (folder names)
- Generate detailed accuracy reports and visualizations

```bash
cd tests
python batch_extract_ground_truth.py
```

### ✨ Resume Feature

The script automatically saves progress after each image. If the script is interrupted:

1. **Progress is automatically saved** in `gt_progress.json`
2. **Simply rerun the script** - it will automatically resume from the last processed image
3. **Progress files are cleaned up** automatically when processing completes successfully

You can stop and restart the script at any time without losing progress!

## Output Files

After running, you'll get:
- `ground_truth_dataset/` - Dataset organized by ingredient folders (apple, banana, bread, etc.)
- `results/gt_test_results.json` - Complete test results with per-image and aggregate metrics
- `results/visualizations/` - Performance charts and confusion matrices
- `gt_progress.json` - Progress tracking file (temporary, auto-deleted on completion)

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
