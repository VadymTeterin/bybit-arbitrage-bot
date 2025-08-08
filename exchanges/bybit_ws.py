import asyncio
from pybit.unified_trading import WebSocket
from logger import log_info, log_error

class BybitWSClient:
    def __init__(self, symbols, on_price_update, is_testnet=False):
        """
        symbols: список монет (наприклад, ["BTCUSDT", "ETHUSDT"])
        on_price_update: асинхронна функція-обробник для нових цін (callable)
        is_testnet: чи використовувати тестнет Bybit
        """
        self.symbols = symbols
        self.on_price_update = on_price_update
        self.is_testnet = is_testnet
        self.ws_spot = None
        self.ws_linear = None

    async def connect(self):
        try:
            # Підключення до спотового ринку
            self.ws_spot = WebSocket(
                testnet=self.is_testnet,
                channel_type="spot"
            )
            # Підключення до ф’ючерсів (USDT perpetual)
            self.ws_linear = WebSocket(
                testnet=self.is_testnet,
                channel_type="linear"
            )
            for symbol in self.symbols:
                self.ws_spot.subscribe("tickers", symbol=symbol)
                self.ws_linear.subscribe("tickers", symbol=symbol)
            log_info("WebSocket: підписка на " + ", ".join(self.symbols))
        except Exception as e:
            log_error(f"WebSocket: не вдалося підключитися — {e}")

    async def listen(self):
        await self.connect()
        try:
            while True:
                # Забираємо дані зі спота
                spot_data = self.ws_spot.fetch_message()
                if spot_data and "data" in spot_data:
                    await self.on_price_update(spot_data["data"], "spot")
                # Забираємо дані з ф’ючерсів
                linear_data = self.ws_linear.fetch_message()
                if linear_data and "data" in linear_data:
                    await self.on_price_update(linear_data["data"], "linear")
                await asyncio.sleep(0.01)  # Дуже короткий інтервал для мінімальної затримки
        except Exception as e:
            log_error(f"WebSocket: помилка при прослуховуванні — {e}")
            # Автоматичний reconnect при помилці
            await asyncio.sleep(2)
            await self.listen()
