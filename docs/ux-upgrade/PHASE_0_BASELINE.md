# Phase 0 — Baseline, Inventory, and Quality Guardrails

Status: **COMPLETE — awaiting approval before Phase 1**
Scope: read-only audit of the current merged SkillBridge project. No source code
was changed. The only file added by this phase is this report.

---

## 1. What was audited

- Repository HEAD: `690e5e1 merge: integrate verified team curriculum` (on `main`,
  2 commits ahead of `origin/main`).
- Working copy is the current checkout at
  `/Users/aboodmr/Desktop/skillbridge-github-ready`. No Trash / mirror / older ZIP
  copies were used.
- Project layout: FastAPI backend (`backend/app/main.py`, 3717 lines; 40 `app`
  modules, 127 test files) + React 18 / Vite 5 frontend
  (`frontend/src`, 8 pages, 24 components, 3 stylesheets, 30 contract scripts).

### Tech stack (unchanged in this audit)

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLite (`backend/skillbridge.db`), SQLAlchemy-style helpers in `app/database.py` |
| Auth | Token-based (`/api/auth/login|signup|verify…`), bearer-token gating, Goog / role flow |
| Frontend | React 18 + TS 5.5, Vite 5, react-router-dom (public profile only), in-shell `section` state nav |
| GenAI | NVIDIA NIM via `app/genai.py` (env-configured, deterministic fallback) |
| Jobs | `app/jobs.py` provider federation (Adzuna / Jooble / etc.), unified feed |
| Curriculum | Curated Python, SQL, Git, Docker content in `app/knowledge_base.py` + `app/lessons.py`; 23 safe static practice reviewers (text-only, never execute) |
| Testing | pytest (venv `.venv/bin/python`), 31 node contract scripts in `frontend/scripts/` (some wrapped by `test_runtime_*_frontend.py`), Puppeteer browser harness in `scripts/browser-regression/` |

### Secrets / safety

- `.env`, `env`, `*.db`, `backend/uploads/` are git-ignored. No credentials,
  API keys, or private files were read or written in this phase. The application
  was not started (no network calls to providers were made).

---

## 2. UX map (page inventory)

| Page / surface | Purpose | Primary action(s) | Notable secondary content | States present (load / empty / error) |
|---|---|---|---|---|
| LoginPage | Auth entry (sign in / create account / reset / Google) | Create account / Sign in | Journey hero, education level select, verification token flow | loading, pending, error, toast |
| DashboardPage | Career-state overview + one recommended next step | "Choose your target career" / priority P1–P4 next-step card → Skills/Practice/Learning | MatchBreakdown, JobTrackerPanel, JourneySpine, LearningActivityMini, pulse appearance selector | `.loading`, `.empty`, `.error`, onboard block |
| SkillsRolesPage (Role Explorer) | Exploration hub: CV upload, target role, role library, saved, recents, market/ESCO, compare | "Select as target" / "Browse roles" / Upload CV | 5-tab layout, 150ms search, filters (facets `<details>`), compare table, RoleDetailsModal, provenance | skeleton grid, loadError, "No roles match…", noscv, market unavailable |
| LearningPage | Gaps → personalized learning paths → diagnostics → lessons | Start/Retake Diagnostic, Continue learning | Tabs (for-you / my-skills / continue / completed), stepper rows, ResourceCard, roadmap timeline | EmptyLearningState, diag phases, error |
| ScenariosPage (Practice) | Practice scenario library + in-browser player | Start scenario | Difficulty/category filters, focus role deep link, results, history | library loading/empty/error, player busy |
| AssessmentsPage | Skill-verification assessments with webcam integrity | Start assessment / Verify a skill | Camera precheck, one-question flow, results, evidence, history | loadError, empty ("No skill gaps…"), camera/precheck states |
| UniversityPage | University Admin aggregated stats + cohort confirm | Cohort confirm | Stats grid, institution banner | `.loading`, `.error` |
| CopilotPanel + VoiceMode + MentorOrb | AI mentor chat, fullscreen live voice, orb visuals | Live voice, message composer | Interview mode, language EN/AR, per-mentor accents | voice-unavailable, TTS errors, stt fallback |
| CopilotOnboarding / CopilotSettingsModal | First-run mentor picker + "Change your copilot" | Choose mentor | Retake quiz, backend onboarding row | loading/error inside modal |
| PublicProfilePage (`/p/:id`) | Public verified-skill card | none (share link) | LevelBadge per skill | loading / missing / ready |

Cross-cutting conventions already present (to preserve / build on):
- One deterministic "next best action" on the Dashboard (P1–P4 priority logic + `JourneySpine`).
- Consistent state classes: `.loading` / `.empty` / `.error` / `.card` / `.btn.btn-primary` / `.chip` / `.eyebrow`.
- Deep-link focus contract: `navigate(dest, {skillId, roleTitle})` consumed by Learning/Scenarios/Assessments/Skills `#explorer`; `backTo` breadcrumbs.
- Role-gated nav kept in `App.tsx` (Student sees Learning/Practice/Assessments; University Admin sees University).
- Toasts (`useToast`) for async feedback; `skip-link`; RTL mirrors (`[dir=rtl]`, logical properties where possible).
- The lagging "Notifications — coming soon" popover is an honest placeholder (labelled as such).

### App shell (App.tsx)

- No URL router for the six sections; `section` React state + `document.title`.
- Sidebar nav (brand → dashboard, nav items, role badge), mobile hamburger + backdrop.
- Topbar: theme toggle, notifications placeholder, user chip → account popover with
  **visual preferences** (Interface style Professional/Casual-Pulse, Appearance
  Light/Dark/System) — already the whole-app appearance mechanism.
- `demo-banner` when GenAI/email unconfigured — honest provider-health copy.

### Theme & interface system (useThemePref.ts + CSS)

- Keys: `sb_appearance` (`light|dark|system`), `sb_interface` (`professional|casual-pulse`),
  legacy `sb_theme` auto-migrated.
- Applied as `dom-element[data-theme]`, `[data-appearance]`, `[data-interface]` +
  `app-shell interface-{style}` class. Tokens are CSS custom properties in
  `index.css` (`--sb-*`), plus `pulse-polish.css` (Casual Pulse token overrides:
  orange `--sb-indigo:#ee853e`, dark navy `#0b1017` base) and `clarity-pass.css`
  (shared page rail, card padding).
- Design-token convention docs already exist: `docs/design-tokens-shell-spec.md`,
  `docs/redesign-brief.md`, `docs/mockups/` — named color roles
  (`--sb-role-*`), "no raw hex in new work", RTL first-class, class contract frozen.
- Mentor accents derive from the same tokens (Nova purple / Axel blue / Sage gold / Vex green).
- RTL is app-language driven (Arabic pages mirror); voice overlay has its own
  `.voice[dir=rtl]`.

---

## 3. Baseline checks (exact commands and results)

All commands run on this checkout. No source files were modified.

### Frontend typecheck

```
cd frontend && npm run typecheck        # = tsc --noEmit
Result: PASS — no output, exit 0
```

### Frontend production build

```
cd frontend && npm run build            # = prebuild fix-bin && tsc -b && vite build
Result: PASS — built in 2.89s
  dist/assets/index-*.css  324.06 kB (gzip 56.15 kB)
  dist/assets/index-*.js   737.80 kB + 1,281.30 kB (gzip 210/200 kB)
Advisory only: "Some chunks are larger than 500 kB" (pre-existing; not a failure).
```

### Backend tests (full suite)

```
cd backend && ../.venv/bin/python -m pytest -q
Result: 14 failed, 1667 passed, 5 skipped, 607 warnings in 543.46s (0:09:03)
Collected: 1686
```

### Frontend contract scripts (source guards, node)

```
for f in frontend/scripts/check-*.mjs practice-git-python-sql.spec.mjs; do node $f; done
Result: 28/29 PASS
```

The 29th script `frontend/scripts/practice-git-python-sql.spec.mjs` cannot run:
it imports `@playwright/test`, which is not declared in any `package.json`.
(The repo's browser harness uses `puppeteer-core`, and
`scripts/browser-regression/node_modules` is not installed.) It is not wrapped by
any pytest test, so the suite is unaffected — but the dependency decision is open.

### Runner conventions

- Backend: `.venv/bin/python -m pytest` from `backend/` (repo-root venv).
- Project npm runner `npm run test:backend` uses `scripts/test-backend.mjs`
  (installs requirements then `pytest tests -v`).
- The 31 `frontend/scripts/check-*.mjs` contracts are also exercised inside the
  pytest suite by the `test_runtime_*_frontend.py` wrappers; those all passed.
- `scripts/verify.sh` starts a fresh seeded server by **deleting
  `backend/skillbridge.db`** — intentionally NOT run, to preserve local DB data.

---

## 4. Failing backend tests — root causes (Phase 0 does NOT fix these)

All 14 failures trace to the merge commit `690e5e1` which rewrote
`practice.py` (+1169), `knowledge_base.py` (+4628), `jobs.py`, `genai.py`,
`path_builder.py`, and `main.py`:

| # | Test | Root cause | Category |
|---|---|---|---|
| 1–3 | `test_learning_practice.py::test_malformed_ai_response_uses_labelled_fallback`, `::test_ai_exception_uses_labelled_fallback`, `test_curated_python_reliability.py::test_live_provider_failure_returns_retryable_error_and_persists_no_grade` | `main.py:3036` does `except practice.PracticeProviderError:` but `practice.py` (merged) renamed it to `PracticeGraderUnavailable(RuntimeError)`. Provider failure in practice review raises `AttributeError` → 500 instead of the intended 503 retry. | Merge bug (broken attribute) |
| 4 | `test_learning_quality.py::test_ai_path_carries_grounded_sources_and_self_check` | Generated AI path lacks the grounded `sources`/`self_check` fields asserted at `test_learning_quality.py:219`. | Stale expectation vs merged path_builder |
| 5 | `test_python_static_check.py::test_static_check_recognizes_a_sound_data_structures_summary_without_execution` | `TypeError: 'NoneType' object is not subscriptable` — static-check result missing a field the test reads (`test_python_static_check.py:32`). | Merge mismatch in practice static check |
| 6–9 | `test_diagnostic.py` (3) + `test_curated_python_reliability.py::test_curated_python_diagnostic_is_exactly_tagged_and_path_is_prerequisite_ordered` | Tests require ≥15 (or 9) diagnostic questions; the merged deterministic question bank yields 9. | Stale count expectation vs merged curriculum |
| 10 | `test_jobs_matching.py::test_jooble_results_can_be_included` | Assert URL `https://api.jooble.org/…`; merged `jobs.py` emits `https://jooble.org/…`. | Stale expectation vs merged endpoint |
| 11 | `test_jobs_matching.py::test_adzuna_explicit_uk_market_uses_gb_endpoint` | Expected market state `'live'`, got `'empty'` — depends on a live Adzuna result during the test. | Environment/network-dependent |
| 12–14 | `test_trusted_cs_knowledge_base.py` (3) | `KeyError: ('sql','joins')`; bilingual (Arabic) explanation marker `'بالعربية'` missing from merged Python Functions lesson; data-structures content/check mismatch. | Merged content not matching its own guard tests |

These are integration-consistency gaps between the merged "verified team
curriculum" and the pre-merge contract tests. They are **not** caused by this
audit. They are reported here as the baseline so Phase 1 onward can treat them
explicitly (fix, update, or defer with a written decision — never silently).

Additionally test-diagnostic related output above shows the deterministic
fallback and the merged curriculum are functioning; only the tests disagree with
the merged content/API shapes.

---

## 5. Blockers for this phase

1. **Backend baseline is not fully green**: 14 failed / 1667 passed. The failing
   tests live in exactly the modules the latest merge rewrote. Phase 0 is
   read-only, so no fix was attempted → they carry into the report as the true
   baseline.
2. **Undeclared dev dependency**: `frontend/scripts/practice-git-python-sql.spec.mjs`
   imports `@playwright/test`; it exists in no package manifest. A decision is
   needed (add the dependency to the browser harness, or convert to the
   puppeteer-core harness, or defer).
3. **Do-not-run guard**: `scripts/verify.sh` deletes `backend/skillbridge.db` and
   would perturb local data — excluded from baseline by policy.

No blockers related to .env, providers, credentials, or private data.

---

## 6. Files changed in Phase 0

| File | Change |
|---|---|
| `docs/ux-upgrade/PHASE_0_BASELINE.md` | New — this report |

Source code, routes, auth, DB, themes, curriculum, and API integration are
untouched. `git status` shows only this report (plus the pre-existing untracked
`OPENCODE_PRODUCT_UX_IMPLEMENTATION_GUIDE.txt`).

---

## 7. What Phase 1 will do (Information Architecture and Page Density)

- Define one consistent page anatomy: context/breadcrumb → title + one-line
  purpose → one primary action → primary content → optional details.
- Split the crowded **Role Explorer** (Skills & Roles) into purposeful sections
  and the **Assessment** landing into a focused pre-flight (skills covered,
  duration, question count, result meaning, Start) — preserving every existing
  route and tab, moving nothing behind removal.
- Establish the card hierarchy (hero/primary → standard → insight/status →
  expandable detail) and systematic alignment (rail, heading spacing, card
  padding, action placement, badge height, consistent loading/empty/error
  spacing) using the existing `--sb-*` token system and `clarity-pass.css`
  conventions.
- Validate at 1440 / 1024 / 768 / 390 px in Professional and Casual Pulse,
  light and dark, EN + AR (RTL) — with no feature or route removed.
- Coordinate with the 14 backend failures so Phase 1 (UI) does not silently
  mask them; recommend a triage decision for the merge-contract mismatches
  before or alongside the UI work, per the guide's "never fake live data /
  provider health" rule.

Phase 1 will not begin until explicitly approved.