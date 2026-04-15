# Sprint 3 Plan — Venture 3: BudgetBite

**Sprint Duration:** April 15 – April 21, 2026
**Sprint Goal:** Close the Sprint 2 documentation gaps, unify the text input path with the full pipeline, and run a clean end-to-end rehearsal of the April 29 demo.
**Final Demo:** April 29, 2026

---

## Context

Sprint 2 shipped the hard engineering: budget regeneration is real code, the validator parsing bug is fixed, text input exists, the camera IP is env-driven, and the refusal flow is documented and tested. The sprint fell short on three P0 documentation tasks (Demo Guide, PRD update, test case backfill) and on making the text input path flow through the full validation + pricing + regeneration pipeline.

Sprint 3 is the last sprint where new work can land comfortably. Sprint 4 should be polish and rehearsal only. That means the P0 carryovers and the text-path unification have to land this week.

The final demo on April 29 is the opportunity to show that the recipe + validation + budget workflows all work end to end, not just the receipt scanner. Every P0 below maps directly to something the graders will look for on demo day.

---

## Sprint 3 Tasks

### P0 — Final Demo Blockers (Days 1–3)

| Task | Owner | Description |
|---|---|---|
| Write Final Demo Guide | Jorge | Create `docs/Final Demo Guide.md` with exact shell commands, env vars, ports, and step-by-step scripts for all three flows: success (image + text), refusal (empty or incoherent input), and budget failure (too-expensive recipe triggers regeneration). Include expected output snippets. |
| Backfill test cases 1–6 | Jorge | Fill in test cases 1–6 in `docs/Milestone-2/mvp_test_cases.md` with real inputs, extracted ingredients, retrieved recipes, generated output, validation result, budget result, and pass/fail. Screenshots where relevant. |
| Update PRD | Jorge | Update `docs/PRD.md` to describe the implemented system: Gemini Vision extraction (remove all CV segmentation language at lines 57–58), Kroger API pricing, budget tier classification, regeneration loop, refusal handling. |
| Unify text input with full pipeline | Kevin + David | Refactor `backend/app.py::analyze_text()` to call the same validation + Kroger pricing + budget regeneration helpers as the image path. Right now text input only returns recipe matches. Target: one shared internal function that both endpoints call after ingredient ingestion. |

### P1 — Evaluation Evidence (Days 2–5)

| Task | Owner | Description |
|---|---|---|
| Re-run budget tier test cases 7 and 8 | Alvaro | With the `7b4aa19` tier boundary fix in place, re-run the expensive and medium test cases. Document the corrected Tier output in `mvp_test_cases.md` and note the fix commit. |
| Update `mvp_results.md` | Alvaro | Refresh the metrics table with post-fix numbers: hallucination rate after validator fix, budget pass rate after tier fix, regeneration success rate (how often regeneration brings a recipe into budget on retry). |
| README port cleanup | Eric | Fix the stale port-5000 references in `README.md` lines 137–140 and 296–302. Add a short "Text input mode" section under usage. |
| Add 3 new text-input test cases | Eric | Create test cases 11–13 in `mvp_test_cases.md` exercising the text input path: one success, one refusal (empty list), one over-budget triggering regeneration. |

### P2 — Demo Readiness (Days 4–6)

| Task | Owner | Description |
|---|---|---|
| First end-to-end rehearsal | Kevin | Run the full Final Demo Guide from a clean clone on a second machine or fresh venv. Time each flow. Record any friction in `docs/Sprint 3 Rehearsal Notes.md`. |
| Validator unit tests | Alvaro | Add a small pytest file that locks in the measurement-word fix: feed a recipe containing thinly, shredded, tbsp, leaves and assert none are reported as unmatched. Prevents regression. |
| Frontend polish pass | Kevin | Camera screen, text input screen, budget tier selector, and results view all visually consistent. Remove any debug logs. |
| Error surface review | David | Walk every error path in `app.py` and confirm each returns a clean JSON shape and a sensible HTTP status. The demo should never show a raw traceback. |

### P3 — Polish (Days 6–7)

| Task | Owner | Description |
|---|---|---|
| Presentation deck outline | Jorge | Start a slide outline for the April 29 presentation, covering problem, solution, architecture, demo, evaluation results. Draft in `docs/presentations/`. |
| Rename rehearsal video file | Eric | `Demo Rehersal Sprint 2.mp4` → `Demo_Rehearsal_Sprint_2.mp4` (spelling fix, no spaces). |
| Sprint 3 summary | Jorge | Write `docs/Sprint 3 Summary.md` at end of sprint listing what shipped and what carries into Sprint 4. |

---

## Definition of Done (Sprint 3)

- [ ] `docs/Final Demo Guide.md` exists with all three flows documented end to end
- [ ] Test cases 1–6 filled with real data; test cases 11–13 added for text input
- [ ] PRD updated, no CV segmentation language remaining
- [ ] `analyze_text()` calls the same validation + pricing + regeneration helpers as the image path
- [ ] `mvp_results.md` refreshed with post-fix metrics
- [ ] README port-5000 references gone
- [ ] At least one full rehearsal completed from a clean clone
- [ ] Validator fix covered by a unit test
- [ ] Every team member has at least one meaningful commit this sprint

---

## Contribution Expectations

Jorge is the key signal this sprint. Three P0 documentation items were assigned to him in Sprint 2 and none landed. Those same three items (slightly expanded) are P0 again here. If Jorge cannot commit to them, the team should reassign during the Monday April 15 standup, not at the end of the sprint.

Kevin and David carried the engineering in Sprint 2 and continue to own the text-path unification, which is the most technically involved item in this sprint. Alvaro owns the evaluation refresh. Eric should keep the momentum from the refusal flow work with README cleanup, new text-input test cases, and the validator unit test.

Everyone should have a visible commit by Wednesday April 17. If any member has zero commits by Friday April 19, that is the right moment to flag it internally, not on April 28.

---

## Remaining Sprints Overview

| Sprint | Dates | Focus |
|---|---|---|
| Sprint 2 | Apr 8–14 | Missing deliverables, text input, budget regeneration, bug fixes (complete) |
| Sprint 3 (this sprint) | Apr 15–21 | Close doc gaps, unify text pipeline, rehearsal #1, evaluation refresh |
| Sprint 4 | Apr 22–28 | Freeze features, rehearsal #2 and #3, slide deck, final deliverables |
| **Final Demo** | **Apr 29** | **Presentation and live demo** |
| Final Deliverables Due | May 3 | All documentation and code finalized |

---

## Risks

1. **Jorge documentation bottleneck.** Three P0 items sit on one person who was inactive after April 8. Mitigation: standup check-in Monday, reassign Wednesday if no progress.
2. **Text path divergence.** The text endpoint currently skips validation, Kroger pricing, and regeneration. If this is not unified this sprint, the April 29 demo will either skip text input or show an inconsistent pipeline.
3. **No headroom in Sprint 4.** Sprint 4 is polish and rehearsal only. Any P0/P1 slip here becomes a Sprint 4 problem, which becomes a demo-day problem.

---

## Final Demo Day Heads-Up (April 29)

Two weeks out. Rehearse toward this format during Sprint 3 and Sprint 4.

**12 minutes per team, hard cap.** I will cut you off at 12:00 to keep all 8 teams on schedule, so rehearse to 10:30 or 11:00 to leave margin. Suggested split:

1. **About 3 min: overall design.** What the product does, the core pipeline, and the architectural decisions that matter (retrieval strategy, validator or grounding approach, refusal policy). No code walkthroughs.
2. **About 4 min: individual contributions.** Every team member speaks briefly about what they personally owned this semester. Plan what you will say, roughly 45 to 60 seconds each.
3. **About 4 min: live demo of the highlights.** Pick 2 or 3 scenarios from your existing demo script. Required: at least one refusal or failure case and at least one end-to-end grounded answer. Do not spend this time on UI polish.
4. **About 1 min: Q&A**, included in the 12 minutes.

**Running order** is Venture 1 through Venture 8 in order, so BudgetBite presents third.

**Backup plan:** have a prerecorded screen capture of the working path ready in case the live demo fails. Internet or API hiccups are not an excuse on demo day.

**Slides and runbook:** not due before the presentation, but both are required artifacts in the final deliverables package due May 3. Save them under `docs/Final_Demo/` in your repo.

**Avoid:** narrating code, reading slides verbatim, skipping the refusal case, opening with missing features. Present the version you are proud of.

Rehearse the full 12 minutes end to end at least twice, at least once with a timer.
