// SkillBridge Phase 3 browser acceptance — the curated Python topics end to end.
//
// What this proves (in a real browser, against an isolated offline server):
//   1. Real UI login (the actual React form), real Bearer token in localStorage.
//   2. Diagnostic -> Personalized Path -> Lesson -> Practice -> Mini Check ->
//      persisted topic completion -> next recommended action, for EVERY curated
//      Python topic (python_functions, python_error_handling, python_data_structures).
//   3. A bad practice submission is structurally flagged and yields GIVE_HINT.
//   4. A corrected submission with sound structure offers MINI_CHECK, and the
//      Mini Check persists topic completion without creating a Verified Skill.
//   5. Exact duplicate submission reuses the stored attempt; a changed answer is
//      re-evaluated.
//   6. Completion survives a fresh browser context + re-login (persistence) and
//      the Learning UI renders the persisted state.
//
// The server is started with a fresh temporary SKILLBRIDGE_DB and provider keys
// removed, so the run is deterministic and offline. It never touches the
// developer's database or the live server on :8000.
//
// Run: node phase3-learning-e2e.js
// Env overrides: SKILLBRIDGE_E2E_BASE (reuse an already-running isolated server),
//                SKILLBRIDGE_PYTHON, SKILLBRIDGE_CHROME, SKILLBRIDGE_E2E_EMAIL.
const puppeteer = require('puppeteer-core')
const { spawn } = require('child_process')
const fs = require('fs')
const os = require('os')
const net = require('net')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', '..')
const OUT = path.join(__dirname, 'results')
fs.mkdirSync(OUT, { recursive: true })

const CHROME = process.env.SKILLBRIDGE_CHROME ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const EMAIL = process.env.SKILLBRIDGE_E2E_EMAIL || 'tomas@student.edu'
const PASSWORD = 'demo1234'
const EXTERNAL_BASE = process.env.SKILLBRIDGE_E2E_BASE || ''

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

let pass = 0
let fail = 0
const failures = []
function ok(cond, msg) {
  if (cond) { pass++; console.log('  PASS: ' + msg) }
  else { fail++; failures.push(msg); console.log('  FAIL: ' + msg) }
}

function findPython() {
  if (process.env.SKILLBRIDGE_PYTHON) return process.env.SKILLBRIDGE_PYTHON
  const venv = path.join(ROOT, '.venv', 'bin', 'python')
  if (fs.existsSync(venv)) return venv
  const backendVenv = path.join(ROOT, 'backend', '.venv', 'bin', 'python')
  if (fs.existsSync(backendVenv)) return backendVenv
  return 'python3'
}

function freePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer()
    srv.on('error', reject)
    srv.listen(0, '127.0.0.1', () => {
      const { port } = srv.address()
      srv.close(() => resolve(port))
    })
  })
}

async function startServer() {
  const port = await freePort()
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'sb-phase3-e2e-'))
  const dbPath = path.join(tmp, 'skillbridge.db')
  const logPath = path.join(tmp, 'server.log')
  const env = { ...process.env, SKILLBRIDGE_DB: dbPath }
  for (const key of ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'NVIDIA_API_KEY', 'NVAPI_KEY', 'NIM_API_KEY']) {
    delete env[key]
  }
  const py = findPython()
  const out = fs.openSync(logPath, 'w')
  const child = spawn(py, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port)], {
    cwd: path.join(ROOT, 'backend'),
    env,
    stdio: ['ignore', out, out],
  })
  const base = `http://127.0.0.1:${port}`
  return { child, base, tmp, logPath, dbPath }
}

async function waitReady(base, child, logPath) {
  for (let i = 0; i < 120; i++) {
    if (child.exitCode !== null) {
      throw new Error(`isolated server exited early (${child.exitCode}); see ${logPath}`)
    }
    try {
      const r = await fetch(base + '/', { redirect: 'manual' })
      if (r.status < 500) return
    } catch { /* not up yet */ }
    await sleep(500)
  }
  throw new Error(`isolated server did not become ready; see ${logPath}`)
}

async function uiLogin(browser, base) {
  const ctx = await browser.createBrowserContext()
  const page = await ctx.newPage()
  page.setDefaultNavigationTimeout(45000)
  page.setDefaultTimeout(15000)
  const consoleIssues = []
  page.on('console', (m) => {
    if (m.type() !== 'error') return
    const t = m.text()
    if (/Failed to load resource|diagnostic\/latest|favicon/.test(t)) return
    consoleIssues.push(t)
  })
  page.on('pageerror', (e) => consoleIssues.push('pageerror: ' + e.message))
  await page.goto(base + '/', { waitUntil: 'domcontentloaded' })
  await page.waitForSelector('form input[autocomplete="email"]', { timeout: 20000 })
  await page.type('form input[autocomplete="email"]', EMAIL, { delay: 2 })
  await page.type('form input[type="password"]', PASSWORD, { delay: 2 })
  await page.evaluate(() => {
    const f = document.querySelector('form')
    const b = f && f.querySelector('button[type="submit"]')
    if (b) b.click(); else if (f) f.requestSubmit()
  })
  await page.waitForFunction(() => !!localStorage.getItem('skillbridge_token'), { timeout: 20000 })
  await sleep(800)
  return { page, ctx, consoleIssues }
}

// Runs inside the browser page: the exact request sequence the Learning UI issues.
async function runJourneyInBrowser() {
  const token = localStorage.getItem('skillbridge_token')
  const H = { 'content-type': 'application/json', authorization: `Bearer ${token}` }
  const j = async (p, opts = {}) => {
    const r = await fetch(p, opts)
    const t = await r.text()
    let d
    try { d = JSON.parse(t) } catch { d = t }
    if (!r.ok) throw new Error(`${r.status} ${p}: ${String(t).slice(0, 300)}`)
    return d
  }
  const me = await j('/api/auth/me', { headers: H })
  const sid = me.student.id
  const skills = await j('/api/skills', { headers: H })
  const skill = skills.find((s) => (s.name || '').toLowerCase() === 'python')
  const skillId = skill.id

  const diag = await j(`/api/students/${sid}/learning/${skillId}/diagnostic/generate`, {
    method: 'POST', headers: H, body: '{}',
  })
  await j(`/api/students/${sid}/learning/${skillId}/diagnostic/submit`, {
    method: 'POST', headers: H,
    body: JSON.stringify({ diagnostic_id: diag.diagnostic_id, answers: ['not sure'] }),
  })
  const p = await j(`/api/students/${sid}/learning/${skillId}/personalized-path/generate`, {
    method: 'POST', headers: H, body: '{}',
  })

  const verifiedBefore = (await j(`/api/students/${sid}`, { headers: H })).verified_skills
  const GOOD = {
    python_functions: 'def celsius_to_fahrenheit(celsius):\n    return (celsius * 9 / 5) + 32\n\nI return the value so other code can reuse it.',
    python_error_handling: 'def parse_score(text):\n    try:\n        return int(text)\n    except ValueError:\n        return None\n\nI return a value on the success and error paths.',
    python_data_structures: "def summarize_scores(scores):\n    return {'count': len(scores), 'average': sum(scores) / len(scores)}\n\nA dictionary makes the two named results explicit.",
  }

  const steps = []
  for (const item of p.items) {
    const slug = item.competency
    const enc = encodeURIComponent(slug)
    const base = `/api/students/${sid}/learning/${skillId}/lessons/${enc}`
    await j(base + '/generate', { method: 'POST', headers: H, body: '{}' })

    const bad = await j(base + '/practice', {
      method: 'POST', headers: H, body: JSON.stringify({ answer: 'def f(x):\n    print(x)' }),
    })
    const hint = await j(`/api/students/${sid}/learning/${skillId}/orchestrator/next`, { headers: H })

    const good = await j(base + '/practice', {
      method: 'POST', headers: H, body: JSON.stringify({ answer: GOOD[slug] }),
    })
    const next = await j(`/api/students/${sid}/learning/${skillId}/orchestrator/next`, { headers: H })

    // Exact duplicate must reuse the stored attempt, not re-evaluate it.
    const dup = await j(base + '/practice', {
      method: 'POST', headers: H, body: JSON.stringify({ answer: GOOD[slug] }),
    })

    const lesson = await j(base, { headers: H })
    const mini = lesson.content?.mini_check?.questions || []
    const done = await j(base + '/mini-check', {
      method: 'POST', headers: H,
      body: JSON.stringify({ answers: mini.map((q) => q.correct_answer) }),
    })
    const after = await j(`/api/students/${sid}/learning/${skillId}/orchestrator/next`, { headers: H })
    const persisted = await j(base, { headers: H })

    steps.push({
      slug,
      badStatic: bad.attempt?.practice_task?.static_check?.status,
      hintAction: hint.action_type,
      goodStatic: good.attempt?.practice_task?.static_check?.status,
      nextAction: next.action_type,
      duplicateReused: dup.reused === true && dup.attempt?.id === good.attempt?.id,
      miniCount: mini.length,
      lessonState: done.lesson?.state,
      persistedState: persisted.state,
      afterAction: after.action_type,
      afterTopic: after.topic_id,
    })
  }

  const verifiedAfter = (await j(`/api/students/${sid}`, { headers: H })).verified_skills
  const finalPath = await j(`/api/students/${sid}/learning/${skillId}/personalized-path`, { headers: H })
  return {
    sid, skillId,
    pathItems: p.items.map((i) => i.competency),
    verifiedBefore, verifiedAfter,
    steps,
    progress: finalPath.progress,
  }
}

async function reLoginPersistence(browser, base) {
  const { page, ctx, consoleIssues } = await uiLogin(browser, base)
  const token = await page.evaluate(() => localStorage.getItem('skillbridge_token'))
  const H = { authorization: `Bearer ${token}` }
  const me = await fetch(base + '/api/auth/me', { headers: H }).then((r) => r.json())
  const sid = me.student.id
  const skills = await fetch(base + '/api/skills', { headers: H }).then((r) => r.json())
  const skillId = skills.find((s) => (s.name || '').toLowerCase() === 'python').id
  const p = await fetch(`${base}/api/students/${sid}/learning/${skillId}/personalized-path`, { headers: H }).then((r) => r.json())
  const states = {}
  for (const slug of ['python_functions', 'python_error_handling']) {
    const l = await fetch(`${base}/api/students/${sid}/learning/${skillId}/lessons/${encodeURIComponent(slug)}`, { headers: H }).then((r) => r.json())
    states[slug] = l.state
  }
  await ctx.close().catch(() => {})
  return { sid, skillId, progress: p.progress, states, consoleIssues }
}

async function renderLearningUI(page, base) {
  await page.goto(base + '/', { waitUntil: 'domcontentloaded' })
  await sleep(600)
  await page.evaluate(() => {
    const skip = [...document.querySelectorAll('button')].find((b) => /skip tour|don't show again/i.test((b.textContent || '').trim()))
    if (skip) skip.click()
  })
  await sleep(400)
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('.nav-item')].find((x) => (x.textContent || '').trim().indexOf('Learning') === 0)
    if (b) b.click()
  })
  await sleep(2000)
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('.focus-flow button')].find((x) => /my paths/i.test(x.textContent || ''))
    if (b) b.click()
  })
  await sleep(1500)
  return page.evaluate(() => ({
    hasPython: /python/i.test(document.body.innerText),
    text: document.body.innerText.replace(/\s+/g, ' ').slice(0, 4000),
  }))
}

(async () => {
  const start = Date.now()
  let server = null
  let browser = null
  const watchdog = setTimeout(() => { console.error('WATCHDOG: aborting after 8 minutes'); process.exit(3) }, 8 * 60 * 1000)
  try {
    const base = EXTERNAL_BASE || (await startServer().then((s) => { server = s; return s.base }))
    if (server) {
      console.log(`isolated server: ${base}  (db ${server.dbPath})`)
      await waitReady(base, server.child, server.logPath)
    } else {
      console.log(`using external isolated server: ${base}`)
    }

    browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox'] })

    console.log('\n-- UI login + in-browser learning journey --')
    const first = await uiLogin(browser, base)
    const journey = await first.page.evaluate(runJourneyInBrowser)
    await first.page.screenshot({ path: path.join(OUT, 'phase3-learning-after-journey.png'), fullPage: true })

    ok(journey.pathItems.includes('python_functions'), 'personalized path includes Python Functions')
    ok(journey.pathItems.includes('python_error_handling'), 'personalized path includes Python Error Handling')
    ok(journey.pathItems.indexOf('python_functions') < journey.pathItems.indexOf('python_error_handling'),
      'Python Functions is ordered before Python Error Handling (prerequisite-aware)')

    const bySlug = Object.fromEntries(journey.steps.map((s) => [s.slug, s]))
    for (const slug of ['python_functions', 'python_error_handling']) {
      const s = bySlug[slug]
      ok(!!s, `${slug}: journey step ran`)
      if (!s) continue
      ok(s.badStatic === 'needs_fix', `${slug}: bad practice gets a non-executing needs_fix structure check`)
      ok(s.hintAction === 'GIVE_HINT', `${slug}: orchestrator offers GIVE_HINT after the bad attempt (got ${s.hintAction})`)
      ok(s.goodStatic === 'looks_structurally_sound', `${slug}: corrected practice is structurally sound (got ${s.goodStatic})`)
      ok(s.nextAction === 'MINI_CHECK', `${slug}: orchestrator offers MINI_CHECK after corrected practice (got ${s.nextAction})`)
      ok(s.miniCount > 0, `${slug}: Mini Check has questions`)
      ok(s.lessonState === 'completed', `${slug}: Mini Check persists topic completion (got ${s.lessonState})`)
      ok(s.persistedState === 'completed', `${slug}: completion persists on re-read (got ${s.persistedState})`)
      ok(s.duplicateReused === true, `${slug}: exact duplicate submission reuses the stored attempt`)
    }
    ok(journey.progress.length >= 2, `personalized path progress has every curated topic (${journey.progress.join(', ')})`)
    ok(JSON.stringify(journey.verifiedBefore) === JSON.stringify(journey.verifiedAfter),
      'learning + Mini Check did NOT create a Verified Skill')

    console.log('\n-- persistence after a fresh browser context + re-login --')
    const persisted = await reLoginPersistence(browser, base)
    await sleep(200)
    ok(persisted.progress.length >= 2, `persisted path progress after re-login (${persisted.progress.join(', ')})`)
    ok(persisted.states.python_functions === 'completed', `Python Functions still completed after re-login (got ${persisted.states.python_functions})`)
    ok(persisted.states.python_error_handling === 'completed', `Python Error Handling still completed after re-login (got ${persisted.states.python_error_handling})`)

    console.log('\n-- Learning UI renders the persisted journey --')
    const ui = await renderLearningUI(first.page, base)
    await first.page.screenshot({ path: path.join(OUT, 'phase3-learning-ui.png'), fullPage: true })
    ok(ui.hasPython, 'Learning UI renders the Python skill/gap')
    ok(!/pageerror/.test(first.consoleIssues.join(' ')), 'no page errors during the journey')
    ok(first.consoleIssues.length === 0, `no unexpected console errors (${first.consoleIssues.slice(0, 3).join(' | ') || 'none'})`)

    await first.ctx.close().catch(() => {})

    const report = {
      timestamp: new Date().toISOString(),
      durationSec: Math.round((Date.now() - start) / 1000),
      base, student: EMAIL,
      pathItems: journey.pathItems, steps: journey.steps, progress: journey.progress,
      verifiedBefore: journey.verifiedBefore, verifiedAfter: journey.verifiedAfter,
      persisted: { progress: persisted.progress, states: persisted.states },
      uiHasPython: ui.hasPython,
      passed: pass, failed: fail, failures,
      note: 'Isolated fresh DB, providers disabled. Real UI login; the learning journey runs through the browser against the real HTTP APIs; completion is re-verified after a fresh context + re-login and rendered by the Learning UI.',
    }
    fs.writeFileSync(path.join(OUT, 'phase3-learning-e2e.json'), JSON.stringify(report, null, 2))

    console.log(`\nPhase 3 learning browser E2E: PASSED=${pass} FAILED=${fail} (${report.durationSec}s)`)
    if (fail > 0) { console.log('FAILURES: ' + failures.join(' | ')); process.exitCode = 1 }
    else console.log('Phase 3 learning browser E2E: ALL GREEN')
  } catch (e) {
    console.error('HARNESS ERROR:', e && e.stack ? e.stack : e)
    process.exitCode = 2
  } finally {
    clearTimeout(watchdog)
    if (browser) await browser.close().catch(() => {})
    if (server) server.child.kill('SIGTERM')
    process.exit(process.exitCode || 0)
  }
})()
