import asyncio
from pybit.unified_trading import WebSocket

def simple_callback(msg):
    print("WS MSG:", msg)

async def main():
    ws = WebSocket(channel_type="spot", testnet=False)
    ws.subscribe(topic="tickers", symbol="*", callback=simple_callback)
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
