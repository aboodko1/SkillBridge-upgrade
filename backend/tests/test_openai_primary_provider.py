"""OpenAI primary provider (WP-GO-02).

The provider chain already prefers OpenAI when ``OPENAI_API_KEY`` is set:
``PROVIDER_PRIORITY = ("openai", "anthropic", "nvidia")`` and ``_generate``
builds candidates in that order, key-gated, then falls through to the
deterministic fallback (``complete(..., fallback=...)``). These tests lock in
that behavior with a mocked HTTP client — no network, no key required.
"""
import httpx

from app import genai, practice


def _fake_openai_response(content, *, status_code=200, malformed=False):
    class Response:
        def __init__(self):
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError(
                    "err", request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
                    response=httpx.Response(self.status_code, request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")),
                )

        def json(self):
            if malformed:
                return {"choices": []}
            return {"choices": [{"message": {"content": content}}]}

    return Response()


def _enable_openai(monkeypatch):
    monkeypatch.setattr(genai, "OPENAI_KEY", "test-openai-key")
    monkeypatch.setattr(genai, "ANTHROPIC_KEY", None)
    monkeypatch.setattr(genai, "NIM_KEY", None)


def _eval_context():
    return {
        "student": {"name": "Aisha"},
        "skill": {"name": "Docker"},
        "target_role": {"title": "Junior AI Engineer"},
        "required_level": "Intermediate",
        "topic": {"competency": "containers", "label": "Containers"},
        "diagnostic": {"score": 40},
        "lesson": {
            "learn": {"title": "Containers", "explanation": "What containers are and why.",
                      "key_ideas": ["isolation", "images"], "key_terms": {"container": "a"}},
            "example": {"title": "Ex", "type": "code", "content": "docker run --rm app",
                        "explanation": "e"},
            "practice": {"type": "practical", "title": "Deploy containers",
                         "task": "Deploy a containerized app.", "response_type": "code",
                         "competency": "containers"},
        },
        "previous_attempts": [],
    }


def test_provider_priority_places_openai_first():
    assert genai.PROVIDER_PRIORITY == ("openai", "anthropic", "nvidia")


def test_openai_is_preferred_when_key_set(monkeypatch):
    _enable_openai(monkeypatch)
    assert genai.genai_enabled() is True
    assert genai.provider_status()["preferred_provider"] == "openai"


def test_openai_success_returns_live_content(monkeypatch):
    _enable_openai(monkeypatch)
    calls = {}

    def fake_post(url, headers, json, timeout):
        calls.update({"url": url, "headers": headers, "json": json})
        return _fake_openai_response("live openai answer")

    monkeypatch.setattr(httpx, "post", fake_post)
    assert genai.complete("system", "user") == "live openai answer"
    assert calls["url"] == "https://api.openai.com/v1/chat/completions"
    assert calls["headers"]["Authorization"] == "Bearer test-openai-key"
    assert calls["json"]["model"] == genai.OPENAI_MODEL
    assert genai.provider_status()["last_active_provider"] == "openai"


def test_openai_success_eval_labels_source_ai(monkeypatch):
    _enable_openai(monkeypatch)
    eval_json = (
        '{"score": 85, "status": "ready", "strengths": ["covers volumes"], '
        '"missing_points": [], "feedback": "Good coverage.", '
        '"next_action": "Try the Mini Check", "source": "ai"}'
    )

    def fake_post(url, headers, json, timeout):
        return _fake_openai_response(eval_json)

    monkeypatch.setattr(httpx, "post", fake_post)
    result = practice.evaluate_practice(_eval_context(), "Use a named volume so data persists.")
    assert result["source"] == "ai"
    assert result["score"] == 85


def test_openai_key_unset_uses_deterministic_fallback(monkeypatch):
    monkeypatch.setattr(genai, "OPENAI_KEY", None)
    monkeypatch.setattr(genai, "ANTHROPIC_KEY", None)
    monkeypatch.setattr(genai, "NIM_KEY", None)
    assert genai.genai_enabled() is False
    assert genai.complete("system", "user", fallback="FALLBACK") == "FALLBACK"
    result = practice.evaluate_practice(_eval_context(), "A concrete practice answer.")
    assert result["source"] == "fallback"


def test_openai_provider_raises_uses_fallback(monkeypatch):
    _enable_openai(monkeypatch)

    def fake_post(url, headers, json, timeout):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", fake_post)
    assert genai.complete("system", "user", fallback="FALLBACK") == "FALLBACK"
    assert genai.provider_status()["last_success"] is False


def test_openai_malformed_response_uses_fallback(monkeypatch):
    _enable_openai(monkeypatch)

    def fake_post(url, headers, json, timeout):
        return _fake_openai_response(None, malformed=True)

    monkeypatch.setattr(httpx, "post", fake_post)
    assert genai.complete("system", "user", fallback="FALLBACK") == "FALLBACK"