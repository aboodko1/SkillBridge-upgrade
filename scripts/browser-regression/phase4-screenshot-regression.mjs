// SkillBridge Phase 4 — Screenshot regression with approved baselines
// ---------------------------------------------------------------------------
// Extends the Phase 3 guardian matrix with pixel-level screenshot comparison.
//
// Baselines live in a clearly named test-artifact folder (NEVER source/public):
//   results/baselines/<role>_<theme>_<viewport>_<page>.png
// Current captures go to:   results/current/<role>_<theme>_<viewport>_<page>.png
// Diffs (red overlay) to:   results/diffs/<role>_<theme>_<viewport>_<page>.diff.png
// Report:                   results/phase4-report.md / .json
//
// Comparison uses a small pixel tolerance (default 3 RGB channels). Baselines
// are updated ONLY by the explicit human review command `--update-baselines`;
// never automatically.
//
// Run (compare):  node phase4-screenshot-regression.mjs --base http://127.0.0.1:8030
// Run (review):   node phase4-screenshot-regression.mjs --base http://127.0.0.1:8030 --update-baselines
// Filters: --only 1680|1440|820|390  --roles aisha|company|university
//          --themes professional-light|professional-dark|casual-pulse-light|casual-pulse-dark
//          --pages dashboard|skills|learning|scenarios|assessments|university
//          --tolerance <rgb diff 0-255>
// Env: SB_BASE_URL, SB_PASS, SB_CHROME
// Exit: 0 ok, 1 diffs/no-baseline findings, 2 harness error.
// ---------------------------------------------------------------------------
import puppeteer from 'puppeteer-core'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const argv = process.argv.slice(2)
const flag = (name, dflt = undefined) => {
  const i = argv.indexOf('--' + name)
  return i !== -1 && argv[i + 1] ? argv[i + 1] : (process.env['SB_' + name.toUpperCase()] || dflt)
}
const has = (name) => argv.includes('--' + name)

const BASE = flag('base', 'http://127.0.0.1:8030').replace(/\/$/, '')
const CHROME = process.env.SB_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const PASS = process.env.SB_PASS || 'demo1234'
const TOL = parseInt(flag('tolerance', '3'), 10)
const UPDATE = has('update-baselines')

const VIEWPORTS = [
  { name: '1680', width: 1680, height: 1050 },
  { name: '1440', width: 1440, height: 900 },
  { name: '820', width: 820, height: 1180 },
  { name: '390', width: 390, height: 844 },
].filter((v) => !has('only') || flag('only') === v.name)

const THEMES = [
  { name: 'professional-light', appearance: 'light', interface: 'professional' },
  { name: 'professional-dark', appearance: 'dark', interface: 'professional' },
  { name: 'casual-pulse-light', appearance: 'light', interface: 'casual-pulse' },
  { name: 'casual-pulse-dark', appearance: 'dark', interface: 'casual-pulse' },
].filter((t) => !has('themes') || flag('themes') === t.name)

const ROLES = [
  { id: 'aisha', email: 'aisha@student.edu', pages: ['dashboard', 'skills', 'learning', 'scenarios', 'assessments'] },
  { id: 'company', email: 'hr@northstar.com', pages: ['dashboard', 'skills'] },
  { id: 'university', email: 'admin@univ.edu', pages: ['dashboard', 'skills', 'university'] },
].filter((r) => !has('roles') || flag('roles') === r.id)
  .map((r) => ({ ...r, pages: r.pages.filter((p) => !has('pages') || p === flag('pages')) }))

const BASE_DIR = path.join(__dirname, 'results')
const BL = path.join(BASE_DIR, 'baselines')
const CUR = path.join(BASE_DIR, 'current')
const DIF = path.join(BASE_DIR, 'diffs')
for (const d of [BL, CUR, DIF]) fs.mkdirSync(d, { recursive: true })

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const manifest = []

async function login(browser, vw, email) {
  const ctx = await browser.createBrowserContext()
  const page = await ctx.newPage()
  page.setDefaultNavigationTimeout(45000)
  page.setDefaultTimeout(15000)
  await page.setViewport({ width: vw.width, height: vw.height })
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

async function capture(page) {
  return Buffer.from(await page.screenshot({ fullPage: false }))
}

// In-page pixel comparer: decodes both PNGs into canvas, counts differing
// pixels beyond tolerance, and renders a red-overlay diff PNG. No extra deps.
async function diffInPage(page, baseB64, curB64, tol) {
  return page.evaluate(async ([b, c, tolerance]) => {
    const load = (src) => new Promise((res, rej) => {
      const img = new Image()
      img.onload = () => res(img)
      img.onerror = rej
      img.src = 'data:image/png;base64,' + src
    })
    const [B, C] = await Promise.all([load(b), load(c)])
    const W = Math.max(B.width, C.width), H = Math.max(B.height, C.height)
    const canvas = document.createElement('canvas')
    canvas.width = W; canvas.height = H
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H)
    ctx.drawImage(B, 0, 0)
    const bd = ctx.getImageData(0, 0, W, H).data
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H)
    ctx.drawImage(C, 0, 0)
    const cd = ctx.getImageData(0, 0, W, H).data
    const diff = ctx.createImageData(W, H)
    let changed = 0, total = 0
    for (let i = 0; i < W * H; i++) {
      const o = i * 4
      const maxd = Math.max(
        Math.abs(bd[o] - cd[o]),
        Math.abs(bd[o + 1] - cd[o + 1]),
        Math.abs(bd[o + 2] - cd[o + 2]))
      if (maxd > tolerance) {
        changed++
        diff.data[o] = 255; diff.data[o + 1] = 0; diff.data[o + 2] = 0; diff.data[o + 3] = 120
      } else {
        diff.data[o] = (bd[o] + cd[o]) >> 1; diff.data[o + 1] = (bd[o + 1] + cd[o + 1]) >> 1
        diff.data[o + 2] = (bd[o + 2] + cd[o + 2]) >> 1; diff.data[o + 3] = 255
      }
      total++
    }
    const out = canvas.cloneNode()
    out.width = W; out.height = H
    out.getContext('2d').putImageData(diff, 0, 0)
    return { ratio: changed / total, changed, total, width: W, height: H, diffDataUrl: out.toDataURL('image/png') }
  }, [baseB64, curB64, tol])
}

const start = Date.now()
let browser
try { browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new' }) }
catch (e) { console.error('Chrome launch failed:', e.message); process.exit(2) }
console.log(`phase4 screenshot regression | base=${BASE} update=${UPDATE} tol=${TOL} dir=${BASE_DIR}`)

let diffs = 0, newShots = 0, updated = 0, clean = 0
for (const vw of VIEWPORTS) {
  for (const theme of THEMES) {
    for (const role of ROLES) {
      const { page, ctx } = await login(browser, vw, role.email)
      await page.evaluate(([app, face]) => {
        localStorage.setItem('sb_appearance', app)
        localStorage.setItem('sb_interface', face)
        localStorage.setItem('sb_theme', app === 'dark' ? 'dark' : 'light')
      }, [theme.appearance, theme.interface])
      await page.reload({ waitUntil: 'domcontentloaded' })
      await sleep(1600)

      for (const pageKey of role.pages) {
        if (pageKey !== 'dashboard') await clickNav(page, pageKey)
        await sleep(500)
        const png = await capture(page)
        const stem = `${role.id}_${theme.name}_${vw.name}_${pageKey}`
        fs.writeFileSync(path.join(CUR, stem + '.png'), png)
        const blPath = path.join(BL, stem + '.png')
        const row = { page: pageKey, theme: theme.name, viewport: vw.name, role: role.id, file: stem }

        if (!fs.existsSync(blPath)) {
          if (UPDATE) { fs.writeFileSync(blPath, png); row.status = 'baseline-created'; updated++ }
          else { row.status = 'no-baseline'; newShots++ }
          manifest.push(row)
          console.log(`  [new]      ${stem}`)
          continue
        }
        if (UPDATE) {
          fs.copyFileSync(path.join(CUR, stem + '.png'), blPath)
          row.status = 'baseline-updated'; updated++
          manifest.push(row)
          console.log(`  [updated]  ${stem}`)
          continue
        }
        const base64 = fs.readFileSync(blPath, 'base64')
        const cur64 = png.toString('base64')
        const d = await diffInPage(page, base64, cur64, TOL)
        const ratioPct = (d.ratio * 100).toFixed(3) + '%'
        if (d.ratio > 0.001) {
          fs.writeFileSync(path.join(DIF, stem + '.diff.png'), Buffer.from(d.diffDataUrl.split(',')[1], 'base64'))
          row.status = 'diff'; row.ratio = d.ratio; row.diffRatio = ratioPct
          diffs++
          console.log(`  [DIFF]     ${stem} changed=${d.changed}/${d.total} (${ratioPct})`)
        } else {
          row.status = 'clean'; row.ratio = d.ratio; row.diffRatio = '0%'
          clean++
          console.log(`  [clean]    ${stem}`)
        }
        manifest.push(row)
      }
      await ctx.close().catch(() => {})
    }
  }
}
await browser.close()

const report = {
  timestamp: new Date().toISOString(),
  base: BASE,
  tolerance: TOL,
  updateMode: UPDATE,
  durationSec: Math.round((Date.now() - start) / 1000),
  viewports: VIEWPORTS.map((v) => v.name),
  themes: THEMES.map((t) => t.name),
  roles: ROLES.map((r) => r.id),
  stats: { clean, diff: diffs, noBaseline: newShots, updated },
  rows: manifest,
  note: UPDATE ? 'Review run: baselines were updated (human-approved).' : 'Compare run: baselines never changed automatically.',
}
fs.writeFileSync(path.join(BASE_DIR, 'phase4-report.json'), JSON.stringify(report, null, 2))

let md = `# SkillBridge Phase 4 — Screenshot regression\n\n`
md += `- Base: ${BASE} · tolerance: ${TOL} · ${report.durationSec}s\n- Mode: ${UPDATE ? 'UPDATE (human-reviewed)' : 'COMPARE'}\n- Stats: ${clean} clean · ${diffs} diff · ${newShots} no-baseline · ${updated} updated\n\n`
md += '| Status | Role | Theme | Viewport | Page | Ratio |\n|---|---|---|---|---|---|\n'
for (const r of manifest) {
  md += `| ${r.status} | ${r.role} | ${r.theme} | ${r.viewport} | ${r.page} | ${r.ratio ?? '-'} |\n`
}
md += `\nDiffs (overlay): \`results/diffs/*.diff.png\`. Review a diff, then accept intentionally with:\n` +
  '`node phase4-screenshot-regression.mjs --base <url> --update-baselines`\n\n' +
  'Baselines are never updated automatically.\n'
fs.writeFileSync(path.join(BASE_DIR, 'phase4-report.md'), md)

console.log(`\nphase4 report: ${path.join(BASE_DIR, 'phase4-report.md')}`)
const findingCount = diffs + newShots
process.exit(UPDATE ? 0 : (findingCount > 0 ? 1 : 0))