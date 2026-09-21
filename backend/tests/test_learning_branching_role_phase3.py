"""WP-GO-04 — Weak vs Developing branching + target-role anchoring.

Lesson generation must branch depth on the backend-resolved mastery band (weak
vs developing), anchor every Learn section to the student's persisted target
role, and never accept a role or band from the request body. All provider calls
are mocked — no network, no cost.
"""
import json

import pytest

from app import genai, lessons, models


@pytest.fixture()
def docker_skill(db):
    return models.get_skill_by_name("Docker")


def _force_ai_path(monkeypatch):
    monkeypatch.setattr(lessons.knowledge_base, "complete_lesson", lambda *a, **k: None)


def _capture_complete(monkeypatch):
    captured = {}

    def fake_complete(system, user, **kwargs):
        captured["system"] = system
        captured["user"] = user
        return json.dumps(_fake_ai_content())

    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    monkeypatch.setattr(genai, "complete", fake_complete)
    return captured


def _fake_ai_content():
    return {
        "learn": {
            "title": "Containers",
            "explanation": "What containers are and why. A Junior AI Engineer runs them daily.",
            "key_ideas": ["isolate apps", "images", "a Junior AI Engineer ships them"],
            "key_terms": {"image": "a snapshot used by a Junior AI Engineer"},
            "job_relevance": "A Junior AI Engineer runs containers for model deploys.",
            "common_mistake": "Assuming syntax is valid. A Junior AI Engineer verifies instead.",
            "worked_example": "A practice walkthrough a Junior AI Engineer would follow.",
            "depth_note": "Weak: starts from fundamentals.",
            "grounding_sources": [],
            "unsupported_claims": [],
        },
        "example": {"title": "Ex", "type": "code", "content": "docker run --rm app",
                    "explanation": "e"},
        "practice": {"type": "practical", "title": "Deploy containers",
                     "task": "Deploy a containerized app.", "response_type": "code",
                     "competency": "containers"},
        "mini_check": {"questions": [
            {"id": "m1", "type": "mcq", "question": "q?", "options": ["a", "b"],
             "correct_answer": "a", "competency": "containers", "difficulty": "beginner"}]},
    }


# ---------------------------------------------------------------- prompt branching


def test_weak_and_developing_produce_different_prompts(monkeypatch):
    _force_ai_path(monkeypatch)
    weak_cap = _capture_complete(monkeypatch)
    lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Junior AI Engineer")
    weak_user = weak_cap["user"]
    weak_system = weak_cap["system"]

    dev_cap = _capture_complete(monkeypatch)
    lessons.generate_lesson(
        "Docker", "containers", "review", topic_status="developing",
        diagnostic_score=0.6, required_level="Intermediate", target_role="Junior AI Engineer")
    dev_user = dev_cap["user"]
    dev_system = dev_cap["system"]

    # The system prompt carries both branch instructions (weak vs developing) so
    # it is intentionally shared; the per-student user prompt must differ.
    assert weak_user != dev_user
    assert "Mode: learn" in weak_user
    assert "Mode: review" in dev_user
    assert "Diagnostic status: weak" in weak_user
    assert "Diagnostic status: developing" in dev_user
    assert "WEAK (mode 'learn')" in weak_system
    assert "DEVELOPING (mode 'review')" in dev_system


def test_role_anchor_directive_names_target_role(monkeypatch):
    _force_ai_path(monkeypatch)
    cap = _capture_complete(monkeypatch)
    lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner",
        target_role="Junior Data Scientist")
    assert "Junior Data Scientist" in cap["system"]
    assert "ROLE ANCHORING" in cap["system"]


def test_two_target_roles_produce_different_prompts(monkeypatch):
    _force_ai_path(monkeypatch)
    cap_a = _capture_complete(monkeypatch)
    lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Data Analyst")
    prompt_a = cap_a["system"]

    cap_b = _capture_complete(monkeypatch)
    lessons.generate_lesson(
        "Docker", "containers", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="DevOps Engineer")
    prompt_b = cap_b["system"]

    assert prompt_a != prompt_b
    assert "Data Analyst" in prompt_a and "DevOps Engineer" in prompt_b


# ---------------------------------------------------------------- fallback branching


def test_fallback_weak_vs_developing_differ_measurably():
    weak = lessons._lesson_fallback("Docker", "containers", "learn", "weak", 0.2,
                                    "Beginner", "Junior AI Engineer")
    dev = lessons._lesson_fallback("Docker", "containers", "review", "developing", 0.6,
                                   "Intermediate", "Junior AI Engineer")
    assert weak["learn"]["explanation"] != dev["learn"]["explanation"]
    assert weak["learn"]["key_ideas"] != dev["learn"]["key_ideas"]
    assert len(weak["learn"]["key_ideas"]) > 0 and len(dev["learn"]["key_ideas"]) > 0
    assert "from the ground" in weak["learn"]["explanation"].lower()
    assert "working foundation" in dev["learn"]["explanation"].lower()


def test_fallback_role_appears_in_every_section():
    content = lessons._lesson_fallback("Docker", "containers", "learn", "weak", 0.2,
                                       "Beginner", "Junior AI Engineer")
    learn = content["learn"]
    all_sections = " ".join([
        learn["explanation"],
        learn["job_relevance"],
        learn["common_mistake"],
        learn["worked_example"],
        " ".join(learn["key_ideas"]),
        " ".join(learn["key_terms"].values()),
    ])
    assert "Junior AI Engineer" in all_sections
    # every individual prose section carries the role
    assert "Junior AI Engineer" in learn["explanation"]
    assert "Junior AI Engineer" in learn["common_mistake"]
    assert "Junior AI Engineer" in learn["worked_example"]


def test_fallback_developing_role_in_every_section():
    content = lessons._lesson_fallback("Docker", "containers", "review", "developing", 0.6,
                                       "Intermediate", "Junior AI Engineer")
    learn = content["learn"]
    assert "Junior AI Engineer" in learn["explanation"]
    assert "Junior AI Engineer" in learn["common_mistake"]
    assert "Junior AI Engineer" in learn["worked_example"]


def test_fallback_still_labelled_ok_for_old_schema():
    # The fallback path does not attach a top-level source label; lessons are
    # normalized at read time. Assert the schema fields that old clients rely on.
    content = lessons._lesson_fallback("Docker", "containers", "learn", "weak", 0.2,
                                       "Beginner", "Junior AI Engineer")
    assert content["learn"]["explanation"]
    assert content["practice"]["type"] == "practical"
    assert content["mini_check"]["questions"]


# ---------------------------------------------------------------- body injection


def test_request_body_role_injection_is_ignored(client, docker_skill, student_id, auth_headers, monkeypatch):
    """A body trying to set target_role is ignored; the role comes from persisted state."""
    _force_ai_path(monkeypatch)
    monkeypatch.setattr(genai, "genai_enabled", lambda: True)

    # Persist a target role for the student server-side.
    role = models.get_student(student_id).get("target_role") or {}
    if not role.get("title"):
        role_id = models.list_roles(search="Junior AI Engineer")
        if role_id:
            models.update_student(student_id, target_role_id=role_id[0]["id"])
    persisted_title = (models.get_student(student_id).get("target_role") or {}).get("title")

    gen = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/diagnostic/generate",
        json={}, headers=auth_headers("aisha@student.edu")).json()
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
        json={"diagnostic_id": gen["diagnostic_id"], "answers": answers},
        headers=auth_headers("aisha@student.edu"))
    path = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/personalized-path/generate",
        json={}, headers=auth_headers("aisha@student.edu")).json()
    comp = path["items"][0]["competency"]

    import json as _json

    def fake_complete(system, user, **kwargs):
        return _json.dumps(_fake_ai_content())

    monkeypatch.setattr(genai, "complete", fake_complete)

    # Attacker tries to inject a role AND a band override.
    resp = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/lessons/{comp}/generate",
        json={"target_role": "attacker", "action": "learn"},
        headers=auth_headers("aisha@student.edu"))
    assert resp.status_code == 200, resp.text
    content = resp.json()
    # The persisted role wins; the injected "attacker" never appears.
    assert "attacker" not in _json.dumps(content)
    # And the persisted role is the one used for anchoring.
    if persisted_title:
        assert persisted_title in content.get("content", {}).get("learn", {}).get("job_relevance", "")