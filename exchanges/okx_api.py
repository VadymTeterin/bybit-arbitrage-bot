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

    def get_spot_symbols(self, min_volume=100000):
        try:
            tickers = self.client.fetch_tickers()
            symbols = [
                {"symbol": s, "volume": float(t["quoteVolume"]) }
                for s, t in tickers.items()
                if s.endswith("/USDT") and float(t["quoteVolume"]) >= min_volume
            ]
            log_info(f"OKX: отримано {len(symbols)} spot-символів з обсягом >= {min_volume}")
            return symbols
        except Exception as e:
            log_error(f"OKX помилка отримання spot-символів: {e}")
            return []

    def get_price(self, symbol, category="spot"):
        try:
            if category == "spot":
                price = float(self.client.fetch_ticker(symbol)["last"])
                log_info(f"OKX SPOT ціна {symbol}: {price}")
                return price
            elif category == "linear":
                market = symbol.replace("/USDT", "USDT")
                ticker = self.client.fapiPublic_get_ticker_price({"symbol": market})
                price = float(ticker["price"])
                log_info(f"OKX FUTURES ціна {symbol}: {price}")
                return price
            elif category == "margin":
                price = float(self.client.fetch_ticker(symbol)["last"])
                log_info(f"OKX MARGIN ціна {symbol}: {price}")
                return price
            else:
                log_error(f"OKX: невідомий тип ринку {category}")
                return None
        except Exception as e:
            log_error(f"OKX помилка отримання ціни {symbol} ({category}): {e}")
            return None
