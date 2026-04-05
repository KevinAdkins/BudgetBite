# Integration Guide - How to Connect Real Components

This guide shows exactly where to integrate the real AI and pricing components into the pipeline.

## 🔌 Integration Point 1: Recipe Generator

### Current State (Mocked)
**File:** `backend/routes/pipeline_routes.py:165-185`
```python
def generate_recipe_mock(
    ingredients: List[str],
    retrieved_context: Optional[List[Dict]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    iteration: int = 1,
) -> Dict:
    """MOCKED recipe generation - returns a valid structure without AI calls."""
    # ... mock code ...
    return mock_recipe
```

### To Integrate Real Generator
**Step 1:** Find the function in pipeline_routes.py around line 200:
```python
def generate_recipe_real(
    ingredients: List[str],
    retrieved_context: Optional[List[Dict]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    iteration: int = 1,
) -> Optional[Dict]:
```

**Step 2:** Replace the placeholder with real implementation:
```python
def generate_recipe_real(
    ingredients: List[str],
    retrieved_context: Optional[List[Dict]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    iteration: int = 1,
) -> Optional[Dict]:
    """Real recipe generation using Gemini AI."""
    
    # Format context
    context = format_retrieved_recipes_for_context(retrieved_context, max_recipes=3)
    
    # Build the prompt
    prompt = f"""
    Available ingredients: {', '.join(ingredients)}
    
    Reference recipes for inspiration:
    {context}
    
    Dietary restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
    Preferred cuisine: {cuisine or 'Any'}
    
    Generate a creative recipe using ONLY the available ingredients.
    Return as JSON with fields: name, category, ingredients_list, instructions, estimated_price
    """
    
    # Call real generator
    recipe = recipe_generator.generate_recipe_from_context(
        ingredients=ingredients,
        context=context,
        prompt=prompt
    )
    
    return recipe
```

**Step 3:** Update the pipeline to use real generator (around line 476):
```python
# BEFORE:
recipe = generate_recipe_mock(...)

# AFTER:
recipe = generate_recipe_real(...)
# Or keep mock for fallback: recipe = generate_recipe_real(...) or generate_recipe_mock(...)
```

---

## 🔌 Integration Point 2: Ingredient Validator

### Current State (Simple String Matching)
**File:** `backend/routes/pipeline_routes.py:226-280`
```python
def validate_recipe_output(
    generated_recipe: Dict,
    input_ingredients: List[str],
) -> Tuple[bool, Dict]:
    """Currently uses simple string matching."""
    # ... simple validation ...
```

### To Integrate Real Validator
**Step 1:** Update the validation function:
```python
def validate_recipe_output(
    generated_recipe: Dict,
    input_ingredients: List[str],
) -> Tuple[bool, Dict]:
    """Use real validator with confidence scores."""
    
    validation_result = {
        "is_valid": False,
        "input_ingredients": input_ingredients,
        "recipe_ingredients": [],
        "missing_ingredients": [],
        "validation_errors": [],
        "confidence_scores": {},  # NEW
    }

    try:
        # Parse recipe ingredients
        recipe_ing_str = generated_recipe.get("ingredients_list", "")
        recipe_ingredients = recipe_ing_str if isinstance(recipe_ing_str, list) else recipe_ing_str.split(",")
        recipe_ingredients = [ing.strip() for ing in recipe_ingredients]
        validation_result["recipe_ingredients"] = recipe_ingredients

        # Call real validator with confidence scoring
        validator_result = validate_recipe_ingredients(
            recipe_ingredients=recipe_ingredients,
            available_ingredients=input_ingredients,
            return_confidence=True  # NEW: Get confidence scores
        )

        # Extract results
        is_valid = validator_result.get("is_valid", False)
        missing = validator_result.get("missing_ingredients", [])
        confidence_scores = validator_result.get("confidence_scores", {})

        validation_result["is_valid"] = is_valid
        validation_result["missing_ingredients"] = missing
        validation_result["confidence_scores"] = confidence_scores  # NEW

        if missing:
            validation_result["validation_errors"].append(
                f"Recipe uses ingredients not in input list: {', '.join(missing)}"
            )

        return validation_result["is_valid"], validation_result

    except Exception as e:
        validation_result["validation_errors"].append(f"Validation error: {str(e)}")
        return False, validation_result
```

---

## 🔌 Integration Point 3: Kroger Pricing API

### Current State (Heuristic Only)
**File:** `backend/routes/pipeline_routes.py:310-370`
```python
def check_budget(
    recipe: Dict,
    budget: Optional[float],
    zip_code: Optional[str],
) -> Tuple[bool, Dict]:
    """Currently uses simple estimate."""
    # ... estimate from recipe ...
    # TODO: If zip_code provided, fetch real pricing from kroger_pricing API
```

### To Integrate Real Pricing
**Step 1:** Update the budget check function:
```python
def check_budget(
    recipe: Dict,
    budget: Optional[float],
    zip_code: Optional[str],
) -> Tuple[bool, Dict]:
    """Check if recipe fits within budget using Kroger pricing if available."""
    
    budget_check = {
        "has_budget_constraint": budget is not None,
        "budget": budget,
        "estimated_cost": None,
        "is_within_budget": None,
        "message": "",
        "pricing_source": "estimate",  # Can be "estimate" or "kroger_api"
    }

    if budget is None:
        budget_check["message"] = "No budget constraint provided"
        return True, budget_check

    try:
        # Get ingredients list
        ingredients = recipe.get("ingredients_list", recipe.get("ingredients", []))
        if isinstance(ingredients, str):
            ingredients = [ing.strip() for ing in ingredients.split(",")]

        # Try real pricing if zip code provided
        if zip_code:
            try:
                pricing_result = kroger_pricing.estimate_ingredient_total(
                    ingredients=ingredients,
                    zip_code=zip_code,
                    price_strategy="average_top3"  # Average of top 3 prices
                )
                
                estimated_cost = pricing_result.get("estimated_total", 0)
                budget_check["pricing_source"] = "kroger_api"
                budget_check["estimated_cost"] = round(estimated_cost, 2)
                
                logger.info(f"✓ Got Kroger pricing: ${estimated_cost:.2f}")
                
            except Exception as e:
                logger.warning(f"Kroger API failed, falling back to estimate: {e}")
                # Fall back to heuristic
                estimated_cost = recipe.get("estimated_price", 0.0)
                budget_check["pricing_source"] = "estimate_fallback"
                budget_check["estimated_cost"] = estimated_cost
        else:
            # No zip code - use estimate
            estimated_cost = recipe.get("estimated_price", 0.0)
            budget_check["estimated_cost"] = estimated_cost

        # Check against budget
        if estimated_cost <= budget:
            budget_check["is_within_budget"] = True
            budget_check["message"] = f"Recipe cost (${estimated_cost:.2f}) is within budget (${budget:.2f})"
        else:
            budget_check["is_within_budget"] = False
            budget_check["message"] = f"Recipe cost (${estimated_cost:.2f}) exceeds budget (${budget:.2f})"
            budget_check["difference"] = round(estimated_cost - budget, 2)

        logger.info(budget_check["message"])
        return budget_check["is_within_budget"], budget_check

    except Exception as e:
        budget_check["message"] = f"Budget check error: {str(e)}"
        budget_check["is_within_budget"] = None
        logger.error(f"Budget check failed: {str(e)}", exc_info=True)
        return True, budget_check  # Soft fail
```

---

## 🔌 Integration Point 4: Database Top-K Query

### Current State (In-Memory Ranking)
**File:** `backend/routes/pipeline_routes.py:110-160`
```python
def retrieve_top_k_recipes(ingredients: List[str], k: int = 5) -> List[Dict]:
    """Currently loads all meals and ranks in memory."""
    # ... simple algorithm ...
```

### Optimization: Add Database Query
If you want to optimize for large datasets:

```python
def retrieve_top_k_recipes_optimized(ingredients: List[str], k: int = 5) -> List[Dict]:
    """Optimized top-k query using database instead of in-memory ranking."""
    
    try:
        # Build SQL query for ingredient matching
        # This assumes you add a database function
        scored_meals = database.search_by_ingredients_sql(
            ingredients=ingredients,
            limit=k
        )
        
        logger.info(f"Retrieved {len(scored_meals)} recipes from database")
        return scored_meals
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        # Fallback to in-memory version
        return retrieve_top_k_recipes(ingredients, k)
```

**Step 2:** Add to `backend/models/database.py`:
```python
def search_by_ingredients_sql(ingredients: List[str], limit: int = 5) -> List[Dict]:
    """SQL-based top-k recipe search."""
    
    with get_db_connection() as conn:
        # Build query with ingredient matching
        placeholders = " OR ".join(
            [f"ingredients LIKE ?" for _ in ingredients]
        )
        
        query = f"""
            SELECT *, 
                   (COUNT(*) FILTER (WHERE ingredients LIKE ?)) as score
            FROM meals
            WHERE {placeholders}
            ORDER BY score DESC
            LIMIT ?
        """
        
        params = [f"%{ing}%" for ing in ingredients] + [limit]
        
        results = conn.execute(query, params).fetchall()
        return [dict(row) for row in results]
```

---

## 📋 Integration Checklist

### Phase 1: Recipe Generation
- [ ] Source code location: `src/recipe_generator.py`
- [ ] Function to call: `generate_recipe_from_context(...)`
- [ ] Update: `generate_recipe_real()` function
- [ ] Test: Verify recipes use input ingredients
- [ ] Integrate: Replace `generate_recipe_mock` calls

### Phase 2: Validation
- [ ] Source code location: `src/validator.py`
- [ ] Function to call: `validate_recipe_ingredients(...)`
- [ ] Update: `validate_recipe_output()` function
- [ ] Add: Confidence score handling
- [ ] Test: Verify validation logic

### Phase 3: Pricing
- [ ] Source code location: `backend/kroger_pricing.py`
- [ ] Function to call: `estimate_ingredient_total(...)`
- [ ] Update: `check_budget()` function
- [ ] Add: Error handling for API failures
- [ ] Test: Verify pricing works with zip codes

### Phase 4: Performance
- [ ] Add database indexes on ingredients
- [ ] Benchmark current implementation
- [ ] Profile hot paths
- [ ] Implement caching if needed
- [ ] Load test with real ingredients

---

## 🧪 Testing Integration

### Test Recipe Generator
```python
from src.recipe_generator import generate_recipe_from_context

recipe = generate_recipe_from_context(
    ingredients=["chicken", "tomato", "basil"],
    context="Italian cuisine context...",
)
print(recipe)
```

### Test Validator
```python
from src.validator import validate_recipe_ingredients

result = validate_recipe_ingredients(
    recipe_ingredients=["chicken", "tomato", "basil"],
    available_ingredients=["chicken", "tomato", "basil", "oil"],
    return_confidence=True
)
print(result)
```

### Test Pricing
```python
from backend.kroger_pricing import estimate_ingredient_total

result = estimate_ingredient_total(
    ingredients=["chicken", "tomato"],
    zip_code="78207"
)
print(result)
```

---

## 🔧 Key Files to Modify

1. **`backend/routes/pipeline_routes.py`**
   - Update `generate_recipe_real()` 
   - Update `validate_recipe_output()`
   - Update `check_budget()`

2. **`backend/models/database.py`**
   - Add `search_by_ingredients_sql()` (optional optimization)

3. **`backend/routes/pipeline_helpers.py`**
   - Already has utilities for formatting context
   - May need additions for new components

---

## ⚠️ Error Handling During Integration

Each integration should handle errors gracefully:

```python
try:
    # Real implementation
    result = real_function(...)
except ImportError:
    logger.warning("Module not available, using fallback")
    result = fallback_function(...)
except Exception as e:
    logger.error(f"Integration failed: {e}")
    result = fallback_function(...)
```

---

## ✅ Verification Steps

After integrating each component:

1. Run tests: `python testing/test_pipeline.py`
2. Check logs for errors
3. Verify response structure unchanged
4. Test with various ingredient combinations
5. Monitor performance impact
6. Commit changes with clear messages

---

This guide provides the exact locations and patterns for integrating the real components! 🚀
