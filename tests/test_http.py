# tests/test_http.py
from unittest.mock import MagicMock

import pytest

import src.api.http as http

# ---------- api_request_with_retry ----------


def test_api_request_with_retry_success(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ok": True}
    mock_resp.raise_for_status.return_value = None

    monkeypatch.setattr("requests.request", lambda *a, **kw: mock_resp)

    result = http.api_request_with_retry("https://x", "GET", retry_count=3)
    assert result == {"ok": True}


def test_api_request_with_retry_retries_then_success(monkeypatch):
    calls = {"n": 0}

    def fake_request(*a, **kw):
        calls["n"] += 1
        if calls["n"] < 2:
            raise http.requests.exceptions.RequestException("temporary fail")
        mock = MagicMock()
        mock.raise_for_status.return_value = None
        mock.json.return_value = {"ok": True}
        return mock

    monkeypatch.setattr("requests.request", fake_request)
    result = http.api_request_with_retry("https://example.com", retry_count=3)
    assert result == {"ok": True}
    assert calls["n"] == 2  # first fail, second success


def test_api_request_with_retry_all_fail(monkeypatch):
    def always_fail(*a, **kw):
        raise http.requests.exceptions.RequestException("fail")

    monkeypatch.setattr("requests.request", always_fail)

    result = http.api_request_with_retry("https://x", retry_count=2)
    assert result is None


# ---------- http_get_json ----------


def test_http_get_json_success(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"value": 123}
    mock_resp.raise_for_status.return_value = None

    monkeypatch.setattr("requests.get", lambda *a, **kw: mock_resp)

    out = http.http_get_json("https://api.test")
    assert out == {"value": 123}


def test_http_get_json_retries_on_429(monkeypatch):
    call_count = {"n": 0}

    def fake_get(url, *a, **kw):
        call_count["n"] += 1
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        if call_count["n"] == 1:
            mock_resp.status_code = 429
        else:
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"ok": True}
        return mock_resp

    monkeypatch.setattr("requests.get", fake_get)
    out = http.http_get_json("https://api.test")
    assert out == {"ok": True}
    assert call_count["n"] == 2


def test_http_get_json_raises_and_reports(monkeypatch):
    captured = {}

    def fake_report_error(ctx, e):
        captured["ctx"] = ctx
        captured["err"] = str(e)

    monkeypatch.setattr(http, "report_error", fake_report_error)
    monkeypatch.setattr("requests.get", lambda *a, **kw: (_ for _ in ()).throw(Exception("boom")))

    with pytest.raises(Exception):  # noqa: B017
        http.http_get_json("https://badurl")

    assert "http_get_json:" in captured["ctx"]
    assert "boom" in captured["err"]
