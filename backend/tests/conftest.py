import os
import sqlite3
import tempfile

import pytest

from app import database, resources, seed

# Use a shared in-memory SQLite connection for all tests so each test starts
# from freshly seeded data and nothing persists across tests.


@pytest.fixture(scope="session", autouse=True)
def _isolated_file_db():
    """Give tests a seeded file DB instead of the developer's own database.

    A clean checkout has no ``backend/skillbridge.db``. The app's startup handler
    seeds a missing file DB, but under pytest the in-memory override is active,
    so that call would double-seed the in-memory database and also create a
    stray empty file. Pointing ``DB_PATH`` at a seeded temp file keeps the suite
    hermetic, makes a fresh checkout behave like an installed one, and never
    touches the developer's data.
    """
    original = database.DB_PATH
    fd, path = tempfile.mkstemp(prefix="skillbridge-test-", suffix=".db")
    os.close(fd)
    database.DB_PATH = path
    try:
        seed.seed()
        yield path
    finally:
        database.set_db_for_test()
        database.DB_PATH = original
        try:
            os.unlink(path)
        except OSError:
            pass


@pytest.fixture(autouse=True)
def _no_live_providers(monkeypatch):
    """Keep provider calls disabled during pytest.

    A developer may have ANTHROPIC/OPENAI/NIM keys exported in their shell; the
    suite must never reach a real provider (or spend tokens) because of that.
    Tests that exercise provider behavior set the key they need themselves, so
    their monkeypatch is applied after this fixture and still wins.
    """
    from app import genai
    for name in ("ANTHROPIC_KEY", "OPENAI_KEY", "NIM_KEY"):
        monkeypatch.setattr(genai, name, None, raising=False)


@pytest.fixture()
def db(monkeypatch):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    database.set_db_for_test(conn)
    # Keep seeding fully offline: resource availability checks normally issue
    # live HTTPS HEAD requests (e.g. YouTube thumbnails) which can hang when the
    # network is unavailable, making every test run depend on connectivity.
    monkeypatch.setattr(resources, "_resource_availability", lambda url, timeout=2.0: None)
    seed.seed()
    yield conn
    database.set_db_for_test()
    conn.close()


@pytest.fixture()
def client(db):
    from fastapi.testclient import TestClient
    from app import main
    with TestClient(main.app) as c:
        yield c


@pytest.fixture()
def login(client):
    def do(email, password="demo1234"):
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return r.json()
    return do


@pytest.fixture()
def auth_headers(login):
    def h(email, password="demo1234"):
        payload = login(email, password)
        return {"Authorization": f"Bearer {payload['token']}"}
    return h


@pytest.fixture()
def student_payload(login):
    return login("aisha@student.edu")


@pytest.fixture()
def student_id(student_payload):
    return student_payload["student"]["id"]