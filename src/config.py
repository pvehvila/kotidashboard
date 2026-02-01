# config.py
"""Configuration settings for the HomeDashboard application."""

import os
from pathlib import Path
from zoneinfo import ZoneInfo

from src.paths import data_path  # ← UUSI

HTTP_TIMEOUT_S: float = 8.0
CACHE_TTL_SHORT: int = 60
CACHE_TTL_MED: int = 300
CACHE_TTL_LONG: int = 3600
COINGECKO_BACKOFF_S: int = 600

DEV: bool = os.environ.get("DEV", "0") == "1"

# ==== TÄRKEÄ: kaikki nämä osoittaa nyt data/ -kansioon ====
ATH_CACHE_FILE = data_path("btc_ath_cache.json")
ETH_ATH_CACHE_FILE = data_path("eth_ath_cache.json")
BTC_PRICE_CACHE_FILE = data_path("btc_price_cache.json")
ETH_PRICE_CACHE_FILE = data_path("eth_price_cache.json")
NAMEDAY_FILE = data_path("nimipaivat_fi.json")
HOLIDAY_FILE = data_path("pyhat_fi.json")

NAMEDAY_PATHS: list[Path] = [
    NAMEDAY_FILE,
    data_path("nimipaivat_fi.json"),
    Path("C:/HomeDashboard/nimipaivat_fi.json"),
    Path.home() / "HomeDashboard" / "nimipaivat_fi.json",
]

HOLIDAY_PATHS: list[Path] = [
    HOLIDAY_FILE,
    data_path("pyhat_fi.json"),
    Path("C:/HomeDashboard/pyhat_fi.json"),
    Path.home() / "HomeDashboard" / "pyhat_fi.json",
]

"""List of potential paths to the Finnish holiday JSON file."""

# ------------------- GEOLOCATION AND TIMEZONE -------------------

LAT: float = 60.737
LON: float = 24.781
"""Riihimäki coordinates for weather data (latitude, longitude)."""

TZ: ZoneInfo = ZoneInfo("Europe/Helsinki")
"""Timezone for the application (Europe/Helsinki)."""

# ------------------- UI COLORS -------------------

COLOR_GREEN: str = "#5cd65c"
"""Green color for positive indicators (e.g., electricity price increase)."""

COLOR_RED: str = "#ff6666"
"""Red color for negative indicators (e.g., electricity price decrease)."""

COLOR_GRAY: str = "#2b2b2b"
"""Gray background color for capsules (e.g., last 7 days)."""

COLOR_TEXT_GRAY: str = "#d0d0d0"
"""Gray color for text elements."""

# ------------------- ELECTRICITY PRICE THRESHOLDS -------------------

PRICE_LOW_THR: float = 5.0
"""Low electricity price threshold (cents/kWh)."""

PRICE_HIGH_THR: float = 15.0
"""High electricity price threshold (cents/kWh)."""

PRICE_Y_STEP_SNT: int = 5
"""Y-axis step size for electricity price chart (cents/kWh)."""

PRICE_Y_MIN_SNT: int = 0
"""Minimum Y-axis value for electricity price chart (cents/kWh)."""

# ------------------- WEATHER THRESHOLDS -------------------

POP_POSSIBLE_THRESHOLD: int = 40
"""Precipitation probability threshold (%) for 'possible' weather icons."""

SLEET_TEMP_MIN: float = -1.0
SLEET_TEMP_MAX: float = 1.0
"""Temperature range (°C) for sleet detection (inclusive)."""

CLOUD_T_CLEAR: int = 15
CLOUD_T_ALMOST: int = 35
CLOUD_T_PARTLY: int = 65
CLOUD_T_MOSTLY: int = 85
"""Cloud cover thresholds (%) for weather icons (d000, d100, d200, d300, d400)."""

# ------------------- PLOTLY CONFIG -------------------

PLOTLY_CONFIG: dict = {
    "displayModeBar": False,
    "responsive": True,
}


# ------------------- BITCOIN CHART SETTINGS -------------------

BTC_Y_STEP_EUR: int = 5000
"""Y-axis step size for Bitcoin price chart (EUR)."""

BTC_Y_PAD_EUR: int = 300
"""Minimum padding for Bitcoin chart Y-axis (EUR)."""

BTC_Y_PAD_PCT: float = 0.02
"""Relative padding for Bitcoin chart Y-axis (2% of data range)."""

BTC_Y_USE_PCT_PAD: bool = True
# Use max(BTC_Y_PAD_EUR, BTC_Y_PAD_PCT * data_range) for Y-axis padding.

# ------------------- HEOS SETTINGS -------------------
HEOS_HOST = os.getenv("HEOS_HOST", "192.168.1.231")
HEOS_USERNAME = os.getenv("HEOS_USERNAME", "")
HEOS_PASSWORD = os.getenv("HEOS_PASSWORD", "")
HEOS_PLAYER_ID = int(os.getenv("HEOS_PLAYER_ID", "186388645"))
HEOS_TIDAL_PLAYLIST = os.getenv("HEOS_TIDAL_PLAYLIST", "My Daily Discovery")
HEOS_TIDAL_SID = int(os.getenv("HEOS_TIDAL_SID", "10"))
HEOS_TIDAL_CID = os.getenv("HEOS_TIDAL_CID", "1025")
