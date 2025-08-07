# exchanges/binance_api.py
# Binance API-клієнт для мультибіржового арбітражного бота (v3.0m_05-08-25)
from binance.client import Client
from logger import log_info, log_error

class BinanceClient:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_spot_symbols(self, min_volume=100000):
        """Отримує всі spot-символи USDT із обсягом >= min_volume."""
        try:
            tickers = self.client.get_ticker_24hr()
            symbols = [
                {"symbol": t["symbol"], "volume": float(t["quoteVolume"])}
                for t in tickers
                if t["symbol"].endswith("USDT") and float(t["quoteVolume"]) >= min_volume
            ]
            log_info(f"Binance: отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"Binance помилка отримання spot-символів: {e}")
            return []

    def get_price(self, symbol, category="spot"):
        try:
            if category == "spot":
                price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])
                log_info(f"Binance SPOT ціна {symbol}: {price}")
                return price
            elif category == "linear":  # для USDT-margined futures
                futures = self.client.futures_symbol_ticker(symbol=symbol)
                price = float(futures["price"])
                log_info(f"Binance FUTURES ціна {symbol}: {price}")
                return price
            elif category == "margin":
                # Margin price = spot price (якщо потрібно — тут можна реалізувати через spot)
                price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])
                log_info(f"Binance MARGIN ціна {symbol}: {price}")
                return price
            else:
                log_error(f"Binance: невідомий тип ринку {category}")
                return None
        except Exception as e:
            log_error(f"Binance помилка отримання ціни {symbol} ({category}): {e}")
            return None
