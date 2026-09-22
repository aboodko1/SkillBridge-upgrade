#!/usr/bin/env node
// Phase 7 static gate: the high-risk, user-facing resilience and accessibility
// safeguards must remain in source even when individual pages are restyled.

import { readFileSync } from 'fs'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..')
const read = (path) => readFileSync(join(root, path), 'utf8')
const problems = []
const ok = (condition, label) => { if (!condition) problems.push(label) }

const dashboard = read('frontend/src/pages/DashboardPage.tsx')
const api = read('frontend/src/lib/api.ts')
const chat = read('frontend/src/components/ChatThread.tsx')
const css = read('frontend/src/index.css')
const main = read('backend/app/main.py')

ok(/const \[retryJobs, setRetryJobs\] = useState\(0\)/.test(dashboard), 'job-feed retry state exists')
ok(/const retryLiveJobs = \(\) => \{[\s\S]*setRetryJobs\(\(count\) => count \+ 1\)/.test(dashboard), 'retry action re-runs the job request')
ok(/Retry live jobs/.test(dashboard) && /Retry jobs/.test(dashboard), 'visible retry actions exist for unavailable and failed feeds')
ok(/role="alert"/.test(dashboard), 'job-feed errors announce to assistive technology')

ok(/function sanitizeServerDetail/.test(api) && /SAFE_DETAIL_MAX/.test(api), 'unsafe server detail sanitizer exists')
ok(/api_secret|credential|password|authorization/i.test(api), 'credential-like server details are rejected')
ok(/const safe = sanitizeServerDetail/.test(api), 'HTTP error paths use the sanitizer')
ok(/detail="STT service unavailable"/.test(main) && /detail="Speech-to-text failed"/.test(main), 'STT returns safe student-facing failures')

ok(/role="status"/.test(chat) && /visually-hidden/.test(chat), 'mentor busy indicator has screen-reader status text')
ok(/\.sr-only, \.visually-hidden/.test(css), 'both screen-reader utility names are styled')
ok(/\[dir="rtl"\] \.md-body pre/.test(css) && /direction: ltr/.test(css), 'RTL lesson code remains left-to-right')
ok(/\.jobn-filterbar > \*/.test(css) && /min-width: 0/.test(css), 'shared dynamic cards have a narrow-screen shrink guard')

if (problems.length) {
  console.error('Phase 7 resilience contracts violated:')
  for (const problem of problems) console.error(`  - ${problem}`)
  process.exit(1)
}
console.log('Phase 7 resilience contracts OK')
