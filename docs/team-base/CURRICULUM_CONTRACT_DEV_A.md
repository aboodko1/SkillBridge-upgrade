# Dev A — Curated SQL Curriculum Contract (team-base batch 1)

Owner: **Dev A (Eslam)**. Scope: the curated CS knowledge base SQL slice owned by
Dev A per `docs/team-curriculum-ownership.md` (SQL = 10 blueprint topics, Git = 11).

This contract applies to the batch that ships the first two unfinished SQL
topics: **SQL Sorting & Limiting** (Beginner) and **SQL Aggregation**
(Intermediate).

## Where content lives

- Canonical lesson data: `backend/app/knowledge_base.py` (module-level topic
  dicts; only `"status": "complete"` entries may be served as lessons).
- Reviewed diagnostic questions: `knowledge_base.curated_diagnostic_questions`.
- Static practice review: additive per-topic functions in `backend/app/practice.py`.
- Tests: `backend/tests/test_curated_sql_foundations.py` and
  `backend/tests/test_curated_sql_foundations_2.py`.

The `backend/data_sources/` directory documented by the ownership file does not
exist in this checkout; the real loader is `knowledge_base.complete_lesson` +
`lessons.generate_lesson` + `genai.generate_diagnostic`, and Dev A edits those
Python facts directly.

## Hard rules (never crossed in this batch)

- Do NOT edit `frontend/src/components/LearningPage.tsx`, `backend/app/models.py`,
  `backend/app/main.py`, or any grading / Verified-Skill authority.
- Static SQL review only. SkillBridge never executes learner SQL and never
  connects to a database on the practice path; review cannot prove runtime results.
- Lessons never award Verified Skills; the Mini Check only marks a path topic
  completed (`lessons.MINI_CHECK_PASS_THRESHOLD = 0.7`, 3 questions).
- The preserved `SQL_QUERIES_FILTERING` topic is not changed byte-for-byte.
  Its `roadmap_rationale` mentions "the rest … are not represented as completed
  lessons here", which is now stale; that copy change is tracked as a follow-up,
  not part of this batch.

## Topic conventions

- Competency slug / display title:
  - `sql_queries_filtering` ↔ `SQL Queries & Filtering` (preserved)
  - `sql_sorting_limiting` ↔ `SQL Sorting & Limiting`
  - `sql_aggregation` ↔ `SQL Aggregation`
- `knowledge_base._key()` normalizes underscores to spaces and lowercases, so
  `complete_lesson` must match: `sorting & limiting`, `sql sorting & limiting`,
  `sql sorting limiting` and `aggregation`, `sql aggregation`.
- Grounding sources per topic (title + URL), English only:
  - Sorting & Limiting: PostgreSQL tutorial-select + SQLite `lang_select.html`.
  - Aggregation: PostgreSQL tutorial-agg + SQLite `lang_aggfunc.html`.
- Bilingual: the Arabic block lives under `locales.ar` and mirrors the English
  blocks 1:1 (same keys, no English answer-leak hints in `misconception_hint`).
- Prerequisites are curated and English-only: both new topics require
  `SQL Queries & Filtering`, so `path_builder` orders:
  `sql_queries_filtering` → `sql_sorting_limiting` → `sql_aggregation`.

## Static-practice review contract

Functions mirror `practice.sql_queries_filtering_static_check`:

- `practice.sql_sorting_limiting_static_check` — `sql_text` kind; read-only
  SELECT on `customers`; `ORDER BY total DESC`; `LIMIT 3`.
- `practice.sql_aggregation_static_check` — `sql_text` kind; read-only SELECT;
  `GROUP BY city`; `HAVING COUNT(...) >= 2` (aggregate guarded by read + group).
- Both return `None` unless the lesson's canonical source is
  `trusted_cs_knowledge_base` and the practice competency matches the topic.
- Both are additive and are NOT wired into the hardcoded static-check chain in
  `main.py` (that file cannot be edited); tests call them directly.

## Diagnostic convention

`genai.generate_diagnostic` serves curated questions first. The SQL branch of
`curated_diagnostic_questions` returns questions for all requested topics from
per-topic banks — 3 questions each, tags `sql_queries_filtering`,
`sql_sorting_limiting`, `sql_aggregation`. Question shape:
`{type, question, options, correct_answer, competency, difficulty}`.

## Test contract

- Update `test_curated_sql_foundations.py` counts: SQL diagnostic = 9 questions,
  competency set = 3 topics, personalized path = 3 items in the order above,
  while keeping every substantive Queries & Filtering assertion.
- Add `test_curated_sql_foundations_2.py` covering: bilingual content + mini
  checks 3/3 for both new topics; static checks accept good answers and reject
  mutations on both topics; full diagnostic → path → lesson → practice →
  mini-check flow does not verify the skill; preserved-topic anchors intact.

## Batch 2 & 3 status (completed — Dev A)

- **Batch 2** shipped `SQL_JOINS` and `SQL_SUBQUERIES` (complete, bilingual,
  mini checks, banking, static checks `practice.sql_joins_static_check` /
  `sql_subqueries_static_check`, focused tests; SQL diagnostic went 9 → 15
  questions, path 3 → 5 items).
- **Batch 3** shipped `SQL_INDEXING_BASICS` and `SQL_WINDOW_FUNCTIONS` (complete,
  bilingual, mini checks, banking, static checks
  `practice.sql_indexing_basics_static_check` / `sql_window_functions_static_check`,
  focused tests; SQL diagnostic went 15 → 21 questions, path 5 → 7 items).
  Remaining SQL blueprint topics, now in `PLANNED_TOPICS`: **Query
  optimization**, and later Transactions + Schema design.
- **Static checks remain additive and are NOT wired into the hardcoded chain in
  `backend/app/main.py`** (owner boundary: Dev C owns endpoint integration).
  `main.py` hardcodes only `python_functions_static_check`,
  `python_error_handling_static_check`, and `sql_queries_filtering_static_check`;
  all other SQL per-topic checks are exercised directly by tests. Verified
  empirically: a Joins / Subqueries / Indexing / Window endpoint practice
  submission carries **no** `static_check` key in `practice_task` and is graded
  by the generic evaluator (`fallback_evaluate_practice` offline), not the
  specialized check.

## Batch 4 (final SQL batch, completed — Dev A)

- Shipped the last three SQL blueprint topics: **Query optimization**,
  **Transactions**, and **Schema design** (complete, bilingual, 3 mini checks
  each with `correct_answer`, per-competency diagnostic banks, and static
  checks `practice.sql_query_optimization_static_check` /
  `sql_transactions_static_check` / `sql_schema_design_static_check`). SQL
  diagnostic is now **30 questions**, path is **10 items**, and
  `PLANNED_TOPICS` contains **no SQL** — only
  `("machine learning", "evaluation basics")` is left planned.
- Static checks stay additive/non-executing and are honest about that: query
  optimization cannot measure performance without a real database benchmark;
  transactions cannot prove commit/rollback/isolation/atomicity; schema design
  cannot prove deployment/validation. All three gate on the learner stating the
  static boundary, exactly like their earlier counterparts.
- `SQL_QUERIES_FILTERING` roadmap_rationale remains byte-for-byte untouched
  (per contract); the four stale "remaining competencies stay separately
  scoped" rationale texts authored in batches 1-2 (Sorting & Limiting,
  Aggregation, Joins, Subqueries) were updated to state the roadmap is
  complete, matching what batches 3-4 already did for Indexing/Window.
- Tests: `test_trusted_cs_knowledge_base.py` planned-topics test now pins all
  ten SQL competencies complete and nothing SQL planned;
  `test_curated_sql_foundations.py` counts 30 questions / 10 competencies / the
  exact 10-item path; `test_curated_sql_foundations_2.py` adds the three
  answer constants, static-review + scoping + bank + flow tests, grounding
  anchors, and a canonical blueprint-order test for all ten topics. Focused:
  **35 passed / 0 failed**; Learning-related sweep (17 files): **224 passed /
  2 skipped / 0 failed**.
- Boundary unchanged: no changes to `backend/app/main.py` (still only the
  three hardcoded checks at lines 2896-2902), `backend/app/models.py`,
  `frontend/src/components/LearningPage.tsx`, or core grading. New checks are
  direct-call-only; Dev C owns endpoint wiring, which is why no new check is
  API-wired yet.

## Batch 5 (Git batch 1 — first two Git topics, completed — Dev A)

- Shipped the first two canonical Git blueprint topics in order: **Local
  repositories** and **Committing** (both Beginner) as `GIT_LOCAL_REPOSITORIES`
  and `GIT_COMMITTING` in `knowledge_base.py` — complete, bilingual EN/عربي, 3
  reviewed mini checks each with `correct_answer`, per-topic diagnostic banks
  (`"local repositories"`, `"committing"` → 6 reviewed Git diagnostic questions),
  ≥2 official Git documentation groundings each (git-scm.com), `complete_lesson`
  branches for both display and slug competency forms. Nothing Git is in
  `PLANNED_TOPICS`; the other nine Git topics (Branching .. Large-repo
  strategies) are NOT served as complete content.
- Static checks `practice.git_local_repositories_static_check` /
  `git_committing_static_check` (kind `git_text`) are additive and never execute:
  they recognize only the narrow written-command exercise shape (folder entry +
  `git init` + `git status`; `git add README.md` + `git commit -m "<msg>"` +
  `git log`) and require the learner to state the static boundary. They review
  text only — no git is run, no repository is created or touched, no commit is
  claimed to exist.
- Committing declares **Local repositories** (display + slug) as a required
  foundation so the personalized-path prerequisite graph orders the two curated
  topics correctly (Local repositories → Committing); Local repositories declares
  Command line basics, matching the honest "written answer, not executed" frame.
- Tests: new `backend/tests/test_curated_git_foundations.py` — blueprint
  exact-order, only-first-two-complete, bilingual content + mini-checks, both
  static checks (never executes + scoping to their own lesson), and the full
  diagnostic → path → practice → mini-check flow that persists progress WITHOUT
  verifying the skill. Focused: **7 passed / 0 failed**; Learning-related sweep
  (18 test files incl. the new git file): **231 passed / 2 skipped / 0 failed**.
- Boundary unchanged: no changes to `backend/app/main.py` (still the three
  hardcoded checks at lines 2896-2902), `models.py`, `LearningPage.tsx`, or core
  grading. Git static checks are direct-call-only; Dev C owns endpoint wiring.

## Batch 6 (Git batch 2 — next two Git topics, completed — Dev A)

- Shipped the next two canonical Git blueprint topics in order: **Branching**
  (Beginner, 3rd) and **Merging** (Intermediate, 4th) as `GIT_BRANCHING` and
  `GIT_MERGING` in `knowledge_base.py` — complete, bilingual EN/عربي, 3 reviewed
  mini checks each with `correct_answer` + non-answer-revealing
  `misconception_hint`, per-topic diagnostic banks (`"branching"`, `"merging"`
  → 6 more reviewed Git questions; Git diagnostic now **12 questions** over 4
  competencies), ≥2 official Git documentation groundings each (git-scm.com
  docs + Pro Git), and `complete_lesson` branches for display and slug forms.
  Four Git topics are now content-complete in canonical order (Local
  repositories → Committing → Branching → Merging); the remaining seven
  (Rebasing .. Large-repo strategies) are NOT served as complete content and
  stay in `PLANNED_TOPICS`-adjacent reserve — nothing Git is planned.
- Prerequisites keep the display + slug pair so the personalized-path graph
  orders the four curated topics: Branching → prereq Committing
  (`git_committing`), Merging → prereq Branching (`git_branching`). The
  diagnostic → path flow now shows the exact 4-item canonical order
  `[git_local_repositories, git_committing, git_branching, git_merging]`.
- Static checks `practice.git_branching_static_check` /
  `git_merging_static_check` (kind `git_text`) are additive and never execute:
  branching recognizes create (`git branch feature-payment`) + switch
  (`git switch feature-payment`) + state inspection; merging recognizes
  `git switch main` + `git merge feature-payment` + `git log` and additionally
  requires a safe conflict-resolution note (edit conflicting lines, stage with
  `git add`, finish the commit). MERGING NEVER RUNS: no real merge, no file
  overwrite, no repository change — both the note and the evaluation contract
  say so.
- Tests: `backend/tests/test_curated_git_foundations.py` now has 9 tests —
  blueprint exact-order, only-first-four-complete, four bilingual lesson
  contracts (content + mini checks + grounding anchors), all four static
  reviews (never executes + own-lesson scoping), and the full diagnostic →
  path → practice → mini-check flow that persists progress for an Intermediate
  topic too and never verifies the skill. Focused: **9 passed / 0 failed**;
  Learning-related sweep (18 test files incl. the git file): **233 passed /
  2 skipped / 0 failed**.
- Boundary unchanged: no changes to `backend/app/main.py` (still the three
  hardcoded checks at lines 2896-2902), `models.py`, `LearningPage.tsx`, or core
  grading. Git static checks are direct-call-only; Dev C owns endpoint wiring.

## Batch 7 (Git batch 3 — next two Git topics, completed — Dev A)

- Shipped the next two canonical Git blueprint topics in order: **Rebasing**
  (Intermediate, 5th) and **Remotes & collaboration** (Intermediate, 6th) as
  `GIT_REBASING` and `GIT_REMOTES_COLLABORATION` in `knowledge_base.py` —
  complete, bilingual EN/عربي, 3 reviewed mini checks each with
  `correct_answer` + non-answer-revealing `misconception_hint`, per-topic
  diagnostic banks (`"rebasing"`, `"remotes & collaboration"` → 6 more reviewed
  Git questions; Git diagnostic now **18 questions** over 6 competencies), ≥2
  official Git documentation groundings each (git-scm.com docs + Pro Git), and
  `complete_lesson` branches for display and slug forms (including the
  ampersand-free slug form `git_remotes_collaboration`). Six Git topics are now
  content-complete in canonical order (Local repositories → Committing →
  Branching → Merging → Rebasing → Remotes & collaboration); the remaining five
  (History rewriting .. Large-repo strategies) are NOT served as complete
  content, and nothing Git is in `PLANNED_TOPICS`.
- Prerequisites keep the display + slug pair so the personalized-path graph
  orders the six curated topics: Rebasing → prereq Merging (`git_merging`),
  Remotes & collaboration → prereq Committing (`git_committing`). The
  diagnostic → path flow shows the exact 6-item canonical order
  `[git_local_repositories, git_committing, git_branching, git_merging,
  git_rebasing, git_remotes_collaboration]`.
- Static checks `practice.git_rebasing_static_check` /
  `git_remotes_collaboration_static_check` (kind `git_text`) are additive and
  never execute: rebasing recognizes `git switch feature-payment` +
  `git rebase main` + `git log` and requires a rebase-vs-merge / never-rebase-
  shared-history safety note; remotes recognizes `git fetch origin` +
  `git pull` + `git push origin feature-payment` and requires a fetch-vs-pull /
  Pull Request review note. REBASING NEVER RUNS (no rebase, no history rewrite)
  and REMOTES NEVER RUNS (no fetch/pull/push, no remote contact) — both notes
  and evaluation contracts say so.
- Tests: `backend/tests/test_curated_git_foundations.py` now has 11 tests —
  blueprint exact-order, only-first-six-complete, six bilingual lesson
  contracts (content + mini checks + grounding anchors), all six static
  reviews (never executes + own-lesson scoping), and the full diagnostic →
  path → practice → mini-check flow that persists progress and never verifies
  the skill. Focused: **11 passed / 0 failed**; Learning-related sweep (18
  test files incl. the git file): **235 passed / 2 skipped / 0 failed**.
- Boundary unchanged: no changes to `backend/app/main.py` (still the three
  hardcoded checks at lines 2896-2902), `models.py`, `LearningPage.tsx`, or core
  grading. Git static checks are direct-call-only; Dev C owns endpoint wiring.


## Batch 8 (Git batch 4 — next two Git topics, completed — Dev A)

- Shipped the next two canonical Git blueprint topics in order: **History
  rewriting** (Intermediate, 7th) and **Bisect & debugging** (Advanced, 8th) as
  `GIT_HISTORY_REWRITING` and `GIT_BISECT_DEBUGGING` in `knowledge_base.py` —
  complete, bilingual EN/عربي, 3 reviewed mini checks each with
  `correct_answer` + non-answer-revealing `misconception_hint`, per-topic
  diagnostic banks (`"history rewriting"`, `"bisect & debugging"` → 6 more
  reviewed Git questions; Git diagnostic now **24 questions** over **8
  competencies**), ≥2 official Git documentation groundings each (git-scm.com
  docs + Pro Git), and `complete_lesson` branches for display and slug forms
  (including `git history rewriting`, `bisect debugging`, `git bisect
  debugging`). Eight Git topics are now content-complete in canonical order
  (Local repositories → Committing → Branching → Merging → Rebasing → Remotes &
  collaboration → History rewriting → Bisect & debugging); the remaining three
  (Submodules, Workflows & policy, Large-repo strategies) are NOT served as
  complete content, and nothing Git is in `PLANNED_TOPICS`.
- Prerequisites keep the display + slug pair so the personalized-path graph
  orders the eight curated topics: History rewriting → prereq Rebasing
  (`git_rebasing`), Bisect & debugging → prereq Committing (`git_committing`).
  The diagnostic → path flow shows the exact 8-item canonical order
  `[git_local_repositories, git_committing, git_branching, git_merging,
  git_rebasing, git_remotes_collaboration, git_history_rewriting,
  git_bisect_debugging]`.
- Static checks `practice.git_history_rewriting_static_check` /
  `git_bisect_debugging_static_check` (kind `git_text`) are additive and never
  execute: history rewriting recognizes `git commit --amend` + `git rebase -i
  main` + `git log` and requires a local-vs-published safety note; bisect
  recognizes `git bisect start`/`bad`/`good`/`reset` and requires a
  midpoint / first-bad-commit note. HISTORY REWRITING NEVER RUNS (no amend, no
  rebase, no history rewrite) and BISECT NEVER RUNS (no bisect, no repo
  checkout) — both notes and evaluation contracts say so, and the review cannot
  prove any history was rewritten or any bisect happened.
- Tests: `backend/tests/test_curated_git_foundations.py` now has 13 tests —
  blueprint exact-order, only-first-eight-complete, eight bilingual lesson
  contracts (content + mini checks + grounding anchors), all eight static
  reviews (never executes + own-lesson scoping + targeted bad-case guidance for
  the two new checks), and the full diagnostic → path → practice → mini-check
  flow (24 questions, 8 competencies ×3, exact 8-item canonical order,
  History-rewriting persistence) that persists progress and never verifies the
  skill. Focused: **13 passed / 0 failed**; Learning-related sweep (18 test
  files incl. the git file): **237 passed / 2 skipped / 0 failed**.
- A fresh safety backup of the pre-edit curated knowledge base was created
  before this batch shipped (verified to contain all 2 Python + 10 SQL + 6 Git
  topic dicts and no secrets).
- Boundary unchanged: no changes to `backend/app/main.py` (still the three
  hardcoded checks at lines 2896-2902), `models.py`, `LearningPage.tsx`, or core
  grading. Git static checks are direct-call-only; Dev C owns endpoint wiring.

## Batch 9 (Git batch 5 — final three Git topics, completed — Dev A)

- Shipped the final three canonical Git blueprint topics in order: **Submodules**
  (Advanced, 9th), **Workflows & policy** (Advanced, 10th), **Large-repo
  strategies** (Advanced, 11th) as `GIT_SUBMODULES`, `GIT_WORKFLOWS_POLICY`,
  `GIT_LARGE_REPO_STRATEGIES` in `knowledge_base.py` — complete, bilingual
  EN/عربي, 3 reviewed mini checks each (`correct_answer` + non-answer-revealing
  `misconception_hint`), per-topic diagnostic banks (`"submodules"`,
  `"workflows & policy"`, `"large-repo strategies"` → 9 more reviewed Git
  questions; Git diagnostic now **33 questions** over **11 competencies**), and
  `complete_lesson` branches for display and slug forms (`git submodules`,
  `git workflows & policy`, `git workflows policy`, `git workflows and policy`,
  `git large-repo strategies`, `git large repo strategies`). All **eleven** Git
  blueprint topics are now content-complete in canonical order, and nothing Git
  is in `PLANNED_TOPICS`.
- Verification against `skill_blueprint.py:53-57` (authoritative): all three
  remaining topics are **Advanced** — the user-task labels "Intermediate (9th)"
  conflicted with the blueprint, and the blueprint won. Groundings are official
  git-scm.com docs / Pro Git plus git-lfs.com for LFS; the workflows example
  uses only real commands (`git switch -c`, `git push`, `git merge`) and
  describes the Pull Request as a hosting-service review step (no invented
  `git pull request` command).
- Prerequisites keep the display + slug pair for correct path ordering:
  Submodules → prereq Branching (`git_branching`); Workflows & policy → prereq
  Rebasing (`git_rebasing`); Large-repo strategies → dual prereqs History
  rewriting (`git_history_rewriting`) AND Bisect & debugging
  (`git_bisect_debugging`). The diagnostic → path flow shows the exact 11-item
  canonical order ending `[..., git_bisect_debugging, git_submodules,
  git_workflows_&_policy, git_large-repo_strategies]`.
- Static checks `practice.git_submodules_static_check` /
  `git_workflows_policy_static_check` / `git_large_repo_strategies_static_check`
  (kind `git_text`) are additive and never execute: submodules recognizes
  `git clone` + `git submodule init` + `git submodule update` and requires a
  pinned-commit note; workflows recognizes `git switch -c`/`git checkout -b` +
  `git push` + `git merge`/PR and requires a hosting-policy/review note; large
  repos recognize `git clone --depth 1` + `git clone --filter` +
  `git sparse-checkout set`/`disable` + `git lfs install`/`track` and require a
  limitations/trade-offs note. SUBMODULES ARE NEVER CLONED/INITIALIZED/UPDATED,
  NO POLICY IS EVER CONFIGURED, and NO PERFORMANCE IS EVER MEASURED — all notes
  and evaluation contracts say so.
- Tests: `backend/tests/test_curated_git_foundations.py` now has 16 tests —
  blueprint exact-order, all-eleven-complete (nothing reserved), eleven
  bilingual lesson contracts (incl. dual-prereq for large-repo), all eleven
  static reviews (never executes + own-lesson scoping + targeted bad-case
  guidance for the three new checks), and the full diagnostic → path → practice
  → mini-check flow (**33 questions, 11 competencies ×3**, exact 11-item
  canonical order, Submodules persistence) that persists progress and never
  verifies the skill. Focused: **16 passed / 0 failed**; curriculum regression
  sweep: **261 passed / 2 skipped / 0 failed** across 24 test files.
- A fresh durability backup was created before this batch shipped and verified:
  `C:\Users\user\Downloads\skillbridge-backup-20260918-20260918-192919`
  (robocopy, secrets/db/node_modules excluded) — confirmed to contain all 20
  topic dicts (2 Python + 10 SQL + 8 pre-batch Git), the git test file,
  `practice.py`, and this contract, with zero secret/database files leaked.
- Boundary unchanged: no changes to `backend/app/main.py` (still the three
  hardcoded checks at lines 2896-2902), `models.py`, `LearningPage.tsx`, or core
  grading. Git static checks are direct-call-only; Dev C owns endpoint wiring.