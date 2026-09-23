// Assessments Phase 3 — "focused, not intimidating" frontend contract guard.
// Locks the landing facts, one-question-at-a-time player with Back, honest
// exit copy (no fake autosave/resume), and the results screen shape
// (plain-language headline, strengths <=3, improvement areas <=3, ONE primary
// next action, raw breakdowns behind "View details", status from backend).

import { readProject } from './path-helpers.mjs'

const read = readProject

const problems = []
const ok = (cond, msg) => { if (!cond) problems.push(msg) }

const assessments = read('frontend/src/pages/AssessmentsPage.tsx')
const css = read('frontend/src/index.css')

// ---- Landing screen: skills covered, approximate duration, question count,
// ---- what the result changes, and Start (all real, honest values).
ok(/asm-facts/.test(assessments) && /asm-fact/.test(assessments),
   'AssessmentsPage: per-assessment landing shows a facts strip')
ok(/\{questionCount\} questions/.test(assessments),
   'AssessmentsPage: landing lists the question count (10, backend default)')
ok(/About \{approxMinutes\} minutes/.test(assessments),
   'AssessmentsPage: landing lists an approximate duration')
ok(/Pass at \{passRule\}% or more/.test(assessments),
   'AssessmentsPage: landing states the real pass rule')
ok(/What this result changes/i.test(assessments),
   'AssessmentsPage: landing explains what the result changes')
ok(/raise your \{gap\.skill_name\} level/.test(assessments) && /Verified/.test(assessments),
   'AssessmentsPage: landing explains passing marks the skill Verified')
ok(/asm-what-changes/.test(css),
   'index.css: landing "what this changes" block is styled')

// ---- Player: one question at a time, progress, Back/Next, honest exit.
ok(/\{current \+ 1\} of \{questions\.length\}/.test(assessments),
   'AssessmentsPage: player shows "Question X of N" progress')
ok(/const previous = \(\) =>/.test(assessments) && /quiz-back/.test(assessments),
   'AssessmentsPage: player has a Back control to review an answered question')
ok(/Next question ›/.test(assessments) && /quiz-next/.test(assessments),
   'AssessmentsPage: Next remains the primary action')
ok(/doesn't autosave mid-attempt drafts/.test(assessments),
   'AssessmentsPage: exit dialog is honest that mid-attempt drafts are not autosaved/resumed')
ok(/start a new attempt any time/.test(assessments),
   'AssessmentsPage: exit dialog points to starting a new attempt as the return-later path')
ok(!/autosaves your answer|auto-saves your answer|resume your draft/i.test(assessments),
   'AssessmentsPage: no claim that answers are autosaved or drafts resume (backend has no attempt-state storage)')

// ---- Results: plain-language headline already presents backend status.
ok(/resultTitle = endedByIntegrity/.test(assessments) && /result\.passed \? `Assessment passed/.test(assessments),
   'AssessmentsPage: result headline is honestly derived from backend result.passed')
ok(/result\.integrity_status === 'review_required'/.test(assessments),
   'AssessmentsPage: integrity review states come from the backend integrity_status')

// ---- Results: strengths (max 3) and improvement areas (max 3).
ok(/const strengths = .*\.slice\(0, 3\)/.test(assessments),
   'AssessmentsPage: strengths are capped at three')
ok(/const improve = .*\.slice\(0, 3\)/.test(assessments),
   'AssessmentsPage: improvement areas are capped at three')
ok(/>Strengths</.test(assessments) && />Improvement areas</.test(assessments),
   'AssessmentsPage: results render Strengths and Improvement areas')
ok(/asm-chip strong/.test(assessments) && /asm-chip warn/.test(assessments),
   'AssessmentsPage: strengths/improvements render as plain-language chips')

// ---- Results: ONE primary next action pointing at a real existing action.
ok(/Improve \$\{String\(improve\[0\]\.competency\)/.test(assessments) && /Open \$\{gap\.skill_name\} learning plan/.test(assessments),
   'AssessmentsPage: results offer one clear improvement action or plan fallback')
ok(/onNavigate\?\.\('learning', \{ skillId: gap\.skill_id, roleTitle: roleTitleForPlan, competency: improve\[0\]\?\.competency \}\)/.test(assessments),
   'AssessmentsPage: the improvement action deep-links to Learning with the skill and weak topic')
ok(/asm-plan-cta/.test(assessments),
   'AssessmentsPage: primary plan action carries a dedicated class')

// ---- Raw score breakdowns / rubric / evidence behind "View details".
ok(/<details className="result-details">/.test(assessments) && /View details/.test(assessments),
   'AssessmentsPage: competency breakdown, integrity flags and question review sit behind a View details disclosure')
ok(/result-details/.test(css) && /result-details summary/.test(css) && /result-details-body/.test(css),
   'index.css: View details disclosure and its body are styled')

// ---- onNavigate is threaded from the page into the starter.
ok(/onNavigate\?: \(section: string, focus\?: \{ skillId: number; roleTitle: string; competency\?: string \}\) => void \}\) \{/.test(assessments),
   'AssessmentsPage: AssessmentStarter accepts onNavigate')
ok(/onNavigate=\{onNavigate\}/.test(assessments),
   'AssessmentsPage: onNavigate is passed at every AssessmentStarter render site')

if (problems.length) {
  console.error('Assessments Phase 3 frontend contract violations:')
  for (const problem of problems) console.error(`  - ${problem}`)
  process.exit(1)
}
console.log('Assessments Phase 3 frontend contracts OK')
