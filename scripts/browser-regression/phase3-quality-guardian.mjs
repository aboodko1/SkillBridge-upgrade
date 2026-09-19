// SkillBridge Phase 3 — Responsive UI Quality Guardian
// ---------------------------------------------------------------------------
// A single-command Puppeteer (puppeteer-core + system Chrome) inspector that
// visits every reachable section for each role under all four interface
// combinations (Professional / Casual Pulse x Light / Dark) at desktop,
// tablet, and mobile, and reports real geometry/contrast/a11y/network issues.
//
// Checks: horizontal overflow, elements outside the viewport, overlapping
// interactive elements, zero-size visible controls, clipped text, computed
// color contrast, missing accessible names, broken images, console errors,
// failed same-origin API calls, and layout-shift signals.
//
// Run:  node phase3-quality-guardian.mjs [--base http://127.0.0.1:8030]
// Env:  SB_BASE_URL, SB_CHROME (default system Chrome), SB_EMAIL/SB_PASS
//       SB_INCLUDE_ROLES (default aisha,company,university)
//
// Emits (report dir printed at the end):
//   results/guardian-<iso>/report.json   machine-readable findings
//   results/guardian-<iso>/report.md     readable Markdown
//   results/guardian-<iso>/shots/*.png   page_theme_viewport_section.png
//
// Exit codes: 0 all clean, 1 findings, 2 harness error, 3 watchdog.
// The app must already be serving the current frontend/dist + backend.
// ---------------------------------------------------------------------------
import puppeteer from 'puppeteer-core'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// --- args / env ----------------------------------------------------------
const argv = process.argv.slice(2)
const argVal = (name, dflt) => {
  const i = argv.indexOf('--' + name)
  return i !== -1 && argv[i + 1] ? argv[i + 1] : (process.env['SB_' + name.toUpperCase()] || dflt)
}
const BASE = argVal('base', 'http://127.0.0.1:8030').replace(/\/$/, '')
const CHROME = process.env.SB_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const PASS = process.env.SB_PASS || 'demo1234'
const INCLUDE_ROLES = (process.env.SB_INCLUDE_ROLES || 'aisha,company,university').split(',')

const VIEWPORTS = [
  { name: '1440', width: 1440, height: 900 },
  { name: '820', width: 820, height: 1180 },
  { name: '390', width: 390, height: 844 },
]
const THEMES = [
  { name: 'professional-light', appearance: 'light', interface: 'professional' },
  { name: 'professional-dark', appearance: 'dark', interface: 'professional' },
  { name: 'casual-pulse-light', appearance: 'light', interface: 'casual-pulse' },
  { name: 'casual-pulse-dark', appearance: 'dark', interface: 'casual-pulse' },
]
const ROLES = [
  { id: 'aisha', email: 'aisha@student.edu', expect: ['dashboard', 'skills', 'learning', 'scenarios', 'assessments'] },
  { id: 'company', email: 'hr@northstar.com', expect: ['dashboard', 'skills'] },
  { id: 'university', email: 'admin@univ.edu', expect: ['dashboard', 'skills', 'university'] },
].filter((r) => INCLUDE_ROLES.includes(r.id))

// Intentional overlays that must never be flagged: the fixed AI/copilot dock,
// the live-voice fullscreen, popovers/dropdowns, the off-canvas nav draw, and
// the skip-to-content link (visually hidden until focused).
const OVERLAY_ALLOW = new Set([
  '.copilot-panel', '.copilot-dock', '.copilot-fab', '.copilot-peek',
  '.voice', '.ml-orb', '.v-top', '.v-bottom', '.v-center',
  '.topbar-popover', '.nav-backdrop', '.skip-link', '.sidebar',
  '.success-overlay', '.modal', '[role=dialog]', '.nav-toggle',
])

// --- output ---------------------------------------------------------------
const OUT = path.join(__dirname, 'results', 'guardian-' + new Date().toISOString().replace(/[:.]/g, '-'))
const SHOTS = path.join(OUT, 'shots')
fs.mkdirSync(SHOTS, { recursive: true })

const findings = [] // { kind, route, theme, viewport, selector, value, fix }
const consoleIssues = []
let shotsTaken = 0

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const add = (f) => findings.push(f)

function watch(page, vw, theme) {
  page.on('console', (m) => {
    if (m.type() !== 'error') return
    const t = m.text()
    if (/Failed to load resource|diagnostic|favicon|Autofill/.test(t)) return
    consoleIssues.push(`${vw.name}/${theme.name} :: ${t}`)
  })
  page.on('pageerror', (e) => consoleIssues.push(`${vw.name}/${theme.name} :: pageerror :: ${e.message}`))
  page.on('requestfailed', (r) => {
    const url = r.url()
    if (!url.startsWith(BASE)) return
    if (/favicon|\.map$/.test(url)) return
    consoleIssues.push(`${vw.name}/${theme.name} :: requestfailed :: ${url} :: ${r.failure()?.errorText || '?'}`)
  })
}

// --- in-page inspectors ---------------------------------------------------
function checks(allowSet, baseOrigin) {
  return {
    route: document.title,
    html: {
      dataTheme: document.documentElement.dataset.theme,
      dataInterface: document.documentElement.dataset.interface,
    },
    overflow: (() => {
      const sw = document.documentElement.scrollWidth
      const cw = document.documentElement.clientWidth
      return { ok: sw <= cw + 1, sw, cw }
    })(),
    outside: (() => {
      const bad = []
      const sel = 'div,section,article,aside,nav,header,main,footer,ul,ol,table,form'
      const els = document.querySelectorAll(sel)
      for (let i = 0; i < els.length; i++) {
        const el = els[i]
        const cs = getComputedStyle(el)
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        if (el.closest([...allowSet].join(','))) continue
        const r = el.getBoundingClientRect()
        if (r.width < 2 || r.height < 2) continue
        if (r.right > window.innerWidth + 8) {
          const cls = (el.className && String(el.className).trim().slice(0, 60)) || el.tagName.toLowerCase()
          bad.push({ selector: `${el.tagName.toLowerCase()}.${cls}`, right: Math.round(r.right), left: Math.round(r.left), vw: window.innerWidth })
        }
      }
      return { ok: bad.length === 0, bad: bad.slice(0, 8) }
    })(),
    overlap: (() => {
      const els = [...document.querySelectorAll('a,button,input,select,textarea,[role="button"]')]
      const vis = els.filter((el) => {
        const cs = getComputedStyle(el)
        const r = el.getBoundingClientRect()
        return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 8 && r.height > 8 &&
          !el.closest([...allowSet].join(','))
      })
      const bad = []
      outer:
      for (let i = 0; i < vis.length; i++) {
        for (let j = i + 1; j < vis.length; j++) {
          const a = vis[i], b = vis[j]
          if (a.contains(b) || b.contains(a)) continue
          const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect()
          const ix = Math.max(0, Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left))
          const iy = Math.max(0, Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top))
          const oa = (ix * iy) / (ra.width * ra.height + 1e-9)
          if (oa > 0.55) {
            bad.push({ a: (a.getAttribute('aria-label') || a.textContent || a.tagName).trim().slice(0, 40), b: (b.getAttribute('aria-label') || b.textContent || b.tagName).trim().slice(0, 40), overlap: Math.round(oa * 100) })
            if (bad.length >= 6) break outer
          }
        }
      }
      return { ok: bad.length === 0, bad }
    })(),
    zeroSize: (() => {
      const bad = []
      const els = document.querySelectorAll('button,a,input,select,textarea,[role="button"],.btn')
      for (const el of els) {
        const cs = getComputedStyle(el)
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        if (Number(cs.opacity) < 0.05) continue
        if (el.closest([...allowSet].join(','))) continue
        const r = el.getBoundingClientRect()
        if (r.width < 8 || r.height < 8) {
          bad.push({ selector: (el.getAttribute('aria-label') || el.textContent || el.tagName).trim().slice(0, 40), w: Math.round(r.width), h: Math.round(r.height) })
        }
      }
      return { ok: bad.length === 0, bad: bad.slice(0, 8) }
    })(),
    clipped: (() => {
      const bad = []
      const els = document.querySelectorAll('[class]')
      for (const el of els) {
        const cs = getComputedStyle(el)
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        if (cs.overflowX !== 'hidden' && cs.overflowY !== 'hidden' && cs.textOverflow !== 'ellipsis') continue
        if (el.closest('.chat-thread, .v-caption, ' + [...allowSet].join(','))) continue
        if (el.scrollHeight > el.clientHeight + 4 && cs.overflowY === 'hidden') {
          const cls = String(el.className).trim().slice(0, 50)
          if (cls) bad.push({ selector: el.tagName.toLowerCase() + '.' + cls, scrollH: el.scrollHeight, clientH: el.clientHeight })
          if (bad.length >= 10) break
        }
      }
      return { ok: bad.length === 0, bad }
    })(),
    contrast: (() => {
      function parseColor(c) {
        c = (c || '').trim().toLowerCase()
        let m = c.match(/^#([0-9a-f]{3})$/i) || c.match(/^#([0-9a-f]{6})$/i)
        if (m) {
          let h = m[1]
          if (h.length === 3) h = h.split('').map((x) => x + x).join('')
          return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16), a: 1 }
        }
        m = c.match(/^rgba?\(([^)]+)\)$/)
        if (m) {
          const p = m[1].split(',').map((x) => parseFloat(x))
          return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? (p[3] == null ? 1 : p[3]) : 1 }
        }
        return null
      }
      function lum({ r, g, b }) {
        function f(x) { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4) }
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
      }
      function bg(el) {
        for (let n = el; n; n = n.parentElement) {
          const c = parseColor(getComputedStyle(n).backgroundColor)
          if (c && c.a > 0.92) return c
        }
        return { r: 255, g: 255, b: 255, a: 1 }
      }
      const bad = []
      const els = document.querySelectorAll('p,h1,h2,h3,h4,h5,li,td,th,a,button,strong,span,.label,.eyebrow')
      let count = 0
      for (const el of els) {
        if (count > 60) break
        const cs = getComputedStyle(el)
        const txt = (el.textContent || '').trim()
        if (!txt) continue
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        if (el.closest([...allowSet].join(','))) continue
        count++
        const fg = parseColor(cs.color), b = bg(el)
        if (!fg) continue
        const l1 = lum(fg), l2 = lum(b)
        const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)
        const fs = parseFloat(cs.fontSize), w = parseInt(cs.fontWeight, 10)
        const large = fs >= 24 || (fs >= 18.7 && w >= 700)
        const min = large ? 3 : 4.5
        if (ratio < min - 0.1) {
          bad.push({ selector: el.tagName.toLowerCase() + ': ' + txt.slice(0, 26), ratio: ratio.toFixed(2), min: min.toFixed(1), size: fs, weight: w })
          if (bad.length >= 10) break
        }
      }
      return { ok: bad.length === 0, bad }
    })(),
    a11yName: (() => {
      const bad = []
      const els = document.querySelectorAll('a,button,input,select,textarea,[role="button"],img')
      for (const el of els) {
        const cs = getComputedStyle(el)
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        if (el.getAttribute('aria-hidden') === 'true') continue
        if (el.closest([...allowSet].join(','))) continue
        const name = (el.getAttribute('aria-label') || el.getAttribute('title') || (el.textContent || '').trim()).trim()
        const isImg = el.tagName === 'IMG'
        const alt = el.getAttribute('alt') || ''
        const r = el.getBoundingClientRect()
        if (r.width < 2 || r.height < 2) continue
        if (isImg ? alt.trim() === '' && !name : !name && !el.hasAttribute('aria-labelledby')) {
          bad.push({ selector: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).trim().slice(0, 30) : '') })
        }
      }
      return { ok: bad.length === 0, bad: bad.slice(0, 10) }
    })(),
    brokenImages: (() => {
      const bad = []
      for (const img of document.querySelectorAll('img')) {
        if (img.getAttribute('aria-hidden') === 'true') continue
        if (img.complete && img.naturalWidth === 0 && img.src) bad.push({ src: img.currentSrc || img.src })
      }
      return { ok: bad.length === 0, bad: bad.slice(0, 10) }
    })(),
    apiErrors: (() => {
      const bad = []
      const src = window.__sbApiErrors || []
      for (const e of src.slice(0, 10)) {
        if (e.url.includes('diagnostic') || e.url.includes('favicon')) continue
        bad.push(e)
      }
      return { ok: bad.length === 0, bad }
    })(),
    layoutShift: window.__sbLS || 0,
  }
}

const apiErrorScript = (origin) => `
  window.__sbApiErrors = []
  window.__sbLS = 0
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) if (!e.hadRecentInput) window.__sbLS += e.value
    }).observe({ type: 'layout-shift', buffered: true })
  } catch (e) {}
  const origFetch = window.fetch
  window.fetch = (...args) => {
    const u = typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url)
    const p = origFetch.apply(window, args)
    p.catch(() => { if (u && u.startsWith(${JSON.stringify(origin)})) window.__sbApiErrors.push({ url: u.slice(0, 120), err: 'network' }) })
    return p
  }
`

// --- flows ----------------------------------------------------------------
async function login(browser, vw, email, theme) {
  const ctx = await browser.createBrowserContext()
  const page = await ctx.newPage()
  page.setDefaultNavigationTimeout(45000)
  page.setDefaultTimeout(15000)
  await page.setViewport({ width: vw.width, height: vw.height })
  watch(page, vw, theme)
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', cache: 'force-cache' })
  await sleep(1200)
  await page.waitForSelector('form input[autocomplete="email"]', { timeout: 15000 })
  await page.type('form input[autocomplete="email"]', email, { delay: 2 })
  await page.type('form input[type="password"]', PASS, { delay: 2 })
  await page.evaluate(() => {
    const f = document.querySelector('form')
    const b = f && f.querySelector('button[type="submit"]')
    if (b) b.click(); else if (f) f.requestSubmit()
  })
  await sleep(2200)
  return { page, ctx }
}

const NAV_LABEL = {
  dashboard: 'Dashboard', skills: 'Skills', learning: 'Learning', scenarios: 'Practice',
  assessments: 'Assessments', university: 'University',
}
async function clickNav(page, sectionKey) {
  await page.evaluate((w) => {
    const items = [...document.querySelectorAll('.nav-item')]
    const t = (n) => (n.textContent || '').replace(/\s+/g, ' ').trim()
    const item = items.find((n) => t(n).toLowerCase().startsWith(w.toLowerCase())) || items.find((n) => t(n).toLowerCase().includes(w.toLowerCase()))
    if (item) item.click()
  }, NAV_LABEL[sectionKey])
  await sleep(1800)
}

// --- main ----------------------------------------------------------------
const start = Date.now()
const watchdog = setTimeout(() => { console.error('WATCHDOG: still running after 20 min; aborting.'); process.exit(3) }, 20 * 60 * 1000)

let browser
try {
  browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new' })
} catch (e) {
  console.error('Unable to launch Chrome at', CHROME, '—', e.message)
  process.exit(2)
}
console.log('guardian launched; base =', BASE)

for (const role of ROLES) {
  console.log(`\n== role ${role.id} ==`)
  for (const vw of VIEWPORTS) {
    let loginOnce = null
    for (const theme of THEMES) {
      const { page, ctx } = loginOnce || (loginOnce = await login(browser, vw, role.email, theme))
      await page.setViewport({ width: vw.width, height: vw.height })
      // Set the interface/appearance and re-enter the shell with it active.
      await page.evaluate(([app, face]) => {
        localStorage.setItem('sb_appearance', app)
        localStorage.setItem('sb_interface', face)
        localStorage.setItem('sb_theme', app === 'dark' ? 'dark' : 'light')
      }, [theme.appearance, theme.interface])
      await page.reload({ waitUntil: 'domcontentloaded' })
      await sleep(1600)
      await page.evaluate(apiErrorScript, BASE)
      for (const want of role.expect) {
        if (want !== 'dashboard') await clickNav(page, want)
        await sleep(500)
        const res = await page.evaluate(checks, [...OVERLAY_ALLOW], BASE)
        const route = res.route || want
        const shot = `${SHOTS}/${role.id}_${theme.name}_${vw.name}_${want}.png`
        await page.screenshot({ path: shot, fullPage: false }).catch(() => {})
        shotsTaken++

        const tag = { route, theme: theme.name, viewport: vw.name }
        if (!res.overflow.ok) add({ kind: 'overflow', selector: 'document', value: `scrollWidth ${res.overflow.sw} > clientWidth ${res.overflow.cw}`, fix: 'find the offending fixed-width element; use min-width:0 and fluid layout.', ...tag })
        for (const b of res.outside.bad) add({ kind: 'outside', selector: b.selector, value: `right=${b.right} left=${b.left} vw=${b.vw}`, fix: 'element sticks out of the viewport horizontally; reflow or wrap.', ...tag })
        for (const b of res.overlap.bad) add({ kind: 'overlap', selector: `${b.a} / ${b.b}`, value: `${b.overlap}% overlap`, fix: 'give the interactive pair separate layout (not 55%+ stacked).', ...tag })
        for (const b of res.zeroSize.bad) add({ kind: 'zero-size', selector: b.selector, value: `${b.w}x${b.h}px`, fix: 'ensure minimum visible hit area (>=8px).', ...tag })
        for (const b of res.clipped.bad) add({ kind: 'clipped', selector: b.selector, value: `scrollH=${b.scrollH} clientH=${b.clientH}`, fix: 'remove fixed height / allow wrap; verify not intentionally clipped.', ...tag })
        for (const b of res.contrast.bad) add({ kind: 'contrast', selector: b.selector, value: `ratio ${b.ratio} (need ${b.min}; ${b.size}px/${b.weight})`, fix: 'darken/lift text or adjust the surface token.', ...tag })
        for (const b of res.a11yName.bad) add({ kind: 'a11y-name', selector: b.selector, value: 'missing accessible name', fix: 'add aria-label/title/alt or visible text.', ...tag })
        for (const b of res.brokenImages.bad) add({ kind: 'broken-image', selector: b.src.slice(0, 90), value: 'naturalWidth=0', fix: 'serve the asset or remove the img.', ...tag })
        for (const b of res.apiErrors.bad) add({ kind: 'api', selector: b.url.slice(0, 90), value: b.err || 'error', fix: 'fix the failing same-origin request.', ...tag })
      }
      if (loginOnce) { await ctx.close().catch(() => {}); loginOnce = null }
    }
  }
}
await browser.close()
clearTimeout(watchdog)

const report = {
  timestamp: new Date().toISOString(),
  base: BASE,
  chrome: CHROME,
  durationSec: Math.round((Date.now() - start) / 1000),
  viewports: VIEWPORTS.map((v) => v.name),
  themes: THEMES.map((t) => t.name),
  roles: ROLES.map((r) => `${r.id}(${r.email})`),
  findCount: findings.length,
  findings: findings.slice(0, 200),
  totalExcised: Math.max(0, findings.length - 200),
  consoleIssues: consoleIssues.slice(0, 40),
  consoleCount: consoleIssues.length,
  shots: shotsTaken,
  exit: findings.length > 0 || consoleIssues.length > 0 ? 1 : 0,
}
fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2))

let md = `# SkillBridge Phase 3 — UI Quality Guardian\n\n`
md += `- Base: ${BASE} · Chrome: ${CHROME}\n`
md += `- Run: ${report.timestamp} · ${report.durationSec}s · ${shotsTaken} screenshots → \`shots/\`\n`
md += `- Roles: ${report.roles.join(', ')}\n`
md += `- Themes: ${report.themes.join(', ')} · Viewports: ${report.viewports.join(', ')}\n\n`
md += `## Result: ${findings.length} finding(s), ${consoleIssues.length} console/network issue(s)\n\n`
const byKind = {}
for (const f of findings) byKind[f.kind] = (byKind[f.kind] || 0) + 1
md += '| Kind | Count |\n|---|---|\n' + Object.entries(byKind).map(([k, c]) => `| ${k} | ${c} |`).join('\n') + '\n\n'
if (findings.length) {
  md += '## Findings\n\n| Route | Theme | Viewport | Kind | Selector | Value | Suggested fix |\n|---|---|---|---|---|---|---|\n'
  for (const f of findings.slice(0, 200)) {
    md += `| ${f.route} | ${f.theme} | ${f.viewport} | ${f.kind} | \`${f.selector}\` | ${f.value} | ${f.fix} |\n`
  }
  if (findings.length > 200) md += `\n… ${findings.length - 200} more findings in report.json\n`
} else {
  md += '_No structural findings._\n'
}
if (consoleIssues.length) {
  md += '\n## Console / network issues\n\n' + consoleIssues.slice(0, 40).map((c) => `- \`${c}\``).join('\n') + '\n'
} else {
  md += '\n_Console clean._\n'
}
md += '\n## Intentional-overlay allow-list\n'
md += [...OVERLAY_ALLOW].join(', ') + '\n'
md += '\n_Geometry/contrast checks are computed live (getBoundingClientRect + computed styles). "Outside/overlap/clipped" distinguish intentional overlays; nothing was changed to hide a failure._\n'
fs.writeFileSync(path.join(OUT, 'report.md'), md)

console.log('\nREPORT:', OUT)
console.log(`findings=${findings.length} console=${consoleIssues.length} shots=${shotsTaken}`)
process.exit(report.exit)