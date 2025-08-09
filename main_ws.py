import sys
import asyncio
import yaml
from core.ws_client import WSClient
from core.bus import EventBus
from core.handlers import on_json_factory
from core.arbitrage import ArbitrageEngine
from exchanges.bybit_ws import BYBIT_WS_SPOT, BYBIT_WS_LINEAR, make_subscribe_tickers
from telegram_bot import TelegramNotifier
from logger import log_info

if sys.platform != "win32":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except:
        pass
else:
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SYMBOLS = config.get("ws_mode", {}).get("symbols", ["BTCUSDT", "ETHUSDT"])
FEE_BP = float(config.get("ws_mode", {}).get("fee_bp", 8.0))
MIN_EDGE_BP = float(config.get("ws_mode", {}).get("min_edge_bp", 12.0))
TTL_SEC = float(config.get("ws_mode", {}).get("ttl_sec", 1.5))
ENABLE_TELEGRAM = bool(config.get("telegram", {}).get("enabled", True))

notifier = TelegramNotifier(
    token=config["telegram"]["bot_token"],
    chat_id=config["telegram"]["chat_id"]
)

async def notify(text: str):
    if ENABLE_TELEGRAM:
        try:
            await notifier.send_message(text)
        except Exception as e:
            print(f"[TG] send failed: {e}")

async def run_fast_ws():
    bus = EventBus()
    handler = await on_json_factory(bus)
    arb = ArbitrageEngine(fee_bp=FEE_BP, min_edge_bp=MIN_EDGE_BP, ttl=TTL_SEC)

    spot_client = WSClient(
        BYBIT_WS_SPOT,
        make_subscribe_tickers(SYMBOLS),
        lambda _, d: handler("bybit:spot", d),
        name="bybit:spot"
    )
    linear_client = WSClient(
        BYBIT_WS_LINEAR,
        make_subscribe_tickers(SYMBOLS),
        lambda _, d: handler("bybit:linear", d),
        name="bybit:linear"
    )

    asyncio.create_task(spot_client.run())
    asyncio.create_task(linear_client.run())

    log_info(f"WS fast mode started for symbols: {SYMBOLS}")
    print(f"✅ WS fast mode: listening {SYMBOLS} on Bybit spot & linear")

    q = await bus.subscribe()
    try:
        while True:
            t = await q.get()
            arb.on_tick(t)
            e = arb.calc_edge(t.symbol)
            if e and e["net_bp"] >= arb.min_edge_bp and e["buy_ex"] != e["sell_ex"]:
                msg = (
                    f"🚀 EDGE {e['symbol']}: BUY {e['buy_ex']} @ {e['buy']:.6f} → "
                    f"SELL {e['sell_ex']} @ {e['sell']:.6f} | NET {e['net_bp']:.2f} bp"
                )
                print(msg)
                await notify(msg)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(run_fast_ws())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
