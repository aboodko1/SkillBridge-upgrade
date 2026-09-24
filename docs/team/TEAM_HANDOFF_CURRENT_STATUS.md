# SkillBridge combined release — team handoff

**Prepared:** 19 September 2026

**Repository:** `aboodko1/SkillBridge-upgrade`

**Purpose:** one public, source-only team baseline combining the latest frontend, backend, tests,
plans, and cross-platform launch scripts.

## Read this first

This release is suitable for continued team development, but it is not a claim that every visual
screen is finished. The application compiles, builds, passes the complete backend suite, and its
core routes were smoke-tested. A focused visual-accessibility cleanup remains necessary and is
listed below.

Historical handoffs are retained under `docs/archive/handoffs/` for traceability. They are not the
current source of truth.

## What was combined

### Product experience

- Student, Company, and University experiences with role-aware navigation.
- Professional and Casual Pulse presentation modes with light, dark, and system appearance.
- Responsive dashboard, Skills & Roles explorer, learning, practice scenarios, assessments, jobs,
  and university analytics.
- Unified career journey from role selection through learning, practice, verification, and applying.
- Explainable target-role and job-match scores backed by the backend calculation payload.
- Role Explorer, role details, comparisons, transitions, recently viewed roles, saved roles, and
  target-role selection.
- Real-provider job aggregation with normalization, deduplication, caching, health states, safe
  links, dead-link reporting, filters, and pagination.
- Private saved-job and application tracker with stage history, notes, deadlines, and preparation
  guidance.

### AI learning and copilot

- Personalized learning paths, diagnostics, lessons, practice, mini-checks, and next-step
  orchestration.
- Four mentor identities (Nova, Axel, Sage, Vex), persisted preferences, conversation history,
  memory controls, English/Arabic behavior, and deterministic fallback behavior.
- Copilot onboarding quiz, manual copilot settings, collapsible/expandable panel, chat composer,
  suggestions, response actions, and interview mode.
- Live voice controls for speech-to-text and text-to-speech, with explicit English/Arabic selection
  and provider-failure fallback.
- Career artifacts and trusted knowledge-base support.

### Backend and trust foundation

- FastAPI + SQLite data layer with ordered migrations `0001` through `0014`.
- Hashed, expiring, revocable auth sessions; reset-token invalidation and rate limiting.
- Canonical role/skill model, ESCO import ledger, company-role mapping, and provenance.
- Student ownership checks and role authorization around private routes.
- Request-scoped provider diagnostics, redacted health responses, cache correctness, and honest
  demo/offline behavior.
- Assessment integrity events and verified-skill separation from self-reported claims.

### Source and verification assets

- All application source, tests, frontend contract checkers, browser-regression harnesses,
  configuration examples, Docker/dev-container files, launch scripts, and phase plans.
- A pull-request checklist, issue templates, and a security policy.
- Archived historical handoffs for context without presenting them as current instructions.

## Verification completed on this exact combined source

| Gate | Result |
|---|---|
| Frontend TypeScript | `npx tsc --noEmit` passed |
| Frontend production build | passed; non-blocking large-chunk advisory remains |
| Frontend contract checkers | 29/29 passed |
| Backend suite | 1614 passed, 5 skipped |
| Isolated server startup | passed on loopback with a fresh audit database |
| Authenticated HTTP smoke | login, auth/me, metrics, roles, jobs, learning, copilot, onboarding, scenarios, and tracker returned 200 |
| Browser console smoke | no console errors or warnings |
| Theme/interaction smoke | Professional/Casual Pulse, light/dark/system, and copilot collapse/expand worked |
| Secret scan | no real environment file, private key, known provider key pattern, or database included |

The backend run also emitted 584 deprecation warnings, mainly from FastAPI/httpx, cryptography, and
audio-library APIs. They do not fail the suite but should be paid down before production work.

## Known issues — do not hide these

### Priority 1: visual clarity and accessibility

The visual guardian found 200 genuine/pre-existing findings after overlay allowances: 184 contrast,
5 zero-size, 5 accessible-name, and 6 clipping findings. Confirmed examples in Professional Dark:

- the `Real jobs matching your skills` heading can become nearly invisible;
- the expanded `How is this score built?` row can render as a bright bar with low-contrast text;
- some expanded AI tutor headings/body text are too dark against the panel;
- small labels inside circular score rings feel cramped and need typographic/spacing refinement.

Treat this as a whole-app token and component-state repair. Do not patch only the screenshots above.
Verify 1440, 1024, 768, and 390 widths in both themes, including Arabic/RTL and keyboard focus.

### Priority 2: visual regression baselines

The screenshot harness captured 160 views: 60 unchanged and 100 with styling differences, with a
maximum 4.86% pixel delta. Most differences were accent bars and outlines, but the current visual
state still needs human approval before accepting new baselines.

### Priority 3: performance

The Vite build succeeds but reports large chunks (approximately 738 KB and 1.28 MB before gzip).
Introduce route/component splitting only after measuring the current load and interaction timings.

### Priority 4: live providers

- Voice synthesis requires a valid provider key and quota; an exhausted ElevenLabs account returns
  a handled service error instead of audio.
- Job-provider availability varies. The feed reports provider status and cached/stale state rather
  than pretending all sources are live.
- High-volume Egypt coverage still needs approved Egypt/MENA providers and scheduled ingestion. Do
  not scrape protected boards or call upstream providers every ten seconds.

### Priority 5: documentation history

`AGENTS.md` is an implementation journal and contains older stop points and test totals. Keep it for
traceability, but use this handoff and the code/tests as the current boundary.

## Recommended next work

1. Fix the design-token/state foundation for text contrast, semantic colors, focus, spacing,
   overflow, and score-ring labels across both presentation modes.
2. Run the guardian and screenshot matrix at 1440/1024/768/390, light/dark, English/Arabic; review
   every remaining exception before accepting baselines.
3. Add route-level code splitting and record before/after bundle and interaction measurements.
4. Complete a real-provider acceptance pass for all four mentors in English and Arabic using a
   funded TTS account, without recording keys or audio containing private data.
5. Decide the approved Egypt/MENA jobs-provider strategy, then build scheduled ingestion and
   database search rather than ten-second upstream polling.
6. Run an independent release review with no source edits, then tag the accepted prototype.

## Packaging and credential rules

- GitHub is source-only. It intentionally excludes `.env`, databases, uploads, dependency folders,
  generated builds, regression output, transcripts, and credentials.
- Transfer the private `.env` separately through an approved secure channel. Do not email it, paste
  it into an issue, or add it to an archive uploaded to GitHub.
- Start from `.env.example`; rotate any credential that has ever appeared in chat, screenshots,
  commit history, or an old shared ZIP.
- No production deployment should use the seeded demo passwords.

## Start here

```bash
git clone https://github.com/aboodko1/SkillBridge-upgrade.git
cd SkillBridge-upgrade
npm start
```

Then open the URL printed by the launcher. Use `npm start -- --reset` for a fresh seeded demo.

Before changing code:

1. Create a branch from the latest `main`.
2. Read this handoff, `README.md`, and the plan relevant to your task.
3. Reproduce the issue and save evidence without secrets.
4. Keep backend truth and permissions intact when changing the UI.
5. Run TypeScript, build, relevant contract checks, backend tests, and the visual matrix.
6. Open a pull request using the included checklist; do not push unfinished work directly to `main`.
