from __future__ import annotations

import pytest

import src.api.http_client as http_client


class DummyResp:
    def __init__(self, status: int, payload: dict | None = None, headers: dict | None = None):
        self.status_code = status
        self._payload = payload or {}
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400 and self.status_code not in (403, 429):
            raise RuntimeError("http error")

    def json(self) -> dict:
        return self._payload


def test_http_get_json_coingecko_backoff_active(monkeypatch):
    monkeypatch.setattr(http_client, "_coingecko_backoff_active", lambda: True)
    monkeypatch.setattr(
        http_client.requests,
        "get",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not call")),
    )

    with pytest.raises(http_client.RateLimitBackoff):
        http_client.http_get_json("https://api.coingecko.com/api/v3/ping")


def test_http_get_json_coingecko_429_sets_backoff(monkeypatch):
    monkeypatch.setattr(http_client.time, "time", lambda: 1000.0)
    http_client._COINGECKO_BACKOFF_UNTIL = 0.0

    resp = DummyResp(429, headers={"Retry-After": "2"})
    monkeypatch.setattr(http_client.requests, "get", lambda *a, **k: resp)

    with pytest.raises(http_client.RateLimitBackoff):
        http_client.http_get_json("https://api.coingecko.com/api/v3/ping")

    assert http_client._COINGECKO_BACKOFF_UNTIL == 1002.0


def test_http_get_json_non_coingecko_retries(monkeypatch):
    calls = {"n": 0}

    def fake_get(url, *a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            return DummyResp(429)
        return DummyResp(200, payload={"ok": True})

    monkeypatch.setattr(http_client.requests, "get", fake_get)
    monkeypatch.setattr(http_client.time, "sleep", lambda *_: None)

    out = http_client.http_get_json("https://example.com/api")

    assert out == {"ok": True}
    assert calls["n"] == 2


def test_http_get_json_reports_error(monkeypatch):
    captured: dict[str, str] = {}

    def fake_report_error(ctx: str, err: Exception) -> None:
        captured["ctx"] = ctx
        captured["err"] = str(err)

    monkeypatch.setattr(http_client, "report_error", fake_report_error)
    monkeypatch.setattr(
        http_client.requests,
        "get",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    with pytest.raises(RuntimeError):
        http_client.http_get_json("https://example.com/api")

    assert "http_get_json" in captured["ctx"]
    assert "boom" in captured["err"]
