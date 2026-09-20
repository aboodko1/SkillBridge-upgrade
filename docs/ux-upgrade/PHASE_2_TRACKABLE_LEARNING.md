# Phase 2 — Learning Plan as a Trackable Journey — IMPLEMENTED

**Status:** AWAITING HUMAN ACCEPTANCE. All frontend gates green; backend untouched.

## Objective
Make the personalized learning plan read as a trackable journey, per the Product UX implementation guide (§ Phase 2):
- "Continue your plan" hero = current lesson + estimated time + purpose + ONE CTA "Continue learning".
- Path map = 5–8 visible milestones, one state each (completed / current / upcoming / locked / needs review).
- Lesson screen = Learn → Example → Practice → Mini check, one active section at a time, completed sections revisitable.
- Plan details optional drawer **(kept: topics + stages inline; long paths capped with a "Show more" disclosure instead of a drawer)**.
- Clearly distinguish plan progress from Verified Skill (never imply reading verifies).
- Plain-language score explanations + unobtrusive "Why this?" beside coverage/match scores.
- Useful empty states (no role / no diagnostic / no path / no lessons) each with one resolving action.
- Existing backend endpoints reused; **no new persisted field** (migration avoided), no fake timers/streaks/completion.

## What changed (additive only; `frontend/src/pages/LearningPage.tsx`, `frontend/src/components/learning.tsx`, `frontend/src/index.css`)

### Journey hero — "Continue your plan" (`journey-band`)
Replaces the raw hero with a resolved single-card band driven by real state; every branch has exactly one action:
1. **In-progress plan → `CurrentLessonCard`:** current lesson title (first not-done topic), purpose line (`Added because your diagnostic score was N%.`), `~N min` estimate, and the ONE primary CTA **Continue learning** → opens that lesson, chooses current lesson, starts its hidden `ready` lesson (mirrors `openLessonTopic`). "N other plans still in progress" note stays beside the card.
2. **Gap with no path yet → "No plan yet":** CTA **Start a diagnostic** → `startLearning` (never fakes a plan).
3. **Paths ready, none started → "Your learning plans are ready":** CTA **Start your first topic**.
4. **No gaps, no target → "Pick a target role":** CTA → Skills & Roles.
5. **No gaps, target set → "You're up to date":** CTA → all modules.
All branches are gated on `pathsLoaded` so the empty-state never flashes while `personalizedPath` results are in flight.

### Path map — milestone chips (`pp-timeline`)
- Each topic row and each stage row now carries a **`MilestoneChip`** with one derived state:
  - `completed` (green) — done topic / done stage;
  - `current` (indigo) — first not-done topic (`is-current` row highlight too);
  - `needs review` (amber) — current topic whose lesson is `in_progress` AND has a failed `mini_check_result` (real backend data via `api.lessonGet`);
  - `upcoming` (slate) — locked stages gate to `locked`; final-assessment stage = `upcoming` until reached.
- Derivations use only persisted state (`path.progress`, `learning_lessons.state`, `lesson.mini_check_result`) — **no backend change**.
- Paths longer than 8 items show the first 8 + **Show all N more topics** disclosure (the guide's "5–8 visible, rest below" without a modal).
- The pinned practice spec `.continue-card` grid is untouched below the panel.

### Lesson screen — one active section, completed sections revisitable
- Tab lock removed (`disabled={isCompleted && t !== tab}` deleted): a completed lesson's Learn / Example / Practice / Mini Check sections are clickable again — revisitable, satisfying "completed sections revisitable".
- The pinned Practice/Mini-Check submit `disabled={practiceSubmitting || isCompleted}` remains — you cannot re-grade an already-completed lesson, only revisit.

### "Why this?" — unobtrusive plain-language explanations (`WhyThis`)
Collapsible, `.why-this` disclosure (aria-expanded, RTL-safe) in exactly three score contexts:
- **Coverage** (hero `Current requirement coverage N%`) — defines what coverage compares, notes it is not a hiring guarantee.
- **Plan progress** (path panel `N/M topics complete`) — plain language: progress comes only from passing Mini Checks; **never grants a Verified Skill**; the pinned "Topics complete only after a Mini Check pass. This does not create a Verified Skill." sentence is preserved byte-for-byte, with the disclosure adding the "how do I get it then" answer.
- (Match % already carries a user-facing explanation in its own panel — untouched.)

### Empty states (each one action)
`journey-band` substitutes each of the four empty branches above; the existing `.continue-card` empty/CTA behaviors below the panel are unchanged.

## Gates
- `npx tsc --noEmit` — **clean**
- `npm run build` — **built in 2.65s** (only the pre-existing >500 kB chunk advisory)
- 29/29 `frontend/scripts/check-*.mjs` contract guards — **PASS** (incl. `check-learning-polish.mjs` pins for `disabled={practiceSubmitting || isCompleted}`, `pp-action-available`, `.pp-stage-final`; `check-learning-tabs.mjs` `activeTab === 'continue'` routing; all Phase 1/2/3/4 learning checks)
- Backend — **untouched**; focused re-run of lesson/practice/orchestrator/remediation/agentic suites: **80 passed / 2 skipped**, the 2 failures (`test_malformed_ai_response_uses_labelled_fallback`, `test_ai_exception_uses_labelled_fallback`) are the pre-existing merge regression documented in Phase 0 (rows 1–2, `PracticeProviderError`/`AttributeError` at `main.py:3036`) — not introduced here.

## Manual inspection checklist (human acceptance)
1. **In-progress plan:** Learning → the band shows one card (current lesson, purpose, ~min, **Continue learning**); clicking it opens that lesson with the right section; second/third in-progress plans appear as the "N other plans" note; the In-progress paths panel below still lists them.
2. **Milestone states:** path timeline shows 4–8 topic chips — current (indigo, row highlighted), completed (green), upcoming/locked (slate), and **needs review** (amber) after you open a lesson, submit a Mini Check that fails (score < 70%), and return.
3. **Long path:** a path with >8 topics shows 8 + **Show all N more topics**; expanding reveals the rest; stage milestones (Learn → Practice → Final Assessment) keep their chips.
4. **Lesson revisit:** open a completed lesson → every section tab is clickable (Learn / Example / Practice / Mini Check appear instantly); Practice's submit stays disabled (already graded).
5. **Why this?:** click the little "Why this?" disclosure beside coverage % and beside "N/M topics complete" — short plain-language explanation, no jargon; the pinned sentence remains visible.
6. **Empty states:** with no target role → "Pick a target role" (→ Skills & Roles); with gaps but no diagnostic/data → "No plan yet" (→ Start a diagnostic); with paths but nothing started → "Your learning plans are ready"; with no gaps + target → "You're up to date". Each shows ONE action and no flash while data loads.
7. **No fake progress:** nothing shows streaks, elapsed timers, fake completions; "~N min" comes from the real `estimated_minutes`; green checks only ever reflect `path.progress` pass states.
8. **Responsive/theme/RTL:** 1440/1024/768/390 px, Professional + Casual Pulse, light + dark, EN + Arabic — journey-card wraps gracefully, chips wrap, `.why-this-body` aligns correctly in RTL.

## Limitations / notes
- No live browser run performed (mirrors Phase 0/1 practice — static dist served; visual verification deferred to the checklist above).
- `frontend/scripts/practice-git-python-sql.spec.mjs` still cannot run (undeclared `@playwright/test`) — unchanged.
- The 14 pre-existing backend failures stand; not masked, not introduced here.
- Backend deliberately untouched: journey states are derived from existing persisted data (`path.progress`, `lesson.state`, `lesson.mini_check_result`), so no migration/endpoint churn against the 13 test files that pin `0014_conversation_live_meta` as the migration tail.

## Next phase
Phase 3 (per the guide) — await approval before starting.