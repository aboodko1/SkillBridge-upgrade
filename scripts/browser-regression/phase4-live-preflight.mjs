#!/usr/bin/env node
// Phase 4C.1 Live-voice preflight: exercises all 4 mentors x EN/AR against a
// running SkillBridge backend and asserts the spoken-reply + TTS audio chain.
//
// This is the automatable half of Phase 4C.1. It proves the server returns a
// real tutor reply and real MP3 bytes for every mentor/language combination,
// attributes the provider that served each half, and surfaces rate-limit /
// quota / provider / configuration errors. The audible half (speaker output,
// trace-stage order in a real browser) still requires a human.
//
// Usage:
//   node scripts/browser-regression/phase4-live-preflight.mjs \
//     --base http://127.0.0.1:8030 \
//     --email omar@student.edu --password demo1234
//
// Options (flags override env, env values shown):
//   --base      SKILLBRIDGE_PREFLIGHT_BASE   default http://localhost:8000
//   --email     SKILLBRIDGE_PREFLIGHT_EMAIL  default omar@student.edu
//   --password  SKILLBRIDGE_PREFLIGHT_PASSWORD
//   --timeout   SKILLBRIDGE_PREFLIGHT_TIMEOUT_MS  default 30000
//   --json      SKILLBRIDGE_PREFLIGHT_JSON    write JSON report to this path
//
// Never prints the session token, reply text, credentials, API keys or audio.

import { writeFileSync } from "node:fs";

const MENTORS = ["nova", "axel", "sage", "vex"];
const LANGUAGES = ["en", "ar"];
const PROMPT = { en: "Explain Docker simply", ar: "اشرح Docker ببساطة" };
const MIN_AUDIO_BYTES = 2000;

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i !== -1 && process.argv[i + 1]) return process.argv[i + 1];
  return process.env[`SKILLBRIDGE_PREFLIGHT_${name.toUpperCase()}`] ?? fallback;
}

const BASE = (arg("base", "http://localhost:8000") || "").replace(/\/+$/, "");
const EMAIL = arg("email", "omar@student.edu");
const PASSWORD = arg("password", "demo1234");
const TIMEOUT = Number(arg("timeout", "30000"));
const JSON_OUT = arg("json", "");

async function request(path, { method = "GET", token, body } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT);
  const started = Date.now();
  try {
    const res = await fetch(`${BASE}${path}`, {
      method,
      signal: controller.signal,
      headers: {
        ...(body ? { "content-type": "application/json" } : {}),
        ...(token ? { authorization: `Bearer ${token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    return { res, ms: Date.now() - started };
  } finally {
    clearTimeout(timer);
  }
}

// Error bodies may be JSON `detail` or an HTML error page. Extract a short,
// secret-free description without leaking anything but the server's message.
async function errorDetail(res) {
  let text = "";
  try {
    text = await res.text();
  } catch {
    return "";
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    try {
      const d = JSON.parse(text);
      const msg = typeof d.detail === "string" ? d.detail : JSON.stringify(d.detail ?? d);
      return String(msg).slice(0, 200);
    } catch {
      /* fall through */
    }
  }
  return text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 160);
}

// Public provider/TTS diagnostics (no auth, no secrets).
async function serverConfig() {
  const { res } = await request("/api/config/demo-mode");
  if (!res.ok) return null;
  try {
    const d = await res.json();
    return { genai_enabled: d.genai_enabled, provider: d.provider || null };
  } catch {
    return null;
  }
}

function providerOf(cfg) {
  const p = cfg?.provider;
  if (!p) return { tutor: "unknown", tts: "unknown" };
  const tutor =
    p.enabled && p.last_active_provider && p.last_success
      ? p.last_active_provider
      : "deterministic-fallback";
  const tts =
    p.tts?.tts_configured || (p.tts?.available && p.tts?.api_key_loaded)
      ? "elevenlabs"
      : "not-configured";
  return { tutor, tts };
}

function classify(cfg) {
  const p = cfg?.provider;
  if (!p) return [];
  const notes = [];
  if (!p.enabled) notes.push("genai-disabled (no provider keys configured)");
  if (p.last_attempted_provider && p.last_success === false) {
    notes.push(
      `provider-error attempted=${p.last_attempted_provider} class=${p.last_error_type} ` +
        `http=${p.last_http_status ?? "-"} timeout=${p.last_timeout}`,
    );
    if (p.last_http_status === 429) notes.push("rate-limit/429");
    if (p.last_http_status === 402 || p.last_http_status === 403) notes.push("quota-or-auth");
  }
  if (!p.tts?.tts_configured) notes.push("tts-not-configured");
  return notes;
}

async function login() {
  const { res, ms } = await request("/api/auth/login", {
    method: "POST",
    body: { email: EMAIL, password: PASSWORD },
  });
  if (!res.ok) {
    const detail = await errorDetail(res);
    console.error(`FAIL login: HTTP ${res.status} from ${BASE} ${detail ? `- ${detail}` : ""}`);
    process.exitCode = 1;
    return null;
  }
  const data = await res.json();
  if (!data.token) {
    console.error("FAIL login: response had no token");
    process.exitCode = 1;
    return null;
  }
  const me = await request("/api/auth/me", { token: data.token });
  if (!me.res.ok) {
    console.error(`FAIL login: token rejected by /api/auth/me (HTTP ${me.res.status})`);
    process.exitCode = 1;
    return null;
  }
  const bundle = await me.res.json();
  const studentId = bundle?.student?.id;
  if (!studentId) {
    console.error("FAIL login: account has no student profile");
    process.exitCode = 1;
    return null;
  }
  console.log(`auth ok (${BASE}, student_id=${studentId}, ${ms}ms)`);
  const voices = await request(`/api/students/${studentId}/interview/voice`, { token: data.token });
  if (voices.res.ok) {
    const v = await voices.res.json();
    console.log(
      `tts config: available=${v.available} api_key_loaded=${v.api_key_loaded} voices=${JSON.stringify(v.tutor_voices_loaded)}`,
    );
  }
  return { token: data.token, studentId };
}

async function runCombo({ token, studentId }, mentor, language) {
  const row = { mentor, language, tutor_ok: false, tts_ok: false, errors: [] };
  const { res: tutorRes, ms: tutorMs } = await request(`/api/students/${studentId}/tutor`, {
    method: "POST",
    token,
    body: {
      message: PROMPT[language],
      tutor_id: mentor,
      language,
      mode: "chat",
      spoken: true,
    },
  });
  row.tutor_status = tutorRes.status;
  row.tutor_ms = tutorMs;
  let reply = "";
  if (tutorRes.ok) {
    const data = await tutorRes.json();
    reply = (data.reply || "").trim();
    row.reply_len = reply.length;
    row.reply_language = data.language || "";
    row.tutor_ok = reply.length > 0;
    if (!row.tutor_ok) row.note = "empty reply";
  } else {
    row.note = `tutor HTTP ${tutorRes.status}`;
    const detail = await errorDetail(tutorRes);
    if (detail) row.errors.push(`tutor: ${detail}`);
  }

  // Attribute which GenAI provider (or deterministic fallback) served this turn.
  const cfgAfter = await serverConfig();
  row.provider_tutor = providerOf(cfgAfter).tutor;
  row.provider_tts = providerOf(cfgAfter).tts;
  row.provider_attempt = cfgAfter?.provider?.last_attempted_provider ?? null;
  row.provider_success = cfgAfter?.provider?.last_success ?? null;
  row.provider_error_type = cfgAfter?.provider?.last_error_type ?? null;
  row.provider_http = cfgAfter?.provider?.last_http_status ?? null;

  if (row.tutor_ok) {
    const { res: ttsRes, ms: ttsMs } = await request(`/api/students/${studentId}/tutor/tts`, {
      method: "POST",
      token,
      body: { tutor: mentor, text: reply },
    });
    const buf = Buffer.from(await ttsRes.arrayBuffer());
    row.tts_status = ttsRes.status;
    row.tts_ms = ttsMs;
    row.audio_bytes = buf.length;
    row.content_type = ttsRes.headers.get("content-type") || "";
    row.tts_ok = ttsRes.ok && buf.length >= MIN_AUDIO_BYTES;
    if (!row.tts_ok) {
      const detail = await errorDetail(ttsRes);
      if (detail) row.errors.push(`tts: ${detail}`);
      row.note = row.note || `tts HTTP ${ttsRes.status}, ${buf.length} bytes`;
    }
  }
  row.classifications = classify(cfgAfter);
  return row;
}

function report(rows, cfgAtStart) {
  console.log("");
  const pad = (s, n) => String(s).padEnd(n);
  console.log(
    `${pad("mentor", 7)} ${pad("lang", 5)} ${pad("tutor", 6)} ${pad("ms", 6)} ${pad("reply", 6)} ` +
      `${pad("tts", 5)} ${pad("ms", 6)} ${pad("KB", 7)} ${pad("tutor-provider", 22)} result`,
  );
  for (const r of rows) {
    const ok = r.tutor_ok && r.tts_ok;
    console.log(
      `${pad(r.mentor, 7)} ${pad(r.language, 5)} ${pad(r.tutor_status ?? "-", 6)} ` +
        `${pad(r.tutor_ms ?? "-", 6)} ${pad(r.reply_len ?? "-", 6)} ${pad(r.tts_status ?? "-", 5)} ` +
        `${pad(r.tts_ms ?? "-", 6)} ${pad(r.audio_bytes ? (r.audio_bytes / 1024).toFixed(1) : "-", 7)} ` +
        `${pad(r.provider_tutor ?? "-", 22)} ${ok ? "PASS" : `FAIL (${r.note || "incomplete"})`}`,
    );
    for (const e of r.errors || []) console.log(`        error: ${e}`);
  }
  const passed = rows.filter((r) => r.tutor_ok && r.tts_ok).length;
  console.log(`\n${passed}/${rows.length} mentor/language combinations passed`);
  if (cfgAtStart) {
    console.log(
      `server genai_enabled=${cfgAtStart.genai_enabled} ` +
        `tutor_provider=${providerOf(cfgAtStart).tutor} tts_provider=${providerOf(cfgAtStart).tts}`,
    );
  }
  if (passed !== rows.length) process.exitCode = 1;
}

async function main() {
  const cfgAtStart = await serverConfig();
  const session = await login();
  if (!session) return;
  const rows = [];
  for (const mentor of MENTORS) {
    for (const language of LANGUAGES) {
      const row = await runCombo(session, mentor, language);
      rows.push(row);
      console.log(
        `${mentor}/${language} tutor=${row.tutor_ok ? "ok" : "FAIL"} tts=${row.tts_ok ? "ok" : "FAIL"} ` +
          `provider=${row.provider_tutor} audio=${row.audio_bytes ? (row.audio_bytes / 1024).toFixed(1) + "KB" : "-"}`,
      );
    }
  }
  report(rows, cfgAtStart);
  if (JSON_OUT) {
    writeFileSync(
      JSON_OUT,
      JSON.stringify(
        { base: BASE, generated_at: new Date().toISOString(), server: cfgAtStart, rows },
        null,
        2,
      ),
    );
    console.log(`report written to ${JSON_OUT}`);
  }
}

main().catch((err) => {
  console.error(`FAIL unexpected: ${err?.message || String(err)}`);
  process.exitCode = 1;
});
