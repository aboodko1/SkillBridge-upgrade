"""Canonical metric registry (data-truth layer).

Every score the product shows a student is one of a small, named set of metrics.
Before this module the same underlying ideas were labelled generically as
"match" in several places, and a few of them were recomputed in the browser from
different inputs, so the same role could show 100% on one page and 88% on
another while a real requirement gap was still visible.

Rules locked by tests (``test_data_truth_phase2.py``):

  - One metric -> one key, one label, one formula, one rounding rule.
  - The backend is the single source of truth; the frontend never recomputes a
    score from raw counts.
  - A visible gap (``gap`` or ``missing``) prevents any "complete requirement
    coverage" claim: ``all_requirements_met`` is False and the coverage metric
    is below 100.0.
  - The four evidence tiers stay distinct: self-reported, CV-detected,
    practiced/topic-completed, and officially verified. Only a passed Final
    Assessment writes a ``verified_skills`` row.

Metrics
-------
- ``target_requirement_coverage``: level-aware, partial-credit coverage of the
  target role's required skills (the Dashboard ring). 1 decimal.
- ``career_readiness``: same evidence, all-or-nothing per requirement (share of
  requirements actually met at/above level). 1 decimal. Never implies verified.
- ``verified_evidence_coverage``: share of required skills with official
  verified evidence. 1 decimal. The only metric backed by assessments.
- ``catalogue_similarity``: name-only overlap between a role's required skills
  and a profile's skill names. NOT a competence or verification claim; used only
  as a labelled fallback for catalogue roles that are not scored by the
  recommendation engine.
"""
from . import matching

TARGET_REQUIREMENT_COVERAGE = "target_requirement_coverage"
CAREER_READINESS = "career_readiness"
VERIFIED_EVIDENCE_COVERAGE = "verified_evidence_coverage"
CATALOGUE_SIMILARITY = "catalogue_similarity"

_METRIC_DEFINITIONS = {
    TARGET_REQUIREMENT_COVERAGE: {
        "key": TARGET_REQUIREMENT_COVERAGE,
        "label": "Target requirement coverage",
        "short_label": "Requirement coverage",
        "formula": ("sum(credit per required skill) / count(required skills) "
                    "* 100, rounded to 1 decimal"),
        "evidence": ("Best available evidence per skill (verified > self-reported). "
                     "Full credit at/above the required level, partial credit for "
                     "progress below it, reduced credit for adjacent-name evidence."),
        "rounding": "1 decimal",
        "complete_when": "100.0 with no gap or missing rows",
    },
    CAREER_READINESS: {
        "key": CAREER_READINESS,
        "label": "Career readiness (requirements met)",
        "short_label": "Requirements met",
        "formula": ("count(required skills at/above the required level) / "
                    "count(required skills) * 100, rounded to 1 decimal"),
        "evidence": ("Same per-skill evidence as target requirement coverage, but "
                     "each requirement is all-or-nothing (no partial credit). It is "
                     "not a verified claim."),
        "rounding": "1 decimal",
        "complete_when": "100.0 (every requirement is met at or above its level)",
    },
    VERIFIED_EVIDENCE_COVERAGE: {
        "key": VERIFIED_EVIDENCE_COVERAGE,
        "label": "Verified evidence coverage",
        "short_label": "Verified coverage",
        "formula": ("count(required skills backed by a passed Final Assessment) / "
                    "count(required skills) * 100, rounded to 1 decimal"),
        "evidence": ("Only ``verified_skills`` rows (earned by passing a Final "
                     "Assessment) count. Self-reported, CV-detected, practiced and "
                     "topic-completed skills never count here."),
        "rounding": "1 decimal",
        "complete_when": "100.0 (every requirement has verified evidence)",
    },
    CATALOGUE_SIMILARITY: {
        "key": CATALOGUE_SIMILARITY,
        "label": "Catalogue similarity",
        "short_label": "Skill-name overlap",
        "formula": ("count(required skill names present in the profile by exact "
                    "name) / count(required skills) * 100, rounded to 1 decimal"),
        "evidence": ("Name presence only (self-reported or CV-detected). It is NOT "
                     "a level or verification claim and is never shown as a "
                     "verified match."),
        "rounding": "1 decimal",
        "complete_when": ("Never treated as completion; name overlap is not proof "
                          "of competence"),
    },
}

CANONICAL_METRICS = (
    TARGET_REQUIREMENT_COVERAGE,
    CAREER_READINESS,
    VERIFIED_EVIDENCE_COVERAGE,
    CATALOGUE_SIMILARITY,
)


def definitions():
    """A deep-enough copy of the registry for API consumers (tooltips/explainers)."""
    return {key: dict(value) for key, value in _METRIC_DEFINITIONS.items()}


def _pct(numerator, denominator):
    if not denominator:
        return 0.0
    return round((numerator / denominator) * 100.0, 1)


def target_requirement_coverage(student, role):
    """Level-aware, partial-credit coverage of the target role's requirements."""
    if not role or not role.get("required_skills"):
        return 0.0
    return round(float(matching.job_match_score(student, role)), 1)


def career_readiness(student, role):
    """Share of requirements actually met at/above level (all-or-nothing)."""
    rows = matching.categorize(student, role)
    if not rows:
        return 0.0
    return _pct(len([r for r in rows if r["status"] == "strong"]), len(rows))


def verified_evidence_coverage(student, role):
    """Share of requirements backed by an official passed-assessment record."""
    rows = matching.categorize(student, role)
    if not rows:
        return 0.0
    return _pct(len([r for r in rows if r.get("verified")]), len(rows))


def catalogue_similarity(role, profile_skill_names):
    """Name-only overlap. Never a competence or verification claim."""
    required = (role or {}).get("required_skills") or []
    if not required:
        return 0.0
    names = {str(n).strip().lower() for n in (profile_skill_names or []) if n}
    present = sum(
        1 for rs in required
        if str(rs.get("name") or "").strip().lower() in names)
    return _pct(present, len(required))


def all_requirements_met(student, role):
    """True only when every required skill is met at/above its level."""
    rows = matching.categorize(student, role)
    return bool(rows) and all(r["status"] == "strong" for r in rows)


def missing_requirements(student, role):
    """Names of required skills that are not yet met (gap or missing)."""
    return [r["skill_name"] for r in matching.categorize(student, role)
            if r["status"] != "strong"]


def bundle(student, role):
    """The canonical metric values for a student/target-role pair."""
    return {
        TARGET_REQUIREMENT_COVERAGE: target_requirement_coverage(student, role),
        CAREER_READINESS: career_readiness(student, role),
        VERIFIED_EVIDENCE_COVERAGE: verified_evidence_coverage(student, role),
    }
