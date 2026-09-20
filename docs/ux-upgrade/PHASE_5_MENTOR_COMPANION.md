# Phase 5 — AI Mentor as a User-Controlled Companion

**Implementation guide:** `OPENCODE_PRODUCT_UX_IMPLEMENTATION_GUIDE.txt` lines 254–281 (mentor as a user-controlled companion).
**Status:** IMPLEMENTED — AWAITING HUMAN ACCEPTANCE (mirror workspace; all gates green).
**Contrast with prior phases:** Phase 4 delivered the welcome tour + contextual mini-tours and is committed (`d4798ff`) and approved. Phase 5 adds a genuine *user control* surface over the Global Copilot: hide the panel entirely, reopen from a persistent compact launcher, a mobile bottom-sheet layout, and per-page contextual prompts in the welcome state — with the visibility choice persisted per student on the backend so it survives refresh. No chat auth, provider keys, history access, or voice behavior were touched; the fixed 14 pre-existing backend failures remain untouched.

## What was implemented

### Backend (server is the source of truth for the visibility choice)
- **Migration `0016_mentor_ui_preferences`** (`backend/app/database.py`): new table
  `mentor_ui_preferences (student_id INTEGER PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
  panel_visible INTEGER NOT NULL DEFAULT 1 CHECK(panel_visible IN (0,1)),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')))`. Registered as the new tail of `MIGRATIONS`.
- **Models** (`backend/app/models.py`): `get_mentor_ui_preference(student_id)` — returns a synthetic
  `{student_id, panel_visible: True, updated_at: None, default: True}` row when no preference exists, so
  never-written students keep the default (visible) experience with zero migration cost;
  `set_mentor_ui_preference(student_id, panel_visible)` — upsert (`ON CONFLICT(student_id) DO UPDATE`, refreshes `updated_at`).
- **Endpoints** (`backend/app/main.py`), immediately after the Phase 4 tour endpoints:
  - `GET /api/students/{student_id}/mentor/ui` → 200 `{student_id, panel_visible, updated_at, default}`.
  - `PUT /api/students/{student_id}/mentor/ui` body `{panel_visible: bool}` → 200 fresh state.
  - Both require Student auth + `_own_student`; PUT is strict: a missing/non-bool `panel_visible` is 400,
    a non-object payload is 422 FastAPI rejection.
- **Tests:** NEW `backend/tests/test_mentor_ui_preference_phase5.py` (12 tests: migration creates + idempotent,
  synthetic visible default, 401/403/403 auth, hide→show roundtrip persisted, per-student isolation,
  400 on missing/non-bool/int, 422 non-object). Migration-tail assertions bumped
  `0015_student_tour_state` → `0016_mentor_ui_preferences` across the 13 affected suites
  (phaseB/phaseD/phaseF/phaseK/phaseL/phaseN/phaseO/phaseP/phaseC, esco-slice2, interview-live-4d,
  tour-4d, tutor-conversations, tutor-memory-2).

### Frontend (all additive; CopilotPanel remains localStorage-free — `check-tutor-memory-phase2.mjs` green)
- **Types/API:** `MentorUiState` + `MentorUiUpdate` in `frontend/src/lib/types.ts`;
  `api.mentorUi(studentId)` / `api.setMentorUi(studentId, body)` in `frontend/src/lib/api.ts` → `/mentor/ui`.
- **Icon:** `IconEyeOff` added to `frontend/src/components/Icons.tsx`.
- **CopilotPanel (`frontend/src/components/CopilotPanel.tsx`):**
  - New `panelVisible` state (default true), loaded once from `api.mentorUi(studentId)` on mount (guarded by `panelPrefLoaded` ref, so no redundant PUT on first load).
  - `.copilot-hide` icon button in the dock bar (eye-off, `aria-label`/`title` localized), next to the existing expand button → persists `false`.
  - When hidden the panel returns early and only a compact `.mentor-launcher` renders: pill with the tutor's avatar + name, fixed bottom-right `z-index:95`, keyboard-focusable, per-mentor accent theme class, `aria-label` "Open {name}" → persists `true` and reopens.
  - The existing window `copilot:focus` handler now also calls `setPanelVisiblePersisted(true)`, so any focus signal (keyboard/global shortcut/copilot entries elsewhere) reopens the mentor from the launcher state.
- **Contextual prompts (per the guide: explain/plan/practise prompts, never forced into chat):**
  - `contextualPromptsFor(lang, page, context)` in `frontend/src/lib/tutorI18n.ts` — localized EN/AR prompt buckets keyed by `CopilotPage` (dashboard, skills_roles, learning, assessment, scenarios, jobs, career_roadmap, mock_interview), interpolating the current topic / skill / job title.
  - Rendered as a `.ctx-prompts` row in the welcome (empty-state) section, above `SuggestionGrid`; clicking a chip sends the prompt through the normal composer path (`send(undefined, prompt)`). Never auto-sent.
- **CSS (`frontend/src/index.css`):** `.copilot-hide`, `.mentor-launcher` (+ `.purple/.blue/.gold/.green` accent overrides, hover glow via existing `--mentor-accent-glow`), `.ctx-prompts` / `.ctx-prompts-label` / `.ctx-prompts-list` / `.ctx-chip`, and a mobile bottom-sheet in `@media (max-width:720px)`: the open non-expanded panel becomes a bottom-anchored drawer (side margins, rounded top corners, `max-height: calc(100dvh - 96px)`, grabber handle `.copilot-bar::before`). All colors/typography reuse existing tokens (incl. dark-mode remaps). Expanded fullscreen (`@media 560px`) untouched.

## Gates (all green)
- Backend focused: **318 passed / 0 failed** across the new file + tour/migrations/interview-live + all bumped tail suites + auth_sessions + copilot (58 + 192 + 56 + new file 12 = lib).
- Frontend contract sweep: **32/32 OK** (31 prior + NEW `check-phase5-mentor.mjs` — server-persistence, localStorage-free panel, launcher/hide/aria, contextual prompts never auto-sent, mobile bottom-sheet, per-theme launcher accents, IconEyeOff).
- `npx tsc --noEmit` clean; `npm run build` clean (2.79s, chunk-size advisory only, pre-existing).
- `frontend/dist` rebuilt; 8060 server restarted (new backend + new bundle). Live-verified: GET default `{panel_visible:true, default:true}` → PUT false persists → PUT 400 on `panel_visible:1` → PUT true. Demo student 1 returned to `panel_visible:true`.

## Manual acceptance steps (browser, 127.0.0.1:8060, sign in aisha@student.edu/demo1234)
1. **Hide:** dock bar → eye-off button → the whole panel disappears, a compact pill launcher (avatar + mentor name) sits bottom-right. `aria-label` announces "Open {name}".
2. **Reopen:** click the launcher → panel returns. Click the launcher instead via keyboard (Tab → Enter) → same result.
3. **Persistence:** hide → hard-refresh the browser → still hidden (launcher only, no panel). Reopen → refresh → panel returns.
4. **Focus entry:** with the panel hidden, trigger any `copilot:focus` entry (e.g. a page "Ask {name}" affordance) → panel reopens.
5. **Contextual prompts:** open the panel on an empty chat on each page (Dashboard, Skills & Roles, Learning, Assessments, Scenarios, Jobs, Roadmap) → a "Based on this page" chip row appears above the suggestion cards; the copy reflects the page/topic; clicking sends the prompt (no auto-send on view).
6. **Mobile bottom-sheet:** resize to ≤720px wide → open the panel (not expanded) → it docks to the bottom edge with rounded top corners and a grabber handle; it never covers the primary actions; expand still goes fullscreen.
7. **Regressions:** Language EN⇄Arabic (RTL chips/launcher), Light/Dark theme, all four mentors' accents on launcher, Mock Interview, History/Clear, Live voice — unchanged.