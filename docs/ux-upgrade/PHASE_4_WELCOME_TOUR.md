# Phase 4 — Welcome Tour + Contextual Mini-Tours — IMPLEMENTED

**Status:** AWAITING HUMAN ACCEPTANCE. All gates green (31/31 frontend checkers incl. the new Phase 4 checker; tsc clean; build clean; backend tour/auth/migration suites green).

## Objective
Per the Product UX implementation guide (§ Phase 4): a short global welcome tour (≤5 steps), contextual first-time mini-tours for the three destination pages (Skills & Roles, Learning, Assessments), and **server-persisted tour state per authenticated student** so a user is never shown the welcome tour again after they finish or skip it — but can always replay it.

## What changed (additive only; no behavior change outside the new tour surfaces)

### Backend (tour state is the source of truth; no existing endpoint touched)
- **Migration `0015_student_tour_state`** (`backend/app/database.py`): table `student_tour_state` —
  `student_id` INTEGER PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE, `tour_version` TEXT NOT NULL DEFAULT 'v1',
  `welcome_state` TEXT CHECK IN ('not_seen','active','completed','skipped') DEFAULT 'not_seen',
  `dont_show_again` INTEGER DEFAULT 0, `mini_states_json` TEXT DEFAULT '{}', `updated_at` TEXT.
  Idempotent, appended to `MIGRATIONS` (design: a future **major version bump** bumps `tour_version` + resets to `not_seen`, which is exactly when re-showing is honest).
- **Models** (`backend/app/models.py`): `TOUR_VERSION='v1'`, `TOUR_PAGES=('roles','learning','assessments')`, state vocabularies;
  `get_student_tour_state(student_id, default=False)` (returns the synthetic `not_seen` default when no row exists — `default:true` signals it);
  `set_student_tour_state(...)` upserts via `INSERT … ON CONFLICT(student_id) DO UPDATE`, `welcome_state`/`dont_show_again` replace, `mini_states` **merge** (never wipes other pages).
- **API** (`backend/app/main.py`): `GET` + `PUT /api/students/{student_id}/tour/state`, both `_require_roles("Student")` + `_own_student`;
  PUT validates vocabulary (400 on bogus `welcome_state`, non-bool `dont_show_again`, unknown mini page/state; non-object body → 422), returns the fresh full state.
- **Tests** (`backend/tests/test_tour_state_phase4.py`, 12 tests): migration applies + idempotent; synthetic default; 401/403 auth;
  lifecycle `not_seen→active→completed`; skip; `dont_show_again` flag; mini completion + merge; PUT validation (400/422); replay returns to `active`.
  Migration-tail assertions bumped to `0015` across 12 test files (same class of intended test updates as prior migrations).

### Frontend
- **`frontend/src/components/ProductTour.tsx` (new):**
  - `TourProvider` + `useTour()`: loads state from the API on student mount (localStorage `sb_tour_cache:{studentId}` is only an offline fallback cache — the backend stays authoritative); auto-opens the welcome tour **once** when `welcome_state === 'not_seen'`; every transition is PUT back to the server.
  - `WelcomeTour` dialog (rendered by the provider): **5 steps** (Dashboard "Next step" → Skills & Roles destination → Learning plan → Practise safely / Assessments → Mentor & jobs), **≤5 per the guide**; controls **Next / Back / Skip tour / Don't show again / Finish**; `role="dialog" aria-modal aria-labelledby`, initial focus + Tab focus trap (wrapped), focus returned to the trigger on close, `role="status" aria-live="polite"` body so every step announces, inline progress "Step X of 5" + dots, Escape → skip, `prefers-reduced-motion` honoured (no transitions).
  - `MiniTourBanner`: a **non-modal** `role="note"` dismissible guide card; shown only when the welcome tour is not mid-run (`welcome_state !== 'active'`) and that page's mini is `not_seen`; Close marks the page `completed` on the server.
- **Wiring** (`frontend/src/App.tsx`): `TourProvider` wraps `Shell`; account menu gains **Replay product tour** (Student-only, next to "Change your copilot") → re-opens the tour and persists `active`; pages mount `MiniTourBanner`: Skills & Roles (`SkillsRolesPage.tsx`), Learning (`LearningPage.tsx`), Assessments (`AssessmentsPage.tsx`) — role/plan/measurement copy each, distinct bullets.
- **Types/API** (`types.ts` + `api.ts`): `StudentTourState`, `TourStateUpdate`, page/state unions; `api.tourState(studentId)`, `api.setTourState(studentId, body)`.
- **Styles** (`index.css`): `.tour-backdrop/.tour-card/.tour-actions/.tour-skip/.tour-dont` modal + `.mini-tour` banner (dashed, panel surface), `.mini-tour-points` bullets, RTL mirrors, responsive ≤520px, `[data-theme="dark"]` overrides following the existing shell pattern.
- **Checker** `frontend/scripts/check-phase4-tour.mjs` (new): API-persistence pins, ≤5 steps, all controls, Escape, dialog semantics, focus management, lifecycle persistence, account-menu replay, mini-tour non-modality + gating + wiring to all three pages, provider wrap, reduced-motion CSS.

## Gates
- Frontend checkers: **31/31 OK** (all 30 pre-existing + `check-phase4-tour.mjs`).
- `npx tsc --noEmit` clean; `npm run build` clean (2.79s; pre-existing chunk-size advisory only).
- Backend: `test_tour_state_phase4.py` + migration + auth files **45 passed / 0 failed** (focused; earlier full migration-tail sweep 192 passed). Pre-existing 14 failures untouched.
- Live smoke on `http://localhost:8060` (restarted with new backend + rebuilt dist): login → `GET /api/students/1/tour/state` `welcome_state:"not_seen" default:true`; PUT mutations round-trip; student 1 reset to a clean first-run row for acceptance.

## Manual retest steps (acceptance)
1. Sign in as `aisha@student.edu` / `demo1234` → the **Welcome tour** opens automatically over the Dashboard on first landing (5 steps, Next/Back/Skip tour/Don't show again/Finish, "Step X of 5", Escape closes). Walk it fully → **Finish**; refresh → it does NOT reopen; account menu → **Replay product tour** → it opens again.
2. Restart the tour → choose **Skip tour** → closes, never auto-reopens; **Don't show again** → same, and the backend row carries `dont_show_again=true` (check via network/e.g. `GET /api/students/1/tour/state`).
3. With the welcome tour done/skipped, open Skills & Roles → a dashed **first-time guide** at the top (bullets about your target role / coverage / catalog) → Close → gone and stays gone (backend `mini_states.roles='completed'`). Repeat independently on **Learning** and **Assessments** — each page has its own mini-tour with its own copy.
4. While a welcome tour is mid-run, the mini-tours are suppressed; completing/skipping the welcome re-enables the not-yet-dismissed ones.
5. Accessibility: keyboard `Tab` stays inside the dialog (wraps), `Escape` skips, dialog has a label + live-announced step text, focus returns to the Replay button after replay closes, reduced-motion has no animation.
6. Log out → log in: only a student whose row is `not_seen` (or a future version bump) sees the tour again; company/university roles see nothing tour-related.
7. Dark mode: tour dialog + mini-tours render on the dark canvas following the existing shell token pattern.