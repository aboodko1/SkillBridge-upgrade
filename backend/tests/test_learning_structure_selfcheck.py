"""WP-GO-05 — 5-part structure enforcement + self-check wiring.

The self-check is a pure function (no LLM, no network). The lesson generator
runs it after generation, repairs missing sections deterministically from the
fallback templates, labels repaired lessons source: "fallback", and records a
selfCheck block. Old persisted lessons normalize at read time (never rewritten).
"""
import json

import pytest

from app import genai, lesson_selfcheck, lessons, models


@pytest.fixture()
def docker_skill(db):
    return models.get_skill_by_name("Docker")


def _well_formed_lesson():
    return {
        "learn": {
            "title": "Containers",
            "explanation": "What containers are and why. A Junior AI Engineer runs them daily.",
            "key_ideas": ["isolate apps", "images", "a Junior AI Engineer ships them"],
            "key_terms": {"image": "a snapshot used by a Junior AI Engineer"},
            "job_relevance": "A Junior AI Engineer runs containers for model deploys.",
            "common_mistake": "Assuming syntax is valid. A Junior AI Engineer verifies instead.",
            "worked_example": "A Junior AI Engineer walks through Deploy containers: the practice task setup.",
            "depth_note": "Weak: starts from fundamentals.",
            "version_note": "Docker 24.",
            "grounding_sources": [],
            "unsupported_claims": [],
        },
        "example": {"title": "Ex", "type": "code", "content": "docker run --rm app",
                    "explanation": "e"},
        "practice": {"type": "practical", "id": "p1", "title": "Deploy containers",
                     "task": "Deploy a containerized app.", "response_type": "code",
                     "competency": "containers"},
        "mini_check": {"questions": [
            {"id": "m1", "type": "mcq", "question": "q?", "options": ["a", "b"],
             "correct_answer": "a", "competency": "containers", "difficulty": "beginner"}]},
        "resources": [{"title": "Docker Docs", "url": "https://docs.docker.com/net/",
                       "source": "Docker"}],
    }


# ---------------------------------------------------------------- pure self-check


def test_well_formed_lesson_passes_self_check():
    problems = lesson_selfcheck.self_check_lesson(
        _well_formed_lesson(),
        {"https://docs.docker.com/net/"},
        "p1",
    )
    assert problems == []


def test_missing_section_is_flagged():
    lesson = _well_formed_lesson()
    lesson["learn"]["common_mistake"] = ""
    problems = lesson_selfcheck.self_check_lesson(
        lesson, {"https://docs.docker.com/net/"}, "p1")
    assert any("common_mistake" in p for p in problems)


def test_url_outside_catalog_is_flagged():
    lesson = _well_formed_lesson()
    lesson["resources"] = [{"title": "X", "url": "https://evil.example.com", "source": "X"}]
    problems = lesson_selfcheck.self_check_lesson(
        lesson, {"https://docs.docker.com/net/"}, "p1")
    assert any("not in curated catalog" in p for p in problems)


def test_placeholder_marker_is_flagged():
    lesson = _well_formed_lesson()
    lesson["learn"]["explanation"] = "TODO: write this properly."
    problems = lesson_selfcheck.self_check_lesson(
        lesson, {"https://docs.docker.com/net/"}, "p1")
    assert any("TODO" in p or "placeholder" in p for p in problems)


def test_missing_role_anchor_is_flagged():
    lesson = _well_formed_lesson()
    lesson["learn"]["job_relevance"] = "This is relevant."
    lesson["learn"]["explanation"] = "No role here at all."
    lesson["learn"]["common_mistake"] = "A mistake."
    lesson["learn"]["worked_example"] = "Walk through a task for the practice task."
    problems = lesson_selfcheck.self_check_lesson(
        lesson, {"https://docs.docker.com/net/"}, "p1")
    assert any("role anchor" in p for p in problems)


def test_worked_example_missing_reference_is_flagged():
    lesson = _well_formed_lesson()
    lesson["learn"]["worked_example"] = "A disconnected toy example."
    problems = lesson_selfcheck.self_check_lesson(
        lesson, {"https://docs.docker.com/net/"}, "p1")
    assert any("worked_example does not reference" in p for p in problems)


# ---------------------------------------------------------------- generation wiring


def _force_ai_path(monkeypatch):
    monkeypatch.setattr(lessons.knowledge_base, "complete_lesson", lambda *a, **k: None)
    monkeypatch.setattr(genai, "genai_enabled", lambda: True)


def test_missing_section_repaired_and_labelled_fallback(monkeypatch):
    _force_ai_path(monkeypatch)
    content_with_gap = _well_formed_lesson()
    content_with_gap["learn"]["common_mistake"] = ""

    def fake_complete(system, user, **kwargs):
        return json.dumps({
            "learn": content_with_gap["learn"],
            "example": content_with_gap["example"],
            "practice": {"type": "practical", "title": "Deploy containers",
                         "task": "Deploy a containerized app.", "response_type": "code",
                         "competency": "containers"},
            "mini_check": content_with_gap["mini_check"],
        })

    monkeypatch.setattr(genai, "complete", fake_complete)
    content = lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Junior AI Engineer")
    assert content["source"] == "fallback"
    assert content["selfCheck"]["repaired"]
    assert content["learn"]["common_mistake"]


def test_well_formed_ai_lesson_stays_live(monkeypatch):
    _force_ai_path(monkeypatch)

    def fake_complete(system, user, **kwargs):
        return json.dumps({
            "learn": _well_formed_lesson()["learn"],
            "example": _well_formed_lesson()["example"],
            "practice": _well_formed_lesson()["practice"],
            "mini_check": _well_formed_lesson()["mini_check"],
        })

    monkeypatch.setattr(genai, "complete", fake_complete)
    content = lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Junior AI Engineer")
    assert content["source"] == "ai"
    assert content["selfCheck"]["passed"] is True


def test_self_check_does_not_trigger_second_llm_call(monkeypatch):
    _force_ai_path(monkeypatch)
    calls = []

    def fake_complete(system, user, **kwargs):
        calls.append(1)
        return json.dumps({
            "learn": _well_formed_lesson()["learn"],
            "example": _well_formed_lesson()["example"],
            "practice": _well_formed_lesson()["practice"],
            "mini_check": _well_formed_lesson()["mini_check"],
        })

    monkeypatch.setattr(genai, "complete", fake_complete)
    lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Junior AI Engineer")
    assert len(calls) == 1  # exactly one LLM call; self-check is pure


# ---------------------------------------------------------------- normalization


def test_old_format_lesson_normalizes_without_rewriting_db(client, docker_skill, student_id, auth_headers):
    """Old persisted lesson (missing parts) renders after read-time normalization."""
    headers = auth_headers("aisha@student.edu")
    gen = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/diagnostic/generate",
        json={}, headers=headers).json()
    answers = [q["correct_answer"] for q in gen["questions"]]
    bad = 0
    for i, q in enumerate(gen["questions"]):
        if q["type"] == "mcq" and bad < 2:
            wrong = [o for o in q["options"] if o != q["correct_answer"]]
            if wrong:
                answers[i] = wrong[0]
                bad += 1
    client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/diagnostic/submit",
        json={"diagnostic_id": gen["diagnostic_id"], "answers": answers}, headers=headers)
    path = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/personalized-path/generate",
        json={}, headers=headers).json()
    path_id = path["id"]

    legacy_content = {
        "learn": {
            "title": "Containers",
            "explanation": "What containers are and why.",
            "key_ideas": ["i1"],
            "key_terms": {"c": "d"},
            # legacy lessons omitted common_mistake / worked_example
        },
        "example": {"title": "Ex", "type": "code", "content": "docker run", "explanation": "e"},
        "practice": {"type": "practical", "title": "Deploy containers",
                     "task": "Deploy a containerized app.", "response_type": "code",
                     "competency": "containers"},
        "mini_check": {"questions": []},
        "resources": [],
    }
    stored = models.create_lesson(
        student_id=student_id,
        skill_id=docker_skill["id"],
        path_id=path_id,
        competency="containers",
        title="Docker > containers",
        action="learn",
        content_json=legacy_content,
    )
    raw = stored["content"]  # already parsed by _lesson_dict
    # Stored JSON is untouched and still missing the parts.
    assert not raw["learn"].get("common_mistake")
    assert not raw["learn"].get("worked_example")

    normalized = lessons.normalize_lesson(
        {"content": raw}, "containers", skill_name="Docker",
        skill_category="DevOps", target_role="Junior AI Engineer", required_level="Beginner")
    content = normalized["content"]
    # Filled at read time; never persisted.
    assert content["learn"]["common_mistake"]
    assert content["learn"]["worked_example"]
    assert content["learn"]["explanation"]
    assert content["mini_check"]["questions"]
    assert content["resources"] is not None