# Milestone 2 Grade — Venture 3: BudgetBite

**Graded:** April 8, 2026
**Deadline:** April 5, 2026 (end of day)
**Late Commits:** None — all 139 commits are on or before 4/5/2026. However, 27 commits were on deadline day (significant last-minute crunch).

---

## Overall Grade: 80/100

---

## Summary

BudgetBite has built an ambitious full-stack system: React Native/Expo frontend with camera-based ingredient recognition (Gemini Vision), a Flask backend with TheMealDB database seeding, a recipe retrieval and generation pipeline, and Kroger API integration for real-world pricing with budget tier classification. The breadth of work is impressive. However, several critical Milestone 2 deliverables are missing or incomplete — the Demo Guide is absent, 6 of 10 required test cases are empty, budget regeneration is described but not implemented in code, and the PRD was not updated to reflect the current system.

### Video Review Notes
The demo video (~2 min) shows the ingredient scanning workflow (camera → Gemini Vision → detected ingredients) and a pantry tracker. The scanning and ingredient extraction pipeline works well. The demo focused on the input side of the pipeline — recipe generation, validation, and budget enforcement were not shown in the video but exist in the codebase. The "refusal" case (photographing a blank desk) demonstrates input absence handling. Budget tier UI is present. For the final demo, the team should ensure the full end-to-end flow (scanning → recipes → budget enforcement) is shown.

---

## Category Breakdown

### 1. End-to-End Demo Path (18/25)
- Image → ingredient extraction (Gemini Vision) → recipe retrieval → generation → pricing works as a pipeline.
- React Native camera UI with budget tier selection modal is functional.
- Kroger API integration for real-world pricing is substantial and impressive work.
- 3 pricing strategies (cheapest, average_top3, first) are a nice design choice.
- **Issue:** No text input path — only image input is implemented. Milestone requires "image OR text."
- **Issue:** Budget regeneration is described in `budget_strategy.md` but NOT implemented in code. `app.py` generates once and returns the result — no regeneration loop.
- **Issue:** Hardcoded IP in `camera.tsx` (`192.168.1.x:5001`) — placeholder, not functional for others.
- **Issue:** Port inconsistency — README says 5000, `app.py` uses 5001.

### 2. Code Quality & Architecture (16/20)
- Clean backend with Flask, SQLite, RESTful routes.
- Pydantic models for structured Gemini output in ingredient extraction.
- Validator with confidence scoring and unmatched ingredient detection — well designed.
- Kroger OAuth token management with multiple pricing strategies is solid engineering.
- **Issue:** Validator has a parsing bug — flags "thinly", "shredded", "tbsp", "leaves" as unmatched ingredients (parsing artifacts, not real hallucinations).
- **Issue:** `docker-compose.yml` is empty (0 bytes).
- **Issue:** Legacy `src/` pipeline modules are somewhat disconnected from the Flask `backend/` routes.

### 3. Documentation & Deliverables (18/25)
- **MISSING:** `Milestone 2 Demo Guide.md` — the most critical missing document. `docs/Milestone-2/demo.md` exists but only contains a video link, NOT the required demo guide with steps, commands, and flows.
- **INCOMPLETE:** `mvp_test_cases.md` has 10 test case headers but the first 6 (4 success + 2 refusal) are completely empty — only budget-failure (2) and edge cases (2) have actual content.
- `mvp_results.md` present with metrics (91% extraction, 87% retrieval, 10% hallucination). ✓
- `budget_strategy.md` present with 3 tiers and Kroger API source. ✓
- Architecture diagrams (both original and updated) present. ✓
- **Issue:** PRD not updated for Milestone 2 — still references CV segmentation, doesn't mention Kroger or budget enforcement.
- `.env.example` present. ✓
- `requirements.txt` present. ✓

### 4. Evaluation Evidence (14/15)
- `mvp_results.md` reports honest metrics: 91% extraction, 87% retrieval, 10% hallucination rate, 100% refusal success, 85% budget pass.
- Budget test cases show budget tier misclassification (test 7: "expensive" tier gives "medium"; test 8: "medium" gives "cheap") — honest reporting.
- But 6 of 10 detailed test cases are empty, significantly undermining the evidence.

### 5. Repository Hygiene (18/15 — bonus for Kroger integration scope)
- `.gitignore`, `.env.example`, `requirements.txt` all present.
- README has setup instructions for both backend and frontend.
- Demo video present in `docs/Milestone-2/`.
- `demo.sh` script for end-to-end demo.

---

## Individual Grades

| Team Member | Commits | Contribution Area | Grade |
|---|---|---|---|
| KevinAdkins | 72 | Frontend (React Native camera, budget UI), retrieval pipeline, integration | 90/100 |
| David Abundis (dabun01) | 63 | Backend (Flask, Kroger pricing, DB seeding, routes), recipe generator | 90/100 |
| Orange-Juice03 (Alvaro) | 28 | Database seeding, backend routes, ingredient extraction | 85/100 |
| RaspyPiano24270 (Eric Gerner) | 13 | Some contributions — should increase involvement for final sprint | 70/100 |
| JorgeAngelMunoz2024 (Jorge) | 12 | Early PRD work, validation commit — should increase involvement for final sprint | 72/100 |

**Note:** Kevin and David led the engineering effort. Eric and Jorge should increase their code contributions for the final demo.

---

## Key Recommendations for Sprint 2
1. Write the missing Demo Guide with exact steps, commands, and all 3 required flows.
2. Fill in the 6 empty test cases in `mvp_test_cases.md`.
3. Add text input path (not just camera/image).
4. Implement budget regeneration loop in code (not just docs).
5. Fix validator ingredient parsing bug (filtering out measurement words).
6. Update PRD to reflect current system (Kroger, budget tiers).
7. Fix port inconsistency and hardcoded IP.
8. Eric and Jorge need substantial code contributions.
