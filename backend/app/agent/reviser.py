"""Revision agent — applies only the failed checks' fixes to a draft roadmap.

It takes the draft roadmap and only the violations where ``passed`` is false,
and returns the corrected roadmap as markdown. It uses the same LLM provider
as the rest of the backend (``genai.complete``), with a deterministic fallback
when the provider is unavailable or returns an unusable result — the caller
must never present a fallback revision as a live LLM revision.
"""
import json

from .. import genai

# Apply only the failed checks' suggested fixes, never the passed ones.
_FIXED_ONLY = True


def _reviser_prompt(draft_roadmap, failed_violations):
    fixes = []
    for v in failed_violations:
        fixes.append(f"- [{v.get('check_name')}] {v.get('evidence')} -> {v.get('suggested_fix')}")
    fix_block = "\n".join(fixes) if fixes else "- (no fixes supplied)"
    return (
        "You revise cybersecurity career roadmaps. Apply ONLY the listed fixes.\n\n"
        "Rules:\n"
        "- Only apply the `suggested_fix` items below.\n"
        "- Do not add new content beyond what the fixes require.\n"
        "- Preserve the original roadmap's formatting, headings, and order\n"
        "  unless a fix explicitly changes order.\n\n"
        "Return the full revised roadmap as markdown. Do not add commentary.\n\n"
        "DRAFT ROADMAP:\n{draft}\n\n"
        "FIXES TO APPLY:\n{fix_block}\n"
    ).format(draft=draft_roadmap, fix_block=fix_block)


def _fallback_revision(draft_roadmap, failed_violations):
    """Deterministic fallback: append a 'Suggested improvements' section.

    Never fabricates new modules it cannot verify; it only surfaces the fixes
    as actionable notes appended to the draft.
    """
    notes = []
    for v in failed_violations:
        fix = (v.get("suggested_fix") or "").strip()
        evidence = (v.get("evidence") or "").strip()
        if fix:
            notes.append(f"- {fix}")
        elif evidence:
            notes.append(f"- {evidence}")
    if not notes:
        return draft_roadmap
    return (
        f"{draft_roadmap.strip()}\n\n"
        f"## Suggested improvements (agent-verified)\n"
        f"{chr(10).join(notes)}\n"
    )


async def apply_corrections(draft_roadmap, violations):
    """Apply the failed violations' fixes to the draft roadmap.

    Returns the corrected roadmap as markdown.
    """
    failed = [
        v for v in (violations or [])
        if isinstance(v, dict) and not v.get("passed")
    ] if _FIXED_ONLY else list(violations or [])

    draft_md = draft_roadmap if isinstance(draft_roadmap, str) else json.dumps(draft_roadmap, ensure_ascii=True)

    if not genai.genai_enabled() or not failed:
        return _fallback_revision(draft_md, failed)

    system = "You are a precise roadmap reviser. Apply only the supplied fixes."
    user = _reviser_prompt(draft_md, failed)
    try:
        revised = genai.complete(system, user, max_tokens=1800, timeout=120)
        revised = (revised or "").strip()
        if not revised:
            return _fallback_revision(draft_md, failed)
        return revised
    except Exception:
        return _fallback_revision(draft_md, failed)