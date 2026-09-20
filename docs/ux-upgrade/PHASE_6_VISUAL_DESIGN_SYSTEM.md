# Phase 6 — Visual Design System and Theme Polish

**Implementation guide:** `OPENCODE_PRODUCT_UX_IMPLEMENTATION_GUIDE.txt` lines 282–310 (visual design system and theme polish).
**Status:** IMPLEMENTED — AWAITING HUMAN ACCEPTANCE (all gates green; fronts a live server on `http://127.0.0.1:8060`).

## Objective and user-facing result

Finish the visual design system: consolidate spacing/radii/elevation/typography/page-rail/focus/color tokens into
single sources, polish Professional and Casual Pulse in both light and dark (light variants designed, not inverted),
give circular-progress labels room (stacked layout on narrow cards, never shrink-to-unreadable), keep role titles
legible, and keep motion restrained + `prefers-reduced-motion`-aware. Same routes, data flows, auth, providers, and
curriculum as approved in Phase 5 (`bdf6892`). Frontend-only; no backend schema/API change.

## What was implemented

### 1. Casual Pulse token consolidation (single source in `index.css`)
- **Removed the duplicate token overrides `pulse-polish.css` lines 11–13** (they won at runtime only because
  pulse-polish loads after index.css — the definitional drift this phase eliminates). Those *winning* values are now
  merged directly into the canonical `[data-interface="casual-pulse"]` base + light + dark blocks in `index.css`:
  - base: `--font` (Inter/Arabic stack), `--radius:18px/--radius-sm:12px/--radius-lg:24px`, the indigo family
    `#ee853e/#b94b0b/#fff0e4`, and the new `--rail-w:228px` token; light/dark blocks adopt the previously-winning
    palette (`#f6f5f1/#fff/#e5e5e1` light, `#0b1017/#111a25/#24303e` dark, matching slate scales, indigo-dark
    `#ffae72`, shadows, translucent cosmos).
  - index-only variables that pulse never overrode are untouched (`--sb-white`, `--sb-midnight*`,
    `--slate-400/300/50`, `--shadow-card`, `--sb-teal/violet/blue`, `--journey-*`, `--sb-indigo-soft-border`).
- **Page rail is now a token**: `.interface-casual-pulse .sidebar/{.content}` and the two 228px media remaps in
  `pulse-polish.css` use `var(--rail-w)` instead of magic numbers.
- **Single-source accent color**: the two remaining `#ee853e` literals in `pulse-polish.css` (primary action button,
  learning-action button) now use `var(--sb-indigo)` (same value, one origin).
- Checkers do not pin these token values or rail widths (verified), so no gate risk.

### 2. Dark `.sro3-page` (Skills & Roles) scoped-token remap
- Added `[data-theme="dark"] .sro3-page` after the scoped token block (`index.css` ~3912): `--sro-bg`, `--sro-border`,
  `--sro-muted`, `--sro-ink`, `--sro-blue/-blue-light`, `--sro-green/-green-light`, `--sro-accent-light/-accent-dark`,
  `--sro-shadow` now follow the dark tokens. **`--sro-midnight` is intentionally NOT remapped** — it stays the fixed
  navy because `.sro3-hero` uses it as a background (hero surface remains the established navy block).
- Direct dark re-assertions for the text that rode `--sro-midnight`/light literals: `.sro3-page h1/h2/h3`,
  `.sro3-stat-value`, `.sro3-rail-title` → `var(--sb-midnight-ink)`; plus dark backgrounds/text for the residual
  literal chips and panels (`.rm-panel`, `.rm-chip`, `.rm-conf-high/medium`, `.rm-action-mapped/unmapped/changed`,
  `.rm-bar-low`).
- Role titles were already theme-aware via clarity-pass (`--sb-midnight-ink`); unchanged.

### 3. Circular-progress label room (stacked, never shrunk unreadable)
- Base `.score-ring .ring-label` (`index.css` ~384): added `box-sizing:border-box; padding:0 12px; text-align:center`,
  `strong` line-height `1.05`, `small` line-height `1.3`.
- `.srb-match-label` (clarity-pass): `8.5px` → `9.5px`, `max-width` 62 → 90px, letter-spacing `.05em`, line-height
  `1.25` — wraps into a stacked layout instead of clipping.
- Casual Pulse role-card ring at the 600px breakpoint (`pulse-polish.css`): the `.66` scale shrink now **counter-scales
  the label font** so the effective size stays readable (`small` 10px→15px, `strong` 30px→44px, max-width 88→128px);
  the ring visual keeps the establish shrink, the text does not.

### 4. Already-complete, verified-not-changed
- Motion: all new media blocks in all four stylesheets respect `prefers-reduced-motion` (checked index/pulse/clarity/ia
  sites); pulse animation gated on `prefers-reduced-motion: no-preference`.
- Branding: no TryHackMe/HackTheBox art in the repo (grep-verified); logo stays SkillBridge-only, `--brand-mark`
  orange-tinted accent maintained.
- Focus: `:focus-visible` outline + offset on buttons/links/inputs/selects/textarea (clarity-pass) — retained.

## Files changed and why
- `frontend/src/index.css`: canonical casual-pulse token blocks (base/light/dark) now carry the merged values;
  `--rail-w`; light sidebar re-assertion aligned to the pulse value (`#edf0f2` nav surface); dark SRO/rm remap block;
  ring-label room on `.score-ring .ring-label`.
- `frontend/src/pulse-polish.css`: removed the definitional token duplicates; rail widths → `var(--rail-w)`; two
  `#ee853e` literals → `var(--sb-indigo)`; ≤600px ring-label counter-scale.
- `frontend/src/clarity-pass.css`: `.srb-match-label` readability bump.

## Backend schema/API changes
None. Frontend-only phase; the demo server (uvicorn on 8060) serves the same backend.

## Tests / build / browser checks (exact results)
- **Backend (focused sanity, unrelated to the change, run to confirm no collateral):**
  `test_tutor_profiles`, `test_tutor_language`, `test_tutor_conversations_phase4a`, `test_learning`,
  `test_webcam_integrity`, `test_assessment`, `test_mentor_ui_preference_phase5` — piped to relative-path stdout:
  **139 passed / 0 failed** in 57.09s.
- **Frontend contract gates (all 32 scripts, green):** checks for mentor-live, copilot-voice-unit,
  step45-copilot, tutor-profiles, tutor-language, tutor-memory-phase2, learning-tabs, webcam-integrity,
  scenarios/assessments/phaseF/K/L/N/P, data-truth, match-breakdown, job-board, job-tracker, phase4-tour,
  phase5-mentor, chat-mentor-15, interview-voice-ux, copilot-vex-mode, copilot-onboarding-phaseP, role-details,
  role-explorer, roles-discovery — **32/32 OK**.
- **`npm run typecheck`-equivalent (`npx tsc --noEmit`) — clean** (no output).
- **`npm run build` — built in 2.75s** (only the pre-existing chunk-size advisory).
- **Browser (Chrome headless via CDP, fresh serving of the rebuilt `frontend/dist` on `http://127.0.0.1:8060`,
  `aisha@student.edu` demo student, computed-style probes):**
  - Professional dark Skills & Roles: `.sro3-page` `--sro-bg` = `#0B1522` (was literal `#F6F8FB`),
    `--sro-border` = `#22334C`; srb label color = `#7E90A9`.
  - Casual Pulse dark Skills & Roles: `--sro-bg` = `#0b1017`, `--sro-border` = `#24303e`; srb label = `#9BA9B9`.
  - Casual Pulse dark dashboard at 600px: pulse ring label small = `15px` / strong = `44px` (counter-scaled;
    effective ≈10px/29px at `.66` scale — readable).
  - Sidebar widths: Professional 264px, Casual Pulse 228px (`var(--rail-w)`), single source.
  - A matrix of full-page screenshots (4 combos × dashboard + Skills & Roles + 600px mobile dark Pulse) was also
    captured into the temp evidence dir for human inspection.
- **Server process**: rebuilt `frontend/dist` is served by the running uvicorn on `127.0.0.1:8060` pointing at the
  **current checkout** (not an old copy).

## Screens/routes to inspect manually
- Dashboard (Professional light/dark, Casual Pulse light/dark) — role-coverage ring labels with breathing room.
- Skills & Roles (both interfaces, both themes) — SRO hero navy intact in dark, role titles legible,
  match-ring labels readable/stacked, rm chips/actions readable in dark.
- Casual Pulse dashboard at ≤600px — the role-ring label stays readable (stacked) instead of shrinking.
- Theme toggle (sun/moon, topbar) + the Professional|Pulse and Light|Dark|System controls in the user menu —
  changes apply immediately and persist via `sb_interface`/`sb_appearance`/`sb_theme`.

## Known limitations / deferred
- The model running this phase cannot render images, so the browser screenshots are provided as files for human
  inspection; the computed-style probes above are the automated acceptance evidence.
- No TryHackMe/HackTheBox art intentionally introduced (guide forbids it); branding remains SkillBridge-only.
- Theme/interface preference stays browser-local (existing behavior, unchanged), matching the guide's
  "existing preference mechanism".

## Next phase
**Phase 7 — Accessibility, RTL, Responsive, and Failure States** (guide lines 311–329): keyboard-audit, semantic
headings/dialog/form/focus, English LTR + Arabic RTL correctness (no code-snippet mirroring), 1440/1024/768/390px
viewport regression (no horizontal scroll/overflow/clipping/mentor-panel occlusion), clear error/loading/empty
states for jobs/tutor/diagnostics/lessons/assessments/network with real retry actions, and provider-error privacy.
Not started — awaiting human approval of this phase per the FINAL HANDOFF FORMAT.