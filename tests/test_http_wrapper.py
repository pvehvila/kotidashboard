from __future__ import annotations

import src.api.http as http
import src.api.http_client as http_client


def test_http_module_reexports():
    assert http.api_request_with_retry is http_client.api_request_with_retry
    assert http.http_get_json is http_client.http_get_json
    assert http.RateLimitBackoff is http_client.RateLimitBackoff
    assert http.report_error is http_client.report_error
    assert http.requests is http_client.requests
