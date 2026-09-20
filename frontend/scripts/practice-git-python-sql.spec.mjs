/**
 * Browser acceptance for the practice static-check dispatch on top of the
 * curated learning flow. Mirrors the repo's own learning-acceptance.spec.mjs
 * helpers so the same UI primitives are exercised.
 *
 * Set SKILLBRIDGE_FRONTEND_URL and SKILLBRIDGE_BACKEND_URL to a disposable
 * instance before running (backend serves the built SPA, so one origin works).
 */
import { test, expect, chromium } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

const FRONTEND = process.env.SKILLBRIDGE_FRONTEND_URL
const BACKEND = process.env.SKILLBRIDGE_BACKEND_URL
const OUT = path.join(process.cwd(), 'test-results', 'practice-git-python-sql')
const email = `practice.acceptance.${Date.now()}@example.test`
const password = 'SyntheticAcceptance9!'
let browser, context, page, token, studentId, pythonId, sqlId, gitId, verifiedBefore, practiceResponses

test.describe.configure({ mode: 'serial' })
test.setTimeout(90000)

async function api(pathname, options = {}) {
  const response = await fetch(`${BACKEND}${pathname}`, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) } })
  const text = await response.text()
  if (!response.ok) throw new Error(`${options.method || 'GET'} ${pathname} -> ${response.status}: ${text}`)
  return text ? JSON.parse(text) : null
}
async function shot(name) { fs.mkdirSync(OUT, { recursive: true }); await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true }) }
async function closeOnboarding() {
  const dialog = page.getByRole('dialog', { name: 'Find your SkillBridge mentor' })
  await expect(dialog).toBeVisible()
  await dialog.getByRole('button', { name: 'Close (decide later)' }).click()
  await expect(dialog).toBeHidden()
}
async function learning() {
  const onboarding = page.getByRole('dialog', { name: 'Find your SkillBridge mentor' })
  const nav = page.getByRole('button', { name: 'Learning', exact: true })
  if (await onboarding.isVisible()) await closeOnboarding()
  await expect(nav).toBeEnabled()
  try {
    await nav.click({ timeout: 10_000 })
  } catch (error) {
    if (!await onboarding.isVisible()) throw error
    await closeOnboarding()
    await nav.click()
  }
  await expect(page.getByRole('heading', { name: 'Learning', exact: true })).toBeVisible()
}
async function skill(name) {
  const card = page.locator('.learning-skill-card').filter({ hasText: name }).first()
  await expect(card).toBeVisible(); await card.click()
  await expect(page.locator('#skill-detail').getByRole('heading', { name, exact: true })).toBeVisible()
}
async function createPath(expected) {
  const questions = page.locator('.diag-question')
  // The panel re-renders while per-skill path lookups resolve, so a normal
  // click can spin on detached nodes. Force-dispatch on the current DOM node
  // and verify the diagnostic actually opened (retry a couple of times).
  for (let attempt = 0; attempt < 3; attempt++) {
    const start = page.getByRole('button', { name: 'Start Diagnostic', exact: true })
    await expect(start).toBeVisible()
    await start.click({ force: true, timeout: 5000 }).catch(() => {})
    await page.waitForTimeout(600)
    try {
      await expect(questions).toHaveCount(expected.length, { timeout: 8000 })
      break
    } catch {
      if (attempt === 2) throw new Error('Diagnostic failed to open after retries')
    }
  }
  await expect(questions.locator('.diag-comp-chip').allTextContents()).resolves.toEqual(expected)
  for (let i = 0; i < expected.length; i++) await questions.nth(i).locator('input[type="radio"]').last().check()
  await page.getByRole('button', { name: 'Submit Diagnostic', exact: true }).click()
  const create = page.getByRole('button', { name: 'Create My Learning Path', exact: true })
  await expect(create).toBeVisible(); await create.click()
  await expect(page.locator('.pp-item')).toHaveCount(new Set(expected).size)
}
async function resume(topic, skillName) {
  const card = page.locator('.continue-card').filter({ hasText: skillName }).first()
  await expect(card).toBeVisible()
  await expect(page.locator('#skill-detail .pp-item').first()).toBeVisible({ timeout: 30_000 })
  for (let attempt = 0; attempt < 3; attempt++) {
    const btn = card.getByRole('button', { name: 'Continue Learning', exact: true })
    await expect(btn).toBeVisible()
    await btn.click({ force: true, timeout: 5000 }).catch(() => {})
    await page.waitForTimeout(600)
    const lesson = page.locator('.lesson-view:not(.lesson-loading-skel)')
    try {
      await expect(lesson).toContainText(topic, { timeout: 15_000 })
      await expect(page.locator('.diagnostic-questions')).toHaveCount(0)
      return
    } catch {
      if (attempt === 2) throw new Error(`Lesson failed to open for ${topic}`)
    }
  }
}
async function practiceAnswer(answer, expectSound) {
  await page.locator('#skill-detail').getByRole('button', { name: 'Practice', exact: true }).click()
  const field = page.locator('textarea.practice-response')
  await expect(field).toBeVisible(); await field.fill(answer)
  const [response] = await Promise.all([
    page.waitForResponse((res) => res.url().includes('/practice') && res.request().method() === 'POST'),
    page.locator('#skill-detail').getByRole('button', { name: 'Submit Practice', exact: true }).click(),
  ])
  practiceResponses.push(await response.json())
  if (expectSound) {
    const toCheck = page.locator('#skill-detail').getByRole('button', { name: 'Continue to Mini Check', exact: true })
    await expect(toCheck).toBeVisible()
} else {
    await expect(page.locator('#skill-detail .lesson-quality-label').filter({ hasText: 'Static' })).toBeVisible()
    await expect(page.locator('#skill-detail').getByRole('button', { name: 'Continue to Mini Check', exact: true })).toHaveCount(0)
  }
}
async function miniCheckCorrect(competency, skillName) {
  const lesson = await api(`/api/students/${studentId}/learning/${skillIdByName(skillName)}/lessons/${competency}`)
  const questions = (lesson.content.mini_check || {}).questions || []
  for (const q of questions) {
    const correct = q.correct_answer
    await page.getByRole('button', { name: correct, exact: true }).waitFor()
    await page.getByRole('button', { name: correct, exact: true }).click()
  }
  await page.locator('#skill-detail').getByRole('button', { name: 'Submit Mini Check', exact: true }).click()
  await expect(page.locator('.lesson-result')).toContainText('topic completed')
}
function skillIdByName(name) {
  return name === 'SQL' ? sqlId : name === 'Git' ? gitId : pythonId
}
async function diagChips(skillId) {
  const diag = await api(`/api/students/${studentId}/learning/${skillId}/diagnostic/generate`, { method: 'POST', body: '{}' })
  return diag.questions.map((q) => q.competency)
}

test.beforeAll(async () => {
  if (!FRONTEND || !BACKEND) throw new Error('Set SKILLBRIDGE_FRONTEND_URL and SKILLBRIDGE_BACKEND_URL to the isolated test instance.')
  const status = await fetch(`${BACKEND}/api/system/db-status`)
  if (!status.ok) throw new Error(`Backend unavailable at ${BACKEND}: ${status.status}`)
  browser = await chromium.launch({ headless: true }); context = await browser.newContext({ viewport: { width: 1440, height: 900 } }); page = await context.newPage()
  practiceResponses = []
})
test.afterEach(async ({}, info) => { if (info.status !== info.expectedStatus) await shot(`FAIL-${info.title.replace(/[^a-z0-9]+/gi, '-')}`) })
test.afterAll(async () => { await context?.close(); await browser?.close() })

test('setup: UI signup, Backend Engineer target, capture Python/SQL/Git ids', async () => {
  await page.goto(`${FRONTEND}/login`)
  await page.getByRole('button', { name: 'Create account', exact: true }).first().click()
  const form = page.locator('form')
  const inputs = form.locator('input')
  await inputs.nth(0).fill('Practice Dispatch Synthetic')
  await inputs.nth(1).fill(email); await inputs.nth(2).fill(password)
  const selects = form.locator('select')
  await selects.first().selectOption({ label: 'Student seeking roles' }); await selects.nth(1).selectOption({ label: 'Egypt' })
  await expectsVisibleSelects(form, selects)
  await form.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard', exact: true })).toBeVisible()
  token = await page.evaluate(() => localStorage.getItem('skillbridge_token')); expect(token).toBeTruthy()
  const me = await api('/api/auth/me'); studentId = me.student.id; verifiedBefore = me.student.verified_skills || []
  await closeOnboarding()
  const roles = await api('/api/roles')
  const be = [...roles.catalog, ...roles.roles].find(role => role.title === 'Backend Engineer')
  expect(be).toBeTruthy(); await api(`/api/students/${studentId}`, { method: 'PUT', body: JSON.stringify({ target_role_id: be.id }) })
  const skills = await api('/api/skills')
  pythonId = skills.find(row => row.name === 'Python').id; sqlId = skills.find(row => row.name === 'SQL').id; gitId = skills.find(row => row.name === 'Git').id
  expect(pythonId).toBeTruthy(); expect(sqlId).toBeTruthy(); expect(gitId).toBeTruthy()
})
async function expectsVisibleSelects(form, selects) {
  await expect(selects.nth(2)).toBeVisible(); await selects.nth(2).selectOption({ index: 1 }); await selects.last().selectOption({ index: 1 })
}

test('Python Functions: incorrect practice shows needs-fix, correct practice continues, mini-check completes, reload persists', async () => {
  await learning(); await skill('Python')
  await createPath(await diagChips(pythonId))
  await resume('Python Functions', 'Python')
  // Incorrect answer: wrong function name, no return -> static check must flag.
  await practiceAnswer('def wrong_name(n):\n    pass', false)
  // Correct answer passes the structural check.
  await practiceAnswer('def celsius_to_fahrenheit(celsius):\n    return (celsius * 9 / 5) + 32\n\nreturn lets the caller reuse and test the converted value.', true)
  await page.locator('#skill-detail').getByRole('button', { name: 'Continue to Mini Check', exact: true }).click()
await miniCheckCorrect('python_functions', 'Python')
  // The practice endpoint must not fabricate a lesson completion, verified
  // skills, or a hidden score inside the static check.
  const lastSound = practiceResponses[practiceResponses.length - 1]
  expect(lastSound.attempt.practice_task.static_check.status).toBe('looks_structurally_sound')
  expect(lastSound.attempt.practice_task.static_check.score).toBeUndefined()
  expect(lastSound.attempt.practice_task.static_check.verified).toBeUndefined()
  expect(lastSound.attempt.practice_task.static_check.completed).toBeUndefined()
  expect(lastSound.attempt.lesson_completed).toBeUndefined()
  expect(lastSound.attempt.verified_skills).toBeUndefined()
  await page.locator('#skill-detail').getByRole('button', { name: 'Next Lesson', exact: true }).click()
  await expect(page.locator('.lesson-view:not(.lesson-loading-skel)')).toContainText('Python Error Handling', { timeout: 30_000 })
  await practiceAnswer('def parse_score(text):\n    try:\n        return int(text)\n    except ValueError:\n        return None\n\nA bare except could hide an unrelated programming bug.', true)
  await page.locator('#skill-detail').getByRole('button', { name: 'Continue to Mini Check', exact: true }).click()
  await miniCheckCorrect('python_error_handling', 'Python')
  await page.reload(); await learning(); await skill('Python')
  await expect(page.locator('#skill-detail')).toContainText('2/2 topics complete')
  await shot('python-completed-and-persisted')
})

test('SQL Queries & Filtering: correct practice, mini-check and persistence', async () => {
  await page.reload(); await learning(); await skill('SQL')
  await createPath(await diagChips(sqlId))
  await resume('SQL Queries & Filtering', 'SQL')
  await practiceAnswer("SELECT name, email\nFROM customers\nWHERE city = 'Cairo'\n  AND status = 'active';\n\nThe city condition keeps Cairo customers, and the status condition keeps active customers.", true)
const lastSound = practiceResponses[practiceResponses.length - 1]
  expect(lastSound.attempt.practice_task.static_check.kind).toBe('sql_text')
  expect(lastSound.attempt.practice_task.static_check.status).toBe('looks_structurally_sound')
  expect(lastSound.attempt.practice_task.static_check.score).toBeUndefined()
  expect(lastSound.attempt.lesson_completed).toBeUndefined()
  expect(lastSound.attempt.verified_skills).toBeUndefined()
  await page.locator('#skill-detail').getByRole('button', { name: 'Continue to Mini Check', exact: true }).click()
await miniCheckCorrect('sql_queries_filtering', 'SQL')
  await page.reload(); await learning(); await skill('SQL')
  await expect(page.locator('#skill-detail')).toContainText('1/10 topics complete')
  await shot('sql-completed-and-persisted')
})

test('Git Local repositories: correct practice, mini-check and persistence', async () => {
  await page.reload(); await learning(); await skill('Git')
  await createPath(await diagChips(gitId))
  await resume('Local repositories', 'Git')
  const lesson = await api(`/api/students/${studentId}/learning/${gitId}/lessons/git_local_repositories`)
  const starter = (lesson.content.practice || {}).starter_code || ''
  await practiceAnswer(`${starter}\n\nThis is a written answer explaining the exact commands I would run and the order to run them; SkillBridge static review does not run these commands or modify anything.`, true)
  const lastSound = practiceResponses[practiceResponses.length - 1]
expect(lastSound.attempt.practice_task.static_check.status).toBe('looks_structurally_sound')
  expect(lastSound.attempt.practice_task.static_check.score).toBeUndefined()
  expect(lastSound.attempt.lesson_completed).toBeUndefined()
  expect(lastSound.attempt.verified_skills).toBeUndefined()
  await page.locator('#skill-detail').getByRole('button', { name: 'Continue to Mini Check', exact: true }).click()
  await miniCheckCorrect('git_local_repositories', 'Git')
  await page.reload(); await learning(); await skill('Git')
  await expect(page.locator('#skill-detail')).toContainText('1/11 topics complete')
  await shot('git-completed-and-persisted')
})

test('Arabic lesson rendering keeps RTL and never fabricates scores or verified skills', async () => {
  await page.reload(); await learning(); await skill('Git')
  await resume('Local repositories', 'Git')
  await page.getByRole('button', { name: 'العربية المصرية', exact: true }).click()
  await expect(page.locator('.lesson-content')).toHaveAttribute('dir', 'rtl')
  await page.getByRole('button', { name: 'English', exact: true }).click()
  await expect(page.locator('.lesson-content')).toHaveAttribute('dir', 'ltr')
  expect((await api(`/api/students/${studentId}`)).verified_skills || []).toEqual(verifiedBefore)
const pathResp = await api(`/api/students/${studentId}/learning/${gitId}/personalized-path`)
  for (const item of (pathResp.items || [])) {
    // Only git_local_repositories was generated; anything else must be
    // "generate first" rather than an invented score.
    const r = await fetch(`${BACKEND}/api/students/${studentId}/learning/${gitId}/lessons/${encodeURIComponent(item.competency)}/practice`, { headers: { Authorization: `Bearer ${token}` } })
    if (r.status !== 200) {
      expect(r.status).toBe(404)
      const body = await r.json().catch(() => ({}))
      expect(String(body.detail || '')).toContain('No lesson found')
      continue
    }
    const latest = (await r.json()).latest
    if (!latest) continue
    const sc = latest.practice_task && latest.practice_task.static_check
    if (sc) expect(sc.score).toBeUndefined()
    if (sc) expect(sc.verified).toBeUndefined()
    if (sc) expect(sc.completed).toBeUndefined()
    expect(latest.verified_skills).toBeUndefined()
    expect(latest.lesson_completed).toBeUndefined()
  }
  await shot('arabic-and-honest-api')
})
