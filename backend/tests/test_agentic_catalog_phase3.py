"""WP-GO-06 — 9 Agentic AI topics in the curated catalog.

Each competency must load through the diagnostic -> learn -> practice -> mini
check pipeline, carry English + Arabic content, 2-3 curated resources whose
URLs pass the safety validator, and mini-check items (>=70% threshold) that are
independent of any Practice score. No existing topic is changed.
"""
from app import diagnostics as dx
from app import knowledge_base as kb
from app import resources
from app import skill_blueprint as sb

AGENTIC_COMPETENCIES = [
    "Tool Use & Function Calling",
    "Model Context Protocol (MCP)",
    "Retrieval-Augmented Generation (RAG)",
    "Multi-Agent Systems",
    "Agent Memory",
    "Planning & Task Decomposition",
    "Agent Evaluation & Guardrails",
    "Context Engineering",
    "Agent Security & Prompt Injection",
]


def test_all_nine_competencies_resolve_through_diagnostic():
    topics = dx.resolve_topics("Agentic AI")
    assert set(topics) == set(AGENTIC_COMPETENCIES)


def test_all_nine_load_canonical_content():
    for comp in AGENTIC_COMPETENCIES:
        topic = kb.complete_lesson("Agentic AI", comp)
        assert topic is not None, comp
        assert topic["status"] == "complete"
        assert topic["competency"] == comp


def test_each_has_english_and_arabic_content():
    for comp in AGENTIC_COMPETENCIES:
        topic = kb.complete_lesson("Agentic AI", comp)
        learn = topic["learn"]
        assert learn["explanation"], comp
        assert learn["key_ideas"], comp
        assert learn["common_mistake"], comp
        assert "ar" in topic["locales"], comp
        ar_learn = topic["locales"]["ar"]["learn"]
        assert ar_learn["explanation"], comp
        assert ar_learn["key_ideas"], comp
        assert topic["locales"]["ar"].get("mini_check", {}).get("questions"), comp


def test_each_has_practice_and_mini_check():
    for comp in AGENTIC_COMPETENCIES:
        topic = kb.complete_lesson("Agentic AI", comp)
        assert topic["practice"]["task"], comp
        assert topic["practice"]["type"] == "practical", comp
        questions = topic["mini_check"]["questions"]
        assert len(questions) >= 3, comp
        for q in questions:
            assert q["correct_answer"], comp
            assert q["options"], comp
            assert q["misconception_hint"], comp


def test_all_resource_urls_pass_the_safety_validator():
    for comp in AGENTIC_COMPETENCIES:
        topic = kb.complete_lesson("Agentic AI", comp)
        sources = topic["learn"]["grounding_sources"]
        assert 2 <= len(sources) <= 3, comp
        for s in sources:
            assert resources.is_safe_public_url(s["url"]), (comp, s["url"])


def test_existing_docker_topics_unchanged():
    docker = kb.complete_lesson("Docker", "Multi-stage builds")
    assert docker is not None
    assert docker["competency"] == "Multi-stage builds"
    # The agentic additions must not disturb an existing curated topic.
    assert "ar" in docker["locales"]


def test_mini_check_threshold_is_seventy_percent_independent_of_practice():
    # Mini Check scoring uses its own pass threshold (>=0.7) and its own items;
    # a Practice score is never reused. Assert each topic has distinct items.
    from app import lessons
    assert lessons.MINI_CHECK_PASS_THRESHOLD == 0.7
    for comp in AGENTIC_COMPETENCIES:
        topic = kb.complete_lesson("Agentic AI", comp)
        mini_ids = [q["id"] for q in topic["mini_check"]["questions"]]
        practice_ids = [q.get("id") for q in topic["practice"].get("questions", [])]
        assert mini_ids, comp
        # Practice questions (if any) and mini-check questions are separate items.
        assert not (set(mini_ids) & set(practice_ids)), comp


def test_agentic_skill_has_trusted_blueprint():
    assert sb.has_blueprint("Agentic AI")
    comps = sb.required_competencies("Agentic AI", "Beginner", "Advanced")
    assert set(comps) == set(AGENTIC_COMPETENCIES)