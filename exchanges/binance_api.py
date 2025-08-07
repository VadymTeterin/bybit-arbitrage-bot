# exchanges/binance_api.py
# Binance API-клієнт для мультибіржового арбітражного бота (v3.0m_05-08-25)
from binance.client import Client
from logger import log_info, log_error
import time

class BinanceClient:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        self._futures_symbols = None
        self._futures_symbols_last_update = 0  # timestamp останнього оновлення

    def get_spot_symbols(self, min_volume=100000):
        """Отримує всі spot-символи USDT із обсягом >= min_volume."""
        try:
            tickers = self.client.get_ticker()
            symbols = [
                {"symbol": t["symbol"], "volume": float(t.get("quoteVolume", 0))}
                for t in tickers
                if t["symbol"].endswith("USDT") and float(t.get("quoteVolume", 0)) >= min_volume
            ]
            log_info(f"Binance: отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"Binance помилка отримання spot-символів: {e}")
            return []

    def get_futures_symbols(self):
        """Оновлює кеш futures-символів не частіше, ніж раз на 60 хвилин."""
        cache_lifetime = 60 * 60  # 60 хвилин у секундах
        now = time.time()
        if self._futures_symbols is not None and now - self._futures_symbols_last_update < cache_lifetime:
            return self._futures_symbols
        try:
            info = self.client.futures_exchange_info()
            self._futures_symbols = set(
                symbol["symbol"] for symbol in info["symbols"] if symbol["quoteAsset"] == "USDT"
            )
            self._futures_symbols_last_update = now
            log_info(f"Binance: кешовано {len(self._futures_symbols)} futures-символів (оновлено)")
            return self._futures_symbols
        except Exception as e:
            log_error(f"Binance помилка отримання списку futures-символів: {e}")
            return self._futures_symbols if self._futures_symbols else set()

    def get_price(self, symbol, category="spot"):
        try:
            if category == "spot":
                price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])
                log_info(f"Binance SPOT ціна {symbol}: {price}")
                return price
            elif category == "linear":  # для USDT-margined futures
                futures_symbols = self.get_futures_symbols()
                if symbol not in futures_symbols:
                    log_error(f"Binance {symbol} (linear): symbol not available for futures")
                    return None
                futures = self.client.futures_symbol_ticker(symbol=symbol)
                price_val = futures.get("price")
                if price_val is None:
                    log_error(f"Binance {symbol} (linear): futures response has no price! {futures}")
                    return None
                price = float(price_val)
                log_info(f"Binance FUTURES ціна {symbol}: {price}")
                return price
            elif category == "margin":
                # Margin price = spot price (для Binance)
                price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])
                log_info(f"Binance MARGIN ціна {symbol}: {price}")
                return price
            else:
                log_error(f"Binance: невідомий тип ринку {category}")
                return None
        except Exception as e:
            log_error(f"Binance помилка отримання ціни {symbol} ({category}): {e}")
            return None
