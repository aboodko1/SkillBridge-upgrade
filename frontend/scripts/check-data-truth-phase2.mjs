// Phase 2 — data truth, match consistency and trust language — source guard.
//
// Locks the frontend side of the canonical metric contract: the target-role
// number is read from the backend, catalogue similarity is a separately
// labelled name-overlap metric, a stale path is labelled, and no score is
// recomputed from raw counts in the browser.

import { readProject } from './path-helpers.mjs'

const read = readProject

const problems = []
const ok = (cond, msg) => { if (!cond) problems.push(msg) }

const roles = read('frontend/src/pages/SkillsRolesPage.tsx')
const learning = read('frontend/src/pages/LearningPage.tsx')
const dashboard = read('frontend/src/pages/DashboardPage.tsx')
const widgets = read('frontend/src/components/widgets.tsx')
const types = read('frontend/src/lib/types.ts')
const css = read('frontend/src/index.css')

// ---- 1. canonical metric keys exist in the type layer
ok(/export type CanonicalMetricKey =/.test(types)
   && /'target_requirement_coverage'/.test(types)
   && /'catalogue_similarity'/.test(types)
   && /'career_readiness'/.test(types)
   && /'verified_evidence_coverage'/.test(types),
   'types.ts defines the four canonical metric keys')
ok(/export interface MetricDefinition/.test(types) && /metric_definitions\?:/.test(types),
   'types.ts carries MetricDefinition + analysis.metric_definitions')
ok(/all_requirements_met\?: boolean/.test(types) && /missing_requirements\?: string\[\]/.test(types),
   'analysis carries all_requirements_met + missing_requirements')
ok(/stale\?: boolean/.test(types) && /path_stale\?: boolean/.test(types),
   'PersonalizedPath/FinalAssessmentStatus expose stale/path_stale')

// ---- 2. Skills & Roles: target coverage comes from the backend
ok(/const targetCoverage = analysis\?\.metrics\?\.target_requirement_coverage/.test(roles),
   'targetPct is sourced from analysis.metrics.target_requirement_coverage')
ok(!/const targetPct = cvSkillNames\.length/.test(roles),
   'the old raw name-overlap targetPct recomputation is gone')
ok(/all_requirements_met === true/.test(roles) && /missing_requirements/.test(roles),
   'the target summary distinguishes complete coverage from open requirements')
ok(/Target requirement coverage/.test(roles)
   && /still open/.test(roles),
   'the target gap section names Target requirement coverage and shows open requirements')
ok(/catalogue_similarity/.test(roles) && /Catalogue similarity/.test(roles)
   && /name overlap only/.test(roles),
   'the name-overlap fallback is labelled Catalogue similarity and documented as non-competence')
ok(/metric: 'target_requirement_coverage'/.test(roles)
   && /metric: 'catalogue_similarity'/.test(roles),
   'displayMatchOf records which canonical metric it returned')
ok(/match\.metricLabel/.test(roles) && /metricLabel=\{displayMatch\(r\)\.metricLabel\}/.test(roles),
   'cards/drawer render the metric label rather than a generic "match"')

// ---- 3. Learning: backend coverage + labelled stale path
ok(/analysis\?\.metrics\?\.target_requirement_coverage/.test(learning)
   && /Current requirement coverage/.test(learning),
   'Learning reads the backend coverage metric and labels it Requirement coverage')
ok(!/allGaps\.filter\(\(g\) => g\.status === 'strong'\)\.length \/ allGaps\.length/.test(learning),
   'Learning no longer recomputes a match from strong/total counts')
ok(/path\.stale/.test(learning) && /pp-stale-note/.test(learning)
   && /earlier diagnostic/.test(learning),
   'Learning labels a stale path instead of showing it as current')
ok(/finalStatus\.path_stale/.test(learning) && /not counted here/.test(learning),
   'Final Assessment coverage notes that stale path topics do not count')

// ---- 4. Dashboard: one named metric + gap-aware completion copy
ok(/Target requirement coverage/.test(dashboard)
   && /label="Requirement coverage"/.test(dashboard),
   'Dashboard labels the ring Target/Requirement coverage, not a bare "match"')
ok(/analysis\.all_requirements_met/.test(dashboard)
   && /All requirements currently met/.test(dashboard),
   'Dashboard completion copy is gated on all_requirements_met')
ok(/metric_definitions\?\.target_requirement_coverage/.test(dashboard),
   'Dashboard explainer comes from the backend metric definition')

// ---- 5. ScoreRing default label is not a generic "match"
ok(/label = 'Requirement coverage'/.test(widgets),
   'ScoreRing default label is Requirement coverage, never a bare "Match"')

// ---- 6. stale styling exists
ok(/\.pp-stale-note \{/.test(css) && /\.pp-stale-inline \{/.test(css),
   'index.css defines stale-path styling')

if (problems.length) {
  console.error('Data truth (Phase 2) contract violations:')
  for (const problem of problems) console.error(`  - ${problem}`)
  process.exit(1)
}
console.log('Data truth (Phase 2) contracts OK')
