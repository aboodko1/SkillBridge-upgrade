# SkillBridge Current Update — Team Handoff

**Prepared:** 12 September 2026  
**Project:** SkillBridge  
**Current phase boundary:** Phases A–H complete; Phase I planned but not implemented

## 1. Executive summary

This handoff contains the team's original SkillBridge project plus the completed upgrades through Phase H. The project remains a React/TypeScript frontend served by a FastAPI backend with SQLite persistence. Existing routes, user roles, provider integrations, and environment-variable names were preserved.

The next team member should begin with Phase I. OpenCode created `PROVIDER_HEALTH_DIAGNOSTICS_PLAN.txt` and inspected the relevant code, but its usage limit stopped before Phase I implementation. Do not describe Phase I as complete.

## 2. Product overview

SkillBridge connects three user groups:

- Students assess skills, choose target roles, follow learning paths, practise scenarios, use AI tutoring, save roles, and view matched jobs.
- Companies define real job roles and required skills, inspect skill coverage, and map their roles to canonical catalog roles.
- University administrators view anonymized outcomes and operate the controlled ESCO catalog refresh API.

The main data loop is: company requirements → student skill evidence → gap analysis → personalized learning and practice → reassessment → updated verified profile → improved role/job matching.

## 3. Completed work

### Phase A — Baseline and audit

- Captured the starting state, routes, database behavior, UI behavior, providers, and verification commands.
- Documented the baseline in `BASELINE_BEFORE_BACKEND_ROLES_JOBS_UI.txt`.

### Phase B — Database/API reliability foundation

- Added an ordered SQLite migration system and migration ledger.
- Added request IDs to responses/errors and reliability checks.
- Preserved the existing database and API contracts.

### Phase C — Authentication and session hardening

- New session tokens are stored as SHA-256 hashes rather than raw bearer tokens.
- Sessions have expiry, heartbeat/last-seen behavior, and revocation.
- Password resets revoke existing sessions.
- Login and reset-request rate limits were added.
- Legacy sessions remain readable during migration but are subject to expiry.

### Phase D — Canonical roles and skills

- Added stable role keys, normalized titles, role families, statuses, aliases, ISCO codes, parent/supersession links, and skill provenance.
- Added normalized role search and migration `0003_canonical_roles`.

### Phase E — Versioned ESCO import and refresh

- Added a controlled preview-then-apply ESCO refresh workflow.
- Added version/language pins, import fingerprints, run/change ledgers, drift protection, and admin-only endpoints.
- Added migration `0004_esco_import`.
- Automated tests use fixtures and do not spend provider quota.

### Phase F — Company role to canonical role mapping

- Added ranked canonical-role suggestions with confidence and explanations.
- Mapping is always confirmed by a human; it is never applied automatically.
- Added confirm/change/unmap operations and append-only mapping history.
- Added the company mapping panel to Skills & Roles.
- Added migration `0005_company_role_mapping`.

### Phase G — Correct multi-user jobs cache

- Replaced the single shared cache entry with a bounded, TTL-based LRU cache.
- Cache keys now include every input that changes results without storing user identity, raw CV text, URLs, emails, or credentials.
- Added concurrent-request deduplication and request-isolated provider reports.
- Added honest feed states: `fresh`, `cached`, `stale_fallback`, and `unavailable`.

### Phase H — Job normalization, deduplication, and link quality

- Added a normalized internal job record with provider identity, fingerprints, provenance, work type, seniority, excerpts, dates, and link/listing state.
- Added conservative deduplication by provider ID, apply URL, or strict identity fallback.
- Unsafe schemes and private/internal hosts are rejected offline.
- Verified-dead links are retained internally for provenance but not shown in the feed.
- No test performs live link probes.

### Earlier visible product upgrades retained

- Three role-specific interfaces: Student, Company, and University Admin.
- Save Roles.
- Role-targeted practice scenarios with eight professional families plus safe generic blueprints.
- Scenario library, difficulty/status filters, history, hints, decision feedback, save/resume, and follow-up actions.
- Connected navigation between role details, learning, practice, and assessment.
- AI tutor modes/personas and multilingual behavior already present in the project.
- Multi-provider jobs feed with honest availability indicators.

## 4. Current verification state

- Last completed Phase H gate recorded: **991 passed, 5 skipped** backend tests.
- Frontend type check and Vite build were recorded clean at the Phase H gate.
- Migrations `0001` through `0005` are applied to the current local database.
- Fresh full backend verification for this handoff: **991 passed, 5 skipped** in 4m43s.
- Fresh frontend verification: **TypeScript check passed; Vite production build passed**.
- The frontend build reports a non-failing large-chunk warning; record code splitting as Phase S performance work.

## 5. Not finished

### Phase I — Honest provider health and diagnostics (next)

Status: **plan only; implementation not started**.

Required work:

- Add the exact public health vocabulary: `unconfigured`, `healthy`, `empty_success`, `cached`, `stale_fallback`, `rate_limited`, `unauthorized`, `network_unreachable`, `timeout`, `malformed_response`, `disabled_by_feature_flag`, and `unknown`.
- Preserve legacy `status` fields for frontend compatibility and add the new `health` field.
- Add request-scoped IDs to provider/build logs without logging search terms, CV data, URLs, or keys.
- Add a short, quota-free health snapshot cache.
- Harden public error redaction.
- Add offline tests for empty success, rate limits, timeouts, unauthorized responses, disabled providers, concurrency, transitions, redaction, and backward compatibility.

The approved design is in `PROVIDER_HEALTH_DIAGNOSTICS_PLAN.txt`.

### Later phases

- **J:** explainable role and job matching.
- **K:** saved jobs and a private application tracker.
- **L:** dedicated Role Explorer UI.
- **M:** role details, comparison, and career transitions.
- **N:** full Jobs Board and match experience.
- **O:** genuinely role-specific dashboards.
- **P:** broader profession-aware scenario coverage.
- **Q:** unified learning and job-application journey.
- **R:** accessibility, Arabic RTL, responsive behavior, and visual consistency.
- **S:** safe observability, performance bounds, and warning cleanup.
- **T:** fresh-session review without edits.
- **U:** complete offline and live verification.
- **V:** final reports and private delivery package.

## 6. Known problems and risks

1. **GitHub publication blocker:** a populated file named `env` is tracked in the existing Git history, and a populated `.env` exists locally. Never push that history or either populated file to GitHub. Rotate any key that may already have been shared.
2. **No GitHub destination is configured:** the local repository has no remote, and GitHub CLI is not installed. The owner must supply the exact repository URL and choose private/public visibility.
3. **Provider availability:** the last live check reported only 7 of 12 job providers available. JSearch was rate-limited, LinkedIn/Google returned subscription errors, and Jooble was unreachable. The application degrades honestly, but regional feeds may be thin.
4. **Phase I status mismatch:** the current provider diagnostics still use legacy status/reason combinations and do not yet implement the approved exact health vocabulary.
5. **No ESCO admin frontend:** ESCO refresh is backend-only.
6. **Role Explorer and Jobs Board are not yet dedicated full interfaces:** these are Phases L and N.
7. **Frontend testing is mostly contract/browser based:** there is no conventional frontend unit-test stack yet.
8. **Warning volume:** the full backend suite previously emitted thousands of warnings; address this in Phase S without hiding meaningful warnings.
9. **Docker path is not fully verified:** Docker files exist, but they were not part of the completed A–H runtime gate.
10. **LocalStorage bearer token:** the frontend stores the bearer token in `localStorage`. This is compatible with the current app but increases impact if an XSS bug is introduced. A production deployment should evaluate secure HttpOnly cookies plus CSRF protection.
11. **Development CORS:** the backend currently permits all origins. Limit origins before an internet-facing deployment.
12. **Prototype integrity scope:** webcam monitoring is metadata-only and is not production proctoring, video recording, or biometric verification.

## 7. Recommendations

### Immediate handoff priorities

1. Finish Phase I exactly from its approved plan and add the full offline test matrix.
2. Re-run the full backend suite, TypeScript check, Vite build, source-contract scripts, and live three-role walkthrough.
3. Keep all provider calls out of automated tests.
4. Update `AGENTS.md` and both handoff reports after every completed phase.

### Product priorities after Phase I

1. Build Phase J explainers so users understand why a role/job matches and what action improves the score.
2. Build Phase K application tracking with private notes, status history, reminders, and export.
3. Combine Phases L–N into a coherent Role Explorer → Role Detail → Job Board journey.
4. Use real backend state for role dashboards; do not create decorative or mocked metrics.
5. Complete Arabic RTL and keyboard/screen-reader work before adding more visual decoration.

### Deployment/security priorities

1. Publish a **clean source-only GitHub history** containing `.env.example`, API/provider code, migrations, tests, and documentation—but no populated environment files, database, uploads, virtual environments, dependencies, or generated build output.
2. Keep a separate **private team package** if the team truly requires runtime data. Transfer credentials using a password manager or encrypted channel, not GitHub.
3. Rotate the existing provider keys because the tracked `env` file means they must be treated as potentially exposed.
4. Before public/internet deployment, restrict CORS, add security headers, review token storage, disable demo credentials, and use a production database/service configuration.

## 8. Files the next agent must read first

1. `AGENTS.md`
2. `TEAM_HANDOFF_CURRENT_STATUS.md` or `TEAM_HANDOFF_CURRENT_STATUS.txt`
3. `PROVIDER_HEALTH_DIAGNOSTICS_PLAN.txt`
4. `JOB_LINK_QUALITY_PLAN.txt`
5. `JOB_CACHE_CORRECTNESS_PLAN.txt`
6. `AUTH_SESSION_MIGRATION_PLAN.txt`
7. `CANONICAL_ROLE_MODEL_PLAN.txt`
8. `ESCO_IMPORT_REFRESH_PLAN.txt`
9. `COMPANY_ROLE_MAPPING_PLAN.txt`

## 9. Run and verify

Backend tests on macOS with the current local environment:

```bash
cd backend
../.venv-mac/bin/python -m pytest -q -p no:cacheprovider -p no:randomly tests/
```

Frontend verification:

```bash
cd frontend
npm run typecheck
npm run build
```

Use the repository's cross-platform start scripts/README for a fresh machine. Run Uvicorn from `backend/` because imports use the `app.*` package path.

## 10. Packaging rule

There are two different deliverables:

- **GitHub source repository:** safe to clone; contains all source code, API integrations, environment variable names/examples, migrations, tests, and docs; excludes all live secrets and machine-generated/runtime data.
- **Private team handoff archive:** may retain the owner's complete local runtime copy when explicitly required, but must be transferred privately and never committed or attached to a public issue/repository.

Nothing in the product/API implementation is removed from the GitHub version. Only credentials and reproducible/private runtime artifacts are omitted from GitHub.
