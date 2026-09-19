# Security policy

SkillBridge is an educational prototype. Do not deploy it as a production identity, hiring, or
assessment system without a dedicated security and privacy review.

## Reporting a problem

Report security concerns privately to the repository owner. Do not open a public issue containing
credentials, tokens, private CVs, student records, database files, or exploit details.

## Credential rules

- Keep real values in an untracked `.env` file copied from `.env.example`.
- Never commit `.env`, databases, uploaded CVs, provider keys, OAuth secrets, or generated session
  artifacts.
- Rotate a credential immediately if it was shared in a repository, issue, chat, screenshot, or
  archive.
- CI and demos must work with deterministic fallbacks when external provider credentials are absent.

## Prototype boundaries

The repository includes demo authentication, AI-generated learning material, heuristic integrity
signals, and external job-provider integrations. These are not guarantees of identity, competence,
academic misconduct, employability, or job availability.
