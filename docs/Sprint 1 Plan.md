### 1. Verify Ingredient Extraction Accuracy
- Improve validation to ensure extracted ingredients are correct
- Handle:
  - incorrect detections
  - missing ingredients
- Consider:
  - confidence thresholds
  - filtering or correction mechanisms

---

### 2. Enforce Budget Constraints with Regeneration
- Validate generated recipe against budget tier
- If recipe exceeds budget:
  - regenerate with stricter constraints
- Ensure final output:
  - respects budget limits
  - is clearly labeled if constraints fail
