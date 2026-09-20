#!/usr/bin/env node
// Phase 5 gate — AI Mentor as a user-controlled companion.
// Server-persisted hide/reopen, compact launcher, keyboard access,
// mobile bottom-sheet, per-page contextual prompts (never auto-sent),
// localStorage-free panel.

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..')
const read = (p) => readFileSync(join(root, 'frontend', p), 'utf8')
const problems = []
const ok = (cond, label) => {
  if (!cond) problems.push(label)
}

const panel = read('src/components/CopilotPanel.tsx')
const css = read('src/index.css')
const i18n = read('src/lib/tutorI18n.ts')
const apiSrc = read('src/lib/api.ts')
const types = read('src/lib/types.ts')
const icons = read('src/components/Icons.tsx')

// ---- 1. Preference is server-persisted (backend source of truth), panel stays localStorage-free.
ok(/api\.mentorUi\(studentId\)/.test(panel) && /api\.setMentorUi\(studentId/.test(panel),
  'mentor UI preference fetched & persisted through the API')
ok(/panelPrefLoaded/.test(panel) && /setPanelVisiblePersisted/.test(panel),
  'load-once guard + persist helper present')
ok(/mentorUi: \(studentId: number\) =>/.test(apiSrc) && /setMentorUi: \(studentId: number, body: MentorUiUpdate\) =>/.test(apiSrc) &&
  /\/api\/students\/\$\{studentId\}\/mentor\/ui/.test(apiSrc),
  'api.mentorUi/setMentorUi point at /mentor/ui')
ok(/MentorUiState/.test(types) && /MentorUiUpdate/.test(types), 'MentorUiState/MentorUiUpdate types')
ok(!/localStorage/.test(panel), 'CopilotPanel remains localStorage-free (tutor-memory-2 contract)')

// ---- 2. Hide control + persistent compact launcher + keyboard access.
ok(/className="copilot-hide"/.test(panel) && /IconEyeOff/.test(panel) && /setPanelVisiblePersisted\(false\)/.test(panel),
  'hide button in the dock bar, eye-off icon, persists false')
ok(/mentor-launcher/.test(panel) && /setPanelVisiblePersisted\(true\)/.test(panel),
  'launcher shown when hidden, click reveals + persists true')
ok(/aria-label=\{ui\.hideMentor\}/.test(panel) && /aria-label=\{ui\.reopenMentor\.replace/.test(panel),
  'hide/reopen controls are aria-labelled')
ok(/hideMentor: s\('Hide mentor panel'/.test(i18n) && /hideMentor: s\('Hide mentor panel', 'أخف/.test(i18n),
  'localized hide label (EN + AR)')
ok(/reopenMentor: s\('Open \{name\}'/.test(i18n), 'localized reopen label (EN + AR)')
ok(/copilot:focus/.test(panel) && /setPanelVisiblePersisted\(true\)/.test(panel),
  'copilot:focus reopens the mentor (keyboard/any-surface entry)')

// ---- 3. Contextual prompts per page — localized, manual only, never auto-sent.
ok(/contextualPromptsFor\(/.test(panel) && /onClick=\{\(\) => void send\(undefined, c\.prompt\)\}/.test(panel),
  'contextual prompts render in the welcome state and send only on click')
ok(/ctx-prompts/.test(panel) && /ctx-chip/.test(panel), 'contextual prompt markup present')
ok(/export function contextualPromptsFor/.test(i18n) && /Record<CopilotPage/.test(i18n),
  'per-page contextual prompt templates keyed by CopilotPage')
for (const page of ['dashboard', 'skills_roles', 'learning', 'assessment', 'scenarios', 'jobs', 'career_roadmap', 'mock_interview']) {
  ok(new RegExp(`${page}: \\[`).test(i18n), `contextual prompt bucket for ${page}`)
}
ok(!/auto.?send/i.test(panel), 'no auto-sending of contextual prompts')

// ---- 4. Launcher + hide + prompts styled; mobile bottom-sheet; theme accents.
for (const sel of ['.copilot-hide', '.mentor-launcher', '.mentor-launcher-avatar', '.mentor-launcher-name',
  '.ctx-prompts', '.ctx-prompts-label', '.ctx-prompts-list', '.ctx-chip']) {
  ok(css.includes(sel), `style ${sel} exists`)
}
for (const theme of ['purple', 'blue', 'gold', 'green']) {
  ok(css.includes(`.mentor-launcher.${theme}`), `launcher theme accent ${theme}`)
}
ok(/@media \(max-width: 720px\)/s.test(css) && /\.copilot-panel\.copilot-open:not\(\.copilot-expanded\)/.test(css),
  'mobile bottom-sheet media query for the open (non-expanded) panel')
ok(/copilot-bar::before/.test(css) && /border-radius: var\(--radius\) var\(--radius\) 0 0/.test(css),
  'drawer grabber handle + rounded top corners on mobile')

// ---- 5. IconEyeOff shipped.
ok(/export const IconEyeOff/.test(icons), 'IconEyeOff icon exists')

if (problems.length) {
  console.error('Phase 5 mentor-companion contracts violated:')
  for (const p of problems) console.error('  - ' + p)
  process.exit(1)
}
console.log('Phase 5 mentor-companion contracts OK')