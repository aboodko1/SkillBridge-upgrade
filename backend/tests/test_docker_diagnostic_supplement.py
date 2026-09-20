"""Docker diagnostic SUPPLEMENT behavior (Phase 1).

Curated banks cover the Docker topics that have them; AI fallback covers the
rest, with deterministic gap-filling when the provider is down or partial.
"""
import json

import pytest

from app import coverage, diagnostics, genai, models


@pytest.fixture(autouse=True)
def offline_by_default(monkeypatch):
    """Most tests run without a real GenAI provider."""
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)


@pytest.fixture()
def docker_skill(db):
    return models.get_skill_by_name("Docker")


@pytest.fixture()
def python_skill(db):
    return models.get_skill_by_name("Python")


@pytest.fixture()
def git_skill(db):
    return models.get_skill_by_name("Git")


@pytest.fixture()
def aisha_id(client):
    return client.post("/api/auth/login", json={
        "email": "aisha@student.edu", "password": "demo1234"}).json()["student"]["id"]


def _generate(client, student_id, skill_id, headers):
    return client.post(
        f"/api/students/{student_id}/learning/{skill_id}/diagnostic/generate",
        json={}, headers=headers)


def _submit(client, student_id, skill_id, diag_id, answers, headers):
    return client.post(
        f"/api/students/{student_id}/learning/{skill_id}/diagnostic/submit",
        json={"diagnostic_id": diag_id, "answers": answers}, headers=headers)


def _final_status(client, student_id, skill_id, headers):
    return client.get(
        f"/api/students/{student_id}/learning/{skill_id}/final-assessment/status",
        headers=headers)


# ------------------------------------------------------------------ coverage

def test_docker_diagnostic_offline_covers_all_11_topics(client, aisha_id,
                                                        docker_skill,
                                                        auth_headers):
    headers = auth_headers("aisha@student.edu")
    r = _generate(client, aisha_id, docker_skill["id"], headers)
    assert r.status_code == 200, r.text
    body = r.json()
    qs = body["questions"]
    expected = {
        "containers", "images", "basic_commands", "dockerfile",
        "ports", "volumes", "networking", "compose",
        "multi-stage_builds", "security_&_secrets", "orchestration_basics",
    }
    actual = {q["competency"] for q in qs}

    assert len(qs) == 15, f"expected 15 questions (curated banks + one probe per remaining competency), got {len(qs)}"
    assert actual == expected, f"missing/extra competencies: {expected ^ actual}"

    # All 11 Docker blueprint topics now have curated MCQ banks.
    curated_topics = {
        "containers", "images", "basic_commands", "dockerfile", "ports",
        "volumes", "networking", "compose", "multi-stage_builds",
        "security_&_secrets", "orchestration_basics",
    }
    curated = [q for q in qs if q["competency"] in curated_topics]
    assert len(curated) == 15
    assert all(q["type"] == "mcq" for q in curated)

    # No uncovered topics remain, so there are no fallback free-text probes.
    fallback = [q for q in qs if q["competency"] not in curated_topics]
    assert len(fallback) == 0


def test_docker_diagnostic_no_duplicate_competency_coverage(client, aisha_id,
                                                            docker_skill,
                                                            auth_headers):
    headers = auth_headers("aisha@student.edu")
    r = _generate(client, aisha_id, docker_skill["id"], headers).json()
    by_comp = {}
    for q in r["questions"]:
        by_comp.setdefault(q["competency"], 0)
        by_comp[q["competency"]] += 1
    # Curated banks intentionally ask 3 questions per topic; other competencies
    # should receive exactly one deterministic probe when offline.
    assert by_comp["containers"] == 3
    assert by_comp["images"] == 3
    for comp in ("basic_commands", "dockerfile", "ports", "volumes",
                 "networking", "compose", "multi-stage_builds",
                 "security_&_secrets", "orchestration_basics"):
        assert by_comp[comp] == 1, f"unexpected count for {comp}: {by_comp[comp]}"


# ------------------------------------------------------------------ provider behavior

def test_docker_partial_provider_fills_uncovered_competencies(
        monkeypatch, client, aisha_id, docker_skill, auth_headers):
    """When the provider only answers some topics, deterministic probes cover the rest."""
    headers = auth_headers("aisha@student.edu")
    comps = diagnostics.resolve_topics(docker_skill["name"])
    slugs = [diagnostics.competency_slug(c) for c in comps]

    # Provider returns exactly 3 questions, all for non-curated competencies.
    payload = json.dumps([
        {"question": f"{s} question?", "type": "mcq",
         "options": ["a", "b", "c", "d"], "correct_answer": "a",
         "competency": s, "difficulty": "beginner"}
        for s in ("basic_commands", "dockerfile", "ports")])

    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    monkeypatch.setattr(genai, "complete", lambda *a, **k: payload)

    r = _generate(client, aisha_id, docker_skill["id"], headers)
    assert r.status_code == 200, r.text
    qs = r.json()["questions"]
    actual = {q["competency"] for q in qs}
    expected = set(slugs)
    assert expected <= actual, f"uncovered: {expected - actual}"


def test_docker_complete_provider_failure_does_not_fabricate_readiness(
        monkeypatch, client, aisha_id, docker_skill, auth_headers):
    """A failed provider falls back to honest coverage; wrong answers are not readiness."""
    headers = auth_headers("aisha@student.edu")
    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    monkeypatch.setattr(genai, "complete", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("provider down")))

    gen = _generate(client, aisha_id, docker_skill["id"], headers).json()
    qs = gen["questions"]
    assert len(qs) == 15
    assert {q["competency"] for q in qs} == {
        "containers", "images", "basic_commands", "dockerfile",
        "ports", "volumes", "networking", "compose",
        "multi-stage_builds", "security_&_secrets", "orchestration_basics",
    }

    # Submit deliberately wrong answers so nothing is mastered.
    answers = []
    for q in qs:
        if q["type"] == "mcq":
            wrong = next(o for o in q["options"] if o != q["correct_answer"])
            answers.append(wrong)
        else:
            answers.append("I don't know")

    sub = _submit(client, aisha_id, docker_skill["id"], gen["diagnostic_id"], answers, headers)
    assert sub.status_code == 200, sub.text
    topic_results = sub.json()["topic_results"]
    assert topic_results
    for t in topic_results:
        assert t["status"] in ("weak", "developing"), t

    status = _final_status(client, aisha_id, docker_skill["id"], headers)
    assert status.status_code == 200, status.text
    assert status.json()["readiness"]["ready"] is False


# ------------------------------------------------------------------ other skills unchanged

def test_python_diagnostic_still_replaces_with_curated_bank(
        client, aisha_id, python_skill, auth_headers):
    headers = auth_headers("aisha@student.edu")
    r = _generate(client, aisha_id, python_skill["id"], headers)
    assert r.status_code == 200, r.text
    qs = r.json()["questions"]
    assert len(qs) == 6
    assert {q["competency"] for q in qs} == {"python_functions", "python_error_handling"}


def test_sql_diagnostic_curated_slice_unchanged(client, aisha_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    sql = models.get_skill_by_name("SQL")
    # Only the curated competency is requested, matching existing SQL behavior.
    qs = genai.generate_diagnostic(
        sql["name"], ["Queries & filtering"], "Data Analyst")
    assert len(qs) == 3
    assert all(q["competency"] == "sql_queries_filtering" for q in qs)


def test_git_diagnostic_unchanged(client, aisha_id, git_skill, auth_headers):
    # Combined curriculum (Eslam Git 11/11): curated banks produce 3 questions
    # per Git topic, so the full Git diagnostic is 33 questions. This matches
    # Eslam's own test_curated_git_foundations.py assertion (== 33) and the
    # browser-validated product. The Docker supplementation work must not
    # change other skills' diagnostic behavior.
    headers = auth_headers("aisha@student.edu")
    r = _generate(client, aisha_id, git_skill["id"], headers)
    assert r.status_code == 200, r.text
    qs = r.json()["questions"]
    assert len(qs) == 33
    assert all(q["competency"] for q in qs)


# ------------------------------------------------------------------ persistence / ordering

def test_docker_diagnostic_progress_persists_and_path_follows_blueprint(
        client, aisha_id, docker_skill, auth_headers):
    headers = auth_headers("aisha@student.edu")
    gen = _generate(client, aisha_id, docker_skill["id"], headers).json()
    qs = gen["questions"]
    answers = [q["correct_answer"] for q in qs]
    sub = _submit(client, aisha_id, docker_skill["id"], gen["diagnostic_id"], answers, headers)
    assert sub.status_code == 200, sub.text

    latest = client.get(
        f"/api/students/{aisha_id}/learning/{docker_skill['id']}/diagnostic/latest",
        headers=headers).json()
    assert latest["id"] == gen["diagnostic_id"]

    path = client.post(
        f"/api/students/{aisha_id}/learning/{docker_skill['id']}/personalized-path/generate",
        json={}, headers=headers).json()
    from app import skill_blueprint as sb
    expected_order = sb.required_competencies("Docker", "Beginner", "Advanced")
    path_competencies = [item["competency"] for item in path["items"]]
    path_indices = [expected_order.index(c) for c in path_competencies if c in expected_order]
    assert path_indices == sorted(path_indices), "Path order must follow blueprint order"
