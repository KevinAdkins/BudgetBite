# Pipeline Architecture & Component Map

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BUDGETBITE PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────┘

CLIENT REQUEST
    │
    ├─ POST /api/pipeline/generate-recipe
    ├─ JSON: {ingredients, budget?, zipCode?, ...}
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: INPUT VALIDATION & REFUSAL HANDLING                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Check ingredients list non-empty                                          │
│ • Validate budget non-negative                                              │
│ • Normalize/sanitize all fields                                             │
│ • Reject invalid input → HTTP 400                                           │
└─────────────────────────────────────────────────────────────────────────────┘
    │ (Valid Input)
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: DATABASE RETRIEVAL (Top-K Matching)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Query: SELECT * FROM meals WHERE ...                                      │
│ • Score: overlap_count / total_ingredients                                  │
│ • Sort: By overlap score descending                                         │
│ • Return: Top-5 recipes as grounding context                                │
│                                                                              │
│ Examples retrieved:                                                          │
│   1. Chicken Parmesan (87% match)                                           │
│   2. Chicken Stir Fry (72% match)                                           │
│   3. Chicken Salad (65% match)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    └──────────────────────────┐
                               ▼
            ┌──────────────────────────────────────────────────────┐
            │ REGENERATION LOOP (MAX 3 ITERATIONS)                │
            ├──────────────────────────────────────────────────────┤
            │                                                      │
            │  ITERATION 1, 2, 3 (as needed):                     │
            │                                                      │
            │  ┌──────────────────────────────────────────────┐   │
            │  │ STEP 3: RECIPE GENERATION                   │   │
            │  ├──────────────────────────────────────────────┤   │
            │  │ Input:                                       │   │
            │  │  • ingredients: ["chicken", "tomato"]        │   │
            │  │  • context: Top-5 retrieved recipes          │   │
            │  │  • iteration: feedback from previous attempt │   │
            │  │                                              │   │
            │  │ Output:                                      │   │
            │  │  • name, category                            │   │
            │  │  • ingredients_list                          │   │
            │  │  • instructions                              │   │
            │  │  • estimated_price                           │   │
            │  │  • metadata                                  │   │
            │  │ [Currently: Mocked | Ready: For AI]          │   │
            │  └──────────────────────────────────────────────┘   │
            │                                                      │
            │  ┌──────────────────────────────────────────────┐   │
            │  │ STEP 4: INGREDIENT VALIDATION               │   │
            │  ├──────────────────────────────────────────────┤   │
            │  │ • Parse recipe ingredients                   │   │
            │  │ • Compare to input ingredients               │   │
            │  │ • Check for missing/unexpected items         │   │
            │  │                                              │   │
            │  │ Result:                                      │   │
            │  │  ✓ Valid: All recipe ingredients in input    │   │
            │  │  ✗ Invalid: Recipe uses extra ingredients    │   │
            │  │ [Currently: Simple | Ready: For Validator]   │   │
            │  └──────────────────────────────────────────────┘   │
            │                                                      │
            │  ┌──────────────────────────────────────────────┐   │
            │  │ STEP 5: BUDGET CHECKING                      │   │
            │  ├──────────────────────────────────────────────┤   │
            │  │ • Calculate: recipe cost                      │   │
            │  │ • Source 1: estimate (heuristic)             │   │
            │  │ • Source 2: Kroger API (if zip code given)   │   │
            │  │ • Compare: cost vs user budget               │   │
            │  │                                              │   │
            │  │ Result:                                      │   │
            │  │  ✓ OK: cost ≤ budget                         │   │
            │  │  ✗ Over: cost > budget                       │   │
            │  │ [Currently: Heuristic | Ready: For Pricing]  │   │
            │  └──────────────────────────────────────────────┘   │
            │                                                      │
            │  BOTH VALID + WITHIN BUDGET?                       │
            │       ├─ YES → EXIT LOOP (SUCCESS!)                │
            │       └─ NO  → REGENERATE with feedback             │
            │                (if iteration < 3)                   │
            │                                                      │
            └──────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────────────────┐
        │ STEP 6: PREPARE FINAL RESPONSE                       │
        ├─────────────────────────────────────────────────────┤
        │ • Determine pipeline_status based on final state     │
        │ • Assemble recipe object                            │
        │ • Add validation results                            │
        │ • Add budget check results                          │
        │ • Include iteration count                           │
        │ • Add timestamp                                     │
        └─────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────────────────┐
        │ STEP 7: RETURN RESPONSE                              │
        ├─────────────────────────────────────────────────────┤
        │ HTTP 200:  Success (valid + within budget)          │
        │ HTTP 202:  Partial (generated but issues remain)    │
        │ HTTP 400:  Bad input (rejected)                     │
        │ HTTP 500:  Server error (generation failed)         │
        └─────────────────────────────────────────────────────┘
                            │
                            ▼
                    CLIENT RESPONSE
```

## 📦 Component Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE ROUTES                              │
│  (backend/routes/pipeline_routes.py)                            │
└─────────────────────────────────────────────────────────────────┘
         │                                                             
         ├─────────────────────────┬──────────────────────┬──────────┤
         │                         │                      │          │
         ▼                         ▼                      ▼          ▼
    ┌─────────────┐          ┌──────────────┐    ┌────────────┐ ┌─────────┐
    │   FLASK     │          │  DATABASE    │    │   PULL     │ │ HELPERS │
    │  (routes)   │          │  (models)    │    │  (utils)   │ │ (utils) │
    └─────────────┘          └──────────────┘    └────────────┘ └─────────┘
         │                         │                   │             │
         └─────────┬───────────────┴─────────────────┬─┴─────────────┘
                   │                                 │
                   ▼                                 ▼
          ┌──────────────────────┐    ┌──────────────────────────────┐
          │    DATA LAYER        │    │    INTEGRATION POINTS        │
          ├──────────────────────┤    ├──────────────────────────────┤
          │ • meals.db (SQLite)  │    │ • src/recipe_generator.py    │
          │ • queries            │    │ • src/validator.py           │
          │ • caching            │    │ • src/retrieval.py           │
          └──────────────────────┘    │ • kroger_pricing.py          │
                                      └──────────────────────────────┘
                                           (Ready for integration)
```

## 📊 Request/Response Flow Example

### Example 1: Successful Pipeline (200)

```
REQUEST:
{
  "ingredients": ["chicken", "rice", "garlic"],
  "budget": 12.00
}

└─ PIPELINE EXECUTION ─────────────────────────────────────┘

Step 1: Input Validation ..................... ✓ PASS
Step 2: Database Retrieval (Top-5) .......... ✓ PASS (found 3 similar)
Step 3: Recipe Generation (Iter 1) ......... ✓ PASS
Step 4: Ingredient Validation .............. ✓ PASS
Step 5: Budget Check ........................ ✓ PASS
Exit Regeneration Loop ...................... ✓ SUCCESS

RESPONSE (200):
{
  "success": true,
  "recipe": {
    "name": "Creative Asian Dish with Chicken",
    "category": "Asian",
    "ingredients": ["chicken", "rice", "garlic"],
    "instructions": "1. Prepare... 2. Cook... 3. Serve...",
    "estimated_price": 10.50
  },
  "validation": {
    "is_valid": true,
    "recipe_ingredients": ["chicken", "rice", "garlic"],
    "missing_ingredients": []
  },
  "budget_check": {
    "is_within_budget": true,
    "budget": 12.00,
    "estimated_cost": 10.50,
    "message": "Recipe cost ($10.50) is within budget ($12.00)"
  },
  "pipeline_status": "success",
  "iterations": 1
}
```

### Example 2: Budget Exceeded → Regenerated (202)

```
REQUEST:
{
  "ingredients": ["salmon", "caviar", "truffles"],
  "budget": 20.00
}

└─ PIPELINE EXECUTION ─────────────────────────────────────┘

Iter 1:
  Step 3: Recipe Generation ............... ✓ PASS
  Step 4: Ingredient Validation .......... ✓ PASS
  Step 5: Budget Check ................... ✗ FAIL (cost=$45, budget=$20)
  → Regenerate with feedback

Iter 2:
  Step 3: Recipe Generation (refined) .... ✓ PASS
  Step 4: Ingredient Validation .......... ✓ PASS
  Step 5: Budget Check ................... ✗ FAIL (cost=$32, budget=$20)
  → Regenerate with feedback

Iter 3:
  Step 3: Recipe Generation (refined) .... ✓ PASS
  Step 4: Ingredient Validation .......... ✓ PASS
  Step 5: Budget Check ................... ✗ FAIL (cost=$28, budget=$20)
  → Max iterations reached, return best attempt

RESPONSE (202 - Partial Success):
{
  "success": false,
  "recipe": {...},
  "budget_check": {
    "is_within_budget": false,
    "budget": 20.00,
    "estimated_cost": 28.00,
    "message": "Recipe cost ($28.00) exceeds budget ($20.00)."
  },
  "pipeline_status": "budget_exceeded",
  "iterations": 3
}
```

### Example 3: Invalid Input (400)

```
REQUEST:
{
  "ingredients": []  # EMPTY!
}

└─ PIPELINE EXECUTION ─────────────────────────────────────┘

Step 1: Input Validation .................... ✗ FAIL
        "ingredients list cannot be empty"

RESPONSE (400 - Bad Request):
{
  "success": false,
  "error": "ingredients list cannot be empty",
  "pipeline_status": "input_rejected"
}
```

## 🔄 State Transitions

```
INPUT REQUEST
    │
    ▼
[Validation] ──INVALID──> 400 ERROR (input_rejected)
    │ VALID
    ▼
[Generation] ──FAILED──> 500 ERROR (generation_failed)
    │ SUCCESS
    ▼
[Validation] ──INVALID──> Try Regeneration
    │ VALID
    ▼
[Budget Check] ──EXCEEDED──> Try Regeneration
    │ OK
    ▼
    200 SUCCESS (success)

Regeneration:
    ├─ Max iterations reached?
    │   ├─ YES ──> 202 PARTIAL (validation_failed/budget_exceeded)
    │   └─ NO  ──> Loop back to [Generation]
    └─ (with feedback from previous errors)
```

## 📈 Operations & Monitoring

### Metrics to Track
```
- Requests per minute
- Average iterations needed
- Pass rate by validation/budget
- Average response time
- Error rate by type
- Database query times
- API call latencies (for Kroger, AI generator)
```

### Logs to Monitor
```
[INFO] Retrieved 3 matching recipes from database (top-5)
[INFO] Generated MOCK recipe (iteration 1): Creative Mixed Dish
[INFO] Validation result: valid=True, missing=0
[DEBUG] Budget check passed: $12.50 <= $15.00
[INFO] Pipeline complete: success (iterations=1)

[WARN] Kroger API failed, falling back to estimate
[ERROR] Recipe generation timeout after 10s
[CRITICAL] Database connection lost
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All components integrated (recipe generator, validator, pricing)
- [ ] Performance tested with realistic data
- [ ] Error handling verified for all failure paths
- [ ] Rate limiting configured
- [ ] Database optimized (indexes, query tuning)
- [ ] Monitoring/alerting setup

### Post-Deployment
- [ ] Monitor error rates
- [ ] Track iteration counts (should improve over time)
- [ ] Monitor API latencies
- [ ] Gather user feedback
- [ ] Plan optimizations based on metrics

## 📚 Related Documentation

- **PIPELINE_QUICKSTART.md** - Get started in 3 steps
- **PIPELINE_GUIDE.md** - Complete technical reference  
- **INTEGRATION_GUIDE.md** - Step-by-step integration
- **PIPELINE_IMPLEMENTATION_SUMMARY.md** - Full overview

---

This architecture provides a **robust, extensible foundation** for recipe generation with built-in error recovery and regeneration loops. 🎉
