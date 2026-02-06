# src/api/__init__.py
from .bitcoin import (
    fetch_btc_ath_eur as fetch_btc_ath_eur,
)
from .bitcoin import (
    fetch_btc_eur as fetch_btc_eur,
)
from .bitcoin import (
    fetch_btc_eur_range as fetch_btc_eur_range,
)
from .bitcoin import (
    fetch_btc_last_7d_eur as fetch_btc_last_7d_eur,
)
from .bitcoin import (
    fetch_btc_last_24h_eur as fetch_btc_last_24h_eur,
)
from .bitcoin import (
    fetch_btc_last_30d_eur as fetch_btc_last_30d_eur,
)
from .bitcoin import (
    fetch_eth_ath_eur as fetch_eth_ath_eur,
)
from .bitcoin import (
    fetch_eth_eur as fetch_eth_eur,
)
from .bitcoin import (
    fetch_eth_eur_range as fetch_eth_eur_range,
)
from .calendar_nameday import fetch_holiday_today as fetch_holiday_today
from .calendar_nameday import fetch_nameday_today as fetch_nameday_today
from .electricity import try_fetch_prices as try_fetch_prices
from .electricity import try_fetch_prices_15min as try_fetch_prices_15min
from .quotes import fetch_daily_quote as fetch_daily_quote
from .weather import card_weather_debug_matrix as card_weather_debug_matrix
from .weather import fetch_weather_points as fetch_weather_points
