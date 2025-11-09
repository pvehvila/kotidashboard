# src/api/quotes.py
from typing import Dict, Optional, List
import streamlit as st
from src.config import HTTP_TIMEOUT_S, CACHE_TTL_LONG
from src.utils import report_error
from src.api.http import http_get_json

LOCAL_ZEN: List[Dict[str, str]] = [
    {"text": "Hiljaisuus on vastaus, jota etsit.", "author": "Tuntematon"},
    {"text": "Paranna sitä, mihin kosket, ja jätä se paremmaksi kuin sen löysit.", "author": "Tuntematon"},
    {"text": "Kärsivällisyys on taito odottaa rauhassa.", "author": "Tuntematon"},
    {"text": "Päivän selkeys syntyy hetken huomiosta.", "author": "Tuntematon"},
]


def _from_zenquotes() -> Optional[Dict[str, str]]:
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            q = data[0]
            quote = {"text": q.get("q", ""), "author": q.get("a", ""), "source": "zenquotes"}
            print("[ZEN] Haettu zenquotes:", quote)  # ← lokitus
            return quote
        else:
            print("[ZEN] Zenquotes palautti odottamattoman rakenteen:", data)
    except Exception as e:
        report_error("zen: zenquotes-today", e)
        print("[ZEN] Zenquotes virhe:", e)
    return None


def _from_quotable() -> Optional[Dict[str, str]]:
    try:
        data = http_get_json(
            "https://api.quotable.io/random?tags=wisdom|life|inspirational",
            timeout=HTTP_TIMEOUT_S,
        )
        quote = {"text": data.get("content", ""), "author": data.get("author", ""), "source": "quotable"}
        print("[ZEN] Haettu quotable:", quote)  # ← lokitus
        return quote
    except Exception as e:
        report_error("zen: quotable", e)
        print("[ZEN] Quotable virhe:", e)
    return None


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> Dict[str, str]:
    print(f"[ZEN] Päivän sitaatti haetaan ({day_iso})")
    if quote := _from_zenquotes():
        print("[ZEN] Käytetään zenquotes-lähdettä.")
        return quote
    if quote := _from_quotable():
        print("[ZEN] Käytetään quotable-lähdettä.")
        return quote
    idx = sum(map(ord, day_iso)) % len(LOCAL_ZEN)
    out = dict(LOCAL_ZEN[idx])
    out["source"] = "local"
    print("[ZEN] Käytetään paikallista sitaattia:", out)
    return out