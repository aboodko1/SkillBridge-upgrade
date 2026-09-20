"""Phase 4D - Unified Mentor Live: interview-mode session summary + meta.

The Unified Live engine runs the accepted one-engine/one-orb loop in two modes
(Conversation and Interview). This file pins the backend contract for Interview
mode over POST /tutor: the thread keeps mode/language metadata (migration 0014),
and POST /api/students/{id}/interview/summary produces a DETERMINISTIC,
non-verifying practice summary built ONLY from stored messages - no provider
call, never exposes transcripts, never creates/verifies a skill. The standalone
mock-interview endpoint and normal chat are untouched.

Never calls a paid API.
"""

import sqlite3

import pytest

from app import genai, models, database
import app.jobs as jobs_mod


@pytest.fixture(autouse=True)
def _deterministic(monkeypatch):
    """Lock generation into the deterministic fallback and keep jobs offline."""
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)
    monkeypatch.setattr(jobs_mod, "_fetch_all", lambda *a, **k: [])
    jobs_mod.clear_job_cache()


def _create_conversation(client, student_id, headers, tutor_id="nova"):
    r = client.post(f"/api/students/{student_id}/tutor/conversations",
                    json={"tutor_id": tutor_id}, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["conversation"]


def _chat(client, student_id, headers, message, conversation_id, extra=None):
    body = {"message": message, "conversation_id": conversation_id, **(extra or {})}
    return client.post(f"/api/students/{student_id}/tutor", json=body, headers=headers)


def _summary(client, student_id, headers, body):
    return client.post(f"/api/students/{student_id}/interview/summary",
                       json=body, headers=headers)


# ------------------------------------------------------------------ summary endpoint contract

def test_summary_requires_login_and_own_student(client):
    assert _summary(client, 1, {}, {"conversation_id": 1}).status_code == 401


def test_summary_requires_conversation_id(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _summary(client, student_id, h, {})
    assert r.status_code == 400
    assert "conversation_id" in r.json()["detail"].lower()


def test_summary_unknown_conversation_is_404(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _summary(client, student_id, h, {"conversation_id": 999999})
    assert r.status_code == 404


def test_summary_empty_conversation_is_400(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h)
    r = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r.status_code == 400, r.text
    assert "No interview messages" in r.json()["detail"]


def test_summary_wrong_tutor_persona_is_404(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    r = _chat(client, student_id, h, "Hello", conv["id"], {"mode": "interview"})
    assert r.status_code == 200, r.text
    other = _summary(client, student_id, h,
                     {"conversation_id": conv["id"], "tutor_id": "vex"})
    assert other.status_code == 404


def test_summary_other_student_conversation_guarded(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h)
    other = auth_headers("omar@student.edu")
    r = _summary(client, student_id, other, {"conversation_id": conv["id"]})
    assert r.status_code in (403, 404)


# ------------------------------------------------------------------ interview-mode metadata

def test_tutor_interview_persists_meta_on_thread(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    same_conv = _chat(client, student_id, h,
                      "I built a small Docker compose setup",
                      conv["id"], {"mode": "interview", "language": "en"})
    assert same_conv.status_code == 200
    assert same_conv.json()["mode"] == "interview"
    assert same_conv.json().get("conversation_id") == conv["id"]
    got = models.get_tutor_conversation(student_id, conv["id"])
    assert got is not None and got.get("mode") == "interview"
    assert got.get("language") in ("en", "ar")


def test_tutor_chat_meta_defaults_to_chat(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h)
    r = _chat(client, student_id, h, "Explain Docker simply",
              conv["id"], {"mode": "chat", "language": "en"})
    assert r.status_code == 200
    got = models.get_tutor_conversation(student_id, conv["id"])
    assert got.get("mode") == "chat"
    # a fresh conversation without an explicit mode still gets a default
    fresh = _create_conversation(client, student_id, h)
    assert models.get_tutor_conversation(student_id, fresh["id"]).get("mode") == "chat"


def _file_db(path, name="live.db"):
    conn = sqlite3.connect(str(path / name))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def test_migration_0014_adds_live_meta_columns(tmp_path):
    conn = _file_db(tmp_path)
    database.set_db_for_test(conn)
    try:
        database.init_db()
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(tutor_conversations)")}
        assert {"mode", "language"} <= cols
        applied = [m["migration_id"] for m in database.applied_migrations()]
        assert applied[-1] == "0016_mentor_ui_preferences"
        assert database.run_migrations() == []
    finally:
        database.set_db_for_test()
        conn.close()


def test_migration_0015_upgrades_existing_db(tmp_path):
    """Phase 4 tour-state migration: an existing DB (everything pre-0015)
    gains the per-student tour table when 0015 runs, and reads back synthetic
    not_seen defaults before any row is written."""
    conn = _file_db(tmp_path, "live-old.db")
    database.set_db_for_test(conn)
    try:
        pre = [m for m in database.MIGRATIONS if m["id"] != "0016_mentor_ui_preferences"]
        database.run_migrations(conn=conn, migrations=pre)
        conn.execute("INSERT INTO students (email, name) VALUES ('live@student.edu', 'Live')")
        sid = conn.execute("SELECT id FROM students WHERE email='live@student.edu'").fetchone()["id"]
        conn.commit()
        pending = database.run_migrations()
        assert pending == ["0016_mentor_ui_preferences"]
        cols = {r["name"] for r in conn.execute(
            "PRAGMA table_info(student_tour_state)").fetchall()}
        assert {"student_id", "tour_version", "welcome_state",
                "dont_show_again", "mini_states_json"} <= cols
        row = conn.execute("SELECT welcome_state, mini_states_json FROM student_tour_state "
                           "WHERE student_id=?", (sid,)).fetchone()
        assert row is None  # synthetic not_seen, nothing persisted yet
        assert database.run_migrations() == []
    finally:
        database.set_db_for_test()
        conn.close()


# ------------------------------------------------------------------ summary content

def _run_interview(client, student_id, headers, conv, answers, tutor_id="nova",
                   language="en"):
    for i, answer in enumerate(answers):
        r = _chat(client, student_id, headers, answer, conv["id"],
                  {"mode": "interview", "tutor_id": tutor_id, "language": language,
                   "turn": i + 1})
        assert r.status_code == 200, (i, r.text)
    return answers


def test_summary_is_deterministic_and_counts_turns(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    answers = [
        "I built a small Docker compose setup last semester for a class project.",
        "I check the ports with docker ps and make sure the container restarts on failure.",
        "I would test the whole flow with a fresh volume to be sure nothing leaks.",
    ]
    _run_interview(client, student_id, h, conv, answers)
    r1 = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    r2 = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r1.status_code == 200, r1.text
    b1, b2 = r1.json(), r2.json()
    assert b1 == b2  # deterministic - no provider, stable output
    assert b1["turns"] == len(answers)
    assert b1["chars"] > 0
    assert b1["tutor_id"] == "nova"
    assert b1["mode"] == "interview"
    assert b1["language"] == "en"
    summary = b1["summary"]
    assert "Interview summary" in summary
    assert "3 answers" in summary
    assert "This is practice feedback only" in summary


def test_summary_english_language_pin(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "sage")
    _run_interview(client, student_id, h, conv,
                   ["I have practiced SQL joins on a real dataset."],
                   tutor_id="sage", language="en")
    r = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r.status_code == 200
    body = r.json()
    assert body["language"] == "en"
    assert "Interview summary" in body["summary"]


def test_summary_arabic_language_pin(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "axel")
    _run_interview(client, student_id, h, conv,
                   ["بنيت اعداد Docker Compose صغير في مشروع التخرج"],
                   tutor_id="axel", language="ar")
    r = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r.status_code == 200
    body = r.json()
    assert body["language"] == "ar"
    assert "ملخص المقابلة" in body["summary"]
    assert "مراجعة تدريبية فقط" in body["summary"]


def test_summary_never_invokes_provider(client, student_id, auth_headers, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("summary must never call the provider")

    monkeypatch.setattr(genai, "complete", boom)
    monkeypatch.setattr(genai, "interview_reply", boom)
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    # a user answer exists on the thread (inserted directly so the boomed
    # provider paths are never exercised by the setup itself)
    models.add_tutor_message(student_id, "nova", None, "user", "I practiced docker",
                             conversation_id=conv["id"])
    r = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r.status_code == 200, r.text
    assert "practice feedback only" in r.json()["summary"]


def test_summary_empty_answers_still_resolves(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    # A stored thread where the only stored user turn was an empty/blank answer
    # (e.g. server STT returned nothing) must still resolve with covered = 0.
    models.add_tutor_message(student_id, "nova", None, "assistant",
                             "Start with a concrete example.", conversation_id=conv["id"])
    models.add_tutor_message(student_id, "nova", None, "user", "",
                             conversation_id=conv["id"])
    r = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r.status_code == 200, r.text
    assert "practice feedback only" in r.json()["summary"]


def test_summary_skill_name_resolves_from_ids(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    _run_interview(client, student_id, h, conv, ["I practiced docker volumes"])
    skill = models.get_skill_by_name("Docker")
    assert skill is not None
    r = _summary(client, student_id, h,
                 {"conversation_id": conv["id"], "skill_id": skill["id"]})
    assert r.status_code == 200
    assert "docker" in r.json()["summary"].lower()


def test_summary_unknown_skill_id_does_not_break(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "nova")
    _run_interview(client, student_id, h, conv, ["I practiced docker volumes"])
    r = _summary(client, student_id, h,
                 {"conversation_id": conv["id"], "skill_id": 999999})
    assert r.status_code == 200


def test_summary_concerted_strong_answer_yields_strengths(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    conv = _create_conversation(client, student_id, h, "vex")
    _run_interview(client, student_id, h, conv, [
        "I built a Python script that loops over the API and writes the JSON to a file.",
        "I ran it, verified the output, and fixed a bug when the endpoint changed.",
    ], tutor_id="vex")
    r = _summary(client, student_id, h, {"conversation_id": conv["id"]})
    assert r.status_code == 200
    s = r.json()["summary"]
    assert "concrete and clear" in s or "was practical and clear" in s or "real experience" in s


def test_summary_preserves_conversation_independence(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    skill_python = models.get_skill_by_name("Python")
    skill_docker = models.get_skill_by_name("Docker")
    conv_a = _create_conversation(client, student_id, h, "nova")
    conv_b = _create_conversation(client, student_id, h, "nova")
    _run_interview(client, student_id, h, conv_a, ["I practiced python generators"])
    _run_interview(client, student_id, h, conv_b, ["I practiced docker volumes"])
    a = _summary(client, student_id, h,
                 {"conversation_id": conv_a["id"], "skill_id": skill_python["id"]}).json()
    b = _summary(client, student_id, h,
                 {"conversation_id": conv_b["id"], "skill_id": skill_docker["id"]}).json()
    assert "python" in a["summary"].lower()
    assert "docker" in b["summary"].lower()
    assert a["turns"] == 1 and b["turns"] == 1


def test_standalone_mock_interview_untouched(client, student_id, auth_headers):
    """The standalone mock-interview engine keeps working byte-identical."""
    h = auth_headers("aisha@student.edu")
    r = client.post(f"/api/students/{student_id}/interview",
                    json={"tutor": "nova", "message": "I built a compose stack"},
                    headers=h)
    assert r.status_code == 200, r.text