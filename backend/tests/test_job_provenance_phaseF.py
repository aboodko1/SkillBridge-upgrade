"""Phase F — honest job provenance and safe apply targets (offline only).

Verifies the additive metadata the feed exposes to the UI: per-listing
provider/fetched_at/link_state/apply_safe, feed status/checked_at retained
across a cache read, and the guarantee that a listing without a validated
absolute http(s) target is surfaced honestly but can never present a clickable
Apply destination. Every provider is mocked via ``_fetch_all``; no network and
no real quota is ever spent.
"""
import pytest

from app import jobs


@pytest.fixture(autouse=True)
def _fresh_jobs_state():
    jobs.clear_job_cache()
    jobs._bg_fetching.clear()
    jobs._PROVIDER_COOLDOWN.clear()
    for p in jobs.PROVIDERS:
        jobs._provider_status[p] = {"status": "skipped", "count": 0, "reason": "", "error": ""}
    jobs._stats.update({
        "cache_hits": 0, "cache_misses": 0,
        "last_success_provider": "", "last_error_by_provider": {},
        "fetch_times": [],
    })
    yield
    jobs.clear_job_cache()


def _listing(**overrides):
    base = {
        "title": "Data Analyst", "company": "Acme Analytics",
        "url": "https://example.test/jobs/1", "location": "Cairo, Egypt",
        "tags": ["SQL", "Data", "Analysis"], "source": "Remotive",
        "date": "2026-09-01",
    }
    base.update(overrides)
    return base


def _build(monkeypatch, raw, **profile):
    monkeypatch.setattr(jobs, "_fetch_all", lambda *a, **k: list(raw))
    params = dict(skills=[("Data Analysis", "Intermediate")], role="Data Analyst",
                  country="Egypt", location="Cairo", limit=5)
    params.update(profile)
    return jobs.recent_jobs(**params, _sync=True)


def test_apply_safe_requires_an_absolute_http_target():
    assert jobs.normalise_listing(_listing(url="https://example.test/jobs/1"))["apply_safe"] is True
    assert jobs.normalise_listing(_listing(url="http://example.test/jobs/1"))["apply_safe"] is True
    assert jobs.normalise_listing(_listing(url="l1"))["apply_safe"] is False
    assert jobs.normalise_listing(_listing(url="javascript:alert(1)"))["apply_safe"] is False
    assert jobs.normalise_listing(_listing(url="https://10.0.0.5/job"))["apply_safe"] is False


def test_provenance_records_the_apply_url_basis():
    item = jobs.normalise_listing(_listing())
    assert item["provenance"]["apply_url"]["value"] == "https://example.test/jobs/1"
    assert item["provenance"]["apply_url"]["basis"] == "provider_field"


def test_merge_keeps_apply_safe_aligned_with_the_chosen_link():
    merged = jobs._merge([
        _listing(url="l1", source="Remotive"),
        _listing(url="https://example.test/safe", source="JSearch"),
    ])
    assert len(merged) == 1
    assert merged[0]["url"] == "https://example.test/safe"
    assert merged[0]["apply_safe"] is True


def test_scheme_less_listing_surfaces_without_a_false_apply(monkeypatch):
    data = _build(monkeypatch, [_listing(url="l1")])
    assert data["jobs"], "the listing is still surfaced with its provenance"
    job = data["jobs"][0]
    assert job["link_state"] == "unverified"
    assert job["apply_safe"] is False


def test_feed_exposes_status_checked_and_per_job_fetched(monkeypatch):
    data = _build(monkeypatch, [_listing()])
    assert data["status"] == "fresh"
    assert data["source"] == "live"
    assert data["checked_at"].endswith("Z")
    job = data["jobs"][0]
    assert job["provider"] == "Remotive"
    assert job["fetched_at"].endswith("+00:00")
    assert job["apply_safe"] is True

    cached = jobs.recent_jobs(
        skills=[("Data Analysis", "Intermediate")], role="Data Analyst",
        country="Egypt", location="Cairo", limit=5, _sync=False)
    assert cached["status"] == "cached"
    assert cached["checked_at"] == data["checked_at"]
    cached_job = cached["jobs"][0]
    assert cached_job["fetched_at"] == job["fetched_at"]
    assert cached_job["apply_safe"] is True
