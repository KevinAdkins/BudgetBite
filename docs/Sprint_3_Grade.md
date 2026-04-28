# Sprint 3 Grade, Venture 3: BudgetBite

**Graded:** April 28, 2026
**Sprint Window:** April 15 – April 24, 2026 (extended from April 21)
**Final Demo:** April 29, 2026
**Final Deliverables Due:** May 3, 2026

---

## Overall Grade: 87/100

**Note on individual grades:** This is the venture-level grade. Members who severely under-contributed during Sprint 3 may receive a reduced individual grade applied separately.

---

## Summary

Sprint 3 unified the text input path with the full pipeline (the largest technical task in the plan), closed every Sprint 2 documentation carryover, and produced the team's first end-to-end timed rehearsal. Both `analyze_image()` and `analyze_text()` in `backend/app.py` now call a shared `_analyze_ingredients_pipeline()` helper, so the text input flows through validation, Kroger pricing, and budget regeneration just like image input does. The Final Demo Guide, PRD update, test cases 1-6, Sprint 3 Summary, and slide deck outline all landed. The team also recorded a timed rehearsal video and committed rehearsal notes. Two real test files appeared in `tests/`: `test_batch_extract.py` and `test_ground_truth_extraction.py`, both backing the Gemini extraction work.

Contribution remained Kevin-heavy (14 commits) and David-heavy (7 plus 2 as dabun01). Jorge's three Sprint-2-carryover P0 doc tasks (Demo Guide, PRD update, Sprint 3 Summary) all landed, but in a single Apr 21 commit on the last day of the original sprint window, repeating the Sprint 2 pattern of doc work landing all at once. Eric (RaspyPiano24270) shipped one Sprint 3 commit, Alvaro shipped four through his two GitHub identities. The Copilot SWE agent produced two automated commits.

The grade sits at 87 because:
1. The README still has port-5000 references on line 141 even though the dev server runs on 5001 (P1 task missed).
2. The text-input test cases (11-13) the plan called for are not visible in `mvp_test_cases.md`.
3. The post-fix `mvp_results.md` numbers refresh is partial.
4. Documentation work continues to concentrate in last-minute commits rather than spread across the sprint.

None of these are demo-blocking. The text-path unification, validator unit tests, and rehearsal evidence are the strong signals.

---

## Category Breakdown

### 1. Task Completion (34/40)

**P0 (4 of 4 complete):**
- Final Demo Guide: shipped as `docs/final-demo-guide.md`.
- Test cases 1-6 backfilled: shipped (Jorge Apr 21, large commit).
- PRD update: shipped. "No CV segmentation model is used" now in PRD; pipeline matches implemented Gemini Vision + Kroger flow.
- Text input unified with full pipeline: shipped. Both endpoints call `_analyze_ingredients_pipeline()`. This is the single most important Sprint 3 task and it landed cleanly.

**P1 (2 of 4 complete):**
- Re-run budget tier test cases 7 and 8: partial. `mvp_results.md` mentions tier classifier is correct on boundary cases but full 20-test rerun was not executed.
- Update `mvp_results.md` with post-fix numbers: partial.
- README port-5000 cleanup: not done. Line 141 still says "If port 5000 is already in use, you can change it by modifying `app.py`" (the actual port is 5001).
- 3 new text-input test cases (11-13): not visible in `mvp_test_cases.md`.

**P2 (4 of 4 complete):**
- First end-to-end rehearsal: shipped (`Sprint_3_Rehearsal_notes.md` + timed rehearsal video, 3:26).
- Validator unit tests: shipped (`tests/test_batch_extract.py`, `tests/test_ground_truth_extraction.py`).
- Frontend polish pass: shipped (saved-recipes feature, analysis result type refactor, requirements consolidation).
- Error surface review: shipped (David's `Update PRD status` and analyze-text error path commits).

**P3 (3 of 3 complete):**
- Presentation deck outline: shipped (`docs/BudgetBite-slidedeck-outline.pdf`).
- Rename rehearsal video: shipped (`Demo_Rehearsal_Sprint_2.mp4`).
- Sprint 3 Summary: shipped (`docs/Sprint 3 Summary.md`).

### 2. Code Quality (17/20)

- `_analyze_ingredients_pipeline()` is a clean shared helper. Both endpoints pass through it cleanly.
- `tests/` has real ground-truth test infrastructure now, not stubs.
- Pricing routes consolidated, frontend types refactored.
- Two auto-bot merge commits in the history (`copilot-swe-agent[bot]`). Acceptable for conflict resolution but worth noting.

### 3. Documentation (13/15)

- Final Demo Guide is concrete and step-by-step.
- PRD reflects the implemented system.
- Sprint 3 Summary lists what shipped clearly.
- README port reference is stale and contradicts the running app. This is the kind of detail a grader will catch.

### 4. Testing / Evaluation (14/15)

- Two real pytest files for batch extraction and ground truth.
- Rehearsal video is concrete evidence of an end-to-end run.
- `mvp_results.md` post-fix numbers are partial.

### 5. Team Contribution (9/10)

| Member | In-window Commits | Sprint 3 Work | Signal |
|---|---|---|---|
| KevinAdkins | 14 | Saved-recipes feature, frontend polish, requirements, README touchups | Strong |
| David Abundis (David) | 7 + 2 (dabun01) | PRD revision, text input feature, error path tests | Strong |
| Alvaro Gonzalez (Alvaro) | 2 + 2 (Orange-Juice03) | Validator regression test, pricing routes, typo fixes | Active |
| RaspyPiano24270 (Eric) | 1 | Sprint 3 task completion (single commit) | Light |
| JorgeMunoz (Jorge) | 1 | Sprint 3 deliverables consolidation (single large commit covering Demo Guide, PRD update, Sprint 3 Summary, slide outline) | Light but the doc work did land |

Eric's contribution is the lightest. Jorge's work pattern continues to be one big commit at the end of the sprint rather than incremental progress across the week.

---

## Per-Task Completion Status

| Priority | Task | Owner | Status |
|---|---|---|---|
| P0 | Write Final Demo Guide | Jorge | Done |
| P0 | Backfill test cases 1-6 | Jorge | Done |
| P0 | Update PRD | Jorge / David | Done |
| P0 | Unify text input with full pipeline | Kevin + David | Done |
| P1 | Re-run budget tier test cases 7 and 8 | Alvaro | Partial |
| P1 | Update mvp_results.md | Alvaro | Partial |
| P1 | README port cleanup | Eric | Not done |
| P1 | Add 3 new text-input test cases (11-13) | Eric | Not visible |
| P2 | First end-to-end rehearsal | Kevin | Done |
| P2 | Validator unit tests | Alvaro | Done |
| P2 | Frontend polish pass | Kevin | Done |
| P2 | Error surface review | David | Done |
| P3 | Presentation deck outline | Jorge | Done |
| P3 | Rename rehearsal video | Eric | Done |
| P3 | Sprint 3 summary | Jorge | Done |

---

## Definition of Done (Sprint 3) Check

- [x] `docs/Final Demo Guide.md` exists with all three flows
- [~] Test cases 1-6 filled with real data; test cases 11-13 added for text input (1-6 done, 11-13 not visible)
- [x] PRD updated, no CV segmentation language remaining
- [x] `analyze_text()` calls same validation + pricing + regeneration helpers as image path
- [~] `mvp_results.md` refreshed with post-fix metrics (partial)
- [ ] README port-5000 references gone
- [x] At least one full rehearsal completed from a clean clone (timed at 3:26)
- [x] Validator fix covered by a unit test
- [x] Every team member has at least one meaningful commit this sprint

---

## Items to Complete by May 3 (Final Deliverables)

The May 3 package is required to be under `docs/Final_Demo/` in the repo. Save the following items there:

1. **Final demo slides** (PDF or PPTX) under `docs/Final_Demo/`. The existing `BudgetBite-slidedeck-outline.pdf` is a starting point. Cover: problem (budget cooking), Gemini Vision extraction, Kroger pricing, budget tier classification, regeneration loop, evaluation results.
2. **Runbook** at `docs/Final_Demo/Runbook.md`. Cover: prerequisites (Python, env vars including KROGER_ZIP_CODE), how to start backend (`python backend/app.py`), how to start frontend, how to use both image and text input modes, how to read budget tier output and regeneration results, common errors.
3. **Final demo video** at `docs/Final_Demo/Final_Demo_Video.mp4`. The existing `BudgetBite_Timed_Rehearsal_Sprint_3.mp4` is a starting point but record a polished cut for the final package.
4. **Final code on `main`**. Confirm `main` reflects the demo state.

Sprint 3 carryovers worth closing in the same window:

5. **Fix README port-5000 references**. Lines 137-140 and 296-302 still say port 5000; the app runs on 5001.
6. **Add text-input test cases 11-13** to `mvp_test_cases.md`: one success, one refusal (empty list), one over-budget triggering regeneration. The text path is unified now, so these are easy to exercise.
7. **Refresh `mvp_results.md` with post-fix metrics**. Validator-fix hallucination rate, post-tier-fix budget pass rate, and the regeneration success rate (how often regeneration brings a recipe into budget on retry). The numbers exist in your test runs, just need to be written into the doc.
