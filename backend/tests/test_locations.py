"""Locations endpoint + countries seed (idempotent).

GET /api/locations must return a non-empty country/city list for the cascading
signup dropdown, and the reference seed must be safe to run repeatedly.
"""
import pytest

from app import models, seed


def test_locations_endpoint_returns_nonempty(client):
    resp = client.get("/api/locations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for entry in data:
        assert entry.get("country")
        assert isinstance(entry.get("cities"), list)
        assert entry["cities"]


def test_countries_seed_is_idempotent(db):
    seed.ensure_locations()
    first = len(models.list_locations())
    seed.ensure_locations()
    second = len(models.list_locations())
    # Same number of countries after re-running; no duplicate city rows.
    assert first > 0
    assert second == first
    with models.get_cursor() as c:
        dup = c.execute(
            "SELECT country, name, count(*) AS n FROM cities GROUP BY country, name HAVING n > 1"
        ).fetchall()
    assert dup == []


def test_universities_seed_is_idempotent(db):
    seed.ensure_locations()
    first = len(models.list_universities())
    seed.ensure_locations()
    second = len(models.list_universities())
    assert first > 0
    assert second == first
    with models.get_cursor() as c:
        dup = c.execute(
            "SELECT country, name, count(*) AS n FROM universities GROUP BY country, name HAVING n > 1"
        ).fetchall()
    assert dup == []


def test_locations_include_egypt_for_demo_flow(db):
    # The demo path uses Egypt (Cairo / Future University in Egypt).
    seed.ensure_locations()
    countries = {e["country"] for e in models.list_locations()}
    assert "Egypt" in countries
    egypt = next(e for e in models.list_locations() if e["country"] == "Egypt")
    assert "Cairo" in egypt["cities"]