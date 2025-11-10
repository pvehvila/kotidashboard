from __future__ import annotations

import datetime as dt
import json
import logging

logger = logging.getLogger(__name__)


def log_raw_prices(source: str, date_ymd: dt.date, data: object) -> None:
    """
    Kevyt loki jota voi kutsua lähteessä.
    """
    try:
        dumped = json.dumps(data, ensure_ascii=False)
    except Exception:
        dumped = str(data)

    if len(dumped) > 2000:
        dumped = dumped[:2000] + "... (truncated)"

    logger.info("raw_prices source=%s date=%s data=%s", source, date_ymd.isoformat(), dumped)
