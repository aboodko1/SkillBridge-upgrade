"""End-to-end contracts for the curated Docker topics (batch 4: multi-stage builds, security & secrets, orchestration basics)."""
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


BATCH4 = {"multi-stage_builds", "security_&_secrets", "orchestration_basics"}


def test_curated_docker_batch4_topics_complete_without_verifying_skill(
        client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    docker = models.get_skill_by_name("Docker")
    before = {(s["name"], s["level"]) for s in models.get_student(student_id).get("verified_skills") or []}
    _, path = _make_path(client, student_id, headers, docker)
    answers = {
        "multi-stage_builds": (
            "Dockerfile:\n"
            "# build stage\n"
            "FROM node:20 AS builder\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm install\n"
            "COPY . .\n"
            "RUN npm run build\n"
            "\n"
            "# runtime stage\n"
            "FROM node:20-alpine\n"
            "RUN addgroup -S appgroup && adduser -S appuser -G appgroup\n"
            "WORKDIR /app\n"
            "COPY --from=builder /app/dist ./dist\n"
            "COPY --from=builder /app/node_modules ./node_modules\n"
            "COPY package.json .\n"
            "USER appuser\n"
            "CMD [\"node\", \"dist/server.js\"]\n\n"
            "docker build -t myapp:1.0 .\n"
            "docker run -d --name myapp -p 3000:3000 myapp:1.0\n"
            "The build stage installs dev tools and builds; the runtime stage keeps only the built output."
        ),
        "security_&_secrets": (
            "The Dockerfile should not copy .env because the secret becomes part of the image history.\n"
            "Dockerfile:\n"
            "FROM node:20-alpine\n"
            "RUN addgroup -S appgroup && adduser -S appuser -G appgroup\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm install --omit=dev\n"
            "COPY . .\n"
            "USER appuser\n"
            "EXPOSE 3000\n"
            "CMD [\"node\", \"server.js\"]\n\n"
            "docker run -d --name api -e DATABASE_URL=REPLACE_AT_RUNTIME -p 3000:3000 myapi:1.0\n"
            "Pass the secret at runtime so it is not baked into the image."
        ),
        "orchestration_basics": (
            "Docker Compose is for single-host development. For production with 3 replicas, self-healing, "
            "and zero-downtime updates, use an orchestrator such as Docker Swarm or Kubernetes.\n"
            "docker swarm init\n"
            "docker service create --name api --replicas 3 -p 8080:3000 myapi:1.0\n"
            "docker service ls\n"
            "docker service scale api=3\n"
            "Swarm maintains the desired replica count and replaces failed tasks."
        ),
    }
    for item in path["items"]:
        if item["competency"] not in BATCH4:
            continue
        base = _url(student_id, docker["id"], item["competency"])
        lesson = client.post(base + "/generate", json={}, headers=headers)
        assert lesson.status_code == 200, lesson.text
        content = lesson.json()["content"]
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        assert len(content["locales"]["ar"]["mini_check"]["questions"]) == 3
        assert content["practice"]["type"] == "practical"

        expected_response_type = "command" if item["competency"] == "orchestration_basics" else "configuration"
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
    batch4_item_ids = {item["id"] for item in path["items"] if item["competency"] in BATCH4}
    assert batch4_item_ids.issubset(set(persisted["progress"]))
    assert {(s["name"], s["level"]) for s in models.get_student(student_id).get("verified_skills") or []} == before


def test_curated_docker_batch4_content_has_bilingual_explanation_and_validated_checks():
    """Each batch-4 topic loads with EN/AR, objectives, prereqs, worked example, practical exercise, Mini Check."""
    from app import lessons, knowledge_base

    for competency in ("Multi-stage builds", "Security & secrets", "Orchestration basics"):
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
        assert content["canonical"]["prerequisites"] == []


def test_curated_docker_batch4_prerequisites_exist_in_blueprint():
    """Any prerequisite topic_id referenced by batch 4 topics exists in the blueprint."""
    from app import knowledge_base, skill_blueprint as sb

    docker_topics = sb.required_competencies("Docker", "Beginner", "Advanced")
    for competency in ("Multi-stage builds", "Security & secrets", "Orchestration basics"):
        topic = knowledge_base.complete_lesson("Docker", competency)
        assert topic is not None, competency
        for prereq in topic["prerequisites"]:
            assert prereq["competency"] in docker_topics, prereq["competency"]


def test_curated_docker_batch4_resource_links_are_curated_and_safe():
    """Recommended resources for batch 4 topics come from the curated docker catalog (docs.docker.com)."""
    from app import resources

    expected_min = {"Multi-stage builds": 2, "Security & secrets": 2, "Orchestration basics": 2}
    for competency in ("Multi-stage builds", "Security & secrets", "Orchestration basics"):
        res = resources.recommend_lesson_resources(
            "Docker", "DevOps", competency, "Beginner", "Junior AI Engineer", live_check=False)
        assert len(res) >= expected_min[competency], f"{competency}: expected >= {expected_min[competency]}, got {len(res)}"
        assert all(r["source_kind"] == "curated" for r in res[:expected_min[competency]])
        assert all("docs.docker.com" in r["url"] for r in res[:expected_min[competency]])


def test_all_docker_blueprint_topics_are_curated():
    """After Batch 4, every Docker blueprint competency has a canonical lesson."""
    from app import knowledge_base, skill_blueprint as sb

    competencies = sb.required_competencies("Docker", "Beginner", "Advanced")
    for comp in competencies:
        assert knowledge_base.complete_lesson("Docker", comp) is not None, comp
