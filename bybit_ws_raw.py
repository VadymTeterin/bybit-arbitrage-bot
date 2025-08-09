import websocket
import json

def on_message(ws, message):
    print("WS MSG:", message)

def on_error(ws, error):
    print("WS ERROR:", error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    # Сюди вставляєш payload для підписки
    payload = {
        "op": "subscribe",
        "args": ["tickers.BTCUSDT"]   # або "tickers.*" для всіх монет, якщо підтримується
    }
    ws.send(json.dumps(payload))

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "wss://stream.bybit.com/v5/public/spot",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()
