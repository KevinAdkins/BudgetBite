# Sprint 2 Plan — Venture 3: BudgetBite

**Sprint Duration:** April 8 – April 14, 2026
**Sprint Goal:** Complete missing deliverables, add text input, implement budget regeneration, and fix validator bugs.
**Final Demo:** April 29, 2026

---

## Context

After Milestone 2, BudgetBite has an impressive full-stack system (React Native camera → Gemini Vision extraction → recipe retrieval → generation → Kroger pricing), but several critical deliverables are missing or incomplete. The Demo Guide is absent, 6/10 test cases are empty, budget regeneration exists only in docs (not code), and the validator has parsing bugs. Sprint 2 focuses on closing these gaps and making the system demo-ready.

---

## Sprint 2 Tasks

### P0 — Critical Missing Deliverables (Days 1–2)

| Task | Owner | Description |
|---|---|---|
| Write Demo Guide | Jorge | Create `/docs/Milestone 2 Demo Guide.md` with exact steps, commands, env vars, and all 3 flows (success, refusal, budget failure) |
| Complete test cases | Eric | Fill in the 6 empty test cases in `mvp_test_cases.md` (4 success + 2 refusal) with real data and screenshots |
| Update PRD | Jorge | Update PRD.md to reflect current system: Kroger API, budget tiers, Gemini Vision (remove CV segmentation references) |

### P1 — Missing Features (Days 2–5)

| Task | Owner | Description |
|---|---|---|
| Add text input path | Kevin | Add text-based ingredient input to frontend (not just camera). Support typing/pasting ingredient list |
| Implement budget regeneration | David | Add regeneration loop in `app.py`: if recipe exceeds selected budget tier, regenerate with tighter constraints (max 2 retries) |
| Fix validator parsing bug | Alvaro | Fix ingredient parser to filter out measurement words ("thinly", "shredded", "tbsp", "leaves") from unmatched ingredient detection |
| Fix port inconsistency | Eric | Standardize port (5000 or 5001) across README and `app.py` |
| Fix camera IP | Kevin | Replace hardcoded `192.168.1.x` in camera.tsx with configurable backend URL |

### P2 — System Robustness (Days 4–6)

| Task | Owner | Description |
|---|---|---|
| Refusal flow testing | Eric | Demonstrate and document the refusal path (too few/incoherent ingredients) with real test data |
| Budget tier accuracy | Alvaro | Debug budget classification (test 7: "expensive" gives "medium", test 8: "medium" gives "cheap") |
| Populate docker-compose | David | Either implement Docker setup or remove the empty file |
| End-to-end demo rehearsal | Kevin | Run full demo flow and document any remaining issues |

### P3 — Polish (Days 6–7)

| Task | Owner | Description |
|---|---|---|
| Update README | Eric | Fix all inconsistencies, ensure setup works from clean install |
| Clean up frontend | Kevin | Ensure all screens (camera, pantry, home) are polished for demo |
| Sprint 2 summary | Jorge | Document what was completed and what remains |

---

## Definition of Done (Sprint 2)

- [ ] Demo Guide exists with all 3 required flows documented
- [ ] All 10 test cases have real data (no empty cells)
- [ ] Text input path works in addition to camera
- [ ] Budget regeneration loop implemented in code
- [ ] Validator no longer flags measurement words as unmatched ingredients
- [ ] Port and IP issues resolved
- [ ] Each team member has code commits this sprint

---

## Contribution Expectations

Kevin (72) and David (63) did the heavy lifting. **Eric** (13 non-substantive commits) and **Jorge** (12, dropped off after M1) need to step up significantly. Tasks are assigned to ensure everyone contributes meaningfully.

---

## Remaining Sprints Overview

| Sprint | Dates | Focus |
|---|---|---|
| Sprint 2 (this sprint) | Apr 8–14 | Missing deliverables, text input, budget regeneration, bug fixes |
| Sprint 3 | Apr 15–21 | UI polish, additional restaurant/recipe testing, demo rehearsal |
| Sprint 4 | Apr 22–28 | Final integration, presentation prep, final deliverables |
| **Final Demo** | **Apr 29** | **Presentation and live demo** |
| Final Deliverables Due | May 3 | All documentation and code finalized |
