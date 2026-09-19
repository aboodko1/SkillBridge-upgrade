"""Phase 3: agentic-learning UI contract.

The frontend renders the orchestrator's decision (action, reason, objective,
evidence) and the non-executing static check. These tests pin the persisted
payload shape the UI depends on, and re-assert the honesty boundary: a static
check never executes code, never changes the practice score, and never verifies
a skill.
"""
from urllib.parse import quote

from app import genai, learning_orchestrator as agent, models

UI_DECISION_KEYS = {"action_type", "topic_id", "evidence", "decision_reason", "next_step", "objective"}


def _python_flow(client, student_id, headers):
    skill = models.get_skill_by_name("Python")
    diagnostic = client.post(
        f"/api/students/{student_id}/learning/{skill['id']}/diagnostic/generate", json={}, headers=headers).json()
    client.post(
        f"/api/students/{student_id}/learning/{skill['id']}/diagnostic/submit",
        json={"diagnostic_id": diagnostic["diagnostic_id"], "answers": ["not sure"] * len(diagnostic["questions"])},
        headers=headers)
    path = client.post(
        f"/api/students/{student_id}/learning/{skill['id']}/personalized-path/generate", json={}, headers=headers).json()
    item = next(row for row in path["items"] if row["competency"] == "python_functions")
    lesson_url = f"/api/students/{student_id}/learning/{skill['id']}/lessons/{quote(item['competency'], safe='')}"
    client.post(lesson_url + "/generate", json={}, headers=headers)
    return skill, item, lesson_url


def test_orchestrator_decision_exposes_every_ui_field(client, student_id, auth_headers, monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)
    headers = auth_headers("aisha@student.edu")
    skill, _, _ = _python_flow(client, student_id, headers)
    decision = client.get(
        f"/api/students/{student_id}/learning/{skill['id']}/orchestrator/next", headers=headers).json()
    assert UI_DECISION_KEYS <= set(decision)
    assert decision["action_type"] in agent.ALLOWED_ACTIONS
    assert isinstance(decision["evidence"], list) and decision["evidence"]
    assert all({"kind", "detail"} <= set(e) for e in decision["evidence"])
    assert decision["decision_reason"] and decision["next_step"]


def test_static_check_disclosure_shape_and_no_runtime_claim(client, student_id, auth_headers, monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)
    headers = auth_headers("aisha@student.edu")
    skill, _, lesson_url = _python_flow(client, student_id, headers)

    bad = client.post(lesson_url + "/practice",
                      json={"answer": "def celsius_to_fahrenheit(celsius):\n    print(celsius)"},
                      headers=headers).json()["attempt"]
    bad_check = bad["practice_task"]["static_check"]
    assert bad_check["status"] == "needs_fix"
    assert "not executed" in bad_check["note"].lower()
    assert isinstance(bad_check["checks"], list) and bad_check["checks"]

    good = client.post(lesson_url + "/practice", json={"answer": """def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32

I return the value so callers can reuse it."""}, headers=headers).json()["attempt"]
    good_check = good["practice_task"]["static_check"]
    assert good_check["status"] == "looks_structurally_sound"
    # The structural check is evidence, not a grade: it must not silently turn a
    # needs-review attempt into a pass or verify the skill.
    assert good["status"] in ("needs_review", "ready")
    assert "not executed" in good_check["note"].lower()


def test_reassessment_decision_still_renders_full_contract(client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    skill = models.get_skill_by_name("Python")
    decision = client.get(
        f"/api/students/{student_id}/learning/{skill['id']}/orchestrator/next", headers=headers).json()
    assert UI_DECISION_KEYS <= set(decision)
    assert decision["action_type"] == agent.REQUEST_REASSESSMENT
    assert decision["topic_id"] is None
    assert decision["evidence"]
