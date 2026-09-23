"""Offline contracts for the keyless Egypt employer-board provider."""

from datetime import date, timedelta

from app import jobs


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_employer_boards_only_returns_egypt_openings(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        if "/Bosta" in url:
            return _Response([
                {"id": "1", "text": "Data Analyst", "hostedUrl": "https://jobs.lever.co/Bosta/1",
                 "categories": {"location": "Cairo"}},
                {"id": "2", "text": "Engineer", "hostedUrl": "https://jobs.lever.co/Bosta/2",
                 "categories": {"location": "Dubai"}},
            ])
        if "/econstruct" in url:
            return _Response([])
        return _Response({"jobs": [
            {"id": 3, "title": "AI Engineer", "absolute_url": "https://job-boards.greenhouse.io/careem/jobs/3",
             "location": {"name": "Alexandria, Egypt"}},
        ]})

    monkeypatch.setattr(jobs.httpx, "get", fake_get)
    rows = jobs._fetch_employer_boards(10, "Egypt")
    assert len(rows) == 2
    assert {row["company"] for row in rows} == {"Bosta", "Careem"}
    assert all(row["source"] == "Employer boards" and row["country"] == "Egypt" for row in rows)
    assert all(row["date"] == "" for row in rows)  # fetch time is not a posting date
    assert all(row["available"] is True for row in rows)
    assert len(calls) == 3
    assert jobs._provider_status["Employer boards"]["status"] == "ok"


def test_employer_boards_skip_non_egypt_without_network(monkeypatch):
    monkeypatch.setattr(jobs.httpx, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network")))
    assert jobs._fetch_employer_boards(10, "United Arab Emirates") == []
    assert jobs._provider_status["Employer boards"]["reason"] == "unsupported_country"


def test_employer_boards_partial_failure_preserves_good_listings(monkeypatch):
    def fake_get(url, **kwargs):
        if "/Bosta" in url:
            raise TimeoutError("provider timeout")
        if "/econstruct" in url:
            return _Response([{"id": "a", "text": ".Net Developer",
                               "hostedUrl": "https://jobs.lever.co/econstruct/a",
                               "categories": {"location": "Cairo"}}])
        return _Response({"jobs": []})

    monkeypatch.setattr(jobs.httpx, "get", fake_get)
    rows = jobs._fetch_employer_boards(10, "Egypt")
    assert len(rows) == 1
    assert rows[0]["company"] == "e.construct"
    assert jobs._provider_status["Employer boards"]["reason"] == "partial_failure"


def test_published_employer_board_is_not_expired_by_age_heuristic():
    old_date = date.today() - timedelta(days=90)
    expired, _, age = jobs._expiry_props({"available": True}, old_date)
    assert age == 90
    assert expired is False
