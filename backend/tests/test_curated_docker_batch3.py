"""End-to-end contracts for the curated Docker topics (batch 3: Volumes, Networking, Compose)."""
from urllib.parse import quote

import pytest

from app import genai, models


@pytest.fixture(autouse=True)
def offline_reviewer(monkeypatch):
    """Use the explicitly labelled local evaluator for deterministic journeys."""
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)


def _url(student_id, skill_id, competency):
    return f"/api/students/{student_id}/learning/{skill_id}/lessons/{quote(competency, safe='')}"


def _answers_for_all_gaps(questions):
    """Return a wrong answer for each question (MCQ or free-text)."""
    answers = []
    for q in questions:
        opts = q.get("options") or []
        if opts:
            wrong = next(opt for opt in opts if opt != q["correct_answer"])
            answers.append(wrong)
        else:
            answers.append("WRONG ANSWER")
    return answers


def _make_path(client, student_id, headers, docker_skill):
    generated = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/diagnostic/generate",
        json={}, headers=headers).json()
    completed = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/diagnostic/submit",
        json={"diagnostic_id": generated["diagnostic_id"], "answers": _answers_for_all_gaps(generated["questions"])},
        headers=headers)
    assert completed.status_code == 200, completed.text
    path = client.post(
        f"/api/students/{student_id}/learning/{docker_skill['id']}/personalized-path/generate",
        json={}, headers=headers).json()
    return generated, path


BATCH3 = {"volumes", "networking", "compose"}


def test_curated_docker_batch3_topics_complete_without_verifying_skill(
        client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    docker = models.get_skill_by_name("Docker")
    before = {(s["name"], s["level"]) for s in models.get_student(student_id).get("verified_skills") or []}
    _, path = _make_path(client, student_id, headers, docker)
    answers = {
        "volumes": (
            "docker volume create pgdata\n"
            "docker run -d --name db -v pgdata:/var/lib/postgresql/data "
            "-e POSTGRES_PASSWORD=secret postgres:16\n"
            "docker volume ls\n"
            "docker volume inspect pgdata\n"
            "docker ps\n"
            "docker rm db\n"
            "docker run -d --name db2 -v pgdata:/var/lib/postgresql/data "
            "-e POSTGRES_PASSWORD=secret postgres:16\n"
            "docker exec db2 psql -U postgres -c '\\l'\n"
            "The same volume is mounted into db2, so the previous databases are still present."
        ),
        "networking": (
            "docker network create appnet\n"
            "docker run -d --name db --network appnet -e POSTGRES_PASSWORD=secret postgres:16\n"
            "docker run -d --name api --network appnet -p 8080:3000 myapi:1.0\n"
            "The api container connects to postgres://db:5432/mydb because db resolves by DNS.\n"
            "docker network inspect appnet\n"
            "The inspect output shows both db and api in the Containers section."
        ),
        "compose": (
            "docker-compose.yml:\n"
            "version: \"3.8\"\n"
            "services:\n"
            "  db:\n"
            "    image: postgres:16\n"
            "    environment:\n"
            "      POSTGRES_PASSWORD: secret\n"
            "    volumes:\n"
            "      - pgdata:/var/lib/postgresql/data\n"
            "  api:\n"
            "    image: myapi:1.0\n"
            "    ports:\n"
            "      - \"8080:3000\"\n"
            "    depends_on:\n"
            "      - db\n"
            "volumes:\n"
            "  pgdata:\n\n"
            "docker compose up -d\n"
            "docker compose logs\n"
            "docker compose down --volumes\n"
            "depends_on controls start order only; the api must still retry until db accepts connections."
        ),
    }
    for item in path["items"]:
        if item["competency"] not in BATCH3:
            continue
        base = _url(student_id, docker["id"], item["competency"])
        lesson = client.post(base + "/generate", json={}, headers=headers)
        assert lesson.status_code == 200, lesson.text
        content = lesson.json()["content"]
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        assert len(content["locales"]["ar"]["mini_check"]["questions"]) == 3
        assert content["practice"]["type"] == "practical"

        expected_response_type = "configuration" if item["competency"] == "compose" else "command"
        assert content["practice"]["response_type"] == expected_response_type

        first = client.post(base + "/practice", json={"answer": answers[item["competency"]]}, headers=headers)
        assert first.status_code == 200, first.text
        attempt = first.json()["attempt"]
        assert attempt["status"] in ("ready", "needs_review")
        assert isinstance(attempt["score"], (int, float))

        cached = client.post(base + "/practice", json={"answer": answers[item["competency"]]}, headers=headers)
        assert cached.status_code == 200, cached.text
        assert cached.json()["reused"] is True
        assert cached.json()["attempt"]["id"] == first.json()["attempt"]["id"]

        changed = client.post(base + "/practice", json={"answer": answers[item["competency"]] + "\nI checked one more case."}, headers=headers)
        assert changed.status_code == 200, changed.text
        assert changed.json().get("reused") is not True

        questions = content["mini_check"]["questions"]
        passed = client.post(base + "/mini-check", json={"answers": [q["correct_answer"] for q in questions]}, headers=headers)
        assert passed.status_code == 200, passed.text
        assert passed.json()["lesson"]["state"] == "completed"

    persisted = client.get(f"/api/students/{student_id}/learning/{docker['id']}/personalized-path", headers=headers).json()
    batch3_item_ids = {item["id"] for item in path["items"] if item["competency"] in BATCH3}
    assert batch3_item_ids.issubset(set(persisted["progress"]))
    assert {(s["name"], s["level"]) for s in models.get_student(student_id).get("verified_skills") or []} == before


def test_curated_docker_batch3_content_has_bilingual_explanation_and_validated_checks():
    """Each batch-3 topic loads with EN/AR, objectives, prereqs, worked example, practical exercise, Mini Check."""
    from app import lessons, knowledge_base

    expected = {
        "Volumes": {"prerequisites": []},
        "Networking": {"prerequisites": []},
        "Compose": {"prerequisites": []},
    }
    for competency in expected:
        content = lessons.generate_lesson("Docker", competency, "learn")
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        assert "بالعربية" not in content["learn"]["explanation"]
        arabic = content["locales"]["ar"]
        assert arabic["learn"]["explanation"]
        assert arabic["learn"]["key_ideas"]
        assert arabic["example"]["content"]
        assert arabic["practice"]["task"]
        assert arabic["practice"]["evaluation_note"]
        assert len(arabic["mini_check"]["questions"]) == 3

        answers = [q["correct_answer"] for q in content["mini_check"]["questions"]]
        from app import lessons as lessons_mod
        assert lessons_mod.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)

        assert content["practice"]["type"] == "practical"
        assert content["practice"]["task"]
        assert content["practice"]["evaluation_note"]
        assert content["example"]["content"]
        assert content["learn"]["grounding_sources"]

        canonical = content["canonical"]
        actual_prereqs = [p["competency"] for p in canonical["prerequisites"]]
        assert actual_prereqs == expected[competency]["prerequisites"]


def test_curated_docker_batch3_prerequisites_exist_in_blueprint():
    """Any prerequisite topic_id referenced by batch 3 topics exists in the blueprint."""
    from app import knowledge_base, skill_blueprint as sb

    docker_topics = sb.required_competencies("Docker", "Beginner", "Advanced")
    for competency in ("Volumes", "Networking", "Compose"):
        topic = knowledge_base.complete_lesson("Docker", competency)
        assert topic is not None, competency
        for prereq in topic["prerequisites"]:
            assert prereq["competency"] in docker_topics, prereq["competency"]


def test_curated_docker_batch3_resource_links_are_curated_and_safe():
    """Recommended resources for batch 3 topics come from the curated docker catalog (docs.docker.com)."""
    from app import resources

    expected_min = {"Volumes": 2, "Networking": 2, "Compose": 2}
    for competency in ("Volumes", "Networking", "Compose"):
        res = resources.recommend_lesson_resources(
            "Docker", "DevOps", competency, "Beginner", "Junior AI Engineer", live_check=False)
        assert len(res) >= expected_min[competency], f"{competency}: expected >= {expected_min[competency]}, got {len(res)}"
        assert all(r["source_kind"] == "curated" for r in res[:expected_min[competency]])
        assert all("docs.docker.com" in r["url"] for r in res[:expected_min[competency]])
