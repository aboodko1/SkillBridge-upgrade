"""WP-GO-03 — Grounding pass.

The Learn generation path must pass trusted catalog sources (excerpt + title +
catalog URL) into the LLM context so content is grounded, and resource links in
output must come only from curated catalog entries (never free-form LLM URLs).
Hallucinated URLs must be dropped. All provider calls are mocked — no network.
"""
import json

from app import genai, lessons


def _force_ai_path(monkeypatch):
    # Docker/containers has a canonical trusted-CS topic that short-circuits
    # generate_lesson before the AI/grounding path runs. Stub it out so these
    # tests exercise the LLM grounding merge exactly.
    monkeypatch.setattr(lessons.knowledge_base, "complete_lesson", lambda *a, **k: None)


def _fake_content(grounding_sources):
    return {
        "learn": {
            "title": "Containers",
            "explanation": "What containers are and why.",
            "key_ideas": ["i1", "i2"],
            "key_terms": {"c": "d"},
            "job_relevance": "A Junior AI Engineer runs containers for model deploys.",
            "common_mistake": "Assuming syntax is valid without checking.",
            "worked_example": "A practice walkthrough for the task to come.",
            "depth_note": "Weak: starts from fundamentals.",
            "grounding_sources": grounding_sources,
            "unsupported_claims": [],
        },
        "example": {"title": "Ex", "type": "code", "content": "docker run --rm app",
                    "explanation": "e"},
        "practice": {"type": "practical", "title": "Deploy containers",
                     "task": "Deploy a containerized app and verify it runs.",
                     "response_type": "code", "competency": "containers"},
        "mini_check": {"questions": [
            {"id": "m1", "type": "mcq", "question": "q?", "options": ["a", "b"],
             "correct_answer": "a", "competency": "containers", "difficulty": "beginner"}]},
    }


def test_grounding_context_carries_excerpt_title_url(monkeypatch):
    _force_ai_path(monkeypatch)
    trusted_source = {"title": "Docker Docs", "url": "https://docs.docker.com/net/",
                      "source": "Docker", "excerpt": "Networking reference for containers."}
    monkeypatch.setattr(lessons, "_grounding_sources",
                        lambda *a, **k: [trusted_source])
    captured = {}

    def fake_complete(system, user, **kwargs):
        captured["system"] = system
        captured["user"] = user
        return json.dumps(_fake_content([trusted_source]))

    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    monkeypatch.setattr(genai, "complete", fake_complete)
    lessons.generate_lesson(
        skill_name="Docker", competency="containers", action="learn",
        target_role="Junior AI Engineer")
    # The prompt must carry the trusted source context (excerpt + title + URL).
    assert "https://docs.docker.com/net/" in captured["user"]
    assert "Docker Docs" in captured["user"]
    assert "Networking reference for containers." in captured["user"]


def test_generated_resources_subset_of_catalog(monkeypatch):
    _force_ai_path(monkeypatch)
    trusted_source = {"title": "Docker Docs", "url": "https://docs.docker.com/net/",
                      "source": "Docker", "excerpt": "Networking reference for containers."}
    monkeypatch.setattr(lessons, "_grounding_sources",
                        lambda *a, **k: [trusted_source])
    monkeypatch.setattr(lessons, "_lesson_resources",
                        lambda *a, **k: [{"title": "Docker Docs",
                                          "url": "https://docs.docker.com/net/",
                                          "source": "Docker"}])

    def fake_complete(system, user, **kwargs):
        return json.dumps(_fake_content([trusted_source]))

    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    monkeypatch.setattr(genai, "complete", fake_complete)
    content = lessons.generate_lesson(
        skill_name="Docker", competency="containers", action="learn",
        target_role="Junior AI Engineer")
    # Resources must come only from the curated catalog entries.
    for res in content.get("resources") or []:
        assert res["url"] == "https://docs.docker.com/net/"


def test_hallucinated_url_is_dropped(monkeypatch):
    _force_ai_path(monkeypatch)
    trusted_source = {"title": "Docker Docs", "url": "https://docs.docker.com/net/",
                      "source": "Docker", "excerpt": "Networking reference for containers."}
    monkeypatch.setattr(lessons, "_grounding_sources",
                        lambda *a, **k: [trusted_source])

    def fake_complete(system, user, **kwargs):
        # Model invented a URL that is NOT in the trusted catalog.
        return json.dumps(_fake_content([
            trusted_source,
            {"title": "Bad link", "url": "https://nope.example.com", "source": "Unknown"},
        ]))

    monkeypatch.setattr(genai, "genai_enabled", lambda: True)
    monkeypatch.setattr(genai, "complete", fake_complete)
    content = lessons.generate_lesson(
        skill_name="Docker", competency="containers", action="learn",
        target_role="Junior AI Engineer")
    srcs = content["learn"]["grounding_sources"] or []
    # Hallucinated URL must be dropped; trusted URL must survive.
    assert all(s["url"] != "https://nope.example.com" for s in srcs)
    assert any(s["url"] == "https://docs.docker.com/net/" for s in srcs)


def test_fallback_path_unchanged_and_labelled(monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)
    content = lessons.generate_lesson(
        skill_name="Docker", competency="containers", action="learn",
        target_role="Junior AI Engineer")
    # Deterministic fallback still renders with a self_check and resources.
    assert content.get("self_check") is not None
    assert isinstance(content.get("resources"), list)