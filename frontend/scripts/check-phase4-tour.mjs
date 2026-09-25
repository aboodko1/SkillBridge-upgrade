#!/usr/bin/env node
// Phase 4 gate — Welcome tour + contextual mini-tours.
// Mirrors the style of the other frontend contract checkers (drive from source).

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..')
const read = (p) => readFileSync(join(root, 'frontend', p), 'utf8')
const problems = []
const ok = (cond, label) => {
  if (!cond) problems.push(label)
}

const tour = read('src/components/ProductTour.tsx')
const app = read('src/App.tsx')
const css = read('src/index.css')

// ---- 1. Tour state is backend-persisted (server is source of truth).
ok(/api\.tourState\(studentId\)/.test(tour) && /\.setTourState\(studentId, patch\)/.test(tour),
  'tour state fetched & persisted through the API (backend source of truth)')
ok(/localStorage/.test(tour) && /OPTIONAL|optional|backend is the source of truth|cache/i.test(tour),
  'localStorage only an optional cache')

// ---- 2. Welcome tour: 5 steps only, required controls, Escape closes.
const steps = tour.match(/title: '[^']+',\n    body: '[^']+'/g) || []
ok(steps.length >= 4 && steps.length <= 5, `welcome tour is <= 5 steps (found ${steps.length})`)
for (const needle of ['Next', 'Back', 'Skip tour', "Don't show again", 'Finish']) {
  ok(tour.includes(needle), `control present: ${needle}`)
}
ok(/e\.key === 'Escape'/.test(tour) && /skip\(\)/.test(tour), 'Escape closes/skips the tour')
ok(/role="dialog"/.test(tour) && /aria-modal="true"/.test(tour) && /aria-labelledby="tour-title"/.test(tour),
  'welcome dialog semantics')
ok(/focus\(\)/.test(tour) && /e\.key !== 'Tab'/.test(tour), 'focus management (trap + first focus)')
ok(/prefers-reduced-motion/.test(css), 'reduced-motion respected in CSS')

// ---- 3. Lifecycle transitions persist server-side.
ok(/welcome_state: 'completed'/.test(tour), 'finish -> completed persisted')
ok(/welcome_state: 'skipped'/.test(tour) && /dont_show_again: true/.test(tour),
  'skip -> skipped; dont-show-again -> skipped + flag')

// ---- 4. Replay entry lives in the account menu.
ok(/tour\.replay\(/.test(app) && /Replay product tour/.test(app), 'account menu replays the tour')

// ---- 5. Contextual mini-tours on the three pages, dismissible, non-modal.
ok(/role="note"/.test(tour) && /MiniTourBanner/.test(tour), 'mini-tour banner is non-modal note')
ok(/markMiniDone\(page\)/.test(tour), 'mini-tour dismiss persists completion')
ok(/showMini\(page\)/.test(tour) && /welcome_state === 'active'/.test(tour),
  "minis hidden while the welcome tour is active")
const pages = ['SkillsRolesPage.tsx', 'LearningPage.tsx', 'AssessmentsPage.tsx']
for (const p of pages) {
  const src = read(`src/pages/${p}`)
  ok(/MiniTourBanner/.test(src) && /page="/.test(src), `mini-tour wired into ${p}`)
}
for (const cls of ['.tour-backdrop', '.tour-card', '.tour-actions', '.tour-skip', '.tour-dont',
  '.mini-tour', '.mini-tour-close']) {
  ok(css.includes(cls), `style ${cls} exists`)
}

// ---- 6. TourProvider wraps the app; useTour rendered inside it only.
ok(/<TourProvider>/.test(app) && /<Shell \/>/.test(app), 'TourProvider wraps Shell')
ok(/const tour = useTour\(\)/.test(app), 'Shell consumes useTour (inside provider)')

if (problems.length) {
  console.error('Phase 4 tour contracts violated:')
  for (const p of problems) console.error('  - ' + p)
  process.exit(1)
}
console.log('Phase 4 tour contracts OK')