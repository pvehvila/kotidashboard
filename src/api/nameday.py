# src/api/nameday.py
"""
Yhteensopivuuskerros vanhoille importeille.

Uusi varsinainen logiikka: src.api.calendar_nameday.fetch_nameday_today
"""

from src.api.calendar_nameday import fetch_nameday_today

__all__ = ["fetch_nameday_today"]
