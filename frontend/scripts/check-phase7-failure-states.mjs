// Phase 7 — accessibility + failure-state source guard.
//
// Locks the Phase 7 acceptance contract:
//   - jobs retry is wired to a real action (setRetryJobs / retryLiveJobs)
//   - every required flow has a loading/empty/error-with-retry path that never
//     shows raw server detail (sanitizeServerDetail is used in api.ts)
//   - error containers are role="alert", loading containers role="status"
//   - retry controls are real <button> elements
//   - code snippets stay LTR inside RTL pages (CSS direction: ltr)
//   - a shared failure-classification helper exists (no raw text to users)

import { readProject } from './path-helpers.mjs'

const read = readProject

const problems = []
const ok = (cond, msg) => { if (!cond) problems.push(msg) }

const api = read('frontend/src/lib/api.ts')
const dashboard = read('frontend/src/pages/DashboardPage.tsx')
const learning = read('frontend/src/pages/LearningPage.tsx')
const assessments = read('frontend/src/pages/AssessmentsPage.tsx')
const copilot = read('frontend/src/components/CopilotPanel.tsx')
const chat = read('frontend/src/components/ChatThread.tsx')
const responseActions = read('frontend/src/components/ResponseActions.tsx')
const i18n = read('frontend/src/lib/tutorI18n.ts')
const failure = read('frontend/src/lib/failureStates.ts')
const css = read('frontend/src/index.css')

// ---- 1. jobs retry is a real action
ok(/retryJobs/.test(dashboard) && /setRetryJobs\(\(count\) => count \+ 1\)/.test(dashboard),
   'Dashboard jobs retry increments retryJobs to re-issue the fetch')
ok(/retryLiveJobs/.test(dashboard) && /onClick=\{retryLiveJobs\}/.test(dashboard),
   'Dashboard jobs retry buttons call retryLiveJobs')

// ---- 2. sanitizeServerDetail exists and is applied in api.ts
ok(/function sanitizeServerDetail/.test(api)
   && /sk-|api[_-]?key|secret|credential|password/.test(api)
   && /Traceback|Exception:/.test(api),
   'api.ts sanitizeServerDetail blocks credential-like and traceback detail')
ok(/sanitizeServerDetail\(res\.status, detail\)/.test(api),
   'api.ts applies sanitizeServerDetail to every error detail')

// ---- 3. loading + empty + error-with-retry across the required flows
//   jobs
ok(/role="status"/.test(dashboard) && /jobs-loading-skel/.test(dashboard),
   'Dashboard jobs shows a loading skeleton with role="status"')
ok(/role="alert"/.test(dashboard) && /Retry jobs/.test(dashboard),
   'Dashboard jobs error is role="alert" with a Retry button')
ok(/pulse-job-empty/.test(dashboard) && /No matching live roles/.test(dashboard),
   'Dashboard jobs has an empty state')
//   diagnostics + lessons (LearningPage)
ok(/role="status"/.test(learning) && /diag-loading/.test(learning),
   'Learning diagnostic has a loading state with role="status"')
ok(/role="alert"/.test(learning) && /setRetryKey\(\(k\) => k \+ 1\)/.test(learning),
   'Learning recommendation error is role="alert" with a real retry')
ok(/retryLoad/.test(learning) && /onClick=\{retryLoad\}/.test(learning),
   'Learning diagnostic panel has an explicit Retry control')
//   assessments
ok(/retryKey/.test(assessments) && /onClick=\{\(\) => setRetryKey\(\(k\) => k \+ 1\)\}/.test(assessments),
   'Assessments load error has a retry that re-issues the load')
ok(/role="alert"/.test(assessments),
   'Assessments error is role="alert"')
//   tutor (send + regenerate)
ok(/ui\.tutorUnavailable/.test(copilot) && !/err\.message.*appendChat/.test(copilot),
   'Copilot tutor failure surfaces localized tutorUnavailable, never raw detail')
ok(/regenerate/.test(copilot) && /setRetryingKey/.test(copilot) && /onRetry/.test(copilot),
   'Copilot regenerate retries with a real retrying state')
ok(/onRetry=\{\(\) => onRetry\(message\)\}/.test(chat)
   && /aria-label=\{ui\.tryAgain\}/.test(responseActions)
   && /type="button"/.test(responseActions)
   && /onClick=\{onRetry\}/.test(responseActions),
   'ChatThread + ResponseActions wire a real, aria-labelled retry button')
ok(/role="status"/.test(chat) && /busy-ellipsis/.test(chat),
   'ChatThread busy indicator is role="status"')

// ---- 4. localized copy (EN + AR) for the new failure text
ok(/tutorUnavailable: s\(/.test(i18n),
   'tutorI18n carries bilingual tutorUnavailable copy')
ok(/OFFLINE_MESSAGES/.test(failure) && /NETWORK_ERROR_MESSAGES/.test(failure)
   && /ar:/.test(failure),
   'failureStates defines bilingual offline/network messages')

// ---- 5. code snippets stay LTR inside RTL pages
ok(/\.md-body pre,/.test(css) && /direction: ltr/.test(css)
   && /unicode-bidi: isolate/.test(css),
   'index.css forces code blocks LTR + isolate inside RTL pages')

if (problems.length) {
  console.error('Phase 7 failure-state contract violations:')
  for (const problem of problems) console.error(`  - ${problem}`)
  process.exit(1)
}
console.log('Phase 7 failure-state contracts OK')