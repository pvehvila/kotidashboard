from __future__ import annotations

import time
from typing import Any

import requests

from src.api.http_client import api_request_with_retry
from src.config import HTTP_TIMEOUT_S
from src.utils import report_error

__all__ = [
    "api_request_with_retry",
    "http_get_json",
    "report_error",
    "requests",
]


def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S) -> dict[str, Any]:
    headers = {"User-Agent": "HomeDashboard/1.0 (+https://github.com/pvehvila/kotidashboard)"}
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        if resp.status_code in (429, 403):
            time.sleep(0.8)
            resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        report_error(f"http_get_json: {url}", e)
        raise
