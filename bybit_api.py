from pybit.unified_trading import HTTP
from logger import log_info, log_error

class BybitClient:
    def __init__(self, api_key, api_secret):
        self.client = HTTP(api_key=api_key, api_secret=api_secret)

    def get_spot_symbols(self, min_volume=100000):
        """Отримує усі символи зі спотового ринку, які мають USDT та обсяг >= min_volume."""
        try:
            data = self.client.get_tickers(category="spot")
            symbols = [
                {"symbol": item["symbol"], "volume": float(item.get("volume24h", 0))}
                for item in data["result"]["list"]
                if item["symbol"].endswith("USDT") and float(item.get("volume24h", 0)) >= min_volume
            ]
            log_info(f"Отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"Помилка отримання списку spot-символів: {e}")
            return []

    def get_price(self, symbol, category="spot"):
        try:
            data = self.client.get_tickers(category=category, symbol=symbol)
            price = float(data["result"]["list"][0]["lastPrice"])
            log_info(f"{category.upper()} ціна {symbol}: {price}")
            return price
        except Exception as e:
            log_error(f"Помилка отримання ціни {symbol} ({category}): {e}")
            return None

