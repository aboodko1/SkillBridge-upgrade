# HANDOFF_FOR_ABDELRAHMAN.md

**Integration branch:** `integration/eslam-khaled-docker`
**Integration commit:** see section 1 (single local commit on top of `6049f07`)
**Status:** local commit only — **not pushed, not merged into main/team-base**.

---

## 1. Branch and commit

- Branch: `integration/eslam-khaled-docker`
- Base commit before integration: `6049f07` (`feat(practice): wire curated static evaluators to API`)
- Integration commit: the **top commit** on the branch —
  `feat(integration): combine Eslam and Khaled curriculum and backend`.
  (This document lives inside that commit, so no hash is hardcoded here —
  confirm it with `git log --oneline -1`.)
- Verify locally with: `git log --oneline -3` on the branch.

This commit combines the curriculum and backend work of **Eslam** and **Khaled**
into one branch. Credit: Eslam (Python/SQL/Git curriculum, diagnostics,
learning quality, lessons) and Khaled (Docker curriculum, job-provider fixes,
browser-regression assets, handoff documentation).

## 2. What is integrated (completed features)

### Curriculum (curated `trusted_cs_knowledge_base` lessons + practice tasks)
| Skill   | Topics | Status |
|---------|--------|--------|
| Python  | 2/2    | Python Functions, Python Error Handling |
| SQL     | 10/10  | Queries & filtering, Sorting & limiting, Aggregation, Joins, Subqueries, Indexing basics, Window functions, Query optimization, Transactions, Schema design |
| Git     | 11/11  | Local repositories, Committing, Branching, Merging, Rebasing, Remotes & collaboration, History rewriting, Bisect & debugging, Submodules, Workflows & policy, Large-repo strategies |
| Docker  | 11/11  | Containers, Images, Basic commands, Dockerfile, Ports, Volumes, Networking, Compose, Multi-stage builds, Security & secrets, Orchestration basics |

### Practice API
- All **23 static evaluators** preserved and wired through
  `app/practice.py::_PRACTICE_STATIC_CHECK_EVALUATORS`
  (2 Python + 10 SQL + 11 Git), dispatched only for verified curated lessons.
- Docker practice is served from curated content; free-text tasks route through
  the standard provider/fallback path (no fabricated scores).

### Diagnostics
- Diagnostic coverage guarantee: every blueprint competency receives at least
  one question. Curated banks (Python/SQL/Git/Docker) serve first; the AI
  fallback now supplements up to the per-skill cap (`max_questions`) so a
  completed diagnostic can always reach Final Assessment readiness.
- Question-count assertions updated accordingly (`test_diagnostic.py`: 5-20
  topic questions; 5-15 in the API response).

### Job providers (Khaled's fixes, preserved)
- Jooble base URL corrected (`https://jooble.org/api/{key}`).
- LinkedIn RapidAPI requires `time_frame` + `title` params; generic RapidAPI
  fetcher supports `extra_params` and `suppress_default_params`.
- Cache-miss blocking semantics preserved.

### Frontend / browser
- Frontend source-contract guards (`backend/tests/test_runtime_*_frontend.py`)
  all pass against the built SPA.
- Browser acceptance spec added for future regression testing:
  `frontend/scripts/practice-git-python-sql.spec.mjs` (Playwright; runs against
  a disposable instance via `SKILLBRIDGE_FRONTEND_URL` / `SKILLBRIDGE_BACKEND_URL`).

## 3. ML status — explicitly UNFINISHED

- Machine Learning curriculum is **not curated**: blueprint has 11 topics
  (Data preparation, Training a first model, Evaluation basics, Feature
  engineering, Model selection, Validation & overfitting, Hyperparameter
  tuning, Model deployment, Ensembles, Drift & monitoring, Experiment tracking)
  but `knowledge_base.complete_lesson("Machine Learning", ...)` returns nothing
  for all of them.
- ML lessons/diagnostics therefore use the generic AI/fallback path. Treat ML
  as a known gap; do not present it as curated content.

## 4. Setup / run instructions

Prereqs: Python 3.14, Node 24, Chrome (for browser regression).

```powershell
# Backend deps (from repo root)
pip install -r backend/requirements.txt   # includes SpeechRecognition==3.17.0

# Run the app (seeds demo DB on startup, serves built frontend)
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# open http://localhost:8000  (demo logins use password demo1234)

# Backend tests
cd backend
python -m pytest tests/ -q            # serial run recommended (see flake note)

# Frontend contract guards only
python -m pytest tests/test_runtime_learning_phase1_frontend.py ... -q

# Frontend typecheck
npm run test:frontend

# Build frontend
npm run build

# Live browser regression (needs the app running on :8000 + Chrome)
cd scripts/browser-regression
npm install
node phase6-regression.js              # note: CHROME path is macOS-specific;
                                       # on Windows point it at chrome.exe
```

Environment: copy `.env` conventions from the repo docs; tests must stay
offline-capable (the suite monkeypatches network availability checks).

## 5. Tests actually executed (exact results)

| Suite | Result |
|-------|--------|
| Full backend (`backend/tests`, `-n 4` parallel) | **1660 passed, 4 skipped, 1 failed** in 968s |
| The 1 parallel failure — `test_artifacts_glm_tier.py::test_artifact_endpoint_uses_artifact_model` | **23/23 passed serially, twice** (~67s each). Resource-contention flake under parallel workers, not a regression. Serial full-suite expectation: 1664 passed / 4 skipped / 0 failed. |
| Frontend contract guards (23 runtime + voice UX) | **24 passed** in 4.5s |
| Live browser regression (Phase 6 Puppeteer, real Chrome, 1440/820/390 × 4 students + Company + University) | **91 passed, 0 failed**, console clean, no horizontal overflow, read-only |
| Targeted curriculum/practice smoke (practice dispatch + docker diagnostic + diagnostic) | **29 passed** |
| STT fallback (after installing locked `SpeechRecognition==3.17.0`) | **8/8 passed** |
| Learning quality grounding | **14/14 passed** (AI-path tests now bypass the curated short-circuit so they exercise the path they name; grounding assertions fully retained) |
| Lesson fencing | `test_lessons.py` **36 passed / 2 skipped** (fence guard moved from curated Git to uncurated Statistics) |

## 6. Known limitations / untested areas

- **ML curriculum unfinished** (see section 3).
- Parallel test runs can flake the GLM artifact-model test (provider probing
  under contention); run serially for a deterministic result.
- The Phase 6 browser harness reads seeded demo data and is read-only: it does
  not exercise scenario scoring, payments, or real provider keys.
- Live LLM/TTS/STT provider paths are only covered via mocks/fallbacks in CI;
  real-key behavior was not exercised in this pass.
- `scripts/browser-regression/phase6-regression.js` hardcodes a macOS Chrome
  path; on Windows point `CHROME` at `chrome.exe` (a patched copy was used for
  the run above — no repo change made).

## 7. Preservation instructions (IMPORTANT)

- **Do not revert or trim** any curated content in
  `backend/app/knowledge_base.py` (Python/SQL/Git/Docker), the evaluator
  registry in `backend/app/practice.py`, the diagnostic supplementation in
  `backend/app/genai.py`, the curated-resource additions in
  `backend/app/resources.py`, or the job-provider fixes in
  `backend/app/jobs.py`.
- Keep the Practice API evaluator wiring intact: new curated topics must add
  their evaluator to `_PRACTICE_STATIC_CHECK_EVALUATORS` and never fabricate
  scores for uncurated lessons.
- Keep the diagnostic coverage guarantee (every competency gets a question).

## 8. How to obtain the integrated branch safely

The commit is **local only** (no push performed). To transfer:

```powershell
# Option A — bundle file (recommended, no remote needed)
git bundle create skillbridge-integration.bundle integration/eslam-khaled-docker
# send the .bundle file; receiver:
git clone skillbridge-integration.bundle -b integration/eslam-khaled-docker SkillBridge

# Option B — direct fetch from this machine's repo path
git fetch <this-repo-path> integration/eslam-khaled-docker:integration/eslam-khaled-docker

# Option C — push to a shared remote ONLY with explicit approval
git push <remote> integration/eslam-khaled-docker
```

After obtaining it: `git checkout integration/eslam-khaled-docker`, then follow
section 4. Verify integrity with `git log --oneline -3` (top commit should be
the integration commit listed in section 1).

---

*Prepared 2026-09-19. Integration work by Eslam and Khaled; merge, regression
and handoff assembled on the integration branch.*
