# src/ui/__init__.py
"""
UI cards export module.

This file tries to import all known cards, but does not crash
if some of them are missing. This is useful while refactoring.
"""

__all__ = []

def _safe_import(name, alias=None):
    try:
        module = __import__(f"src.ui.{name}", fromlist=["*"])
    except ImportError:
        return
    obj_name = alias or name
    globals()[obj_name] = module.__dict__[obj_name] if obj_name in module.__dict__ else module
    __all__.append(obj_name)


# --- list your cards here ---
# these are ones we've seen in your repo/logs
_safe_import("card_prices", "card_prices")
_safe_import("card_weather", "card_weather")
_safe_import("card_bitcoin", "card_bitcoin")
_safe_import("card_nameday", "card_nameday")
_safe_import("card_system", "card_system")

# if you have Tidal / HEOS / sun cards etc., add them here:
# _safe_import("card_tidal", "card_tidal")
# _safe_import("card_sun", "card_sun")
# _safe_import("card_zenquotes", "card_zenquotes")
