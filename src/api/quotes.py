# src/api/quotes.py

import streamlit as st

from src.api.http_client import http_get_json
from src.config import CACHE_TTL_LONG, HTTP_TIMEOUT_S
from src.utils import report_error

LOCAL_ZEN: list[dict[str, str]] = [
    {"text": "Hiljaisuus on vastaus, jota etsit.", "author": "Tuntematon"},
    {
        "text": "Paranna sitä, mihin kosket, ja jätä se paremmaksi kuin sen löysit.",
        "author": "Tuntematon",
    },
    {"text": "Kärsivällisyys on taito odottaa rauhassa.", "author": "Tuntematon"},
    {"text": "Päivän selkeys syntyy hetken huomiosta.", "author": "Tuntematon"},
]


def _from_zenquotes() -> dict[str, str] | None:
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            q = data[0]
            quote = {"text": q.get("q", ""), "author": q.get("a", ""), "source": "zenquotes"}
            return quote
    except Exception as e:
        report_error("zen: zenquotes-today", e)
    return None


def _from_quotable() -> dict[str, str] | None:
    try:
        data = http_get_json(
            "https://api.quotable.io/random?tags=wisdom|life|inspirational",
            timeout=HTTP_TIMEOUT_S,
        )
        quote = {
            "text": data.get("content", ""),
            "author": data.get("author", ""),
            "source": "quotable",
        }
        return quote
    except Exception as e:
        report_error("zen: quotable", e)
    return None


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> dict[str, str]:
    if quote := _from_zenquotes():
        return quote
    if quote := _from_quotable():
        return quote
    idx = sum(map(ord, day_iso)) % len(LOCAL_ZEN)
    out = dict(LOCAL_ZEN[idx])
    out["source"] = "local"
    return out
