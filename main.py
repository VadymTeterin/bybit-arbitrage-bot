# main.py (для v3.0m_05-08-25)
import asyncio
import yaml
import time
from datetime import datetime

from telegram_bot import TelegramNotifier
from logger import log_info
from cache.cache_manager import CacheManager
from utils.history_manager import HistoryManager
from formatters.message_formatter import format_exchange_report

# ==== Імпорт API-клієнтів та арбітраж-блоків для всіх бірж ====
from exchanges.bybit_api import BybitClient
from arbitrage_blocks.bybit_arbitrage import get_spot_futures_arbitrage as bybit_arbitrage, get_margin_futures_arbitrage as bybit_margin_arbitrage

from exchanges.binance_api import BinanceClient
from arbitrage_blocks.binance_arbitrage import get_spot_futures_arbitrage as binance_arbitrage, get_margin_futures_arbitrage as binance_margin_arbitrage

from exchanges.okx_api import OKXClient
from arbitrage_blocks.okx_arbitrage import get_spot_futures_arbitrage as okx_arbitrage, get_margin_futures_arbitrage as okx_margin_arbitrage

from exchanges.kucoin_api import KucoinClient
from arbitrage_blocks.kucoin_arbitrage import get_spot_futures_arbitrage as kucoin_arbitrage, get_margin_futures_arbitrage as kucoin_margin_arbitrage

from exchanges.gateio_api import GateioClient
from arbitrage_blocks.gateio_arbitrage import get_spot_futures_arbitrage as gateio_arbitrage, get_margin_futures_arbitrage as gateio_margin_arbitrage

from exchanges.bingx_api import BingxClient
from arbitrage_blocks.bingx_arbitrage import get_spot_futures_arbitrage as bingx_arbitrage, get_margin_futures_arbitrage as bingx_margin_arbitrage

from exchanges.mexc_api import MexcClient
from arbitrage_blocks.mexc_arbitrage import get_spot_futures_arbitrage as mexc_arbitrage, get_margin_futures_arbitrage as mexc_margin_arbitrage

from exchanges.htx_api import HtxClient
from arbitrage_blocks.htx_arbitrage import get_spot_futures_arbitrage as htx_arbitrage, get_margin_futures_arbitrage as htx_margin_arbitrage

# ==== Мапи для гнучкого підключення ====
API_CLIENTS = {
    'bybit': BybitClient,
    'binance': BinanceClient,
    'okx': OKXClient,
    'kucoin': KucoinClient,
    'gateio': GateioClient,
    'bingx': BingxClient,
    'mexc': MexcClient,
    'htx': HtxClient,
}
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

async def check_arbitrage():
    start_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    start_msg = (
        f"🌐 Мультибіржовий арбітражний бот v3.0m успішно ЗАПУЩЕНО!\n\n"
        f"🔍 Пошук арбітражу між спотом, маржею і ф’ючерсами на кількох біржах.\n"
        f"⏰ {start_time}\n\n"
        f"Бажаю прибуткових сигналів! 🚀"
    )
    await notifier.send_message(start_msg)
    log_info("v3.0m: Бот мультибіржовий запущено")

    try:
        while True:
            print("v3.0m: Бот мультибіржовий запущено, шукаю арбітраж...")

            total_msg = ""
            at_least_one_update = False

            for exch_name, exch_cfg in config['exchanges'].items():
                if not exch_cfg.get('enabled', False):
                    continue

                client_class = API_CLIENTS.get(exch_name)
                arbitrage_funcs = ARBITRAGE_BLOCKS.get(exch_name)
                if not client_class or not arbitrage_funcs:
                    continue

                client = client_class(exch_cfg['api_key'], exch_cfg['api_secret'])
                symbols = cache_manager.get_symbols(
                    exch_name,
                    client,
                    exch_cfg.get('min_volume', 100000)
                )

                get_spot_arbitrage, get_margin_arbitrage = arbitrage_funcs
                top_spot = await get_spot_arbitrage(client, symbols, config)
                top_margin = await get_margin_arbitrage(client, symbols, config)

                # ---- антиспам через history_manager ----
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
            f"🌐 v3.0m: Мультибіржовий бот ЗУПИНЕНО!\n\n"
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
            f"🌐 v3.0m: Мультибіржовий бот ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено вручну.\n"
            f"⏰ {stop_time}\n\n"
            f"Бот коректно зупинено за запитом користувача."
        )
        await notifier.send_message(stop_msg)
        log_info(stop_msg)

    finally:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        final_msg = (
            f"🌐 v3.0m: Мультибіржовий бот ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено.\n"
            f"⏰ {stop_time}\n\n"
            f"Перевір роботу, якщо зупинка була неочікуваною!"
        )
        await notifier.send_message(final_msg)
        log_info(final_msg)

if __name__ == "__main__":
    asyncio.run(check_arbitrage())
