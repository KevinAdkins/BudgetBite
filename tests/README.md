# Ground Truth Testing

This folder contains scripts for testing ingredient extraction accuracy against labeled food image datasets.

## Test Datasets

### 1. Manual Fridge Images (5 images)
Located in `ground_truth_dataset/`:
- **fridge1.webp** + fridge1.txt (8 ingredients)
- **fridge2.jpg** + fridge2.txt (13 ingredients)
- **fridge3.webp** + fridge3.txt
- **fridge4.jpeg** + fridge4.txt
- **fridge5.jpeg** + fridge5.txt

**Format**: Each image has a corresponding `.txt` file with manually labeled ground truth ingredients (one per line).

**Test Script**: `test_ground_truth_extraction.py` - Compares Gemini API extraction against these labeled files.

### 2. Kaggle Singular Food Items Dataset
Optional additional testing with single-ingredient images:
- **Source**: [Kaggle - Singular Food Items Dataset](https://www.kaggle.com/datasets/liamboyd1/singular-food-items)
- **Format**: Folder-based organization where each folder name represents the ingredient label
- **Structure**: `ground_truth_dataset/<ingredient>/<image_files>`
- **Test Script**: `batch_extract_ground_truth.py` (if available)

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

## Running Tests

### Test Manual Fridge Images

Tests the 5 manually labeled fridge images:

```bash
cd tests
python test_ground_truth_extraction.py
```

This will:
- Test all 5 fridge images (fridge1-fridge5)
- Compare Gemini extraction against manual `.txt` labels
- Calculate precision, recall, and F1 scores
- Generate `ground_truth_test_results.json` with detailed metrics

### Test Kaggle Dataset (Optional)

If you've downloaded the Kaggle dataset, run the batch test:

```bash
cd tests
python batch_extract_ground_truth.py
```
### Manual Fridge Images Test
- `ground_truth_test_results.json` - Complete test results with per-image and aggregate metrics

### Kaggle Dataset Test (if run)
- `results/gt_test_results.json` - Complete test results for Kaggle dataset
- Extract ingredients from each image using AI
- Compare AI predictions with ground truth labels (folder names)
- Generate detailed accuracy reports and visualizations

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

### Terminal Output
```
======================================================================
Testing: fridge1.webp
======================================================================
📋 Ground Truth (8 ingredients):
   • beef broth
   • grapes
   • yogurt
   • carrots
   ...

🤖 Gemini Extracted (7 ingredients):
   • grapes (fruit)
   • yogurt (dairy)
   • carrots (vegetable)
   ...

📊 Analysis:
   ✅ Matched: 6/8
   ❌ Missed: 2
   
📈 Metrics:
   Precision: 85.7% (of extracted, how many are correct)
   Recall:    75.0% (of ground truth, how many found)
   F1 Score:  80.0% (overall accuracy)
```

### JSON Output
```json
{
  "image": "fridge1.webp",
  "success": true,
  "ground_truth_count": 8,
  "extracted_count": 7,
  "metrics": {
    "precision": 0.857,
    "recall": 0.750,
    "f1_score": 0.800
  },
  "matches": {
    "matched_count": 6,
    "misses": ["beef broth", "hummus"],
    "false_positives": ["broth"]
  }1,
  "recall": 1,
  "f1_score": 1
}
```
