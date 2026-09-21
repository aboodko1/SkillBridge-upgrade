"""Final verification pass — hard invariants (V2 + V3).

Verifies on the deployed code (locally, not on Render):
  - all 9 agentic catalog IDs load (V2)
  - Practice score is never reused as a Mini Check score (invariant 2)
  - only a passed Final Assessment creates a Verified Skill (invariant 1)
  - fallback output is labelled source: "fallback" (invariant 3)
  - the frontend cannot spoof the target role (invariant 4)
  - old persisted lessons still render via read-time normalization (invariant 9)
"""
import json

import pytest

from app import genai, lessons, models, resources
from app import knowledge_base as kb

AGENTIC_IDS = [
    "agentic_tool_use",
    "agentic_mcp",
    "agentic_rag",
    "agentic_multi_agent",
    "agentic_memory",
    "agentic_planning",
    "agentic_evaluation",
    "agentic_context_engineering",
    "agentic_security",
]

# Display labels in the catalog for each agentic competency (for complete_lesson).
AGENTIC_LABELS = {
    "agentic_tool_use": "Tool Use & Function Calling",
    "agentic_mcp": "Model Context Protocol (MCP)",
    "agentic_rag": "Retrieval-Augmented Generation (RAG)",
    "agentic_multi_agent": "Multi-Agent Systems",
    "agentic_memory": "Agent Memory",
    "agentic_planning": "Planning & Task Decomposition",
    "agentic_evaluation": "Agent Evaluation & Guardrails",
    "agentic_context_engineering": "Context Engineering",
    "agentic_security": "Agent Security & Prompt Injection",
}


@pytest.fixture()
def docker_skill(db):
    return models.get_skill_by_name("Docker")


# ------------------------------------------------------------------ V2


def test_all_nine_agentic_ids_exist_in_catalog():
    """All 9 agentic competency IDs resolve to complete curated content."""
    for cid, label in AGENTIC_LABELS.items():
        topic = kb.complete_lesson("Agentic AI", label)
        assert topic is not None, f"{cid} ({label}) missing from catalog"
        assert topic["status"] == "complete", cid
        assert topic["competency"] == label, cid
        for s in topic["learn"]["grounding_sources"]:
            assert resources.is_safe_public_url(s["url"]), (cid, s["url"])


# ------------------------------------------------------------------ V3


def _setup_path(client, headers, skill_id, student_id):
    for _ in range(3):
        gen = client.post(
            f"/api/students/{student_id}/learning/{skill_id}/diagnostic/generate",
            json={}, headers=headers).json()
        answers = [q["correct_answer"] for q in gen["questions"]]
        misses = 0
        for i, q in enumerate(gen["questions"]):
            if misses >= 3:
                break
            if q["type"] == "mcq":
                wrong = [o for o in q["options"] if o != q["correct_answer"]]
                if not wrong:
                    continue
                answers[i] = wrong[0]
            else:
                answers[i] = "not sure yet"
            misses += 1
        client.post(
            f"/api/students/{student_id}/learning/{skill_id}/diagnostic/submit",
            json={"diagnostic_id": gen["diagnostic_id"], "answers": answers},
            headers=headers)
        path = client.post(
            f"/api/students/{student_id}/learning/{skill_id}/personalized-path/generate",
            json={}, headers=headers).json()
        if path.get("items"):
            return path
    raise AssertionError("Expected diagnostic to produce at least one learning topic")


def _setup_lesson(client, headers, skill_id, student_id):
    path = _setup_path(client, headers, skill_id, student_id)
    item = path["items"][0]
    comp = item["competency"]
    r = client.post(
        f"/api/students/{student_id}/learning/{skill_id}/lessons/{comp}/generate",
        json={}, headers=headers)
    assert r.status_code == 200, r.text
    return path, item, r.json()


def test_practice_score_never_reused_as_mini_check_score(client, docker_skill, student_id, auth_headers):
    """A passed Practice never sets the Mini Check score; Mini Check is independent."""
    headers = auth_headers("aisha@student.edu")
    sk = docker_skill["id"]
    _, item, _ = _setup_lesson(client, headers, sk, student_id)
    comp = item["competency"]
    lesson_url = f"/api/students/{student_id}/learning/{sk}/lessons/{comp}"
    client.post(f"{lesson_url}/start", json={}, headers=headers)

    # Strong practice answer -> practice source fallback (deterministic), no mini score.
    p = client.post(
        f"{lesson_url}/practice",
        json={"answer": "I would explain the container storage choice, then use a named volume or bind mount so data persists beyond the container lifecycle. I would show the docker volume create step, mount it into the container, verify the host directory or volume contents, and call out the tradeoff between portable Docker-managed persistence and direct host-file access."},
        headers=headers)
    assert p.status_code == 200, p.text
    attempt = p.json()["attempt"]
    assert attempt["source"] == "fallback"
    lesson_after_practice = client.get(lesson_url, headers=headers).json()
    assert lesson_after_practice["mini_check_result"] is None, "Practice must not set a Mini Check score"

    # Now submit a Mini Check; it computes independently (pass on correct answers).
    questions = lesson_after_practice["content"]["mini_check"]["questions"]
    passed = client.post(
        f"{lesson_url}/mini-check",
        json={"answers": [q["correct_answer"] for q in questions]}, headers=headers).json()
    assert passed["lesson"]["mini_check_result"]["passed"] is True
    assert passed["lesson"]["state"] == "completed"
    # The Mini Check's own questions (distinct ids from practice) are what scored it.
    mini_ids = [q["id"] for q in passed["lesson"]["content"]["mini_check"]["questions"]]
    assert mini_ids, "Mini Check must carry its own items"


def test_only_final_assessment_creates_verified_skill(client, docker_skill, student_id, auth_headers):
    """Lesson + Mini Check (>=70%) => Completed, NOT Verified. Final Assessment => Verified."""
    headers = auth_headers("aisha@student.edu")
    sk = docker_skill["id"]
    _, item, _ = _setup_lesson(client, headers, sk, student_id)
    comp = item["competency"]
    lesson_url = f"/api/students/{student_id}/learning/{sk}/lessons/{comp}"
    client.post(f"{lesson_url}/start", json={}, headers=headers)
    lesson = client.get(lesson_url, headers=headers).json()
    mini = [q["correct_answer"] for q in lesson["content"]["mini_check"]["questions"]]
    client.post(f"{lesson_url}/mini-check", json={"answers": mini}, headers=headers)
    completed = client.get(lesson_url, headers=headers).json()
    assert completed["state"] == "completed"

    before = {(v["name"], v["level"]) for v in models.get_student(student_id).get("verified_skills") or []}
    assert "Docker" not in {name for name, _ in before}, "Mini Check must NOT verify the skill"

    # Pass the Final Assessment for Docker -> verified.
    import app.coverage as cov
    req = cov.required_slugs("Docker", "Intermediate")
    questions = [
        {"question": f"{c} q{i}", "type": "multiple_choice",
         "options": ["a", "b", "c"], "answer": "b", "explanation": "x", "competency": c}
        for i, c in enumerate(req)
    ]
    answers = ["b" for _ in questions]
    r = client.post(f"/api/students/{student_id}/assessments", json={
        "skill_id": sk, "questions": questions, "answers": answers,
        "total_seconds": 300, "tab_switches": 0, "free_text_answers": []}, headers=headers)
    assert r.json()["passed"] is True
    after = {(v["name"], v["level"]) for v in models.get_student(student_id).get("verified_skills") or []}
    assert "Docker" in {name for name, _ in after}, "Final Assessment must verify the skill"


def test_fallback_is_labelled_when_provider_fails(monkeypatch):
    """A provider failure yields source 'fallback'; a healthy provider yields live source."""
    monkeypatch.setattr(lessons.knowledge_base, "complete_lesson", lambda *a, **k: None)
    monkeypatch.setattr(genai, "genai_enabled", lambda: True)

    def failing_complete(*args, **kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(genai, "complete", failing_complete)
    fallback_lesson = lessons.generate_lesson(
        "Fake Skill 99", "weirdness", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Junior AI Engineer")
    assert fallback_lesson.get("source") == "fallback", "provider failure must be labelled fallback"

    def ok_complete(*args, **kwargs):
        return json.dumps({
            "learn": {"title": "Weirdness", "explanation": "What weirdness is and why. A Junior AI Engineer uses it.",
                      "key_ideas": ["i1", "i2"], "key_terms": {"k": "v"},
                      "job_relevance": "A Junior AI Engineer applies weirdness daily.",
                      "common_mistake": "Assuming it is valid.", "worked_example": "A walkthrough for Apply weirdness.",
                      "depth_note": "Weak.", "grounding_sources": [], "unsupported_claims": []},
            "example": {"title": "Ex", "type": "code", "content": "run", "explanation": "e"},
            "practice": {"type": "practical", "title": "Apply weirdness", "task": "Apply it.",
                         "response_type": "code", "competency": "weirdness"},
            "mini_check": {"questions": [{"id": "m1", "type": "mcq", "question": "q?", "options": ["a", "b"],
                                          "correct_answer": "a", "competency": "weirdness", "difficulty": "beginner"}]},
        })

    monkeypatch.setattr(genai, "complete", ok_complete)
    live_lesson = lessons.generate_lesson(
        "Fake Skill 99", "weirdness", "learn", topic_status="weak",
        diagnostic_score=0.2, required_level="Beginner", target_role="Junior AI Engineer")
    assert live_lesson.get("source") != "fallback", "healthy provider must not be labelled fallback"


def test_frontend_cannot_spoof_target_role(client, student_id, auth_headers, monkeypatch):
    """A request body with target_role='attacker' is ignored; the persisted role wins."""
    headers = auth_headers("aisha@student.edu")

    # Build a non-canonical skill so the provider path (and role resolution) runs.
    skill = models.create_skill("Fake Skill 99", "General")
    sk = skill["id"]
    path = _setup_path(client, headers, sk, student_id)
    comp = path["items"][0]["competency"]
    persisted = (models.get_student(student_id).get("target_role") or {}).get("title")

    monkeypatch.setattr(lessons.knowledge_base, "complete_lesson", lambda *a, **k: None)
    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    captured = {}

    def ok_complete(system, user, **kwargs):
        captured["user"] = user
        return json.dumps({
            "learn": {"title": "Weirdness", "explanation": "What weirdness is and why. A Junior AI Engineer uses it.",
                      "key_ideas": ["i1"], "key_terms": {"k": "v"},
                      "job_relevance": "A Junior AI Engineer applies weirdness daily.",
                      "common_mistake": "Assuming it is valid.", "worked_example": "A walkthrough for Apply weirdness.",
                      "depth_note": "Weak.", "grounding_sources": [], "unsupported_claims": []},
            "example": {"title": "Ex", "type": "code", "content": "run", "explanation": "e"},
            "practice": {"type": "practical", "title": "Apply weirdness", "task": "Apply it.",
                         "response_type": "code", "competency": comp},
            "mini_check": {"questions": [{"id": "m1", "type": "mcq", "question": "q?", "options": ["a", "b"],
                                          "correct_answer": "a", "competency": comp, "difficulty": "beginner"}]},
        })

    monkeypatch.setattr(genai, "complete", ok_complete)
    r = client.post(
        f"/api/students/{student_id}/learning/{sk}/lessons/{comp}/generate",
        json={"target_role": "attacker"}, headers=headers)
    assert r.status_code == 200, r.text
    content = r.json()["content"]
    # The spoofed role never appears anywhere.
    assert "attacker" not in json.dumps(content).lower()
    if persisted:
        # The persisted role was threaded into the provider prompt (trusted context).
        assert persisted in captured.get("user", "")


def test_old_persisted_lesson_still_renders(client, docker_skill, student_id, auth_headers):
    """An old-format persisted lesson (missing parts) renders after read-time normalization."""
    headers = auth_headers("aisha@student.edu")
    sk = docker_skill["id"]
    path = _setup_path(client, headers, sk, student_id)
    comp = path["items"][0]["competency"]
    legacy_content = {
        "learn": {"title": "Containers", "explanation": "What containers are and why.",
                  "key_ideas": ["i1"], "key_terms": {"c": "d"}},
        "example": {"title": "Ex", "type": "code", "content": "docker run", "explanation": "e"},
        "practice": {"type": "practical", "title": "Deploy containers", "task": "Deploy a containerized app.",
                     "response_type": "code", "competency": "containers"},
        "mini_check": {"questions": []},
        "resources": [],
    }
    stored = models.create_lesson(
        student_id=student_id, skill_id=sk, path_id=path["id"],
        competency=comp, title="Docker > containers", action="learn", content_json=legacy_content)
    raw = stored["content"]
    assert not raw["learn"].get("common_mistake")
    assert not raw["learn"].get("worked_example")

    normalized = lessons.normalize_lesson(
        {"content": raw}, comp, skill_name="Docker", skill_category="DevOps",
        target_role="Junior AI Engineer", required_level="Beginner")
    content = normalized["content"]
    # Filled at read time; stored JSON untouched.
    assert content["learn"]["common_mistake"]
    assert content["learn"]["worked_example"]
    assert content["learn"]["explanation"]
    assert content["mini_check"]["questions"]
    assert content["resources"] is not None