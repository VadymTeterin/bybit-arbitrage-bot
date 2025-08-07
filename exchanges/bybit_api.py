# exchanges/bybit_api.py
# Bybit API-клієнт для мультибіржового арбітражного бота (v3.0m_05-08-25)
from pybit.unified_trading import HTTP
from logger import log_info, log_error

class BybitClient:
    def __init__(self, api_key, api_secret):
        self.client = HTTP(api_key=api_key, api_secret=api_secret)
        self._futures_symbols = None  # Кеш ф’ючерсних символів

    def get_spot_symbols(self, min_volume=100000):
        """Отримує всі spot-символи USDT із обсягом >= min_volume."""
        try:
            data = self.client.get_tickers(category="spot")
            symbols = [
                {"symbol": item["symbol"], "volume": float(item.get("volume24h", 0))}
                for item in data["result"]["list"]
                if item["symbol"].endswith("USDT") and float(item.get("volume24h", 0)) >= min_volume
            ]
            log_info(f"Bybit: отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"Bybit помилка отримання spot-символів: {e}")
            return []

    def get_futures_symbols(self):
        """Отримує всі доступні linear futures-символи USDT для фільтрації."""
        if self._futures_symbols is not None:
            return self._futures_symbols
        try:
            data = self.client.get_tickers(category="linear")
            self._futures_symbols = set(
                item["symbol"] for item in data["result"]["list"]
                if item["symbol"].endswith("USDT")
            )
            log_info(f"Bybit: кешовано {len(self._futures_symbols)} futures-символів")
            return self._futures_symbols
        except Exception as e:
            log_error(f"Bybit помилка отримання futures-символів: {e}")
            return set()

    def get_price(self, symbol, category="spot"):
        try:
            if category == "margin":
                # Для Bybit margin price = spot price
                data = self.client.get_tickers(category="spot", symbol=symbol)
                symbol_list = data["result"]["list"]
                if not symbol_list:
                    log_error(f"Bybit {symbol} (margin): no data returned (symbol not available)")
                    return None
                price = float(symbol_list[0]["lastPrice"])
                log_info(f"Bybit MARGIN ціна {symbol}: {price}")
                return price
            else:
                data = self.client.get_tickers(category=category, symbol=symbol)
                symbol_list = data["result"]["list"]
                if not symbol_list:
                    log_error(f"Bybit {symbol} ({category}): no data returned (symbol not available)")
                    return None
                price = float(symbol_list[0]["lastPrice"])
                log_info(f"Bybit {category.upper()} ціна {symbol}: {price}")
                return price
        except Exception as e:
            log_error(f"Bybit помилка отримання ціни {symbol} ({category}): {e}")
            return None
