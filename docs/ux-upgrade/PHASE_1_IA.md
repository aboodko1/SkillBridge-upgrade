# Phase 1 — Information Architecture & Page Density — IMPLEMENTED

**Status:** AWAITING HUMAN ACCEPTANCE. All frontend gates green; backend untouched.

## Objective
Reduce overload without removing features, per the Product UX implementation guide:
- Consistent page anatomy (clear title + purpose + one obvious primary action).
- Roles and Assessments each expose **one** obvious primary action above the fold.
- Sections grouped and labelled; secondary content progressively disclosed.
- No routes, features, themes, auth, or RTL behavior removed — strictly additive.

## What changed (additive only)

### New: `frontend/src/ia-system.css` (imported last in `frontend/src/main.tsx`)
A token-based IA layer that composes with the existing `index.css` / `pulse-polish.css` / `clarity-pass.css` systems (both Professional and Casual Pulse, light and dark):
- **Roles hero CTA placement** — `.sro3-hero-copy > .sro3-hero-cta` (left-aligned, no competing weight).
- **Assessments hero CTA** — `.asm-hero-cta` under the purpose line.
- **Pre-flight facts strip** — `.preflight` / `.preflight-item`, full-width hero row on the navy gradient.
- **Progressive disclosure** — `.details-expander` native `<details>` styling with a rotating chevron (RTL-safe via `margin-inline-start`), `prefers-reduced-motion` respected.
- **Consistent page head** — `.page-head` / `.page-head-text` / `.page-head-title` / `.page-head-purpose` / `.page-head-action`.
- Responsive breakpoint at 720px; no max-width layout changes.

### Assessments (`frontend/src/pages/AssessmentsPage.tsx`)
- **Primary action above the fold:** a hero CTA that jumps straight to the real next step:
  - open gaps → `Start assessment — <first gap skill>` (scroll + focus-flash into the verify list);
  - no open gaps (browse mode) → `Browse skills to verify`;
  - analysis still loading → no CTA (never fakes a step).
- **Pre-flight facts (honest, real numbers):** 10 questions per skill, score ≥70% passes (`PASS_THRESHOLD = 70.0`), camera proctoring throughout.
- **History demoted** behind a native `<details>` expander («Show assessment history (N attempts)»). Every history class (`history-list`, `history-item`, `status-pill`, `integrity-alert`, `history-meta`, `link-btn`), the evidence breakdown, and the empty state are preserved byte-for-byte — only the wrapper changed.

### Role Explorer (`frontend/src/pages/SkillsRolesPage.tsx`, StudentBrowse)
- When no target career is selected, the dark hero now carries the single primary CTA **«Choose a target role»** → switches to All Roles and smooth-scrolls to `#role-library`.
- When a target is selected, the existing **Browse roles** action in the target card remains the above-the-fold primary (no duplicate hero CTA).
- Filters were already collapsed behind facet `<details>`; card hierarchy already handled by `clarity-pass.css` (target = action card accent, profile/CV = neutral insight card) — behaviour unchanged.

### University (`frontend/src/pages/UniversityPage.tsx`)
- Adopted the shared `.page-head` anatomy (eyebrow + title «Cohort statistics» + purpose). The consent/confirm card remains the single primary action.

## Gates
- `npx tsc --noEmit` — **clean**
- `npm run build` — **built in 2.76s** (only the pre-existing >500 kB chunk advisory)
- 29/29 `frontend/scripts/check-*.mjs` contract guards — **PASS** (incl. `check-step45-copilot.mjs`, `check-learning-phase1.mjs`, `check-webcam-integrity.mjs`, `check-roles-discovery-phase2.mjs`, `check-role-explorer-phaseL.mjs`)
- Backend — **untouched** this phase (the 14 pre-existing merge-regression failures from Phase 0 stand; not masked).

## Manual inspection checklist (human acceptance)
1. **Assessments:** hero shows facts + one CTA. With an open gap the CTA reads «Start assessment — <skill>» and scrolls/focus-flash to that skill's Start button. History is one collapsed row under the verify panel; expand reveals the full list with integrity flags and evidence links.
2. **Roles:** no target selected → hero CTA «Choose a target role» jumps into the Role library. Target selected → hero shows no extra button; «Browse roles» in the target card is the primary. All five tabs, Saved chip, facet filters, and pager behave exactly as before.
3. **University:** new page head (title + purpose) above the privacy/min-cohort banner; consent card unchanged.
4. **Responsive/theme:** 1440/1024/768/390 px, Professional + Casual Pulse, light + dark, EN + RTL — no clipped preflight text, no chevron misalignment, heroes unchanged in weight.

## Limitations / notes
- No live browser run performed this phase (the frontend is static-dist served; visual verification deferred to the manual checklist above, mirroring Phase 0 practice).
- `frontend/scripts/practice-git-python-sql.spec.mjs` still cannot run (undeclared `@playwright/test` dependency) — unchanged from Phase 0.
- The 14 backend failures are pre-existing (merge regressions: `PracticeProviderError` mismatch, jooble/adzuna URL assertions, diagnostic counts, trusted-CS bundle, etc.). No fix attempted in Phase 1.

## Next phase
Phase 2 (per the guide) — await approval before starting.