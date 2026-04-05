# Quick Start: BudgetBite Pipeline

## ✅ Setup Complete

The main recipe generation pipeline is fully implemented with:
- ✅ Input validation & refusal handling
- ✅ Database retrieval (top-k matching)
- ✅ Recipe generation (mocked for E2E testing)
- ✅ Ingredient validation
- ✅ Budget checking
- ✅ Regeneration loop (up to 3 iterations)
- ✅ Comprehensive error handling

## 🚀 Getting Started (3 Steps)

### 1. Start the Flask Server

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
```

### 2. Test the Pipeline in Another Terminal

**Option A: Using Python**
```bash
cd testing
python -c "
import requests
import json

response = requests.post(
    'http://127.0.0.1:5001/api/pipeline/generate-recipe',
    json={
        'ingredients': ['chicken', 'tomato', 'garlic', 'olive oil'],
        'budget': 15.00
    }
)

print(json.dumps(response.json(), indent=2))
"
```

**Option B: Using cURL**
```bash
curl -X POST http://127.0.0.1:5001/api/pipeline/generate-recipe \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "tomato", "garlic", "olive oil"],
    "budget": 15.00
  }' | python -m json.tool
```

**Option C: Run Full Test Suite**
```bash
cd testing
python test_pipeline.py
```

### 3. See the Response

```json
{
  "success": true,
  "recipe": {
    "name": "Creative Mixed Dish with Chicken",
    "category": "Mixed",
    "ingredients": ["chicken", "tomato", "garlic", "olive oil"],
    "instructions": "1. Prepare chicken, tomato, garlic...",
    "estimated_price": 6.0,
    "metadata": {
      "iteration": 1,
      "type": "mock",
      "generated_at": "2026-04-04T..."
    }
  },
  "validation": {
    "is_valid": true,
    "recipe_ingredients": ["chicken", "tomato", "garlic", "olive oil"],
    "missing_ingredients": [],
    "validation_errors": []
  },
  "budget_check": {
    "has_budget_constraint": true,
    "budget": 15.0,
    "estimated_cost": 6.0,
    "is_within_budget": true,
    "message": "Recipe cost ($6.00) is within budget ($15.00)"
  },
  "pipeline_status": "success",
  "iterations": 1,
  "retrieved_context_count": 3,
  "timestamp": "2026-04-04T21:30:45Z"
}
```

## 📋 API Reference

### Endpoint
```
POST /api/pipeline/generate-recipe
```

### Required Request Fields
```json
{
  "ingredients": ["chicken", "tomato", "basil"]
}
```

### Optional Request Fields
```json
{
  "budget": 15.00,
  "zipCode": "78207",
  "dietaryRestrictions": ["vegetarian"],
  "cuisine": "Italian"
}
```

### Response Status Codes
| Code | Meaning |
|------|---------|
| 200 | ✅ Success - recipe valid and within budget |
| 202 | ⚠️ Partial - recipe generated but validation/budget issues |
| 400 | ❌ Bad input - rejected by validation |
| 500 | ❌ Server error - generation/validation failed |

## 🧪 Test Scenarios

The test suite validates all these scenarios:

```bash
python testing/test_pipeline.py
```

1. **Basic Pipeline** - Minimal input only
2. **With Budget** - Cost constraint checking
3. **Invalid Input** - Refusal handling (empty ingredients)
4. **Dietary Restrictions** - Filter preferences
5. **Real Pricing Lookup** - With zip code for Kroger API
6. **Response Shape** - Validates all required fields

## 📁 Project Structure

```
backend/
├── app.py                          # Main Flask app (imports pipeline)
├── routes/
│   ├── meal_routes.py             # Existing meal endpoints
│   ├── pricing_routes.py           # Existing pricing endpoints
│   ├── pipeline_routes.py          # ✨ NEW: Main pipeline endpoint
│   └── pipeline_helpers.py         # ✨ NEW: Integration utilities
├── models/
│   └── database.py                # Database layer
├── pull.py                         # API + database utilities
└── requirements.txt               # Dependencies

src/
├── recipe_generator.py            # AI recipe generation (mocked in flow)
├── validator.py                   # Ingredient validation
├── retrieval.py                   # Recipe database queries
└── ingredient_extractor.py        # Image → ingredient extraction

testing/
├── test_pipeline.py               # ✨ NEW: Full E2E test suite
└── test_cases.py                  # Existing unit tests

docs/
└── PIPELINE_GUIDE.md              # ✨ NEW: Complete documentation
```

## 🔧 How It Works

### The Pipeline Flow

```
1. INPUT VALIDATION
   └─ Validates ingredients list, budget, etc.
   └─ Returns 400 if invalid

2. DATABASE RETRIEVAL
   └─ Queries meals table for top-k matches
   └─ Ranks by ingredient overlap
   └─ Used as grounding context

3. RECIPE GENERATION
   └─ Creates recipe from ingredients
   └─ Uses retrieved context for inspiration
   └─ Currently MOCKED for testing

4. INGREDIENT VALIDATION
   └─ Checks recipe only uses input ingredients
   └─ Flags any missing ingredients
   └─ If invalid: triggers regeneration

5. BUDGET CHECKING
   └─ Validates recipe cost < budget
   └─ Uses pricing heuristic or Kroger API
   └─ If exceeded: triggers regeneration

6. REGENERATION LOOP
   └─ Feeds back validation/budget errors
   └─ Max 3 attempts before giving up
   └─ Returns best result found
```

### Error Handling Strategy

**Invalid Input (400):**
```bash
curl -X POST http://127.0.0.1:5001/api/pipeline/generate-recipe \
  -H "Content-Type: application/json" \
  -d '{"ingredients": []}'  # Empty - rejected

# Response:
{
  "success": false,
  "error": "ingredients list cannot be empty",
  "pipeline_status": "input_rejected"
}
```

**Budget Exceeded (202):**
```bash
curl -X POST http://127.0.0.1:5001/api/pipeline/generate-recipe \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["salmon", "caviar"],
    "budget": 5.00
  }'

# Response (202):
{
  "success": false,
  "recipe": {...},
  "pipeline_status": "budget_exceeded",
  "budget_check": {
    "is_within_budget": false,
    "message": "Recipe cost ($45.00) exceeds budget ($5.00)"
  }
}
```

## 📊 Debugging & Monitoring

### Enable Debug Logging

Edit `backend/routes/pipeline_routes.py` and uncomment:
```python
logger.setLevel(logging.DEBUG)
```

### See Detailed Logs

In terminal where Flask is running:
```
[INFO] Retrieved 3 matching recipes from database (top-5)
[INFO] Generated MOCK recipe (iteration 1): Creative Mixed Dish with Chicken
[INFO] Validation result: valid=True, missing=0
[INFO] Pipeline complete: success (iterations=1)
```

### Check Database Queries

The pipeline retrieves recipes from `backend/data/meals.db`:
```bash
sqlite3 backend/data/meals.db "SELECT name, category FROM meals LIMIT 5;"
```

## 🎯 Next Steps

### For Testing
1. ✅ Verify pipeline works with `python testing/test_pipeline.py`
2. ✅ Try different ingredient combinations
3. ✅ Test budget constraints working correctly

### For Integration
1. Replace `generate_recipe_mock()` with real AI from `src/recipe_generator.py`
2. Integrate `src/validator.py` for confidence-scored ingredient validation
3. Wire up `backend/kroger_pricing.py` for real pricing when zip code provided
4. Optimize database queries for large ingredient lists
5. Add performance testing for regeneration loop

### For Production
1. Add rate limiting to prevent abuse
2. Implement caching for database queries
3. Add request timeout handling
4. Monitor pipeline performance metrics
5. Set up error tracking (Sentry, etc.)

## 📞 Support

**Check the detailed guide:**
```bash
cat docs/PIPELINE_GUIDE.md
```

**Review full test coverage:**
```bash
python testing/test_pipeline.py  # 6 scenarios
```

**Check implementation:**
```bash
cat backend/routes/pipeline_routes.py
cat backend/routes/pipeline_helpers.py
```

---

**Pipeline Status:** ✅ Ready for testing and integration
