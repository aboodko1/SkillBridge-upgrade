"""Bright Data Google Jobs adapter contracts; no account key or live quota used."""

from urllib.parse import parse_qs, urlsplit

import httpx

from app import jobs


class _Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("POST", jobs.BRIGHTDATA_URL)
            raise httpx.HTTPStatusError("provider error", request=request,
                                        response=httpx.Response(self.status_code, request=request))

    def json(self):
        return self.payload


def test_key_without_zone_skips_without_spending_quota(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.delenv("BRIGHTDATA_SERP_ZONE", raising=False)
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("must not request without zone")))
    assert jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt") == []
    assert jobs._provider_status["Bright Data"]["reason"] == "zone_not_configured"
    assert jobs._provider_is_configured("Bright Data") is False


def test_egypt_jobs_are_localized_and_foreign_results_excluded(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return _Response({"jobs": [
            {"id": "1", "title": "Junior AI Engineer", "company": "Cairo Tech",
             "location": "Cairo, Egypt", "apply_options": [
                 {"link": "https://employer.example/jobs/1"}]},
            {"id": "2", "title": "AI Engineer", "company": "Dubai Tech",
             "location": "Dubai, United Arab Emirates", "country": "United Arab Emirates",
             "link": "https://employer.example/jobs/2"},
            {"id": "3", "title": "Remote AI Engineer", "location": "Remote",
             "link": "https://employer.example/jobs/3"},
        ]})

    monkeypatch.setattr(jobs.httpx, "post", fake_post)
    result = jobs._fetch_brightdata_jobs(10, ["AI Engineer", "Python"], "Egypt")
    assert len(calls) == 3  # bounded nationwide + Cairo + Alexandria searches
    assert calls[0][0] == jobs.BRIGHTDATA_URL
    assert calls[0][1]["headers"]["Authorization"] == "Bearer test-key"
    assert calls[0][1]["json"]["zone"] == "test-serp-zone"
    search = parse_qs(urlsplit(calls[0][1]["json"]["url"]).query)
    assert search["gl"] == ["eg"] and "ibp" not in search
    assert "AI Engineer" in search["q"][0]
    assert calls[0][1]["json"]["format"] == "json"
    assert len(result) == 1 and result[0]["country"] == "Egypt"
    assert result[0]["url"] == "https://employer.example/jobs/1"
    assert result[0]["date"] == ""  # no posting date was supplied
    assert jobs._provider_status["Bright Data"]["status"] == "ok"


def test_one_upstream_failure_does_not_hide_other_egypt_results(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")

    def fake_post(url, **kwargs):
        query = parse_qs(urlsplit(kwargs["json"]["url"]).query)["q"][0]
        if "Cairo" in query:
            return _Response({"status_code": 502, "body": "upstream unavailable"})
        return _Response({"jobs": [{"id": "alex-1", "title": "AI Engineer",
                                    "location": "Alexandria, Egypt",
                                    "link": "https://employer.example/alex-1"}]})

    monkeypatch.setattr(jobs.httpx, "post", fake_post)
    result = jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt")
    assert len(result) == 1  # duplicate across working searches is removed
    assert result[0]["location"] == "Alexandria, Egypt"
    assert jobs._provider_status["Bright Data"]["status"] == "ok"


def test_ordinary_search_results_are_not_misrepresented_as_jobs(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: _Response({
        "organic": [{"title": "Jobs in Cairo", "link": "https://search.example/jobs"}]}))
    assert jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt") == []
    assert jobs._provider_status["Bright Data"]["reason"] == "malformed_response"


def test_valid_serp_without_jobs_is_honestly_empty(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: _Response({
        "status_code": 200,
        "body": '{"general":{"search_engine":"google"},'
                '"organic":[{"title":"Not a job","link":"https://search.example"}]}'
    }))
    assert jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt") == []
    assert jobs._provider_status["Bright Data"]["status"] == "ok"
    assert jobs._provider_status["Bright Data"]["count"] == 0


def test_real_serp_wrapper_and_nested_jobs_items(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: _Response({
        "status_code": 200,
        "body": '{"jobs":{"items":[{"title":"AI Engineer","company":"Cairo Tech",'
                '"location":"Cairo, Egypt","link":"https://google.example/job",'
                '"apply_link":"https://employer.example/apply"}]},'
                '"organic":[{"title":"Not a job","link":"https://search.example"}]}'
    }))
    result = jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt")
    assert len(result) == 1
    assert result[0]["url"] == "https://employer.example/apply"
    assert result[0]["country"] == "Egypt"


def test_inner_upstream_error_is_not_a_success(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: _Response({
        "status_code": 502, "body": "upstream unavailable"}))
    assert jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt") == []
    assert jobs._provider_status["Bright Data"]["reason"] == "upstream_error"


def test_relative_apply_link_falls_back_to_absolute_listing(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: _Response({
        "status_code": 200,
        "body": '{"jobs":{"items":[{"title":"Software Engineer",'
                '"location":"Cairo","apply_link":"/goto?url=relative",'
                '"link":"https://www.google.com/search?ibp=htl%3Bjobs"}]}}'
    }))
    result = jobs._fetch_brightdata_jobs(10, ["Software Engineer"], "Egypt")
    assert len(result) == 1
    assert result[0]["url"].startswith("https://www.google.com/search?")


def test_rate_limit_degrades_without_disclosing_key(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "unique-test-secret")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: _Response({}, 429))
    assert jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Egypt") == []
    assert jobs._provider_status["Bright Data"]["reason"] == "rate_limited"
    assert "unique-test-secret" not in str(jobs.provider_status())
    assert "unique-test-secret" not in jobs._redact("key=unique-test-secret")


def test_non_egypt_does_not_query_brightdata(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test-key")
    monkeypatch.setenv("BRIGHTDATA_SERP_ZONE", "test-serp-zone")
    monkeypatch.setattr(jobs.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("Egypt-only provider")))
    assert jobs._fetch_brightdata_jobs(10, ["AI Engineer"], "Germany") == []
    assert jobs._provider_status["Bright Data"]["reason"] == "unsupported_country"
