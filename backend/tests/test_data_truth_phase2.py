"""Phase 2 — data truth, match consistency and trust language.

Locks the guide's Phase 2 acceptance criteria:

- one metric has one name/formula/value across pages (canonical registry);
- a visible gap prevents any "complete requirement coverage" claim, so the
  Junior AI Engineer case can no longer show 100% while Docker is a level gap;
- name-only catalogue similarity is a distinct, non-competence metric;
- verified-evidence coverage counts only passed Final Assessments;
- a stale path is labelled and cannot satisfy Final Assessment readiness;
- no education/profile statement is treated as proven competence;
- trust language holds in English and Arabic.
"""
from urllib.parse import quote

from app import career_roadmap, coverage, genai, matching, metrics, models


# --------------------------------------------------------------------------
# canonical metrics
# --------------------------------------------------------------------------

def test_canonical_registry_has_one_definition_per_metric():
    defs = metrics.definitions()
    assert set(defs) == set(metrics.CANONICAL_METRICS)
    for key, d in defs.items():
        assert d["key"] == key
        assert d["label"] and d["short_label"]
        assert d["formula"] and d["evidence"] and d["rounding"]


def test_metric_definitions_endpoint_returns_registry(client, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = client.get("/api/metrics/definitions", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body["canonical"]) == set(metrics.CANONICAL_METRICS)
    assert body["metrics"][metrics.TARGET_REQUIREMENT_COVERAGE]["label"] == \
        "Target requirement coverage"


def test_analysis_exposes_canonical_metrics(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = client.get(f"/api/students/{student_id}/analysis", headers=h)
    assert r.status_code == 200, r.text
    a = r.json()
    assert a["match_score"] == a["metrics"][metrics.TARGET_REQUIREMENT_COVERAGE]
    assert set(a["metrics"]) == {
        metrics.TARGET_REQUIREMENT_COVERAGE,
        metrics.CAREER_READINESS,
        metrics.VERIFIED_EVIDENCE_COVERAGE,
    }
    assert set(a["metric_definitions"]) == set(metrics.CANONICAL_METRICS)


def test_visible_gap_blocks_complete_coverage_claim(student_id, db):
    a = matching.analyze_student(student_id)
    assert a is not None
    gaps = [g for g in a["skill_gaps"] if g["status"] != "strong"]
    assert gaps, "the seed student must have an open requirement for this contract"
    assert a["metrics"][metrics.TARGET_REQUIREMENT_COVERAGE] < 100.0
    assert a["metrics"][metrics.CAREER_READINESS] < 100.0
    assert a["all_requirements_met"] is False
    assert a["missing_requirements"]


def test_catalogue_similarity_is_name_only_and_never_complete(student_id, db):
    """The Junior AI Engineer contradiction: Docker is present by name but below
    the required level, so name overlap reads 100% while real coverage does not."""
    student = models.get_student(student_id)
    role = student["target_role"]
    names = ([s["name"] for s in student["self_reported_skills"]]
             + [v["name"] for v in student["verified_skills"]])
    assert "Docker" in names
    sim = metrics.catalogue_similarity(role, names)
    cov = metrics.target_requirement_coverage(student, role)
    assert sim > cov
    assert cov < 100.0
    assert metrics.all_requirements_met(student, role) is False


def test_verified_evidence_coverage_only_counts_passed_assessments(student_id, db):
    db.execute("DELETE FROM verified_skills WHERE student_id=?", (student_id,))
    db.commit()
    student = models.get_student(student_id)
    role = student["target_role"]
    assert student["self_reported_skills"], "self-reported evidence must exist"
    assert metrics.verified_evidence_coverage(student, role) == 0.0

    docker = models.get_skill_by_name("Docker")
    models.update_verified_skill(student_id, docker["id"], "Intermediate")
    student = models.get_student(student_id)
    total = len(role["required_skills"])
    assert metrics.verified_evidence_coverage(student, role) == round(100.0 / total, 1)


def test_frontend_does_not_recompute_match_from_raw_counts():
    """Source contract: the target-role number must come from the backend metric."""
    from contract_paths import WORKSPACE_ROOT
    src = (WORKSPACE_ROOT / "frontend/src/pages/SkillsRolesPage.tsx").read_text()
    assert "analysis?.metrics?.target_requirement_coverage" in src
    assert "metrics?.target_requirement_coverage" in \
        (WORKSPACE_ROOT / "frontend/src/pages/LearningPage.tsx").read_text()


# --------------------------------------------------------------------------
# stale path must never satisfy readiness
# --------------------------------------------------------------------------

def _completed_diagnostic(student_id, python, slugs):
    questions = [{"idn": i, "competency": slug, "type": "mcq",
                  "question": f"q{i}", "options": ["a", "b"], "correct_answer": "a"}
                 for i, slug in enumerate(slugs)]
    diag = models.create_diagnostic(student_id, python["id"], questions)
    topics = [{"competency": slug, "label": slug.replace("_", " "),
               "score": 0.0, "status": "weak", "correct": 0, "total": 1}
              for slug in slugs]
    return models.complete_diagnostic(diag["id"], [], 0.0, {
        "overall_score": 0.0, "topics": topics,
        "weak_topics": list(slugs), "strong_topics": []})


def _path_items(slugs):
    return [{"id": f"{slug}-{i}", "competency": slug, "title": slug.replace("_", " "),
             "topic_status": "weak", "diagnostic_score": 0.0, "action": "learn",
             "order": i, "estimated_minutes": 30, "state": "not_started"}
            for i, slug in enumerate(slugs, start=1)]


def test_stale_path_is_labelled_and_cannot_satisfy_readiness(
        client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    python = models.get_skill_by_name("Python")
    slugs = ["python_functions", "python_error_handling", "python_data_structures"]

    older = _completed_diagnostic(student_id, python, slugs)
    items = _path_items(slugs)
    models.create_personalized_path(student_id, python["id"], older["id"],
                                    "Intermediate", items, [], [])
    # Mark every path item complete — without the stale guard this would make the
    # Final Assessment "ready".
    models.update_path_progress(student_id, python["id"],
                                [it["id"] for it in items])

    before = client.get(
        f"/api/students/{student_id}/learning/{python['id']}/final-assessment/status",
        headers=h).json()
    assert before["path_stale"] is False
    assert before["readiness"]["ready"] is True

    # A newer completed diagnostic supersedes the path.
    newer = _completed_diagnostic(student_id, python, slugs)
    assert newer["id"] > older["id"]

    after = client.get(
        f"/api/students/{student_id}/learning/{python['id']}/final-assessment/status",
        headers=h).json()
    assert after["path_stale"] is True
    assert after["latest_diagnostic_id"] == newer["id"]
    # Stale path evidence is excluded: nothing is satisfied from the old path.
    assert after["readiness"]["satisfied"] == []
    assert after["readiness"]["ready"] is False

    # The stale path itself is labelled through the public path payload too.
    path = client.get(
        f"/api/students/{student_id}/learning/{python['id']}/personalized-path",
        headers=h).json()
    assert path["stale"] is True
    assert path["latest_diagnostic_id"] == newer["id"]


# --------------------------------------------------------------------------
# unsupported competence claims
# --------------------------------------------------------------------------

def test_roadmap_checkpoint_is_conditional_not_a_past_tense_claim(student_id, db):
    student = models.get_student(student_id)
    role = student["target_role"]
    roadmap = career_roadmap.build_career_roadmap(student, role)
    checkpoints = " ".join(p["checkpoint"] for p in roadmap["phases"])
    assert "You have passed the role's skill assessments" not in checkpoints
    assert "Once you pass the role's Final Assessments" in checkpoints
    assert "from zero to a job-ready" not in roadmap["summary"]


def test_education_is_never_treated_as_proven_competence(monkeypatch):
    """A profile with only education (no skills) must not yield a proficiency claim."""
    student_context = (
        "Student: Layla\nUniversity: Cairo University\nEducation level: BSc Computer Science\n"
        "Self-reported skills: (none)\nVerified skills: (none)\n"
    )
    for lang in ("en", "ar"):
        reply = genai._verified_skills_fallback("nova", lang, student_context)
        low = reply.lower()
        assert "officially verified" in low or "رسمياً" in reply
        # No skill may be asserted from the education fields.
        assert "bsc" not in low and "cairo" not in low


def test_match_explain_uses_canonical_labels_and_no_bare_fit_claim(student_id, db):
    from app import match_explain
    student = models.get_student(student_id)
    target = match_explain.target_role_match_breakdown(student)
    assert target["metric_key"] == metrics.TARGET_REQUIREMENT_COVERAGE
    assert target["metric_label"] == "Target requirement coverage"
    assert isinstance(target["complete"], bool)
    if not target["complete"]:
        assert target["next_action"].lower().startswith(("close the gap", "learn or verify"))


# --------------------------------------------------------------------------
# trust language, English and Arabic
# --------------------------------------------------------------------------

def test_trust_language_en_and_ar_distinguish_official_from_reported():
    en = genai._verified_skills_fallback("nova", "en", None)
    ar = genai._verified_skills_fallback("nova", "ar", None)
    assert "no officially verified skills" in en.lower()
    assert "user-reported" in en.lower()
    assert "لا يعرض أي مهارات موثقة رسمياً" in ar
    assert "ظل كلاماً منك" in ar
    assert "official" in en.lower()
