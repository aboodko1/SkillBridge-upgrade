"""Practice static-check dispatch contracts.

End-to-end coverage for the single Practice API dispatch point
(``practice.evaluate_practice_static_check``): every one of the 23 curated
learning topics is routed to its exact specialized static evaluator and the
result is exposed as ``attempt.practice_task.static_check`` — while uncurated
or unknown lessons get no static check (an honest provider/fallback only),
student answers are never executed, and practice never verifies a skill.

Each curated family is walked with one diagnostic -> path -> lesson flow; the
correct answer for every topic is derived from its own lesson's canonical
``starter_code`` so the assertions stay honest to the prescribed exercise shape.
"""
from urllib.parse import quote

import inspect
import re

import pytest

from app import genai, lessons, models, practice


@pytest.fixture(autouse=True)
def offline_reviewer(monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)


CURATED_TOPICS = {
    "SQL": ["SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins",
            "Subqueries", "Indexing basics", "Window functions", "Query optimization",
            "Transactions", "Schema design"],
    "Git": ["Local repositories", "Committing", "Branching", "Merging", "Rebasing",
            "Remotes & collaboration", "History rewriting", "Bisect & debugging",
            "Submodules", "Workflows & policy", "Large-repo strategies"],
    "Python": ["Python Functions", "Python Error Handling"],
}


PYTHON_ANSWERS = {
    "Python Functions": "def celsius_to_fahrenheit(celsius):\n    return (celsius * 9 / 5) + 32",
    "Python Error Handling": "def parse_score(text):\n    try:\n        return int(text)\n    except ValueError:\n        return None",
}


GIT_PROSE = {
    "Merging": "When both branches changed the same lines, Git reports a conflict and you resolve it by editing the file, staging with `git add`, then finishing the commit.",
    "Rebasing": "Rebase replays commits onto main to keep a linear history, and you must never rebase commits that have already been shared.",
    "Remotes & collaboration": "The difference is that fetch only downloads remote state while pull integrates it, and a Pull Request is a review step on the hosting service.",
    "History rewriting": "Local unpublished commits may be rewritten, but published commits must not because their hashes are already shared.",
    "Bisect & debugging": "Git checks out midpoint commits for you to test, and the finished bisect names the first bad commit.",
    "Submodules": "The parent records a pinned commit (a specific SHA), not a moving branch.",
    "Workflows & policy": "Feature branches isolate work, and Pull Requests, protected branches, and CI are hosting-service policy.",
    "Large-repo strategies": "The trade-offs are history size, on-demand network, working-tree scope, and server storage.",
}

GIT_BOUNDARY = " SkillBridge static review does not run these commands or modify anything."

SQL_BOUNDARY = "\n\nThis is a written answer; the static review does not execute it."


def _canonical_answer(lesson_content):
    """Build the exact accepted answer for a curated lesson's practice task.

    Every curated ``practice`` block owns its ``starter_code`` (the prescribed
    commands / expression the reviewer recognises), so the answer here is the
    lesson's own reference plus the family-specific explanatory prose that each
    gate (e.g. ``mentions_static_boundary``) requires.
    """
    practice_block = lesson_content["practice"] or {}
    competency = practice_block.get("competency")
    starter = str(practice_block.get("starter_code") or "").strip()
    if competency in PYTHON_ANSWERS:
        return PYTHON_ANSWERS[competency]
    if practice_block.get("language") == "bash":
        return (starter + "\n\n" + GIT_PROSE.get(competency, "") + GIT_BOUNDARY).strip()
    return starter + SQL_BOUNDARY


def _make_path(client, student_id, headers, skill):
    generated = client.post(
        f"/api/students/{student_id}/learning/{skill['id']}/diagnostic/generate",
        json={}, headers=headers)
    assert generated.status_code == 200, generated.text
    diagnostic = generated.json()
    submitted = client.post(
        f"/api/students/{student_id}/learning/{skill['id']}/diagnostic/submit",
        json={"diagnostic_id": diagnostic["diagnostic_id"], "answers": ["not this" for _ in diagnostic["questions"]]},
        headers=headers)
    assert submitted.status_code == 200, submitted.text
    path = client.post(
        f"/api/students/{student_id}/learning/{skill['id']}/personalized-path/generate",
        json={}, headers=headers)
    assert path.status_code == 200, path.text
    return path.json()


def _url(student_id, skill_id, competency):
    return f"/api/students/{student_id}/learning/{skill_id}/lessons/{quote(competency, safe='')}"


# ---------------------------------------------------------------- unit: registry

def test_dispatch_registry_is_exactly_1_1_with_the_curated_topics():
    # The registry exposes one entry per curated topic and each entry is the
    # exact evaluator that owns that topic (matched by the competency gate the
    # evaluator itself enforces, never by naming convention).
    registry = practice._PRACTICE_STATIC_CHECK_EVALUATORS
    assert set(registry) == {topic for topics in CURATED_TOPICS.values() for topic in topics}
    assert len(registry) == 23

    dispatcher = [name for name in dir(practice) if name == "evaluate_practice_static_check"]
    static_checks = [name for name in dir(practice)
                     if name.endswith("_static_check") and name != "evaluate_practice_static_check"]
    assert len(dispatcher) == 1
    assert len(static_checks) == 23
    for topic, evaluator in registry.items():
        assert callable(evaluator)
        assert evaluator.__module__ == practice.__name__
        source = inspect.getsource(evaluator)
        gate = re.search(r'get\("competency"\)\s*!=\s*"([^"]+)"', source)
        assert gate, f"no competency gate found in {evaluator.__name__}"
        assert gate.group(1) == topic, f"{evaluator.__name__} gate {gate.group(1)!r} != key {topic!r}"


def test_dispatch_is_scope_limited_and_never_fabricates_a_check():
    assert practice.evaluate_practice_static_check({}, "anything") is None
    assert practice.evaluate_practice_static_check({"content": {}}, "anything") is None
    # Curated source but an unknown / uncurated competency gets no check.
    assert practice.evaluate_practice_static_check(
        {"content": {"canonical": {"source": "trusted_cs_knowledge_base"},
                     "practice": {"competency": "Not a curated topic"}}}, "x") is None
    # Human-authorable source never engages the curated teacher's check.
    content = lessons.generate_lesson("SQL", "Queries & filtering", "learn")
    content["canonical"]["source"] = "generated"
    assert practice.evaluate_practice_static_check({"content": content}, "SELECT 1;") is None


def test_dispatch_envelope_is_never_a_score_or_verification_claim():
    lesson = {"content": lessons.generate_lesson("Python", "Python Functions", "learn")}
    result = practice.evaluate_practice_static_check(lesson, PYTHON_ANSWERS["Python Functions"])
    assert result is not None
    for key in ("score", "verified", "completed", "pass", "id"):
        assert key not in result, f"static check must not fabricate {key!r}"
    assert isinstance(result["status"], str)
    assert all(not (isinstance(check, str) and "verified" in check.lower()) for check in result.get("checks", []))


# --------------------------------------------------------- endpoint: SQL (10/10)

def test_sql_static_dispatch_routes_ten_topic_lessons(client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    sql = models.get_skill_by_name("SQL")
    before = {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []}
    path = _make_path(client, student_id, headers, sql)
    competencies = [item["competency"] for item in path["items"]]
    assert competencies == ["sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins",
                            "sql_subqueries", "sql_indexing_basics", "sql_window_functions", "sql_query_optimization",
                            "sql_transactions", "sql_schema_design"]

    routed_topics = set()
    for item in path["items"]:
        base = _url(student_id, sql["id"], item["competency"])
        lesson = client.post(base + "/generate", json={}, headers=headers)
        assert lesson.status_code == 200, lesson.text
        content = lesson.json()["content"]
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        topic = content["practice"]["competency"]
        routed_topics.add(topic)

        attempt = client.post(base + "/practice", json={"answer": _canonical_answer(content)}, headers=headers)
        assert attempt.status_code == 200, attempt.text
        payload = attempt.json()
        assert payload.get("reused") is not True
        static = payload["attempt"]["practice_task"].get("static_check")
        assert static is not None, f"{item['competency']} did not route to a static reviewer"
        assert static["kind"] == "sql_text", f"{item['competency']} routed to the wrong reviewer family"
        assert static["status"] == "looks_structurally_sound"

        # A mutating / unsafe answer is honestly flagged, never accepted.
        unsafe = client.post(base + "/practice", json={"answer": "DELETE FROM customers;\nnot a SELECT review"}, headers=headers)
        assert unsafe.status_code == 200, unsafe.text
        unsafe_static = unsafe.json()["attempt"]["practice_task"].get("static_check")
        assert unsafe_static is not None
        assert unsafe_static["status"] == "needs_fix"
        assert unsafe_static.get("checks"), "unsafe answer produced no corrective checks"
        assert any(("read-only" in check) or ("SELECT" in check) or (check.startswith("Start the statement"))
                   for check in unsafe_static.get("checks", []))

    assert routed_topics == set(CURATED_TOPICS["SQL"])
    assert {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []} == before


# ---------------------------------------------------------- endpoint: Git (11/11)

def test_git_static_dispatch_routes_eleven_topic_lessons(client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    git = models.get_skill_by_name("Git")
    before = {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []}
    path = _make_path(client, student_id, headers, git)
    competencies = [item["competency"] for item in path["items"]]
    assert competencies == ["git_local_repositories", "git_committing", "git_branching", "git_merging",
                            "git_rebasing", "git_remotes_collaboration", "git_history_rewriting",
                            "git_bisect_debugging", "git_submodules", "git_workflows_&_policy",
                            "git_large-repo_strategies"]

    routed_topics = set()
    for item in path["items"]:
        base = _url(student_id, git["id"], item["competency"])
        lesson = client.post(base + "/generate", json={}, headers=headers)
        assert lesson.status_code == 200, lesson.text
        content = lesson.json()["content"]
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        topic = content["practice"]["competency"]
        routed_topics.add(topic)

        attempt = client.post(base + "/practice", json={"answer": _canonical_answer(content)}, headers=headers)
        assert attempt.status_code == 200, attempt.text
        payload = attempt.json()
        assert payload.get("reused") is not True
        static = payload["attempt"]["practice_task"].get("static_check")
        assert static is not None, f"{item['competency']} did not route to a static reviewer"
        assert static["kind"] == "git_text", f"{item['competency']} routed to the wrong reviewer family"
        assert static["status"] == "looks_structurally_sound"
        assert "did not run" in static["note"]

    assert routed_topics == set(CURATED_TOPICS["Git"])
    assert {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []} == before


# ------------------------------------------------------ endpoint: Python (2/2)

def test_python_static_dispatch_routes_both_topic_lessons(client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    python = models.get_skill_by_name("Python")
    before = {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []}
    path = _make_path(client, student_id, headers, python)
    assert [item["competency"] for item in path["items"]] == ["python_functions", "python_error_handling"]

    routed_topics = set()
    for item in path["items"]:
        base = _url(student_id, python["id"], item["competency"])
        lesson = client.post(base + "/generate", json={}, headers=headers)
        assert lesson.status_code == 200, lesson.text
        content = lesson.json()["content"]
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        topic = content["practice"]["competency"]
        routed_topics.add(topic)

        first = client.post(base + "/practice", json={"answer": _canonical_answer(content)}, headers=headers)
        assert first.status_code == 200, first.text
        static = first.json()["attempt"]["practice_task"].get("static_check")
        assert static is not None, f"{item['competency']} did not route to a static reviewer"
        assert static["status"] == "looks_structurally_sound"
        assert "not executed" in static["note"]

        # Exact-answer reuse only: the same answer reuses, a changed answer
        # re-enters the evaluator.
        cached = client.post(base + "/practice", json={"answer": _canonical_answer(content)}, headers=headers)
        assert cached.status_code == 200, cached.text
        assert cached.json()["reused"] is True
        changed = client.post(base + "/practice", json={"answer": _canonical_answer(content) + "\nI checked one more case."}, headers=headers)
        assert changed.status_code == 200, changed.text
        assert changed.json().get("reused") is not True

    assert routed_topics == set(CURATED_TOPICS["Python"])
    assert {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []} == before