# Phase 7 — Resilience, accessibility, RTL, and responsive safety

## Delivered

- Job-feed failures now offer a visible **Retry jobs** action. It keeps the current
  market and filters, clears stale feedback, and makes a fresh request without a
  full page reload.
- Job-feed error messages use an assertive accessible announcement, while the
  mentor thinking state has a screen-reader-only status label.
- API error details are reduced to short, student-safe messages before display;
  credential-like text and internal diagnostics are not passed into the UI.
- Speech-to-text provider failures return safe, plain client messages while the
  raw provider context remains operator-only server logging.
- English commands/code retain left-to-right ordering inside Arabic content.
- Shared dynamic layout surfaces may shrink on small screens rather than causing
  a card to force horizontal overflow.
- `frontend/scripts/check-phase7-resilience.mjs` prevents removal of these
  critical contracts during future visual work.

## Verification to run

```sh
cd frontend
npm run typecheck
npm run build
node scripts/check-phase7-resilience.mjs
```

For backend scope, run the focused STT test without printing `.env` values:

```sh
cd backend
../.venv/bin/python -m pytest tests/test_tutor_stt_fallback.py -q
```

## Manual visual checklist

At 1440, 1024, 768, and 390px, in both themes and Arabic where available:

1. Trigger a job provider outage or use a disconnected network, then choose
   **Retry live jobs**. Confirm the current market remains selected.
2. Tab through the job retry action, filters, mentor launcher, and chat controls;
   each has a visible focus indicator and logical order.
3. Read a lesson containing a terminal command in Arabic: command order remains
   left-to-right and the lesson itself remains right-to-left.
4. Confirm no horizontal page scroll and no mentor overlay hides the primary
   page action on a phone-width viewport.

## Boundary

This phase deliberately does not redesign pages or begin Phase 8 production
polish. It makes the existing experience safer to recover from errors and more
reliable for keyboard, RTL, and narrow-screen users.
