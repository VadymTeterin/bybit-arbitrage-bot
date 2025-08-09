import asyncio
from pybit.unified_trading import WebSocket
from logger import log_info, log_error

class BybitWSClient:
    def __init__(self, symbols, on_price_update, is_testnet=False):
        self.symbols = symbols
        self.on_price_update = on_price_update
        self.is_testnet = is_testnet
        self.ws_spot = None
        self.ws_linear = None

    async def connect(self):
        try:
            self.ws_spot = WebSocket(
                testnet=self.is_testnet,
                channel_type="spot"
            )
            self.ws_linear = WebSocket(
                testnet=self.is_testnet,
                channel_type="linear"
            )
            for symbol in self.symbols:
                self.ws_spot.subscribe(
                    topic="tickers",
                    symbol=symbol,
                    callback=lambda msg, s=symbol: asyncio.create_task(self.on_price_update(msg['data'], "spot"))
                )
                self.ws_linear.subscribe(
                    topic="tickers",
                    symbol=symbol,
                    callback=lambda msg, s=symbol: asyncio.create_task(self.on_price_update(msg['data'], "linear"))
                )
            log_info("WebSocket: підписка на " + ", ".join(self.symbols))
        except Exception as e:
            log_error(f"WebSocket: не вдалося підключитися — {e}")

    async def listen(self):
        await self.connect()
        while True:
            await asyncio.sleep(10)
