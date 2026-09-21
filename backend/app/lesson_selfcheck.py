"""Pure 5-part structure self-check for generated lessons (WP-GO-05).

``self_check_lesson`` is deliberately free of side effects: no LLM call, no
network, no DB writes. It returns a list of human-readable problems; an empty
list means the lesson passes. The lesson generator wires it AFTER generation and
repairs deterministically when it fails (see ``lessons.repair_lesson_structure``).
"""

import re

# Actual section keys in the lesson schema (see lessons.generate_lesson).
# The 5-part Learn shape maps onto the schema like this:
#   what_why        -> learn["explanation"] (+ learn["job_relevance"])
#   core_mechanics  -> learn["key_ideas"] + learn["key_terms"]
#   common_mistake  -> learn["common_mistake"]
#   worked_example  -> learn["worked_example"]
#   resources       -> top-level lesson["resources"][]
_RESOURCE_URL_FIELD = "url"

_PLACEHOLDER_MARKERS = (
    "todo",
    "lorem ipsum",
    "as an ai",
    "[insert",
)


def _text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(str(x) for x in value if str(x).strip())
    if isinstance(value, dict):
        return " ".join(str(v) for v in value.values() if str(v).strip())
    return str(value or "")


def _role_anchor(job_relevance):
    """Derive the target-role noun phrase from job_relevance.

    Matches the role phrase pattern WP-GO-04 established (e.g. "Junior AI
    Engineer" inside "A Junior AI Engineer runs containers..."). Returns the
    longest consecutive title-case phrase, or "" when none is found.
    """
    text = _text(job_relevance)
    phrases = re.findall(r"\b[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)+\b", text)
    if not phrases:
        return ""
    return max(phrases, key=len)


def self_check_lesson(lesson, catalog_urls, practice_task_id):
    """Return a list of problems. Empty list = passes.

    ``catalog_urls`` is the set of curated-catalog URLs for this competency;
    ``practice_task_id`` is the persisted id/title of the NEXT Practice task the
    worked example must reference. No LLM call, no network, no side effects.
    """
    if not isinstance(lesson, dict):
        return ["lesson is not a dict"]

    problems = []
    learn = lesson.get("learn") if isinstance(lesson.get("learn"), dict) else {}

    # 1. All 5 parts present and non-empty.
    what_why = _text(learn.get("explanation") or "").strip()
    if not what_why:
        problems.append("what_why (learn.explanation) is empty")

    core_mechanics = (
        _text(learn.get("key_ideas") or "").strip()
        + " "
        + _text(learn.get("key_terms") or "").strip()
    )
    if not core_mechanics.strip():
        problems.append("core_mechanics (learn.key_ideas / learn.key_terms) is empty")

    common_mistake = _text(learn.get("common_mistake") or "").strip()
    if not common_mistake:
        problems.append("common_mistake (learn.common_mistake) is empty")

    worked_example = _text(learn.get("worked_example") or "").strip()
    if not worked_example:
        problems.append("worked_example (learn.worked_example) is empty")

    resources = lesson.get("resources")
    resource_list = resources if isinstance(resources, list) else []
    if not resource_list:
        problems.append("resources (top-level lesson['resources']) is empty")

    # 2. worked_example references the next Practice task id/title.
    practice = lesson.get("practice") if isinstance(lesson.get("practice"), dict) else {}
    practice_title = str(practice.get("title") or "").strip()
    reference_ok = False
    if practice_task_id:
        reference_ok = str(practice_task_id).lower() in worked_example.lower()
    if not reference_ok and practice_title:
        reference_ok = practice_title.lower() in worked_example.lower()
    if not reference_ok and "practice" in worked_example.lower():
        reference_ok = True
    if not reference_ok:
        problems.append(
            f"worked_example does not reference the next Practice task "
            f"('{practice_task_id or ''}' / '{practice_title}')"
        )

    # 3. Every URL in resources[].url is in the curated catalog.
    for item in resource_list:
        if not isinstance(item, dict):
            problems.append("resource entry is not an object")
            continue
        url = str(item.get(_RESOURCE_URL_FIELD) or "").strip()
        if url and url not in catalog_urls:
            problems.append(f"resource URL not in curated catalog: {url}")

    # 4. No placeholder markers anywhere in the lesson body.
    all_text = _text(lesson)
    lower = all_text.lower()
    for marker in _PLACEHOLDER_MARKERS:
        if marker in lower:
            problems.append(f"lesson contains placeholder marker: {marker!r}")

    # 5. A role-anchor sentence exists in every text section.
    role = _role_anchor(learn.get("job_relevance") or "")
    if role:
        sections = {
            "explanation": what_why,
            "common_mistake": common_mistake,
            "worked_example": worked_example,
        }
        for name, section in sections.items():
            if role.lower() not in section.lower():
                problems.append(f"{name} lacks role anchor '{role}'")
    else:
        problems.append("no role anchor found in learn.job_relevance")

    return problems