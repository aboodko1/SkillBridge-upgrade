"""Agentic roadmap validation tests.

All LLM calls are mocked — no network, no key. Covers:
  1. validate returns a coverage score in [0,1]
  2. validate handles malformed LLM JSON without crashing
  3. apply_corrections only uses failed checks
  4. unknown role id returns an error dict, no exception
"""
import asyncio
import json

import pytest

from app import genai
from app.agent import reviser, validator

DRAFT = "## Phase 1: Foundations\nLearn Python and networking basics.\n\n## Phase 2: Operations\nQuery a SIEM, triage alerts, write reports."
CV = "3 years as helpdesk. Knows Python and basic networking."


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _force_provider(monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: True)


def _mock_complete(monkeypatch, payload):
    def fake(*args, **kwargs):
        return json.dumps(payload)
    monkeypatch.setattr(genai, "complete", fake)


def test_validate_returns_coverage_score(monkeypatch):
    payload = [
        {"check_name": "FRAMEWORK_COVERAGE", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "PREREQUISITE_ORDER", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "CV_REDUNDANCY", "passed": False, "evidence": "teaches Python already on CV", "suggested_fix": "Skip Python basics"},
        {"check_name": "RECENCY", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "HALLUCINATION", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "LEVEL_APPROPRIATENESS", "passed": True, "evidence": "ok", "suggested_fix": ""},
    ]
    _mock_complete(monkeypatch, payload)
    result = _run(validator.validate_roadmap(DRAFT, CV, "soc_analyst"))
    assert "coverage_score" in result
    assert 0.0 <= result["coverage_score"] <= 1.0
    assert 0.0 <= result["personalization_score"] <= 1.0
    assert result["source"] == "live"
    assert len(result["violations"]) == 6
    assert result["sources"] == ["NIST NICE v2.1 work role 511", "MITRE ATT&CK Enterprise"]


def test_validate_handles_malformed_llm_json(monkeypatch):
    # Malformed on first attempt, valid on the retry.
    calls = {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return "not json at all {{"
        return json.dumps([
            {"check_name": "FRAMEWORK_COVERAGE", "passed": True, "evidence": "ok", "suggested_fix": ""},
        ])

    monkeypatch.setattr(genai, "complete", flaky)
    result = _run(validator.validate_roadmap(DRAFT, CV, "soc_analyst"))
    assert "coverage_score" in result
    assert calls["n"] == 2  # exactly one retry after the malformed response


def test_validate_returns_error_on_persistent_malformed(monkeypatch):
    monkeypatch.setattr(genai, "complete", lambda *a, **k: "still not json")
    result = _run(validator.validate_roadmap(DRAFT, CV, "soc_analyst"))
    # Malformed output now falls through to the deterministic fallback rather
    # than surfacing {"error": "validation_failed"}.
    assert result.get("source") == "fallback"
    assert isinstance(result.get("coverage_score"), float)
    assert "warning" in result


def test_validator_falls_back_on_llm_failure(monkeypatch):
    """A raising LLM provider must not surface an error; it falls back to the
    deterministic rule check and labels the result 'fallback'."""
    calls = {"n": 0}

    def boom(*args, **kwargs):
        calls["n"] += 1
        raise RuntimeError("provider down")

    monkeypatch.setattr(genai, "complete", boom)
    result = _run(validator.validate_roadmap(DRAFT, CV, "soc_analyst"))
    assert calls["n"] == 2  # one retry, then fallback
    assert result.get("source") == "fallback"
    assert isinstance(result.get("coverage_score"), float)
    assert isinstance(result.get("personalization_score"), float)
    assert isinstance(result.get("violations"), list)
    assert "LLM unavailable" in (result.get("warning") or "")


def test_apply_corrections_only_uses_failed_checks(monkeypatch):
    violations = [
        {"check_name": "FRAMEWORK_COVERAGE", "passed": False, "evidence": "missing log analysis", "suggested_fix": "Add Log Analysis Basics"},
        {"check_name": "RECENCY", "passed": True, "evidence": "ok", "suggested_fix": "should be ignored"},
        {"check_name": "HALLUCINATION", "passed": False, "evidence": "fake cert", "suggested_fix": "Remove fake cert"},
    ]

    captured = {}
    def fake_complete(system, user, **kwargs):
        captured["user"] = user
        # Echo the draft back unchanged (the test asserts prompt content only).
        return DRAFT

    monkeypatch.setattr(genai, "complete", fake_complete)
    result = _run(reviser.apply_corrections(DRAFT, violations))
    assert isinstance(result, str)
    prompt = captured["user"]
    # The failed checks' fixes are in the prompt; the passed check's fix is not.
    assert "Add Log Analysis Basics" in prompt
    assert "Remove fake cert" in prompt
    assert "should be ignored" not in prompt


def test_role_id_missing_ground_truth(monkeypatch):
    result = _run(validator.validate_roadmap(DRAFT, CV, "does_not_exist"))
    assert result.get("error") == "role_not_found"


def test_frontend_cv_flows_into_validator(monkeypatch):
    """A non-empty CV body reaches the validator and raises personalization.

    The CV demonstrates Python, so the validator must NOT flag a CV_REDUNDANCY
    violation for Python (and personalization_score must be > 0).
    """
    payload = [
        {"check_name": "FRAMEWORK_COVERAGE", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "PREREQUISITE_ORDER", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "CV_REDUNDANCY", "passed": True, "evidence": "Python already demonstrated", "suggested_fix": ""},
        {"check_name": "RECENCY", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "HALLUCINATION", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "LEVEL_APPROPRIATENESS", "passed": True, "evidence": "ok", "suggested_fix": ""},
    ]

    captured = {}
    def fake_complete(system, user, **kwargs):
        captured["user"] = user
        return json.dumps(payload)

    monkeypatch.setattr(genai, "complete", fake_complete)
    cv_text = "Built a Python SQLi detector tool. Three Java projects. Peer teaching."
    result = _run(validator.validate_roadmap(DRAFT, cv_text, "soc_analyst"))
    assert "coverage_score" in result
    assert 0.0 < result["personalization_score"] <= 1.0
    # The CV body actually reached the prompt.
    assert "Python SQLi detector" in captured["user"]
    # No CV_REDUNDANCY failure remains (Python is demonstrated).
    redundancy = [v for v in result["violations"] if v["check_name"] == "CV_REDUNDANCY"]
    assert not redundancy or all(v["passed"] for v in redundancy)


def test_parse_llm_json_handles_markdown_fence():
    raw = '```json\n[{"check_name": "FRAMEWORK_COVERAGE", "passed": false, "evidence": "x", "suggested_fix": "y"}]\n```'
    out = validator._parse_llm_json(raw)
    assert out[0]["check_name"] == "FRAMEWORK_COVERAGE"
    assert out[0]["passed"] is False
    # Prose after the fence is ignored too.
    raw2 = "Here is the result:\n```json\n[{\"check_name\": \"RECENCY\", \"passed\": true}]\n```\nLet me know if you need more."
    out2 = validator._parse_llm_json(raw2)
    assert out2[0]["check_name"] == "RECENCY"
    assert out2[0]["passed"] is True


def test_parse_llm_json_handles_trailing_comma():
    raw = '[{"check_name": "HALLUCINATION", "passed": true,},]'
    out = validator._parse_llm_json(raw)
    assert out[0]["check_name"] == "HALLUCINATION"
    assert out[0]["passed"] is True
    # Nested trailing comma inside the object is tolerated too.
    raw2 = '[{"check_name": "RECENCY", "evidence": "ok",}, {"check_name": "RECENCY", "evidence": "ok2",}]'
    out2 = validator._parse_llm_json(raw2)
    assert len(out2) == 2


def test_fallback_personalization_matches_live_on_bad_draft(monkeypatch):
    """A draft that re-teaches a demonstrated skill gets the same
    personalization_score from the deterministic fallback as from the live
    LLM path — both must be 0.0 when CV_REDUNDANCY and LEVEL_APPROPRIATENESS
    fail."""
    bad_draft = ("## Phase 1: Foundations\nLearn Python basics and beginner networking.\n"
                 "\n## Phase 2: Operations\nQuery a SIEM, triage alerts.")
    cv = "Knows Python and networking from 3 years in a NOC."

    # Live path: mock the LLM to fail the CV checks (the exact scenario the
    # fallback should reproduce).
    live_payload = [
        {"check_name": "FRAMEWORK_COVERAGE", "passed": False, "evidence": "missing", "suggested_fix": "add"},
        {"check_name": "PREREQUISITE_ORDER", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "CV_REDUNDANCY", "passed": False, "evidence": "teaches Python already on CV", "suggested_fix": "Skip Python basics"},
        {"check_name": "RECENCY", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "HALLUCINATION", "passed": True, "evidence": "ok", "suggested_fix": ""},
        {"check_name": "LEVEL_APPROPRIATENESS", "passed": False, "evidence": "beginner Python despite CV", "suggested_fix": "raise level"},
    ]
    _mock_complete(monkeypatch, live_payload)
    live = _run(validator.validate_roadmap(bad_draft, cv, "soc_analyst"))

    # Fallback path: provider disabled.
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)
    fallback = _run(validator.validate_roadmap(bad_draft, cv, "soc_analyst"))

    assert live["source"] == "live"
    assert fallback["source"] == "fallback"
    assert fallback["personalization_score"] == live["personalization_score"] == 0.0
    # The fallback also emitted CV_REDUNDANCY and LEVEL_APPROPRIATENESS failures.
    fb_checks = {v["check_name"] for v in fallback["violations"]}
    assert "CV_REDUNDANCY" in fb_checks
    assert "LEVEL_APPROPRIATENESS" in fb_checks