# HANDOFF_FOR_ESLAM.md

## 1. TL;DR — read this first

- **team-base** is the shared staging branch where Khaled lands job-provider and Docker work before it reaches your main.
- **State:** code is ready, but three decisions are blocking the next move. No commits have been pushed to your repo.
- **What you need to do:** read sections 3–5 and reply with one option for each decision using the template in section 8.
- **How to read:** straight through — sections 2 and 6–7 are context only; the asks are in 3, 4, and 5.

## 2. What's on team-base right now

Three local commits since `218bd6c`:

| Commit | Message |
|--------|---------|
| `9e8a482` | `fix(jobs): Jooble URL + cache-miss blocking` |
| `0fc9adc` | `feat(learning): Docker Containers + Images curated content` |
| `59037b5` | `fix(jobs): LinkedIn requires time_frame + title params` |

- **Nothing has been pushed to `eslamkan121-sketch/SkillBridge-Final`.**
- **Backup:** `khaled1234kh/SkillBridge-team-base` is up to date.
- **Your main** is untouched at `b3a1db2`.

## 3. DECISION 1 — Diagnostic question coverage (BLOCKS the Docker commit)

**Context:**

- Python skills already use **curated diagnostic questions** that fully replace the AI fallback for those skills.
- When Docker curated diagnostic banks were added for **Containers** and **Images**, the diagnostic stopped covering the other **9 Docker topics** (only 2 of 11 were tested). A student completing the diagnostic could no longer reach Final Assessment readiness.
- We **reverted** the Docker diagnostic banks. Diagnostic now uses the AI fallback for all 11 Docker topics (original behavior).
- Docker **lesson content** is unaffected.

**Choose one:**

- **A) REPLACE** — curated banks replace the fallback for a skill. Requires all 11 Docker topics to have curated banks before any can ship. Consistent with Python.
- **B) SUPPLEMENT** — curated banks supplement the fallback; uncovered topics use AI-generated questions. Smaller curation effort.
- **C) SOMETHING ELSE** — describe.

**What happens after your answer:**

- If **A**: hold Docker Batch 1 diagnostic banks until all 11 topics are curated, then re-commit.
- If **B**: re-add the 2 curated banks, and the diagnostic mixes them with AI-generated questions for the other 9.

## 4. DECISION 2 — Merge strategy for team-base into your main

Three options are documented at `docs/team-base/MERGE_PLAN_FOR_ESLAM.md`. Short version:

- **A) Cherry-pick** — you pull selected commits from team-base into main. Low risk, you control what lands.
- **B) Rebase-then-PR** — Khaled rebases team-base onto your latest main and opens a PR. Cleaner history, conflicts possible.
- **C) Reference-only** — you read team-base as a spec and reimplement pieces by hand.

Pick one. Nothing gets pushed to your repo until you say so.

## 5. DECISION 3 — Docker Batch 2 or pause?

Batch 1 delivered 2 topics (`Containers`, `Images`). 9 Docker topics remain. Batch 2 would be the next 2 (`basic_commands`, and the next in canonical order).

- **A) Continue Docker Batch 2 now**
- **B) Pause Docker, focus on merge + review first**
- **C) Change the batching** — fewer/more per batch

## 6. Current provider status (context — no action needed)

| Provider | Status | Note |
|----------|--------|------|
| Jooble | healthy | 20 jobs |
| Google Jobs | healthy | 10 jobs |
| Remotive, Jobicy, Arbeitnow, RemoteOK, Himalayas, Get on Board | healthy | — |
| LinkedIn | empty_success | 400 fixed, 0 jobs — not a bug |
| JSearch | rate_limited | quota, resets next month |
| Adzuna | request_failed | env placeholder App Key — do not chase |
| USAJobs | unsupported_country | correct for non-US profile |

## 7. What you do NOT need to worry about

- Nothing has been pushed to your repo.
- Nothing changed in your files (`path_builder.py`, `LearningPage.tsx`, diagnostic question banks, Learning acceptance spec).
- The Jooble, LinkedIn, Google Jobs, and cache-miss fixes are isolated in `backend/app/jobs.py` and covered by tests.

## 8. Reply template — paste this back

```
Decision 1 (diagnostic): A / B / C — <note if C>
Decision 2 (merge):      A / B / C — <note if C>
Decision 3 (Docker):     A / B / C — <note if C>
Any other feedback:      <free text>
```
