# src/api/http.py
import logging
import time
from typing import Any

import requests
from requests.exceptions import RequestException

from src.config import HTTP_TIMEOUT_S
from src.utils import report_error

logger = logging.getLogger("homedashboard")


def api_request_with_retry(
    url: str, method: str = "GET", retry_count: int = 3, **kwargs
) -> dict[Any, Any] | None:
    for attempt in range(retry_count):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except RequestException as e:
            logger.warning("API request failed (%s/%s): %s", attempt + 1, retry_count, e)
            if attempt + 1 == retry_count:
                return None
            time.sleep(2**attempt)


def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S) -> dict:
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
