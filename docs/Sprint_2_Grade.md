# Sprint 2 Grade — Venture 3: BudgetBite

**Graded:** April 15, 2026
**Sprint Window:** April 8 – April 14, 2026
**Commits Counted:** Team commits authored in the window (Zechun Cao / "Jacob" excluded as instructor).

---

## Overall Grade: 84/100

---

## Summary

BudgetBite made real progress on the engineering side. The budget regeneration loop (the single biggest missing feature from Milestone 2) is now wired into `backend/app.py` with `max_regeneration_attempts`, tier limits, and over/under budget checks. The text input path (`/api/analyze-text`) exists in both backend and frontend. The validator parsing bug is fixed (`src/validator.py` now filters thinly, shredded, tbsp, leaves, grated, etc.). Port standardization to 5001 is done in code, and the hardcoded IP is now env-driven (`EXPO_PUBLIC_API_BASE_URL`). Pricing tier boundaries were corrected in a targeted commit.

Where Sprint 2 fell short is documentation and test evidence. The **Demo Guide is still missing**, the **6 empty test cases in `mvp_test_cases.md` are still empty**, and the **PRD is still not updated** (still references CV segmentation, no Kroger or budget tier mention). These were the three P0 items on Jorge. None landed. Refusal flow testing (P2, Eric) was documented well. Alvaro's pricing-tier fix partially addresses the budget classification issue but is not demonstrated against the original failing test cases.

Given that all P1 engineering items shipped, the validator fix landed, and regeneration is now real code instead of a doc, this is a solid sprint. It is pulled down by three missed P0 documentation tasks.

---

## Category Breakdown

### 1. Task Completion (32/40)

**P0 — Critical Missing Deliverables**
- Demo Guide: **NOT DONE.** No `Milestone 2 Demo Guide.md` in `docs/`. `docs/Milestone-2/demo.md` still only contains a video link.
- Complete test cases: **NOT DONE.** Test cases 1–6 in `docs/Milestone-2/mvp_test_cases.md` are still empty placeholders.
- Update PRD: **NOT DONE.** `docs/PRD.md` still says "The CV segmentation model will be trained on open-source data" and has no mention of Kroger, budget tiers, or Gemini Vision.

**P1 — Missing Features**
- Text input path: **DONE.** `backend/app.py` has `analyze_text()` endpoint (commit `54c4568`, Kevin). Frontend text-input mode in `camera.tsx` (commit `46a098b`, Kevin). Note: the text path currently returns recipe matches only, not the full validation + Kroger pricing + budget-tier pipeline that the image path runs.
- Budget regeneration loop: **DONE.** Commit `93e83ac` (David) adds a real regeneration loop in `backend/app.py` with `BUDGET_TIER_LIMITS`, `_is_recipe_over_budget`, `_is_recipe_below_budget_floor`, and `max_regeneration_attempts`. Confirmed working in rehearsal video.
- Fix validator parsing bug: **DONE.** Commit `16e75dc` (Alvaro) adds `measurement_and_descriptor_terms` set covering thinly, shredded, tbsp, tsp, leaves, grated, peeled, drained, reserved, and others. The exact words flagged at M2 are now filtered.
- Fix port inconsistency: **PARTIAL.** Commit `d8533c7` (Eric) standardizes the backend to 5001. `app.py` and `EXPO_PUBLIC_API_BASE_URL` are consistent. The README still has three stale `http://localhost:5000` curl examples on lines 296–302 and a "If port 5000 is already in use" paragraph.
- Fix camera IP: **DONE.** Commits `1d6f9db`, `263232a` (David) move the base URL to `EXPO_PUBLIC_API_BASE_URL`. `camera.tsx` now uses `${process.env.EXPO_PUBLIC_API_BASE_URL}/api/analyze`.

**P2 — System Robustness**
- Refusal flow testing: **DONE.** `docs/Sprint 2 Refusal Flow Testing.md` documents 7 validation test cases against `validate_pipeline_input()` with real results. `testing/test_refusal_flow.py` exists. Good write-up.
- Budget tier accuracy: **PARTIAL.** Commit `7b4aa19` (Alvaro) adjusts tier boundaries ("25=medium and 50=expensive"). The empty test cases 7 and 8 in `mvp_test_cases.md` were not re-run to show the fix worked, so this is code-only evidence.
- Populate docker-compose: **DONE (by removal).** The empty `docker-compose.yml` was deleted in David's commit, which is an acceptable resolution.
- End-to-end demo rehearsal: **DONE.** `docs/Demo Rehersal Sprint 2.mp4` exists. (Spelling: "Rehersal".)

**P3 — Polish**
- Update README: **PARTIAL.** Formatting touched but port-5000 references still present.
- Clean up frontend: **DONE.** Camera/pantry formatting, empty-pantry messaging, dotenv refactors all landed.
- Sprint 2 summary: **NOT DONE.** No `Sprint 2 Summary.md` or equivalent write-up in `docs/`.

### 2. Code Quality (17/20)
- Regeneration loop is cleanly structured with helper functions and attempt limits capped at 5. Good.
- Validator fix is minimal and correct: extends the filter set without disturbing existing logic.
- Merge history is noisy (8 of Alvaro's 8 commits are fix/merge, David has visible conflict-resolution commits) but conflicts were resolved rather than avoided.
- `analyze_text` duplicates a subset of the image pipeline instead of calling into a shared helper. This means text input skips validation, Kroger pricing, and budget regeneration. Needs unification before the final demo.

### 3. Documentation (8/15)
- Refusal flow doc is strong.
- Demo Guide missing.
- PRD untouched.
- 6 empty test cases unchanged.
- No Sprint 2 summary.
- This is the weakest category and the main reason the grade is 84 rather than 90+.

### 4. Testing / Evaluation (12/15)
- Refusal flow: 7/7 tests passing with documented output.
- Validator fix is not backed by a unit test or a re-run against the M2 unmatched-word cases.
- Budget tier boundary fix is not backed by re-running test cases 7 and 8.
- No updated `mvp_results.md` numbers reflecting post-fix metrics.

### 5. Team Contribution (9/10)
See per-member notes below. Distribution improved over M2: Eric moved from 13 low-value commits at M2 to 5 meaningful commits including the refusal flow doc. Jorge did not pick up his assigned P0 docs work, which is the main contribution concern this sprint.

---

## Per-Task Completion Status

| Priority | Task | Owner | Status |
|---|---|---|---|
| P0 | Write Demo Guide | Jorge | Not done |
| P0 | Complete 6 empty test cases | Jorge | Not done |
| P0 | Update PRD | Jorge | Not done |
| P1 | Add text input path | Kevin | Done (but limited to matching, not full pipeline) |
| P1 | Implement budget regeneration | David | Done |
| P1 | Fix validator parsing bug | Alvaro | Done |
| P1 | Fix port inconsistency | Eric | Code done, README stale in spots |
| P1 | Fix camera IP | Kevin / David | Done |
| P2 | Refusal flow testing | Eric | Done, well documented |
| P2 | Budget tier accuracy | Alvaro | Code fix done, not re-tested against failing cases |
| P2 | Populate docker-compose | David | Resolved by removal |
| P2 | End-to-end demo rehearsal | Kevin | Done (video in docs) |
| P3 | Update README | Eric | Partial |
| P3 | Clean up frontend | Kevin | Done |
| P3 | Sprint 2 summary | Jorge | Not done |

---

## What Is Missing (Carry to Sprint 3)

1. `Milestone 2 Demo Guide.md` (or a Final Demo Guide equivalent) with exact commands, env vars, and all three flows.
2. Test cases 1–6 in `docs/Milestone-2/mvp_test_cases.md` filled with real data, screenshots, and pass/fail.
3. PRD updated to match the implemented system (Kroger, budget tiers, Gemini Vision, regeneration), remove CV segmentation language.
4. Text input path routed through the full validation + pricing + regeneration pipeline, not just recipe matching.
5. README port cleanup (lines 137–140 and curl examples at 296–302).
6. Re-run of budget tier tests 7 and 8 to confirm the `7b4aa19` fix resolves the M2 misclassification.
7. Updated `mvp_results.md` with post-fix metrics.

---

## Individual Contribution Summary

Commits in the Sprint 2 window, instructor commit excluded.

| Member | Commits | Notable Work |
|---|---|---|
| KevinAdkins | 12 | Text input endpoint (`analyze_text`), frontend text mode in `camera.tsx`, dotenv refactor, pantry UI cleanup, Sprint 2 DoD updates |
| Alvaro Gonzalez | 8 | Validator measurement-word filter (`16e75dc`), pricing tier boundary fix (`7b4aa19`), merge conflict resolution for recipe generator + app.py + validator |
| RaspyPiano24270 (Eric) | 5 | Port standardization to 5001, refusal flow testing script and documentation, pipeline cleanup |
| David Abundis / dabun01 | 6 (3 + 3) | Budget regeneration loop (`93e83ac`), camera IP moved to env file, recipe generator merges |
| JorgeMunoz | 3 | Fridge test image restoration on April 8 only; no contributions after April 8. Did not complete any of the three P0 documentation tasks assigned this sprint. |

**Red flag (indicator only, not a verdict):** Jorge was assigned three P0 items (Demo Guide, test cases, PRD) and none shipped. Per the individual grades policy, this is a signal for rebalancing in Sprint 3, not a penalty. Kevin and Alvaro should not absorb these tasks again unless the team formally agrees to reassign them.

Eric is credited for the meaningful improvement: the refusal flow work is substantive and the kind of contribution that was missing at Milestone 2.

---

## Recommendations for Sprint 3

1. Jorge picks up Demo Guide, PRD update, and test case backfill as a bundled deliverable. If Jorge cannot commit, the team should reassign today, not on April 21.
2. Wire the text input path through the full pipeline (validation + pricing + budget regeneration). Right now there are effectively two backends.
3. Re-run test cases 7 and 8 to prove the tier fix, and capture new numbers in `mvp_results.md`.
4. Rehearse the full April 29 demo flow end to end at least twice during Sprint 3 (not Sprint 4), including the refusal and budget-failure paths.
