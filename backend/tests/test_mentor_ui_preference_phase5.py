"""Phase 5 — mentor UI visibility preference (server-side source of truth).

Covers the migration, the strict validation contract of the GET/PUT
/api/students/{id}/mentor/ui endpoints, and authorization (401, 403
cross-student, 403 non-student). The Copilot panel is localStorage-free by
contract, so this row is what makes the "hidden vs shown" mentor choice
survive a refresh; a never-written student reads back panel_visible=True so
the Phase-5 feature never changes the default experience.
"""


def _get(client, sid, headers):
    return client.get(f"/api/students/{sid}/mentor/ui", headers=headers)


def _put(client, sid, headers, payload):
    return client.put(f"/api/students/{sid}/mentor/ui", headers=headers, json=payload)


# ------------------------------------------------------------------ migration

def test_migration_0016_creates_mentor_ui_preferences(tmp_path):
    import sqlite3
    from app import database

    conn = sqlite3.connect(str(tmp_path / "mentor_ui.db"))
    conn.row_factory = sqlite3.Row
    database.set_db_for_test(conn)
    try:
        database.init_db()
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(mentor_ui_preferences)").fetchall()}
        assert {"student_id", "panel_visible", "updated_at"} <= cols
        applied = [m["migration_id"] for m in database.applied_migrations()]
        assert "0016_mentor_ui_preferences" in applied
        assert database.run_migrations() == []
    finally:
        database.set_db_for_test()
        conn.close()


def test_migration_0016_is_idempotent(tmp_path):
    import sqlite3
    from app import database

    conn = sqlite3.connect(str(tmp_path / "mentor_ui2.db"))
    conn.row_factory = sqlite3.Row
    database.set_db_for_test(conn)
    try:
        database.init_db()
        assert database.run_migrations() == []
    finally:
        database.set_db_for_test()
        conn.close()


# ------------------------------------------------------------------ defaults

def test_never_written_student_is_visible(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _get(client, student_id, h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["student_id"] == student_id
    assert body["panel_visible"] is True
    assert body["default"] is True
    assert body["updated_at"] is None


# ------------------------------------------------------------------ auth

def test_mentor_ui_requires_login(client):
    assert _get(client, 1, {}).status_code == 401

def test_mentor_ui_update_requires_login(client):
    assert _put(client, 1, {}, {"panel_visible": False}).status_code == 401

def test_mentor_ui_rejects_another_student(client, student_id, auth_headers):
    h = auth_headers("omar@student.edu")
    r = _get(client, student_id, h)
    assert r.status_code == 403

def test_mentor_ui_update_rejects_another_student(client, student_id, auth_headers):
    h = auth_headers("omar@student.edu")
    r = _put(client, student_id, h, {"panel_visible": False})
    assert r.status_code == 403

def test_mentor_ui_rejects_non_student_role(client, auth_headers):
    h = auth_headers("hr@northstar.com")
    r = _get(client, 1, h)
    assert r.status_code == 403


# ------------------------------------------------------------------ lifecycle

def test_visibility_hide_show_roundtrip(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {"panel_visible": False})
    assert r.status_code == 200
    assert r.json()["panel_visible"] is False
    assert r.json()["default"] is False
    # persists server-side — a later GET (e.g. after refresh) still hides.
    assert _get(client, student_id, h).json()["panel_visible"] is False
    assert _put(client, student_id, h, {"panel_visible": True}).json()["panel_visible"] is True
    assert _get(client, student_id, h).json()["panel_visible"] is True


def test_visibility_is_per_student(client, student_id, auth_headers):
    aisha = auth_headers("aisha@student.edu")
    omar = auth_headers("omar@student.edu")
    assert _put(client, student_id, aisha, {"panel_visible": False}).json()["panel_visible"] is False
    # The other student's own view is untouched by this student's choice.
    omar_id = omar_id_of(client)
    assert _get(client, omar_id, omar).json()["panel_visible"] is True


def omar_id_of(client):
    r = client.post("/api/auth/login", json={"email": "omar@student.edu", "password": "demo1234"})
    assert r.status_code == 200
    return r.json()["student"]["id"]


def test_partial_payload_requires_boolean(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = _put(client, student_id, h, {})
    assert r.status_code == 400
    assert "panel_visible" in r.json()["detail"]
    r2 = _put(client, student_id, h, {"panel_visible": "no"})
    assert r2.status_code == 400
    r3 = _put(client, student_id, h, {"panel_visible": 1})
    assert r3.status_code == 400
    # nothing was written by the rejected calls
    assert _get(client, student_id, h).json()["panel_visible"] is True


def test_non_object_payload_is_rejected(client, student_id, auth_headers):
    h = auth_headers("aisha@student.edu")
    r = client.put(f"/api/students/{student_id}/mentor/ui",
                   headers={**h, "Content-Type": "application/json"}, content=b"[1,2]")
    assert r.status_code == 422
    assert _get(client, student_id, h).json()["panel_visible"] is True