import asyncio
import yaml
from datetime import datetime

from telegram_bot import TelegramNotifier
from logger import log_info
from cache.cache_manager import CacheManager
from utils.history_manager import HistoryManager
from formatters.message_formatter import format_exchange_report

from exchange_manager import ExchangeManager

# === Імпорт арбітражних блоків для всіх бірж ===
from arbitrage_blocks.bybit_arbitrage import get_spot_futures_arbitrage as bybit_arbitrage, get_margin_futures_arbitrage as bybit_margin_arbitrage
from arbitrage_blocks.binance_arbitrage import get_spot_futures_arbitrage as binance_arbitrage, get_margin_futures_arbitrage as binance_margin_arbitrage
from arbitrage_blocks.okx_arbitrage import get_spot_futures_arbitrage as okx_arbitrage, get_margin_futures_arbitrage as okx_margin_arbitrage
from arbitrage_blocks.kucoin_arbitrage import get_spot_futures_arbitrage as kucoin_arbitrage, get_margin_futures_arbitrage as kucoin_margin_arbitrage
from arbitrage_blocks.gateio_arbitrage import get_spot_futures_arbitrage as gateio_arbitrage, get_margin_futures_arbitrage as gateio_margin_arbitrage
from arbitrage_blocks.bingx_arbitrage import get_spot_futures_arbitrage as bingx_arbitrage, get_margin_futures_arbitrage as bingx_margin_arbitrage
from arbitrage_blocks.mexc_arbitrage import get_spot_futures_arbitrage as mexc_arbitrage, get_margin_futures_arbitrage as mexc_margin_arbitrage
from arbitrage_blocks.htx_arbitrage import get_spot_futures_arbitrage as htx_arbitrage, get_margin_futures_arbitrage as htx_margin_arbitrage

from exchanges.bybit_ws import BybitWSClient

ARBITRAGE_BLOCKS = {
    'bybit': (bybit_arbitrage, bybit_margin_arbitrage),
    'binance': (binance_arbitrage, binance_margin_arbitrage),
    'okx': (okx_arbitrage, okx_margin_arbitrage),
    'kucoin': (kucoin_arbitrage, kucoin_margin_arbitrage),
    'gateio': (gateio_arbitrage, gateio_margin_arbitrage),
    'bingx': (bingx_arbitrage, bingx_margin_arbitrage),
    'mexc': (mexc_arbitrage, mexc_margin_arbitrage),
    'htx': (htx_arbitrage, htx_margin_arbitrage),
}

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

notifier = TelegramNotifier(config['telegram']['bot_token'], config['telegram']['chat_id'])
cache_manager = CacheManager(cache_ttl=600)
history_manager = HistoryManager()
exchange_manager = ExchangeManager(config)

# === Додаємо WebSocket моніторинг для Bybit ===
latest_prices = {
    'spot': {},
    'linear': {},
}

async def ws_price_update(data, market_type):
    symbol = data["symbol"]
    price = float(data["lastPrice"])
    latest_prices[market_type][symbol] = price

    # Перевіряємо чи є ціна на споті та ф’ючерсі
    if symbol in latest_prices['spot'] and symbol in latest_prices['linear']:
        spot_price = latest_prices['spot'][symbol]
        futures_price = latest_prices['linear'][symbol]
        diff = abs(futures_price - spot_price) / spot_price * 100

        threshold = config['exchanges']['bybit'].get("arbitrage_difference", 1)
        # Антиспам – не спамити одне і те саме
        alert_id = f"bybit_ws_{symbol}_{round(diff,2)}"
        if diff >= threshold and history_manager.is_new_top('bybit', alert_id, diff):
            msg = (
                f"🚨 <b>LIVE Арбітраж Bybit</b>:\n"
                f"{symbol}\n"
                f"Спот: <code>{spot_price}</code>\n"
                f"Ф’ючерси: <code>{futures_price}</code>\n"
                f"Різниця: <b>{diff:.2f}%</b>"
            )
            await notifier.send_message(msg)
            log_info(msg)
            history_manager.save_top('bybit', alert_id, diff)

async def run_bybit_ws():
    bybit_client = exchange_manager.get_active_exchanges().get('bybit')
    if not bybit_client:
        log_info("Bybit WS: біржа неактивна")
        return
    # Отримуємо ТОП-5 монет Bybit з фільтром за ліквідністю
    symbols = cache_manager.get_symbols(
        'bybit', bybit_client,
        config['exchanges']['bybit'].get('min_volume', 100000)
    )[:5]
    ws_client = BybitWSClient(symbols, ws_price_update)
    await ws_client.listen()

# === Класичний цикл HTTP-арбітражу (як у тебе) ===
async def check_arbitrage():
    enabled_exchanges = [name.capitalize() for name in exchange_manager.get_active_exchanges().keys()]
    start_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    start_msg = (
        f"🌐 Арбітражний бот v4.0 успішно ЗАПУЩЕНО!\n\n"
        f"🟢 Працює для бірж: <b>{', '.join(enabled_exchanges)}</b>\n"
        f"🔍 Пошук арбітражу між спотом, маржею і ф’ючерсами на кількох біржах.\n"
        f"⏰ {start_time}\n\n"
        f"Бажаю прибуткових сигналів! 🚀"
    )
    await notifier.send_message(start_msg)
    log_info(f"Арбітражний бот v4.0 запущено для бірж: {', '.join(enabled_exchanges)}")

    try:
        while True:
            print("Арбітражний бот v4.0 запущено, шукаю арбітраж...")

            total_msg = ""
            at_least_one_update = False

            for exch_name, client in exchange_manager.get_active_exchanges().items():
                exch_cfg = exchange_manager.get_config(exch_name)
                arbitrage_funcs = ARBITRAGE_BLOCKS.get(exch_name)
                if not arbitrage_funcs:
                    continue

                symbols = cache_manager.get_symbols(
                    exch_name,
                    client,
                    exch_cfg.get('min_volume', 100000)
                )

                get_spot_arbitrage, get_margin_arbitrage = arbitrage_funcs
                top_spot = await get_spot_arbitrage(client, symbols, config)
                top_margin = await get_margin_arbitrage(client, symbols, config)

                if history_manager.is_new_top(exch_name, 'spot', top_spot) or history_manager.is_new_top(exch_name, 'margin', top_margin):
                    at_least_one_update = True
                    msg = format_exchange_report(exch_name, top_spot, top_margin)
                    total_msg += msg + "\n"
                    history_manager.save_top(exch_name, 'spot', top_spot)
                    history_manager.save_top(exch_name, 'margin', top_margin)
                else:
                    log_info(f"{exch_name.capitalize()}: Топи не змінилися — алерт не надсилаємо")

                await asyncio.sleep(exch_cfg.get('request_interval', config.get('request_interval', 3)))

            if at_least_one_update:
                loud = "SPECIAL ALERT" in total_msg or "⚡️" in total_msg
                await notifier.send_message(total_msg, loud=loud)
                log_info(total_msg)

    except Exception as e:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        error_msg = (
            f"🌐 Арбітражний бот v4.0 ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено через помилку.\n"
            f"⏰ {stop_time}\n\n"
            f"Помилка: {str(e)}"
        )
        await notifier.send_message(error_msg)
        log_info(error_msg)
        raise

    except KeyboardInterrupt:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        stop_msg = (
            f"🌐 Арбітражний бот v4.0 ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено вручну.\n"
            f"⏰ {stop_time}\n\n"
            f"Бот коректно зупинено за запитом користувача."
        )
        await notifier.send_message(stop_msg)
        log_info(stop_msg)

    finally:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        final_msg = (
            f"🌐 Арбітражний бот v4.0 ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено.\n"
            f"⏰ {stop_time}\n\n"
            f"Перевір роботу, якщо зупинка була неочікуваною!"
        )
        await notifier.send_message(final_msg)
        log_info(final_msg)

# === Запуск одразу двох процесів: HTTP та WS ===
if __name__ == "__main__":
    async def main():
        await asyncio.gather(
            check_arbitrage(),   # класичний цикл
            run_bybit_ws(),      # WebSocket моніторинг Bybit
        )
    asyncio.run(main())
