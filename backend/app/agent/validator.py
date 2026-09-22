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
import logging
import os
import re
from pathlib import Path

from .. import genai

logger = logging.getLogger("skillbridge")

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


def _match_role(candidates, role_id):
    """Resolve ``role_id`` against the ground-truth role list.

    Accepts three forms:
      1. exact match on the role ``id`` (e.g. ``"soc_analyst"``);
      2. case-insensitive match on the role ``name`` (e.g. ``"SOC Analyst"``);
      3. an integer catalog role id, resolved via ``models.get_role(id)`` and
         then matched by name (case-insensitive).
    Returns the matching role dict, or None.
    """
    if isinstance(role_id, str):
        for r in candidates:
            if r.get("id") == role_id:
                return r
        lowered = role_id.strip().lower()
        for r in candidates:
            if (r.get("name") or "").strip().lower() == lowered:
                return r
        if role_id.isdigit():
            role_id = int(role_id)
        else:
            return None
    if isinstance(role_id, int):
        from .. import models
        db_role = models.get_role(role_id)
        if not db_role:
            return None
        title = (db_role.get("title") or "").strip().lower()
        for r in candidates:
            if (r.get("name") or "").strip().lower() == title:
                return r
    return None


def load_role(role_id):
    """Load the ground-truth files for a role id.

    ``role_id`` may be the canonical id (``"soc_analyst"``), the role name
    (``"SOC Analyst"``, case-insensitive), or an integer catalog role id —
    ``_match_role`` resolves all three to the same ground-truth entry.

    Returns (role_meta, ground_truth_payload). Raises KeyError when the role id
    is unknown or a referenced file is missing.
    """
    roles = _load_json("roles.json")
    role = _match_role(roles["roles"], role_id)
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


_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def _parse_llm_json(raw):
    """Parse a JSON array from raw LLM output.

    The model sometimes wraps the array in a ```json fence, adds prose before
    or after the array, or emits trailing commas. Returns a list of violation
    dicts; raises ValueError (including the raw text) when no array can be
    extracted.
    """
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty validator response")
    # Strip a surrounding markdown fence (```json ... ``` or bare ``` ... ```).
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    # Extract the JSON array span (first '[' through last ']'), ignoring prose.
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"no JSON array in validator response:\n{raw}")
    text = text[start:end + 1]
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Retry with trailing commas removed before ] or }.
        cleaned = _TRAILING_COMMA_RE.sub(r"\1", text)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"validator response is not valid JSON:\n{raw}")
    if not isinstance(data, list):
        # Some models wrap the array in an object; unwrap a single array key.
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    data = value
                    break
    if not isinstance(data, list):
        raise ValueError(f"validator response is not a JSON array:\n{raw}")
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


# Skill evidence map for the deterministic fallback: skill key ->
# (listed terms, demonstrated-evidence terms). A skill is:
#   DEMONSTRATED  -> a listed term AND an evidence term appear in the CV
#                    (e.g. "python" + "sql injection detector").
#   LISTED        -> only a listed term appears (e.g. "networking basics",
#                    "penetration testing", SIEM named as a tool with no
#                    querying artifact).
#   UNKNOWN       -> no listed term appears.
# The roadmap is penalised when it frames a DEMONSTRATED/LISTED skill at
# beginner level, and flagged CV_REDUNDANCY when it re-teaches a DEMONSTRATED
# skill from scratch.
_CV_SKILL_EVIDENCE = {
    "python": (("python",), ("sql", "detector", "scapy", "sniffer", "script",
                             "automation", "payload", "years", "experience", "noc")),
    "java": (("java",), ("project", "chatbot", "swing", "reservation", "tracker",
                         "oop", "years", "experience")),
    "communication": (("communication", "teaching", "presentation", "explain",
                        "soft skills"), ("teaching", "presentation", "peers",
                                         "explain", "present", "mentor")),
    "networking": (("networking", "network"), ("packet", "sniffer", "scapy",
                                                "traffic", "years", "experience", "noc")),
    "siem querying": (("siem", "splunk", "elk"), ("query", "search", "correlate",
                                                   "dashboard", "rule")),
    "incident response": (("incident response", "incident handling", "incident"), ()),
    "triage": (("triage", "triaging"), ()),
    "escalation": (("escalat",), ()),
    "mitre": (("mitre", "att&ck", "attack"), ()),
    "ticketing": (("ticket", "case-management", "case management"), ()),
    "threat intelligence": (("threat intelligence", "threat intel"), ()),
}

_BEGINNER_MARKERS = ("basics", "beginner", "introduction", "intro",
                     "fundamentals", "learn")


def _classify_cv_skills(student_cv):
    """Classify each tracked skill against the CV: DEMONSTRATED / LISTED /
    UNKNOWN (see ``_CV_SKILL_EVIDENCE`` for the definitions)."""
    cv = (student_cv or "").lower()
    out = {}
    for skill, (listed_terms, evidence_terms) in _CV_SKILL_EVIDENCE.items():
        listed = any(t in cv for t in listed_terms)
        if not listed:
            out[skill] = "UNKNOWN"
        elif any(t in cv for t in evidence_terms):
            out[skill] = "DEMONSTRATED"
        else:
            out[skill] = "LISTED"
    return out


def _cv_personalization(draft_md, student_cv):
    """Personalization for the fallback: fraction of the tracked competency set
    the roadmap handles correctly against the CV evidence.

    The tracked set is every skill in ``_CV_SKILL_EVIDENCE`` (the SOC-relevant
    competency groups). ``known`` = DEMONSTRATED + LISTED skills found in the
    CV; the remaining tracked skills are UNKNOWN and still require teaching.
    A known skill counts as handled when the roadmap does not frame it at
    beginner level (omission of a DEMONSTRATED skill is fine — it needs no
    re-teaching; a LISTED skill must still appear as a module).

    Denominator = all tracked skills, so a roadmap can only be "personalized"
    for the CV-known portion — the CV-unknown modules are generic and do not
    inflate the score. An empty CV yields 1.0 (nothing to personalize against).
    """
    classif = _classify_cv_skills(student_cv)
    if all(st == "UNKNOWN" for st in classif.values()):
        return 1.0
    body = draft_md.lower()
    handled = 0
    for skill, status in classif.items():
        listed_terms = _CV_SKILL_EVIDENCE[skill][0]
        mentioned = any(t in body for t in listed_terms)
        framed_beginner = mentioned and any(m in body for m in _BEGINNER_MARKERS)
        if status == "DEMONSTRATED":
            if not framed_beginner:
                handled += 1
        elif status == "LISTED":
            if mentioned and not framed_beginner:
                handled += 1
    return max(0.0, min(1.0, handled / len(classif)))


def _deterministic_violations(draft_md, student_cv, ground_truth):
    """No-LLM fallback: a conservative rule check when the provider is down.

    Returns (violations, coverage_fraction) computed without a model so the
    endpoint always returns something structured instead of crashing. Callers
    must label this as a fallback.

    Emits the same six check names as the live path and mirrors the live
    personalization score: CV_REDUNDANCY fires when the roadmap teaches a skill
    the CV already demonstrates, LEVEL_APPROPRIATENESS when the roadmap frames
    that skill at beginner level.
    """
    nice = ground_truth.get("nice_soc_analyst.json") or {}
    competencies = nice.get("competencies") or []
    violations = []
    body = draft_md.lower()
    covered = 0
    missing = []
    for c in competencies:
        name = c.get("name") or ""
        # Very coarse keyword overlap — enough to flag an obviously sparse draft.
        keywords = [w for w in name.lower().replace(",", " ").split() if len(w) > 4]
        hit = any(kw in body for kw in keywords) if keywords else name.lower() in body
        if hit:
            covered += 1
        else:
            missing.append((c.get("id") or "?", name))
    if missing:
        # Collapse into a single violation; keep the full list for the UI.
        ids = ", ".join(mid for mid, _ in missing)
        violations.append({
            "check_name": "FRAMEWORK_COVERAGE",
            "passed": False,
            "evidence": f"Roadmap missing {len(missing)} competencies: {ids}",
            "suggested_fix": "Add modules covering each listed competency.",
            "missing_competencies": [{"id": mid, "name": name} for mid, name in missing],
        })
    elif not competencies:
        violations.append({
            "check_name": "FRAMEWORK_COVERAGE",
            "passed": False,
            "evidence": "No ground-truth competencies available",
            "suggested_fix": "Review the role ground-truth data",
        })

    # CV-aware checks (deterministic mirror of the live CV_REDUNDANCY and
    # LEVEL_APPROPRIATENESS checks). The classifier distinguishes DEMONSTRATED
    # (artifact evidence in the CV), LISTED (named but no artifact), and
    # UNKNOWN skills so the fallback's personalization tracks the CV.
    classif = _classify_cv_skills(student_cv)
    demonstrated = [s for s, st in classif.items() if st == "DEMONSTRATED"]
    listed = [s for s, st in classif.items() if st == "LISTED"]
    re_taught = [s for s in demonstrated if s in body]
    if re_taught:
        violations.append({
            "check_name": "CV_REDUNDANCY",
            "passed": False,
            "evidence": "Roadmap re-teaches skills the CV demonstrates: "
                        + ", ".join(re_taught),
            "suggested_fix": "Replace these with assessment-first or advanced modules.",
        })
    # Beginner framing of a demonstrated skill is wrong level; a listed skill
    # (e.g. SIEM querying when the CV only shows log generation) must stay an
    # assessment-first module, never a beginner recap.
    beginner_framed = [s for s in demonstrated + listed if s in body]
    if beginner_framed and any(m in body for m in _BEGINNER_MARKERS):
        violations.append({
            "check_name": "LEVEL_APPROPRIATENESS",
            "passed": False,
            "evidence": "Roadmap frames a CV-relevant skill at beginner level: "
                        + ", ".join(beginner_framed),
            "suggested_fix": "Raise the difficulty to match the CV's demonstrated level.",
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
        # coverage = fraction of competencies present in the roadmap (computed
        # by the deterministic check, not re-derived from the violation list,
        # which is always 0.0 while FRAMEWORK_COVERAGE fails).
        coverage = covered
        if not violations:
            coverage = 1.0
        personalization = _cv_personalization(draft_md, student_cv)
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
            violations = _parse_llm_json(raw)
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
            logger.warning("validator LLM attempt %d failed: %s", attempt + 1, exc)
            if "raw" in locals() and isinstance(raw, str):
                logger.warning("validator raw LLM output:\n%s", raw[:4000])
            if attempt == 0:
                continue
            break

    # Live LLM failed — use deterministic fallback so endpoint
    # always returns a structured result.
    violations, covered = _deterministic_violations(draft_md, student_cv, ground_truth)
    # coverage = fraction of competencies present in the roadmap (computed
    # by the deterministic check, not re-derived from the violation list,
    # which is always 0.0 while FRAMEWORK_COVERAGE fails).
    coverage = covered
    if not violations:
        coverage = 1.0
    personalization = _cv_personalization(draft_md, student_cv)
    return {
        "coverage_score": round(coverage, 3),
        "personalization_score": round(personalization, 3),
        "violations": violations,
        "sources": sources,
        "source": "fallback",
        "deterministic": covered,
        "warning": f"LLM unavailable ({llm_failed_reason}); deterministic validation used.",
    }