# exchanges/okx_api.py
# OKX API-клієнт для мультибіржового арбітражного бота (v3.0m_05-08-25)
import ccxt
from logger import log_info, log_error

class OKXClient:
    def __init__(self, api_key, api_secret):
        self.client = ccxt.okx({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self._futures_symbols = None

    def get_spot_symbols(self, min_volume=100000):
        try:
            tickers = self.client.fetch_tickers()
            symbols = [
                {"symbol": s, "volume": float(t["quoteVolume"])}
                for s, t in tickers.items()
                if s.endswith("/USDT") and float(t["quoteVolume"]) >= min_volume
            ]
            log_info(f"OKX: отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"OKX помилка отримання spot-символів: {e}")
            return []

    def get_futures_symbols(self):
        if self._futures_symbols is not None:
            return self._futures_symbols
        try:
            markets = self.client.fetch_markets()
            self._futures_symbols = set(
                m['symbol'] for m in markets if m['type'] == 'swap' and m['symbol'].endswith(":USDT")
            )
            log_info(f"OKX: кешовано {len(self._futures_symbols)} futures-символів")
            return self._futures_symbols
        except Exception as e:
            log_error(f"OKX помилка отримання futures-символів: {e}")
            return set()

    def get_price(self, symbol, category="spot"):
        try:
            if category == "spot" or category == "margin":
                ticker = self.client.fetch_ticker(symbol)
                price = float(ticker["last"])
                log_info(f"OKX {category.upper()} ціна {symbol}: {price}")
                return price
            elif category == "linear":
                futures_symbols = self.get_futures_symbols()
                if symbol not in futures_symbols:
                    log_error(f"OKX {symbol} (linear): symbol not available for futures")
                    return None
                ticker = self.client.fetch_ticker(symbol)
                price = float(ticker["last"])
                log_info(f"OKX FUTURES ціна {symbol}: {price}")
                return price
            else:
                log_error(f"OKX: невідомий тип ринку {category}")
                return None
        except Exception as e:
            log_error(f"OKX помилка отримання ціни {symbol} ({category}): {e}")
            return None
