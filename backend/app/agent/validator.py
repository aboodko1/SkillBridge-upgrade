"""Adversarial validator for SkillBridge career roadmaps.

Wraps the existing roadmap generator (never rewrites it): the validator checks a
draft roadmap against authoritative ground truth (NIST NICE v2.1, MITRE ATT&CK)
and the student's actual CV, and returns a structured verification report.

The LLM provider is the same one the rest of the backend uses
(``genai.complete``). If the provider is unavailable or returns malformed JSON,
the validator degrades to a deterministic rule check (never a crash) and labels
the result accordingly — the caller must not present a degraded result as a
live LLM validation.
"""
import json
import os
from pathlib import Path

from .. import genai

GROUND_TRUTH_DIR = Path(__file__).resolve().parent / "ground_truth"

# The six checks the validator prompt must perform, in the fixed order.
CHECK_NAMES = [
    "FRAMEWORK_COVERAGE",
    "PREREQUISITE_ORDER",
    "CV_REDUNDANCY",
    "RECENCY",
    "HALLUCINATION",
    "LEVEL_APPROPRIATENESS",
]


def _load_json(name):
    with open(GROUND_TRUTH_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


def load_role(role_id):
    """Load the ground-truth files for a role id.

    Returns (role_meta, ground_truth_payload). Raises KeyError when the role id
    is unknown or a referenced file is missing.
    """
    roles = _load_json("roles.json")
    role = next((r for r in roles["roles"] if r["id"] == role_id), None)
    if not role:
        raise KeyError(role_id)
    files = role.get("ground_truth_files") or []
    payload = {}
    for name in files:
        if name not in ("nice_soc_analyst.json", "mitre_soc_subset.json", "roles.json"):
            raise KeyError(f"unknown ground truth file: {name}")
        payload[name] = _load_json(name)
    return role, payload


def roadmap_to_markdown(draft_roadmap):
    """Render a draft roadmap (markdown string or structured dict) as markdown.

    The existing generator produces a structured ``CareerRoadmap`` dict
    (phases -> goals/deliverables/skills). The validator prompt works on
    markdown, so a dict is rendered deterministically here. A markdown string
    passes through unchanged.
    """
    if isinstance(draft_roadmap, str):
        return draft_roadmap
    if not isinstance(draft_roadmap, dict):
        return str(draft_roadmap or "")
    lines = []
    summary = draft_roadmap.get("summary")
    if summary:
        lines.append(str(summary).strip())
        lines.append("")
    phases = draft_roadmap.get("phases") or []
    for phase in phases:
        if not isinstance(phase, dict):
            continue
        phase_no = phase.get("phase")
        title = phase.get("title") or f"Phase {phase_no}"
        lines.append(f"## Phase {phase_no}: {title}")
        goal = phase.get("goal")
        if goal:
            lines.append(f"Goal: {goal}")
        skills = phase.get("skills") or []
        names = [str(s.get("name")) for s in skills if isinstance(s, dict) and s.get("name")]
        if names:
            lines.append("Develops: " + ", ".join(names))
        deliverables = phase.get("deliverables") or []
        for d in deliverables:
            if isinstance(d, dict) and d.get("task"):
                lines.append(f"- {d.get('task')}")
            elif isinstance(d, str):
                lines.append(f"- {d}")
        lines.append("")
    return "\n".join(lines).strip()


def _validator_system(role_name):
    return (
        "You are an adversarial validator for cybersecurity career roadmaps.\n"
        "Your job is to find flaws, not to approve. You have no incentive to be lenient.\n"
    )


def _validator_user(draft_roadmap, student_cv, role_name, ground_truth_json):
    return (
        f"You are given:\n"
        f"1. A draft roadmap for a student targeting the role: {role_name}\n"
        f"2. The student's CV.\n"
        f"3. A ground-truth competency graph for {role_name}.\n\n"
        f"For each of these checks, output a JSON object with\n"
        f"`check_name`, `passed` (true/false), `evidence`, `suggested_fix`:\n\n"
        f"1. FRAMEWORK_COVERAGE: Does the roadmap cover every competency\n"
        f"   in the graph?\n"
        f"2. PREREQUISITE_ORDER: Is every skill taught after its prerequisites?\n"
        f"3. CV_REDUNDANCY: Does the roadmap teach a skill the CV already\n"
        f"   demonstrates?\n"
        f"4. RECENCY: Does the roadmap include AI/automation skills for\n"
        f"   the 2026 role?\n"
        f"5. HALLUCINATION: Are all tools, certifications, and frameworks\n"
        f"   real and current?\n"
        f"6. LEVEL_APPROPRIATENESS: Is the difficulty appropriate for the\n"
        f"   student's CV?\n\n"
        f"Output only the JSON array. Do not add commentary.\n\n"
        f"DRAFT ROADMAP:\n{draft_roadmap}\n\n"
        f"STUDENT CV:\n{student_cv}\n\n"
        f"GROUND TRUTH:\n{ground_truth_json}\n"
    )


def _parse_violations(raw):
    """Parse the LLM response as a JSON array of violation objects."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty validator response")
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = json.loads(text)
    if not isinstance(data, list):
        # Some models wrap the array in an object; unwrap a single array key.
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    data = value
                    break
    if not isinstance(data, list):
        raise ValueError("validator response is not a JSON array")
    out = []
    for item in data:
        if not isinstance(item, dict):
            continue
        out.append({
            "check_name": str(item.get("check_name") or ""),
            "passed": bool(item.get("passed") is True),
            "evidence": str(item.get("evidence") or ""),
            "suggested_fix": str(item.get("suggested_fix") or ""),
        })
    if not out:
        raise ValueError("validator response array is empty")
    return out


def _deterministic_violations(draft_md, student_cv, ground_truth):
    """No-LLM fallback: a conservative rule check when the provider is down.

    Returns (violations, coverage_fraction) computed without a model so the
    endpoint always returns something structured instead of crashing. Callers
    must label this as a fallback.
    """
    nice = ground_truth.get("nice_soc_analyst.json") or {}
    competencies = nice.get("competencies") or []
    violations = []
    body = draft_md.lower()
    covered = 0
    for c in competencies:
        name = c.get("name") or ""
        # Very coarse keyword overlap — enough to flag an obviously sparse draft.
        keywords = [w for w in name.lower().replace(",", " ").split() if len(w) > 4]
        hit = any(kw in body for kw in keywords) if keywords else name.lower() in body
        if hit:
            covered += 1
        else:
            violations.append({
                "check_name": "FRAMEWORK_COVERAGE",
                "passed": False,
                "evidence": f"Roadmap missing competency '{name}'",
                "suggested_fix": f"Add a module or phase covering '{name}'",
            })
    if not competencies:
        violations.append({
            "check_name": "FRAMEWORK_COVERAGE",
            "passed": False,
            "evidence": "No ground-truth competencies available",
            "suggested_fix": "Review the role ground-truth data",
        })
    return violations, (covered / len(competencies)) if competencies else 0.0


def _coverage_and_personalization(violations):
    """Derive scores from the violation list (0.0-1.0 each)."""
    total = len(violations) or 1
    passed = sum(1 for v in violations if v.get("passed"))
    coverage = (passed / total) if total else 1.0
    # Personalization is a soft proxy: no CV_REDUNDANCY or LEVEL_APPROPRIATENESS
    # findings implies the roadmap accounts for the CV.
    personalization = 1.0
    for v in violations:
        if not v.get("passed") and v.get("check_name") in ("CV_REDUNDANCY", "LEVEL_APPROPRIATENESS"):
            personalization -= 0.5
    personalization = max(0.0, min(1.0, personalization))
    return coverage, personalization


async def validate_roadmap(draft_roadmap, student_cv, role_id):
    """Validate a draft roadmap against ground truth + the student CV.

    Returns a dict:
      {
        "coverage_score": float,        # 0.0 to 1.0
        "personalization_score": float, # 0.0 to 1.0
        "violations": [ ... ],
        "sources": [...],
        "source": "live" | "fallback",
      }
    On unknown role / missing ground truth, returns {"error": "role_not_found"}
    without raising. On persistent LLM failure (malformed output or a raising
    provider), falls through to the deterministic fallback and returns a
    structured result labelled "fallback".
    """
    try:
        role, ground_truth = load_role(role_id)
    except (KeyError, OSError, ValueError) as exc:
        return {"error": "role_not_found", "detail": str(exc)}
    role_name = role.get("name") or role_id

    draft_md = roadmap_to_markdown(draft_roadmap)
    ground_truth_json = json.dumps(ground_truth, ensure_ascii=True, sort_keys=True)
    sources = []
    for name in role.get("ground_truth_files") or []:
        if name == "nice_soc_analyst.json":
            sources.append("NIST NICE v2.1 work role 511")
        elif name == "mitre_soc_subset.json":
            sources.append("MITRE ATT&CK Enterprise")
    sources = sources or ["curated ground truth"]

    if not genai.genai_enabled():
        violations, covered = _deterministic_violations(draft_md, student_cv, ground_truth)
        coverage, personalization = _coverage_and_personalization(violations)
        if not violations:
            coverage = 1.0
        return {
            "coverage_score": round(coverage, 3),
            "personalization_score": round(personalization, 3),
            "violations": violations,
            "sources": sources,
            "source": "fallback",
            "deterministic": covered,
        }

    system = _validator_system(role_name)
    user = _validator_user(draft_md, student_cv, role_name, ground_truth_json)

    llm_failed_reason = None
    for attempt in range(2):
        try:
            raw = genai.complete(system, user, max_tokens=1400, timeout=90)
            violations = _parse_violations(raw)
            coverage, personalization = _coverage_and_personalization(violations)
            return {
                "coverage_score": round(coverage, 3),
                "personalization_score": round(personalization, 3),
                "violations": violations,
                "sources": sources,
                "source": "live",
            }
        except Exception as exc:
            llm_failed_reason = str(exc)
            import logging
            logging.getLogger("skillbridge").warning(
                "validator LLM attempt %d failed: %s", attempt + 1, exc
            )
            if attempt == 0:
                continue
            break

    # Live LLM failed — use deterministic fallback so endpoint
    # always returns a structured result.
    violations, covered = _deterministic_violations(draft_md, student_cv, ground_truth)
    coverage, personalization = _coverage_and_personalization(violations)
    if not violations:
        coverage = 1.0
    return {
        "coverage_score": round(coverage, 3),
        "personalization_score": round(personalization, 3),
        "violations": violations,
        "sources": sources,
        "source": "fallback",
        "deterministic": covered,
        "warning": f"LLM unavailable ({llm_failed_reason}); deterministic validation used.",
    }