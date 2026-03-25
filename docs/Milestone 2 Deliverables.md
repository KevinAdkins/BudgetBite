# Milestone 2 Deliverables
## Team: BudgetBite
### Focus: MVP of a Grounded, Budget-Aware Recipe Assistant

---

## Context

Milestone 1 established the project direction: grounded recipe recommendation from detected or provided ingredients.

Sprint 1 was intended to strengthen:
- ingredient extraction accuracy
- budget enforcement with regeneration

One week from today, you are due for **Milestone 2**, which is the **MVP checkpoint**.

At Milestone 2, the question is no longer "Do the pieces exist?"

The question is:

> Can the team reliably demonstrate one end-to-end MVP workflow that is grounded, validated, and budget-aware?

---

# Milestone 2 Objective

By Milestone 2, your team must demonstrate an MVP that supports:

1. Ingredient input from image **or** text
2. Ingredient normalization into a canonical list
3. Retrieval of top-k candidate recipes from a structured recipe database
4. Grounded recipe generation using only retrieved context
5. Validation against the detected/provided ingredient list
6. Refusal when ingredients are insufficient for a coherent recipe
7. Budget check on the final recipe
8. Regeneration or fallback when the recipe exceeds the selected budget tier

This milestone is about **integration and reliability**, not adding unrelated features.

---

# 1. Required MVP Workflow

You must be able to demo the following sequence live:

Image or text input
-> ingredient extraction / parsing
-> ingredient normalization
-> recipe retrieval
-> grounded generation
-> validation
-> budget check
-> final recipe or refusal / budget fallback

## Minimum accepted user flows

You must support at least these two scenarios:

### A. Valid Recipe Flow
- User provides ingredients
- System retrieves matching recipes
- System generates a grounded recipe
- System validates no unsupported ingredients were added
- System checks price against a budget tier
- System returns a recipe that passes validation and budget rules

### B. Failure / Refusal Flow
- User provides too few or incoherent ingredients
- System refuses cleanly or asks for additional ingredients

### C. Budget Failure Flow
- Initial generated recipe exceeds budget
- System either:
  - regenerates under stricter budget constraints, or
  - returns a clear failure state explaining that budget could not be met

---

# 2. MVP Functional Requirements

## A. Input

Support at least one of the following:
- image input
- text ingredient list input

If image input is used, the extraction must be stable enough to demo repeatedly.

## B. Ingredient Normalization

You must convert user-provided or detected ingredients into a normalized list.

Examples:
- "green onions" -> "scallion"
- "tomatoes" -> "tomato"
- packaged or noisy labels should be simplified when possible

## C. Retrieval

The system must:
- retrieve top-k recipes from the structured recipe database
- show the retrieved candidates
- use those retrieved recipes as the grounding context for generation

## D. Grounded Generation

The generator must:
- use retrieved recipes as context
- avoid invented ingredients
- label any assumed basics explicitly if allowed

## E. Validation

The system must validate:
- ingredients used in output are supported by the input list
- unsupported ingredients are flagged
- the recipe is blocked or marked invalid if hallucinations are found

## F. Budget Enforcement

You must implement:
- at least 2 budget tiers
- a documented cost calculation approach
- recipe budget validation
- regeneration or failure handling when over budget

---

# 3. Required Deliverables

Submit the following in the repository by Milestone 2:

- `/docs/Milestone 2 Demo Guide.md`
- `/docs/mvp_test_cases.md`
- `/docs/mvp_results.md`
- `/docs/budget_strategy.md`
- `/docs/updated_architecture.png` or an updated `/docs/architecture.png`
- updated `/docs/PRD.md`
- updated `README.md`

## A. `/docs/Milestone 2 Demo Guide.md`

Must include:
- exact demo steps
- exact commands to run
- required environment variables
- which input example(s) to use
- one valid flow
- one refusal flow
- one budget failure or regeneration flow

## B. `/docs/mvp_test_cases.md`

Include at least 10 focused MVP tests:
- 4 successful recipe cases
- 2 refusal cases
- 2 budget-failure cases
- 2 edge cases

For each case include:
- input
- normalized ingredients
- retrieved recipe(s)
- generated output summary
- validation result
- budget result
- pass/fail

## C. `/docs/mvp_results.md`

Summarize actual observed outcomes, not target claims.

Include:
- extraction accuracy summary
- retrieval relevance summary
- hallucination count/rate
- refusal success rate
- budget pass rate
- regeneration success rate
- known failures

## D. `/docs/budget_strategy.md`

Document:
- chosen budget tiers
- threshold values
- pricing source or heuristic
- what happens when pricing data is missing
- regeneration strategy

---

# 4. Engineering Expectations

Your repository must reflect a clean MVP path.

## Required engineering quality

- README setup must match the actual ports and commands used by the app
- the main demo must run without contradictory instructions
- source files must match the names referenced in docs
- failures must be handled explicitly, not hidden
- reported metrics must come from actual runs

## Not acceptable for Milestone 2

- a demo that only works with pre-generated files and no explanation
- a budget feature that exists only as an isolated endpoint
- a refusal feature described in docs but not implemented
- reported evaluation that omits runtime failures, missing files, or quota issues
- unrelated feature work taking priority over the MVP path

---

# 5. Required Live Demo

In class, your team must demonstrate:

1. A successful end-to-end grounded recipe flow
2. A refusal case
3. A budget overrun case with regeneration or explicit fallback
4. The validation result that shows whether unsupported ingredients were introduced
5. The retrieved recipe context used to ground generation

If you cannot show budget enforcement inside the recipe workflow, Milestone 2 is incomplete.

---

# 6. Milestone 2 Standard

By Milestone 2, the project should clearly communicate:

> We can take ingredients from a user, retrieve grounded recipe candidates, generate a validated recipe, and enforce a budget-aware MVP workflow.

That is the expected senior-level MVP standard for next week.
