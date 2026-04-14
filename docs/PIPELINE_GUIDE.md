# BudgetBite Pipeline Guide

## What is the Pipeline?

BudgetBite's core functionality is a 6-step recipe generation pipeline that processes user ingredients into validated, budget-friendly meal suggestions.

## Pipeline Steps

### 1. Input Validation
- Validates the ingredients list (must not be empty)
- Checks budget constraints if provided
- Rejects invalid requests with HTTP 400

### 2. Database Retrieval
- Queries the meals database for recipes matching user ingredients
- Returns top-5 matches ranked by ingredient overlap
- Provides grounding context for AI generation

### 3. Recipe Generation
- Uses AI to create a new recipe from available ingredients
- Incorporates retrieved database recipes as inspiration
- Currently mocked for testing (returns sample recipe)

### 4. Ingredient Validation
- Verifies the generated recipe only uses input ingredients
- Flags any missing or extra ingredients
- Triggers regeneration if validation fails

### 5. Budget Checking
- Estimates recipe cost using pricing heuristics or Kroger API
- Compares against user budget constraint
- Triggers regeneration if budget exceeded

### 6. Regeneration Loop
- Automatically retries up to 3 times if validation or budget issues occur
- Feeds error feedback to improve subsequent generations
- Returns best result found or partial success

## Pipeline Flow Diagram

```
User Input (ingredients + budget)
       ↓
1. Input Validation
   └─ Invalid? → HTTP 400 Error
   └─ Valid? → Continue

2. Database Retrieval
   └─ Top-5 matching recipes

3. Recipe Generation
   └─ AI creates new recipe

4. Ingredient Validation
   └─ Valid? → Continue
   └─ Invalid? → Regenerate (up to 3x)

5. Budget Checking
   └─ Within budget? → Continue
   └─ Over budget? → Regenerate (up to 3x)

6. Success Response
   └─ HTTP 200 with recipe + validation + budget info
```

## API Usage

### Main Endpoint
```
POST /api/pipeline/generate-recipe
```

### Request Format
```json
{
  "ingredients": ["chicken", "tomato", "garlic"],
  "budget": 15.00,
  "zipCode": "78207",
  "dietaryRestrictions": ["vegetarian"],
  "cuisine": "Italian"
}
```

### Response Format
```json
{
  "success": true,
  "recipe": {
    "name": "Creative Mixed Dish with Chicken",
    "ingredients": ["chicken", "tomato", "garlic"],
    "instructions": "1. Prepare chicken...",
    "estimated_price": 6.0
  },
  "validation": {
    "is_valid": true,
    "missing_ingredients": []
  },
  "budget_check": {
    "is_within_budget": true,
    "message": "Recipe cost ($6.00) is within budget ($15.00)"
  },
  "pipeline_status": "success",
  "iterations": 1
}
```

## Error Handling

- **400 Bad Request:** Invalid input (empty ingredients, etc.)
- **202 Partial Success:** Recipe generated but validation/budget issues
- **500 Server Error:** Pipeline failure

## Testing the Pipeline

### Quick Test
```bash
python test_pipeline_quick.py
```

### Full Test Suite
```bash
cd testing
python test_pipeline.py
```

### Manual API Test
```bash
curl -X POST http://127.0.0.1:5001/api/pipeline/generate-recipe \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["chicken", "rice"], "budget": 10}'
```

## Integration Points

1. **Recipe Generation:** Replace `generate_recipe_mock()` with real AI
2. **Ingredient Validation:** Add confidence scores from image analysis
3. **Pricing:** Integrate Kroger API for real-time costs
4. **Database:** Optimize queries for large ingredient sets</content>
<filePath>c:\Users\ericg\OneDrive - Texas A&M University-San Antonio\Spring2026\Budget_Bite\BudgetBite\STARTUP_GUIDE.md