# BudgetBite Recipe Generation Pipeline

## Overview

The main recipe generation pipeline integrates all components of BudgetBite into a single, cohesive API endpoint. It manages:

1. **Input Validation & Refusal Handling** - Rejects invalid inputs with clear error messages
2. **Database Retrieval** - Queries meals table for top-k recipe matches  
3. **Recipe Generation** - Creates recipes from ingredients (with grounding context)
4. **Output Validation** - Ensures generated recipes use only input ingredients
5. **Budget Checking** - Validates cost against user budget (optional)
6. **Regeneration Loop** - Automatically refines recipes if validation/budget fails
7. **Error Handling** - Clean error states for all failure cases

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
python app.py
```

Server runs on `http://127.0.0.1:5001`

### 2. Call the Pipeline Endpoint

**Endpoint:** `POST /api/pipeline/generate-recipe`

**Request:**
```json
{
  "ingredients": ["chicken", "tomato", "basil", "olive oil"],
  "budget": 15.00,
  "zipCode": "78207",
  "dietaryRestrictions": ["vegetarian"],
  "cuisine": "Italian"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "recipe": {
    "name": "Creative Italian Dish with Chicken",
    "category": "Italian",
    "ingredients": ["chicken", "tomato", "basil", "olive oil"],
    "instructions": "1. Prepare chicken, tomato, basil...",
    "estimated_price": 12.50,
    "metadata": {
      "iteration": 1,
      "type": "mock",
      "generated_at": "2026-04-04T..."
    }
  },
  "validation": {
    "is_valid": true,
    "recipe_ingredients": [...],
    "missing_ingredients": [],
    "validation_errors": []
  },
  "budget_check": {
    "has_budget_constraint": true,
    "budget": 15.00,
    "estimated_cost": 12.50,
    "is_within_budget": true,
    "message": "Recipe cost ($12.50) is within budget ($15.00)"
  },
  "pipeline_status": "success",
  "iterations": 1,
  "retrieved_context_count": 5,
  "timestamp": "2026-04-04T..."
}
```

### 3. Run Integration Tests

```bash
cd testing
python test_pipeline.py
```

Tests validate all scenarios:
- ✅ Basic pipeline with minimal input
- ✅ With budget constraint
- ✅ Invalid input rejection  
- ✅ With dietary restrictions
- ✅ With pricing lookup (real Kroger API)
- ✅ Response shape validation

## API Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ingredients` | `string[]` | ✅ Yes | List of available ingredients |
| `budget` | `number` | Optional | Max spending in USD |
| `zipCode` | `string` | Optional | For Kroger API real pricing |
| `dietaryRestrictions` | `string[]` | Optional | E.g. `["vegetarian", "vegan"]` |
| `cuisine` | `string` | Optional | Preferred cuisine (e.g. "Italian") |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | True if pipeline_status == "success" |
| `recipe` | `object` | Generated recipe with metadata |
| `validation` | `object` | Ingredient validation results |
| `budget_check` | `object` | Budget constraint check results |
| `pipeline_status` | `string` | One of: `success`, `validation_failed`, `budget_exceeded`, `input_rejected`, `generation_failed`, `error` |
| `iterations` | `number` | Number of regeneration loops used |
| `retrieved_context_count` | `number` | Number of database recipes retrieved |
| `timestamp` | `string` | ISO 8601 UTC timestamp |

## Status Codes

| Code | Scenario |
|------|----------|
| **200** | Pipeline succeeded - recipe is valid and within budget |
| **202** | Recipe generated but validation/budget issues exist (partial success) |
| **400** | Invalid input - rejected by validation |
| **500** | Internal pipeline error during generation/validation |
| **502** | External service error (Kroger API, etc.) |

## Pipeline Architecture

### Step 1: Input Validation
```python
validate_pipeline_input(data)
# Returns: (is_valid: bool, error_msg: str, normalized_data: dict)
```

**Checks:**
- ✅ `ingredients` field exists and is non-empty list
- ✅ All ingredients are non-empty strings
- ✅ `budget` is non-negative number (if provided)
- ✅ Sanitizes whitespace and removes duplicates

**Failure:** Returns 400 with error message

### Step 2: Database Retrieval
```python
retrieve_top_k_recipes(ingredients, k=5)
# Returns: List[Recipe] - top-k matches ranked by ingredient overlap
```

**Algorithm:**
1. Query meals table for all recipes
2. Count ingredient overlap for each recipe
3. Score by: `overlap_count / total_ingredients`
4. Return top-k by score

**Used for:** Grounding context during recipe generation

### Step 3: Recipe Generation (Mocked)
```python
generate_recipe_mock(ingredients, retrieved_context, ...)
# Returns: {name, category, ingredients, instructions, ...}
```

**Currently:** Mocked with deterministic fake recipes for E2E testing

**Next:** Integrate `src.recipe_generator.generate_recipe_from_context(...)`

### Step 4: Ingredient Validation
```python
validate_recipe_output(generated_recipe, input_ingredients)
# Returns: (is_valid: bool, validation_result: dict)
```

**Algorithm:**
1. Extract ingredient list from recipe
2. For each recipe ingredient, check if it matches any input ingredient
3. Flag missing ingredients
4. Return validation status

**Failure:** Recipe uses ingredients not in input list → triggers regeneration

### Step 5: Budget Checking
```python
check_budget(recipe, budget, zip_code)
# Returns: (is_within_budget: bool, budget_check: dict)
```

**Stages:**
1. Use quick estimate from `recipe.estimated_price`
2. (Optional) If zip_code provided: Call Kroger API for real pricing

**Failure:** Recipe cost exceeds budget → triggers regeneration

### Step 6: Regeneration Loop
```python
regenerate_with_feedback(original_recipe, validation_result, budget_check, ...)
```

**Triggers on:**
- ❌ Validation failed (uses ingredients not in list)
- ❌ Budget exceeded (cost > budget)

**Max Iterations:** 3 (configurable)

**Feedback:** Previous iteration's errors are passed as context for refinement

## Current Implementation Status

### ✅ Complete
- [x] Main pipeline endpoint structure
- [x] Input validation & refusal handling
- [x] Database retrieval (top-k matching)
- [x] Ingredient validation logic
- [x] Budget checking framework
- [x] Regeneration loop infrastructure
- [x] Error handling & recovery
- [x] Response formatting
- [x] Logging & debugging

### 🔧 In Progress / Next Steps

1. **Integrate Real Recipe Generator**
   - Currently using mock for E2E testing
   - Location: `src/recipe_generator.py`
   - Function: `generate_recipe_from_context(ingredients, context, ...)`
   - Input: list of ingredients + grounding context
   - Output: structured recipe dict with ingredients_list

2. **Integrate Real Ingredient Validator**
   - Currently using simple string matching
   - Location: `src/validator.py`
   - Improve confidence score handling
   - Better ingredient canonicalization

3. **Wire Up Kroger Pricing API**
   - Currently using heuristic estimates
   - Location: `backend/kroger_pricing.py`
   - When zip_code provided: fetch real prices
   - Update budget check response

4. **Handle Edge Cases**
   - Recipe generation timeout
   - API rate limiting
   - Database connection errors
   - Invalid API responses

5. **Performance Optimization**
   - Cache database queries
   - Parallel API calls where possible
   - Reduce regeneration loops with better feedback

6. **Testing & Validation**
   - Run `testing/test_pipeline.py` for E2E tests
   - Add unit tests for each step
   - Validate response schemas

## Helper Modules

### `pipeline_helpers.py`
Utility functions for:
- Formatting recipes for AI context
- Extracting ingredients from text
- Parsing confidence scores
- Recipe cost estimation
- Response formatting

### `test_pipeline.py`
6 test scenarios covering:
- Basic pipeline
- Budget constraints
- Invalid input rejection
- Dietary restrictions
- Real pricing lookup
- Response shape validation

## Configuration

Located in `pipeline_routes.py`:

```python
MAX_REGENERATION_LOOPS = 3      # Max attempts to generate valid recipe
TOP_K_RETRIEVED = 5              # Number of database recipes to retrieve
CONFIDENCE_THRESHOLD = 0.7       # Min confidence for extracted ingredients
```

## Error Handling

### Input Rejected (400)
```json
{
  "success": false,
  "error": "ingredients list cannot be empty",
  "pipeline_status": "input_rejected",
  "timestamp": "..."
}
```

### Generation Failed (500)
```json
{
  "success": false,
  "error": "Failed to generate recipe",
  "pipeline_status": "generation_failed",
  "timestamp": "..."
}
```

### Validation Failed (202)
```json
{
  "success": false,
  "recipe": {...},
  "validation": {
    "is_valid": false,
    "missing_ingredients": ["saffron", "truffle"],
    "validation_errors": [...]
  },
  "pipeline_status": "validation_failed",
  "timestamp": "..."
}
```

## Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs in pipeline_routes.py:
- Recipe retrieval logs
- Generation attempts
- Validation results
- Budget checks
- Regeneration decisions

## Integration Checklist

- [ ] Test basic pipeline end-to-end with mocked generator
- [ ] Integrate `src/recipe_generator.py`
- [ ] Integrate `src/validator.py` with real confidence scores
- [ ] Wire up `backend/kroger_pricing.py` for zip code lookups
- [ ] Add database top-k query optimization
- [ ] Handle duplicate ingredients in input
- [ ] Add max ingredients limit
- [ ] Add recipe complexity scoring
- [ ] Performance test with large ingredient lists
- [ ] Load test regeneration loop
- [ ] Deploy to production

## Next Steps

1. **This iteration:** Confirm pipeline E2E works with mock generator
2. **Next:** Integrate real recipe generator from `src/recipe_generator.py`
3. **Then:** Add real ingredient validation with confidence scores
4. **Finally:** Hook up real pricing from Kroger API
