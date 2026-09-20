# Phase 3 — Assessments That Feel Focused, Not Intimidating — IMPLEMENTED

**Status:** AWAITING HUMAN ACCEPTANCE. All frontend gates green; backend untouched.

## Objective
Make Assessments match the Product UX implementation guide (§ Phase 3):
- **Landing screen:** skills covered, approximate duration, question count if known, what the result changes, and Start.
- **Player:** one question at a time, clear progress, Back/Next, autosave only if the backend supports it, and an exit/return-later option.
- **Results:** plain-language headline, strengths (max 3), improvement areas (max 3), and one primary next action ("Add this to my plan.").
- **Details:** raw score breakdowns / rubric / evidence live behind "View details.".
- **Honesty:** assessment status is always derived from the backend (`result.passed`, `result.integrity_status`, attempt records) — never faked or inferred client-side.

## What changed (additive only; `frontend/src/pages/AssessmentsPage.tsx`, `frontend/src/index.css`, new `frontend/scripts/check-assessments-phase3.mjs`)

### Landing screen — per-skill facts ("What you're taking")
The camera-integrity notice (kept for the webcam contract and the pinned `camera_notice` flow) is now a real landing: the skill name, a facts strip (**10 questions · About 10 minutes · Pass at 70% or more** — the true backend default `num_questions` and `PASS_THRESHOLD`), and a "What this result changes" note:
- Passing raises the skill's level and marks it **Verified** — the only way assessments affect the profile.
- Every attempt is recorded in history; below 70% or an integrity flag leaves the level unchanged.
Then the unchanged Camera integrity notice + **Cancel / Enable Camera** controls follow in the same surface (no new mode, no checker breakage).

### Player — reviewable, honestly stated
- **Back** control (`‹ Back`) appears on every run-CTA row once past question 1 (all four variants: MC answered, MC pending, free-text answered, free-text pending), so a learner can review a prior answer without losing progress. **Next** stays the primary action (`Next question ›` / `Submit assessment`).
- Progress was already real ("Question X of N" + progress bar + timer) — unchanged.
- **No fake autosave/resume:** the backend stores only final graded attempts (`assessment_attempts`) plus a session lock (`active_assessments`); there is **no partial-answer persistence**, so the guide's "autosave only if the backend supports it" condition is false and we did **not** claim/implement resume. The exit confirmation now says exactly that: answers so far are graded and saved as an attempt, unanswered questions count as zero, "SkillBridge doesn't autosave mid-attempt drafts, so there is no 'return later' resume — you can start a new attempt any time from the skill list."

### Results — headline + strengths/improvement + ONE plan action
- Plain-language headline unchanged and still backend-derived ("Assessment passed: {skill}" / "Not passed — keep learning {skill}" / integrity-violation "Assessment Ended").
- New **Strengths** (top 3 passed competencies, best-first) and **Improvement areas** (top 3 not-passed, worst-first) chips, each with the plain competency name and score, with honest fallback lines when there are none.
- **Primary next action:** **"Add {skill} to my plan"** → deep-links to the real, existing Learning page for that exact skill (`onNavigate('learning', { skillId, roleTitle })` → `LearningPage` `initialFocus`, verified self-paced-learning target / the actual in-progress path). Back to skill list and Practice review remain secondary.
- **View details** (`<details>` disclosure, chevron via CSS): the competency breakdown (full/partial coverage), integrity flags, no-concern note, and per-question review now sit behind one disclosure as required — the focus is the outcome and next action, not the rubric.

### Contract guard
`frontend/scripts/check-assessments-phase3.mjs` (new) pins the above: facts strip + real counts, "What this result changes", Back control, honest no-autosave copy, absence of autosave/resume claims, strengths/improve `.slice(0, 3)`, backend-derived headline/integrity wording, `<details>` View details, and the one `asm-plan-cta` → `onNavigate?.('learning', ...)` action.

## Gates (all green)
- Frontend contract checkers **30/30 PASS** (all 29 prior checks + new `check-assessments-phase3.mjs`; the webcam-integrity, step-4.5, scenario-phase5, learning tabs, and mentor-live pins that constrain the assessment surface are unaffected).
- `npx tsc --noEmit` clean; `npm run build` clean in 2.65s (chunk-size advisory only, pre-existing).
- Backend untouched; assessment suites re-verified `55 passed / 0 failed` (`test_assessment`, `test_final_assessment`, `test_final_assessment_exit`, `test_runtime_webcam_integrity_frontend`).

## Manual checklist
1. **Landing:** open a skill's assessment → skill name, "10 questions · About 10 minutes · Pass at 70% or more", a "What this result changes" note, then the standard Camera integrity notice with Cancel / Enable Camera. (Start follows the pinned webcam precheck flow as before.)
2. **Player:** questions one at a time with "Question X of N"; after answering Q1+, the `‹ Back` ghost button appears next to Next; clicking Back returns to the prior question with the prior selection/answer intact; Next returns to the current position; progress bar tracks correctly.
3. **Exit honesty:** End assessment → confirm dialog explains attempts are graded final-only, unanswered = zero, and there is no "return later" resume — starting fresh is the documented path.
4. **Results passed:** headline from backend, Strengths (≤3 green chips) and Improvement areas (≤3 amber chips), primary **"Add {skill} to my plan"** jumps to the Learning page for that skill, then secondary Back to skill list + Practice review; View details discloses competency breakdown + integrity + question review.
5. **Results not passed / integrity-ended / exited-early:** headline + Strengths/Improvement adapt; integrity flags and "unanswered scored as zero" notices render honestly.
6. **Regressions:** EN/AR (RTL), light/dark, 1440/768/390px; all four webcam-integrity and step-4.5 contract gates stay green; no broadcast/impact to practice, verified-skills, or mentor surfaces.

## Limitations / notes
- No live browser run performed (mirrors Phases 0–2 practice — static dist served; visual verification deferred to the checklist above).
- `frontend/scripts/practice-git-python-sql.spec.mjs` still cannot run (undeclared `@playwright/test`) — unchanged.
- Backend deliberately untouched: assessments already gate on the backend trial and store only final attempts, so no new attempt storage, no endpoint changes, and the 14 pre-existing backend failures are neither masked nor extended.

## Next phase
Await approval before starting Phase 4 (per the guide).