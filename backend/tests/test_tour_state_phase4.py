"""Phase 4 — product tour state (server-side source of truth).

Covers the migration, the strict validation contract of the GET/PUT endpoints,
and authorization (401 unauthenticated, 403 cross-student, 400 bad payloads).
The welcome tour + contextual mini-tours are driven entirely by this state;
localStorage on the frontend is only an optional UI cache.
"""


def _get(client, sid, headers):
    return client.get(f"/api/students/{sid}/tour/state", headers=headers)


def _put(client, sid, headers, payload):
    return client.put(f"/api/students/{sid}/tour/state", headers=headers, json=payload)


# ------------------------------------------------------------------ migration

def test_migration_0015_creates_student_tour_state(tmp_path):
    import sqlite3
    from app import database

    conn = sqlite3.connect(str(tmp_path / "tour.db"))
    conn.row_factory = sqlite3.Row
    database.set_db_for_test(conn)
    try:
        database.init_db()
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(student_tour_state)").fetchall()}
        assert {"student_id", "tour_version", "welcome_state",
                "dont_show_again", "mini_states_json"} <= cols
        applied = [m["migration_id"] for m in database.applied_migrations()]
        assert "0015_student_tour_state" in applied
        assert "0016_mentor_ui_preferences" in applied
        assert database.run_migrations() == []
    finally:
        database.set_db_for_test()
        conn.close()


def test_migration_0015_is_idempotent(tmp_path):
    import sqlite3
    from app import database

    conn = sqlite3.connect(str(tmp_path / "tour2.db"))
    conn.row_factory = sqlite3.Row
    database.set_db_for_test(conn)
    try:
        database.init_db()
        assert database.run_migrations() == []
    finally:
        database.set_db_for_test()
        conn.close()


# ------------------------------------------------------------------ defaults

def test_never_written_student_is_not_seen(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _get(client, student_id, h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["welcome_state"] == "not_seen"
    assert body["default"] is True
    assert body["mini_states"] == {}
    assert body["dont_show_again"] is False
    assert body["tour_version"] == "v1"


# ------------------------------------------------------------------ auth

def test_tour_state_requires_login(client):
    r = _get(client, 1, {})
    assert r.status_code == 401

def test_tour_state_update_requires_login(client):
    r = _put(client, 1, {}, {"welcome_state": "completed"})
    assert r.status_code == 401

def test_tour_state_rejects_another_student(client, student_id, auth_headers):
    h = auth_headers("omar@student.edu")
    r = _get(client, student_id, h)
    assert r.status_code == 403

def test_tour_state_update_rejects_another_student(client, student_id, auth_headers):
    h = auth_headers("omar@student.edu")
    r = _put(client, student_id, h, {"welcome_state": "completed"})
    assert r.status_code == 403

def test_tour_state_rejects_non_student_role(client, auth_headers):
    h = auth_headers("hr@northstar.com")
    r = _get(client, 1, h)
    assert r.status_code == 403


# ------------------------------------------------------------------ lifecycle

def test_welcome_complete_and_skip_flow(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    assert _put(client, student_id, h, {"welcome_state": "active"}).json()["welcome_state"] == "active"
    r = _put(client, student_id, h, {"welcome_state": "completed"})
    assert r.status_code == 200
    assert r.json()["welcome_state"] == "completed"
    assert r.json()["default"] is False
    # completed persists — replay must be explicit (active), never auto.
    assert _get(client, student_id, h).json()["welcome_state"] == "completed"
    assert _put(client, student_id, h, {"welcome_state": "active"}).json()["welcome_state"] == "active"
    assert _put(client, student_id, h, {"welcome_state": "skipped"}).json()["welcome_state"] == "skipped"


def test_dont_show_again_flag(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {"welcome_state": "skipped", "dont_show_again": True})
    assert r.status_code == 200
    assert r.json()["welcome_state"] == "skipped"
    assert r.json()["dont_show_again"] is True
    assert _get(client, student_id, h).json()["dont_show_again"] is True
    # flag can be cleared for a later major-version re-tour.
    assert _put(client, student_id, h, {"dont_show_again": False}).json()["dont_show_again"] is False


def test_mini_tour_transitions_and_merge(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    assert _put(client, student_id, h, {"mini_states": {"roles": "completed"}}).json()["mini_states"] == {"roles": "completed"}
    merged = _put(client, student_id, h, {"mini_states": {"learning": "completed"}}).json()["mini_states"]
    assert merged == {"roles": "completed", "learning": "completed"}
    assert _get(client, student_id, h).json()["mini_states"] == merged


# ------------------------------------------------------------------ validation

def test_invalid_welcome_state_is_400(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {"welcome_state": "maybe"})
    assert r.status_code == 400

def test_invalid_dont_show_again_type_is_400(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {"dont_show_again": "yes"})
    assert r.status_code == 400

def test_invalid_mini_page_is_400(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {"mini_states": {"tutorial": "completed"}})
    assert r.status_code == 400

def test_invalid_mini_state_is_400(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {"mini_states": {"roles": "revealed"}})
    assert r.status_code == 400

def test_non_object_payload_is_rejected(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    # A JSON array is not the {welcome_state, dont_show_again, mini_states}
    # object shape → FastAPI validation rejects it before any mutation.
    r = client.put(f"/api/students/{student_id}/tour/state",
                   headers={**h, "Content-Type": "application/json"}, content=b"[1,2]")
    assert r.status_code == 422
    assert _get(client, student_id, h).json()["welcome_state"] == "not_seen"