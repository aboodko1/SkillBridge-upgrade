# SkillBridge contributor guidance

This is the current guidance for work in this repository. The old phase-by-phase
agent journal is archived at `docs/archive/AGENTS_HISTORY.md`; it is historical
evidence, not a list of current instructions or verified results.

- Keep the public README accurate, short, and focused on the product. Put
  implementation details in `docs/` and preserve historical plans in
  `docs/archive/`.
- Never commit real `.env` files, databases, uploads, credentials, transcripts,
  generated builds, or private user data. Use `.env.example` as the public guide.
- Do not imply that in-app assessment verification is a professional credential,
  that camera checks prove identity, or that the jobs feed covers every opening.
- Separate verified, self-reported, generated, demo, cached, and live data in both
  the UI and documentation.
- Before changing behavior, read the relevant code and tests. Run focused tests,
  frontend typecheck/build, and review desktop/mobile plus light/dark and RTL
  screens when a visual change is involved.
- `npm start -- --reset` removes the local SQLite database. Never use it on data
  that has not been backed up. The end-to-end verification script also creates
  or resets demo data; inspect its effects before running it.
- Review work on a branch and keep a concise handoff in `docs/team/` when a
  change is not complete.
