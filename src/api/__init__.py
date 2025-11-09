# src/api/__init__.py
from .electricity import try_fetch_prices as try_fetch_prices, try_fetch_prices_15min as try_fetch_prices_15min
from .weather import fetch_weather_points as fetch_weather_points, card_weather_debug_matrix as card_weather_debug_matrix
from .quotes import fetch_daily_quote as fetch_daily_quote
from .calendar import fetch_nameday_today as fetch_nameday_today, fetch_holiday_today as fetch_holiday_today
from .bitcoin import (
    fetch_btc_eur as fetch_btc_eur,
    fetch_btc_last_24h_eur as fetch_btc_last_24h_eur,
    fetch_btc_last_7d_eur as fetch_btc_last_7d_eur,
    fetch_btc_last_30d_eur as fetch_btc_last_30d_eur,
    fetch_btc_eur_range as fetch_btc_eur_range,
    fetch_btc_ath_eur as fetch_btc_ath_eur,
)
