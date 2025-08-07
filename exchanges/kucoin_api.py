# exchanges/kucoin_api.py
# Kucoin API-клієнт для мультибіржового арбітражного бота (v3.0m_05-08-25)
import ccxt
from logger import log_info, log_error

class KucoinClient:
    def __init__(self, api_key, api_secret):
        self.client = ccxt.kucoin({
            'apiKey': api_key,
            'secret': api_secret,
        })

    def get_spot_symbols(self, min_volume=100000):
        try:
            tickers = self.client.fetch_tickers()
            symbols = [
                {"symbol": s, "volume": float(t["quoteVolume"]) }
                for s, t in tickers.items()
                if s.endswith("/USDT") and float(t["quoteVolume"]) >= min_volume
            ]
            log_info(f"Kucoin: отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"Kucoin помилка отримання spot-символів: {e}")
            return []

    def get_price(self, symbol, category="spot"):
        try:
            price = float(self.client.fetch_ticker(symbol)["last"])
            log_info(f"Kucoin {category.upper()} ціна {symbol}: {price}")
            return price
        except Exception as e:
            log_error(f"Kucoin помилка отримання ціни {symbol} ({category}): {e}")
            return None
