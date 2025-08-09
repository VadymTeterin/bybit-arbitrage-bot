import time
from core.bus import Tick

async def on_json_factory(bus):
    async def handle(exch_name, data):
        now = time.time()
        topic = data.get("topic", "")
        if topic.startswith("tickers."):
            items = data.get("data") or []
            for it in items:
                symbol = it["symbol"]
                bid1 = float(it["bid1Price"])
                ask1 = float(it["ask1Price"])
                await bus.publish(Tick(exch=exch_name, symbol=symbol, bid=bid1, ask=ask1, ts=now))
    return handle
