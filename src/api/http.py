"""Compatibility wrapper for HTTP helpers (single source of truth in http_client)."""

from __future__ import annotations

from src.api import http_client as _http_client

api_request_with_retry = _http_client.api_request_with_retry
http_get_json = _http_client.http_get_json
RateLimitBackoff = _http_client.RateLimitBackoff
report_error = _http_client.report_error
requests = _http_client.requests

__all__ = [
    "api_request_with_retry",
    "http_get_json",
    "RateLimitBackoff",
    "report_error",
    "requests",
]
