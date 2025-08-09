import orjson

BYBIT_WS_SPOT   = "wss://stream.bybit.com/v5/public/spot"
BYBIT_WS_LINEAR = "wss://stream.bybit.com/v5/public/linear"

def make_subscribe_tickers(symbols):
    topics = [f"tickers.{s}" for s in symbols]
    payload = {"op": "subscribe", "args": topics}
    return lambda: orjson.dumps(payload).decode()
