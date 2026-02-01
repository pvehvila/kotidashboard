# src/api/http.py
import logging
import time
from typing import Any

import requests
from requests.exceptions import RequestException

from src.config import COINGECKO_BACKOFF_S, HTTP_TIMEOUT_S
from src.utils import report_error

logger = logging.getLogger("homedashboard")
_COINGECKO_BACKOFF_UNTIL = 0.0


class RateLimitBackoff(requests.HTTPError):
    """Raised when a rate-limited endpoint is in backoff window."""


def _is_coingecko_url(url: str) -> bool:
    return "api.coingecko.com" in url


def _set_coingecko_backoff(resp: requests.Response) -> None:
    global _COINGECKO_BACKOFF_UNTIL
    retry_after = resp.headers.get("Retry-After")
    backoff = COINGECKO_BACKOFF_S
    if retry_after:
        try:
            backoff = max(int(retry_after), 1)
        except ValueError:
            backoff = COINGECKO_BACKOFF_S
    _COINGECKO_BACKOFF_UNTIL = time.time() + float(backoff)


def _coingecko_backoff_active() -> bool:
    return time.time() < _COINGECKO_BACKOFF_UNTIL


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
        if _is_coingecko_url(url) and _coingecko_backoff_active():
            raise RateLimitBackoff("coingecko backoff active")
        resp = requests.get(url, timeout=timeout, headers=headers)
        if resp.status_code in (429, 403):
            if _is_coingecko_url(url):
                _set_coingecko_backoff(resp)
                raise RateLimitBackoff(f"coingecko rate limited ({resp.status_code})")
            time.sleep(0.8)
            resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except RateLimitBackoff:
        raise
    except Exception as e:
        report_error(f"http_get_json: {url}", e)
        raise
