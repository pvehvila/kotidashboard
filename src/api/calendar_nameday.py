# src/api/calendar_nameday.py
"""Backward compatibility shim for nameday API.

Older code used:
    from src.api.calendar_nameday import fetch_nameday_today

Now the actual logic lives in src/api/nameday.py.
This file simply re-exports that function for compatibility.
"""

from .nameday import fetch_nameday_today  # noqa: F401
